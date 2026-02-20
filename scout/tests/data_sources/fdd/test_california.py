"""
Test suite for California FDD Scraper

Validates:
- Search functionality with standard validation queries
- Document type filtering (only FDDs, no Blacklines/Applications)
- Caching behavior
- Pagination for >10 results
"""

import pytest
import json
from pathlib import Path
from unittest.mock import patch, MagicMock
from datetime import datetime

from data_sources.fdd.california import CaliforniaFDDScraper, FDD_DOCUMENT_TYPES, NON_FDD_DOCUMENT_TYPES


class TestCaliforniaFDDScraper:
    """Test California FDD scraper functionality"""

    @pytest.fixture
    def scraper(self):
        """Create scraper instance"""
        return CaliforniaFDDScraper()

    @pytest.fixture(autouse=True)
    def cleanup_cache(self, scraper):
        """Clean up cache before and after tests"""
        yield
        cache_dir = Path("cache/california_fdd")
        if cache_dir.exists():
            for cache_file in cache_dir.glob("*.json"):
                try:
                    cache_file.unlink()
                except Exception:
                    pass

    # ----------------------------------------------------------------
    # Test 1: Basic search works
    # ----------------------------------------------------------------
    def test_california_search(self, scraper):
        """Test basic search returns correctly structured results"""
        results = scraper.search(
            industry="car wash",
            max_results=10,
            download_pdfs=False,
            extract_item19=False,
            use_cache=False,
        )

        # Validate response structure
        assert "source" in results
        assert results["source"] == "california_fdd"
        assert "search_date" in results
        assert "industry" in results
        assert results["industry"] == "car wash"
        assert "total_found" in results
        assert isinstance(results["total_found"], int)
        assert results["total_found"] >= 0
        assert "results" in results
        assert isinstance(results["results"], list)

        # If results found, validate structure of each
        if results["total_found"] > 0:
            first = results["results"][0]
            assert "franchise_name" in first
            assert "document_type" in first
            assert "pdf_url" in first
            assert "source_url" in first

            assert isinstance(first["franchise_name"], str)
            assert len(first["franchise_name"]) > 0

            # All results should be FDD type
            for r in results["results"]:
                assert r["document_type"] == "FDD", (
                    f"Expected document_type='FDD', got '{r['document_type']}' "
                    f"for {r['franchise_name']}"
                )

    # ----------------------------------------------------------------
    # Test 2: Document filtering - only FDDs returned
    # ----------------------------------------------------------------
    def test_document_filtering(self, scraper):
        """Test that _filter_document_type correctly removes non-FDD documents"""
        # Create mixed results with various document types
        mixed_results = [
            {
                "franchise_name": "Good Franchise A",
                "document_id": "001",
                "document_type": "FDD",
                "pdf_url": "https://example.com/a.pdf",
                "fdd_year": 2024,
                "source_url": "https://docqnet.dfpi.ca.gov/search/",
            },
            {
                "franchise_name": "Blackline Corp",
                "document_id": "002",
                "document_type": "Blackline",
                "pdf_url": "https://example.com/b.pdf",
                "fdd_year": 2024,
                "source_url": "https://docqnet.dfpi.ca.gov/search/",
            },
            {
                "franchise_name": "Application Inc",
                "document_id": "003",
                "document_type": "Application",
                "pdf_url": "https://example.com/c.pdf",
                "fdd_year": 2023,
                "source_url": "https://docqnet.dfpi.ca.gov/search/",
            },
            {
                "franchise_name": "Good Franchise B",
                "document_id": "004",
                "document_type": "Franchise Disclosure Document",
                "pdf_url": "https://example.com/d.pdf",
                "fdd_year": 2024,
                "source_url": "https://docqnet.dfpi.ca.gov/search/",
            },
            {
                "franchise_name": "Amendment LLC",
                "document_id": "005",
                "document_type": "Amendment",
                "pdf_url": "https://example.com/e.pdf",
                "fdd_year": 2023,
                "source_url": "https://docqnet.dfpi.ca.gov/search/",
            },
            {
                "franchise_name": "Unknown Type Corp",
                "document_id": "006",
                "document_type": "",
                "pdf_url": "https://example.com/f.pdf",
                "fdd_year": 2024,
                "source_url": "https://docqnet.dfpi.ca.gov/search/",
            },
            {
                "franchise_name": "Annual Report Co",
                "document_id": "007",
                "document_type": "Annual Report",
                "pdf_url": "https://example.com/g.pdf",
                "fdd_year": 2024,
                "source_url": "https://docqnet.dfpi.ca.gov/search/",
            },
        ]

        filtered = scraper._filter_document_type(mixed_results)

        # Should keep FDD, Franchise Disclosure Document, and empty/unknown types
        assert len(filtered) == 3, (
            f"Expected 3 FDDs, got {len(filtered)}: "
            f"{[r['franchise_name'] for r in filtered]}"
        )

        # Verify the right ones survived
        names = {r["franchise_name"] for r in filtered}
        assert "Good Franchise A" in names
        assert "Good Franchise B" in names
        assert "Unknown Type Corp" in names

        # Verify blackline, application, amendment, annual report were removed
        assert "Blackline Corp" not in names
        assert "Application Inc" not in names
        assert "Amendment LLC" not in names
        assert "Annual Report Co" not in names

        # All surviving results should be tagged as FDD
        for r in filtered:
            assert r["document_type"] == "FDD"

    # ----------------------------------------------------------------
    # Test 3: Caching works
    # ----------------------------------------------------------------
    def test_caching(self, scraper):
        """Test that cache saves and loads correctly"""
        industry = "test_cache_query_xyz"
        cache_key = scraper._get_cache_key(industry, 5, False, False)

        # Ensure no cache exists
        cache_path = scraper._get_cache_path(cache_key)
        if cache_path.exists():
            cache_path.unlink()

        # First call -- scrapes (or returns empty for non-existent query)
        results1 = scraper.search(
            industry=industry,
            max_results=5,
            download_pdfs=False,
            extract_item19=False,
            use_cache=True,
        )

        assert results1["source"] == "california_fdd"
        assert results1["industry"] == industry

        # Cache file should now exist
        assert cache_path.exists(), "Cache file should be created after first search"

        # Second call -- should use cache
        results2 = scraper.search(
            industry=industry,
            max_results=5,
            download_pdfs=False,
            extract_item19=False,
            use_cache=True,
        )

        # Results should match
        assert results1["total_found"] == results2["total_found"]
        assert results1["industry"] == results2["industry"]
        assert results1["source"] == results2["source"]

        # Third call -- bypass cache
        results3 = scraper.search(
            industry=industry,
            max_results=5,
            download_pdfs=False,
            extract_item19=False,
            use_cache=False,
        )

        assert results3["source"] == "california_fdd"
        assert results3["industry"] == industry

    # ----------------------------------------------------------------
    # Test 4: Pagination for >10 results
    # ----------------------------------------------------------------
    def test_pagination(self, scraper):
        """Test that requesting >10 results triggers pagination handling.

        This test validates that:
        1. The scraper accepts max_results > 10
        2. The response structure is correct regardless of actual count
        3. The pagination method exists and is callable
        """
        results = scraper.search(
            industry="restaurant",
            max_results=20,
            download_pdfs=False,
            extract_item19=False,
            use_cache=False,
        )

        # Validate response structure
        assert results["source"] == "california_fdd"
        assert results["industry"] == "restaurant"
        assert isinstance(results["total_found"], int)
        assert results["total_found"] >= 0
        assert isinstance(results["results"], list)

        # If the site returned results, verify we attempted to get more than 10
        # (the actual count depends on what the live site returns)
        if results["total_found"] > 0:
            # Results should respect the max_results limit
            assert len(results["results"]) <= 20

            # All should be FDD type (filtering applied)
            for r in results["results"]:
                assert r["document_type"] == "FDD"

        # Verify the pagination method is properly defined and callable
        assert hasattr(scraper, "_handle_pagination")
        assert callable(scraper._handle_pagination)


