# Plan: Multi-State FDD Scraper Pipeline for SMB Due Diligence

## Context

The user wants to build scrapers for multiple state FDD (Franchise Disclosure Document) databases to create a comprehensive data pipeline for doing due diligence on small and medium businesses.

**Current State:**
- ✅ Minnesota CARDS scraper is fully functional (449 lines)
  - Covers ~2,000-3,000 franchise brands (15% market share)
  - Uses Selenium + BeautifulSoup + PyMuPDF pattern
  - 90-day cache, PDF download, Item 19 extraction working
- ✅ Research complete on 10 state FDD databases
  - Wisconsin, California, NASAA FRED tested and confirmed scrapable
  - No CAPTCHA, no authentication barriers
  - Combined coverage: 90%+ of U.S. franchise market

**Business Need:**
FDD documents contain Item 19 financial performance data (revenue, EBITDA, unit economics) that's critical for valuing small businesses during due diligence. Currently this data is scattered across 10 state databases. We need a unified pipeline to aggregate FDD data from all sources.

**Target State:**
- 4 total FDD scrapers covering 10 states
- ~15,000-20,000 unique franchise brands
- ~30,000-40,000 FDD documents
- Unified aggregator for multi-state queries
- 90%+ U.S. franchise market coverage

---

## Implementation Roadmap

### Priority Order (Sequential with Validation Gates)

**Week 1: NASAA FRED Scraper** (3-4 days) - **HIGHEST ROI**
- Covers 7 states in one implementation (NY, IL, MD, VA, WA, ND, RI)
- 46% combined market share
- ~3,000-4,000 brands, ~6,000-8,000 documents
- **Rationale:** Maximum return on development effort

**Week 2: Wisconsin DFI Scraper** (2-3 days) - **QUICK WIN**
- 11% market share (~1,500-2,000 brands)
- Simplest implementation (direct PDF downloads, well-documented)
- **Rationale:** Validate pattern replication on simpler system

**Week 2-3: California DocQNet Scraper** (3-4 days) - **LARGEST MARKET**
- 30% market share (~4,000-5,000 brands, largest single state)
- More complex (pagination, slower database)
- **Rationale:** Save complexity for after pattern validation

**Week 3: FDD Aggregator** (1-2 days) - **UNIFIED INTERFACE**
- Queries all 4 scrapers
- Deduplicates cross-state results
- Provides coverage statistics

**Week 3: Integration & Testing** (1-2 days)
- End-to-end testing
- Documentation
- Real-world validation

**Total Timeline:** 10-15 days

---

## Architecture Design

### File Structure

```
scout/
├── tools/
│   ├── base.py                      # ✅ Already exists (Tool base class)
│   ├── minnesota_fdd.py             # ✅ Already exists (449 lines, working)
│   ├── wisconsin_fdd.py             # NEW - ~400 lines
│   ├── california_fdd.py            # NEW - ~450 lines
│   ├── nasaa_fred_fdd.py            # NEW - ~500 lines (multi-state)
│   ├── fdd_aggregator.py            # NEW - ~200 lines (unified interface)
│   └── __init__.py                  # UPDATE - export new scrapers
├── outputs/
│   ├── cache/                       # Shared cache directory (90-day TTL)
│   ├── fdds/                        # PDF storage by state
│   │   ├── minnesota/
│   │   ├── wisconsin/
│   │   ├── california/
│   │   └── nasaa/
│   └── raw_data/                    # JSON exports
└── tests/
    ├── test_wisconsin_fdd.py        # NEW
    ├── test_california_fdd.py       # NEW
    └── test_nasaa_fred_fdd.py       # NEW
```

### Common Pattern (All Scrapers Follow Minnesota)

