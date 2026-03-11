"""Terminal mode declarations for Scout's Textual shell."""

from __future__ import annotations

from enum import Enum


class TerminalMode(str, Enum):
    """Top-level shell modes in the terminal app."""

    UNIVERSE = "universe"
    QUEUE = "queue"
    LEAD_SET = "lead_set"
    HISTORY = "history"
    COMMAND = "command"


MODE_LABELS: dict[TerminalMode, str] = {
    TerminalMode.UNIVERSE: "Universe",
    TerminalMode.QUEUE: "Queue",
    TerminalMode.LEAD_SET: "Lead Set",
    TerminalMode.HISTORY: "History",
    TerminalMode.COMMAND: "Command",
}


ORDERED_MODES: tuple[TerminalMode, ...] = tuple(TerminalMode)
