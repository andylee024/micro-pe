"""Tests for FetchPipeline (mock provider, no network)."""

import tempfile
from datetime import datetime
from pathlib import Path
from typing import List
from unittest.mock import MagicMock, patch

import pytest

from data_sources.marketplaces.base import ListingQuery, MarketplaceProvider
from data_sources.marketplaces.pipeline import FetchPipeline
from data_sources.marketplaces.store import ListingStore
from scout.domain.listing import Listing


def _make_listing(
    source_id: str = "001",
    name: str = "Test HVAC Business",
    industry: str = "hvac",
    location: str = "Austin, TX",
    state: str = "TX",
    asking_price: float = 500_000.0,
    cash_flow: float = 150_000.0,
) -> Listing:
    return Listing(
        source="mock",
        source_id=source_id,
        url=f"https://example.com/{source_id}",
        name=name,
        industry=industry,
        location=location,
        state=state,
        asking_price=asking_price,
        cash_flow=cash_flow,
        fetched_at=datetime.now().isoformat(),
    )


class MockProvider(MarketplaceProvider):
    """A mock provider that returns canned listings without network access."""

    SOURCE_ID = "mock"

    def __init__(self, listings: List[Listing] = None, **kwargs):
        super().__init__(**kwargs)
        self._listings = listings or []
        self.fetch_count = 0

    def _fetch(self, query: ListingQuery) -> List[Listing]:
        self.fetch_count += 1
        return self._listings[: query.max_results]


def _make_pipeline(
    listings: List[Listing] = None,
) -> tuple:
    """Create a pipeline with an in-memory store and mock provider.

    Uses a temp directory for the provider's file cache to avoid
    interference from real cached data on disk.
    """
    store = ListingStore(":memory:")
    tmp_cache = Path(tempfile.mkdtemp())
    provider = MockProvider(listings=listings or [], cache_dir=tmp_cache)
    pipeline = FetchPipeline(store=store, providers=[provider])
    return pipeline, store, provider


# --- Basic pipeline tests ---


class TestFetchPipelineBasic:
    def test_run_returns_listings(self):
        listings = [_make_listing(source_id=str(i)) for i in range(5)]
        pipeline, store, provider = _make_pipeline(listings)
        results = pipeline.run("hvac", max_results=10)
        assert len(results) == 5
        assert all(isinstance(r, Listing) for r in results)

    def test_run_empty_results(self):
        pipeline, store, provider = _make_pipeline([])
        results = pipeline.run("hvac")
        assert results == []

    def test_run_respects_max_results(self):
        listings = [_make_listing(source_id=str(i)) for i in range(20)]
        pipeline, store, provider = _make_pipeline(listings)
        results = pipeline.run("hvac", max_results=5)
        assert len(results) <= 5

    def test_run_upserts_to_store(self):
        listings = [_make_listing(source_id=str(i)) for i in range(3)]
        pipeline, store, provider = _make_pipeline(listings)
        pipeline.run("hvac")
        assert store.count() == 3

    def test_run_logs_scrape(self):
        listings = [_make_listing(source_id=str(i)) for i in range(3)]
        pipeline, store, provider = _make_pipeline(listings)
        pipeline.run("hvac", location="texas")
        ts = store.last_scraped("mock", "hvac", "texas")
        assert ts is not None


# --- Caching / staleness tests ---


class TestFetchPipelineCaching:
    def test_stale_data_triggers_scrape(self):
        listings = [_make_listing(source_id="s1")]
        pipeline, store, provider = _make_pipeline(listings)
        # First run should scrape (no prior data)
        pipeline.run("hvac")
        assert provider.fetch_count == 1

    def test_fresh_data_skips_scrape(self):
        listings = [_make_listing(source_id="f1")]
        pipeline, store, provider = _make_pipeline(listings)
        # First run: scrapes
        pipeline.run("hvac")
        assert provider.fetch_count == 1
        # Second run: data is fresh, should not scrape again
        pipeline.run("hvac")
        assert provider.fetch_count == 1

    def test_force_refresh_triggers_scrape(self):
        listings = [_make_listing(source_id="fr1")]
        pipeline, store, provider = _make_pipeline(listings)
        pipeline.run("hvac")
        assert provider.fetch_count == 1
        pipeline.run("hvac", force_refresh=True)
        assert provider.fetch_count == 2


# --- Error handling ---


class TestFetchPipelineErrors:
    def test_scrape_error_is_caught(self):
        pipeline, store, provider = _make_pipeline([])
        # Make the provider raise an error
        provider._fetch = MagicMock(side_effect=RuntimeError("Network error"))
        # search() calls _fetch internally
        provider.search = MagicMock(side_effect=RuntimeError("Network error"))
        results = pipeline.run("hvac")
        assert results == []

    def test_scrape_error_is_logged(self):
        pipeline, store, provider = _make_pipeline([])
        provider.search = MagicMock(side_effect=RuntimeError("Network error"))
        pipeline.run("hvac")
        # Check that an error scrape log was created
        cur = store.conn.execute(
            "SELECT status, error_msg FROM scrape_log WHERE source = 'mock'"
        )
        row = cur.fetchone()
        assert row is not None
        assert row["status"] == "error"
        assert "Network error" in row["error_msg"]


# --- Multiple providers ---


class TestFetchPipelineMultiProvider:
    def test_aggregates_from_multiple_providers(self):
        listings_a = [
            _make_listing(source_id="a1", name="HVAC Co A"),
        ]
        listings_b = [
            _make_listing(source_id="b1", name="HVAC Co B"),
        ]
        store = ListingStore(":memory:")
        provider_a = MockProvider(listings=listings_a)
        provider_a.SOURCE_ID = "mock_a"
        provider_b = MockProvider(listings=listings_b)
        provider_b.SOURCE_ID = "mock_b"
        pipeline = FetchPipeline(store=store, providers=[provider_a, provider_b])
        results = pipeline.run("hvac", max_results=10)
        assert len(results) == 2


# --- Validation integration ---


class TestFetchPipelineValidation:
    def test_validation_report_logged(self):
        listings = [
            _make_listing(source_id="v1", name="HVAC Business"),
            _make_listing(source_id="v2", name="Coffee Shop"),
        ]
        pipeline, store, provider = _make_pipeline(listings)
        pipeline.run("hvac")
        cur = store.conn.execute(
            "SELECT precision_pct FROM scrape_log WHERE source = 'mock'"
        )
        row = cur.fetchone()
        assert row is not None
        assert row["precision_pct"] is not None
