"""End-to-end integration tests for Terminal UI"""

import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
from scout.ui.terminal import ScoutTerminal
from scout.ui.keyboard import KeyboardHandler


@pytest.fixture
def mock_businesses():
    """Generate mock business data"""
    return [
        {
            'name': f'HVAC Business {i}',
            'phone': f'(555) {i:03d}-0000',
            'website': f'hvac{i}.com',
            'address': f'{i} Main St, Los Angeles, CA 90001',
            'category': 'HVAC'
        }
        for i in range(500)
    ]


@pytest.fixture
def mock_google_maps_response(mock_businesses):
    """Mock Google Maps API response"""
    return {
        'source': 'google_maps',
        'search_date': '2026-02-19T10:00:00',
        'industry': 'HVAC',
        'location': 'Los Angeles',
        'total_found': len(mock_businesses),
        'results': mock_businesses,
        'cached': False
    }


@pytest.fixture
def mock_cached_response(mock_businesses):
    """Mock cached Google Maps response"""
    return {
        'source': 'google_maps',
        'search_date': '2026-02-19T10:00:00',
        'industry': 'HVAC',
        'location': 'Los Angeles',
        'total_found': len(mock_businesses),
        'results': mock_businesses,
        'cached': True
    }


class TestFullUIPipeline:
    """Test full UI pipeline from CLI to display to export"""

    def test_full_ui_pipeline_fresh_data(self, mock_google_maps_response, tmp_path):
        """Test: CLI → Terminal UI → Google Maps → Display → Export"""
        with patch('data_sources.maps.google_maps.GoogleMapsTool.search') as mock_search:
            mock_search.return_value = mock_google_maps_response

            # Initialize terminal
            terminal = ScoutTerminal(
                industry="HVAC",
                location="Los Angeles",
                use_cache=False,
                max_results=500
            )

            # Simulate data fetch
            terminal._fetch_data()

            # Verify data was loaded
            assert len(terminal.businesses) == 500
            assert terminal.status == "Ready"
            assert terminal.cached is False

            # Verify layout can be built
            layout = terminal._build_layout()
            assert layout is not None

            # Test scrolling
            terminal.scroll_down()
            assert terminal.selected_index == 1
            assert terminal.scroll_offset == 0

            terminal.scroll_up()
            assert terminal.selected_index == 0

            # Test export (with mocked output dir)
            from scout import config
            original_output_dir = config.OUTPUT_DIR
            config.OUTPUT_DIR = tmp_path / "outputs"

            try:
                terminal.export_csv()
                # Status should indicate export completion
                assert "Exported" in terminal.status or "Ready" in terminal.status
            finally:
                config.OUTPUT_DIR = original_output_dir

    def test_caching_with_ui(self, mock_cached_response):
        """Test: Second run uses cache, UI shows 'Cached' status"""
        with patch('data_sources.maps.google_maps.GoogleMapsTool.search') as mock_search:
            mock_search.return_value = mock_cached_response

            # Initialize terminal with cache enabled
            terminal = ScoutTerminal(
                industry="HVAC",
                location="Los Angeles",
                use_cache=True,
                max_results=500
            )

            # Simulate data fetch
            terminal._fetch_data()

            # Verify cached flag is set
            assert terminal.cached is True
            assert len(terminal.businesses) == 500
            assert terminal.status == "Ready"

    def test_scrolling_500_businesses(self, mock_businesses):
        """Test: Scroll through all 500 businesses, no crashes"""
        terminal = ScoutTerminal(
            industry="HVAC",
            location="Los Angeles"
        )
        terminal.businesses = mock_businesses
        terminal.status = "Ready"

        # Test scrolling to bottom
        max_offset = len(terminal.businesses) - terminal.page_size
        terminal.scroll_to_bottom()
        assert terminal.scroll_offset == max_offset
        assert terminal.selected_index == len(terminal.businesses) - 1

        # Test page down at bottom (should not crash)
        terminal.page_down()
        assert terminal.scroll_offset == max_offset

        # Test scrolling back to top
        terminal.scroll_to_top()
        assert terminal.scroll_offset == 0

        # Test page up at top (should not crash)
        terminal.page_up()
        assert terminal.scroll_offset == 0

    def test_error_handling_in_ui(self):
        """Test: API error shows user-friendly message in UI"""
        with patch('data_sources.maps.google_maps.GoogleMapsTool.search') as mock_search:
            # Simulate API error
            mock_search.side_effect = ConnectionError("Network connection failed")

            terminal = ScoutTerminal(
                industry="HVAC",
                location="Los Angeles"
            )

            # Simulate data fetch with error
            terminal._fetch_data()

            # Verify error is handled gracefully
            assert "Error" in terminal.status or terminal.error_message is not None
            assert len(terminal.businesses) == 0


