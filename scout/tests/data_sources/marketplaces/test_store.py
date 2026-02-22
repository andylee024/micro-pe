"""Tests for ListingStore (SQLite backend, all in-memory)."""

from datetime import datetime, timedelta

from scout.domain.listing import Listing
from data_sources.marketplaces.store import ListingStore


def _make_listing(
    source_id="001",
    name="Test Biz",
    industry="HVAC",
    location="Austin, TX",
    state="TX",
    asking_price=500_000.0,
    annual_revenue=1_200_000.0,
    cash_flow=150_000.0,
    **kwargs,
) -> Listing:
    return Listing(
        source="bizbuysell",
        source_id=source_id,
        url=f"https://www.bizbuysell.com/{source_id}",
        name=name,
        industry=industry,
        location=location,
        state=state,
        asking_price=asking_price,
        annual_revenue=annual_revenue,
        cash_flow=cash_flow,
        fetched_at=datetime.now().isoformat(),
        **kwargs,
    )


def _make_store() -> ListingStore:
    return ListingStore(":memory:")


# --- upsert tests ---

def test_upsert_basic():
    store = _make_store()
    listings = [_make_listing(source_id=str(i)) for i in range(5)]
    store.upsert(listings)
    assert store.count() == 5


def test_upsert_deduplication():
    store = _make_store()
    listing = _make_listing(source_id="dup1")
    store.upsert([listing])
    store.upsert([listing])
    assert store.count() == 1


def test_upsert_update():
    store = _make_store()
    listing = _make_listing(source_id="upd1", asking_price=100_000.0)
    store.upsert([listing])
    updated = _make_listing(source_id="upd1", asking_price=200_000.0)
    store.upsert([updated])
    results = store.search()
    assert len(results) == 1
    assert results[0].asking_price == 200_000.0


# --- search tests ---

def test_search_by_industry():
    store = _make_store()
    hvac = [_make_listing(source_id=f"h{i}", industry="HVAC") for i in range(3)]
    plumbing = [_make_listing(source_id=f"p{i}", industry="Plumbing") for i in range(2)]
    store.upsert(hvac + plumbing)
    results = store.search(industry="HVAC")
    assert len(results) == 3


def test_search_by_location():
    store = _make_store()
    tx = [_make_listing(source_id=f"tx{i}", location="Houston, TX", state="TX") for i in range(2)]
    ca = [_make_listing(source_id=f"ca{i}", location="Los Angeles, CA", state="CA") for i in range(3)]
    store.upsert(tx + ca)
    results = store.search(location="Texas")
    # location search is partial match on location field -- "TX" != "Texas"
    # but our fixtures use "Houston, TX" so let's search for "TX" instead
    results = store.search(location="TX")
    assert len(results) == 2


def test_search_by_price_range():
    store = _make_store()
    prices = [100_000, 300_000, 500_000, 800_000, 1_200_000]
    listings = [_make_listing(source_id=f"pr{i}", asking_price=float(p)) for i, p in enumerate(prices)]
    store.upsert(listings)
    results = store.search(min_price=200_000, max_price=600_000)
    assert len(results) == 2
    result_prices = sorted(r.asking_price for r in results)
    assert result_prices == [300_000.0, 500_000.0]


def test_search_by_cash_flow():
    store = _make_store()
    listings = [
        _make_listing(source_id="cf1", cash_flow=50_000.0),
        _make_listing(source_id="cf2", cash_flow=100_000.0),
        _make_listing(source_id="cf3", cash_flow=200_000.0),
    ]
    store.upsert(listings)
    results = store.search(min_cash_flow=100_000)
    assert len(results) == 2


def test_search_none_filters():
    store = _make_store()
    listings = [_make_listing(source_id=str(i)) for i in range(10)]
    store.upsert(listings)
    results = store.search()
    assert len(results) == 10


def test_search_no_results():
    store = _make_store()
    listings = [_make_listing(source_id="x1", industry="HVAC")]
    store.upsert(listings)
    results = store.search(industry="Underwater Basket Weaving")
    assert results == []


def test_search_returns_listings():
    store = _make_store()
    store.upsert([_make_listing(source_id="typ1")])
    results = store.search()
    assert isinstance(results, list)
    assert len(results) == 1
    assert isinstance(results[0], Listing)


# --- scrape log tests ---

def test_scrape_log_roundtrip():
    store = _make_store()
    store.log_scrape("bizbuysell", "HVAC", "Texas", 42, "success")
    ts = store.last_scraped("bizbuysell", "HVAC", "Texas")
    assert ts is not None
    # Should be a valid ISO datetime string
    parsed = datetime.fromisoformat(ts)
    assert (datetime.now() - parsed).total_seconds() < 5


def test_is_stale_never_scraped():
    store = _make_store()
    assert store.is_stale("bizbuysell", "HVAC", "Texas") is True


def test_is_stale_fresh():
    store = _make_store()
    store.log_scrape("bizbuysell", "HVAC", "Texas", 10, "success")
    assert store.is_stale("bizbuysell", "HVAC", "Texas", max_age_hours=24) is False


def test_is_stale_expired():
    store = _make_store()
    # Insert a scrape_log entry with a timestamp 25 hours ago
    old_ts = (datetime.now() - timedelta(hours=25)).isoformat()
    store.conn.execute(
        """INSERT INTO scrape_log (source, industry, location, scraped_at, listing_count, status)
           VALUES (?, ?, ?, ?, ?, ?)""",
        ("bizbuysell", "HVAC", "Texas", old_ts, 10, "success"),
    )
    store.conn.commit()
    assert store.is_stale("bizbuysell", "HVAC", "Texas", max_age_hours=24) is True
