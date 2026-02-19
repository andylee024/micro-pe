"""Rich terminal UI controller for Scout"""

import threading
import time
from typing import Dict, List, Optional
from pathlib import Path

from rich.console import Console
from rich.live import Live
from rich.layout import Layout

from .components import (
    create_header,
    create_business_table,
    create_status_bar,
    create_progress_panel,
    create_help_panel,
    create_footer_instructions,
    create_main_layout
)
from .keyboard import KeyboardHandler
from scout.utils.export import export_to_csv, format_export_message
from scout.utils.errors import (
    handle_errors,
    handle_api_error,
    handle_file_error,
    format_error_message
)


class ScoutTerminal:
    """Terminal UI controller using Rich library"""

    def __init__(
        self,
        industry: str,
        location: str,
        use_cache: bool = True,
        max_results: int = 500
    ):
        """Initialize Scout terminal UI

        Args:
            industry: Industry/business type to search for
            location: Geographic location to search in
            use_cache: Whether to use cached data
            max_results: Maximum number of businesses to fetch
        """
        self.industry = industry
        self.location = location
        self.use_cache = use_cache
        self.max_results = max_results

        # UI state
        self.console = Console()
        self.businesses: List[Dict] = []
        self.status = "Initializing..."
        self.scroll_offset = 0
        self.cached = False
        self.show_help = False
        self.error_message: Optional[str] = None

        # UI constants
        self.page_size = 20  # Number of businesses to show at once

        # Live display reference
        self.live: Optional[Live] = None

        # Keyboard handler
        self.keyboard_handler = KeyboardHandler(self)

    def run(self) -> None:
        """Main entry point - launch terminal UI"""
        try:
            with Live(
                self._build_layout(),
                console=self.console,
                refresh_per_second=4,
                screen=True
            ) as live:
                self.live = live

                # Fetch data in a separate thread
                fetch_thread = threading.Thread(target=self._fetch_data)
                fetch_thread.daemon = True
                fetch_thread.start()

                # Handle keyboard events in main thread
                self.keyboard_handler.handle_event_loop()

                # Wait for fetch to complete if still running
                if fetch_thread.is_alive():
                    fetch_thread.join(timeout=1.0)

        except KeyboardInterrupt:
            self.console.print("\n[yellow]Exiting Scout...[/yellow]")
        except Exception as e:
            self.console.print(f"\n[red]Error: {str(e)}[/red]")

    def _fetch_data(self) -> None:
        """Fetch data from Google Maps with progress updates

        This runs in a background thread to allow keyboard input
        """
        try:
            # Import here to avoid circular dependency
            from tools.google_maps_tool import GoogleMapsTool

            # Update status
            self.status = "Searching Google Maps..."
            self._update_display()

            # Initialize Google Maps tool
            tool = GoogleMapsTool()

            # Search for businesses
            result = tool.search(
                industry=self.industry,
                location=self.location,
                max_results=self.max_results,
                use_cache=self.use_cache
            )

            # Extract results
            self.businesses = result.get('results', [])
            self.cached = result.get('cached', False)

            # Update status
            self.status = "Ready"
            self._update_display()

        except ConnectionError as e:
            # Network connection error
            error_msg = "Network connection failed. Please check your internet connection."
            self.status = f"Error: {error_msg}"
            self.error_message = error_msg
            self._update_display()

        except Exception as e:
            # Handle API errors gracefully
            api_error = handle_api_error(e, "Google Maps")
            error_msg = format_error_message(api_error)
            self.status = f"Error: {str(e)}"
            self.error_message = error_msg
            self._update_display()

    def _build_layout(self) -> Layout:
        """Build Rich Layout with header, table, footer

        Returns:
            Rich Layout with current UI state
        """
        layout = create_main_layout()

        # Build header
        query_text = f"{self.industry} in {self.location}"
        layout["header"].update(create_header(query_text))

        # Build body - either help panel or business table
        if self.show_help:
            layout["body"].update(create_help_panel())
        elif self.businesses:
            layout["body"].update(
                create_business_table(
                    self.businesses,
                    offset=self.scroll_offset,
                    limit=self.page_size
                )
            )
        else:
            # Show progress during data fetch
            layout["body"].update(create_progress_panel(self.status))

        # Build footer instructions
        layout["instructions"].update(create_footer_instructions())

        # Build status bar
        layout["status"].update(
            create_status_bar(
                num_businesses=len(self.businesses),
                cached=self.cached,
                status_message=self.status
            )
        )

        return layout

    def _update_display(self) -> None:
        """Update the live display with current state"""
        if self.live:
            self.live.update(self._build_layout())

    # Keyboard action handlers

    def scroll_up(self) -> None:
        """Scroll up one row"""
        if self.scroll_offset > 0:
            self.scroll_offset -= 1
            self._update_display()

    def scroll_down(self) -> None:
        """Scroll down one row"""
        max_offset = max(0, len(self.businesses) - self.page_size)
        if self.scroll_offset < max_offset:
            self.scroll_offset += 1
            self._update_display()

    def page_up(self) -> None:
        """Scroll up one page"""
        self.scroll_offset = max(0, self.scroll_offset - self.page_size)
        self._update_display()

    def page_down(self) -> None:
        """Scroll down one page"""
        max_offset = max(0, len(self.businesses) - self.page_size)
        self.scroll_offset = min(max_offset, self.scroll_offset + self.page_size)
        self._update_display()

    def scroll_to_top(self) -> None:
        """Scroll to the top of the list"""
        self.scroll_offset = 0
        self._update_display()

    def scroll_to_bottom(self) -> None:
        """Scroll to the bottom of the list"""
        max_offset = max(0, len(self.businesses) - self.page_size)
        self.scroll_offset = max_offset
        self._update_display()

    def export_csv(self) -> None:
        """Export businesses to CSV file"""
        if not self.businesses:
            self.status = "No data to export"
            self._update_display()
            return

        try:
            self.status = "Exporting to CSV..."
            self._update_display()

            # Export to CSV
            csv_path = export_to_csv(
                self.businesses,
                self.industry,
                self.location
            )

            # Format success message
            success_msg = format_export_message(csv_path, len(self.businesses))

            # Update status with success message
            self.status = f"✅ Exported {len(self.businesses)} businesses to {csv_path.name}"
            self._update_display()

            # Show success for a moment
            time.sleep(2)

            # Return to ready state
            self.status = "Ready"
            self._update_display()

        except Exception as e:
            # Handle export errors gracefully
            error = handle_file_error(e, "CSV export", "write")
            error_msg = format_error_message(error)
            self.status = f"Export failed: {str(e)}"
            self.error_message = error_msg
            self._update_display()
            time.sleep(2)
            self.status = "Ready"
            self._update_display()

    def toggle_help(self) -> None:
        """Toggle help panel visibility"""
        self.show_help = not self.show_help
        self._update_display()

    def refresh_data(self) -> None:
        """Refresh data from Google Maps (bypass cache)"""
        self.use_cache = False
        self.businesses = []
        self.scroll_offset = 0
        self.status = "Refreshing data..."
        self._update_display()

        # Fetch data in background thread
        fetch_thread = threading.Thread(target=self._fetch_data)
        fetch_thread.daemon = True
        fetch_thread.start()

    def quit(self) -> None:
        """Quit the application"""
        self.status = "Goodbye!"
        self._update_display()
        self.keyboard_handler.stop()

    def set_error(self, error: str) -> None:
        """Set an error message

        Args:
            error: Error message to display
        """
        self.error_message = error
        self.status = f"Error: {error}"
        self._update_display()
