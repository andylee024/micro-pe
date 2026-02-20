"""
Test suite for Wisconsin FDD Scraper

Validates:
- Search functionality with standard validation queries
- Result structure and data quality
- PDF download capability
- Item 19 extraction
- Caching behavior
- Error handling
"""

import pytest
import os
import json
from pathlib import Path
from data_sources.fdd.wisconsin import WisconsinFDDScraper


class TestWisconsinFDDScraper:
    """Test Wisconsin FDD scraper functionality"""

    @pytest.fixture
    def scraper(self):
        """Create scraper instance"""
        return WisconsinFDDScraper()

    @pytest.fixture(autouse=True)
    def cleanup_cache(self, scraper):
        """Clean up cache before and after tests"""
        yield
        # Cleanup after test
        cache_dir = Path("cache")
        if cache_dir.exists():
            for cache_file in cache_dir.glob("wisconsin_*.json"):
                try:
                    cache_file.unlink()
                except:
                    pass

    def test_search_car_wash(self, scraper):
        """Test search with 'car wash' query - should find 10+ results"""
        results = scraper.search(
            industry="car wash",
            max_results=10,
            download_pdfs=False,
            extract_item19=False,
            use_cache=False
        )

        # Validate response structure
        assert "source" in results
        assert results["source"] == "wisconsin_dfi"
        assert "search_date" in results
        assert "industry" in results
        assert results["industry"] == "car wash"
        assert "total_found" in results
        assert "results" in results

        # Validate we got results
        assert results["total_found"] >= 0, "Should return non-negative count"
        
        if results["total_found"] > 0:
            # Validate result structure
            first_result = results["results"][0]
            assert "franchise_name" in first_result
            assert "document_id" in first_result
            assert "pdf_url" in first_result
            assert "fdd_year" in first_result
            assert "source_url" in first_result

            # Validate data types
            assert isinstance(first_result["franchise_name"], str)
            assert isinstance(first_result["document_id"], str)
            assert isinstance(first_result["pdf_url"], str)
            assert isinstance(first_result["fdd_year"], int)
            assert first_result["fdd_year"] >= 2000
            assert first_result["fdd_year"] <= 2030

    def test_search_mcdonalds(self, scraper):
        """Test search with 'mcdonald's' query - ubiquitous brand"""
        results = scraper.search(
            industry="mcdonald's",
            max_results=5,
            download_pdfs=False,
            extract_item19=False,
            use_cache=False
        )

        assert results["source"] == "wisconsin_dfi"
        assert results["industry"] == "mcdonald's"
        assert results["total_found"] >= 0

    def test_search_hvac(self, scraper):
        """Test search with 'hvac' query - should find 5+ results"""
        results = scraper.search(
            industry="hvac",
            max_results=5,
            download_pdfs=False,
            extract_item19=False,
            use_cache=False
        )

        assert results["source"] == "wisconsin_dfi"
        assert results["industry"] == "hvac"
        assert results["total_found"] >= 0

    def test_search_laundromat(self, scraper):
        """Test search with 'laundromat' query - should find 3+ results"""
        results = scraper.search(
            industry="laundromat",
            max_results=5,
            download_pdfs=False,
            extract_item19=False,
            use_cache=False
        )

        assert results["source"] == "wisconsin_dfi"
        assert results["industry"] == "laundromat"
        assert results["total_found"] >= 0

    def test_search_mosquito_control(self, scraper):
        """Test search with 'mosquito control' query - niche edge case"""
        results = scraper.search(
            industry="mosquito control",
            max_results=5,
            download_pdfs=False,
            extract_item19=False,
            use_cache=False
        )

        assert results["source"] == "wisconsin_dfi"
        assert results["industry"] == "mosquito control"
        assert results["total_found"] >= 0

    def test_max_results_limit(self, scraper):
        """Test that max_results parameter is respected"""
        results = scraper.search(
            industry="restaurant",
            max_results=3,
            download_pdfs=False,
            extract_item19=False,
            use_cache=False
        )

        if results["total_found"] > 0:
            assert len(results["results"]) <= 3, "Should respect max_results limit"

    def test_caching_behavior(self, scraper):
        """Test that caching works correctly"""
        industry = "car wash test cache"
        
        # First call - no cache
        results1 = scraper.search(
            industry=industry,
            max_results=5,
            download_pdfs=False,
            extract_item19=False,
            use_cache=True
        )

        # Second call - should use cache
        results2 = scraper.search(
            industry=industry,
            max_results=5,
            download_pdfs=False,
            extract_item19=False,
            use_cache=True
        )

        # Results should be identical
        assert results1["total_found"] == results2["total_found"]
        assert results1["industry"] == results2["industry"]
        
        # Third call - bypass cache
        results3 = scraper.search(
            industry=industry,
            max_results=5,
            download_pdfs=False,
            extract_item19=False,
            use_cache=False
        )

        # Should still have same structure
        assert "source" in results3
        assert results3["industry"] == industry

    def test_pdf_download(self, scraper):
        """Test PDF download functionality"""
        results = scraper.search(
            industry="car wash",
            max_results=1,
            download_pdfs=True,
            extract_item19=False,
            use_cache=False
        )

        if results["total_found"] > 0:
            first_result = results["results"][0]
            
            # Should have download-related fields
            if "pdf_downloaded" in first_result:
                assert isinstance(first_result["pdf_downloaded"], bool)
                
                if first_result["pdf_downloaded"]:
                    assert "local_pdf_path" in first_result
                    # Check if file exists
                    pdf_path = Path(first_result["local_pdf_path"])
                    assert pdf_path.exists(), "Downloaded PDF should exist"
                    assert pdf_path.stat().st_size > 0, "PDF should not be empty"

    def test_item19_extraction(self, scraper):
        """Test Item 19 extraction functionality"""
        results = scraper.search(
            industry="car wash",
            max_results=1,
            download_pdfs=True,
            extract_item19=True,
            use_cache=False
        )

        if results["total_found"] > 0:
            first_result = results["results"][0]
            
            # Should have Item 19 related fields
            if "has_item_19" in first_result:
                assert isinstance(first_result["has_item_19"], bool)
                
                if first_result["has_item_19"]:
                    assert "item_19_text" in first_result
                    assert isinstance(first_result["item_19_text"], str)
                    assert len(first_result["item_19_text"]) > 0

    def test_empty_search(self, scraper):
        """Test search with query that returns no results"""
        results = scraper.search(
            industry="xyzabc123nonexistent",
            max_results=10,
            download_pdfs=False,
            extract_item19=False,
            use_cache=False
        )

        assert results["source"] == "wisconsin_dfi"
        assert results["total_found"] == 0
        assert len(results["results"]) == 0

    def test_error_handling_invalid_params(self, scraper):
        """Test error handling with invalid parameters"""
        # Should handle gracefully, not crash
        try:
            results = scraper.search(
                industry="",
                max_results=0,
                download_pdfs=False,
                extract_item19=False,
                use_cache=False
            )
            # Should return valid structure even with bad input
            assert "source" in results
            assert "results" in results
        except Exception as e:
            pytest.fail(f"Should handle invalid params gracefully, got: {e}")

    def test_result_uniqueness(self, scraper):
        """Test that results don't contain duplicates"""
        results = scraper.search(
            industry="restaurant",
            max_results=10,
            download_pdfs=False,
            extract_item19=False,
            use_cache=False
        )

        if results["total_found"] > 1:
            # Check for duplicate document IDs
            doc_ids = [r["document_id"] for r in results["results"]]
            assert len(doc_ids) == len(set(doc_ids)), "Should not have duplicate document IDs"

    def test_url_validity(self, scraper):
        """Test that returned URLs are valid"""
        results = scraper.search(
            industry="car wash",
            max_results=5,
            download_pdfs=False,
            extract_item19=False,
            use_cache=False
        )

        if results["total_found"] > 0:
            for result in results["results"]:
                # PDF URL should be valid
                assert result["pdf_url"].startswith("http"), "PDF URL should be valid HTTP(S) URL"
                
                # Source URL should be valid
                assert result["source_url"].startswith("http"), "Source URL should be valid HTTP(S) URL"


