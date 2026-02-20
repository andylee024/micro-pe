"""Tests for Reddit Sentiment Scraper"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from data_sources.sentiment.reddit import RedditSentimentScraper


@pytest.fixture
def mock_reddit():
    """Patch praw.Reddit so no real API calls are made."""
    with patch("data_sources.sentiment.reddit.praw.Reddit") as mock_cls:
        yield mock_cls


def _make_post(title, selftext, score, num_comments, subreddit, days_ago=5):
    """Helper to build a mock Reddit post."""
    post = Mock()
    post.title = title
    post.selftext = selftext
    post.score = score
    post.num_comments = num_comments
    post.permalink = f"/r/{subreddit}/comments/abc/{title.replace(' ', '_')}"
    post.created_utc = (datetime.now().timestamp()) - (days_ago * 86400)
    return post


class TestRedditSentimentScraper:

    def test_reddit_search(self, mock_reddit, tmp_path):
        """search() returns posts from mocked subreddits."""
        posts = [
            _make_post("HVAC business is booming", "Lots of revenue this year", 42, 10, "sweatystartup"),
            _make_post("Started an HVAC company", "It's been great so far", 15, 5, "sweatystartup"),
        ]

        mock_sub = MagicMock()
        mock_sub.search.return_value = iter(posts)
        mock_reddit.return_value.subreddit.return_value = mock_sub

        scraper = RedditSentimentScraper(
            client_id="fake_id",
            client_secret="fake_secret",
            user_agent="test-agent/1.0",
            cache_dir=tmp_path / "cache",
        )

        result = scraper.search("HVAC", max_posts=50, use_cache=False)

        assert result["source"] == "reddit_sentiment"
        assert result["industry"] == "HVAC"
        assert result["total_posts"] > 0
        assert "subreddits_searched" in result
        assert len(result["posts"]) > 0

        first = result["posts"][0]
        assert "title" in first
        assert "score" in first
        assert "permalink" in first

    def test_sentiment_analysis(self, mock_reddit, tmp_path):
        """Sentiment average is in valid range [-1, 1]."""
        posts = [
            _make_post("HVAC is amazing and profitable!", "Great margins", 50, 12, "smallbusiness"),
            _make_post("HVAC is terrible", "Lost all my money", 3, 20, "Entrepreneur"),
            _make_post("HVAC update", "Nothing special", 10, 2, "sweatystartup"),
        ]

        mock_sub = MagicMock()
        mock_sub.search.return_value = iter(posts)
        mock_reddit.return_value.subreddit.return_value = mock_sub

        scraper = RedditSentimentScraper(
            client_id="fake_id",
            client_secret="fake_secret",
            user_agent="test-agent/1.0",
            cache_dir=tmp_path / "cache",
        )

        result = scraper.search("HVAC", max_posts=50, use_cache=False)
        sentiment = result["sentiment"]

        assert -1.0 <= sentiment["average"] <= 1.0
        assert sentiment["positive"] + sentiment["neutral"] + sentiment["negative"] == result["total_posts"]

    def test_quote_extraction(self, mock_reddit, tmp_path):
        """Quotes are extracted from posts containing financial keywords."""
        posts = [
            _make_post("HVAC revenue hit $500k", "Profit margin is 30%", 100, 30, "sweatystartup"),
            _make_post("Nice HVAC setup", "Looks cool", 20, 5, "smallbusiness"),
            _make_post("HVAC earning potential", "Good income stream with dollars flowing", 60, 15, "Entrepreneur"),
        ]

        mock_sub = MagicMock()
        mock_sub.search.return_value = iter(posts)
        mock_reddit.return_value.subreddit.return_value = mock_sub

        scraper = RedditSentimentScraper(
            client_id="fake_id",
            client_secret="fake_secret",
            user_agent="test-agent/1.0",
            cache_dir=tmp_path / "cache",
        )

        result = scraper.search("HVAC", max_posts=50, extract_quotes=True, use_cache=False)
        quotes = result["top_quotes"]

        assert len(quotes) >= 1
        # Quotes should be sorted by score descending
        for i in range(len(quotes) - 1):
            assert quotes[i]["score"] >= quotes[i + 1]["score"]
        # "Nice HVAC setup" has no financial keyword, should not appear
        quote_texts = [q["text"] for q in quotes]
        assert not any("Nice HVAC setup" in t for t in quote_texts)

    def test_caching(self, mock_reddit, tmp_path):
        """Second call with use_cache=True returns cached data (no extra API calls)."""
        posts = [
            _make_post("Car wash profits", "Revenue is $200k", 30, 8, "sweatystartup"),
        ]

        mock_sub = MagicMock()
        mock_sub.search.return_value = iter(posts)
        mock_reddit.return_value.subreddit.return_value = mock_sub

        scraper = RedditSentimentScraper(
            client_id="fake_id",
            client_secret="fake_secret",
            user_agent="test-agent/1.0",
            cache_dir=tmp_path / "cache",
        )

        # First call — should hit the mock
        result1 = scraper.search("car wash", max_posts=20, use_cache=True)
        call_count_after_first = mock_reddit.return_value.subreddit.call_count

        # Second call — should use cache
        result2 = scraper.search("car wash", max_posts=20, use_cache=True)
        call_count_after_second = mock_reddit.return_value.subreddit.call_count

        assert call_count_after_first == call_count_after_second
        assert result1["total_posts"] == result2["total_posts"]
        assert result1["industry"] == result2["industry"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
