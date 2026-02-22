# v0-listings: Implementation Plan

**Status:** Planning
**Date:** 2026-02-22
**Goal:** A data pipeline that consistently fetches businesses-for-sale, stores them in SQLite, and returns results verified to match the query industry.

---

## Guiding Principle

Prove correctness locally before hardening anything. Every milestone has explicit validation gates. We do not move to the next milestone until the current one passes its checks. The central concern is **query fidelity**: when a user asks for HVAC businesses, they get HVAC businesses — not random listings that happen to contain the word "HVAC" somewhere.

---

## Milestone 0: BizBuySell Reconnaissance (no code)

Before writing a single line of provider code, we need ground truth on how BizBuySell actually works. This milestone is investigation only. All findings get documented in a `discovery.md` scratch file.

### ✅ 0.1 URL structure — CONFIRMED

Discovered via manual browser inspection and URL analysis (2026-02-22):

- **Standard `requests.get()`**: Returns 200 but no `__NEXT_DATA__` — server-renders a shell only.
- **Standard headless Selenium**: Returns "Access Denied" (315 bytes) — blocked by **Akamai** bot detection. Reference: `errors.edgesuite.net`. This is NOT Cloudflare.
- **`undetected-chromedriver` required**: Must bypass Akamai to get real page content. Add to `pyproject.toml`.
- **Category URLs confirmed**: BizBuySell uses 18 broad top-level categories, NOT per-industry slugs.
  - `https://www.bizbuysell.com/{category-slug}-businesses-for-sale/` (no state)
  - `https://www.bizbuysell.com/{state}/{category-slug}-businesses-for-sale/` (with state)
  - Example: `https://www.bizbuysell.com/california/agriculture-businesses-for-sale/`
  - Example: `https://www.bizbuysell.com/building-and-construction-businesses-for-sale/`
- **State** is a URL path segment (e.g., `california`, `texas`), NOT a query param.

**Confirmed BizBuySell category list and slugs:**

| Category | URL Slug |
|---|---|
| Agriculture | `agriculture` |
| Automotive & Boat | `automotive-boat` *(verify exact slug)* |
| Beauty & Personal Care | `beauty-personal-care` *(verify)* |
| Building & Construction | `building-and-construction` |
| Communication & Media | `communication-media` *(verify)* |
| Education & Children | `education-children` *(verify)* |
| Entertainment & Recreation | `entertainment-recreation` *(verify)* |
| Financial Services | `financial-services` *(verify)* |
| Health Care & Fitness | `health-care-fitness` *(verify)* |
| Manufacturing | `manufacturing` *(verify)* |
| Non-Classifiable Establishments | `non-classifiable-establishments` *(verify)* |
| Online & Technology | `online-technology` *(verify)* |
| Pet Services | `pet-services` *(verify)* |
| Restaurants & Food | `restaurants-food` *(verify)* |
| Retail | `retail` |
| Service Businesses | `service-businesses` *(verify)* |
| Transportation & Storage | `transportation-storage` *(verify)* |
| Travel | `travel` *(verify)* |
| Wholesale & Distributors | `wholesale-distributors` *(verify)* |

**Industry → BizBuySell category mapping (our target industries):**

| Our industry | BizBuySell category | Post-filter keywords |
|---|---|---|
| HVAC | `building-and-construction` | hvac, air conditioning, heating, cooling |
| Plumbing | `building-and-construction` | plumbing, plumber, pipe, drain |
| Electrical | `building-and-construction` | electrical, electrician, wiring |
| Car Wash | `service-businesses` | car wash, auto wash, detail |
| Landscaping | `service-businesses` | landscaping, lawn care, tree service |
| Cleaning | `service-businesses` | cleaning, janitorial, maid |
| Pest Control | `service-businesses` | pest control, exterminator, termite |
| Pool Service | `service-businesses` | pool, swimming pool, spa |
| Auto Repair | `automotive-boat` | auto repair, mechanic, body shop |
| Restaurant | `restaurants-food` | *(entire category is relevant)* |

**Important implication:** Multiple industries share the same BizBuySell category (e.g., HVAC + Plumbing + Electrical all → `building-and-construction`). A single scrape of that category URL returns all three. The validation layer (Milestone 5) handles filtering results to the queried industry.

### ✅ 0.2 The `q=` filter encoding — CONFIRMED (V2 feature)

The `q=` param is base64(`lt=ID1,ID2,...`) where `lt` = "listing type" (internal BizBuySell filter IDs). Examples:
- State-only: `q=bHQ9MzAsODA%3D` → base64 decode → `lt=30,80`
- State + category: `q=bHQ9MzAsNDAsODA%3D` → `lt=30,40,80`

The category is in the URL slug; `q=` encodes additional filter checkboxes (e.g., "broker-represented", "asset sale"). We do **not** need to generate `q=` for V0 — it can be omitted. Document for V2 (price range filters, listing type filters):

```python
import base64
def encode_listing_type_filter(ids: list[int]) -> str:
    raw = "lt=" + ",".join(str(i) for i in sorted(ids))
    return base64.b64encode(raw.encode()).decode()
```

### 0.3 Map `__NEXT_DATA__` JSON structure (requires `undetected-chromedriver`)

**Status: Blocked until undetected-chromedriver is installed (M4 prerequisite)**