class TestCaliforniaHelpers:
    """Test helper methods in isolation"""

    @pytest.fixture
    def scraper(self):
        return CaliforniaFDDScraper()

    def test_extract_year_from_text(self, scraper):
        """Test year extraction from various text formats"""
        assert scraper._extract_year_from_text("FDD 2024") == 2024
        assert scraper._extract_year_from_text("4/30/2025") == 2025
        assert scraper._extract_year_from_text("Filed 2023-01-15") == 2023
        assert scraper._extract_year_from_text("No year here") is None
        assert scraper._extract_year_from_text("") is None
        assert scraper._extract_year_from_text(None) is None

    def test_filter_document_type_empty(self, scraper):
        """Test filtering with empty list"""
        assert scraper._filter_document_type([]) == []

    def test_filter_document_type_all_fdd(self, scraper):
        """Test filtering when all are FDDs"""
        results = [
            {"franchise_name": "A", "document_type": "FDD"},
            {"franchise_name": "B", "document_type": "fdd"},
            {"franchise_name": "C", "document_type": "Franchise Disclosure Document"},
        ]
        filtered = scraper._filter_document_type(results)
        assert len(filtered) == 3

    def test_filter_document_type_all_non_fdd(self, scraper):
        """Test filtering when none are FDDs"""
        results = [
            {"franchise_name": "A", "document_type": "Blackline"},
            {"franchise_name": "B", "document_type": "Application"},
            {"franchise_name": "C", "document_type": "Amendment"},
        ]
        filtered = scraper._filter_document_type(results)
        assert len(filtered) == 0

    def test_cache_key_deterministic(self, scraper):
        """Test that same params produce same cache key"""
        key1 = scraper._get_cache_key("car wash", 10, False, False)
        key2 = scraper._get_cache_key("car wash", 10, False, False)
        assert key1 == key2

    def test_cache_key_different_params(self, scraper):
        """Test that different params produce different cache keys"""
        key1 = scraper._get_cache_key("car wash", 10, False, False)
        key2 = scraper._get_cache_key("hvac", 10, False, False)
        assert key1 != key2

    def test_response_format(self, scraper):
        """Test that search returns the standardized response format"""
        # Use a query unlikely to have results -- tests the empty-result path
        results = scraper.search(
            industry="xyznonexistent123abc",
            max_results=5,
            download_pdfs=False,
            extract_item19=False,
            use_cache=False,
        )

        # Must have all required top-level keys
        required_keys = {"source", "search_date", "industry", "total_found", "results"}
        assert required_keys.issubset(results.keys()), (
            f"Missing keys: {required_keys - results.keys()}"
        )

        assert results["source"] == "california_fdd"
        assert results["total_found"] == 0
        assert results["results"] == []


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
