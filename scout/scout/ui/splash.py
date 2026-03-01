"""Splash screen — thesis input before research begins."""

import readchar
from typing import Optional

from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.text import Text
from rich.align import Align


_WORDMARK = """\
  ███████╗ ██████╗ ██████╗ ██╗   ██╗████████╗
  ██╔════╝██╔════╝██╔═══██╗██║   ██║╚══██╔══╝
  ███████╗██║     ██║   ██║██║   ██║   ██║
  ╚════██║██║     ██║   ██║██║   ██║   ██║
  ███████║╚██████╗╚██████╔╝╚██████╔╝   ██║
  ╚══════╝ ╚═════╝ ╚═════╝  ╚═════╝    ╚═╝   """


class SplashScreen:
    """Full-terminal thesis input screen shown before research begins."""

    EXAMPLES = [
        "HVAC businesses in Los Angeles",
        "plumbing contractors in Chicago",
        "auto repair shops in Phoenix",
        "landscaping companies in Austin",
    ]

    def __init__(self) -> None:
        self.console = Console()
        self.input_text: str = ""
        self.running: bool = True
        self.submitted: bool = False

    def run(self) -> Optional[str]:
        """
        Block until user submits a query or quits.

        Returns:
            The thesis string on Enter, or None if user pressed Esc/Ctrl+C.
        """
        with Live(
            self._render(),
            console=self.console,
            refresh_per_second=8,
            screen=True,
        ) as live:
            while self.running:
                try:
                    key = readchar.readkey()
                    self._handle_key(key)
                    live.update(self._render())
                    if not self.running:
                        break
                except KeyboardInterrupt:
                    return None

        return self.input_text.strip() if self.submitted else None

    def _handle_key(self, key: str) -> None:
        if key in (readchar.key.ENTER, "\r", "\n"):
            if self.input_text.strip():
                self.submitted = True
                self.running = False
        elif key in (getattr(readchar.key, "ESCAPE", None), "\x1b"):
            self.input_text = ""
            self.submitted = False
            self.running = False
        elif key in (
            getattr(readchar.key, "BACKSPACE", None),
            "\x7f",
            "\x08",
        ):
            if self.input_text:
                self.input_text = self.input_text[:-1]
        elif len(key) == 1 and key.isprintable():
            self.input_text += key

    def _render(self) -> Panel:
        t = Text()

        # Wordmark
        t.append("\n")
        for line in _WORDMARK.splitlines():
            t.append(line + "\n", style="bold white")
        t.append("\n")
        t.append("  Bloomberg Terminal for Small Business Acquisition\n", style="dim white")
        t.append("\n")
        t.append("  " + "─" * 54 + "\n\n", style="dim white")

        # Input line
        t.append("  Research thesis:\n", style="dim white")
        t.append("  > ", style="bold white")
        t.append(self.input_text, style="white")
        t.append("▌\n\n", style="green")

        t.append("  " + "─" * 54 + "\n\n", style="dim white")

        # Examples
        t.append("  Examples:\n", style="dim white")
        for ex in self.EXAMPLES:
            t.append(f"    {ex}\n", style="dim white")

        t.append("\n")

        return Panel(
            t,
            border_style="dim white",
            padding=(0, 0),
        )
