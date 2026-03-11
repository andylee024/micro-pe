"""Textual application shell for Scout terminal workflows."""

from __future__ import annotations

from textual.app import App, ComposeResult, ScreenStackError
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.css.query import NoMatches
from textual.reactive import reactive
from textual.widgets import Footer, Header, Static

from scout.app.modes import MODE_LABELS, ORDERED_MODES, TerminalMode
from scout.app.state import TerminalState, TerminalStateStore


class ScoutTerminalApp(App[None]):
    """Dense Textual shell with mode routing and shared terminal state."""

    TITLE = "Scout"
    SUB_TITLE = "SMB acquisition intelligence"

    DEFAULT_CSS = """
    Screen {
        layout: vertical;
    }

    #shell {
        height: 1fr;
    }

    #mode-rail {
        width: 24;
        border: round $panel;
        padding: 1 1;
        margin-right: 1;
    }

    #mode-content {
        border: round $panel;
        padding: 1 2;
    }

    .mode-item {
        padding: 0 0 0 1;
        margin: 0 0 1 0;
    }

    .active {
        background: $accent 20%;
        text-style: bold;
    }

    .header-line {
        color: $text-muted;
    }

    #mode-title {
        text-style: bold;
        margin: 1 0;
    }
    """

    BINDINGS = [
        Binding("1", "mode_universe", "Universe"),
        Binding("2", "mode_queue", "Queue"),
        Binding("3", "mode_lead_set", "Lead Set"),
        Binding("4", "mode_history", "History"),
        Binding("5", "mode_command", "Command"),
        Binding("tab", "next_mode", "Next Mode"),
        Binding("q", "quit", "Quit"),
    ]

    active_mode: reactive[str] = reactive(TerminalMode.UNIVERSE.value)

    def __init__(
        self,
        *,
        state_store: TerminalStateStore,
        query_text: str,
        max_results: int = 100,
        use_cache: bool = True,
    ) -> None:
        super().__init__()
        self.state_store = state_store
        self.query_text = query_text
        self.max_results = max_results
        self.use_cache = use_cache

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal(id="shell"):
            with Vertical(id="mode-rail"):
                yield Static("Modes", classes="header-line")
                for mode in ORDERED_MODES:
                    yield Static("", id=f"mode-{mode.value}", classes="mode-item")
            with Vertical(id="mode-content"):
                yield Static("", id="query-line", classes="header-line")
                yield Static("", id="summary-line", classes="header-line")
                yield Static("", id="mode-title")
                yield Static("", id="mode-body")
        yield Footer()

    def on_mount(self) -> None:
        self.bootstrap_state()
        self._sync_widgets()

    def bootstrap_state(self) -> TerminalState:
        state = self.state_store.bootstrap(
            query_text=self.query_text,
            max_results=self.max_results,
            use_cache=self.use_cache,
        )
        self.active_mode = state.mode.value
        return state

    def set_mode(self, mode: TerminalMode) -> None:
        self.state_store.set_mode(mode)
        self.active_mode = mode.value
        self._sync_widgets()

    def action_mode_universe(self) -> None:
        self.set_mode(TerminalMode.UNIVERSE)

    def action_mode_queue(self) -> None:
        self.set_mode(TerminalMode.QUEUE)

    def action_mode_lead_set(self) -> None:
        self.set_mode(TerminalMode.LEAD_SET)

    def action_mode_history(self) -> None:
        self.set_mode(TerminalMode.HISTORY)

    def action_mode_command(self) -> None:
        self.set_mode(TerminalMode.COMMAND)

    def action_next_mode(self) -> None:
        current = self._mode_from_active()
        current_index = ORDERED_MODES.index(current)
        next_mode = ORDERED_MODES[(current_index + 1) % len(ORDERED_MODES)]
        self.set_mode(next_mode)

    def watch_active_mode(self, _active_mode: str) -> None:
        self._sync_widgets()

    def _mode_from_active(self) -> TerminalMode:
        return TerminalMode(self.active_mode)

    def _sync_widgets(self) -> None:
        try:
            mode = self._mode_from_active()
            self._set_text("query-line", self.state_store.build_query_line())
            self._set_text("summary-line", self.state_store.build_summary_line())
            self._set_text("mode-title", MODE_LABELS[mode])
            self._set_text("mode-body", self.state_store.build_mode_body())

            for candidate in ORDERED_MODES:
                widget = self.query_one(f"#mode-{candidate.value}", Static)
                label = MODE_LABELS[candidate]
                widget.update(f"{'>' if candidate is mode else ' '} {label}")
                if candidate is mode:
                    widget.add_class("active")
                else:
                    widget.remove_class("active")
        except (ScreenStackError, NoMatches):
            return

    def _set_text(self, widget_id: str, value: str) -> None:
        self.query_one(f"#{widget_id}", Static).update(value)
