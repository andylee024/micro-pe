"""History and diff presentation models."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class RunHistoryEntry:
    run_id: str
    created_at: str
    industry: str
    location: str
    business_count: int
    listing_count: int
    previous_run_id: str | None = None
    added_businesses: int = 0
    removed_businesses: int = 0
    added_listings: int = 0
    removed_listings: int = 0


@dataclass
class RunDiffItem:
    item_type: str
    change_type: str
    item_key: str
    source: str
    name: str
    location: str
    state: str


@dataclass
class RunDiffView:
    run_id: str
    created_at: str
    industry: str
    location: str
    previous_run_id: str | None
    added_businesses: int
    removed_businesses: int
    added_listings: int
    removed_listings: int
    items: list[RunDiffItem] = field(default_factory=list)
