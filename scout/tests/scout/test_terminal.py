"""Tests for terminal UI components and controller"""

import pytest
from scout.ui.terminal import ScoutTerminal
from scout.ui.components import (
    create_header,
    create_business_table,
    create_footer,
    create_detail_panel,
    create_status_bar,
    create_progress_panel,
    create_help_panel,
    create_footer_instructions,
    create_main_layout,
)
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.layout import Layout


# Test ScoutTerminal initialization

def test_scout_terminal_init():
    """Test ScoutTerminal initialization"""
    terminal = ScoutTerminal(
        industry="HVAC",
        location="Los Angeles",
        use_cache=True,
        max_results=500
    )

    assert terminal.industry == "HVAC"
    assert terminal.location == "Los Angeles"
    assert terminal.use_cache is True
    assert terminal.max_results == 500
    assert terminal.scroll_offset == 0
    assert terminal.selected_index == 0
    assert terminal.opened_business is None
    assert len(terminal.businesses) == 0
    assert terminal.page_size == 8


# Test scrolling functionality

@pytest.fixture
def sample_businesses():
    """Generate sample business data for testing"""
    return [
        {
            'name': f'Business {i}',
            'phone': f'(555) {i:03d}-0000',
            'website': f'business{i}.com',
            'address': f'{i} Main St, Los Angeles, CA'
        }
        for i in range(487)
    ]


def test_scroll_down(sample_businesses):
    """Test scrolling down advances the cursor"""
    terminal = ScoutTerminal(industry="HVAC", location="LA")
    terminal.businesses = sample_businesses
    terminal.selected_index = 0

    terminal.scroll_down()

    assert terminal.selected_index == 1


def test_scroll_down_at_bottom(sample_businesses):
    """Test scrolling down when cursor is at last business does nothing"""
    terminal = ScoutTerminal(industry="HVAC", location="LA")
    terminal.businesses = sample_businesses
    terminal.selected_index = len(sample_businesses) - 1

    terminal.scroll_down()

    assert terminal.selected_index == len(sample_businesses) - 1


def test_scroll_up(sample_businesses):
    """Test scrolling up moves cursor up"""
    terminal = ScoutTerminal(industry="HVAC", location="LA")
    terminal.businesses = sample_businesses
    terminal.selected_index = 10

    terminal.scroll_up()

    assert terminal.selected_index == 9


def test_scroll_up_at_top(sample_businesses):
    """Test scrolling up when already at top"""
    terminal = ScoutTerminal(industry="HVAC", location="LA")
    terminal.businesses = sample_businesses
    terminal.scroll_offset = 0

    terminal.scroll_up()

    # Should stay at 0
    assert terminal.scroll_offset == 0


def test_page_down(sample_businesses):
    """Test page down scrolling"""
    terminal = ScoutTerminal(industry="HVAC", location="LA")
    terminal.businesses = sample_businesses
    terminal.scroll_offset = 0

    terminal.page_down()

    assert terminal.scroll_offset == terminal.page_size


def test_page_up(sample_businesses):
    """Test page up scrolling"""
    terminal = ScoutTerminal(industry="HVAC", location="LA")
    terminal.businesses = sample_businesses
    terminal.scroll_offset = terminal.page_size * 2

    terminal.page_up()

    assert terminal.scroll_offset == terminal.page_size


def test_scroll_to_top(sample_businesses):
    """Test scrolling to top"""
    terminal = ScoutTerminal(industry="HVAC", location="LA")
    terminal.businesses = sample_businesses
    terminal.scroll_offset = 100

    terminal.scroll_to_top()

    assert terminal.scroll_offset == 0


def test_scroll_to_bottom(sample_businesses):
    """Test scrolling to bottom"""
    terminal = ScoutTerminal(industry="HVAC", location="LA")
    terminal.businesses = sample_businesses
    terminal.scroll_offset = 0

    terminal.scroll_to_bottom()

    max_offset = len(terminal.businesses) - terminal.page_size
    assert terminal.scroll_offset == max_offset


