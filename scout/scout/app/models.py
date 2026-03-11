"""App-layer models for persisted searches, runs, and curated leads."""

from __future__ import annotations

from dataclasses import dataclass

from scout.pipeline.models.market_dataset import MarketDataset


@dataclass(frozen=True)
class SearchRecord:
    search_id: str
    query_text: str
    industry: str
    location: str
    max_results: int
    use_cache: bool
    created_at: str
    updated_at: str


@dataclass(frozen=True)
class SearchRunRecord:
    run_id: str
    search_id: str
    status: str
    created_at: str
    completed_at: str
    business_count: int
    listing_count: int
    coverage_json: str


@dataclass(frozen=True)
class LeadRecord:
    lead_id: str
    lead_type: str
    source: str
    source_record_id: str
    name: str
    industry: str
    location: str
    state: str
    phone: str
    website: str
    url: str
    summary: str
    note: str
    search_id: str
    saved_at: str
    is_saved: bool


@dataclass(frozen=True)
class SearchExecution:
    search: SearchRecord
    search_run: SearchRunRecord
    dataset: MarketDataset
