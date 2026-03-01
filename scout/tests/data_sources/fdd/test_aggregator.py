"""Tests for FDD Aggregator"""

import pytest
from unittest.mock import Mock, patch
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from data_sources.fdd.aggregator import FDDAggregator


def test_aggregator_initialization():
    """Test that aggregator initializes all 4 scrapers"""
    agg = FDDAggregator()

    assert len(agg.scrapers) == 4
    assert 'minnesota' in agg.scrapers
    assert 'wisconsin' in agg.scrapers
    assert 'nasaa_fred' in agg.scrapers
    assert 'california' in agg.scrapers


@patch('data_sources.fdd.aggregator.MinnesotaFDDScraper')
@patch('data_sources.fdd.aggregator.WisconsinFDDScraper')
@patch('data_sources.fdd.aggregator.NASAAFredScraper')
@patch('data_sources.fdd.aggregator.CaliforniaFDDScraper')
def test_search_all_queries_all_scrapers(mock_ca, mock_nasaa, mock_wi, mock_mn):
    """Test that search_all queries all 4 scrapers"""
    # Setup mocks
    mock_mn_instance = Mock()
    mock_wi_instance = Mock()
    mock_nasaa_instance = Mock()
    mock_ca_instance = Mock()

    mock_mn.return_value = mock_mn_instance
    mock_wi.return_value = mock_wi_instance
    mock_nasaa.return_value = mock_nasaa_instance
    mock_ca.return_value = mock_ca_instance

    # Mock responses
    mock_response = {
        "source": "test",
        "search_date": "2026-02-20T00:00:00",
        "industry": "car wash",
        "total_found": 5,
        "results": [
            {
                "franchise_name": "Test Franchise",
                "fdd_year": 2024,
                "pdf_url": "https://example.com/test.pdf"
            }
        ]
    }

    mock_mn_instance.search.return_value = mock_response
    mock_wi_instance.search.return_value = mock_response
    mock_nasaa_instance.search.return_value = mock_response
    mock_ca_instance.search.return_value = mock_response

    # Create aggregator and search
    agg = FDDAggregator()
    results = agg.search_all(industry="car wash", max_results_per_source=5)

    # Verify all scrapers were called
    mock_mn_instance.search.assert_called_once()
    mock_wi_instance.search.assert_called_once()
    mock_nasaa_instance.search.assert_called_once()
    mock_ca_instance.search.assert_called_once()

    # Verify response structure
    assert results["source"] == "fdd_aggregator"
    assert results["industry"] == "car wash"
    assert results["total_states_searched"] == 4
    assert "by_state" in results
    assert "deduplicated" in results
    assert len(results["by_state"]) == 4


@patch('data_sources.fdd.aggregator.MinnesotaFDDScraper')
@patch('data_sources.fdd.aggregator.WisconsinFDDScraper')
@patch('data_sources.fdd.aggregator.NASAAFredScraper')
@patch('data_sources.fdd.aggregator.CaliforniaFDDScraper')
def test_deduplication(mock_ca, mock_nasaa, mock_wi, mock_mn):
    """Test that deduplication removes duplicate franchises across states"""
    # Setup mocks
    mock_mn_instance = Mock()
    mock_wi_instance = Mock()
    mock_nasaa_instance = Mock()
    mock_ca_instance = Mock()

    mock_mn.return_value = mock_mn_instance
    mock_wi.return_value = mock_wi_instance
    mock_nasaa.return_value = mock_nasaa_instance
    mock_ca.return_value = mock_ca_instance

    # Mock responses with duplicate franchises
    # McDonald's appears in both MN and CA
    mock_mn_instance.search.return_value = {
        "source": "minnesota",
        "total_found": 2,
        "results": [
            {
                "franchise_name": "McDonald's",
                "fdd_year": 2024,
                "pdf_url": "https://mn.example.com/mcdonalds.pdf",
                "has_item_19": False
            },
            {
                "franchise_name": "Subway",
                "fdd_year": 2024,
                "pdf_url": "https://mn.example.com/subway.pdf",
                "has_item_19": True
            }
        ]
    }

    mock_ca_instance.search.return_value = {
        "source": "california",
        "total_found": 2,
        "results": [
            {
                "franchise_name": "McDonald's",
                "fdd_year": 2024,
                "pdf_url": "https://ca.example.com/mcdonalds.pdf",
                "has_item_19": True  # CA version has Item 19
            },
            {
                "franchise_name": "Burger King",
                "fdd_year": 2024,
                "pdf_url": "https://ca.example.com/bk.pdf",
                "has_item_19": False
            }
        ]
    }

    mock_wi_instance.search.return_value = {"source": "wisconsin", "total_found": 0, "results": []}
    mock_nasaa_instance.search.return_value = {"source": "nasaa_fred", "total_found": 0, "results": []}

    # Create aggregator and search
    agg = FDDAggregator()
    results = agg.search_all(industry="test", max_results_per_source=10)

    # Should have 4 results before dedup (2 MN + 2 CA)
    assert results["total_found_before_dedup"] == 4

    # Should have 3 unique results after dedup (McDonald's, Subway, Burger King)
    assert results["total_unique"] == 3

    deduplicated = results["deduplicated"]
    franchise_names = [fdd["franchise_name"] for fdd in deduplicated]

    # Verify unique franchises
    assert "McDonald's" in franchise_names
    assert "Subway" in franchise_names
    assert "Burger King" in franchise_names

    # Verify McDonald's kept CA version (has Item 19)
    mcdonalds = next(fdd for fdd in deduplicated if fdd["franchise_name"] == "McDonald's")
    assert mcdonalds["has_item_19"] is True
    assert mcdonalds["source_state"] == "california"


