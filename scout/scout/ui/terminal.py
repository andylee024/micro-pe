"""Rich terminal UI controller for Scout — 4-pane Bloomberg layout"""

import threading
import time
from typing import Dict, List, Optional
from pathlib import Path

from rich.console import Console
from rich.live import Live
from rich.layout import Layout

from .components import (
    create_market_overview_panel,
    create_target_list_panel,
    create_business_profile_panel,
    create_market_pulse_panel,
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

        # Page size for target list pane (half-height, 2 lines/biz)
        self.page_size = 8

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
            self.businesses.sort(key=lambda b: b.get("score", 0) or 0, reverse=True)
            self.market_overview = self._market_overview_from_result(result)
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
        self.businesses.sort(key=lambda b: b.get("score", 0) or 0, reverse=True)
        self.market_overview = self._market_overview_from_result(result)
        self.market_pulse = result.pulse or self._market_pulse_placeholder()
        self.cached = True
        self.selected_index = 0
        self.status = "Ready (mock data)"

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
            )
        )

        # Help overlay replaces the profile pane
        if self.show_help:
            layout["business_profile"].update(create_help_panel())
        else:
            layout["business_profile"].update(
                create_business_profile_panel(
                    business=self.opened_business,
                    market_data=self.market_overview or None,
                )
            )

        # Market overview (always shown)
        layout["market_overview"].update(
            create_market_overview_panel(self.market_overview)
        )

        # Target list — loading spinner or business list
        if self.businesses:
            layout["target_list"].update(
                create_target_list_panel(
                    self.businesses,
                    offset=self.scroll_offset,
                    limit=self.page_size,
                    selected_index=self.selected_index,
                )
            )
        else:
            layout["target_list"].update(create_progress_panel(self.status))

        # Market pulse (always shown)
        layout["market_pulse"].update(
            create_market_pulse_panel(self.market_pulse)
        )

        # Footer — single line
        layout["footer"].update(
            create_footer_text(
                has_selection=self.opened_business is not None,
                show_help=self.show_help,
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

    def close_detail(self) -> None:
        """Clear the profile pane."""
        self.opened_business = None
        self._update_display()

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
            self.status = f"Exported {len(self.businesses)} businesses to {csv_path.name}"
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
            "reddit": {
                "thread_count": 0,
                "overall": "—",
                "overall_emoji": "😐",
                "positive_pct": 0,
                "key_points_pos": [],
                "key_points_neg": [],
            },
            "trends": {"job_postings": "—", "new_entrants": "—"},
            "insights": [],
            "green_flags": [],
            "red_flags": [],
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