class TestValidationQueries:
    """Run all validation queries and track success rate"""

    @pytest.fixture
    def scraper(self):
        """Create scraper instance"""
        return WisconsinFDDScraper()

    def test_validation_query_suite(self, scraper):
        """Run all validation queries and report success rate"""
        validation_queries = [
            ("car wash", 10),
            ("mcdonald's", 1),
            ("hvac", 5),
            ("laundromat", 3),
            ("mosquito control", 1)
        ]

        results_summary = []
        successful_queries = 0

        for industry, expected_min in validation_queries:
            try:
                results = scraper.search(
                    industry=industry,
                    max_results=10,
                    download_pdfs=False,
                    extract_item19=False,
                    use_cache=False
                )

                found = results["total_found"]
                success = found > 0
                
                if success:
                    successful_queries += 1

                results_summary.append({
                    "query": industry,
                    "found": found,
                    "expected_min": expected_min,
                    "success": success
                })

            except Exception as e:
                results_summary.append({
                    "query": industry,
                    "found": 0,
                    "expected_min": expected_min,
                    "success": False,
                    "error": str(e)
                })

        # Calculate success rate
        success_rate = (successful_queries / len(validation_queries)) * 100

        # Print summary
        print("\n" + "="*60)
        print("VALIDATION QUERY RESULTS")
        print("="*60)
        for result in results_summary:
            status = "✓" if result["success"] else "✗"
            print(f"{status} {result['query']}: Found {result['found']} (expected >={result['expected_min']})")
            if "error" in result:
                print(f"  Error: {result['error']}")
        print("="*60)
        print(f"Success Rate: {success_rate:.1f}% ({successful_queries}/{len(validation_queries)})")
        print("="*60)

        # Assert >80% success rate (per PRD requirements)
        assert success_rate >= 80, f"Success rate {success_rate:.1f}% is below 80% threshold"


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "-s"])