- [ ] Install `undetected-chromedriver`: `pip install undetected-chromedriver`
- [ ] Run `scripts/recon_bizbuysell.py` with uc driver against `https://www.bizbuysell.com/building-and-construction-businesses-for-sale/`
- [ ] Confirm `__NEXT_DATA__` is present in page source
- [ ] Print top-level JSON keys, navigate `props.pageProps`, find listings array path
- [ ] Print all field names on the first listing object
- [ ] Document: exact paths to `listings array`, `asking_price`, `revenue`, `cash_flow`, `listing_id`, `url`, `location`, `days_on_market`, `broker`, `total_count`, `page_size`
- [ ] Test with state filter: `/california/building-and-construction-businesses-for-sale/` — confirm `__NEXT_DATA__` still present and locations are in California
- [ ] Verify exact state slug format: `california`, `texas`, `florida` (all lowercase, full state name)
- [ ] Write all findings to `docs/feature/v0-listings/discovery.md`

### 0.4 Verify category slug formats

- [ ] Using `undetected-chromedriver`, load the 5 slugs marked *(verify)* above and confirm each returns listings (check HTTP status and result count)
- [ ] Correct any slugs that 404 or redirect
- [ ] Update the category table above with confirmed slugs

**Gate:** Do not start Milestone 4 until `discovery.md` documents the exact `__NEXT_DATA__` JSON paths. Milestones 1, 2, 3 can proceed in parallel.

---

## Milestone 1: Listing Domain Model

### 1.1 Create `Listing` dataclass

**File:** `scout/scout/domain/listing.py`

- [ ] Define `@dataclass class Listing` with these fields:
  - `source: str` — "bizbuysell", "bizquest", etc.
  - `source_id: str` — the source's internal listing ID (extracted from URL or JSON id field)
  - `url: str` — full URL to the listing page
  - `name: str` — business name
  - `industry: str` — from our search query (e.g., "HVAC")
  - `location: str` — "Austin, TX" (raw from source)
  - `state: str = ""` — extracted 2-letter state code ("TX")
  - `description: str = ""`
  - `asking_price: Optional[float] = None`
  - `annual_revenue: Optional[float] = None`
  - `cash_flow: Optional[float] = None` — SDE or EBITDA
  - `asking_multiple: Optional[float] = None` — computed: asking_price / cash_flow
  - `days_on_market: Optional[int] = None`
  - `broker: str = ""`
  - `listed_at: Optional[str] = None` — ISO date string from source
  - `fetched_at: str = ""` — ISO datetime when we scraped it
- [ ] Add `@property def id(self) -> str: return f"{self.source}:{self.source_id}"`
- [ ] Add `@classmethod def from_dict(cls, d: Dict[str, Any]) -> "Listing"` with safe type coercion (never crash on bad input)
- [ ] Add `def to_dict(self) -> Dict[str, Any]` (all fields, None values included)
- [ ] Add private helpers `_to_float(v) -> Optional[float]` and `_to_int(v) -> Optional[int]` (module-level)

### 1.2 Unit tests for Listing

**File:** `tests/data_sources/marketplaces/test_listing.py`

- [ ] `test_from_dict_full` — all fields present → all fields populated correctly
- [ ] `test_from_dict_missing_fields` — only required fields present → optional fields are None/""
- [ ] `test_from_dict_bad_types` — numeric fields contain strings ("not a number") → coerces to None, does not crash
- [ ] `test_roundtrip` — `Listing.from_dict(l.to_dict()) == l`
- [ ] `test_id_property` — `Listing(source="bizbuysell", source_id="abc123", ...).id == "bizbuysell:abc123"`
- [ ] `test_to_dict_contains_all_fields` — every field name in the dataclass appears in `to_dict()` output

**Gate:** `pytest tests/data_sources/marketplaces/test_listing.py` — all pass.

---

## Milestone 2: ListingStore (SQLite)

### 2.1 Create `ListingStore`

**File:** `data_sources/marketplaces/store.py`

- [ ] `class ListingStore` with `__init__(self, db_path: str = "outputs/listings.db")`
- [ ] Opens SQLite connection; creates tables if not exist on init

### 2.2 Schema creation

- [ ] Implement `_create_tables(conn)` with:
  ```sql
  CREATE TABLE IF NOT EXISTS listings (
      id TEXT PRIMARY KEY,
      source TEXT NOT NULL,
      source_id TEXT NOT NULL,
      name TEXT NOT NULL,
      industry TEXT,
      location TEXT,
      state TEXT,
      asking_price REAL,
      annual_revenue REAL,
      cash_flow REAL,
      asking_multiple REAL,
      days_on_market INTEGER,
      broker TEXT,
      url TEXT,
      description TEXT,
      listed_at TEXT,
      fetched_at TEXT NOT NULL
  );
  CREATE INDEX IF NOT EXISTS idx_industry_state ON listings(industry, state);
  CREATE INDEX IF NOT EXISTS idx_asking_price ON listings(asking_price);
  CREATE INDEX IF NOT EXISTS idx_cash_flow ON listings(cash_flow);
  CREATE INDEX IF NOT EXISTS idx_fetched_at ON listings(fetched_at);

  CREATE TABLE IF NOT EXISTS scrape_log (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      source TEXT NOT NULL,
      industry TEXT NOT NULL,
      location TEXT NOT NULL,
      scraped_at TEXT NOT NULL,
      listing_count INTEGER,
      status TEXT,
      precision_pct REAL,
      error_msg TEXT
  );
  ```

