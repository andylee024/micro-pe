"""BizBuySell Market Comparables Tool (best-effort scraping)."""

from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

import requests
from bs4 import BeautifulSoup

from data_sources.shared.base import Tool


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


def scrape_bizbuysell(industry: str, max_listings: int = 20) -> List[Dict[str, Any]]:
    """
    Best-effort scraper for BizBuySell listings.

    Note: Site is protected by bot mitigation. This uses basic requests and
    may fail depending on network environment. Returns an empty list on failure.
    """
    listings: List[Dict[str, Any]] = []
    query = industry.replace(" ", "-").lower()

    # Try multiple URL patterns
    candidate_urls = [
        f"https://www.bizbuysell.com/businesses-for-sale/{query}/",
        "https://www.bizbuysell.com/businesses-for-sale/",
    ]

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }

    for url in candidate_urls:
        try:
            params = {"q": industry} if "businesses-for-sale/" in url and url.endswith("/") else None
            resp = requests.get(url, params=params, headers=headers, timeout=20)
            if resp.status_code != 200:
                continue
            soup = BeautifulSoup(resp.text, "html.parser")
            cards = soup.select("[class*='listing']") or soup.select("[data-listing-id]") or []

            for card in cards:
                if len(listings) >= max_listings:
                    break

                title = _text_from(card, [".listing-title", "h2", "h3"])
                price = _text_from(card, [".listing-price", ".price", "[data-price]"])
                revenue = _text_from(card, [".listing-revenue", ".revenue", "[data-revenue]"])
                cash_flow = _text_from(card, [".listing-cashflow", ".cash-flow", "[data-cashflow]"])
                location = _text_from(card, [".listing-location", ".location"])
                link = _link_from(card)

                if not title:
                    continue

                listings.append(
                    {
                        "title": title,
                        "price": price,
                        "revenue": revenue,
                        "cash_flow": cash_flow,
                        "location": location,
                        "url": link,
                    }
                )

            if listings:
                break

        except Exception:
            continue

    if not listings:
        listings = _scrape_bizbuysell_selenium(industry, max_listings)

    return listings


def _scrape_bizbuysell_selenium(industry: str, max_listings: int) -> List[Dict[str, Any]]:
    """Fallback Selenium-based scrape for BizBuySell (best-effort)."""
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.common.by import By
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium.webdriver.chrome.service import Service
    except Exception:
        return []

    query = industry.replace(" ", "-").lower()
    url = f"https://www.bizbuysell.com/businesses-for-sale/{query}/"

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = None
    listings: List[Dict[str, Any]] = []
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get(url)
        cards = driver.find_elements(By.CSS_SELECTOR, "[class*='listing']")

        for card in cards:
            if len(listings) >= max_listings:
                break
            try:
                title = card.text.splitlines()[0].strip()
                link_el = card.find_element(By.CSS_SELECTOR, "a[href]")
                link = link_el.get_attribute("href")
                listings.append({"title": title, "url": link})
            except Exception:
                continue
    except Exception:
        return []
    finally:
        if driver:
            driver.quit()

    return listings


def _text_from(node, selectors: List[str]) -> str:
    for sel in selectors:
        el = node.select_one(sel)
        if el and el.get_text(strip=True):
            return el.get_text(strip=True)
    return ""


def _link_from(node) -> str:
    link = node.select_one("a[href]")
    if not link:
        return ""
    href = link.get("href", "")
    if href.startswith("/"):
        return f"https://www.bizbuysell.com{href}"
    return href


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
