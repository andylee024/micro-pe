"""Keyboard event handling for terminal UI"""

import readchar
import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .terminal import ScoutTerminal


class KeyboardHandler:
    """Handles keyboard events in the terminal UI"""

    def __init__(self, terminal: "ScoutTerminal"):
        """Initialize keyboard handler

        Args:
            terminal: Reference to the ScoutTerminal instance
        """
        self.terminal = terminal
        self.running = True
        self._pending_g = False
        self._last_g_time = 0.0

    def handle_event_loop(self) -> None:
        """Non-blocking keyboard event loop

        Continuously listens for keyboard events and dispatches
        them to appropriate handlers.
        """
        while self.running:
            try:
                key = readchar.readkey()
                self._dispatch_key(key)
            except KeyboardInterrupt:
                # Handle Ctrl+C gracefully
                self.terminal.quit()
                self.running = False
            except Exception as e:
                # Log error but continue running
                self.terminal.set_error(f"Keyboard error: {str(e)}")

    def _dispatch_key(self, key: str) -> None:
        """Dispatch key to appropriate handler

        Args:
            key: The key that was pressed
        """
        if self.terminal.chat_mode:
            self._handle_chat_key(key)
            return

        now = time.monotonic()
        if self._pending_g and (now - self._last_g_time) > 0.7:
            self._pending_g = False

        # Handle special keys (arrows)
        if key == readchar.key.UP:
            self.terminal.scroll_up()
        elif key == readchar.key.DOWN:
            self.terminal.scroll_down()
        elif key == readchar.key.PAGE_UP:
            self.terminal.page_up()
        elif key == readchar.key.PAGE_DOWN:
            self.terminal.page_down()
        elif key == readchar.key.HOME:
            self.terminal.scroll_to_top()
        elif key == readchar.key.END:
            self.terminal.scroll_to_bottom()
        elif key in (getattr(readchar.key, "CTRL_D", None), '\x04'):
            self.terminal.page_down()
        elif key in (getattr(readchar.key, "CTRL_U", None), '\x15'):
            self.terminal.page_up()
        # Handle regular keys (case insensitive)
        elif key in (readchar.key.ENTER, '\r', '\n'):
            if self.terminal.focused_pane == "scout_assistant":
                self.terminal.enter_chat_mode()
            else:
                self.terminal.select_business()
        elif key in (getattr(readchar.key, "ESCAPE", None), '\x1b'):
            if self.terminal.focused_pane == "scout_assistant" and self.terminal.active_filter:
                self.terminal.clear_filter()
                return
            closed = self.terminal.close_detail()
            if not closed:
                # Nothing was open — return focus to target list
                self.terminal.focused_pane = "target_list"
                self.terminal._update_display()
        elif key.lower() == 'b':
            self.terminal.close_detail()
        elif key.lower() == 'j':
            if self.terminal.focused_pane == "scout_assistant":
                self.terminal.chat_scroll_down()
            else:
                self.terminal.scroll_down()
        elif key.lower() == 'k':
            if self.terminal.focused_pane == "scout_assistant":
                self.terminal.chat_scroll_up()
            else:
                self.terminal.scroll_up()
        elif key == 'g':
            if self._pending_g and (now - self._last_g_time) <= 0.7:
                self.terminal.scroll_to_top()
                self._pending_g = False
            else:
                self._pending_g = True
                self._last_g_time = now
            return
        elif key == 'G':
            self.terminal.scroll_to_bottom()
        elif key.lower() == 'e':
            self.terminal.export_csv()
        elif key.lower() == 'w':
            self.terminal.open_website()
        elif key == 'R':
            self.terminal.refresh_data()
        elif key.lower() == 'r':
            self.terminal.open_reviews()
        elif key.lower() == 'q':
            self.terminal.quit()
            self.running = False
        elif key.lower() == 'h':
            self.terminal.toggle_help()
        elif key == '/':
            self.terminal.enter_chat_mode()
        elif key in ('\t', getattr(readchar.key, 'TAB', None)):
            self.terminal.focus_next_pane()
        elif key.lower() == 's':
            self.terminal.toggle_sources()

    def _handle_chat_key(self, key: str) -> None:
        """Handle key press while in chat input mode."""
        if key in (getattr(readchar.key, "ESCAPE", None), '\x1b'):
            self.terminal.exit_chat_mode()
        elif key in (readchar.key.ENTER, '\r', '\n'):
            self.terminal.chat_submit()
        elif key in (getattr(readchar.key, "BACKSPACE", None), '\x7f', '\x08'):
            self.terminal.chat_backspace()
        elif len(key) == 1 and key.isprintable():
            self.terminal.chat_type(key)

    def stop(self) -> None:
        """Stop the keyboard event loop"""
        self.running = False