### 2.3 `upsert()` method

- [ ] Signature: `def upsert(self, listings: List[Listing]) -> int`
- [ ] Uses `INSERT OR REPLACE INTO listings VALUES (...)` (deduplicates by `id`)
- [ ] Wraps batch in a single transaction for atomicity
- [ ] Returns count of rows actually written
- [ ] Handles empty list (returns 0, no-op)

### 2.4 `search()` method

- [ ] Signature: `def search(self, industry: str = "", location: str = "", state: str = "", min_price: Optional[float] = None, max_price: Optional[float] = None, min_revenue: Optional[float] = None, min_cash_flow: Optional[float] = None, max_multiple: Optional[float] = None, source: Optional[str] = None, limit: int = 100, offset: int = 0) -> List[Listing]`
- [ ] `industry` filter: `WHERE LOWER(industry) LIKE LOWER('%' || ? || '%')` — partial match
- [ ] `location` filter: `WHERE LOWER(location) LIKE LOWER('%' || ? || '%')` OR `WHERE state = ?` — use whichever is more specific
- [ ] `min_price` / `max_price`: `WHERE asking_price BETWEEN ? AND ?` (only applies to rows where asking_price IS NOT NULL)
- [ ] `min_cash_flow`: `WHERE cash_flow >= ?`
- [ ] `max_multiple`: `WHERE asking_multiple <= ?`
- [ ] `source`: `WHERE source = ?`
- [ ] `LIMIT ? OFFSET ?` for pagination
- [ ] Returns `[Listing.from_dict(dict(row)) for row in rows]`

### 2.5 Scrape log methods

- [ ] `def log_scrape(self, source, industry, location, count, status, precision_pct=None, error_msg=None)` — inserts one row
- [ ] `def last_scraped(self, source, industry, location) -> Optional[str]` — returns `scraped_at` ISO string of most recent successful scrape, or None
- [ ] `def is_stale(self, source, industry, location, max_age_hours=24) -> bool` — compares last_scraped to now; True if never scraped or older than threshold
- [ ] `def count(self, industry="", location="") -> int` — total matching rows in listings table

### 2.6 Unit tests for ListingStore

**File:** `tests/data_sources/marketplaces/test_store.py`
All tests use `ListingStore(":memory:")` (in-memory SQLite — no disk I/O, no cleanup needed)

- [ ] `test_upsert_basic` — insert 5 listings, `count()` returns 5
- [ ] `test_upsert_deduplication` — upsert same listing twice → still 1 record
- [ ] `test_upsert_update` — upsert listing, then upsert same id with updated price → new price wins
- [ ] `test_search_by_industry` — 3 HVAC + 2 plumbing listings; search "HVAC" returns 3
- [ ] `test_search_by_location` — 2 Texas + 3 California; search location="Texas" returns 2
- [ ] `test_search_by_price_range` — 5 listings at $100K, $300K, $500K, $800K, $1.2M; filter $200K–$600K returns 2
- [ ] `test_search_by_cash_flow` — min_cash_flow=100000 filters correctly
- [ ] `test_search_none_filters` — search with no filters returns all rows up to limit
- [ ] `test_search_no_results` — search for industry that doesn't exist returns []
- [ ] `test_search_returns_listings` — result type is `List[Listing]`, not list of dicts
- [ ] `test_scrape_log_roundtrip` — log_scrape then last_scraped returns correct timestamp
- [ ] `test_is_stale_never_scraped` — returns True when no log entry exists
- [ ] `test_is_stale_fresh` — returns False when scraped 1 hour ago with 24h threshold
- [ ] `test_is_stale_expired` — returns True when scraped 25 hours ago with 24h threshold

**Gate:** `pytest tests/data_sources/marketplaces/test_store.py` — all pass, no disk files created.

---

## Milestone 3: MarketplaceProvider Interface

**File:** `data_sources/marketplaces/base.py`

### 3.1 ListingQuery dataclass

- [ ] `@dataclass class ListingQuery` with: `industry: str`, `location: str = ""`, `max_results: int = 50`

### 3.2 MarketplaceProvider ABC

- [ ] `class MarketplaceProvider(Tool, ABC)` with `SOURCE_ID: str = ""`, `CACHE_TTL_DAYS: int = 7`
- [ ] Abstract method: `def _fetch(self, query: ListingQuery) -> List[Listing]`
- [ ] Template method: `def search(self, query: ListingQuery, use_cache: bool = True) -> List[Listing]` that: checks file cache → calls `_fetch()` → computes `asking_multiple` where None → sets `fetched_at` → saves to file cache → returns
- [ ] `def _cache_key(self, query) -> str` — `"{SOURCE_ID}_{industry}_{location}_{max_results}".lower()`

### 3.3 `parse_money()` static method

- [ ] `@staticmethod def parse_money(text: str) -> Optional[float]`
- [ ] Handles: `$1.2M`, `$450K`, `$1,200,000`, `$450,000`, `$1.5B`, `1200000` (no symbol)
- [ ] Returns None for: `""`, `None`, `"Not Disclosed"`, `"N/A"`, `"Undisclosed"`, any non-numeric string

### 3.4 Unit tests for parse_money

**File:** `tests/data_sources/marketplaces/test_base.py`