def test_is_better_version_pdf_priority():
    """Test that version with PDF is prioritized"""
    agg = FDDAggregator()

    new = {"pdf_path": "/path/to/pdf", "has_item_19": False}
    existing = {"has_item_19": True}

    # New has PDF, existing doesn't -> new is better
    assert agg._is_better_version(new, existing) is True

    # Reverse: existing has PDF, new doesn't -> new is not better
    assert agg._is_better_version(existing, new) is False


def test_is_better_version_item19_priority():
    """Test that version with Item 19 is prioritized (when both have/don't have PDF)"""
    agg = FDDAggregator()

    # Both don't have PDF
    new = {"has_item_19": True}
    existing = {"has_item_19": False}

    # New has Item 19, existing doesn't -> new is better
    assert agg._is_better_version(new, existing) is True


def test_is_better_version_state_priority():
    """Test that larger state is prioritized (when PDF and Item 19 are equal)"""
    agg = FDDAggregator()

    # CA (priority 1) vs MN (priority 3)
    new = {"source_state": "california"}
    existing = {"source_state": "minnesota"}

    # CA has higher priority -> new is better
    assert agg._is_better_version(new, existing) is True

    # Reverse
    assert agg._is_better_version(existing, new) is False


@patch('data_sources.fdd.aggregator.MinnesotaFDDScraper')
@patch('data_sources.fdd.aggregator.WisconsinFDDScraper')
@patch('data_sources.fdd.aggregator.NASAAFredScraper')
@patch('data_sources.fdd.aggregator.CaliforniaFDDScraper')
def test_search_by_states(mock_ca, mock_nasaa, mock_wi, mock_mn):
    """Test that search_by_states only queries specified states"""
    # Setup mocks
    mock_mn_instance = Mock()
    mock_wi_instance = Mock()
    mock_nasaa_instance = Mock()
    mock_ca_instance = Mock()

    mock_mn.return_value = mock_mn_instance
    mock_wi.return_value = mock_wi_instance
    mock_nasaa.return_value = mock_nasaa_instance
    mock_ca.return_value = mock_ca_instance

    mock_response = {
        "source": "test",
        "total_found": 2,
        "results": [{"franchise_name": "Test", "fdd_year": 2024}]
    }

    mock_mn_instance.search.return_value = mock_response
    mock_ca_instance.search.return_value = mock_response

    # Create aggregator and search only MN and CA
    agg = FDDAggregator()
    results = agg.search_by_states(
        industry="car wash",
        states=["minnesota", "california"],
        max_results_per_source=5
    )

    # Only MN and CA search() should be called
    mock_mn_instance.search.assert_called_once()
    mock_ca_instance.search.assert_called_once()

    # WI and NASAA should not have search() called (but they are instantiated in __init__)
    mock_wi_instance.search.assert_not_called()
    mock_nasaa_instance.search.assert_not_called()

    # Verify response
    assert results["total_states_searched"] == 2
    assert "minnesota" in results["by_state"]
    assert "california" in results["by_state"]
    assert "wisconsin" not in results["by_state"]
    assert "nasaa_fred" not in results["by_state"]


def test_get_coverage_stats():
    """Test coverage statistics"""
    agg = FDDAggregator()
    stats = agg.get_coverage_stats()

    assert stats["total_sources"] == 4
    assert stats["total_states"] == 10
    assert stats["total_market_share"] == "90%+"

    # Verify all sources present
    assert "minnesota" in stats["sources"]
    assert "wisconsin" in stats["sources"]
    assert "nasaa_fred" in stats["sources"]
    assert "california" in stats["sources"]

    # Verify NASAA FRED covers 7 states
    assert len(stats["sources"]["nasaa_fred"]["states_covered"]) == 7
    assert "NY" in stats["sources"]["nasaa_fred"]["states_covered"]
    assert "CA" in stats["sources"]["california"]["states_covered"]


@patch('data_sources.fdd.aggregator.MinnesotaFDDScraper')
@patch('data_sources.fdd.aggregator.WisconsinFDDScraper')
@patch('data_sources.fdd.aggregator.NASAAFredScraper')
@patch('data_sources.fdd.aggregator.CaliforniaFDDScraper')
def test_error_handling(mock_ca, mock_nasaa, mock_wi, mock_mn):
    """Test that errors from one scraper don't stop others"""
    # Setup mocks
    mock_mn_instance = Mock()
    mock_wi_instance = Mock()
    mock_nasaa_instance = Mock()
    mock_ca_instance = Mock()

    mock_mn.return_value = mock_mn_instance
    mock_wi.return_value = mock_wi_instance
    mock_nasaa.return_value = mock_nasaa_instance
    mock_ca.return_value = mock_ca_instance

    # MN raises error
    mock_mn_instance.search.side_effect = Exception("Network error")

    # Others return normally
    mock_response = {"source": "test", "total_found": 1, "results": [{"franchise_name": "Test", "fdd_year": 2024}]}
    mock_wi_instance.search.return_value = mock_response
    mock_nasaa_instance.search.return_value = mock_response
    mock_ca_instance.search.return_value = mock_response

    # Create aggregator and search
    agg = FDDAggregator()
    results = agg.search_all(industry="test", max_results_per_source=5)

    # Should have results from 3 working sources + error from MN
    assert results["total_states_searched"] == 4
    assert "error" in results["by_state"]["minnesota"]
    assert results["by_state"]["minnesota"]["error"] == "Network error"

    # Other 3 should have results
    assert "error" not in results["by_state"]["wisconsin"]
    assert "error" not in results["by_state"]["nasaa_fred"]
    assert "error" not in results["by_state"]["california"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
