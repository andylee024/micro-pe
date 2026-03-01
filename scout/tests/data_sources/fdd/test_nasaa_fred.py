"""
Test suite for NASAA FRED FDD Scraper

Validates:
- Basic search returns results with filing_state field
- State filtering works correctly
- Caching behavior
- Empty results handling
"""

import pytest
import json
from pathlib import Path
from unittest.mock import patch, MagicMock
from data_sources.fdd.nasaa_fred import NASAAFredScraper


class TestNASAAFredScraper:
    """Test NASAA FRED FDD scraper functionality"""

    @pytest.fixture
    def scraper(self):
        """Create scraper instance"""
        return NASAAFredScraper()

    @pytest.fixture
    def mock_scrape_results(self):
        """Return realistic mock FDD results for testing without network"""
        return [
            {
                "franchise_name": "McDonald's Corporation",
                "document_id": "FDD-2024-001",
                "pdf_url": "https://www.nasaaefd.org/Franchise/Document/12345",
                "fdd_year": 2024,
                "filing_state": "NY",
                "source_url": "https://www.nasaaefd.org/Franchise/Search"
            },
            {
                "franchise_name": "McDonald's Corporation",
                "document_id": "FDD-2024-002",
                "pdf_url": "https://www.nasaaefd.org/Franchise/Document/12346",
                "fdd_year": 2024,
                "filing_state": "IL",
                "source_url": "https://www.nasaaefd.org/Franchise/Search"
            },
            {
                "franchise_name": "McDonald's Corporation",
                "document_id": "FDD-2024-003",
                "pdf_url": "https://www.nasaaefd.org/Franchise/Document/12347",
                "fdd_year": 2024,
                "filing_state": "MD",
                "source_url": "https://www.nasaaefd.org/Franchise/Search"
            },
            {
                "franchise_name": "McDonald's Corporation",
                "document_id": "FDD-2024-004",
                "pdf_url": "https://www.nasaaefd.org/Franchise/Document/12348",
                "fdd_year": 2024,
                "filing_state": "VA",
                "source_url": "https://www.nasaaefd.org/Franchise/Search"
            },
            {
                "franchise_name": "McDonald's Corporation",
                "document_id": "FDD-2024-005",
                "pdf_url": "https://www.nasaaefd.org/Franchise/Document/12349",
                "fdd_year": 2024,
                "filing_state": "WA",
                "source_url": "https://www.nasaaefd.org/Franchise/Search"
            },
        ]

    @pytest.fixture(autouse=True)
    def cleanup_cache(self, scraper):
        """Clean up cache before and after tests"""
        yield
        cache_dir = Path("outputs/cache")
        if cache_dir.exists():
            for cache_file in cache_dir.glob("nasaa_fred_*.json"):
                try:
                    cache_file.unlink()
                except Exception:
                    pass

    def test_nasaa_fred_search(self, scraper, mock_scrape_results):
        """Test basic search returns results with filing_state field"""
        with patch.object(scraper, '_scrape_fdds', return_value=mock_scrape_results):
            results = scraper.search(
                industry="McDonald's",
                max_results=10,
                download_pdfs=False,
                extract_item19=False,
                use_cache=False
            )

        # Validate response structure
        assert "source" in results
        assert results["source"] == "nasaa_fred"
        assert "search_date" in results
        assert "industry" in results
        assert results["industry"] == "McDonald's"
        assert "states_searched" in results
        assert results["states_searched"] == ["NY", "IL", "MD", "VA", "WA", "ND", "RI"]
        assert "total_found" in results
        assert "results" in results

        # Should have results
        assert results["total_found"] == 5
        assert len(results["results"]) == 5

        # Validate each result has filing_state
        for fdd in results["results"]:
            assert "franchise_name" in fdd
            assert "filing_state" in fdd
            assert fdd["filing_state"] in scraper.STATES, \
                f"filing_state '{fdd['filing_state']}' not in expected states"
            assert "document_id" in fdd
            assert "pdf_url" in fdd
            assert "fdd_year" in fdd
            assert isinstance(fdd["fdd_year"], int)
            assert 2000 <= fdd["fdd_year"] <= 2030

        # Verify results span multiple states
        states_found = set(fdd["filing_state"] for fdd in results["results"])
        assert len(states_found) > 1, "Should find results from multiple states"

    def test_state_filtering(self, scraper, mock_scrape_results):
        """Test filtering by states parameter works correctly"""
        with patch.object(scraper, '_scrape_fdds', return_value=mock_scrape_results):
            results = scraper.search(
                industry="McDonald's",
                max_results=10,
                states=["NY", "IL"],
                download_pdfs=False,
                extract_item19=False,
                use_cache=False
            )

        # Should only contain NY and IL results
        assert results["total_found"] == 2
        assert results["states_searched"] == ["NY", "IL"]

        for fdd in results["results"]:
            assert fdd["filing_state"] in ["NY", "IL"], \
                f"Result state '{fdd['filing_state']}' should be NY or IL"

        # Test with a single state
        with patch.object(scraper, '_scrape_fdds', return_value=mock_scrape_results):
            results_va = scraper.search(
                industry="McDonald's",
                max_results=10,
                states=["VA"],
                download_pdfs=False,
                extract_item19=False,
                use_cache=False
            )

        assert results_va["total_found"] == 1
        assert results_va["results"][0]["filing_state"] == "VA"

    def test_caching(self, scraper, mock_scrape_results):
        """Test cache hit on second call with same params"""
        with patch.object(scraper, '_scrape_fdds', return_value=mock_scrape_results) as mock_scrape:
            # First call - should scrape
            results1 = scraper.search(
                industry="test_cache_query",
                max_results=5,
                download_pdfs=False,
                extract_item19=False,
                use_cache=True
            )
            assert mock_scrape.call_count == 1

            # Second call - should use cache (no additional scrape call)
            results2 = scraper.search(
                industry="test_cache_query",
                max_results=5,
                download_pdfs=False,
                extract_item19=False,
                use_cache=True
            )
            # _scrape_fdds should NOT be called again
            assert mock_scrape.call_count == 1, \
                "Second call should use cache, not scrape again"

        # Results should be identical
        assert results1["total_found"] == results2["total_found"]
        assert results1["industry"] == results2["industry"]
        assert results1["source"] == results2["source"]
        assert len(results1["results"]) == len(results2["results"])

    def test_empty_results(self, scraper):
        """Test handles no results gracefully (empty list, not error)"""
        with patch.object(scraper, '_scrape_fdds', return_value=[]):
            results = scraper.search(
                industry="xyzabc123nonexistent",
                max_results=10,
                download_pdfs=False,
                extract_item19=False,
                use_cache=False
            )

        # Should return valid structure with empty results
        assert results["source"] == "nasaa_fred"
        assert results["total_found"] == 0
        assert results["results"] == []
        assert results["industry"] == "xyzabc123nonexistent"
        assert "search_date" in results
        assert "states_searched" in results


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
