"""Reddit search adapter using public JSON endpoints."""

from typing import Dict, List
import requests


class RedditSearchAdapter:
    def __init__(self):
        self.base_url = "https://www.reddit.com/search.json"

    def search(self, industry: str, location: str = "", use_cache: bool = True) -> dict:
        """
        Search Reddit for posts about a given industry using multiple queries.

        Runs up to 3 queries, deduplicates by post id, and returns the top 8
        posts sorted by score alongside a thread count.
        """
        queries = [
            f"{industry} acquisition",
            f"buying {industry} business",
            f"{industry} small business owner",
        ]

        headers = {"User-Agent": "Scout/1.0"}
        params_base = {"sort": "relevance", "t": "year", "limit": 10}

        seen_ids: set = set()
        all_posts: List[Dict] = []

        for query in queries:
            try:
                params = {**params_base, "q": query}
                resp = requests.get(
                    self.base_url, params=params, headers=headers, timeout=5
                )
                if resp.status_code != 200:
                    continue
                data = resp.json()
                children = data.get("data", {}).get("children", [])
                for child in children:
                    post = child.get("data", {})
                    post_id = post.get("id")
                    if post_id and post_id not in seen_ids:
                        seen_ids.add(post_id)
                        all_posts.append(child)
            except Exception:
                continue  # skip this query on any error

        if not all_posts:
            return {"thread_count": 0, "reddit_threads": []}

        # Sort by score (upvotes) descending
        all_posts.sort(
            key=lambda c: c.get("data", {}).get("score", 0), reverse=True
        )

        top_posts = all_posts[:8]
        reddit_threads = [
            {
                "title": p["data"].get("title", ""),
                "sub": p["data"].get("subreddit_name_prefixed", ""),
                "excerpt": (
                    p["data"].get("selftext", "")[:150].strip()
                    or p["data"].get("title", "")
                ),
            }
            for p in top_posts
        ]

        return {
            "thread_count": len(all_posts),
            "reddit_threads": reddit_threads,
        }