def test_toggle_help():
    """Test toggling help panel"""
    terminal = ScoutTerminal(industry="HVAC", location="LA")
    initial_state = terminal.show_help

    terminal.toggle_help()
    assert terminal.show_help == (not initial_state)

    terminal.toggle_help()
    assert terminal.show_help == initial_state


# Test cursor navigation and detail view

def test_cursor_moves_with_scroll_down(sample_businesses):
    """Test that selected_index advances when scrolling down"""
    terminal = ScoutTerminal(industry="HVAC", location="LA")
    terminal.businesses = sample_businesses
    terminal.selected_index = 0

    terminal.scroll_down()

    assert terminal.selected_index == 1


def test_cursor_viewport_follows_down(sample_businesses):
    """Test that viewport scrolls to keep cursor visible when moving down"""
    terminal = ScoutTerminal(industry="HVAC", location="LA")
    terminal.businesses = sample_businesses
    # Place cursor at last visible row (page_size - 1 with offset 0)
    terminal.selected_index = terminal.page_size - 1
    terminal.scroll_offset = 0

    terminal.scroll_down()

    assert terminal.scroll_offset == 1
    assert terminal.selected_index == terminal.page_size


def test_cursor_viewport_follows_up(sample_businesses):
    """Test that viewport scrolls to keep cursor visible when moving up"""
    terminal = ScoutTerminal(industry="HVAC", location="LA")
    terminal.businesses = sample_businesses
    terminal.selected_index = 5
    terminal.scroll_offset = 5

    terminal.scroll_up()

    assert terminal.scroll_offset == 4
    assert terminal.selected_index == 4


def test_select_business_enters_detail(sample_businesses):
    """Test that selecting a business populates the profile pane"""
    terminal = ScoutTerminal(industry="HVAC", location="LA")
    terminal.businesses = sample_businesses
    terminal.selected_index = 3

    terminal.select_business()

    assert terminal.opened_business == sample_businesses[3]


def test_close_detail_returns_to_list(sample_businesses):
    """Test that closing detail clears the profile pane"""
    terminal = ScoutTerminal(industry="HVAC", location="LA")
    terminal.businesses = sample_businesses
    terminal.opened_business = sample_businesses[0]

    terminal.close_detail()

    assert terminal.opened_business is None


def test_select_business_no_data():
    """Test selecting with no businesses loaded does nothing"""
    terminal = ScoutTerminal(industry="HVAC", location="LA")
    terminal.businesses = []

    terminal.select_business()

    assert terminal.opened_business is None


# Test UI components

def test_create_header():
    """Test header panel creation"""
    panel = create_header("HVAC in Los Angeles")

    assert isinstance(panel, Panel)


def test_create_header_with_stats():
    """Test header includes stats when provided"""
    panel = create_header(
        query="HVAC in LA",
        num_businesses=42,
        cached=True,
        status_message="Ready",
    )

    assert isinstance(panel, Panel)


def test_create_business_table_empty():
    """Test business table creation with no data"""
    table = create_business_table([])

    assert isinstance(table, Table)
    assert table.row_count == 0


def test_create_business_table_with_data():
    """Test business table creation with data"""
    businesses = [
        {
            'name': 'Test Business',
            'phone': '(555) 123-4567',
            'website': 'test.com',
            'address': '123 Main St'
        }
    ]
    table = create_business_table(businesses)

    assert isinstance(table, Table)
    assert table.row_count == 1


def test_create_business_table_pagination():
    """Test business table pagination"""
    businesses = [
        {
            'name': f'Business {i}',
            'phone': f'555-000{i}',
            'website': f'biz{i}.com',
            'address': f'{i} Main St'
        }
        for i in range(50)
    ]

    # Display first 20
    table = create_business_table(businesses, offset=0, limit=20)
    assert table.row_count == 20

    # Display next 20
    table = create_business_table(businesses, offset=20, limit=20)
    assert table.row_count == 20

    # Display last 10
    table = create_business_table(businesses, offset=40, limit=20)
    assert table.row_count == 10


def test_create_status_bar():
    """Test status bar creation"""
    panel = create_status_bar(num_businesses=487, cached=True, status_message="Ready")

    assert isinstance(panel, Panel)


def test_create_status_bar_not_cached():
    """Test status bar with fresh data"""
    panel = create_status_bar(num_businesses=100, cached=False, status_message="Ready")

    assert isinstance(panel, Panel)


