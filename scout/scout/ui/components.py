"""UI components for Rich terminal display"""

from typing import Dict, List
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.layout import Layout
from rich.align import Align


def create_header(query: str, industry: str = "", location: str = "") -> Panel:
    """Create header panel with query information

    Args:
        query: The search query string
        industry: Industry/business type (optional)
        location: Location/geographic area (optional)

    Returns:
        Rich Panel with header information
    """
    header_text = Text()
    header_text.append("SCOUT", style="bold cyan")
    header_text.append(" - Market Research\n", style="bold white")

    # Show query or industry/location if provided
    if industry and location:
        header_text.append(f"Query: {industry} in {location}", style="white")
    else:
        header_text.append(f"Query: {query}", style="white")

    return Panel(
        Align.center(header_text),
        style="bold white on blue",
        border_style="cyan"
    )


def create_business_table(
    businesses: List[Dict],
    offset: int = 0,
    limit: int = 20
) -> Table:
    """Create scrollable business table

    Args:
        businesses: List of business dictionaries
        offset: Starting index for display
        limit: Maximum number of businesses to show

    Returns:
        Rich Table with business data
    """
    table = Table(
        title=f"[bold cyan]Businesses[/bold cyan] [white]({len(businesses)} results)[/white]",
        show_header=True,
        header_style="bold cyan",
        border_style="cyan",
        show_lines=False,
        expand=True
    )

    table.add_column("Name", style="cyan", no_wrap=False, width=30)
    table.add_column("Phone", style="green", width=18)
    table.add_column("Website", style="blue", no_wrap=False, width=30)
    table.add_column("Address", style="white", no_wrap=False)

    # Calculate end index
    end_idx = min(offset + limit, len(businesses))

    # Add rows for visible businesses
    for biz in businesses[offset:end_idx]:
        table.add_row(
            biz.get('name', 'N/A'),
            biz.get('phone', 'N/A'),
            biz.get('website', 'N/A'),
            biz.get('address', 'N/A')
        )

    # Add footer row showing range
    if businesses:
        footer_text = f"Showing {offset + 1}-{end_idx} of {len(businesses)} businesses"
        table.caption = f"[dim]{footer_text}[/dim]"

    return table


def create_status_bar(
    num_businesses: int,
    cached: bool = False,
    status_message: str = "Ready"
) -> Panel:
    """Create status bar at bottom

    Args:
        num_businesses: Number of businesses found
        cached: Whether data was retrieved from cache
        status_message: Current status message

    Returns:
        Rich Panel with status information
    """
    cache_status = "Cached for 90 days" if cached else "Fresh data"

    status_text = Text()
    status_text.append("Status: ", style="dim white")
    status_text.append(status_message, style="green")
    status_text.append(f" • {num_businesses} businesses found • ", style="dim white")
    status_text.append(cache_status, style="yellow" if cached else "green")

    return Panel(
        status_text,
        style="dim white on black",
        border_style="dim cyan"
    )


def create_progress_panel(message: str, spinner: bool = True) -> Panel:
    """Create progress indicator

    Args:
        message: Progress message to display
        spinner: Whether to show a spinner character

    Returns:
        Rich Panel with progress information
    """
    progress_text = Text()
    if spinner:
        progress_text.append("⠋ ", style="yellow")
    progress_text.append(message, style="yellow")

    return Panel(
        progress_text,
        title="[bold yellow]Building Universe[/bold yellow]",
        style="yellow",
        border_style="yellow"
    )


def create_help_panel() -> Panel:
    """Create help panel showing keyboard shortcuts

    Returns:
        Rich Panel with keyboard shortcuts
    """
    help_text = Text()
    help_text.append("Keyboard Shortcuts\n\n", style="bold cyan")

    shortcuts = [
        ("↑ / ↓", "Scroll through businesses"),
        ("E", "Export to CSV"),
        ("Q", "Quit application"),
        ("H", "Show/hide this help"),
    ]

    for key, description in shortcuts:
        help_text.append(f"  {key:10}", style="bold green")
        help_text.append(f" {description}\n", style="white")

    return Panel(
        help_text,
        title="[bold cyan]Help[/bold cyan]",
        style="white on black",
        border_style="cyan"
    )


def create_footer_instructions() -> Panel:
    """Create footer with keyboard instruction hints

    Returns:
        Rich Panel with instruction hints
    """
    instructions = Text()
    instructions.append("[↑↓]", style="bold green")
    instructions.append(" Scroll  ", style="dim white")
    instructions.append("[E]", style="bold green")
    instructions.append("xport CSV  ", style="dim white")
    instructions.append("[Q]", style="bold green")
    instructions.append("uit  ", style="dim white")
    instructions.append("[H]", style="bold green")
    instructions.append("elp", style="dim white")

    return Panel(
        Align.center(instructions),
        style="dim white on black",
        border_style="dim cyan"
    )


def create_main_layout() -> Layout:
    """Create the main application layout

    Returns:
        Rich Layout with organized sections
    """
    layout = Layout()

    # Split into header, body, footer
    layout.split_column(
        Layout(name="header", size=5),
        Layout(name="body"),
        Layout(name="instructions", size=3),
        Layout(name="status", size=3)
    )

    return layout


def create_layout(header: Panel, table: Table, status: Panel, progress: Panel = None) -> Layout:
    """Combine all components into main layout

    Args:
        header: Header panel with query information
        table: Business table with data
        status: Status bar panel
        progress: Optional progress panel (shown during loading)

    Returns:
        Rich Layout with all components assembled
    """
    layout = Layout()

    if progress:
        # During loading: header, progress, status
        layout.split_column(
            Layout(header, name="header", size=5),
            Layout(progress, name="progress", size=7),
            Layout(status, name="status", size=3)
        )
    else:
        # Normal view: header, table, instructions, status
        layout.split_column(
            Layout(header, name="header", size=5),
            Layout(table, name="body"),
            Layout(create_footer_instructions(), name="instructions", size=3),
            Layout(status, name="status", size=3)
        )

    return layout
