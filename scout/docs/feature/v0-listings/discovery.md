# BizBuySell Reconnaissance — Discovery

**Date:** 2026-02-22
**Status:** Complete
**Method:** `undetected-chromedriver` 3.5.5, non-headless mode (visible window)

---

## Critical Finding: NOT a Next.js App

BizBuySell is an **Angular** application, not Next.js. There is **no `__NEXT_DATA__`** tag.

**Evidence:**
- Script URLs contain `/_ng/` prefix (e.g., `/_ng/main-EOYN3Y2E.js`, `/_ng/polyfills-BKCAYBI7.js`)
- HTML elements use `ng-tns-*` and `ng-star-inserted` class names (Angular template syntax)
- Window contains Zone.js symbols (`__zone_symbol__*`) — Angular's change detection dependency
- No React, no `__NEXT_DATA__`, no `window.__INITIAL_STATE__`

**Data is embedded in:** `<script id="BBS-state" type="application/json">` (Angular transfer state)

This is a ~655 KB JSON blob containing pre-rendered API responses. The plan references to `__NEXT_DATA__` and `props.pageProps.listings` must be updated to use the BBS-state extraction path instead.

---

## 1. Bot Detection: Akamai (NOT Cloudflare)

| Method | Result |
|---|---|
| `requests.get()` | 200 but empty shell (no data) |
| Standard Selenium (headless) | "Access Denied" — 315-346 bytes, `errors.edgesuite.net` reference |
| `undetected-chromedriver` (headless) | "Access Denied" — Akamai detects headless even with UC |
| `undetected-chromedriver` (visible/non-headless) | **Works** — full page with data |

**Important:** Headless mode does NOT work. The driver must run with `headless=False`. On macOS this opens a visible Chrome window. On Linux servers, a virtual framebuffer (Xvfb) will be needed.

**Intermittent behavioral challenge:** Akamai sometimes serves a CAPTCHA-like challenge (`sec-if-cpt-container`) even in visible mode. Warming up with a homepage visit first and adding 6-8s delays between page loads helps. A retry loop is recommended.

---

## 2. URL Patterns

### Category URL Structure

```
https://www.bizbuysell.com/{urlStub}-for-sale/
https://www.bizbuysell.com/{state-slug}/{urlStub}-for-sale/
```

The `urlStub` comes from the BBS-state `categoryHierarchy[].parentCategoryInfo.urlStub` field. These are **NOT** simple slug guesses — they are the exact values BizBuySell uses internally.

### State URL Pattern — CONFIRMED

State is a lowercase path segment (full state name):

```
https://www.bizbuysell.com/texas/building-and-construction-businesses-for-sale/
https://www.bizbuysell.com/california/building-and-construction-businesses-for-sale/
```

Tested and confirmed: Texas filter returns Texas-only listings. The `region` field on each listing is the 2-letter state code (e.g., "TX", "MA", "FL").

### Sub-category URLs

Sub-categories also have `urlStub` values and follow the same pattern:

```
https://www.bizbuysell.com/hvac-businesses-for-sale/
https://www.bizbuysell.com/texas/plumbing-businesses-for-sale/
https://www.bizbuysell.com/car-washes-for-sale/
```

This is useful for V0 because we can scrape **sub-category pages directly** for target industries like HVAC, plumbing, etc., instead of scraping the full parent category and post-filtering.

---

## 3. Data Extraction Path

### Primary: BBS-state (Angular Transfer State)

```
<script id="BBS-state" type="application/json">{ ... }</script>
```

**Extraction:**
```python
raw = driver.execute_script(
    "const el = document.getElementById('BBS-state'); return el ? el.textContent : null;"
)
data = json.loads(raw)
```

The BBS-state is a dict where keys are API endpoint URLs. The listings are at:

```
data[search_key]["value"]["bfsSearchResult"]["value"]
```

Where `search_key` starts with `api/bff/v2/BbsBfsSearchResults{...}`. To find it programmatically:

```python
for key in data:
    if "BbsBfsSearchResults" in key:
        listings = data[key]["value"]["bfsSearchResult"]["value"]
        total = data[key]["value"]["bfsSearchResult"]["total"]
        break
```

### Secondary: LD+JSON (Schema.org)

Also available via `<script type="application/ld+json">` with `@type: "SearchResultsPage"`. Contains fewer fields (name, price, image, URL, location) but is simpler to extract and doesn't require JavaScript execution.

```python
# LD+JSON path
block["about"][i]["item"]  # each item is @type: "Product"
```

