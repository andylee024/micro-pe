"""Reddit Sentiment Scraper Tool"""

from typing import Dict, Any, List
from datetime import datetime, timedelta

try:
    import praw
except Exception:  # pragma: no cover - fallback when dependency missing
    class _PrawStub:
        class Reddit:
            def __init__(self, *args, **kwargs):
                raise ImportError("praw is required for RedditSentimentScraper")
    praw = _PrawStub()

try:
    from textblob import TextBlob
except Exception:  # pragma: no cover - fallback when dependency missing
    TextBlob = None

from data_sources.shared.base import Tool


class RedditSentimentScraper(Tool):
    """Scrape Reddit for industry sentiment and financial quotes."""

    CACHE_TTL_DAYS = 7
    SUBREDDITS = ['sweatystartup', 'smallbusiness', 'Entrepreneur']

    def __init__(self, client_id: str, client_secret: str, user_agent: str, **kwargs):
        super().__init__(**kwargs)
        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )

    def search(
        self,
        industry: str,
        max_posts: int = 50,
        days_back: int = 90,
        extract_quotes: bool = True,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Search Reddit for industry sentiment.

        Args:
            industry: Industry keyword (e.g., "HVAC", "car wash")
            max_posts: Maximum number of posts to fetch
            days_back: How far back to search (in days)
            extract_quotes: Whether to extract financial quotes
            use_cache: Whether to use cached results

        Returns:
            Dict with posts, sentiment analysis, and top quotes
        """
        cache_key = f"reddit_{industry.replace(' ', '_')}_{max_posts}"

        # Check cache
        if use_cache:
            cached = self.load_cache(cache_key)
            if cached:
                return cached["data"]

        # Scrape posts
        posts = self._scrape_posts(industry, max_posts, days_back)

        # Analyze sentiment
        sentiment = self._analyze_sentiment(posts)

        # Extract financial quotes
        top_quotes = []
        if extract_quotes:
            top_quotes = self._extract_quotes(posts, industry)

        # Build response
        response = {
            "source": "reddit_sentiment",
            "search_date": datetime.now().isoformat(),
            "industry": industry,
            "total_posts": len(posts),
            "subreddits_searched": self.SUBREDDITS,
            "sentiment": sentiment,
            "top_quotes": top_quotes,
            "posts": posts
        }

        # Cache results
        if use_cache:
            self.save_cache(cache_key, response, self.CACHE_TTL_DAYS)

        return response

    def _scrape_posts(self, industry: str, max_posts: int, days_back: int) -> List[Dict]:
        """Scrape posts from configured subreddits."""
        results = []
        cutoff = datetime.now() - timedelta(days=days_back)
        per_sub = max_posts // len(self.SUBREDDITS)

        for name in self.SUBREDDITS:
            try:
                subreddit = self.reddit.subreddit(name)
                posts = subreddit.search(industry, limit=per_sub)

                for post in posts:
                    post_date = datetime.fromtimestamp(post.created_utc)
                    if post_date < cutoff:
                        continue

                    results.append({
                        "title": post.title,
                        "text": post.selftext or "",
                        "permalink": f"https://www.reddit.com{post.permalink}",
                        "score": post.score,
                        "num_comments": post.num_comments,
                        "subreddit": name,
                        "created_utc": post.created_utc,
                        "post_date": post_date.isoformat(),
                    })
            except Exception as e:
                print(f"Error scraping r/{name}: {e}")

        return results

    def _analyze_sentiment(self, posts: List[Dict]) -> Dict[str, Any]:
        """Analyze sentiment of posts using TextBlob."""
        if not posts:
            return {
                "average": 0.0,
                "positive": 0,
                "neutral": 0,
                "negative": 0,
            }

        if TextBlob is None:
            return {
                "average": 0.0,
                "positive": 0,
                "neutral": len(posts),
                "negative": 0,
            }

        polarities = []
        for post in posts:
            text = f"{post['title']} {post['text']}"
            polarity = TextBlob(text).sentiment.polarity
            polarities.append(polarity)

        avg = sum(polarities) / len(polarities)
        positive = sum(1 for p in polarities if p > 0.1)
        neutral = sum(1 for p in polarities if -0.1 <= p <= 0.1)
        negative = sum(1 for p in polarities if p < -0.1)

        return {
            "average": round(avg, 4),
            "positive": positive,
            "neutral": neutral,
            "negative": negative,
        }

    def _extract_quotes(self, posts: List[Dict], industry: str) -> List[Dict]:
        """Extract top financial quotes from posts."""
        financial_keywords = [
            'revenue', 'profit', 'margin', 'money', 'earning',
            'income', '$', 'dollar',
        ]

        quotes = []
        for post in posts:
            combined = f"{post['title']} {post['text']}".lower()
            if any(kw in combined for kw in financial_keywords):
                quotes.append({
                    "text": post["title"][:200],
                    "url": post["permalink"],
                    "score": post["score"],
                })

        quotes.sort(key=lambda q: q["score"], reverse=True)
        return quotes[:5]
