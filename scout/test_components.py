#!/usr/bin/env python3
"""Test script to verify Rich UI components render correctly"""

from rich.console import Console
from scout.ui.components import (
    create_header,
    create_business_table,
    create_status_bar,
    create_progress_panel,
    create_help_panel,
    create_layout
)

# Sample business data
SAMPLE_BUSINESSES = [
    {
        "name": "Cool Air HVAC",
        "phone": "(310) 555-0100",
        "website": "coolair.com",
        "address": "1234 Wilshire Blvd, Los Angeles, CA 90010"
    },
    {
        "name": "Premier Climate",
        "phone": "(310) 555-0200",
        "website": "premierclimate.com",
        "address": "456 Main St, Santa Monica, CA 90401"
    },
    {
        "name": "SoCal Heating & Air",
        "phone": "(626) 555-0300",
        "website": "socalheating.com",
        "address": "789 Colorado Blvd, Pasadena, CA 91105"
    },
    {
        "name": "Valley Air Experts",
        "phone": "(818) 555-0400",
        "website": "valleyairexperts.com",
        "address": "321 Ventura Blvd, Sherman Oaks, CA 91403"
    },
    {
        "name": "West Coast Climate",
        "phone": "(424) 555-0500",
        "website": "westcoastclimate.com",
        "address": "654 Ocean Ave, Santa Monica, CA 90402"
    }
]

console = Console()

def test_individual_components():
    """Test each component individually"""
    console.print("\n[bold cyan]Testing Individual Components[/bold cyan]\n")

    # Test 1: Header with query
    console.print("[yellow]1. Header Component (query only):[/yellow]")
    header1 = create_header("HVAC businesses in Los Angeles")
    console.print(header1)
    console.print()

    # Test 2: Header with industry and location
    console.print("[yellow]2. Header Component (industry + location):[/yellow]")
    header2 = create_header("HVAC businesses in Los Angeles", industry="HVAC", location="Los Angeles")
    console.print(header2)
    console.print()

    # Test 3: Business table
    console.print("[yellow]3. Business Table (offset=0, limit=5):[/yellow]")
    table = create_business_table(SAMPLE_BUSINESSES, offset=0, limit=5)
    console.print(table)
    console.print()

    # Test 4: Business table with scrolling
    console.print("[yellow]4. Business Table (offset=2, limit=3):[/yellow]")
    table_scroll = create_business_table(SAMPLE_BUSINESSES, offset=2, limit=3)
    console.print(table_scroll)
    console.print()

    # Test 5: Status bar (cached)
    console.print("[yellow]5. Status Bar (cached):[/yellow]")
    status_cached = create_status_bar(len(SAMPLE_BUSINESSES), cached=True)
    console.print(status_cached)
    console.print()

    # Test 6: Status bar (fresh)
    console.print("[yellow]6. Status Bar (fresh):[/yellow]")
    status_fresh = create_status_bar(len(SAMPLE_BUSINESSES), cached=False)
    console.print(status_fresh)
    console.print()

    # Test 7: Progress panel
    console.print("[yellow]7. Progress Panel:[/yellow]")
    progress = create_progress_panel("Searching Google Maps...")
    console.print(progress)
    console.print()

    # Test 8: Progress panel (success)
    console.print("[yellow]8. Progress Panel (success):[/yellow]")
    progress_success = create_progress_panel("✓ Found 487 businesses", spinner=False)
    console.print(progress_success)
    console.print()

    # Test 9: Help panel
    console.print("[yellow]9. Help Panel:[/yellow]")
    help_panel = create_help_panel()
    console.print(help_panel)
    console.print()


def test_full_layout():
    """Test the complete layout with all components"""
    console.print("\n[bold cyan]Testing Full Layout[/bold cyan]\n")

    # Create all components
    header = create_header("HVAC businesses in Los Angeles", industry="HVAC", location="Los Angeles")
    table = create_business_table(SAMPLE_BUSINESSES, offset=0, limit=5)
    status = create_status_bar(len(SAMPLE_BUSINESSES), cached=True)

    # Test layout without progress
    console.print("[yellow]Full Layout (normal view):[/yellow]")
    layout = create_layout(header, table, status)
    console.print(layout)
    console.print()

    # Test layout with progress
    console.print("[yellow]Full Layout (with progress):[/yellow]")
    progress = create_progress_panel("Searching Google Maps...")
    layout_progress = create_layout(header, table, status, progress=progress)
    console.print(layout_progress)
    console.print()


def test_bloomberg_style():
    """Test Bloomberg-style appearance"""
    console.print("\n[bold cyan]Testing Bloomberg-Style Appearance[/bold cyan]\n")

    # Create a more realistic dataset
    businesses = SAMPLE_BUSINESSES * 100  # 500 businesses

    header = create_header("HVAC businesses in Los Angeles", industry="HVAC", location="Los Angeles")
    table = create_business_table(businesses, offset=0, limit=20)
    status = create_status_bar(len(businesses), cached=True, status_message="Ready")

    console.print("[yellow]Bloomberg-style Terminal View:[/yellow]")
    layout = create_layout(header, table, status)
    console.print(layout)


if __name__ == "__main__":
    console.rule("[bold cyan]Scout UI Components Test Suite[/bold cyan]")

    # Run all tests
    test_individual_components()
    test_full_layout()
    test_bloomberg_style()

    console.rule("[bold green]All Tests Completed[/bold green]")
    console.print("\n[bold green]✓[/bold green] All 6 required components implemented:")
    console.print("  1. create_header(query, industry, location)")
    console.print("  2. create_business_table(businesses, offset, limit)")
    console.print("  3. create_status_bar(num_businesses, cached)")
    console.print("  4. create_progress_panel(message)")
    console.print("  5. create_help_panel()")
    console.print("  6. create_layout(header, table, status, progress)\n")
