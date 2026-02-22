"""Tests for the validation layer (all offline, no network)."""

import pytest

from scout.domain.listing import Listing
from data_sources.marketplaces.validation import (
    INDUSTRY_KEYWORDS,
    ValidationReport,
    check_financial_sanity,
    is_relevant,
    validate_batch,
)


def _make_listing(
    name: str = "Test Business",
    description: str = "",
    industry: str = "hvac",
    asking_price=500_000.0,
    cash_flow=150_000.0,
    **kwargs,
) -> Listing:
    return Listing(
        source="bizbuysell",
        source_id="12345",
        url="https://www.bizbuysell.com/12345/",
        name=name,
        industry=industry,
        location="Austin, TX",
        state="TX",
        description=description,
        asking_price=asking_price,
        cash_flow=cash_flow,
        fetched_at="2026-02-22T00:00:00",
        **kwargs,
    )


# --- is_relevant tests ---


class TestIsRelevant:
    def test_hvac_keyword_in_name(self):
        listing = _make_listing(name="HVAC Business For Sale")
        assert is_relevant(listing, "hvac") is True

    def test_hvac_keyword_in_description(self):
        listing = _make_listing(
            name="Service Business", description="Provides heating and cooling services"
        )
        assert is_relevant(listing, "hvac") is True

    def test_hvac_irrelevant(self):
        listing = _make_listing(
            name="Coffee Shop", description="Popular downtown cafe"
        )
        assert is_relevant(listing, "hvac") is False

    def test_plumbing_relevant(self):
        listing = _make_listing(name="Joe's Plumbing Service")
        assert is_relevant(listing, "plumbing") is True

    def test_car_wash_relevant(self):
        listing = _make_listing(name="Express Car Wash")
        assert is_relevant(listing, "car wash") is True

    def test_restaurant_relevant(self):
        listing = _make_listing(name="Italian Restaurant")
        assert is_relevant(listing, "restaurant") is True

    def test_unknown_industry_is_permissive(self):
        listing = _make_listing(name="Random Business")
        assert is_relevant(listing, "unknown_industry_xyz") is True

    def test_case_insensitive(self):
        listing = _make_listing(name="HVAC Contractor")
        assert is_relevant(listing, "HVAC") is True

    def test_cleaning_relevant(self):
        listing = _make_listing(name="Professional Cleaning Co")
        assert is_relevant(listing, "cleaning") is True

    def test_pest_control_relevant(self):
        listing = _make_listing(
            name="Bug Be Gone", description="Pest control and exterminator service"
        )
        assert is_relevant(listing, "pest control") is True

    def test_landscaping_relevant(self):
        listing = _make_listing(name="Green Lawn Landscaping")
        assert is_relevant(listing, "landscaping") is True

    def test_auto_repair_relevant(self):
        listing = _make_listing(name="Quick Auto Repair Shop")
        assert is_relevant(listing, "auto repair") is True


# --- validate_batch tests ---


class TestValidateBatch:
    def test_all_relevant(self):
        listings = [
            _make_listing(name="HVAC Business"),
            _make_listing(name="Heating and Cooling Co"),
            _make_listing(name="Air Conditioning Service"),
        ]
        report = validate_batch(listings, "hvac")
        assert report.total == 3
        assert report.relevant == 3
        assert report.precision_pct == 100.0
        assert report.irrelevant_names == []

    def test_mixed_relevance(self):
        listings = [
            _make_listing(name="HVAC Business"),
            _make_listing(name="Coffee Shop"),
            _make_listing(name="Air Conditioning Service"),
            _make_listing(name="Pet Store"),
        ]
        report = validate_batch(listings, "hvac")
        assert report.total == 4
        assert report.relevant == 2
        assert report.precision_pct == 50.0
        assert "Coffee Shop" in report.irrelevant_names
        assert "Pet Store" in report.irrelevant_names

    def test_empty_batch(self):
        report = validate_batch([], "hvac")
        assert report.total == 0
        assert report.relevant == 0
        assert report.precision_pct == 0.0

    def test_none_relevant(self):
        listings = [
            _make_listing(name="Coffee Shop"),
            _make_listing(name="Pet Store"),
        ]
        report = validate_batch(listings, "hvac")
        assert report.total == 2
        assert report.relevant == 0
        assert report.precision_pct == 0.0

    def test_report_type(self):
        listings = [_make_listing(name="HVAC Co")]
        report = validate_batch(listings, "hvac")
        assert isinstance(report, ValidationReport)
        assert report.query_industry == "hvac"


# --- check_financial_sanity tests ---


class TestCheckFinancialSanity:
    def test_normal_listing_no_warnings(self):
        listing = _make_listing(asking_price=500_000.0, cash_flow=150_000.0)
        warnings = check_financial_sanity(listing)
        assert warnings == []

    def test_negative_price(self):
        listing = _make_listing(asking_price=-100_000.0)
        warnings = check_financial_sanity(listing)
        assert any("Negative" in w for w in warnings)

    def test_very_high_price(self):
        listing = _make_listing(asking_price=200_000_000.0)
        warnings = check_financial_sanity(listing)
        assert any("high asking price" in w for w in warnings)

    def test_very_negative_cash_flow(self):
        listing = _make_listing(cash_flow=-2_000_000.0)
        warnings = check_financial_sanity(listing)
        assert any("negative cash flow" in w for w in warnings)

    def test_high_multiple(self):
        listing = _make_listing(asking_price=5_000_000.0, cash_flow=100_000.0)
        warnings = check_financial_sanity(listing)
        assert any("multiple" in w.lower() for w in warnings)

    def test_none_financials_no_warnings(self):
        listing = _make_listing(asking_price=None, cash_flow=None)
        warnings = check_financial_sanity(listing)
        assert warnings == []

    def test_normal_multiple_no_warning(self):
        listing = _make_listing(asking_price=600_000.0, cash_flow=200_000.0)
        warnings = check_financial_sanity(listing)
        assert warnings == []


# --- INDUSTRY_KEYWORDS coverage ---


class TestIndustryKeywords:
    def test_all_target_industries_have_keywords(self):
        expected = [
            "hvac", "plumbing", "electrical", "car wash", "landscaping",
            "cleaning", "pest control", "auto repair", "restaurant", "pool service",
        ]
        for industry in expected:
            assert industry in INDUSTRY_KEYWORDS, f"Missing keywords for {industry}"

    def test_all_keyword_lists_nonempty(self):
        for industry, keywords in INDUSTRY_KEYWORDS.items():
            assert len(keywords) > 0, f"Empty keywords for {industry}"
