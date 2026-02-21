"""Rich terminal UI controller for Scout — 4-pane Bloomberg layout"""

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
    # legacy compat
    create_header,
    create_business_table,
    create_footer,
    create_detail_panel,
    create_status_bar,
    create_footer_instructions,
)
from .keyboard import KeyboardHandler
from scout.shared.export import export_to_csv, format_export_message
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
    ):
        self.industry = industry
        self.location = location
        self.use_cache = use_cache
        self.max_results = max_results

        # Data
        self.businesses: List[Dict] = []
        self.market_overview: Dict = {}
        self.market_pulse: Dict = {}

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
        self.page_size = 8

        # Chat state
        self.chat_history: List[Dict] = []
        self.chat_input: str = ""
        self.chat_mode: bool = False
        self.chat_scroll_offset: int = 0

        # Pane focus state
        self.focused_pane: str = "target_list"  # market_overview | market_pulse | target_list | scout_assistant
        self.overview_show_sources: bool = False
        self.pulse_show_sources: bool = False
        self.query_string: str = ""

        self.live: Optional[Live] = None
        self.keyboard_handler = KeyboardHandler(self)

        if initial_result is not None:
            self._seed_from_result(initial_result)

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

            self.status = "Searching data sources..."
            self._update_display()

            use_case = ResearchMarket()
            result = use_case.run(
                industry=self.industry,
                location=self.location,
                max_results=self.max_results,
                use_cache=self.use_cache,
                include_benchmarks=True,
            )

            self.businesses = [self._business_to_dict(b) for b in result.businesses]
            # Keep source order; no scoring-based ranking for now.
            self.market_overview = result.market_overview or self._market_overview_from_result(result)
            self.market_pulse = result.pulse or self._market_pulse_placeholder()
            self.cached = self.use_cache
            self.selected_index = 0
            self.status = "Ready"
            self._update_display()

        except ConnectionError:
            self.status = "Error: network connection failed"
            self.error_message = "Network connection failed."
            self._update_display()

        except Exception as e:
            api_error = handle_api_error(e, "Google Maps")
            self.status = f"Error: {str(e)}"
            self.error_message = format_error_message(api_error)
            self._update_display()

    def _seed_from_result(self, result) -> None:
        """Seed the UI with a precomputed ResearchResult (mock or cached)."""
        self.businesses = [self._business_to_dict(b) for b in result.businesses]
        # Keep source order; no scoring-based ranking for now.
        self.market_overview = result.market_overview or self._market_overview_from_result(result)
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

    def _build_layout(self) -> Layout:
        """Build the 4-pane layout with current state."""
        layout = create_main_layout()

        # Header — single line
        layout["header"].update(
            create_header_text(
                industry=self.industry,
                location=self.location,
                count=len(self.businesses),
                cached=self.cached,
                status=self.status,
                grade=(self.market_overview.get("outlook", {}) or {}).get("grade", ""),
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
        elif self.businesses:
            layout["target_list"].update(
                create_target_list_panel(
                    self.businesses,
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
                scope_count=len(self.businesses),
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
            )
        )

        return layout

    def _update_display(self) -> None:
        if self.live:
            self.live.update(self._build_layout())

    # ── Navigation ────────────────────────────────────────────────────────────

    def scroll_up(self) -> None:
        if not self.businesses:
            return
        if self.selected_index > 0:
            self.selected_index -= 1
            if self.selected_index < self.scroll_offset:
                self.scroll_offset = self.selected_index
            self._update_display()

    def scroll_down(self) -> None:
        if not self.businesses:
            return
        if self.selected_index < len(self.businesses) - 1:
            self.selected_index += 1
            if self.selected_index >= self.scroll_offset + self.page_size:
                self.scroll_offset = self.selected_index - self.page_size + 1
            self._update_display()

    def page_up(self) -> None:
        self.scroll_offset = max(0, self.scroll_offset - self.page_size)
        self.selected_index = max(0, self.selected_index - self.page_size)
        self._update_display()

    def page_down(self) -> None:
        max_offset = max(0, len(self.businesses) - self.page_size)
        self.scroll_offset = min(max_offset, self.scroll_offset + self.page_size)
        self.selected_index = min(
            max(0, len(self.businesses) - 1),
            self.selected_index + self.page_size,
        )
        self._update_display()

    def scroll_to_top(self) -> None:
        self.scroll_offset = 0
        self.selected_index = 0
        self._update_display()

    def scroll_to_bottom(self) -> None:
        max_offset = max(0, len(self.businesses) - self.page_size)
        self.scroll_offset = max_offset
        self.selected_index = max(0, len(self.businesses) - 1)
        self._update_display()

    # ── Profile pane ──────────────────────────────────────────────────────────

    def select_business(self) -> None:
        """Open the profile pane for the currently highlighted business."""
        if self.businesses and 0 <= self.selected_index < len(self.businesses):
            self.opened_business = self.businesses[self.selected_index]
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
        if not self.businesses:
            self.status = "No data to export"
            self._update_display()
            return
        try:
            self.status = "Exporting to CSV..."
            self._update_display()
            csv_path = export_to_csv(self.businesses, self.industry, self.location)
            format_export_message(csv_path, len(self.businesses))
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
        if self.businesses and 0 <= self.selected_index < len(self.businesses):
            return self.businesses[self.selected_index]
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
        fin = (self.market_overview or {}).get("financial", {})
        outlook = (self.market_overview or {}).get("outlook", {})
        quality = (self.market_overview or {}).get("quality", {})
        if fin.get("median_revenue"):
            lines.append("MARKET BENCHMARKS:")
            lines.append(f"  Median revenue: {fin.get('median_revenue', '—')}")
            if fin.get("ebitda_margin"):
                lines.append(f"  EBITDA margin: {fin.get('ebitda_margin', '—')} (range: {fin.get('margin_range', '—')})")
            if fin.get("typical_acquisition"):
                lines.append(f"  Typical acquisition price: {fin.get('typical_acquisition', '—')}")
            if outlook.get("grade"):
                lines.append(f"  Market grade: {outlook.get('grade', '—')}")
            if quality.get("avg_rating"):
                lines.append(f"  Avg business rating: {quality.get('avg_rating', '—')}")
            lines.append("")

        # Business list
        if self.businesses:
            lines.append("BUSINESSES IN THIS MARKET:")
            sorted_biz = sorted(self.businesses, key=lambda b: b.get("reviews") or 0, reverse=True)
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
        pulse = self.market_pulse or {}
        opps = pulse.get("opportunities", [])
        risks = pulse.get("risks", [])
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
        ])
        return "\n".join(lines)

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
            self.chat_history[-1]["a"] = buffer
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

    def _business_to_dict(self, business) -> Dict:
        score = 0
        if business.rating is not None:
            score = int(round(business.rating * 20))
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
            "score": score,
            "signals": signals,
            "location": getattr(business, "location", None),
            "review_themes_pos": getattr(business, "review_themes_pos", None),
            "next_steps": getattr(business, "next_steps", None),
            "revenue_vs_median": getattr(business, "revenue_vs_median", None),
            "ebitda_vs_median": getattr(business, "ebitda_vs_median", None),
        }

    def _market_overview_from_result(self, result) -> Dict:
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

        return overview

    def _market_pulse_placeholder(self) -> Dict:
        return {
            "business_model": {
                "customers": "—",
                "revenue": "—",
            },
            "operating_models": [],
            "opportunities": [],
            "risks": [],
            "sources": {
                "reddit": "—",
                "reviews": "—",
                "reports": "—",
                "listings": "—",
            },
        }

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
