"""BizBuySell marketplace provider using undetected-chromedriver.

Extracts listing data from BBS-state Angular transfer state JSON blob.
Requires non-headless Chrome (Akamai blocks headless mode).
"""

import json
import logging
import random
import re
import subprocess
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
    # Fire protection listings are typically grouped under security categories.
    "fire protection": "security-established-businesses",
    "fire suppression": "security-established-businesses",
    "fire sprinkler": "security-established-businesses",
    "fire alarm": "security-established-businesses",
    "security and fire alarm": "security-established-businesses",
    "security services": "security-established-businesses",
    "security": "security-established-businesses",
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

# Common city-only inputs used in NL queries.
_CITY_TO_STATE_SLUG: Dict[str, str] = {
    "los angeles": "california",
    "san diego": "california",
    "san jose": "california",
    "san francisco": "california",
    "sacramento": "california",
    "new york": "new-york",
    "houston": "texas",
    "dallas": "texas",
    "austin": "texas",
    "san antonio": "texas",
    "miami": "florida",
    "orlando": "florida",
    "tampa": "florida",
    "chicago": "illinois",
    "phoenix": "arizona",
    "seattle": "washington",
    "denver": "colorado",
    "atlanta": "georgia",
    "boston": "massachusetts",
    "philadelphia": "pennsylvania",
}