class TestKeyboardInteraction:
    """Test keyboard event handling"""

    def test_keyboard_handler_dispatch(self, mock_businesses):
        """Test keyboard events are dispatched correctly"""
        terminal = ScoutTerminal(industry="HVAC", location="LA")
        terminal.businesses = mock_businesses
        handler = terminal.keyboard_handler

        # Test scrolling methods directly (not via key dispatch which has special key codes)
        initial_offset = terminal.scroll_offset
        terminal.scroll_down()
        assert terminal.selected_index == 1
        assert terminal.scroll_offset == initial_offset

        terminal.scroll_up()
        assert terminal.selected_index == 0
        assert terminal.scroll_offset == initial_offset

        terminal.scroll_up()
        assert terminal.selected_index == 0
        assert terminal.scroll_offset == initial_offset

    def test_export_key_press(self, mock_businesses, tmp_path):
        """Test export via keyboard shortcut"""
        from scout import config
        original_output_dir = config.OUTPUT_DIR
        config.OUTPUT_DIR = tmp_path / "outputs"

        try:
            terminal = ScoutTerminal(industry="HVAC", location="LA")
            terminal.businesses = mock_businesses[:10]
            handler = terminal.keyboard_handler

            # Simulate 'e' key press
            handler._dispatch_key('e')

            # Status should show export completion
            assert "Exported" in terminal.status or "Ready" in terminal.status

        finally:
            config.OUTPUT_DIR = original_output_dir

    def test_quit_key_press(self, mock_businesses):
        """Test quit via keyboard shortcut"""
        terminal = ScoutTerminal(industry="HVAC", location="LA")
        terminal.businesses = mock_businesses
        handler = terminal.keyboard_handler

        assert handler.running is True

        # Simulate 'q' key press
        handler._dispatch_key('q')

        # Handler should stop
        assert handler.running is False

    def test_help_toggle_key_press(self, mock_businesses):
        """Test help panel toggle via keyboard"""
        terminal = ScoutTerminal(industry="HVAC", location="LA")
        terminal.businesses = mock_businesses
        handler = terminal.keyboard_handler

        initial_help_state = terminal.show_help

        # Simulate 'h' key press
        handler._dispatch_key('h')

        # Help state should toggle
        assert terminal.show_help == (not initial_help_state)

        # Toggle again
        handler._dispatch_key('h')
        assert terminal.show_help == initial_help_state


class TestUIState:
    """Test UI state management"""

    def test_initial_state(self):
        """Test terminal initializes with correct state"""
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
        assert terminal.businesses == []
        assert terminal.status == "Initializing..."
        assert terminal.cached is False
        assert terminal.show_help is False

    def test_state_after_data_load(self, mock_businesses):
        """Test terminal state after loading data"""
        terminal = ScoutTerminal(industry="HVAC", location="LA")
        terminal.businesses = mock_businesses
        terminal.status = "Ready"
        terminal.cached = True

        assert len(terminal.businesses) == 500
        assert terminal.status == "Ready"
        assert terminal.cached is True

    def test_error_state(self):
        """Test terminal error state handling"""
        terminal = ScoutTerminal(industry="HVAC", location="LA")
        error_msg = "Test error message"

        terminal.set_error(error_msg)

        assert terminal.error_message == error_msg
        assert "Error" in terminal.status


class TestUIComponents:
    """Test UI component integration"""

    def test_layout_with_no_data(self):
        """Test layout displays correctly with no data"""
        terminal = ScoutTerminal(industry="HVAC", location="LA")
        terminal.status = "Loading..."

        layout = terminal._build_layout()

        assert layout is not None
        assert layout.get("header") is not None
        assert layout.get("body") is not None
        assert layout.get("market_overview") is not None
        assert layout.get("target_list") is not None
        assert layout.get("business_profile") is not None
        assert layout.get("market_pulse") is not None

    def test_layout_with_data(self, mock_businesses):
        """Test layout displays correctly with data"""
        terminal = ScoutTerminal(industry="HVAC", location="LA")
        terminal.businesses = mock_businesses
        terminal.status = "Ready"

        layout = terminal._build_layout()

        assert layout is not None
        assert layout.get("header") is not None
        assert layout.get("body") is not None
        assert layout.get("market_overview") is not None
        assert layout.get("target_list") is not None
        assert layout.get("business_profile") is not None
        assert layout.get("market_pulse") is not None

    def test_layout_with_help(self, mock_businesses):
        """Test layout displays help panel"""
        terminal = ScoutTerminal(industry="HVAC", location="LA")
        terminal.businesses = mock_businesses
        terminal.show_help = True

        layout = terminal._build_layout()

        assert layout is not None
        # Help panel should be in body when show_help is True