**LD+JSON fields:** `@type`, `name`, `logo`, `image`, `description`, `url`, `productId`, `offers.price`, `offers.availableAtOrFrom.address.addressLocality`, `offers.availableAtOrFrom.address.addressRegion`

### Tertiary: HTML (fallback)

Listings are also in `.listing` divs (60+ per page). Links follow the pattern:
```
https://www.bizbuysell.com/business-opportunity/{slug}/{listNumber}/
```

---

## 4. Listing Field Mapping (BBS-state)

### Core Fields

| Our field | BBS-state field | Type | Example |
|---|---|---|---|
| name | `header` | str | `"Carpet, Tile & Flooring Store - Comm/Res - RE Incld"` |
| source_id | `listNumber` | int | `2363575` |
| url | `urlStub` | str | `"https://www.bizbuysell.com/business-opportunity/carpet-tile.../2363575/"` |
| asking_price | `price` | int | `2499999` (cents NOT dollars — this is in dollars) |
| cash_flow | `cashFlow` | int or null | `451918` |
| ebitda | `ebitda` | int or null | `null` (rarely populated at listing level) |
| location | `location` | str | `"Middlesex County, MA"` |
| state | `region` | str | `"MA"` (2-letter state code) |
| description | `description` | str | `"Carpet, Tile, Hardwoods - this company does it all..."` |
| broker | `contactInfo.contactFullName` | str | `"Ron Ekstrom"` |
| broker_company | `contactInfo.brokerCompany` | str | `"George & Company/CentralBrokers"` |
| image | `img[0]` | str (URL) | `"https://images.bizbuysell.com/shared/listings/..."` |

### Financial Fields

| Field | BBS-state key | Coverage | Notes |
|---|---|---|---|
| asking_price | `price` | 57/61 (93%) | Integer, in USD. Some listings have `price=1` (auction) |
| cash_flow (SDE) | `cashFlow` | 38/61 (62%) | Integer, in USD. null when not disclosed |
| ebitda | `ebitda` | 12/61 (20%) | Rarely populated at search result level |
| annual_revenue | **NOT AVAILABLE** | 0% | Not in search results. Only on detail page. |
| days_on_market | **NOT AVAILABLE** | 0% | Not in search results. Only on detail page. |
| listed_date | **NOT AVAILABLE** | 0% | Not in search results. |

### Additional Fields

| BBS-state field | Type | Notes |
|---|---|---|
| `specificId` | int | Same as `listNumber` |
| `siteSpecificId` | int | Same as `listNumber` |
| `listingTypeId` | int | 40 = standard listing |
| `financingTypeId` | int | 1 = seller financing available |
| `adLevelId` | int | Ad tier (5 = premium) |
| `hotProperty` | bool | Flagged as hot |
| `recentlyUpdated` | bool | Recently modified |
| `recentlyAdded` | bool | Newly listed |
| `listingPriceReduced` | bool | Price was reduced |
| `realEstateIncludedInAskingPrice` | bool | RE included |
| `region` | str | 2-letter state code |
| `diamondMetaData.locationSt` | str | Full state name (e.g., "Massachusetts") |
| `diamondMetaData.regionId` | int | Internal region ID |
| `contactInfo.contactFullName` | str | Broker/seller name |
| `contactInfo.brokerCompany` | str | Brokerage firm |
| `contactInfo.contactPhoneNumber.telephone` | str | Phone |
| `contactInfo.brokerProfileUrl` | str | Broker profile URL |

---

## 5. Pagination

### Fields from BBS-state

```python
sr = data[search_key]["value"]["bfsSearchResult"]
```

| Field | Value | Notes |
|---|---|---|
| `sr["count"]` | 50 | Results per page (page size) |
| `sr["total"]` | 3782 | Total matching listings across all pages |
| `sr["criteria"]["pageNumber"]` | 1 | Current page (1-indexed) |
| `sr["criteria"]["offset"]` | 0 | Offset (0-indexed) |
| `sr["criteria"]["howMany"]` | 50 | Page size from criteria |

### Pagination URL Parameter

Not yet confirmed whether pagination uses `?pg=2` or `?offset=50` or is encoded in the URL path. The `criteria` object suggests `offset` + `howMany` is the internal mechanism. The URL for page 2 is likely:

```
https://www.bizbuysell.com/building-and-construction-businesses-for-sale/2/
```

or:

```
https://www.bizbuysell.com/building-and-construction-businesses-for-sale/?pg=2
```

**NOTE:** The BBS-state `value` array contains 61 items on a page with `count=50`. This is because the array includes 50 regular listings + ~11 "related" or "diamond" listings mixed in. Filter by `listingTypeId` or `isInlineAd` to get clean results.