FIRE_RELEVANCE_KEYWORDS: Tuple[str, ...] = (
    "fire protection",
    "fire alarm",
    "fire sprinkler",
    "sprinkler",
    "fire suppression",
    "suppression system",
    "extinguisher",
    "alarm system",
)


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

            filtered = self._apply_query_relevance_filter(all_listings, query.industry)
            return filtered[: query.max_results]

        finally:
            if driver:
                try:
                    driver.quit()
                except Exception:
                    pass

    def _make_driver(self):
        """Create a non-headless undetected-chromedriver instance."""
        import undetected_chromedriver as uc

        def _chrome_options():
            opts = uc.ChromeOptions()
            # NO --headless flag. Akamai blocks headless even with UC.
            opts.add_argument("--window-size=1920,1080")
            opts.add_argument("--no-sandbox")
            opts.add_argument("--disable-dev-shm-usage")
            return opts

        local_major = self._detect_local_chrome_major()
        if local_major:
            self.logger.info(
                f"Detected local Chrome major version {local_major}; "
                f"starting driver with version_main={local_major}"
            )
            try:
                return uc.Chrome(
                    options=_chrome_options(),
                    use_subprocess=True,
                    version_main=local_major,
                )
            except Exception as exc:
                self.logger.warning(
                    "Pinned driver startup failed for detected Chrome major "
                    f"{local_major}: {exc}"
                )

        try:
            return uc.Chrome(options=_chrome_options(), use_subprocess=True)
        except Exception as exc:
            extracted_major = self._extract_browser_major_from_driver_error(str(exc))
            if extracted_major and extracted_major != local_major:
                self.logger.warning(
                    "Retrying driver startup with extracted browser major "
                    f"{extracted_major}"
                )
                return uc.Chrome(
                    options=_chrome_options(),
                    use_subprocess=True,
                    version_main=extracted_major,
                )
            raise

    @staticmethod
    def _extract_major_version(version_text: str) -> Optional[int]:
        """Extract Chrome major version from a version string."""
        if not version_text:
            return None
        match = re.search(r"(\d+)\.", version_text)
        if not match:
            return None
        return int(match.group(1))

    @staticmethod
    def _extract_browser_major_from_driver_error(error_text: str) -> Optional[int]:
        """Extract browser major version from a ChromeDriver mismatch error."""
        if not error_text:
            return None
        match = re.search(r"Current browser version is (\d+)\.", error_text)
        if not match:
            return None
        return int(match.group(1))

    def _detect_local_chrome_major(self) -> Optional[int]:
        """Best-effort detection of locally installed Chrome major version."""
        commands = [
            ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "--version"],
            ["/Applications/Google Chrome Canary.app/Contents/MacOS/Google Chrome Canary", "--version"],
            ["google-chrome", "--version"],
            ["google-chrome-stable", "--version"],
            ["chromium", "--version"],
            ["chromium-browser", "--version"],
        ]
        for command in commands:
            try:
                proc = subprocess.run(
                    command,
                    check=False,
                    capture_output=True,
                    text=True,
                    timeout=4,
                )
            except (FileNotFoundError, OSError, subprocess.SubprocessError):
                continue

            if proc.returncode != 0:
                continue

            output = (proc.stdout or proc.stderr or "").strip()
            major = self._extract_major_version(output)
            if major:
                return major

        return None

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
        key = BizBuySellProvider._normalize_industry(industry)
        if not key:
            return None

        if key in INDUSTRY_SLUG_MAP:
            return INDUSTRY_SLUG_MAP[key]

        # Try partial match
        for slug_key, slug_val in INDUSTRY_SLUG_MAP.items():
            if slug_key in key or key in slug_key:
                return slug_val
        return None

    @staticmethod
    def _normalize_industry(industry: str) -> str:
        """Normalize user-provided industry text for slug matching."""
        key = str(industry or "").strip().lower()
        key = re.sub(r"[,&/]+", " ", key)
        key = re.sub(r"\b(business|businesses|company|companies)\b", " ", key)
        return re.sub(r"\s+", " ", key).strip()

    @classmethod
    def _relevance_keywords(cls, industry: str) -> Tuple[str, ...]:
        normalized = cls._normalize_industry(industry)
        if "fire" in normalized or "sprinkler" in normalized or "suppression" in normalized:
            return FIRE_RELEVANCE_KEYWORDS
        return ()

    def _apply_query_relevance_filter(self, listings: List[Listing], industry: str) -> List[Listing]:
        keywords = self._relevance_keywords(industry)
        if not listings or not keywords:
            return listings

        filtered: List[Listing] = []
        for listing in listings:
            text = f"{listing.name} {listing.description}".lower()
            if any(keyword in text for keyword in keywords):
                filtered.append(listing)

        if filtered:
            self.logger.info(
                "Applied fire relevance filter for '%s': %d -> %d",
                industry,
                len(listings),
                len(filtered),
            )
            return filtered

        # Fallback to unfiltered data if no keyword hits are found.
        self.logger.info(
            "Fire relevance filter found no matches for '%s'; returning unfiltered batch (%d)",
            industry,
            len(listings),
        )
        return listings

    @staticmethod
    def _to_state_slug(location: str) -> Optional[str]:
        """Parse a state from a location string and return the URL slug.

        Handles: "Texas", "TX", "Austin, TX", "texas", "tx"
        """
        if not location:
            return None

        loc = re.sub(r"\s+", " ", location.strip().lower())

        # Try as a 2-letter abbreviation
        if loc in _STATE_ABBREV_TO_NAME:
            return _STATE_ABBREV_TO_NAME[loc]

        # Try as a full state name
        if loc in _STATE_NAME_TO_SLUG:
            return _STATE_NAME_TO_SLUG[loc]

        # Try exact city match
        if loc in _CITY_TO_STATE_SLUG:
            return _CITY_TO_STATE_SLUG[loc]

        # Try extracting state from "City, ST" pattern
        if "," in loc:
            parts = loc.rsplit(",", 1)
            state_part = parts[-1].strip()
            if state_part in _STATE_ABBREV_TO_NAME:
                return _STATE_ABBREV_TO_NAME[state_part]
            if state_part in _STATE_NAME_TO_SLUG:
                return _STATE_NAME_TO_SLUG[state_part]

            city_part = parts[0].strip()
            if city_part in _CITY_TO_STATE_SLUG:
                return _CITY_TO_STATE_SLUG[city_part]

        # Try matching city as a substring
        for city, slug in _CITY_TO_STATE_SLUG.items():
            if city in loc:
                return slug

        # Try matching against state names as a substring
        for name, slug in _STATE_NAME_TO_SLUG.items():
            if name in loc:
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
    def _find_market_stats(data: dict) -> dict:
        """Extract market benchmark stats from BBS-state.

        Returns a flat dict with total_listed, median_ask, median_sde, median_multiple,
        ask_low, ask_high — or {} if not found.
        """
        def _extract_benchmarks(blob: dict) -> dict:
            if not isinstance(blob, dict) or "listedForSale" not in blob:
                return {}
            ask = blob.get("askingPriceBenchmarks") or {}
            sde = blob.get("sdeBenchmarks") or {}
            mult = blob.get("sdeMultipleBenchmarks") or {}
            return {
                "total_listed": blob.get("listedForSale"),
                "median_ask": ask.get("median"),
                "median_sde": sde.get("median"),
                "median_multiple": mult.get("median"),
                "ask_low": ask.get("lowerQuartile"),
                "ask_high": ask.get("upperQuartile"),
            }

        # Look for a key containing IndustryDetails or MarketStats
        for key in data:
            lower = key.lower()
            if any(s in lower for s in ("industrydetails", "marketstats", "bbsindustry")):
                try:
                    val = data[key].get("value", {})
                    result = _extract_benchmarks(val)
                    if result:
                        return result
                except (AttributeError, TypeError):
                    continue

        # Fallback: look inside the search results blob
        for key in data:
            if "BbsBfsSearchResults" in key:
                try:
                    result_val = data[key]["value"]["bfsSearchResult"]
                    for sub_key in ("industryData", "benchmarks", "categoryData"):
                        sub = result_val.get(sub_key) or {}
                        result = _extract_benchmarks(sub)
                        if result:
                            return result
                except (KeyError, TypeError, AttributeError):
                    continue

        return {}

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

        # Extract market benchmark stats on first page only
        if page == 1:
            stats = self._find_market_stats(data)
            if stats:
                self._last_market_stats = stats

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
