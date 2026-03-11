"""Shared terminal state container backed by app services."""

from __future__ import annotations

from dataclasses import dataclass

from scout.app.modes import MODE_LABELS, TerminalMode
from scout.app.services import ResearchService
from scout.pipeline.models.business import Business
from scout.pipeline.models.market_dataset import MarketDataset


@dataclass
class TerminalState:
    """Single source of truth for the terminal shell."""

    query_text: str
    mode: TerminalMode = TerminalMode.UNIVERSE
    dataset: MarketDataset | None = None
    load_error: str = ""


class TerminalStateStore:
    """State holder that hydrates from the canonical app service layer."""

    def __init__(self, service: ResearchService) -> None:
        self._service = service
        self._state: TerminalState | None = None

    @property
    def state(self) -> TerminalState | None:
        return self._state

    def bootstrap(self, *, query_text: str, max_results: int, use_cache: bool) -> TerminalState:
        state = TerminalState(query_text=query_text)
        try:
            state.dataset = self._service.load_dataset(
                query_text=query_text,
                max_results=max_results,
                use_cache=use_cache,
            )
        except Exception as exc:  # noqa: BLE001
            state.load_error = str(exc)
        self._state = state
        return state

    def set_mode(self, mode: TerminalMode) -> TerminalState:
        state = self._require_state()
        state.mode = mode
        return state

    def build_summary_line(self) -> str:
        state = self._require_state()
        if state.load_error:
            return f"load error: {state.load_error}"
        if state.dataset is None:
            return "no dataset loaded"
        return (
            f"{len(state.dataset.businesses)} businesses · "
            f"{len(state.dataset.listings)} listings · "
            f"mode {MODE_LABELS[state.mode]}"
        )

    def build_query_line(self) -> str:
        state = self._require_state()
        if state.dataset is None:
            return state.query_text
        query = state.dataset.query
        return f"{query.industry} · {query.location} · run {query.run_id}"

    def build_mode_body(self) -> str:
        state = self._require_state()
        mode = state.mode
        if state.load_error:
            return f"Unable to hydrate dataset from service layer.\n{state.load_error}"
        if state.dataset is None:
            return "Dataset unavailable."

        dataset = state.dataset
        if mode is TerminalMode.UNIVERSE:
            return self._render_universe(dataset)
        if mode is TerminalMode.QUEUE:
            return self._render_queue(dataset)
        if mode is TerminalMode.LEAD_SET:
            return self._render_lead_set(dataset.businesses)
        if mode is TerminalMode.HISTORY:
            return self._render_history(dataset)
        if mode is TerminalMode.COMMAND:
            return self._render_command(dataset)
        return "Mode not implemented."

    def _require_state(self) -> TerminalState:
        if self._state is None:
            raise RuntimeError("Terminal state not initialized. Call bootstrap(...) first.")
        return self._state

    @staticmethod
    def _render_universe(dataset: MarketDataset) -> str:
        if not dataset.businesses:
            return "No businesses discovered in current universe."

        rows = []
        for business in dataset.businesses[:8]:
            rating = f"{business.rating:.1f}" if business.rating is not None else "-"
            reviews = business.reviews if business.reviews is not None else 0
            rows.append(f"- {business.name} · rating {rating} · reviews {reviews}")
        return "\n".join(rows)

    @staticmethod
    def _render_queue(dataset: MarketDataset) -> str:
        if not dataset.coverage:
            return "No source coverage entries available."

        rows = []
        for item in dataset.coverage:
            suffix = f" error={item.error}" if item.error else ""
            rows.append(
                f"- {item.source}: {item.status} · records {item.records} · "
                f"{item.duration_ms}ms{suffix}"
            )
        return "\n".join(rows)

    @staticmethod
    def _render_lead_set(businesses: list[Business]) -> str:
        if not businesses:
            return "No lead candidates available."

        ranked = sorted(
            businesses,
            key=lambda item: (
                item.reviews if item.reviews is not None else -1,
                item.rating if item.rating is not None else -1.0,
            ),
            reverse=True,
        )
        rows = []
        for index, business in enumerate(ranked[:10], start=1):
            rating = f"{business.rating:.1f}" if business.rating is not None else "-"
            reviews = business.reviews if business.reviews is not None else 0
            rows.append(f"{index:>2}. {business.name} · {rating}★ · {reviews} reviews")
        return "\n".join(rows)

    @staticmethod
    def _render_history(dataset: MarketDataset) -> str:
        rows = [f"dataset created_at: {dataset.created_at}"]
        for item in dataset.coverage:
            rows.append(f"- {item.source}: status={item.status}")
        return "\n".join(rows)

    @staticmethod
    def _render_command(dataset: MarketDataset) -> str:
        return (
            "Command mode scaffold\n"
            f"- query: {dataset.query.industry} in {dataset.query.location}\n"
            f"- sources: {len(dataset.coverage)}\n"
            "- bindings: 1-5 mode switch, tab cycle, q quit"
        )
