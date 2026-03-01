"""Unit tests for BizBuySellProvider (offline, no network)."""

import json

import pytest

from data_sources.marketplaces.base import ListingQuery
from data_sources.marketplaces.bizbuysell import (
    INDUSTRY_SLUG_MAP,
    BizBuySellProvider,
    _STATE_ABBREV_TO_NAME,
    _STATE_NAME_TO_SLUG,
)


@pytest.fixture
def provider():
    return BizBuySellProvider()


# --- URL building tests ---


class TestBuildUrl:
    def test_hvac_no_location(self, provider):
        url = provider._build_url(ListingQuery("hvac"), page=1)
        assert url == "https://www.bizbuysell.com/hvac-businesses-for-sale/"

    def test_hvac_with_state(self, provider):
        url = provider._build_url(ListingQuery("hvac", "texas"), page=1)
        assert url == "https://www.bizbuysell.com/texas/hvac-businesses-for-sale/"

    def test_car_wash_california(self, provider):
        url = provider._build_url(ListingQuery("car wash", "california"), page=1)
        assert url == "https://www.bizbuysell.com/california/car-washes-for-sale/"

    def test_page_2(self, provider):
        url = provider._build_url(ListingQuery("hvac", "texas"), page=2)
        assert url == "https://www.bizbuysell.com/texas/hvac-businesses-for-sale/2/"

    def test_page_1_no_number(self, provider):
        url = provider._build_url(ListingQuery("hvac"), page=1)
        assert "/1/" not in url

    def test_unknown_industry_fallback(self, provider):
        url = provider._build_url(ListingQuery("underwater basket weaving"), page=1)
        assert "service-businesses" in url


# --- Industry slug mapping ---


class TestIndustrySlug:
    def test_hvac(self):
        assert BizBuySellProvider._to_industry_slug("hvac") == "hvac-businesses"

    def test_plumbing(self):
        assert BizBuySellProvider._to_industry_slug("plumbing") == "plumbing-businesses"

    def test_car_wash(self):
        assert BizBuySellProvider._to_industry_slug("car wash") == "car-washes"

    def test_case_insensitive(self):
        assert BizBuySellProvider._to_industry_slug("HVAC") == "hvac-businesses"

    def test_unknown_returns_none(self):
        assert BizBuySellProvider._to_industry_slug("zzz_no_match_zzz") is None

    def test_all_target_industries_mapped(self):
        targets = [
            "hvac", "plumbing", "electrical", "car wash", "landscaping",
            "cleaning", "pest control", "auto repair", "restaurant", "pool service",
        ]
        for industry in targets:
            slug = BizBuySellProvider._to_industry_slug(industry)
            assert slug is not None, f"No slug for {industry}"


# --- State slug mapping ---


class TestStateSlug:
    def test_abbreviation(self):
        assert BizBuySellProvider._to_state_slug("TX") == "texas"

    def test_full_name(self):
        assert BizBuySellProvider._to_state_slug("texas") == "texas"

    def test_city_state_format(self):
        assert BizBuySellProvider._to_state_slug("Austin, TX") == "texas"

    def test_california(self):
        assert BizBuySellProvider._to_state_slug("CA") == "california"

    def test_new_york(self):
        assert BizBuySellProvider._to_state_slug("NY") == "new-york"

    def test_empty_returns_none(self):
        assert BizBuySellProvider._to_state_slug("") is None

    def test_none_returns_none(self):
        assert BizBuySellProvider._to_state_slug(None) is None

    def test_all_50_states(self):
        assert len(_STATE_ABBREV_TO_NAME) >= 50


# --- BBS-state parsing ---


