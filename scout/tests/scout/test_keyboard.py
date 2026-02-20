"""Tests for keyboard event handler"""

import pytest
from unittest.mock import MagicMock, patch
from scout.ui.keyboard import KeyboardHandler
from scout.ui.terminal import ScoutTerminal


@pytest.fixture
def terminal():
    """Create a terminal instance for testing"""
    term = ScoutTerminal(industry="HVAC", location="Los Angeles")
    term.businesses = [
        {
            'name': f'Business {i}',
            'phone': f'(555) {i:03d}-0000',
            'website': f'business{i}.com',
            'address': f'{i} Main St'
        }
        for i in range(50)
    ]
    return term


@pytest.fixture
def handler(terminal):
    """Create a keyboard handler instance"""
    return KeyboardHandler(terminal)


class TestKeyboardHandlerInit:
    """Test keyboard handler initialization"""

    def test_initialization(self, terminal):
        """Test keyboard handler initializes correctly"""
        handler = KeyboardHandler(terminal)

        assert handler.terminal == terminal
        assert handler.running is True

    def test_terminal_has_keyboard_handler(self):
        """Test terminal initializes with keyboard handler"""
        terminal = ScoutTerminal(industry="HVAC", location="LA")

        assert hasattr(terminal, 'keyboard_handler')
        assert isinstance(terminal.keyboard_handler, KeyboardHandler)


class TestKeyDispatch:
    """Test key dispatch functionality"""

    def test_dispatch_up_arrow(self, handler, terminal):
        """Test up arrow key dispatch"""
        terminal.scroll_offset = 5
        terminal.selected_index = 5

        with patch('readchar.key') as mock_key:
            mock_key.UP = '\x1b[A'
            handler._dispatch_key(mock_key.UP)

        assert terminal.selected_index == 4
        assert terminal.scroll_offset == 4

    def test_dispatch_down_arrow(self, handler, terminal):
        """Test down arrow key dispatch"""
        terminal.scroll_offset = 0
        terminal.selected_index = 0

        with patch('readchar.key') as mock_key:
            mock_key.DOWN = '\x1b[B'
            handler._dispatch_key(mock_key.DOWN)

        assert terminal.selected_index == 1

    def test_dispatch_page_up(self, handler, terminal):
        """Test page up key dispatch"""
        terminal.scroll_offset = 30
        terminal.selected_index = 30

        with patch('readchar.key') as mock_key:
            mock_key.PAGE_UP = '\x1b[5~'
            handler._dispatch_key(mock_key.PAGE_UP)

        assert terminal.selected_index == 22
        assert terminal.scroll_offset == 22

    def test_dispatch_page_down(self, handler, terminal):
        """Test page down key dispatch"""
        terminal.scroll_offset = 0
        terminal.selected_index = 0

        with patch('readchar.key') as mock_key:
            mock_key.PAGE_DOWN = '\x1b[6~'
            handler._dispatch_key(mock_key.PAGE_DOWN)

        assert terminal.selected_index == terminal.page_size

    def test_dispatch_home_key(self, handler, terminal):
        """Test home key dispatch"""
        terminal.scroll_offset = 100
        terminal.selected_index = 100

        with patch('readchar.key') as mock_key:
            mock_key.HOME = '\x1b[H'
            handler._dispatch_key(mock_key.HOME)

        assert terminal.scroll_offset == 0
        assert terminal.selected_index == 0

    def test_dispatch_end_key(self, handler, terminal):
        """Test end key dispatch"""
        terminal.scroll_offset = 0
        terminal.selected_index = 0

        with patch('readchar.key') as mock_key:
            mock_key.END = '\x1b[F'
            handler._dispatch_key(mock_key.END)

        max_offset = len(terminal.businesses) - terminal.page_size
        assert terminal.scroll_offset == max_offset
        assert terminal.selected_index == len(terminal.businesses) - 1


class TestCharacterKeys:
    """Test character key handling"""

    def test_e_key_lowercase(self, handler, terminal, tmp_path):
        """Test 'e' key triggers export"""
        from scout import config
        original_output_dir = config.OUTPUT_DIR
        config.OUTPUT_DIR = tmp_path / "outputs"

        try:
            handler._dispatch_key('e')
            # Should update status
            assert "Exported" in terminal.status or "Ready" in terminal.status
        finally:
            config.OUTPUT_DIR = original_output_dir

    def test_e_key_uppercase(self, handler, terminal, tmp_path):
        """Test 'E' key triggers export (case insensitive)"""
        from scout import config
        original_output_dir = config.OUTPUT_DIR
        config.OUTPUT_DIR = tmp_path / "outputs"

        try:
            handler._dispatch_key('E')
            # Should update status
            assert "Exported" in terminal.status or "Ready" in terminal.status
        finally:
            config.OUTPUT_DIR = original_output_dir

    def test_q_key_lowercase(self, handler, terminal):
        """Test 'q' key triggers quit"""
        assert handler.running is True

        handler._dispatch_key('q')

        assert handler.running is False

    def test_q_key_uppercase(self, handler, terminal):
        """Test 'Q' key triggers quit (case insensitive)"""
        assert handler.running is True

        handler._dispatch_key('Q')

        assert handler.running is False

    def test_h_key_toggles_help(self, handler, terminal):
        """Test 'h' key toggles help panel"""
        initial_state = terminal.show_help

        handler._dispatch_key('h')

        assert terminal.show_help == (not initial_state)

    def test_h_key_uppercase(self, handler, terminal):
        """Test 'H' key toggles help (case insensitive)"""
        initial_state = terminal.show_help

        handler._dispatch_key('H')

        assert terminal.show_help == (not initial_state)

    def test_r_key_triggers_refresh(self, handler, terminal):
        """Test 'r' key triggers data refresh"""
        terminal.use_cache = True

        with patch.object(terminal, '_fetch_data'):
            handler._dispatch_key('r')

        assert terminal.use_cache is False
        assert "Refreshing" in terminal.status

    def test_unknown_key_ignored(self, handler, terminal):
        """Test unknown keys are ignored without error"""
        initial_offset = terminal.scroll_offset

        # Send unknown key
        handler._dispatch_key('x')

        # Nothing should change
        assert terminal.scroll_offset == initial_offset