```python
class StateFDDScraper(Tool):
    """Scrape FDD documents from [State] database"""

    BASE_URL = "https://..."
    CACHE_TTL_DAYS = 90

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.output_dir = Path("outputs/fdds/[state]")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def search(
        self,
        industry: str,
        max_results: int = 10,
        download_pdfs: bool = True,
        extract_item19: bool = True,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """Unified search API across all scrapers"""
        # 1. Check cache (90-day TTL)
        # 2. Scrape with Selenium + BeautifulSoup
        # 3. Download PDFs (optional, flag-based)
        # 4. Extract Item 19 (optional, flag-based)
        # 5. Save cache
        # 6. Return standardized response

    def _scrape_fdds(self, industry: str, max_results: int) -> List[Dict]:
        """State-specific Selenium scraping logic"""

    def _download_pdf_with_selenium(self, fdd: Dict, driver):
        """PDF download with session preservation (CDP + httpx fallback)"""

    def _extract_item19(self, fdd: Dict):
        """PyMuPDF + regex extraction of Item 19 financial data"""

    def _build_response(self, industry: str, results: List[Dict]) -> Dict:
        """Standardized response format"""
```

**Anti-Detection (All Scrapers):**
- Chrome options: `--disable-blink-features=AutomationControlled`, `--headless=new`
- CDP overrides: `navigator.webdriver = undefined`, user-agent override
- Rate limiting: 2-5 seconds between requests
- Retry logic: Exponential backoff on failures

---

## Implementation Details

### 1. NASAA FRED Scraper (`tools/nasaa_fred_fdd.py`)

**URL:** https://www.nasaaefd.org/Franchise/Search

**Key Features:**
- Multi-state search (NY, IL, MD, VA, WA, ND, RI)
- Each FDD tagged with filing state
- Optional state filtering
- Deduplication of cross-state filings

**Enhanced API:**
```python
def search(
    self,
    industry: str,
    max_results: int = 10,
    states: Optional[List[str]] = None,  # NEW: Filter by state codes
    download_pdfs: bool = True,
    extract_item19: bool = True,
    use_cache: bool = True
) -> Dict[str, Any]:
```

**Response Format:**
```python
{
  "source": "nasaa_fred",
  "search_date": "2026-02-17T...",
  "industry": "car wash",
  "states_searched": ["NY", "IL", "MD", "VA", "WA", "ND", "RI"],
  "total_found": 45,
  "results": [
    {
      "franchise_name": "Splash Car Wash",
      "document_id": "NASAA-2024-12345",
      "pdf_url": "https://...",
      "fdd_year": 2024,
      "filing_state": "NY",      # NEW: Track which state
      "filing_date": "2024-03-15",
      "source_url": "https://nasaaefd.org/..."
    }
  ]
}
```

**Estimated Size:** ~500 lines

**Critical Implementation Steps:**
1. Navigate to NASAA FRED search form
2. Fill franchise name/keyword field
3. Submit and wait for results
4. Parse results table with state detection
5. Tag each FDD with filing state
6. Download PDFs (preserve session cookies)
7. Extract Item 19 from PDFs

---

### 2. Wisconsin DFI Scraper (`tools/wisconsin_fdd.py`)

**URL:** https://apps.dfi.wi.gov/apps/FranchiseSearch/MainSearch.aspx

**Key Features:**
- Simplest implementation (direct PDF downloads)
- Well-documented form structure
- ASP.NET GridView for results

**Form Handling:**
```python
# Wisconsin-specific form elements
franchise_input = driver.find_element(By.ID, "ctl00_MainContent_txtSearch")
search_button = driver.find_element(By.ID, "ctl00_MainContent_btnSearch")
```

**Result Parsing:**
```python
# Wisconsin uses ASP.NET GridView
table = soup.find('table', class_='GridView')
# Different cell structure than Minnesota
```

**Estimated Size:** ~400 lines (simpler than Minnesota)

**Critical Implementation Steps:**
1. Navigate to Wisconsin DFI search
2. Fill ASP.NET form fields
3. Submit and wait for GridView results
4. Parse GridView table structure
5. Direct PDF downloads (no complex session handling needed)
6. Extract Item 19

---