---

## 6. Confirmed Category Slugs (All 21)

### Parent Categories (urlStub values from BBS-state)

| Category | urlStub | Full URL (append `-for-sale/`) | Category ID |
|---|---|---|---|
| Agriculture | `agriculture-businesses` | `/agriculture-businesses-for-sale/` | 62 |
| Automotive & Boat | `automotive-and-boat-businesses` | `/automotive-and-boat-businesses-for-sale/` | 68 |
| Beauty & Personal Care | `beauty-and-personal-care-businesses` | `/beauty-and-personal-care-businesses-for-sale/` | 69 |
| Building & Construction | `building-and-construction-businesses` | `/building-and-construction-businesses-for-sale/` | 60 |
| CLASSIFIEDS | `business-classifieds` | `/business-classifieds-for-sale/` | 65 |
| Communication & Media | `communication-and-media-businesses` | `/communication-and-media-businesses-for-sale/` | 63 |
| Education & Children | `education-and-child-related-businesses` | `/education-and-child-related-businesses-for-sale/` | 55 |
| Entertainment & Recreation | `entertainment-and-recreation-businesses` | `/entertainment-and-recreation-businesses-for-sale/` | 54 |
| Financial Services | `financial-services-businesses` | `/financial-services-businesses-for-sale/` | 67 |
| Health Care & Fitness | `health-care-and-fitness-businesses` | `/health-care-and-fitness-businesses-for-sale/` | 57 |
| Manufacturing | `manufacturing-businesses` | `/manufacturing-businesses-for-sale/` | 58 |
| Non-Classifiable Establishments | `all-non-classifiable-establishments` | `/all-non-classifiable-establishments-for-sale/` | 64 |
| Online & Technology | `online-and-technology-businesses` | `/online-and-technology-businesses-for-sale/` | 66 |
| Pet Services | `pet-service-businesses` | `/pet-service-businesses-for-sale/` | 70 |
| Real Estate | `real-estate-businesses` | `/real-estate-businesses-for-sale/` | 61 |
| Restaurants & Food | `restaurants-and-food-businesses` | `/restaurants-and-food-businesses-for-sale/` | 52 |
| Retail | `retail-businesses` | `/retail-businesses-for-sale/` | 51 |
| Service Businesses | `service-businesses` | `/service-businesses-for-sale/` | 53 |
| Transportation & Storage | `transportation-and-storage-businesses` | `/transportation-and-storage-businesses-for-sale/` | 56 |
| Travel | `travel-businesses` | `/travel-businesses-for-sale/` | 71 |
| Wholesale & Distributors | `wholesale-and-distribution-businesses` | `/wholesale-and-distribution-businesses-for-sale/` | 59 |

### Plan vs. Reality — Slug Corrections

| Plan assumed | Actual urlStub | Different? |
|---|---|---|
| `agriculture` | `agriculture-businesses` | YES |
| `automotive-boat` | `automotive-and-boat-businesses` | YES |
| `beauty-personal-care` | `beauty-and-personal-care-businesses` | YES |
| `building-and-construction` | `building-and-construction-businesses` | YES (missing `-businesses`) |
| `communication-media` | `communication-and-media-businesses` | YES |
| `education-children` | `education-and-child-related-businesses` | YES |
| `entertainment-recreation` | `entertainment-and-recreation-businesses` | YES |
| `financial-services` | `financial-services-businesses` | YES |
| `health-care-fitness` | `health-care-and-fitness-businesses` | YES |
| `manufacturing` | `manufacturing-businesses` | YES |
| `non-classifiable-establishments` | `all-non-classifiable-establishments` | YES |
| `online-technology` | `online-and-technology-businesses` | YES |
| `pet-services` | `pet-service-businesses` | YES |
| `restaurants-food` | `restaurants-and-food-businesses` | YES |
| `retail` | `retail-businesses` | YES |
| `service-businesses` | `service-businesses` | NO (correct) |
| `transportation-storage` | `transportation-and-storage-businesses` | YES |
| `travel` | `travel-businesses` | YES |
| `wholesale-distributors` | `wholesale-and-distribution-businesses` | YES |

**Every slug in the plan was wrong except `service-businesses`.** The URL pattern appends `-for-sale/` to the `urlStub`, and the `urlStub` values typically end with `-businesses`.

### Target Industry Sub-Categories (can be scraped directly)