class TestKeyboardHandlerStop:
    """Test keyboard handler stop functionality"""

    def test_stop_method(self, handler):
        """Test stop method sets running to False"""
        assert handler.running is True

        handler.stop()

        assert handler.running is False

    def test_quit_calls_stop(self, handler, terminal):
        """Test quit action stops the handler"""
        assert handler.running is True

        handler._dispatch_key('q')

        assert handler.running is False


class TestErrorHandling:
    """Test error handling in keyboard handler"""

    def test_dispatch_with_terminal_error(self, handler, terminal):
        """Test error handling when terminal method fails"""
        # Note: Currently _dispatch_key doesn't have error handling
        # for individual key dispatches, only in the event loop.
        # This test verifies the current behavior.

        # Make scroll_down raise an exception
        original_scroll_down = terminal.scroll_down

        def failing_scroll_down():
            raise Exception("Test error")

        terminal.scroll_down = failing_scroll_down

        # This will raise an exception (expected current behavior)
        with pytest.raises(Exception, match="Test error"):
            with patch('readchar.key') as mock_key:
                mock_key.DOWN = '\x1b[B'
                handler._dispatch_key(mock_key.DOWN)

        # Restore original method
        terminal.scroll_down = original_scroll_down


class TestEventLoop:
    """Test keyboard event loop"""

    def test_event_loop_stops_when_running_false(self, handler):
        """Test event loop exits when running is False"""
        # Set running to False immediately
        handler.running = False

        # Mock readkey to verify it's not called
        with patch('readchar.readkey') as mock_readkey:
            handler.handle_event_loop()

            # readkey should not be called since loop exits immediately
            mock_readkey.assert_not_called()

    def test_event_loop_handles_keyboard_interrupt(self, handler, terminal):
        """Test event loop handles Ctrl+C gracefully"""
        with patch('readchar.readkey') as mock_readkey:
            # Simulate Ctrl+C
            mock_readkey.side_effect = KeyboardInterrupt()

            handler.handle_event_loop()

            # Handler should stop
            assert handler.running is False

    def test_event_loop_processes_multiple_keys(self, handler, terminal):
        """Test event loop processes multiple key presses"""
        terminal.scroll_offset = 5
        terminal.selected_index = 5
        keys_to_send = ['\x1b[B', '\x1b[B', 'q']  # Down, Down, Quit

        with patch('readchar.readkey') as mock_readkey:
            mock_readkey.side_effect = keys_to_send

            handler.handle_event_loop()

            # Should have scrolled down twice
            assert terminal.selected_index == 7
            assert terminal.scroll_offset == 5
            # Should have stopped
            assert handler.running is False


class TestIntegrationWithTerminal:
    """Test keyboard handler integration with terminal"""

    def test_terminal_methods_called(self, handler, terminal):
        """Test that keyboard handler calls correct terminal methods"""
        # Track method calls
        scroll_up_called = False
        scroll_down_called = False
        export_called = False

        original_scroll_up = terminal.scroll_up
        original_scroll_down = terminal.scroll_down
        original_export = terminal.export_csv

        def track_scroll_up():
            nonlocal scroll_up_called
            scroll_up_called = True
            original_scroll_up()

        def track_scroll_down():
            nonlocal scroll_down_called
            scroll_down_called = True
            original_scroll_down()

        def track_export():
            nonlocal export_called
            export_called = True
            # Don't actually export

        terminal.scroll_up = track_scroll_up
        terminal.scroll_down = track_scroll_down
        terminal.export_csv = track_export

        # Test up arrow
        with patch('readchar.key') as mock_key:
            mock_key.UP = '\x1b[A'
            handler._dispatch_key(mock_key.UP)
        assert scroll_up_called

        # Test down arrow
        with patch('readchar.key') as mock_key:
            mock_key.DOWN = '\x1b[B'
            handler._dispatch_key(mock_key.DOWN)
        assert scroll_down_called

        # Test export
        handler._dispatch_key('e')
        assert export_called

        # Restore original methods
        terminal.scroll_up = original_scroll_up
        terminal.scroll_down = original_scroll_down
        terminal.export_csv = original_export
