"""BizBuySell marketplace provider using undetected-chromedriver.

Extracts listing data from BBS-state Angular transfer state JSON blob.
Requires non-headless Chrome (Akamai blocks headless mode).
"""

import json
import logging
import random
import time
from typing import Dict, List, Optional, Tuple

from data_sources.marketplaces.base import ListingQuery, MarketplaceProvider
from scout.domain.listing import Listing

logger = logging.getLogger(__name__)

# Map our industry names to BizBuySell sub-category URL slugs.
# Values are the urlStub from BBS-state categoryHierarchy.
INDUSTRY_SLUG_MAP: Dict[str, str] = {
    "hvac": "hvac-businesses",
    "plumbing": "plumbing-businesses",
    "electrical": "electrical-and-mechanical-contracting-businesses",
    "car wash": "car-washes",
    "landscaping": "landscaping-and-yard-service-businesses",
    "cleaning": "cleaning-businesses",
    "pest control": "pest-control-businesses",
    "auto repair": "auto-repair-and-service-shops",
    "restaurant": "restaurants-and-food-businesses",
    "pool service": "service-businesses",
    # Parent categories (fallback when no sub-category match)
    "building and construction": "building-and-construction-businesses",
    "automotive": "automotive-and-boat-businesses",
    "service": "service-businesses",
    "retail": "retail-businesses",
    "manufacturing": "manufacturing-businesses",
    "health care": "health-care-and-fitness-businesses",
}

# State name / abbreviation -> URL slug (lowercase full name).
_STATE_ABBREV_TO_NAME: Dict[str, str] = {
    "al": "alabama", "ak": "alaska", "az": "arizona", "ar": "arkansas",
    "ca": "california", "co": "colorado", "ct": "connecticut", "de": "delaware",
    "fl": "florida", "ga": "georgia", "hi": "hawaii", "id": "idaho",
    "il": "illinois", "in": "indiana", "ia": "iowa", "ks": "kansas",
    "ky": "kentucky", "la": "louisiana", "me": "maine", "md": "maryland",
    "ma": "massachusetts", "mi": "michigan", "mn": "minnesota", "ms": "mississippi",
    "mo": "missouri", "mt": "montana", "ne": "nebraska", "nv": "nevada",
    "nh": "new-hampshire", "nj": "new-jersey", "nm": "new-mexico", "ny": "new-york",
    "nc": "north-carolina", "nd": "north-dakota", "oh": "ohio", "ok": "oklahoma",
    "or": "oregon", "pa": "pennsylvania", "ri": "rhode-island", "sc": "south-carolina",
    "sd": "south-dakota", "tn": "tennessee", "tx": "texas", "ut": "utah",
    "vt": "vermont", "va": "virginia", "wa": "washington", "wv": "west-virginia",
    "wi": "wisconsin", "wy": "wyoming", "dc": "district-of-columbia",
}

# Also accept full state names (lowered)
_STATE_NAME_TO_SLUG: Dict[str, str] = {
    v.replace("-", " "): v for v in _STATE_ABBREV_TO_NAME.values()
}


