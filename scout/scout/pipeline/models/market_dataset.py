"""Output dataset model for one pipeline run."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from scout.pipeline.models.business import Business
from scout.pipeline.models.listing import Listing
from scout.pipeline.models.query import Query


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class Coverage:
    source: str
    status: str
    records: int = 0
    error: str = ""
    duration_ms: int = 0


@dataclass
class RunDiffSummary:
    run_id: str
    previous_run_id: str | None = None
    added_businesses: int = 0
    removed_businesses: int = 0
    added_listings: int = 0
    removed_listings: int = 0


@dataclass
class MarketDataset:
    query: Query
    businesses: list[Business] = field(default_factory=list)
    listings: list[Listing] = field(default_factory=list)
    signals: dict[str, object] = field(default_factory=dict)
    coverage: list[Coverage] = field(default_factory=list)
    run_diff: RunDiffSummary | None = None
    created_at: str = field(default_factory=_utc_now_iso)