### 3. California DocQNet Scraper (`tools/california_fdd.py`)

**URL:** https://docqnet.dfpi.ca.gov/search/

**Key Features:**
- Largest market (30% share)
- Slower database (need longer waits: 7-10 seconds)
- Pagination required
- Document type filtering (FDDs vs blacklines vs applications)

**Enhanced Features:**
```python
def _handle_pagination(self, soup, max_results):
    """Navigate through multi-page results"""

def _filter_document_type(self, results):
    """Filter for FDD documents only (not blacklines, applications, etc.)"""
```

**Estimated Size:** ~450 lines (includes pagination)

**Critical Implementation Steps:**
1. Navigate to California DocQNet
2. Fill search form
3. Wait 7-10 seconds for slow database
4. Parse first page of results
5. Handle pagination if needed (navigate to next pages)
6. Filter for FDD document types only
7. Download PDFs
8. Extract Item 19

---

### 4. FDD Aggregator (`tools/fdd_aggregator.py`)

**Purpose:** Unified interface to query all state scrapers

**API:**
```python
class FDDAggregator:
    """Aggregate FDD data from all state scrapers"""

    def __init__(self):
        self.scrapers = {
            'minnesota': MinnesotaFDDScraper(),
            'wisconsin': WisconsinFDDScraper(),
            'california': CaliforniaFDDScraper(),
            'nasaa_fred': NASAAFredFDDScraper()
        }

    def search_all(
        self,
        industry: str,
        max_results_per_source: int = 10,
        download_pdfs: bool = False,
        extract_item19: bool = False,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """Search ALL FDD databases for an industry"""

    def search_by_states(
        self,
        industry: str,
        states: List[str],
        **kwargs
    ) -> Dict[str, Any]:
        """Search specific states only"""

    def deduplicate_results(self, results: Dict) -> List[Dict]:
        """Remove duplicate FDDs across states (same franchise, different states)"""

    def get_coverage_stats(self) -> Dict[str, Any]:
        """Return coverage statistics"""
```

**Deduplication Logic:**
```python
def _is_better_version(new_fdd, existing_fdd):
    """
    Determine which FDD version to keep.

    Criteria (in order):
    1. More recent year
    2. Has PDF downloaded (vs no PDF)
    3. Has Item 19 extracted (vs no Item 19)
    4. Larger state (CA > NY > MN > WI)
    """
```

**Estimated Size:** ~200 lines

---

## Testing Strategy

### Per-Scraper Testing

```python
def test_scraper_basic():
    """Test basic search functionality"""
    scraper = WisconsinFDDScraper()
    results = scraper.search(
        industry="car wash",
        max_results=5,
        download_pdfs=False,
        extract_item19=False,
        use_cache=False
    )

    assert results['source'] == 'wisconsin_dfi'
    assert results['total_found'] > 0
    assert len(results['results']) <= 5

def test_pdf_download():
    """Test PDF download"""
    # Download 1 PDF, verify file exists and size > 10KB

def test_item19_extraction():
    """Test Item 19 extraction"""
    # Extract Item 19, verify text found (if present in FDD)

def test_caching():
    """Test cache functionality"""
    # First call no cache, second call uses cache
```

### Integration Testing

```python
def test_aggregator_all_states():
    """Test searching all states"""
    aggregator = FDDAggregator()
    results = aggregator.search_all(
        industry="car wash",
        max_results_per_source=3
    )

    assert results['total_states_searched'] == 4
    assert 'minnesota' in results['by_state']
    assert 'wisconsin' in results['by_state']
    assert 'california' in results['by_state']
    assert 'nasaa_fred' in results['by_state']

def test_deduplication():
    """Test deduplication across states"""
    # Search "mcdonald's" (likely in all states)
    # Verify no duplicates, state provenance tracked
```

### Real-World Validation Queries

1. "car wash" - Should find 50+ results across all states
2. "mcdonald's" - Should find in all 4 databases
3. "hvac" - Should find 30+ results
4. "laundromat" - Should find 10+ results
5. "mosquito control" - Specific test

