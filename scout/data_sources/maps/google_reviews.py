"""Google Reviews Scraper Tool - Fetch reviews with NLP theme extraction and sentiment analysis"""

import os
from typing import Dict, Any, List
from datetime import datetime
from collections import Counter

import googlemaps
from textblob import TextBlob

from data_sources.shared.base import Tool


class GoogleReviewsScraper(Tool):
    """Fetch Google reviews for a place and extract themes + sentiment"""

    CACHE_TTL_DAYS = 7  # Reviews change frequently

    STOPWORDS = {
        'the', 'a', 'an', 'is', 'was', 'are', 'were', 'and', 'or', 'but',
        'in', 'on', 'at', 'to', 'for', 'with', 'very', 'so', 'too', 'this', 'that'
    }

    def __init__(self, api_key: str = None, **kwargs):
        super().__init__(**kwargs)
        self.api_key = api_key or os.getenv("GOOGLE_MAPS_API_KEY") or os.getenv("GOOGLE_PLACES_API_KEY")
        if not self.api_key:
            raise ValueError("Google Maps API key not found. Pass api_key or set GOOGLE_MAPS_API_KEY env var.")
        self.client = googlemaps.Client(key=self.api_key)

    def search(
        self,
        place_id: str,
        extract_themes: bool = True,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Fetch reviews for a Google Place and analyze them.

        Args:
            place_id: Google Place ID (e.g. from google_maps.py results)
            extract_themes: Whether to extract word-frequency themes
            use_cache: Whether to use cached results

        Returns:
            Dict with reviews, themes, and sentiment analysis
        """
        print(f"\n[GoogleReviews] Fetching reviews for place_id: {place_id}")

        cache_key = f"reviews_{place_id}"

        # Check cache
        if use_cache:
            cached = self.load_cache(cache_key)
            if cached:
                print(f"[GoogleReviews] Using cached results from {cached['cached_at']}")
                return cached["data"]

        # Fetch place details with reviews
        place_details = self.client.place(place_id, fields=['reviews', 'rating', 'user_ratings_total'])
        result = place_details.get('result', {})

        reviews = result.get('reviews', [])
        average_rating = result.get('rating')
        total_ratings = result.get('user_ratings_total', len(reviews))

        print(f"[GoogleReviews] Got {len(reviews)} reviews, average rating: {average_rating}")

        # Extract review texts for NLP
        review_texts = [r.get('text', '') for r in reviews if r.get('text')]

        # Theme extraction
        themes = {}
        if extract_themes and review_texts:
            themes = self._extract_themes(review_texts)

        # Sentiment analysis
        sentiment = self._analyze_sentiment(reviews)

        # Build response
        response = {
            "source": "google_reviews",
            "search_date": datetime.now().isoformat(),
            "place_id": place_id,
            "total_reviews": total_ratings,
            "average_rating": average_rating,
            "themes": themes,
            "sentiment": sentiment,
            "reviews": reviews
        }

        # Cache results
        if use_cache:
            self.save_cache(cache_key, response, self.CACHE_TTL_DAYS)

        return response

    def _extract_themes(self, review_texts: List[str]) -> Dict[str, int]:
        """Extract common themes from review texts using word frequency.

        Args:
            review_texts: List of review text strings

        Returns:
            Dict of top 20 words with their counts
        """
        combined = ' '.join(review_texts).lower()

        words = combined.split()

        # Filter stopwords and short words
        filtered = [
            w.strip('.,!?;:()[]"\'') for w in words
        ]
        filtered = [
            w for w in filtered
            if len(w) >= 4 and w not in self.STOPWORDS
        ]

        counts = Counter(filtered)
        return dict(counts.most_common(20))

    def _analyze_sentiment(self, reviews: List[Dict]) -> Dict[str, Any]:
        """Analyze sentiment of reviews using TextBlob.

        Args:
            reviews: List of review dicts from Google API

        Returns:
            Dict with average polarity and positive/neutral/negative counts
        """
        if not reviews:
            return {"average": 0.0, "positive": 0, "neutral": 0, "negative": 0}

        polarities = []
        positive = 0
        neutral = 0
        negative = 0

        for review in reviews:
            text = review.get('text', '')
            if not text:
                continue
            polarity = TextBlob(text).sentiment.polarity
            polarities.append(polarity)

            if polarity > 0.1:
                positive += 1
            elif polarity < -0.1:
                negative += 1
            else:
                neutral += 1

        average = sum(polarities) / len(polarities) if polarities else 0.0

        return {
            "average": round(average, 4),
            "positive": positive,
            "neutral": neutral,
            "negative": negative
        }


if __name__ == "__main__":
    scraper = GoogleReviewsScraper()
    # Test with a known place_id (Cool Air HVAC Los Angeles or similar)
    # You can get a place_id from google_maps.py search results
    result = scraper.search(place_id="ChIJN1t_tDeuEmsRUsoyG83frY4", use_cache=False)
    print(f"\nResults: {result['total_reviews']} reviews")
    print(f"Average rating: {result['average_rating']}")
    print(f"Themes: {result['themes']}")
    print(f"Sentiment: {result['sentiment']}")
