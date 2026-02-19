"""Keyboard event handling for terminal UI"""

import readchar
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
        # Handle regular keys (case insensitive)
        elif key.lower() == 'e':
            self.terminal.export_csv()
        elif key.lower() == 'q':
            self.terminal.quit()
            self.running = False
        elif key.lower() == 'h':
            self.terminal.toggle_help()
        elif key.lower() == 'r':
            self.terminal.refresh_data()

    def stop(self) -> None:
        """Stop the keyboard event loop"""
        self.running = False