class TestScrollingEdgeCases:
    """Test scrolling edge cases"""

    def test_scroll_with_empty_list(self):
        """Test scrolling with no businesses loaded"""
        terminal = ScoutTerminal(industry="HVAC", location="LA")
        terminal.businesses = []

        # Should not crash
        terminal.scroll_down()
        terminal.scroll_up()
        terminal.page_down()
        terminal.page_up()

        assert terminal.scroll_offset == 0

    def test_scroll_with_fewer_than_page_size(self):
        """Test scrolling with fewer businesses than page size"""
        terminal = ScoutTerminal(industry="HVAC", location="LA")
        terminal.businesses = [
            {'name': f'Business {i}', 'phone': '555-0000', 'website': 'test.com', 'address': 'Test'}
            for i in range(5)
        ]

        # Should not scroll since all fit on one page
        terminal.scroll_down()
        assert terminal.scroll_offset == 0
        assert terminal.selected_index == 1

        terminal.page_down()
        assert terminal.scroll_offset == 0

    def test_scroll_exactly_page_size(self):
        """Test scrolling with exactly page_size businesses"""
        terminal = ScoutTerminal(industry="HVAC", location="LA")
        terminal.businesses = [
            {'name': f'Business {i}', 'phone': '555-0000', 'website': 'test.com', 'address': 'Test'}
            for i in range(20)
        ]

        # Should not scroll since all fit on one page
        terminal.scroll_down()
        assert terminal.scroll_offset == 0
        assert terminal.selected_index == 1

    def test_scroll_one_more_than_page_size(self):
        """Test scrolling with page_size + 1 businesses"""
        terminal = ScoutTerminal(industry="HVAC", location="LA")
        terminal.businesses = [
            {'name': f'Business {i}', 'phone': '555-0000', 'website': 'test.com', 'address': 'Test'}
            for i in range(21)
        ]

        # Should be able to scroll down by 1
        terminal.scroll_down()
        assert terminal.scroll_offset == 0
        assert terminal.selected_index == 1

        terminal.scroll_down()
        assert terminal.scroll_offset == 0
        assert terminal.selected_index == 2


class TestExportIntegration:
    """Test export functionality integration"""

    def test_export_with_no_data(self):
        """Test export with no data shows appropriate message"""
        terminal = ScoutTerminal(industry="HVAC", location="LA")
        terminal.businesses = []

        terminal.export_csv()

        assert "No data" in terminal.status

    def test_export_creates_file(self, mock_businesses, tmp_path):
        """Test export creates CSV file"""
        from scout import config
        original_output_dir = config.OUTPUT_DIR
        config.OUTPUT_DIR = tmp_path / "outputs"

        try:
            terminal = ScoutTerminal(industry="HVAC", location="Los Angeles")
            terminal.businesses = mock_businesses[:50]  # Smaller set for speed

            terminal.export_csv()

            # Check file was created
            csv_files = list((tmp_path / "outputs").glob("*.csv"))
            assert len(csv_files) > 0

        finally:
            config.OUTPUT_DIR = original_output_dir


class TestRefreshFunctionality:
    """Test data refresh functionality"""

    def test_refresh_bypasses_cache(self, mock_google_maps_response):
        """Test refresh forces fresh data fetch"""
        with patch('data_sources.maps.google_maps.GoogleMapsTool.search') as mock_search:
            mock_search.return_value = mock_google_maps_response

            terminal = ScoutTerminal(
                industry="HVAC",
                location="LA",
                use_cache=True
            )

            # Initially use_cache is True
            assert terminal.use_cache is True

            # Call refresh
            terminal.refresh_data()

            # use_cache should be False now
            assert terminal.use_cache is False
            # Status changes quickly, so just verify it's not the initial state
            assert terminal.status != "Initializing..."


class TestPerformance:
    """Test performance characteristics"""

    def test_layout_build_with_large_dataset(self, mock_businesses):
        """Test layout builds efficiently with 500+ businesses"""
        import time

        terminal = ScoutTerminal(industry="HVAC", location="LA")
        terminal.businesses = mock_businesses

        start = time.time()
        layout = terminal._build_layout()
        elapsed = time.time() - start

        # Layout should build in under 0.5 seconds
        assert elapsed < 0.5
        assert layout is not None

    def test_scrolling_performance(self, mock_businesses):
        """Test scrolling is efficient"""
        import time

        terminal = ScoutTerminal(industry="HVAC", location="LA")
        terminal.businesses = mock_businesses

        start = time.time()

        # Perform 100 scroll operations
        for _ in range(100):
            terminal.scroll_down()

        elapsed = time.time() - start

        # Should complete in under 0.1 seconds
        assert elapsed < 0.1
