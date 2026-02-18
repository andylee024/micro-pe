"""Google Maps Business Search Tool"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
from dotenv import load_dotenv

try:
    from .base import Tool
except ImportError:
    from base import Tool

# Load environment variables
load_dotenv()


class GoogleMapsTool(Tool):
    """Search for businesses using Google Maps API"""

    CACHE_TTL_DAYS = 7  # Cache for 1 week

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.output_dir = Path("outputs/universe")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def search(
        self,
        industry: str,
        location: str,
        max_results: int = 100,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Search for businesses by industry and location.

        Args:
            industry: Business type (e.g., "car wash", "HVAC")
            location: Location (e.g., "Houston, TX", "California")
            max_results: Max businesses to return
            use_cache: Whether to use cached results

        Returns:
            Dict with business universe data
        """
        print(f"\n🔍 Searching Google Maps for: {industry} in {location}")
        print(f"   Max results: {max_results}")

        cache_key = f"maps_{industry.replace(' ', '_')}_{location.replace(' ', '_')}_{max_results}"

        # Check cache
        if use_cache:
            cached = self.load_cache(cache_key)
            if cached:
                print(f"✅ Using cached results from {cached['cached_at']}")
                return cached["data"]

        # Call legacy Google Maps scraper
        from scrapers.google_maps import search_google_maps

        # Get API key from environment
        api_key = os.getenv("GOOGLE_MAPS_API_KEY") or os.getenv("GOOGLE_PLACES_API_KEY")
        if not api_key:
            raise ValueError("Google Maps API key not found in environment variables")

        businesses = search_google_maps(
            industry=industry,
            city=location,
            api_key=api_key,
            max_results=max_results
        )

        # Build response
        response = {
            "source": "google_maps",
            "search_date": datetime.now().isoformat(),
            "industry": industry,
            "location": location,
            "total_found": len(businesses),
            "results": businesses
        }

        # Cache results
        if use_cache:
            self.save_cache(cache_key, response, self.CACHE_TTL_DAYS)

        print(f"✅ Found {len(businesses)} businesses")

        return response


if __name__ == "__main__":
    # Test the tool
    tool = GoogleMapsTool()
    results = tool.search(
        industry="car wash",
        location="Houston, TX",
        max_results=10
    )

    print(f"\n✅ Found {results['total_found']} businesses")
    for biz in results['results'][:3]:
        print(f"   - {biz['name']} ({biz.get('rating', 'N/A')}⭐)")