class BizBuySellProvider(MarketplaceProvider):
    """Fetch business-for-sale listings from BizBuySell via undetected-chromedriver."""

    SOURCE_ID = "bizbuysell"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._warmup_delay = 3.0
        self._page_delay_range = (2.0, 4.0)
        self._retry_delay = 8.0

    def _fetch(self, query: ListingQuery) -> List[Listing]:
        """Fetch listings from BizBuySell. Handles driver lifecycle."""
        driver = None
        try:
            driver = self._make_driver()
            all_listings: List[Listing] = []
            page = 1

            while len(all_listings) < query.max_results:
                page_listings, total = self._fetch_page(driver, query, page)

                if not page_listings:
                    break

                all_listings.extend(page_listings)
                self.logger.info(
                    f"Page {page}: got {len(page_listings)} listings "
                    f"(total so far: {len(all_listings)}, server total: {total})"
                )

                if len(all_listings) >= query.max_results:
                    break
                if total > 0 and page * 50 >= total:
                    break

                page += 1
                time.sleep(random.uniform(*self._page_delay_range))

            return all_listings[: query.max_results]

        finally:
            if driver:
                try:
                    driver.quit()
                except Exception:
                    pass

    def _make_driver(self):
        """Create a non-headless undetected-chromedriver instance."""
        import undetected_chromedriver as uc

        opts = uc.ChromeOptions()
        # NO --headless flag. Akamai blocks headless even with UC.
        opts.add_argument("--window-size=1920,1080")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        driver = uc.Chrome(options=opts, use_subprocess=True)
        return driver

    def _build_url(self, query: ListingQuery, page: int = 1) -> str:
        """Build the BizBuySell search URL for industry + location + page."""
        slug = self._to_industry_slug(query.industry)
        if not slug:
            slug = "service-businesses"
            self.logger.warning(
                f"No slug for industry '{query.industry}', falling back to service-businesses"
            )

        state_slug = self._to_state_slug(query.location) if query.location else None

        if state_slug:
            url = f"https://www.bizbuysell.com/{state_slug}/{slug}-for-sale/"
        else:
            url = f"https://www.bizbuysell.com/{slug}-for-sale/"

        if page > 1:
            url += f"{page}/"

        return url

    @staticmethod
    def _to_industry_slug(industry: str) -> Optional[str]:
        """Map an industry string to a BizBuySell URL slug (case-insensitive)."""
        key = industry.strip().lower()
        if key in INDUSTRY_SLUG_MAP:
            return INDUSTRY_SLUG_MAP[key]
        # Try partial match
        for slug_key, slug_val in INDUSTRY_SLUG_MAP.items():
            if slug_key in key or key in slug_key:
                return slug_val
        return None

    @staticmethod
    def _to_state_slug(location: str) -> Optional[str]:
        """Parse a state from a location string and return the URL slug.

        Handles: "Texas", "TX", "Austin, TX", "texas", "tx"
        """
        if not location:
            return None

        loc = location.strip().lower()

        # Try as a 2-letter abbreviation
        if loc in _STATE_ABBREV_TO_NAME:
            return _STATE_ABBREV_TO_NAME[loc]

        # Try as a full state name
        if loc in _STATE_NAME_TO_SLUG:
            return _STATE_NAME_TO_SLUG[loc]

        # Try extracting state from "City, ST" pattern
        if "," in loc:
            parts = loc.rsplit(",", 1)
            state_part = parts[-1].strip()
            if state_part in _STATE_ABBREV_TO_NAME:
                return _STATE_ABBREV_TO_NAME[state_part]
            if state_part in _STATE_NAME_TO_SLUG:
                return _STATE_NAME_TO_SLUG[state_part]

        # Try matching against state names as a substring
        for name, slug in _STATE_NAME_TO_SLUG.items():
            if name == loc:
                return slug

        return None

    def _load_page(self, driver, url: str) -> str:
        """Load a URL with warmup visit and retry on block."""
        # Warmup: visit homepage first
        self.logger.info("Warming up with homepage visit...")
        driver.get("https://www.bizbuysell.com/")
        time.sleep(self._warmup_delay + random.uniform(1.0, 3.0))

        self.logger.info(f"Loading {url}")
        driver.get(url)
        time.sleep(4.0 + random.uniform(1.0, 3.0))

        # Retry up to 2 times if blocked or BBS-state not found
        for attempt in range(2):
            page_source = driver.page_source or ""
            has_bbs = self._check_bbs_state(driver)
            blocked = (
                len(page_source) < 5000
                or "Access Denied" in page_source
                or "sec-if-cpt-container" in page_source
            )

            if has_bbs and not blocked:
                return page_source

            self.logger.warning(
                f"Block/missing data detected (attempt {attempt + 1}/2), "
                f"retrying after delay..."
            )
            time.sleep(self._retry_delay + random.uniform(2.0, 5.0))
            driver.get(url)
            time.sleep(5.0 + random.uniform(1.0, 3.0))

        return driver.page_source or ""

    def _check_bbs_state(self, driver) -> bool:
        """Quick check if BBS-state element exists in the page."""
        try:
            result = driver.execute_script(
                "return !!document.getElementById('BBS-state');"
            )
            return bool(result)
        except Exception:
            return False

    def _load_page_direct(self, driver, url: str) -> str:
        """Load a URL directly (no warmup). Used for pagination after first page."""
        self.logger.info(f"Loading {url}")
        driver.get(url)
        time.sleep(4.0 + random.uniform(1.0, 2.0))

        page_source = driver.page_source or ""
        has_bbs = self._check_bbs_state(driver)
        blocked = (
            len(page_source) < 5000
            or "Access Denied" in page_source
            or "sec-if-cpt-container" in page_source
        )

        if not has_bbs or blocked:
            self.logger.warning("Possible block detected, retrying after delay...")
            time.sleep(self._retry_delay + random.uniform(2.0, 4.0))
            driver.get(url)
            time.sleep(5.0 + random.uniform(1.0, 3.0))
            page_source = driver.page_source or ""

        return page_source

    def _extract_bbs_state(self, driver) -> Optional[dict]:
        """Extract and parse the BBS-state JSON blob via JS execution."""
        try:
            raw = driver.execute_script(
                "const el = document.getElementById('BBS-state'); "
                "return el ? el.textContent : null;"
            )
            if not raw:
                self.logger.warning("BBS-state element not found")
                return None
            return json.loads(raw)
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse BBS-state JSON: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Failed to extract BBS-state: {e}")
            return None

    @staticmethod
    def _find_listings_array(data: dict) -> Tuple[list, int]:
        """Find the listings array and total count in the BBS-state data.

        Returns (listings_list, total_count).
        """
        for key in data:
            if "BbsBfsSearchResults" in key:
                try:
                    result = data[key]["value"]["bfsSearchResult"]
                    listings = result.get("value", [])
                    total = result.get("total", 0)
                    return (listings if isinstance(listings, list) else [], total)
                except (KeyError, TypeError):
                    continue
        return ([], 0)

    def _parse_listing(self, raw: dict, query: ListingQuery) -> Optional[Listing]:
        """Map a BBS-state listing dict to a Listing dataclass."""
        try:
            header = raw.get("header", "")
            if not header:
                return None

            source_id = str(raw.get("listNumber", ""))
            if not source_id:
                return None

            url = raw.get("urlStub", "")
            if not url:
                url = f"https://www.bizbuysell.com/business-opportunity/{source_id}/"

            # Price: integer USD. 0 or 1 are auction markers -> None
            price = raw.get("price")
            asking_price: Optional[float] = None
            if price is not None and isinstance(price, (int, float)) and price > 1:
                asking_price = float(price)

            # Cash flow
            cash_flow_raw = raw.get("cashFlow")
            cash_flow: Optional[float] = None
            if cash_flow_raw is not None and isinstance(cash_flow_raw, (int, float)):
                cash_flow = float(cash_flow_raw)

            location = raw.get("location", "")
            state = raw.get("region", "")

            description = raw.get("description", "")

            # Broker info
            contact_info = raw.get("contactInfo") or {}
            broker = contact_info.get("contactFullName", "")

            return Listing(
                source=self.SOURCE_ID,
                source_id=source_id,
                url=url,
                name=header,
                industry=query.industry,
                location=location,
                state=state,
                description=description,
                asking_price=asking_price,
                annual_revenue=None,  # Not available in search results
                cash_flow=cash_flow,
                days_on_market=None,  # Not available in search results
                broker=broker,
                listed_at=None,  # Not available in search results
            )
        except Exception as e:
            self.logger.warning(f"Failed to parse listing: {e}")
            return None

    def _fetch_page(
        self, driver, query: ListingQuery, page: int
    ) -> Tuple[List[Listing], int]:
        """Fetch one page of results. Returns (listings, total)."""
        url = self._build_url(query, page)

        if page == 1:
            self._load_page(driver, url)
        else:
            self._load_page_direct(driver, url)

        data = self._extract_bbs_state(driver)
        if data is None:
            return ([], 0)

        raw_listings, total = self._find_listings_array(data)
        if not raw_listings:
            return ([], total)

        listings: List[Listing] = []
        for raw in raw_listings:
            # Filter out ads/sponsored (listingTypeId 40 = standard)
            listing_type = raw.get("listingTypeId")
            if listing_type is not None and listing_type != 40:
                continue

            listing = self._parse_listing(raw, query)
            if listing:
                listings.append(listing)

        return (listings, total)

    @staticmethod
    def extract_market_stats(data: dict) -> Optional[dict]:
        """Extract market-level benchmark stats from BBS-state (bonus data)."""
        for key in data:
            if "BbsIndustryDetails" in key or "MarketStats" in key:
                try:
                    return data[key]["value"]
                except (KeyError, TypeError):
                    continue
        return None
