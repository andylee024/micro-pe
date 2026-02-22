"""Live integration tests for BizBuySellProvider.

Requires: SCOUT_LIVE_TESTS=1 environment variable and a visible Chrome browser.
These tests hit the real BizBuySell website.
"""

import os

import pytest

LIVE = os.getenv("SCOUT_LIVE_TESTS") == "1"


@pytest.mark.skipif(not LIVE, reason="requires SCOUT_LIVE_TESTS=1")
def test_live_hvac_texas():
    from data_sources.marketplaces.base import ListingQuery
    from data_sources.marketplaces.bizbuysell import BizBuySellProvider

    provider = BizBuySellProvider()
    listings = provider._fetch(ListingQuery("hvac", "texas", 20))
    assert len(listings) >= 5, f"Expected >= 5 listings, got {len(listings)}"
    assert all(l.source == "bizbuysell" for l in listings)
    assert any(l.asking_price for l in listings)
    assert all(l.url.startswith("https://www.bizbuysell.com") for l in listings)


@pytest.mark.skipif(not LIVE, reason="requires SCOUT_LIVE_TESTS=1")
def test_live_car_wash_california():
    from data_sources.marketplaces.base import ListingQuery
    from data_sources.marketplaces.bizbuysell import BizBuySellProvider

    provider = BizBuySellProvider()
    listings = provider._fetch(ListingQuery("car wash", "california", 20))
    assert len(listings) >= 5, f"Expected >= 5 car wash listings, got {len(listings)}"
    assert all(l.source == "bizbuysell" for l in listings)


@pytest.mark.skipif(not LIVE, reason="requires SCOUT_LIVE_TESTS=1")
def test_live_result_fields():
    """Verify that 80%+ of results have non-empty core fields."""
    from data_sources.marketplaces.base import ListingQuery
    from data_sources.marketplaces.bizbuysell import BizBuySellProvider

    provider = BizBuySellProvider()
    listings = provider._fetch(ListingQuery("plumbing", "florida", 20))
    assert len(listings) >= 5, f"Expected >= 5 listings, got {len(listings)}"

    # Check field completeness
    has_name = sum(1 for l in listings if l.name)
    has_url = sum(1 for l in listings if l.url)
    has_source_id = sum(1 for l in listings if l.source_id)

    total = len(listings)
    threshold = 0.8

    assert has_name / total >= threshold, (
        f"Only {has_name}/{total} have name"
    )
    assert has_url / total >= threshold, (
        f"Only {has_url}/{total} have url"
    )
    assert has_source_id / total >= threshold, (
        f"Only {has_source_id}/{total} have source_id"
    )