| Industry | Sub-category | urlStub | Parent Category |
|---|---|---|---|
| HVAC | HVAC Businesses | `hvac-businesses` | Building & Construction (60) |
| Plumbing | Plumbing | `plumbing-businesses` | Building & Construction (60) |
| Electrical | Electrical & Mechanical | `electrical-and-mechanical-contracting-businesses` | Building & Construction (60) |
| Car Wash | Car Washes | `car-washes` | Automotive & Boat (68) |
| Landscaping | Landscaping & Yard Services | `landscaping-and-yard-service-businesses` | Service Businesses (53) |
| Cleaning | Cleaning Businesses | `cleaning-businesses` | Service Businesses (53) |
| Pest Control | Pest Control | `pest-control-businesses` | Service Businesses (53) |
| Auto Repair | Auto Repair & Service Shops | `auto-repair-and-service-shops` | Automotive & Boat (68) |
| Restaurant | Restaurants & Food (parent) | `restaurants-and-food-businesses` | (parent category 52) |
| Pool Service | **No sub-category** | N/A | Search within Service Businesses |

---

## 7. Market Stats Data

The BBS-state includes aggregate market statistics per category:

```json
{
  "industryDescription": "Building and Construction Business",
  "listedForSale": 2472,
  "askingPriceBenchmarks": {
    "median": 690000,
    "lowerQuartile": 299000,
    "upperQuartile": 1650000
  },
  "grossRevenueBenchmarks": {
    "median": 1371593,
    "lowerQuartile": 718000,
    "upperQuartile": 3030991
  },
  "sdeBenchmarks": {
    "median": 280000,
    "lowerQuartile": 159566.25,
    "upperQuartile": 520435
  },
  "sdeMultipleBenchmarks": {
    "median": 2.82,
    "lowerQuartile": 1.89,
    "upperQuartile": 3.81
  },
  "revenueMultipleBenchmarks": {
    "median": 0.6,
    "lowerQuartile": 0.36,
    "upperQuartile": 0.92
  }
}
```

This is free industry-level valuation data. Useful for the validation layer (Milestone 5) and for the UI.

---

## 8. Sample Raw Listing (from BBS-state)

```json
{
  "header": "Owner-Operated HVAC Business with Vehicles Included",
  "location": "Hamilton Township, NJ",
  "price": 450000,
  "cashFlow": 172000,
  "ebitda": null,
  "description": "Owner-Operated HVAC Business with Vehicles Included...",
  "listNumber": 2472123,
  "urlStub": "https://www.bizbuysell.com/business-opportunity/owner-operated-hvac-business.../2472123/",
  "region": "NJ",
  "img": ["https://images.bizbuysell.com/shared/listings/..."],
  "contactInfo": {
    "contactFullName": "Jane Doe",
    "brokerCompany": "ABC Business Brokers",
    "contactPhoneNumber": { "telephone": "555-123-4567" }
  },
  "listingTypeId": 40,
  "financingTypeId": 1,
  "hotProperty": false,
  "recentlyUpdated": true,
  "recentlyAdded": false,
  "listingPriceReduced": false,
  "realEstateIncludedInAskingPrice": false
}
```

---

## 9. Implementation Implications

### Must change from plan:

1. **No `__NEXT_DATA__`** — Replace all references with BBS-state extraction (`<script id="BBS-state">`)
2. **No headless mode** — `undetected-chromedriver` must run with `headless=False`. Need Xvfb on servers.
3. **Category slugs are all wrong** — Use the `urlStub` values documented above
4. **No revenue at listing level** — `annual_revenue` will always be null from search results. Revenue is only available on individual listing detail pages.
5. **No days_on_market at listing level** — Same as revenue; detail page only
6. **No listed_date at listing level** — Same
7. **Sub-category URLs work** — Can scrape `/hvac-businesses-for-sale/` directly instead of scraping all of Building & Construction and post-filtering. This dramatically improves precision for V0.
8. **Listing array has ~61 items** for `count=50` — includes "related" listings mixed in. May need to filter by `listingTypeId` or `adLevelId`.
9. **Price is integer** (not string) — No `parse_money()` needed for BBS-state extraction. LD+JSON also has integer price.
10. **Location format** — `"City, ST"` or `"County, ST"` — the `region` field gives the clean 2-letter state code

### LD+JSON as simpler alternative:

The LD+JSON `SearchResultsPage` provides ~55-60 listings per page with `name`, `price`, `url`, `productId`, `description`, and location. It has fewer fields than BBS-state but doesn't require parsing the complex BBS-state key structure. Consider using LD+JSON as the primary extraction method with BBS-state as enrichment.

### Recommended extraction priority:

1. **BBS-state** — richest data (price, cashFlow, broker, region, flags)
2. **LD+JSON** — fallback if BBS-state parsing changes
3. **HTML** — last resort fallback
