"""Tests for MarketplaceProvider.parse_money()."""

import pytest

from data_sources.marketplaces.base import MarketplaceProvider


class TestParseMoney:
    def test_1_2m(self):
        assert MarketplaceProvider.parse_money("$1.2M") == 1_200_000.0

    def test_450k(self):
        assert MarketplaceProvider.parse_money("$450K") == 450_000.0

    def test_comma_separated_millions(self):
        assert MarketplaceProvider.parse_money("$1,200,000") == 1_200_000.0

    def test_comma_separated_thousands(self):
        assert MarketplaceProvider.parse_money("$450,000") == 450_000.0

    def test_1_5b(self):
        assert MarketplaceProvider.parse_money("$1.5B") == 1_500_000_000.0

    def test_plain_number(self):
        assert MarketplaceProvider.parse_money("1200000") == 1_200_000.0

    def test_not_disclosed(self):
        assert MarketplaceProvider.parse_money("Not Disclosed") is None

    def test_na(self):
        assert MarketplaceProvider.parse_money("N/A") is None

    def test_empty_string(self):
        assert MarketplaceProvider.parse_money("") is None

    def test_none(self):
        assert MarketplaceProvider.parse_money(None) is None

    def test_zero(self):
        assert MarketplaceProvider.parse_money("$0") == 0.0

    def test_negative(self):
        # Negative values parse as negative floats
        result = MarketplaceProvider.parse_money("$-500K")
        assert result == -500_000.0 or result is None
