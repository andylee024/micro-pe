"""Application-facing services for terminal state hydration."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Protocol

from scout.pipeline.models.market_dataset import MarketDataset
from scout.shared.query_parser import parse_query


class ResearchService(Protocol):
    """Service boundary used by the terminal app."""

    def load_dataset(self, *, query_text: str, max_results: int, use_cache: bool) -> MarketDataset:
        """Return the canonical market dataset for one user query."""


@dataclass
class PipelineResearchService:
    """Production app service that delegates to the canonical pipeline runner."""

    query_parser: Callable[[str], tuple[str, str]] = parse_query
    runner_factory: Callable[[], object] | None = field(default=None)

    def load_dataset(self, *, query_text: str, max_results: int, use_cache: bool) -> MarketDataset:
        industry, location = self.query_parser(query_text)

        if self.runner_factory is None:
            from scout.pipeline.runner import Runner

            runner = Runner()
        else:
            runner = self.runner_factory()

        if not hasattr(runner, "run"):
            raise TypeError("runner_factory must return an object with a run(...) method")

        return runner.run(
            industry=industry,
            location=location,
            max_results=max_results,
            use_cache=use_cache,
        )