- [ ] `"$1.2M"` → `1_200_000.0`
- [ ] `"$450K"` → `450_000.0`
- [ ] `"$1,200,000"` → `1_200_000.0`
- [ ] `"$450,000"` → `450_000.0`
- [ ] `"$1.5B"` → `1_500_000_000.0`
- [ ] `"1200000"` → `1_200_000.0`
- [ ] `"Not Disclosed"` → `None`
- [ ] `"N/A"` → `None`
- [ ] `""` → `None`
- [ ] `None` → `None`
- [ ] `"$0"` → `0.0` (zero price is valid — don't discard)
- [ ] `"$-500K"` → None or negative (document behavior)

**Gate:** `pytest tests/data_sources/marketplaces/` — all unit tests pass.

---

## Milestone 4: BizBuySell Provider

**File:** `data_sources/marketplaces/bizbuysell.py`
This is the most critical milestone. Each sub-section must be validated independently before proceeding.

### 4.1 Category map (uses BizBuySell's exact language)

BizBuySell has 18 fixed categories. For V0, callers use BizBuySell's category slugs directly as the `industry` param. A future V2 LLM layer will translate natural language queries → category slugs (trivial classification problem: fixed 18-option output space).

The exact slugs must be confirmed by Milestone 0.3–0.4 reconnaissance. The map below uses slugs confirmed so far; *(verify)* items are filled in after M0 recon:

- [ ] Define `BIZBUYSELL_CATEGORIES: Dict[str, str]` — maps slug → display name (source of truth from live site):
  ```python
  BIZBUYSELL_CATEGORIES = {
      "agriculture": "Agriculture",
      "automotive-boat": "Automotive & Boat",          # *(verify slug)*
      "beauty-personal-care": "Beauty & Personal Care", # *(verify slug)*
      "building-and-construction": "Building & Construction",
      "communication-media": "Communication & Media",   # *(verify slug)*
      "education-children": "Education & Children",     # *(verify slug)*
      "entertainment-recreation": "Entertainment & Recreation",  # *(verify slug)*
      "financial-services": "Financial Services",       # *(verify slug)*
      "health-care-fitness": "Health Care & Fitness",   # *(verify slug)*
      "manufacturing": "Manufacturing",                  # *(verify slug)*
      "online-technology": "Online & Technology",        # *(verify slug)*
      "pet-services": "Pet Services",                    # *(verify slug)*
      "restaurants-food": "Restaurants & Food",          # *(verify slug)*
      "retail": "Retail",
      "service-businesses": "Service Businesses",        # *(verify slug)*
      "transportation-storage": "Transportation & Storage",  # *(verify slug)*
      "travel": "Travel",                                # *(verify slug)*
      "wholesale-distributors": "Wholesale & Distributors",  # *(verify slug)*
  }
  ```
- [ ] All *(verify)* slugs confirmed and corrected after M0 reconnaissance
- [ ] Implement `is_valid_category(slug: str) -> bool` — returns True if slug is in `BIZBUYSELL_CATEGORIES`
- [ ] Implement `list_categories() -> List[str]` — returns sorted list of valid slugs (for help/docs)
- [ ] Unit test: `is_valid_category("building-and-construction")` → True
- [ ] Unit test: `is_valid_category("hvac")` → False (not a BizBuySell category)
- [ ] Unit test: `is_valid_category("unknown")` → False
- [ ] **Note:** Natural language → category mapping (e.g., "HVAC" → "building-and-construction") is a V2 feature implemented as a single Claude API call with the 18 categories as the output constraint.

### 4.2 URL builder

- [ ] Define `STATE_SLUGS: Dict[str, str]` — maps state names/abbreviations to lowercase URL slugs (e.g., `"texas": "texas"`, `"tx": "texas"`, `"california": "california"`, `"ca": "california"` — all 50 states)
- [ ] Implement `_to_state_slug(location: str) -> Optional[str]` — parses "Texas", "TX", "Austin, TX" → `"texas"`, returns None if unrecognized
- [ ] Implement `_build_url(query: ListingQuery) -> str`:
  - Category + state: `https://www.bizbuysell.com/{state-slug}/{category-slug}-businesses-for-sale/`
  - Category, no state: `https://www.bizbuysell.com/{category-slug}-businesses-for-sale/`
  - No category (fallback): `https://www.bizbuysell.com/businesses-for-sale/?q={industry}` *(may hit Akamai)*
  - **No `q=` listing-type param** — not needed for V0
- [ ] Unit test: `_build_url(ListingQuery("HVAC", "Texas"))` → `"https://www.bizbuysell.com/texas/building-and-construction-businesses-for-sale/"`
- [ ] Unit test: `_build_url(ListingQuery("HVAC", "CA"))` → `"https://www.bizbuysell.com/california/building-and-construction-businesses-for-sale/"`
- [ ] Unit test: `_build_url(ListingQuery("HVAC"))` (no location) → `"https://www.bizbuysell.com/building-and-construction-businesses-for-sale/"`
- [ ] Unit test: `_build_url(ListingQuery("Unknown XYZ", "Texas"))` → keyword fallback URL

### 4.3 Page loader (uses `undetected-chromedriver`)

Standard headless Selenium is blocked by Akamai (confirmed in M0 — returns "Access Denied", 315 bytes). `undetected-chromedriver` patches Chrome to evade Akamai detection.

- [ ] Implement `_load_page(url: str) -> str` (returns `driver.page_source`)
- [ ] Uses `undetected_chromedriver` (import as `uc`):
  ```python
  import undetected_chromedriver as uc
  opts = uc.ChromeOptions()
  opts.add_argument("--headless=new")
  opts.add_argument("--window-size=1920,1080")
  opts.add_argument("--no-sandbox")
  opts.add_argument("--disable-dev-shm-usage")
  driver = uc.Chrome(options=opts, use_subprocess=True)
  ```
- [ ] Waits for `document.readyState == "complete"` via `WebDriverWait`
- [ ] Additional `time.sleep(3)` after readyState for React hydration
- [ ] Retries once with 5s delay if page source is < 1000 bytes (indicates block)
- [ ] Logs WARNING if "Access Denied" in page source — Akamai still blocking
- [ ] `driver.quit()` in finally block — never leave dangling Chrome processes
- [ ] Logs URL and final page source length at INFO level

### 4.4 `__NEXT_DATA__` extractor

- [ ] Implement `_extract_next_data(page_source: str) -> Optional[Dict]`
- [ ] Uses BeautifulSoup: `soup.find("script", {"id": "__NEXT_DATA__"})`
- [ ] Returns `json.loads(script.string)` or `None` if tag not found
- [ ] Returns `None` on any `json.JSONDecodeError` (logs WARNING)

- [ ] Implement `_find_listings_array(data: Dict) -> List[Dict]`
- [ ] Tries these paths in order (based on Milestone 0 discovery — put the correct one first):
  1. `data["props"]["pageProps"]["listings"]`
  2. `data["props"]["pageProps"]["initialData"]["listings"]`
  3. `data["props"]["pageProps"]["businessListings"]`
  4. `data["props"]["pageProps"]["results"]`
  5. `data["props"]["pageProps"]["initialState"]["listings"]`
- [ ] Returns `[]` if none found
- [ ] Logs the path that succeeded at DEBUG level
- [ ] Logs WARNING if all paths fail (so we know to investigate a structure change)

- [ ] **Validation checkpoint:** After extracting, log `f"__NEXT_DATA__: found {len(listings)} raw listings"` at INFO level — must be > 0 for a live test

### 4.5 Listing field parser

- [ ] Implement `_parse_listing(raw: Dict, query: ListingQuery) -> Optional[Listing]`

**Required fields (return None if missing):**
- [ ] Extract `name`: try `raw["businessName"]`, `raw["title"]`, `raw["name"]` in that order
- [ ] Extract `source_id`: try `raw["listingId"]`, `raw["id"]`, extract from URL slug; return None if none found
- [ ] Extract `url`: try `raw["detailUrl"]`, `raw["url"]`; prepend `https://www.bizbuysell.com` if relative

**Financial fields (None if missing or unparseable):**
- [ ] Extract `asking_price`: try `raw["askingPrice"]`, `raw["price"]`, `raw["listPrice"]`; pass through `parse_money()`
- [ ] Extract `annual_revenue`: try `raw["grossRevenue"]`, `raw["revenue"]`, `raw["annualRevenue"]`; pass through `parse_money()`
- [ ] Extract `cash_flow`: try `raw["cashFlow"]`, `raw["sde"]`, `raw["ebitda"]`, `raw["netIncome"]`; pass through `parse_money()`

**Location fields:**
- [ ] Extract `location`: try `raw["location"]`, `raw["city"]`, build from `raw["city"] + ", " + raw["state"]`
- [ ] If location is a dict: `f'{raw["location"]["city"]}, {raw["location"]["state"]}'`
- [ ] Extract `state`: parse 2-letter code from location string using regex `r'\b([A-Z]{2})\b'` or dict field

**Other fields:**
- [ ] Extract `days_on_market`: try `raw["daysListed"]`, `raw["daysOnMarket"]`; convert to int
- [ ] Extract `broker`: try `raw["brokerName"]`, `raw["sellerName"]`, `raw["contactName"]`
- [ ] Extract `description`: try `raw["description"]`, `raw["briefDescription"]`, `raw["summary"]`; truncate to 500 chars
- [ ] Extract `listed_at`: try `raw["listedDate"]`, `raw["datePosted"]`, `raw["publishedAt"]`

**Computed field:**
- [ ] `asking_multiple = asking_price / cash_flow` if both are > 0, else None
- [ ] `industry = query.industry`
- [ ] `source = "bizbuysell"`
- [ ] `fetched_at = datetime.now().isoformat()`

**Parse correctness assertion (not a hard filter — just log):**
- [ ] After building the Listing, log at DEBUG: name, asking_price, cash_flow, location
- [ ] If asking_price is None AND annual_revenue is None AND cash_flow is None: log WARNING `"listing '{name}' has no financial data"` (note: this is common and expected for some listings)

### 4.6 HTML fallback extractor

- [ ] Implement `_extract_from_html(page_source: str, query: ListingQuery) -> List[Listing]`
- [ ] Called only if `_find_listings_array()` returns `[]`
- [ ] Log INFO: "Falling back to HTML extraction"
- [ ] Try card selectors in order: `[data-listing-id]`, `.listing-card`, `[class*='BusinessCard']`, `[class*='listing-item']`
- [ ] For each card: extract name (h2/h3), URL (first `<a href>`), asking price (labeled text search), location
- [ ] Implement `_find_labeled_value(text: str, labels: List[str]) -> str` — regex `{label}[:\s]+(\$[\d,.]+[KMB]?)`
- [ ] Log WARNING if HTML fallback also returns 0: "Both extraction methods failed — BizBuySell structure may have changed"
- [ ] Unit test: pass pre-saved HTML fixture → returns at least 1 listing

### 4.7 Core `_fetch()` method

- [ ] Implements `_fetch(self, query: ListingQuery) -> List[Listing]`
- [ ] Calls `_build_url()` → logs URL
- [ ] Calls `_load_page()` → gets `page_source`
- [ ] Calls `_extract_next_data()` → then `_find_listings_array()`
- [ ] If empty → calls `_extract_from_html()`
- [ ] Maps each raw item through `_parse_listing()` — collect non-None results
- [ ] Returns `listings[:query.max_results]`
- [ ] Entire method wrapped in try/except; logs exception and returns `[]` on failure

### 4.8 Pagination

- [ ] Find total results count in `__NEXT_DATA__` (field name from Milestone 0, e.g., `totalCount` or `pagination.total`)
- [ ] Find page size (e.g., 20 listings per page)
- [ ] Implement `_fetch_all_pages(query: ListingQuery) -> List[Listing]`
- [ ] Iterates pages by adding `&pg={n}` (or correct param from Milestone 0) to URL
- [ ] Stops when: `max_results` reached, OR no more pages, OR page returns 0 new listings
- [ ] Rate limits between page requests: `time.sleep(random.uniform(1.0, 2.0))`
- [ ] Logs: `f"Page {n}: {len(page_listings)} listings (total so far: {total})"` at INFO

**Gate (Milestone 4 exit criteria):**
- [ ] `python -c "from data_sources.marketplaces.bizbuysell import BizBuySellProvider; p = BizBuySellProvider(); r = p._fetch(ListingQuery('HVAC', 'Texas', 20)); print(len(r), r[0])"` prints at least 1 listing
- [ ] The first listing has `name`, `url`, and `source_id` populated
- [ ] The URL is a valid BizBuySell listing URL
- [ ] Manually visit 3 of the returned URLs and verify they are HVAC businesses

---

## Milestone 5: Result Validation (Paranoid Correctness Checks)

This milestone adds a layer specifically to answer: **"Are these results actually what we asked for?"**

**File:** `data_sources/marketplaces/validation.py`

### 5.1 Industry keyword map

- [ ] Define `INDUSTRY_KEYWORDS: Dict[str, List[str]]` with exhaustive synonyms:
  ```python
  INDUSTRY_KEYWORDS = {
      "hvac": ["hvac", "air conditioning", "a/c", "heating", "cooling", "refrigeration",
               "ac repair", "ductwork", "furnace", "heat pump", "hvac/r", "ventilation",
               "air handler", "chiller"],
      "plumbing": ["plumbing", "plumber", "pipe", "drain", "sewer", "water heater",
                   "septic", "backflow"],
      "car wash": ["car wash", "carwash", "auto wash", "vehicle wash", "detail",
                   "hand wash", "self-serve wash"],
      "landscaping": ["landscaping", "lawn care", "lawn mowing", "lawn service",
                      "tree service", "groundskeeping", "irrigation", "sod", "mulch"],
      "cleaning": ["cleaning", "janitorial", "maid service", "housekeeping",
                   "sanitation", "commercial cleaning", "carpet cleaning", "pressure wash"],
      "restaurant": ["restaurant", "café", "cafe", "diner", "eatery", "food service",
                     "bar and grill", "pizzeria", "bistro", "deli"],
      "auto repair": ["auto repair", "mechanic", "automotive", "car repair", "body shop",
                      "transmission", "tire shop", "oil change"],
      "electrical": ["electrical", "electrician", "wiring", "lighting contractor",
                     "low voltage", "panel upgrade"],
      "pest control": ["pest control", "exterminator", "termite", "rodent control",
                       "fumigation", "insect control"],
  }
  ```
- [ ] Keys are lowercase; values are all lowercase
- [ ] Add more industries as we encounter them during testing

### 5.2 Relevance checker for a single listing

- [ ] Implement `is_relevant(listing: Listing, query_industry: str) -> Tuple[bool, str]`
- [ ] Returns `(True, "name_match")` if any keyword appears in `listing.name.lower()`
- [ ] Returns `(True, "description_match")` if any keyword appears in `listing.description.lower()` (fallback)
- [ ] Returns `(True, "category_match")` if any keyword appears in `listing.industry.lower()`
- [ ] Returns `(False, "no_match")` if none of the above
- [ ] Returns `(True, "no_map")` with a logged WARNING if the query_industry has no entry in `INDUSTRY_KEYWORDS` — we can't check what we don't know

### 5.3 Batch validation

- [ ] Implement `@dataclass class ValidationReport` with: `query_industry`, `total`, `relevant`, `irrelevant`, `precision_pct`, `irrelevant_listings: List[str]` (names), `warnings: List[str]`
- [ ] Implement `validate_batch(listings: List[Listing], query_industry: str) -> ValidationReport`
- [ ] Runs `is_relevant()` on each listing
- [ ] `precision_pct = relevant / total * 100` (or 0 if total == 0)
- [ ] Collects names of irrelevant listings for inspection

### 5.4 Financial sanity checks

- [ ] Implement `check_listing_financials(listing: Listing) -> List[str]` — returns list of warning strings
- [ ] `asking_price is not None and asking_price <= 0` → `"asking_price is zero or negative"`
- [ ] `asking_price is not None and asking_price > 50_000_000` → `"price > $50M — may not be SMB"`
- [ ] `cash_flow is not None and asking_price is not None and cash_flow > asking_price` → `"cash flow exceeds asking price — verify data"`
- [ ] `annual_revenue is not None and cash_flow is not None and cash_flow > annual_revenue` → `"cash flow exceeds revenue — verify data"`
- [ ] `asking_multiple is not None and asking_multiple < 0.5` → `"multiple < 0.5x — unusually low"`
- [ ] `asking_multiple is not None and asking_multiple > 10` → `"multiple > 10x — unusually high for SMB"`
- [ ] **These are logged warnings only — do not filter listings out**

### 5.5 Validation integration in FetchPipeline

- [ ] After each provider `_fetch()` call, run `validate_batch()` on the results
- [ ] Log the full `ValidationReport` at INFO level
- [ ] If `precision_pct < 70` and `total >= 5`: log WARNING with sample of irrelevant listing names
- [ ] If `precision_pct < 50` and `total >= 5`: log ERROR — "scraper may be returning wrong industry; investigate"
- [ ] Store `precision_pct` in `scrape_log`

### 5.6 Unit tests for validation

**File:** `tests/data_sources/marketplaces/test_validation.py`

- [ ] `test_is_relevant_name_match` — listing with "HVAC" in name → relevant
- [ ] `test_is_relevant_description_match` — listing with "air conditioning" in description → relevant
- [ ] `test_is_relevant_no_match` — listing with "Italian Restaurant" in name, searching "HVAC" → irrelevant
- [ ] `test_is_relevant_no_keyword_map` — searching "Exotic Industry" → returns (True, "no_map") with warning
- [ ] `test_validate_batch_all_relevant` — 5 HVAC listings → precision 100%
- [ ] `test_validate_batch_mixed` — 3 HVAC + 2 random → precision 60%, irrelevant list has 2 names
- [ ] `test_validate_batch_empty` — empty list → precision 0%, no crash
- [ ] `test_financial_sanity_zero_price` — listing with asking_price=0 → warning returned
- [ ] `test_financial_sanity_cf_exceeds_revenue` — cash_flow > revenue → warning returned
- [ ] `test_financial_sanity_clean` — reasonable listing → empty warning list

**Gate:** `pytest tests/data_sources/marketplaces/test_validation.py` — all pass.

---

## Milestone 6: FetchPipeline

**File:** `data_sources/marketplaces/pipeline.py`

### 6.1 Core pipeline

- [ ] `class FetchPipeline` with `__init__(self, store: Optional[ListingStore] = None, providers: Optional[List[MarketplaceProvider]] = None)`
- [ ] Defaults: `store = ListingStore()`, `providers = [BizBuySellProvider()]`
- [ ] Implement `run(self, industry: str, location: str = "", max_results: int = 50, use_cache: bool = True, force_refresh: bool = False) -> List[Listing]`

### 6.2 `run()` logic

- [ ] Check `store.is_stale(source, industry, location)` for each provider
- [ ] If not stale and not `force_refresh`: skip scraping, go straight to `store.search()`
- [ ] If stale or `force_refresh`: run provider scraping
- [ ] For each provider: catch exceptions individually — log the exception, continue to next provider
- [ ] After each provider fetch: run validation via `validate_batch()`, log report
- [ ] `store.upsert(new_listings)` for each provider's results
- [ ] `store.log_scrape(source, industry, location, count, status, precision_pct)`
- [ ] Return `store.search(industry=industry, location=location, limit=max_results)`

### 6.3 Unit tests for FetchPipeline

**File:** `tests/data_sources/marketplaces/test_pipeline.py`

- [ ] `test_run_with_mock_provider` — mock provider returns 5 listings → pipeline stores them and returns them
- [ ] `test_run_skips_when_fresh` — mock scrape_log shows recent scrape → provider not called
- [ ] `test_run_on_provider_exception` — provider raises exception → pipeline logs error, returns [] (not crash)
- [ ] `test_run_logs_scrape` — after run, `store.last_scraped()` returns a timestamp

**Gate:** `pytest tests/data_sources/marketplaces/` — all unit tests pass (no live network calls).

---

## Milestone 7: End-to-End Local Validation

These steps prove the pipeline works end-to-end against real BizBuySell data. Run from `scout/` directory.

### 7.1 Live scrape test (requires network)

- [ ] Run: `SCOUT_LIVE_TESTS=1 pytest tests/data_sources/marketplaces/test_bizbuysell_live.py -v -s`

**File:** `tests/data_sources/marketplaces/test_bizbuysell_live.py`

- [ ] `test_live_hvac_texas` — BizBuySellProvider fetches HVAC Texas → at least 5 results, precision ≥ 70%
- [ ] `test_live_car_wash_california` — fetches Car Wash California → at least 3 results
- [ ] `test_live_result_fields` — at least 80% of results have non-empty `name`, `url`, `source_id`
- [ ] `test_live_financial_coverage` — at least 30% of results have `asking_price` set (not None)
- [ ] `test_live_urls_valid` — all `url` fields start with `https://www.bizbuysell.com`
- [ ] `test_live_no_wrong_industry` — none of the HVAC results have names that are obviously restaurants, retailers, etc. (manual inspection prompt included)

### 7.2 Validation script

**File:** `scripts/validate_listings.py`

- [ ] Create a script that runs the full pipeline and prints a human-readable report
- [ ] Tests these 3 queries: `("HVAC", "Texas")`, `("Car Wash", "California")`, `("Plumbing", "Florida")`
- [ ] For each query, prints:
  ```
  === HVAC in Texas ===
  Total listings found: 42
  Precision: 88.1% (37 relevant, 5 flagged)
  Listings with asking_price: 31 (73.8%)
  Listings with cash_flow: 24 (57.1%)

  Sample (first 5):
    1. Smith's HVAC & AC Services — Austin, TX — Ask: $485,000 — CF: $145,000 (3.3x)
    2. Comfort Air Systems Inc — Houston, TX — Ask: $1.2M — CF: $380,000 (3.2x)
    ...

  Flagged as potentially irrelevant:
    - "North Texas General Contracting" (no HVAC keywords in name/description)
  ```
- [ ] Exits with code 1 if any query returns 0 results
- [ ] Exits with code 1 if any query has precision < 60%

### 7.3 SQLite verification queries

After running the pipeline, confirm the database looks correct:

- [ ] Run and verify: `SELECT COUNT(*) FROM listings WHERE LOWER(industry) LIKE '%hvac%'` — count > 0
- [ ] Run and verify: `SELECT MIN(asking_price), MAX(asking_price), AVG(asking_price) FROM listings WHERE LOWER(industry) LIKE '%hvac%' AND asking_price IS NOT NULL` — values look like SMB prices ($50K–$10M range)
- [ ] Run and verify: `SELECT COUNT(*) FROM scrape_log` — at least 1 row
- [ ] Run and verify: `SELECT DISTINCT source FROM listings` — shows "bizbuysell"
- [ ] Run and verify: `SELECT COUNT(*) FROM listings WHERE asking_price IS NULL` — note % with no price (expected, some listings don't disclose)
- [ ] Manually inspect 5–10 random rows: `SELECT name, location, asking_price, cash_flow, url FROM listings ORDER BY RANDOM() LIMIT 10`

### 7.4 Manual spot-check protocol

After the automated checks, do a manual review:

- [ ] Open 5 listing URLs from the DB in a browser — are they real HVAC businesses?
- [ ] Check that the `asking_price` in our DB matches the price shown on the listing page
- [ ] Check that the `cash_flow` / SDE in our DB matches the listing page
- [ ] If any prices don't match: investigate field name mapping in `_parse_listing()` and fix

**Gate (Milestone 7 exit criteria — the pipeline is working):**
- [ ] `validate_listings.py` exits with code 0
- [ ] All three test industries return > 5 listings with precision ≥ 70%
- [ ] Manual spot-check confirms listing URLs are real and prices match

---

## File Manifest

| File | Status | Notes |
|---|---|---|
| `scout/scout/domain/listing.py` | Create | Domain model |
| `data_sources/marketplaces/base.py` | Create | Provider interface |
| `data_sources/marketplaces/store.py` | Create | SQLite store |
| `data_sources/marketplaces/pipeline.py` | Create | FetchPipeline |
| `data_sources/marketplaces/bizbuysell.py` | Rewrite | Full rewrite using __NEXT_DATA__ |
| `data_sources/marketplaces/validation.py` | Create | Relevance + sanity checks |
| `scout/scout/adapters/bizbuysell.py` | Update | Return `List[Listing]` |
| `scout/pyproject.toml` | Update | Add `undetected-chromedriver>=3.5.5` (required — Akamai blocks standard Selenium) |
| `docs/feature/v0-listings/discovery.md` | Create | M0 findings (URL patterns, JSON structure) |
| `scripts/validate_listings.py` | Create | E2E validation script |
| `tests/data_sources/marketplaces/test_listing.py` | Create | |
| `tests/data_sources/marketplaces/test_store.py` | Create | |
| `tests/data_sources/marketplaces/test_base.py` | Create | parse_money tests |
| `tests/data_sources/marketplaces/test_validation.py` | Create | |
| `tests/data_sources/marketplaces/test_pipeline.py` | Create | |
| `tests/data_sources/marketplaces/test_bizbuysell_live.py` | Create | Live tests (SCOUT_LIVE_TESTS=1) |

---

## Implementation Order

```
M0.1–0.2 ✅ (URL structure confirmed, Akamai identified, q= decoded)
M0.3–0.4 (verify __NEXT_DATA__ with uc + confirm remaining category slugs)
  → M1 (Listing model) + M3 (Provider interface)  [can run in parallel with M0.3–0.4]
    → M2 (ListingStore)
      → M4 (BizBuySell provider — needs M0 complete + M3)
        → M5 (Validation, needs M4)
          → M6 (Pipeline, needs M2 + M4 + M5)
            → M7 (E2E, needs all)
```

---

## What Success Looks Like

The pipeline is done when:

1. `pytest tests/data_sources/marketplaces/ -v` — all unit tests pass (no network)
2. `SCOUT_LIVE_TESTS=1 pytest tests/data_sources/marketplaces/test_bizbuysell_live.py -v` — all live tests pass
3. `python scripts/validate_listings.py` — exits 0, prints results showing 3 industries with 70%+ precision
4. Manual spot-check: 5 random listing URLs opened in browser — all are the correct industry, all prices match DB values
5. `outputs/listings.db` exists and contains real listing data queryable via SQLite