class TestFindListingsArray:
    def test_finds_listings(self):
        data = {
            "api/bff/v2/BbsBfsSearchResults|some|params": {
                "value": {
                    "bfsSearchResult": {
                        "value": [
                            {"header": "HVAC Biz", "listNumber": 123},
                            {"header": "Plumbing Co", "listNumber": 456},
                        ],
                        "total": 100,
                    }
                }
            }
        }
        listings, total = BizBuySellProvider._find_listings_array(data)
        assert len(listings) == 2
        assert total == 100

    def test_no_match_returns_empty(self):
        data = {"some_other_key": {"value": {}}}
        listings, total = BizBuySellProvider._find_listings_array(data)
        assert listings == []
        assert total == 0

    def test_malformed_data_returns_empty(self):
        data = {"BbsBfsSearchResults": "not_a_dict"}
        listings, total = BizBuySellProvider._find_listings_array(data)
        assert listings == []
        assert total == 0


# --- Listing parsing ---


class TestParseListing:
    def test_full_listing(self, provider):
        raw = {
            "header": "Owner-Operated HVAC Business",
            "listNumber": 2472123,
            "urlStub": "https://www.bizbuysell.com/business-opportunity/hvac/2472123/",
            "price": 450000,
            "cashFlow": 172000,
            "location": "Hamilton Township, NJ",
            "region": "NJ",
            "description": "Great HVAC business for sale",
            "contactInfo": {
                "contactFullName": "Jane Doe",
                "brokerCompany": "ABC Brokers",
            },
        }
        query = ListingQuery("hvac", "new jersey")
        listing = provider._parse_listing(raw, query)

        assert listing is not None
        assert listing.source == "bizbuysell"
        assert listing.source_id == "2472123"
        assert listing.name == "Owner-Operated HVAC Business"
        assert listing.asking_price == 450000.0
        assert listing.cash_flow == 172000.0
        assert listing.location == "Hamilton Township, NJ"
        assert listing.state == "NJ"
        assert listing.broker == "Jane Doe"
        assert listing.annual_revenue is None
        assert listing.days_on_market is None

    def test_auction_price_zero(self, provider):
        raw = {
            "header": "Auction Biz",
            "listNumber": 999,
            "urlStub": "https://www.bizbuysell.com/999/",
            "price": 0,
            "cashFlow": None,
            "location": "NYC, NY",
            "region": "NY",
        }
        listing = provider._parse_listing(raw, ListingQuery("hvac"))
        assert listing is not None
        assert listing.asking_price is None

    def test_auction_price_one(self, provider):
        raw = {
            "header": "Auction Biz 2",
            "listNumber": 998,
            "urlStub": "https://www.bizbuysell.com/998/",
            "price": 1,
            "cashFlow": 50000,
            "location": "LA, CA",
            "region": "CA",
        }
        listing = provider._parse_listing(raw, ListingQuery("hvac"))
        assert listing is not None
        assert listing.asking_price is None
        assert listing.cash_flow == 50000.0

    def test_missing_header_returns_none(self, provider):
        raw = {"listNumber": 111, "price": 100000}
        listing = provider._parse_listing(raw, ListingQuery("hvac"))
        assert listing is None

    def test_missing_list_number_returns_none(self, provider):
        raw = {"header": "Some Biz"}
        listing = provider._parse_listing(raw, ListingQuery("hvac"))
        assert listing is None

    def test_no_contact_info(self, provider):
        raw = {
            "header": "Simple Biz",
            "listNumber": 777,
            "urlStub": "https://www.bizbuysell.com/777/",
            "price": 200000,
            "cashFlow": None,
            "location": "Denver, CO",
            "region": "CO",
        }
        listing = provider._parse_listing(raw, ListingQuery("hvac"))
        assert listing is not None
        assert listing.broker == ""

    def test_missing_url_generates_fallback(self, provider):
        raw = {
            "header": "No URL Biz",
            "listNumber": 555,
            "price": 100000,
            "location": "Miami, FL",
            "region": "FL",
        }
        listing = provider._parse_listing(raw, ListingQuery("hvac"))
        assert listing is not None
        assert "555" in listing.url
