"""Reddit search adapter using public JSON endpoints."""

from typing import Dict, List
import requests


class RedditSearchAdapter:
    def __init__(self):
        self.base_url = "https://www.reddit.com/search.json"

    def search(self, query: str, limit: int = 25) -> Dict:
        headers = {
            "User-Agent": "scout-research-bot/1.0",
        }
        params = {
            "q": query,
            "limit": limit,
            "sort": "relevance",
            "t": "year",
        }
        try:
            resp = requests.get(self.base_url, params=params, headers=headers, timeout=15)
            if resp.status_code != 200:
                return {}
            data = resp.json()
            posts = self._parse_posts(data)
            return self._summarize(posts)
        except Exception:
            return {}

    def _parse_posts(self, payload: Dict) -> List[Dict]:
        posts = []
        for child in payload.get("data", {}).get("children", []):
            data = child.get("data", {})
            posts.append(
                {
                    "title": data.get("title", ""),
                    "subreddit": data.get("subreddit", ""),
                    "upvotes": data.get("ups", 0),
                    "comments": data.get("num_comments", 0),
                    "permalink": f"https://www.reddit.com{data.get('permalink', '')}",
                }
            )
        return posts

    def _summarize(self, posts: List[Dict]) -> Dict:
        if not posts:
            return {}
        top = sorted(posts, key=lambda p: p.get("upvotes", 0), reverse=True)[:1]
        return {
            "thread_count": len(posts),
            "overall": "Mixed",
            "overall_emoji": "😐",
            "positive_pct": 50,
            "top_thread": top[0] if top else {},
            "key_points_pos": [],
            "key_points_neg": [],
        }