def test_create_progress_panel():
    """Test progress panel creation"""
    panel = create_progress_panel("Searching Google Maps...")

    assert isinstance(panel, Panel)


def test_create_help_panel():
    """Test help panel creation"""
    panel = create_help_panel()

    assert isinstance(panel, Panel)


def test_create_footer_instructions():
    """Test footer instructions creation"""
    panel = create_footer_instructions()

    assert isinstance(panel, Panel)


def test_create_footer_list_mode():
    """Test minimal footer in list mode"""
    text = create_footer(offset=0, total=50, limit=20, view_mode="list")

    assert isinstance(text, Text)


def test_create_footer_detail_mode():
    """Test minimal footer in detail mode"""
    text = create_footer(offset=0, total=50, limit=20, view_mode="detail")

    assert isinstance(text, Text)


def test_create_detail_panel():
    """Test detail panel creation"""
    business = {
        "name": "Test Business",
        "phone": "(555) 123-4567",
        "website": "test.com",
        "address": "123 Main St",
        "rating": 4.5,
    }
    panel = create_detail_panel(business)

    assert isinstance(panel, Panel)


def test_create_business_table_selected_row():
    """Test that selected row index is accepted without error"""
    businesses = [
        {"name": f"Biz {i}", "phone": "555-0000", "website": "", "address": "1 Main St"}
        for i in range(5)
    ]
    table = create_business_table(businesses, offset=0, limit=20, selected_index=2)

    assert isinstance(table, Table)
    assert table.row_count == 5


def test_create_main_layout():
    """Test layout creation"""
    layout = create_main_layout()

    assert isinstance(layout, Layout)
    assert layout.get("header") is not None
    assert layout.get("market_overview") is not None
    assert layout.get("market_pulse") is not None
    assert layout.get("target_list") is not None
    assert layout.get("scout_assistant") is not None
    assert layout.get("footer") is not None


# Test edge cases

def test_export_with_no_data():
    """Test export when no businesses loaded"""
    terminal = ScoutTerminal(industry="HVAC", location="LA")
    terminal.businesses = []

    terminal.export_csv()

    assert "No data" in terminal.status


def test_error_handling():
    """Test error message setting"""
    terminal = ScoutTerminal(industry="HVAC", location="LA")
    error_msg = "Test error"

    terminal.set_error(error_msg)

    assert terminal.error_message == error_msg
    assert error_msg in terminal.status


# Integration test

def test_build_layout_integration(sample_businesses):
    """Test building layout with all components"""
    terminal = ScoutTerminal(industry="HVAC", location="Los Angeles")
    terminal.businesses = sample_businesses

    layout = terminal._build_layout()

    assert isinstance(layout, Layout)
    assert terminal.scroll_offset == 0


def test_build_layout_with_help(sample_businesses):
    """Test building layout with help panel"""
    terminal = ScoutTerminal(industry="HVAC", location="Los Angeles")
    terminal.businesses = sample_businesses
    terminal.show_help = True

    layout = terminal._build_layout()

    assert isinstance(layout, Layout)


# Test keyboard handler integration

def test_keyboard_handler_initialization():
    """Test keyboard handler is initialized with terminal"""
    terminal = ScoutTerminal(industry="HVAC", location="LA")

    assert terminal.keyboard_handler is not None
    assert terminal.keyboard_handler.terminal == terminal
    assert terminal.keyboard_handler.running is True


# Test export functionality

def test_export_csv_integration(sample_businesses, tmp_path):
    """Test CSV export with mocked file system"""
    from scout import config

    # Temporarily override output directory
    original_output_dir = config.OUTPUT_DIR
    config.OUTPUT_DIR = tmp_path / "outputs"

    try:
        terminal = ScoutTerminal(industry="HVAC", location="Los Angeles")
        terminal.businesses = sample_businesses[:10]  # Just 10 for faster test

        terminal.export_csv()

        # Check that status was updated
        assert "Exported" in terminal.status or "Ready" in terminal.status

    finally:
        # Restore original output directory
        config.OUTPUT_DIR = original_output_dir
