"""BizBuySell Market Comparables Tool"""

from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

try:
    from .base import Tool
except ImportError:
    from base import Tool


class BizBuySellTool(Tool):
    """Search for market comps on BizBuySell"""

    CACHE_TTL_DAYS = 30  # Cache for 1 month

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.output_dir = Path("outputs/benchmarks")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def search(
        self,
        industry: str,
        max_results: int = 20,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Search for business listings by industry.

        Args:
            industry: Industry keyword (e.g., "car wash", "HVAC")
            max_results: Max listings to return
            use_cache: Whether to use cached results

        Returns:
            Dict with benchmark data
        """
        print(f"\n🔍 Searching BizBuySell for: {industry}")
        print(f"   Max results: {max_results}")

        cache_key = f"bizbuysell_{industry.replace(' ', '_')}_{max_results}"

        # Check cache
        if use_cache:
            cached = self.load_cache(cache_key)
            if cached:
                print(f"✅ Using cached results from {cached['cached_at']}")
                return cached["data"]

        # Call legacy BizBuySell scraper
        from scrapers.bizbuysell import scrape_bizbuysell

        listings = scrape_bizbuysell(
            industry=industry,
            max_listings=max_results
        )

        # Build response
        response = {
            "source": "bizbuysell",
            "search_date": datetime.now().isoformat(),
            "industry": industry,
            "total_found": len(listings),
            "results": listings
        }

        # Cache results
        if use_cache:
            self.save_cache(cache_key, response, self.CACHE_TTL_DAYS)

        print(f"✅ Found {len(listings)} listings")

        return response


if __name__ == "__main__":
    # Test the tool
    tool = BizBuySellTool()
    results = tool.search(
        industry="car wash",
        max_results=10
    )

    print(f"\n✅ Found {results['total_found']} listings")
    for listing in results['results'][:3]:
        print(f"   - {listing.get('title', 'N/A')} - ${listing.get('price', 0):,}")
