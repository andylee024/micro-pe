"""Rich terminal UI controller for Scout — 4-pane Bloomberg layout"""

import json
import re
import threading
import time
from typing import Dict, List, Optional
from pathlib import Path
import webbrowser

from rich.console import Console
from rich.live import Live
from rich.layout import Layout

from .components import (
    create_market_overview_panel,
    create_target_list_panel,
    create_business_profile_panel,
    create_market_pulse_panel,
    create_scout_assistant_panel,
    create_header_text,
    create_footer_text,
    create_help_panel,
    create_progress_panel,
    create_main_layout,
)
from .keyboard import KeyboardHandler
from scout.shared.export import export_to_csv, format_export_message
from scout.domain.models import MarketOverview, MarketPulse
from scout.shared.errors import (
    handle_api_error,
    handle_file_error,
    format_error_message,
)


class ScoutTerminal:
    """Terminal UI controller — 4-pane Bloomberg-style interface."""

    def __init__(
        self,
        industry: str,
        location: str,
        use_cache: bool = True,
        max_results: int = 500,
        initial_result=None,
        query_string: Optional[str] = None,
    ):
        self.industry = industry
        self.location = location
        self.use_cache = use_cache
        self.max_results = max_results

        # Data
        self.businesses: List[Dict] = []
        self.market_overview: MarketOverview = MarketOverview()
        self.market_pulse: MarketPulse = MarketPulse()
        self.filtered_businesses: Optional[List[Dict]] = None
        self.active_filter: str = ""

        # UI state
        self.console = Console()
        self.status = "Initializing..."
        self.scroll_offset = 0
        self.selected_index = 0        # cursor in target list
        self.opened_business: Optional[Dict] = None   # profile pane
        self.cached = False
        self.show_help = False
        self.error_message: Optional[str] = None

        # Page size for target list pane
        self.page_size = self._compute_page_size()

        # Chat state
        self.chat_history: List[Dict] = []
        self.chat_input: str = ""
        self.chat_mode: bool = False
        self.chat_scroll_offset: int = 0

        # Pane focus state
        self.focused_pane: str = "target_list"  # market_overview | market_pulse | target_list | scout_assistant
        self.overview_show_sources: bool = False
        self.pulse_show_sources: bool = False
        self.query_string: str = query_string or f"{industry} businesses in {location}"

        # Loading screen state
        self.screen: str = "ready"  # "loading" | "ready"
        self.pipeline_stages: dict = {}   # stage → "pending" | "running" | "done" | "error"
        self.pipeline_counts: dict = {}   # stage → int count

        self.live: Optional[Live] = None
        self.keyboard_handler = KeyboardHandler(self)

        if initial_result is not None:
            self._seed_from_result(initial_result)

    def _compute_page_size(self) -> int:
        """Estimate how many rows fit in the target list pane."""
        height = self.console.size.height or 24
        # Reserve header/footer and divide space between top/bottom rows (2/3 ratio).
        usable = max(10, height - 2)
        bottom_height = int(usable * 3 / 5)
        # Each business takes ~3 lines including spacing.
        return max(6, (bottom_height - 2) // 3)

    def run(self) -> None:
        """Launch terminal UI."""
        try:
            with Live(
                self._build_layout(),
                console=self.console,
                refresh_per_second=4,
                screen=True,
            ) as live:
                self.live = live

                if not self.businesses:
                    fetch_thread = threading.Thread(target=self._fetch_data)
                    fetch_thread.daemon = True
                    fetch_thread.start()
                else:
                    fetch_thread = None
                    self.status = "Ready (mock data)" if self.status == "Initializing..." else self.status

                self.keyboard_handler.handle_event_loop()

                if fetch_thread and fetch_thread.is_alive():
                    fetch_thread.join(timeout=1.0)

        except KeyboardInterrupt:
            self.console.print("\n[dim]Exiting Scout...[/dim]")
        except Exception as e:
            self.console.print(f"\n[red]Error: {str(e)}[/red]")

    def _fetch_data(self) -> None:
        """Fetch data from Google Maps in background thread."""
        try:
            from scout.application.research_market import ResearchMarket

            self.screen = "loading"
            self.pipeline_stages = {s: "pending" for s in ["maps", "bizbuysell", "reddit", "ai_analysis"]}
            self.pipeline_counts = {}
            self._update_display()

            self.status = "Searching data sources..."
            self._update_display()

            use_case = ResearchMarket()
            result = use_case.run(
                industry=self.industry,
                location=self.location,
                query=self.query_string,
                max_results=self.max_results,
                use_cache=self.use_cache,
                include_benchmarks=True,
                on_progress=self._on_pipeline_progress,
            )

            self.businesses = [self._business_to_dict(b) for b in result.businesses]
            # Keep source order; no scoring-based ranking for now.
            self.market_overview = (
                result.market_overview
                if result.market_overview and result.market_overview.total_businesses
                else self._market_overview_from_result(result)
            )
            self.market_pulse = result.pulse or self._market_pulse_placeholder()
            self.cached = self.use_cache
            self.selected_index = 0
            self.screen = "ready"
            self.status = "Ready"
            self._update_display()

        except ConnectionError:
            self.screen = "ready"
            self.status = "Error: network connection failed"
            self.error_message = "Network connection failed."
            self._update_display()

        except Exception as e:
            self.screen = "ready"
            api_error = handle_api_error(e, "Google Maps")
            self.status = f"Error: {str(e)}"
            self.error_message = format_error_message(api_error)
            self._update_display()

    def _seed_from_result(self, result) -> None:
        """Seed the UI with a precomputed ResearchResult (mock or cached)."""
        self.businesses = [self._business_to_dict(b) for b in result.businesses]
        # Keep source order; no scoring-based ranking for now.
        self.market_overview = (
            result.market_overview
            if result.market_overview and result.market_overview.total_businesses
            else self._market_overview_from_result(result)
        )
        self.market_pulse = result.pulse or self._market_pulse_placeholder()
        self.cached = True
        self.selected_index = 0
        self.status = "Ready (mock data)"
        self.query_string = result.summary.query
        self.chat_history = [
            {
                "q": "Which companies have 150+ reviews?",
                "a": "3 match: Cool Air HVAC (350), Precision Comfort (420),\nRapid Response (310).  [Enter] apply filter",
            },
            {
                "q": "Summarize the key risks.",
                "a": "3 risks: tech shortage limits scale, price pressure\ncompresses margins, top operators rarely sell.",
            },
        ]

    def _build_loading_layout(self) -> Layout:
        """Single-pane loading screen showing pipeline progress."""
        from rich.text import Text as RichText
        from rich.panel import Panel as RichPanel

        layout = Layout()
        layout.split_column(
            Layout(name="header", size=1),
            Layout(name="body"),
            Layout(name="footer", size=1),
        )

        layout["header"].update(
            create_header_text(
                industry=self.industry,
                location=self.location,
                count=0,
                cached=False,
                status="researching...",
            )
        )

        t = RichText()
        t.append("\n")

        stage_labels = {
            "maps": "Google Maps",
            "bizbuysell": "BizBuySell",
            "reddit": "Reddit",
            "ai_analysis": "AI analysis",
        }

        for stage, label in stage_labels.items():
            status = self.pipeline_stages.get(stage, "pending")
            count = self.pipeline_counts.get(stage, 0)

            if status == "done":
                icon = "✓"
                icon_style = "green"
                detail = f"{count:,} found" if count else "done"
                detail_style = "dim white"
            elif status == "running":
                icon = "⠸"
                icon_style = "yellow"
                detail = "fetching..."
                detail_style = "yellow"
            elif status == "error":
                icon = "✗"
                icon_style = "red"
                detail = "unavailable"
                detail_style = "dim white"
            else:  # pending
                icon = "◻"
                icon_style = "dim white"
                detail = "pending"
                detail_style = "dim white"

            t.append(f"  {icon}  ", style=icon_style)
            t.append(f"{label:<20}", style="white" if status == "running" else "dim white")
            t.append(f"{detail}\n\n", style=detail_style)

        layout["body"].update(
            RichPanel(t, border_style="dim white", padding=(0, 0))
        )

        layout["footer"].update(create_footer_text())

        return layout

    def _build_layout(self) -> Layout:
        """Build the 4-pane layout with current state."""
        if self.screen == "loading":
            return self._build_loading_layout()

        layout = create_main_layout()

        # Header — single line
        visible_businesses = self._visible_businesses()

        layout["header"].update(
            create_header_text(
                industry=self.industry,
                location=self.location,
                count=len(visible_businesses),
                cached=self.cached,
                status=self.status,
                grade=self.market_overview.outlook.grade,
            )
        )

        # Market overview — top-left context pane
        layout["market_overview"].update(
            create_market_overview_panel(
                self.market_overview,
                focused=self.focused_pane == "market_overview",
                show_sources=self.overview_show_sources,
            )
        )

        # Market pulse — top-right context pane
        layout["market_pulse"].update(
            create_market_pulse_panel(
                self.market_pulse,
                focused=self.focused_pane == "market_pulse",
                show_sources=self.pulse_show_sources,
            )
        )

        # Target list — bottom-left work pane
        if self.opened_business:
            layout["target_list"].update(
                create_business_profile_panel(
                    business=self.opened_business,
                    market_data=self.market_overview,
                )
            )
        elif visible_businesses:
            layout["target_list"].update(
                create_target_list_panel(
                    visible_businesses,
                    offset=self.scroll_offset,
                    limit=self.page_size,
                    selected_index=self.selected_index,
                    focused=self.focused_pane == "target_list",
                )
            )
        else:
            layout["target_list"].update(create_progress_panel(self.status))

        # Scout assistant — bottom-right work pane
        layout["scout_assistant"].update(
            create_scout_assistant_panel(
                self.chat_history,
                self.chat_input,
                self.chat_mode,
                scope_count=len(visible_businesses),
                active_filter=self.active_filter,
                focused=self.focused_pane == "scout_assistant",
                chat_scroll_offset=self.chat_scroll_offset,
            )
        )

        # Footer — single line
        layout["footer"].update(
            create_footer_text(
                has_selection=self.opened_business is not None,
                show_help=self.show_help,
                focused_pane=self.focused_pane,
                show_sources=self.overview_show_sources or self.pulse_show_sources,
                active_filter=bool(self.active_filter),
            )
        )

        return layout

    def _update_display(self) -> None:
        if self.live:
            self.live.update(self._build_layout())

    def _visible_businesses(self) -> List[Dict]:
        """Return the active business list (filtered if a filter is applied)."""
        return self.filtered_businesses if self.filtered_businesses is not None else self.businesses

    def clear_filter(self) -> None:
        """Clear any active assistant filter."""
        if self.filtered_businesses is not None:
            self.filtered_businesses = None
            self.active_filter = ""
            self.scroll_offset = 0
            self.selected_index = 0
            self.opened_business = None
            self._update_display()

    # ── Navigation ────────────────────────────────────────────────────────────

    def scroll_up(self) -> None:
        visible = self._visible_businesses()
        if not visible:
            return
        if self.selected_index > 0:
            self.selected_index -= 1
            if self.selected_index < self.scroll_offset:
                self.scroll_offset = self.selected_index
            self._update_display()

    def scroll_down(self) -> None:
        visible = self._visible_businesses()
        if not visible:
            return
        if self.selected_index < len(visible) - 1:
            self.selected_index += 1
            if self.selected_index >= self.scroll_offset + self.page_size:
                self.scroll_offset = self.selected_index - self.page_size + 1
            self._update_display()

    def page_up(self) -> None:
        if not self._visible_businesses():
            return
        self.scroll_offset = max(0, self.scroll_offset - self.page_size)
        self.selected_index = max(0, self.selected_index - self.page_size)
        self._update_display()

    def page_down(self) -> None:
        visible = self._visible_businesses()
        if not visible:
            return
        max_offset = max(0, len(visible) - self.page_size)
        self.scroll_offset = min(max_offset, self.scroll_offset + self.page_size)
        self.selected_index = min(
            max(0, len(visible) - 1),
            self.selected_index + self.page_size,
        )
        self._update_display()

    def scroll_to_top(self) -> None:
        if not self._visible_businesses():
            return
        self.scroll_offset = 0
        self.selected_index = 0
        self._update_display()

    def scroll_to_bottom(self) -> None:
        visible = self._visible_businesses()
        if not visible:
            return
        max_offset = max(0, len(visible) - self.page_size)
        self.scroll_offset = max_offset
        self.selected_index = max(0, len(visible) - 1)
        self._update_display()

    # ── Profile pane ──────────────────────────────────────────────────────────

    def select_business(self) -> None:
        """Open the profile pane for the currently highlighted business."""
        visible = self._visible_businesses()
        if visible and 0 <= self.selected_index < len(visible):
            self.opened_business = visible[self.selected_index]
            self._update_display()

    def close_detail(self) -> bool:
        """Close sources view or profile pane. Returns True if something was closed."""
        if self.overview_show_sources:
            self.overview_show_sources = False
            self._update_display()
            return True
        if self.pulse_show_sources:
            self.pulse_show_sources = False
            self._update_display()
            return True
        if self.opened_business is not None:
            self.opened_business = None
            self._update_display()
            return True
        return False

    # ── Pane navigation ───────────────────────────────────────────────────────

    _PANE_ORDER = ["market_overview", "market_pulse", "target_list", "scout_assistant"]

    def focus_next_pane(self) -> None:
        """Cycle focus to the next pane."""
        panes = self._PANE_ORDER
        idx = panes.index(self.focused_pane) if self.focused_pane in panes else 2
        self.focused_pane = panes[(idx + 1) % len(panes)]
        # Close any open sources view when leaving that pane
        if self.focused_pane != "market_overview":
            self.overview_show_sources = False
        if self.focused_pane != "market_pulse":
            self.pulse_show_sources = False
        self._update_display()

    def toggle_sources(self) -> None:
        """Toggle the sources drill-down for the focused pane (overview/pulse only)."""
        if self.focused_pane == "market_overview":
            self.overview_show_sources = not self.overview_show_sources
            self._update_display()
        elif self.focused_pane == "market_pulse":
            self.pulse_show_sources = not self.pulse_show_sources
            self._update_display()

    # ── Chat ──────────────────────────────────────────────────────────────────

    def enter_chat_mode(self) -> None:
        self.chat_mode = True
        self._update_display()

    def exit_chat_mode(self) -> None:
        self.chat_mode = False
        self.chat_input = ""
        self._update_display()

    def chat_type(self, char: str) -> None:
        self.chat_input += char
        self._update_display()

    def chat_backspace(self) -> None:
        if self.chat_input:
            self.chat_input = self.chat_input[:-1]
            self._update_display()

    def chat_scroll_up(self) -> None:
        """Scroll chat history up."""
        if self.chat_scroll_offset > 0:
            self.chat_scroll_offset -= 1
            self._update_display()

    def chat_scroll_down(self) -> None:
        """Scroll chat history down."""
        if self.chat_scroll_offset < max(0, len(self.chat_history) - 1):
            self.chat_scroll_offset += 1
            self._update_display()

    def chat_submit(self) -> None:
        q = self.chat_input.strip()
        if not q:
            self.exit_chat_mode()
            return
        # Optimistic UI: show question + thinking indicator
        self.chat_history.append({"q": q, "a": "thinking..."})
        self.chat_scroll_offset = max(0, len(self.chat_history) - 1)
        self.chat_input = ""
        self.chat_mode = False
        self._update_display()
        # Fire async API call
        threading.Thread(target=self._run_assistant, args=(q,), daemon=True).start()

    # ── Actions ───────────────────────────────────────────────────────────────

    def export_csv(self) -> None:
        visible = self._visible_businesses()
        if not visible:
            self.status = "No data to export"
            self._update_display()
            return
        try:
            self.status = "Exporting to CSV..."
            self._update_display()
            csv_path = export_to_csv(visible, self.industry, self.location)
            format_export_message(csv_path, len(visible))
            self.status = f"Exported → {csv_path}"
            self._update_display()
            time.sleep(2)
            self.status = "Ready"
            self._update_display()
        except Exception as e:
            error = handle_file_error(e, "CSV export", "write")
            self.status = f"Export failed: {str(e)}"
            self.error_message = format_error_message(error)
            self._update_display()
            time.sleep(2)
            self.status = "Ready"
            self._update_display()

    def toggle_help(self) -> None:
        self.show_help = not self.show_help
        self._update_display()

    def refresh_data(self) -> None:
        self.use_cache = False
        self.businesses = []
        self.filtered_businesses = None
        self.active_filter = ""
        self.scroll_offset = 0
        self.selected_index = 0
        self.opened_business = None
        self.status = "Refreshing data..."
        self._update_display()
        fetch_thread = threading.Thread(target=self._fetch_data)
        fetch_thread.daemon = True
        fetch_thread.start()

    def quit(self) -> None:
        self.status = "Goodbye!"
        self._update_display()
        self.keyboard_handler.stop()

    def set_error(self, error: str) -> None:
        self.error_message = error
        self.status = f"Error: {error}"
        self._update_display()

    def open_website(self) -> None:
        business = self._current_business()
        if not business:
            self.status = "No business selected"
            self._update_display()
            return
        website = business.get("website") or ""
        if not website:
            self.status = "No website available"
            self._update_display()
            return
        if not website.startswith(("http://", "https://")):
            website = f"https://{website}"
        try:
            webbrowser.open(website)
            self.status = "Opened website in browser"
            self._update_display()
        except Exception as e:
            self.status = f"Failed to open website: {e}"
            self._update_display()

    def open_reviews(self) -> None:
        business = self._current_business()
        if not business:
            self.status = "No business selected"
            self._update_display()
            return
        place_id = business.get("place_id") or ""
        if not place_id:
            self.status = "No reviews link available"
            self._update_display()
            return
        url = f"https://www.google.com/maps/search/?api=1&query_place_id={place_id}"
        try:
            webbrowser.open(url)
            self.status = "Opened reviews in browser"
            self._update_display()
        except Exception as e:
            self.status = f"Failed to open reviews: {e}"
            self._update_display()

    def _current_business(self) -> Optional[Dict]:
        if self.opened_business:
            return self.opened_business
        visible = self._visible_businesses()
        if visible and 0 <= self.selected_index < len(visible):
            return visible[self.selected_index]
        return None

    # ── Chat helpers ──────────────────────────────────────────────────────────

    def _build_assistant_context(self) -> str:
        """Build system prompt with full market context for Claude."""
        lines = [
            "You are Scout, a concise research assistant for small business acquisition.",
            "The user is evaluating businesses to potentially acquire.",
            "",
            f"MARKET: {self.industry} businesses in {self.location}",
            f"Total businesses found: {len(self.businesses)}",
            "",
        ]

        # Market financials
        overview = self.market_overview or MarketOverview()
        fin = overview.financial
        outlook = overview.outlook
        quality = overview.quality
        if fin.median_revenue:
            lines.append("MARKET BENCHMARKS:")
            lines.append(f"  Median revenue: {fin.median_revenue}")
            if fin.ebitda_margin:
                lines.append(f"  EBITDA margin: {fin.ebitda_margin} (range: {fin.margin_range or '—'})")
            if fin.typical_acquisition:
                lines.append(f"  Typical acquisition price: {fin.typical_acquisition}")
            if outlook.grade:
                lines.append(f"  Market grade: {outlook.grade}")
            if quality.avg_rating:
                lines.append(f"  Avg business rating: {quality.avg_rating}")
            lines.append("")

        # Business list
        visible = self._visible_businesses()
        if self.active_filter:
            lines.append(f"ACTIVE FILTER: {self.active_filter}")
            lines.append("")
        if visible:
            lines.append("BUSINESSES IN THIS MARKET:")
            sorted_biz = sorted(visible, key=lambda b: b.get("reviews") or 0, reverse=True)
            for i, b in enumerate(sorted_biz[:25], 1):
                name = b.get("name", "—")
                rating = b.get("rating", "")
                reviews = b.get("reviews") or 0
                phone = b.get("phone", "")
                website = b.get("website", "")
                conf = b.get("confidence", "")
                rev = b.get("est_revenue") or b.get("revenue", "")
                parts = [f"{i}. {name}"]
                if rating:
                    parts.append(f"{rating}★")
                if reviews:
                    parts.append(f"{reviews:,} reviews")
                if rev:
                    parts.append(f"~{rev} revenue")
                if conf:
                    parts.append(f"({conf} confidence)")
                if phone:
                    parts.append(f"phone: {phone}")
                if website:
                    parts.append(f"web: {website}")
                lines.append("  " + "  |  ".join(parts))
            lines.append("")

        # Pulse (opportunities and risks)
        pulse = self.market_pulse or MarketPulse()
        opps = pulse.opportunities
        risks = pulse.risks
        if opps:
            lines.append("MARKET OPPORTUNITIES: " + "; ".join(opps))
        if risks:
            lines.append("MARKET RISKS: " + "; ".join(risks))
        if opps or risks:
            lines.append("")

        lines.extend([
            "INSTRUCTIONS:",
            "- Answer in 1-4 sentences. Be specific — cite business names and exact numbers.",
            "- If asked to find or filter businesses, list matching names with their key stats.",
            "- If asked about market outlook, cite the grade and benchmark figures.",
            "- Do not repeat back the question. Get straight to the answer.",
            "",
            "If a structured action is needed, append a line exactly like:",
            'ACTION:{"type":"filter","field":"reviews","op":"gte","value":150,"label":"reviews ≥ 150"}',
            "Valid fields: reviews, rating, name, address, category.",
            "Valid ops: gte, lte, eq, contains.",
        ])
        return "\n".join(lines)

    def _extract_assistant_action(self, text: str) -> tuple[str, Optional[Dict]]:
        """Extract ACTION JSON from assistant response."""
        match = re.search(r"\n?ACTION:(\{.*\})\s*$", text.strip(), re.DOTALL)
        if not match:
            return text, None
        raw = match.group(1)
        try:
            action = json.loads(raw)
        except json.JSONDecodeError:
            return text, None
        cleaned = text[: match.start()].rstrip()
        return cleaned, action

    def _filter_businesses(self, action: Dict) -> Optional[List[Dict]]:
        field = (action.get("field") or "").lower()
        op = (action.get("op") or "").lower()
        value = action.get("value")

        if field not in {"reviews", "rating", "name", "address", "category"}:
            return None
        if op not in {"gte", "lte", "eq", "contains"}:
            return None

        def _get_val(biz: Dict):
            if field in {"reviews", "rating"}:
                return biz.get(field) or 0
            return str(biz.get(field) or "")

        def _match(biz: Dict) -> bool:
            v = _get_val(biz)
            if op == "contains":
                return str(value or "").lower() in str(v).lower()
            try:
                v_num = float(v)
                target = float(value)
            except (TypeError, ValueError):
                return False
            if op == "gte":
                return v_num >= target
            if op == "lte":
                return v_num <= target
            return v_num == target

        return [b for b in self.businesses if _match(b)]

    def _summarize_filter(self, filtered: List[Dict]) -> str:
        if not filtered:
            return "No businesses match that filter."
        top = filtered[:5]
        parts = []
        for b in top:
            name = b.get("name", "—")
            rating = b.get("rating")
            reviews = b.get("reviews")
            stats = []
            if rating:
                stats.append(f"{rating}★")
            if reviews:
                stats.append(f"{reviews} reviews")
            stat_str = f" ({', '.join(stats)})" if stats else ""
            parts.append(f"{name}{stat_str}")
        suffix = "" if len(filtered) <= 5 else f" (+{len(filtered) - 5} more)"
        return f"{len(filtered)} match: " + ", ".join(parts) + suffix

    def _apply_assistant_action(self, action: Dict) -> Optional[str]:
        action_type = (action.get("type") or "").lower()
        if action_type == "filter":
            filtered = self._filter_businesses(action)
            if filtered is None:
                return "Could not apply that filter."
            self.filtered_businesses = filtered
            self.active_filter = action.get("label") or f"{action.get('field')} {action.get('op')} {action.get('value')}"
            self.scroll_offset = 0
            self.selected_index = 0
            self.opened_business = None
            return self._summarize_filter(filtered)
        if action_type == "clear_filter":
            self.clear_filter()
            return "Filter cleared."
        return None

    def _run_assistant(self, query: str) -> None:
        """Call Claude API with streaming, update last chat entry in real time."""
        from scout import config
        if not config.ANTHROPIC_API_KEY:
            self.chat_history[-1]["a"] = (
                "ANTHROPIC_API_KEY not configured.\n"
                "Add it to your .env file to enable the scout assistant."
            )
            self._update_display()
            return
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
            system = self._build_assistant_context()
            buffer = ""
            with client.messages.stream(
                model="claude-sonnet-4-6",
                max_tokens=400,
                system=system,
                messages=[{"role": "user", "content": query}],
            ) as stream:
                for text in stream.text_stream:
                    buffer += text
                    self.chat_history[-1]["a"] = buffer + "▌"
                    self._update_display()
            cleaned, action = self._extract_assistant_action(buffer)
            action_note = self._apply_assistant_action(action) if action else None
            if action_note:
                if cleaned:
                    self.chat_history[-1]["a"] = f"{cleaned}\n{action_note}"
                else:
                    self.chat_history[-1]["a"] = action_note
            else:
                self.chat_history[-1]["a"] = cleaned or buffer
            self._update_display()
        except ImportError:
            self.chat_history[-1]["a"] = (
                "anthropic package not installed.\n"
                "Run: pip install anthropic"
            )
            self._update_display()
        except Exception as e:
            self.chat_history[-1]["a"] = f"Error: {str(e)}"
            self._update_display()

    # ── Helpers ──────────────────────────────────────────────────────────────

    def _on_pipeline_progress(self, stage: str, status: str, count: int = 0) -> None:
        """Receive progress update from ResearchMarket pipeline."""
        self.pipeline_stages[stage] = status
        if count:
            self.pipeline_counts[stage] = count
        self._update_display()

    def _business_to_dict(self, business) -> Dict:
        signals = []
        if business.rating is not None:
            signals.append(f"{business.rating}★")
        if business.reviews:
            signals.append(f"{business.reviews} reviews")
        extra_signals = getattr(business, "signals", None) or []
        if extra_signals:
            signals.extend(extra_signals)
        return {
            "name": business.name,
            "address": business.address,
            "phone": business.phone,
            "website": business.website,
            "category": business.category,
            "rating": business.rating,
            "reviews": business.reviews,
            "place_id": business.place_id,
            "lat": business.lat,
            "lng": business.lng,
            "est_revenue": _format_money(business.estimated_revenue) if business.estimated_revenue else "",
            "est_cash_flow": business.estimated_cash_flow,
            "est_value": business.estimated_value,
            "revenue": _format_money(business.estimated_revenue) if business.estimated_revenue else "",
            "ebitda": _format_money(business.estimated_cash_flow) if business.estimated_cash_flow else "",
            "valuation": _format_money(business.estimated_value) if business.estimated_value else "",
            "confidence": business.confidence,
            "signals": signals,
            "location": getattr(business, "location", None),
            "review_themes_pos": getattr(business, "review_themes_pos", None),
            "next_steps": getattr(business, "next_steps", None),
            "revenue_vs_median": getattr(business, "revenue_vs_median", None),
            "ebitda_vs_median": getattr(business, "ebitda_vs_median", None),
        }

    def _market_overview_from_result(self, result) -> MarketOverview:
        overview = {
            "total_businesses": len(result.businesses),
            "market_density": "—",
            "financial": {
                "fdd_count": 0,
                "confidence": "—",
                "median_revenue": "—",
                "revenue_range": "",
                "ebitda_margin": "—",
                "margin_range": "",
                "typical_acquisition": "—",
            },
            "quality": {
                "avg_rating": self._avg_rating(result.businesses),
                "sentiment_positive": 0,
                "review_volume": self._total_reviews(result.businesses),
            },
            "trends": {},
            "outlook": {"grade": "—", "note": ""},
        }

        if result.summary.benchmarks:
            b = result.summary.benchmarks[0]
            overview["financial"] = {
                "fdd_count": b.sample_size,
                "confidence": "medium" if b.sample_size >= 5 else "low",
                "median_revenue": _format_money(b.median_revenue),
                "revenue_range": "",
                "ebitda_margin": f"{b.margin_pct:.1f}%" if b.margin_pct else "—",
                "margin_range": "",
                "typical_acquisition": "—",
            }

        return MarketOverview.from_dict(overview)

    def _market_pulse_placeholder(self) -> MarketPulse:
        return MarketPulse.from_dict(
            {
                "business_model": {
                    "customers": "—",
                    "revenue": "—",
                },
                "operating_models": [],
                "opportunities": [],
                "risks": [],
                "sources": {
                    "reddit": 0,
                    "reviews": 0,
                    "reports": 0,
                    "listings": 0,
                },
            }
        )

    def _avg_rating(self, businesses) -> float:
        ratings = [b.rating for b in businesses if b.rating is not None]
        if not ratings:
            return 0.0
        return round(sum(ratings) / len(ratings), 2)

    def _total_reviews(self, businesses) -> int:
        reviews = [b.reviews or 0 for b in businesses]
        return sum(reviews)


def _format_money(value: Optional[float]) -> str:
    if value is None:
        return "—"
    if value >= 1_000_000:
        return f"${value/1_000_000:.1f}M"
    if value >= 1_000:
        return f"${value/1_000:.0f}K"
    return f"${value:.0f}"
