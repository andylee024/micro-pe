"""Reddit sentiment DataSource."""

from __future__ import annotations

import os

from data_sources.sentiment.reddit import RedditSentimentScraper
from scout.pipeline.data_sources.base import DataSource, NormalizedBatch
from scout.pipeline.models.query import Query


class RedditDataSource(DataSource):
    name = "reddit"

    def __init__(self) -> None:
        self.client_id = os.getenv("REDDIT_CLIENT_ID", "")
        self.client_secret = os.getenv("REDDIT_CLIENT_SECRET", "")
        self.user_agent = os.getenv("REDDIT_USER_AGENT", "scout-pipeline/1.0")

    def fetch(self, query: Query) -> dict[str, object]:
        if not self.client_id or not self.client_secret:
            return {
                "source": "reddit_sentiment",
                "industry": query.industry,
                "total_posts": 0,
                "sentiment": {},
                "top_quotes": [],
                "posts": [],
            }

        scraper = RedditSentimentScraper(
            client_id=self.client_id,
            client_secret=self.client_secret,
            user_agent=self.user_agent,
        )
        return scraper.search(
            industry=query.industry,
            max_posts=min(query.max_results, 50),
            use_cache=query.use_cache,
        )

    def normalize(self, raw: dict[str, object], query: Query) -> NormalizedBatch:
        return NormalizedBatch(
            businesses=[],
            listings=[],
            signals={
                "total_posts": raw.get("total_posts", 0),
                "sentiment": raw.get("sentiment", {}),
                "top_quotes": raw.get("top_quotes", []),
            },
        )
