"""Tests for Google Reviews Scraper Tool"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from data_sources.maps.google_reviews import GoogleReviewsScraper


# Sample review data matching Google Places API response format
SAMPLE_REVIEWS = [
    {
        "author_name": "John Smith",
        "rating": 5,
        "text": "Great service! Very professional and reliable team. They fixed our AC quickly and the price was fair. Highly recommend this company.",
        "time": 1700000000,
        "relative_time_description": "2 months ago"
    },
    {
        "author_name": "Jane Doe",
        "rating": 4,
        "text": "Good experience overall. The technician was friendly and knowledgeable. Professional work done on time. Would use again.",
        "time": 1699000000,
        "relative_time_description": "3 months ago"
    },
    {
        "author_name": "Bob Wilson",
        "rating": 2,
        "text": "Disappointing experience. Took forever to arrive and the repair didn't last. Had to call them back again. Not worth the money.",
        "time": 1698000000,
        "relative_time_description": "4 months ago"
    },
    {
        "author_name": "Alice Brown",
        "rating": 5,
        "text": "Absolutely wonderful service. Professional, reliable, and friendly. They went above and beyond. Best HVAC company in the area.",
        "time": 1697000000,
        "relative_time_description": "5 months ago"
    },
    {
        "author_name": "Charlie Davis",
        "rating": 3,
        "text": "Average service. Nothing special but got the job done. Pricing was okay. The technician was professional enough.",
        "time": 1696000000,
        "relative_time_description": "6 months ago"
    }
]

SAMPLE_PLACE_RESPONSE = {
    "result": {
        "rating": 4.2,
        "user_ratings_total": 150,
        "reviews": SAMPLE_REVIEWS
    }
}


class TestGoogleReviewsFetch:
    """Test fetching reviews from Google Places API"""

    @pytest.fixture
    def scraper(self, tmp_path):
        """Create a GoogleReviewsScraper with mocked client"""
        with patch('data_sources.maps.google_reviews.googlemaps.Client'):
            scraper = GoogleReviewsScraper(api_key="test-api-key", cache_dir=tmp_path / "cache")
        return scraper

    def test_google_reviews_fetch(self, scraper):
        """Test that reviews are fetched and response is properly structured"""
        scraper.client.place = Mock(return_value=SAMPLE_PLACE_RESPONSE)

        result = scraper.search(place_id="ChIJtest123", use_cache=False)

        # Verify API was called correctly
        scraper.client.place.assert_called_once_with(
            "ChIJtest123",
            fields=['reviews', 'rating', 'user_ratings_total']
        )

        # Verify response structure
        assert result["source"] == "google_reviews"
        assert "search_date" in result
        assert result["place_id"] == "ChIJtest123"
        assert result["total_reviews"] == 150
        assert result["average_rating"] == 4.2
        assert isinstance(result["themes"], dict)
        assert isinstance(result["sentiment"], dict)
        assert isinstance(result["reviews"], list)
        assert len(result["reviews"]) == 5


class TestThemeExtraction:
    """Test NLP theme extraction from review texts"""

    @pytest.fixture
    def scraper(self, tmp_path):
        with patch('data_sources.maps.google_reviews.googlemaps.Client'):
            scraper = GoogleReviewsScraper(api_key="test-api-key", cache_dir=tmp_path / "cache")
        return scraper

    def test_theme_extraction(self, scraper):
        """Test that themes dict is returned with word counts"""
        scraper.client.place = Mock(return_value=SAMPLE_PLACE_RESPONSE)

        result = scraper.search(place_id="ChIJtest123", use_cache=False)

        themes = result["themes"]
        assert isinstance(themes, dict)
        assert len(themes) > 0

        # "professional" appears in multiple reviews
        assert "professional" in themes
        assert themes["professional"] >= 2

        # All values should be positive integers
        for word, count in themes.items():
            assert isinstance(count, int)
            assert count > 0
            assert len(word) >= 4  # No short words

    def test_theme_extraction_empty(self, scraper):
        """Test theme extraction with no reviews"""
        empty_response = {"result": {"rating": 0, "reviews": []}}
        scraper.client.place = Mock(return_value=empty_response)

        result = scraper.search(place_id="ChIJempty", use_cache=False)
        assert result["themes"] == {}

    def test_stopwords_excluded(self, scraper):
        """Test that stopwords are excluded from themes"""
        review_texts = ["This is very good and the service was great with professional care"]
        themes = scraper._extract_themes(review_texts)

        for stopword in ['this', 'very', 'the', 'was', 'with', 'and']:
            assert stopword not in themes


class TestSentimentAnalysis:
    """Test sentiment analysis of reviews"""

    @pytest.fixture
    def scraper(self, tmp_path):
        with patch('data_sources.maps.google_reviews.googlemaps.Client'):
            scraper = GoogleReviewsScraper(api_key="test-api-key", cache_dir=tmp_path / "cache")
        return scraper

    def test_sentiment_analysis(self, scraper):
        """Test that sentiment average is between -1 and 1"""
        scraper.client.place = Mock(return_value=SAMPLE_PLACE_RESPONSE)

        result = scraper.search(place_id="ChIJtest123", use_cache=False)

        sentiment = result["sentiment"]
        assert isinstance(sentiment, dict)
        assert "average" in sentiment
        assert "positive" in sentiment
        assert "neutral" in sentiment
        assert "negative" in sentiment

        # Average sentiment should be between -1 and 1
        assert -1 <= sentiment["average"] <= 1

        # Counts should add up to total reviews with text
        total_categorized = sentiment["positive"] + sentiment["neutral"] + sentiment["negative"]
        reviews_with_text = len([r for r in SAMPLE_REVIEWS if r.get("text")])
        assert total_categorized == reviews_with_text

        # With our sample data (3 positive, 1 negative, 1 neutral-ish), expect mostly positive
        assert sentiment["positive"] > 0
        assert sentiment["negative"] > 0

    def test_sentiment_empty_reviews(self, scraper):
        """Test sentiment with empty reviews"""
        sentiment = scraper._analyze_sentiment([])
        assert sentiment["average"] == 0.0
        assert sentiment["positive"] == 0
        assert sentiment["neutral"] == 0
        assert sentiment["negative"] == 0


class TestCaching:
    """Test caching behavior"""

    @pytest.fixture
    def scraper(self, tmp_path):
        with patch('data_sources.maps.google_reviews.googlemaps.Client'):
            scraper = GoogleReviewsScraper(api_key="test-api-key", cache_dir=tmp_path / "cache")
        return scraper

    def test_caching(self, scraper):
        """Test that second call uses cache instead of API"""
        scraper.client.place = Mock(return_value=SAMPLE_PLACE_RESPONSE)

        # First call - hits API
        result1 = scraper.search(place_id="ChIJcache_test", use_cache=True)
        assert scraper.client.place.call_count == 1

        # Second call - should use cache
        result2 = scraper.search(place_id="ChIJcache_test", use_cache=True)
        assert scraper.client.place.call_count == 1  # Still 1 - cache was used

        # Results should match
        assert result1["place_id"] == result2["place_id"]
        assert result1["total_reviews"] == result2["total_reviews"]
        assert result1["average_rating"] == result2["average_rating"]

    def test_cache_bypass(self, scraper):
        """Test that use_cache=False bypasses cache"""
        scraper.client.place = Mock(return_value=SAMPLE_PLACE_RESPONSE)

        # First call with cache
        scraper.search(place_id="ChIJbypass_test", use_cache=True)
        assert scraper.client.place.call_count == 1

        # Second call without cache - should hit API again
        scraper.search(place_id="ChIJbypass_test", use_cache=False)
        assert scraper.client.place.call_count == 2

    def test_cache_ttl_is_7_days(self, scraper):
        """Test that cache TTL is 7 days for reviews"""
        assert scraper.CACHE_TTL_DAYS == 7


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