**Success Criteria:**
- >80% of searches return results
- >90% PDF download success rate
- >60% Item 19 extraction success rate (not all FDDs have Item 19)
- >50% cache hit rate on repeated queries
- <5 minutes per 10 results per state

---

## Data Aggregation Strategy

### Flow

```
User Query: "car wash"
    ↓
Aggregator calls all 4 scrapers (parallel or sequence)
    ↓
Each scraper returns standardized response
    ↓
Aggregator deduplicates by (franchise_name, year)
    ↓
Aggregator sorts by:
  - Most recent year
  - Most complete (has PDF, has Item 19)
  - Largest state (CA > NY > MN > WI)
    ↓
Return unified result with state provenance
```

### Why Post-Processing (Not Shared Database)

- Each state has different update schedules
- Same franchise may file in multiple states with different dates
- Easier to maintain separate scrapers + aggregation layer
- Flexible deduplication rules

---

## Error Handling & Anti-Detection

### Common Errors & Mitigation

**1. Timeout / Page Load:**
```python
try:
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "results")))
except TimeoutException:
    driver.save_screenshot("debug_timeout.png")
    return []
```

**2. No Results:**
```python
if not rows:
    print(f"   ℹ️  No results found for '{industry}'")
    return self._build_response(industry, [])  # Empty, not error
```

**3. PDF Download Failures:**
```python
try:
    self._download_pdf_with_cdp(fdd, driver)  # Try CDP first
except:
    self._download_pdf_with_httpx(fdd, driver.get_cookies())  # Fallback
```

**4. Item 19 Extraction:**
```python
try:
    self._extract_item19(fdd)
except Exception as e:
    fdd['has_item_19'] = False  # Graceful degradation
    fdd['item_19_error'] = str(e)
```

### Anti-Detection (All Scrapers)

**Chrome Options:**
```python
options.add_argument('--headless=new')
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
```

**CDP Overrides:**
```python
driver.execute_cdp_cmd('Network.setUserAgentOverride', {...})
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
```

**Rate Limiting:**
```python
time.sleep(random.uniform(2.0, 5.0))  # Between searches
time.sleep(random.uniform(1.0, 3.0))  # Between PDF downloads
```

---

## Critical Files

**Reference Files (Read Only):**
1. `/Users/andylee/Projects/micro-pe/scout/tools/minnesota_fdd.py` (449 lines)
   - Complete working implementation to use as template
   - Shows Selenium setup, form handling, PDF download, Item 19 extraction

2. `/Users/andylee/Projects/micro-pe/scout/tools/base.py` (72 lines)
   - Tool base class with caching, save/load methods
   - All new scrapers inherit from this

3. `/Users/andylee/Projects/micro-pe/scout/docs/RESEARCH.md` (17KB)
   - Scrapability assessment for all states
   - URLs, form structures, state-specific details

**Files to Create:**
1. `/Users/andylee/Projects/micro-pe/scout/tools/nasaa_fred_fdd.py` (~500 lines)
2. `/Users/andylee/Projects/micro-pe/scout/tools/wisconsin_fdd.py` (~400 lines)
3. `/Users/andylee/Projects/micro-pe/scout/tools/california_fdd.py` (~450 lines)
4. `/Users/andylee/Projects/micro-pe/scout/tools/fdd_aggregator.py` (~200 lines)
5. `/Users/andylee/Projects/micro-pe/scout/tests/test_wisconsin_fdd.py`
6. `/Users/andylee/Projects/micro-pe/scout/tests/test_california_fdd.py`
7. `/Users/andylee/Projects/micro-pe/scout/tests/test_nasaa_fred_fdd.py`

**Files to Update:**
1. `/Users/andylee/Projects/micro-pe/scout/tools/__init__.py` - Export new scrapers

---

## Success Metrics

