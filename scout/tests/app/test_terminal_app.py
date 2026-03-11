from __future__ import annotations

from dataclasses import dataclass, field

from scout.app.modes import TerminalMode
from scout.app.state import TerminalStateStore
from scout.app.terminal import ScoutTerminalApp
from scout.pipeline.models.business import Business
from scout.pipeline.models.market_dataset import Coverage, MarketDataset
from scout.pipeline.models.query import Query


@dataclass
class StubResearchService:
    dataset: MarketDataset
    calls: list[dict[str, object]] = field(default_factory=list)

    def load_dataset(self, *, query_text: str, max_results: int, use_cache: bool) -> MarketDataset:
        self.calls.append(
            {
                "query_text": query_text,
                "max_results": max_results,
                "use_cache": use_cache,
            }
        )
        return self.dataset


def _dataset() -> MarketDataset:
    query = Query(industry="hvac businesses", location="los angeles, ca", max_results=25)
    return MarketDataset(
        query=query,
        businesses=[
            Business(name="Cool Air HVAC", rating=4.8, reviews=350),
            Business(name="Premier Climate", rating=4.6, reviews=210),
        ],
        coverage=[
            Coverage(source="google_maps", status="success", records=2, duration_ms=380),
            Coverage(source="bizbuysell", status="success", records=4, duration_ms=620),
        ],
    )


def test_terminal_app_bootstrap_reads_from_service_layer():
    dataset = _dataset()
    service = StubResearchService(dataset=dataset)
    state_store = TerminalStateStore(service=service)
    app = ScoutTerminalApp(
        state_store=state_store,
        query_text="HVAC businesses in Los Angeles",
        max_results=25,
        use_cache=False,
    )

    state = app.bootstrap_state()

    assert state.dataset is dataset
    assert service.calls == [
        {
            "query_text": "HVAC businesses in Los Angeles",
            "max_results": 25,
            "use_cache": False,
        }
    ]
    assert app.active_mode == TerminalMode.UNIVERSE.value
    assert "2 businesses" in state_store.build_summary_line()


def test_terminal_app_mode_routing_updates_shared_state():
    dataset = _dataset()
    service = StubResearchService(dataset=dataset)
    state_store = TerminalStateStore(service=service)
    app = ScoutTerminalApp(
        state_store=state_store,
        query_text="HVAC businesses in Los Angeles",
        max_results=25,
        use_cache=True,
    )
    app.bootstrap_state()

    app.action_mode_queue()
    assert state_store.state is not None
    assert state_store.state.mode is TerminalMode.QUEUE
    assert app.active_mode == TerminalMode.QUEUE.value

    app.action_mode_lead_set()
    assert state_store.state.mode is TerminalMode.LEAD_SET
    assert app.active_mode == TerminalMode.LEAD_SET.value

    app.action_next_mode()
    assert state_store.state.mode is TerminalMode.HISTORY
    assert app.active_mode == TerminalMode.HISTORY.value

    app.action_mode_command()
    assert state_store.state.mode is TerminalMode.COMMAND
    assert app.active_mode == TerminalMode.COMMAND.value
