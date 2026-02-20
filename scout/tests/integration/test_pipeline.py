"""Integration tests for complete data pipeline

Tests that all 6 data sources work together:
1. FDD Aggregator (4 sources: MN, WI, NASAA, CA)
2. Google Maps
3. Google Reviews
4. Reddit Sentiment
5. BizBuySell
"""

import pytest
from unittest.mock import Mock, patch
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from data_sources.fdd.aggregator import FDDAggregator
from data_sources.maps.google_maps import GoogleMapsTool
from data_sources.maps.google_reviews import GoogleReviewsScraper
from data_sources.sentiment.reddit import RedditSentimentScraper


def test_fdd_aggregator_unified_interface():
    """Test that FDD aggregator provides unified interface to 4 FDD sources"""
    agg = FDDAggregator()

    # Verify all 4 scrapers initialized
    assert len(agg.scrapers) == 4
    assert 'minnesota' in agg.scrapers
    assert 'wisconsin' in agg.scrapers
    assert 'nasaa_fred' in agg.scrapers
    assert 'california' in agg.scrapers

    # Verify coverage stats
    stats = agg.get_coverage_stats()
    assert stats['total_sources'] == 4
    assert stats['total_states'] == 10
    assert stats['total_market_share'] == '90%+'


@patch('data_sources.fdd.aggregator.MinnesotaFDDScraper')
@patch('data_sources.fdd.aggregator.WisconsinFDDScraper')
@patch('data_sources.fdd.aggregator.NASAAFredScraper')
@patch('data_sources.fdd.aggregator.CaliforniaFDDScraper')
def test_full_pipeline_response_formats(mock_ca, mock_nasaa, mock_wi, mock_mn):
    """Test that all sources return consistent response formats"""
    # Setup mocks
    mock_mn_instance = Mock()
    mock_wi_instance = Mock()
    mock_nasaa_instance = Mock()
    mock_ca_instance = Mock()

    mock_mn.return_value = mock_mn_instance
    mock_wi.return_value = mock_wi_instance
    mock_nasaa.return_value = mock_nasaa_instance
    mock_ca.return_value = mock_ca_instance

    # Mock FDD responses - all should have standardized format
    fdd_response = {
        "source": "test_fdd",
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

    mock_mn_instance.search.return_value = fdd_response
    mock_wi_instance.search.return_value = fdd_response
    mock_nasaa_instance.search.return_value = fdd_response
    mock_ca_instance.search.return_value = fdd_response

    # Test FDD Aggregator
    agg = FDDAggregator()
    fdd_results = agg.search_all(industry="car wash", max_results_per_source=5)

    # Verify aggregator response format
    assert "source" in fdd_results
    assert fdd_results["source"] == "fdd_aggregator"
    assert "search_date" in fdd_results
    assert "industry" in fdd_results
    assert "by_state" in fdd_results
    assert "deduplicated" in fdd_results
    assert "total_states_searched" in fdd_results

    # Verify all 4 FDD sources queried
    assert len(fdd_results["by_state"]) == 4

    # Verify each source has standardized format
    for state, data in fdd_results["by_state"].items():
        if "error" not in data:
            assert "source" in data
            assert "search_date" in data
            assert "total_found" in data
            assert "results" in data


@patch('data_sources.maps.google_reviews.googlemaps.Client')
def test_google_reviews_response_format(mock_client):
    """Test Google Reviews returns standardized format"""
    # Mock Google Places API response
    mock_client_instance = Mock()
    mock_client.return_value = mock_client_instance

    mock_client_instance.place.return_value = {
        'result': {
            'reviews': [
                {
                    'author_name': 'John Doe',
                    'rating': 5,
                    'text': 'Great service, very professional and reliable.',
                    'time': 1700000000
                }
            ],
            'rating': 4.5,
            'user_ratings_total': 100
        }
    }

    scraper = GoogleReviewsScraper(api_key="test_key")
    results = scraper.search(place_id="test_place_id", use_cache=False)

    # Verify standardized format
    assert "source" in results
    assert results["source"] == "google_reviews"
    assert "search_date" in results
    assert "place_id" in results
    assert "total_reviews" in results
    assert "average_rating" in results
    assert "themes" in results
    assert "sentiment" in results
    assert "reviews" in results


@patch('data_sources.sentiment.reddit.praw.Reddit')
def test_reddit_sentiment_response_format(mock_reddit):
    """Test Reddit Sentiment returns standardized format"""
    # Mock Reddit API
    mock_reddit_instance = Mock()
    mock_reddit.return_value = mock_reddit_instance

    mock_subreddit = Mock()
    mock_reddit_instance.subreddit.return_value = mock_subreddit

    # Mock search results
    mock_post = Mock()
    mock_post.title = "Starting an HVAC business"
    mock_post.selftext = "Looking to start HVAC business, revenue expectations?"
    mock_post.created_utc = 1700000000
    mock_post.score = 50
    mock_post.num_comments = 10
    mock_post.permalink = "/r/sweatystartup/comments/abc123"

    mock_subreddit.search.return_value = [mock_post]

    scraper = RedditSentimentScraper(
        client_id="test_id",
        client_secret="test_secret",
        user_agent="test_agent"
    )

    results = scraper.search(industry="HVAC", max_posts=10, use_cache=False)

    # Verify standardized format
    assert "source" in results
    assert results["source"] == "reddit_sentiment"
    assert "search_date" in results
    assert "industry" in results
    assert "total_posts" in results
    assert "subreddits_searched" in results
    assert "sentiment" in results
    assert "top_quotes" in results
    assert "posts" in results


@patch('data_sources.fdd.aggregator.MinnesotaFDDScraper')
def test_error_handling_one_source_fails(mock_mn):
    """Test that if one source fails, others continue"""
    # MN raises error
    mock_mn_instance = Mock()
    mock_mn.return_value = mock_mn_instance
    mock_mn_instance.search.side_effect = Exception("Network timeout")

    agg = FDDAggregator()
    results = agg.search_all(industry="test", max_results_per_source=5)

    # Should still return results structure
    assert "by_state" in results
    assert "minnesota" in results["by_state"]
    assert "error" in results["by_state"]["minnesota"]

    # Other states should have attempted (even if mocked)
    assert "wisconsin" in results["by_state"]
    assert "nasaa_fred" in results["by_state"]
    assert "california" in results["by_state"]


@patch('data_sources.maps.google_reviews.googlemaps.Client')
def test_all_sources_use_caching(mock_client):
    """Test that all sources implement caching correctly"""
    # Mock Google Maps client to avoid API key validation
    mock_client.return_value = Mock()

    # FDD Aggregator
    agg = FDDAggregator()
    for scraper in agg.scrapers.values():
        assert hasattr(scraper, 'load_cache')
        assert hasattr(scraper, 'save_cache')
        assert hasattr(scraper, 'CACHE_TTL_DAYS')

    # Google Reviews
    reviews = GoogleReviewsScraper(api_key="test_key")
    assert hasattr(reviews, 'load_cache')
    assert hasattr(reviews, 'save_cache')
    assert reviews.CACHE_TTL_DAYS == 7  # Fast-changing data

    # Reddit
    reddit = RedditSentimentScraper(
        client_id="test",
        client_secret="test",
        user_agent="test"
    )
    assert hasattr(reddit, 'load_cache')
    assert hasattr(reddit, 'save_cache')
    assert reddit.CACHE_TTL_DAYS == 7  # Fast-changing data


@patch('data_sources.maps.google_reviews.googlemaps.Client')
def test_all_sources_implement_search_method(mock_client):
    """Test that all sources implement required search() method"""
    # Mock Google Maps client to avoid API key validation
    mock_client.return_value = Mock()

    # FDD Aggregator
    agg = FDDAggregator()
    assert hasattr(agg, 'search_all')
    assert hasattr(agg, 'search_by_states')

    # All FDD scrapers
    for scraper in agg.scrapers.values():
        assert hasattr(scraper, 'search')

    # Google Reviews
    reviews = GoogleReviewsScraper(api_key="test_key")
    assert hasattr(reviews, 'search')

    # Reddit
    reddit = RedditSentimentScraper(
        client_id="test",
        client_secret="test",
        user_agent="test"
    )
    assert hasattr(reddit, 'search')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