### Scraper-Level
- Success Rate: >80% of searches return results
- PDF Download Rate: >90% success
- Item 19 Extraction Rate: >60% (not all FDDs have Item 19)
- Cache Hit Rate: >50% on repeated queries
- Error Rate: <10% unhandled exceptions
- Performance: <5 minutes per 10 results

### Pipeline-Level
- Coverage: 90%+ of U.S. franchise market
- Total Brands: 15,000-20,000 unique franchises
- Total Documents: 30,000-40,000 FDDs
- State Coverage: 10 states
- Deduplication Accuracy: >95%

### Business Value
- **Benchmark Quality:** FDD Item 19 data enables revenue/EBITDA estimation for due diligence
- **Time Savings:** Automated scraping vs manual (100x faster)
- **Data Freshness:** 90-day cache ensures recent FDDs
- **Multi-State Coverage:** Single query searches all relevant states

---

## Risk Mitigation

**Risk: Site Structure Changes**
- Mitigation: Debug screenshots, HTML dumps on failure, version pins

**Risk: Bot Detection / IP Blocking**
- Mitigation: Anti-detection (CDP, user-agent), rate limiting, respect robots.txt

**Risk: Slow Performance**
- Mitigation: Aggressive caching (90-day TTL), optional PDF download/Item 19 extraction

**Risk: Inconsistent Data Quality**
- Mitigation: Graceful degradation, partial data OK, track quality metrics

**Risk: Legal / Compliance**
- Mitigation: Public records only, no auth bypass, no CAPTCHA circumvention, rate limiting

---

## Verification Plan

### After Each Scraper Implementation

1. **Unit Tests:** Basic search, PDF download, Item 19 extraction, caching
2. **Integration Tests:** Works with aggregator
3. **Real-World Queries:** 10+ test searches, verify >80% success rate
4. **Validation Gate:** Must pass before moving to next scraper

### Final Pipeline Verification

1. **End-to-End Test:** Search "car wash" across all 4 scrapers
2. **Deduplication Test:** Verify no duplicates, state provenance tracked
3. **Performance Test:** <5 minutes per 10 results per state
4. **Coverage Test:** Verify 90%+ market coverage

### Example Usage After Implementation

```python
# Option 1: Query single state
from tools.wisconsin_fdd import WisconsinFDDScraper

scraper = WisconsinFDDScraper()
results = scraper.search(
    industry="car wash",
    max_results=10,
    download_pdfs=True,
    extract_item19=True
)

# Option 2: Query all states
from tools.fdd_aggregator import FDDAggregator

aggregator = FDDAggregator()
results = aggregator.search_all(
    industry="car wash",
    max_results_per_source=10,
    download_pdfs=False,  # Faster, metadata only
    use_cache=True
)

# Option 3: Query specific states
results = aggregator.search_by_states(
    industry="car wash",
    states=["CA", "NY", "WI"],
    max_results_per_source=10
)
```

---

## Summary

**What This Plan Delivers:**

1. **4 FDD Scrapers** - Minnesota (✅ done), Wisconsin, California, NASAA FRED (7 states)
2. **Unified Aggregator** - Query all states, deduplicate results
3. **90%+ Market Coverage** - 10 states, 15,000-20,000 brands, 30,000-40,000 documents
4. **Consistent API** - Same search() interface across all scrapers
5. **Production-Ready** - Caching, error handling, anti-detection, testing
6. **Due Diligence Pipeline** - Extract Item 19 financial data for SMB valuation

**Timeline:** 10-15 days total

**Priority Order:**
1. NASAA FRED (3-4 days) - 7 states, highest ROI
2. Wisconsin (2-3 days) - Simplest, validate pattern
3. California (3-4 days) - Largest market
4. Aggregator (1-2 days) - Unified interface
5. Testing (1-2 days) - Integration & validation

**Business Value:** Complete FDD data pipeline for small business due diligence, enabling automated benchmark collection for revenue/EBITDA estimation across 90%+ of U.S. franchise market.
