"""Tests for the Listing domain model."""

from dataclasses import fields

from scout.domain.listing import Listing


def _make_full_dict():
    """Return a dict with all Listing fields populated."""
    return {
        "source": "bizbuysell",
        "source_id": "abc123",
        "url": "https://www.bizbuysell.com/Business-Opportunity/abc123",
        "name": "Smith's HVAC Services",
        "industry": "HVAC",
        "location": "Austin, TX",
        "state": "TX",
        "description": "Full-service HVAC company with 20 years of history.",
        "asking_price": 500000.0,
        "annual_revenue": 1200000.0,
        "cash_flow": 150000.0,
        "asking_multiple": 3.33,
        "days_on_market": 45,
        "broker": "John Doe",
        "listed_at": "2026-01-15",
        "fetched_at": "2026-02-20T10:30:00",
    }


def test_from_dict_full():
    d = _make_full_dict()
    listing = Listing.from_dict(d)
    assert listing.source == "bizbuysell"
    assert listing.source_id == "abc123"
    assert listing.name == "Smith's HVAC Services"
    assert listing.asking_price == 500000.0
    assert listing.annual_revenue == 1200000.0
    assert listing.cash_flow == 150000.0
    assert listing.asking_multiple == 3.33
    assert listing.days_on_market == 45
    assert listing.broker == "John Doe"
    assert listing.state == "TX"
    assert listing.listed_at == "2026-01-15"
    assert listing.fetched_at == "2026-02-20T10:30:00"


def test_from_dict_missing_fields():
    d = {
        "source": "bizbuysell",
        "source_id": "xyz",
        "url": "https://example.com",
        "name": "Test Biz",
        "industry": "HVAC",
        "location": "Dallas, TX",
    }
    listing = Listing.from_dict(d)
    assert listing.source == "bizbuysell"
    assert listing.asking_price is None
    assert listing.annual_revenue is None
    assert listing.cash_flow is None
    assert listing.asking_multiple is None
    assert listing.days_on_market is None
    assert listing.broker == ""
    assert listing.state == ""
    assert listing.listed_at is None
    assert listing.fetched_at == ""


def test_from_dict_bad_types():
    d = {
        "source": "bizbuysell",
        "source_id": "bad1",
        "url": "https://example.com",
        "name": "Bad Data Biz",
        "industry": "HVAC",
        "location": "Austin, TX",
        "asking_price": "not a number",
        "annual_revenue": "garbage",
        "cash_flow": "N/A",
        "days_on_market": "unknown",
    }
    listing = Listing.from_dict(d)
    assert listing.asking_price is None
    assert listing.annual_revenue is None
    assert listing.cash_flow is None
    assert listing.days_on_market is None


def test_roundtrip():
    d = _make_full_dict()
    original = Listing.from_dict(d)
    roundtripped = Listing.from_dict(original.to_dict())
    assert roundtripped == original


def test_id_property():
    listing = Listing(
        source="bizbuysell",
        source_id="abc123",
        url="https://example.com",
        name="Test",
        industry="HVAC",
        location="Austin, TX",
    )
    assert listing.id == "bizbuysell:abc123"


def test_to_dict_contains_all_fields():
    d = _make_full_dict()
    listing = Listing.from_dict(d)
    result = listing.to_dict()
    field_names = {f.name for f in fields(Listing)}
    assert set(result.keys()) == field_names
