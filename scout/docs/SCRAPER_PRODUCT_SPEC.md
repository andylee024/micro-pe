# Scout Multi-State FDD Scraper - Product Specification
**Version:** 1.0
**Date:** February 17, 2026
**Owner:** Scout Team
**Status:** Ready for Implementation

---

## Executive Summary

Build a comprehensive FDD (Franchise Disclosure Document) data collection system covering 90%+ of the U.S. franchise market. This system will enable automated due diligence on small and medium businesses by aggregating Item 19 financial performance data from 10 state databases.

**Business Value:**
- Automate FDD data collection (100x faster than manual)
- Access Item 19 financial benchmarks (revenue, EBITDA, unit economics)
- Cover 15,000-20,000 unique franchise brands
- Enable data-driven SMB acquisition decisions

**Timeline:** 10-12 days autonomous implementation
**Coverage:** 90%+ U.S. franchise market (10 states)

---

## Product Vision

### Problem Statement

Private equity firms and SMB acquirers need accurate financial benchmarks to value businesses during due diligence. Franchise Disclosure Documents (FDDs) contain Item 19 data with revenue, EBITDA, and unit economics—but this data is scattered across 10 state databases with different interfaces, formats, and access methods.

**Current Pain:**
- Manual FDD collection: 2-4 hours per franchise brand
- Inconsistent data formats across states
- No unified view of cross-state filings
- Item 19 extraction requires manual PDF reading

### Solution Overview

Autonomous scraping system with 4 specialized scrapers + 1 aggregator:

```
┌─────────────────────────────────────────────────────────┐
│              FDD Aggregator (Unified API)               │
│  • Queries all scrapers                                 │
│  • Deduplicates cross-state filings                     │
│  • Returns 50+ FDDs per industry query                  │
└─────────────────────────────────────────────────────────┘
                           │
        ┌──────────────────┴──────────────────┐
        │                                     │
┌───────▼────────┐  ┌──────────┐  ┌──────────▼─────────┐
│ Minnesota (✅) │  │Wisconsin │  │  California         │
│ 70 car washes  │  │   (NEW)  │  │     (NEW)          │
│ 2K brands      │  │1.5K      │  │  4-5K brands       │
│ 15% market     │  │11% market│  │  30% market        │
└────────────────┘  └──────────┘  └────────────────────┘

┌─────────────────────────────────┐  ┌──────────────────┐
│   NASAA FRED (NEW)              │  │ BizBuySell       │
│   7 states: NY, IL, MD, VA,     │  │   (ENHANCE)      │
│   WA, ND, RI                     │  │ Market comps     │
│   3-4K brands, 46% market        │  │ Sales data       │
└─────────────────────────────────┘  └──────────────────┘
```

**Key Capabilities:**
- Search by industry keyword across all states
- Download FDD PDFs automatically
- Extract Item 19 financial data
- 90-day intelligent caching
- Deduplicate cross-state filings
- Track data provenance (which state provided which FDD)

---

## Target Users

### Primary: Data Analysts (Scout Team)
- **Need:** Quick access to FDD financial benchmarks
- **Use Case:** "Find all car wash FDD Item 19 data in California"
- **Success:** Get 20+ FDDs with Item 19 text in <2 minutes

### Secondary: PE Deal Teams
- **Need:** Validate target company financials against franchise benchmarks
- **Use Case:** "Is $1.2M revenue typical for this car wash brand?"
- **Success:** Compare target against 50+ franchise unit economics

### Tertiary: Automated Reports
- **Need:** Programmatic access to FDD data for report generation
- **Use Case:** Generate market overview reports automatically
- **Success:** JSON API returns structured FDD data

---

## System Architecture

### Component Overview

```python
# High-level usage
from tools.fdd_aggregator import FDDAggregator

aggregator = FDDAggregator()

# Search all states
results = aggregator.search_all(
    industry="car wash",
    max_results_per_source=10,
    download_pdfs=False,    # Fast metadata only
    extract_item19=False,
    use_cache=True
)

# Results
{
    "total_deduplicated": 67,  # Unique FDDs after dedup
    "states_covered": 10,
    "market_coverage": "92%",
    "by_state": {
        "minnesota": {"total_found": 18, "results": [...]},
        "wisconsin": {"total_found": 12, "results": [...]},
        "california": {"total_found": 25, "results": [...]},
        "nasaa_fred": {"total_found": 31, "results": [...]}
    }
}
```

### Data Flow

```
1. User Query
   ↓
2. FDD Aggregator
   ├─→ Query Minnesota Scraper
   ├─→ Query Wisconsin Scraper
   ├─→ Query California Scraper
   └─→ Query NASAA FRED Scraper
   ↓
3. Cache Layer (check 90-day TTL)
   ↓
4. Web Scraping (if cache miss)
   ├─→ Selenium + BeautifulSoup
   ├─→ Anti-detection measures
   └─→ Rate limiting
   ↓
5. PDF Download (optional)
   ↓
6. Item 19 Extraction (optional)
   ├─→ PyMuPDF text extraction
   └─→ Regex pattern matching
   ↓
7. Deduplication
   ├─→ Key: (franchise_name, year)
   └─→ Precedence: Recent > Has PDF > Has Item19 > Larger state
   ↓
8. Return Results
```

---

## Component Specifications

### 1. Wisconsin FDD Scraper (`tools/wisconsin_fdd.py`)

**Purpose:** Scrape Wisconsin Department of Financial Institutions FDD database

**Technical Details:**
- **URL:** https://apps.dfi.wi.gov/apps/FranchiseSearch/MainSearch.aspx
- **Technology:** ASP.NET web forms
- **Complexity:** Medium (simpler than Minnesota)
- **Market Coverage:** 11% (1,500-2,000 brands)

**Key Features:**
- Form ID: `ctl00_MainContent_txtSearch`
- Button ID: `ctl00_MainContent_btnSearch`
- Results table: `ctl00_MainContent_gvResults`
- ASP.NET GridView parsing
- Direct PDF downloads (easier than Minnesota)
- 90-day cache TTL

**API:**
```python
class WisconsinFDDScraper(Tool):
    def search(
        self,
        industry: str,
        max_results: int = 10,
        download_pdfs: bool = True,
        extract_item19: bool = True,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """Search Wisconsin DFI for FDDs"""
```

**Estimated Size:** 400 lines
**Implementation Time:** 2-3 days (agent loop)

---

### 2. California FDD Scraper (`tools/california_fdd.py`)

**Purpose:** Scrape California DFPI DocQNet FDD database

**Technical Details:**
- **URL:** https://docqnet.dfpi.ca.gov/search/
- **Technology:** Custom web application
- **Complexity:** High (pagination, slow DB, document filtering)
- **Market Coverage:** 30% (4,000-5,000 brands, LARGEST)

**Key Features:**
- Slow database (7-10 second waits required)
- Pagination support (results span multiple pages)
- Document type filtering (FDDs vs blacklines vs applications)
- Largest single-state database
- 90-day cache TTL

**Special Handling:**
```python
# California requires longer waits
time.sleep(random.uniform(7, 10))  # vs 2-5 for other states

# Pagination handling
def _handle_pagination(self, soup, max_results):
    while len(results) < max_results:
        # Parse current page
        # Click "Next" button
        # Wait 7-10 seconds
        # Continue
```

**API:** Same as Wisconsin (consistent interface)

**Estimated Size:** 450 lines
**Implementation Time:** 3-4 days (agent loop)

---

### 3. NASAA FRED FDD Scraper (`tools/nasaa_fred_fdd.py`)

**Purpose:** Scrape NASAA FRED multi-state FDD database

**Technical Details:**
- **URL:** https://www.nasaaefd.org/Franchise/Search
- **Technology:** Multi-state aggregator
- **Complexity:** Medium-High (state tagging, deduplication)
- **Market Coverage:** 46% (7 states: NY, IL, MD, VA, WA, ND, RI)

**Key Features:**
- Single database covering 7 states
- Each FDD tagged with filing state
- Optional state filtering
- Cross-state deduplication needed
- Highest ROI (covers most states in one implementation)

**Enhanced API:**
```python
class NASAAFredFDDScraper(Tool):
    def search(
        self,
        industry: str,
        max_results: int = 10,
        states: Optional[List[str]] = None,  # NEW: Filter by state
        download_pdfs: bool = True,
        extract_item19: bool = True,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """Search NASAA FRED for FDDs across 7 states"""
```

**Response Format:**
```python
{
    "source": "nasaa_fred",
    "states_searched": ["NY", "IL", "MD", "VA", "WA", "ND", "RI"],
    "total_found": 45,
    "results": [
        {
            "franchise_name": "TOMMY'S EXPRESS",
            "filing_state": "NY",  # NEW: Track provenance
            "document_id": "NASAA-2024-12345",
            "pdf_url": "https://...",
            "fdd_year": 2024
        }
    ]
}
```

**Estimated Size:** 500 lines
**Implementation Time:** 3-4 days (agent loop)

---

### 4. FDD Aggregator (`tools/fdd_aggregator.py`)

**Purpose:** Unified interface to query all FDD scrapers with deduplication

**Technical Details:**
- **Complexity:** Medium (orchestration + deduplication logic)
- **Dependencies:** All 4 FDD scrapers (MN, WI, CA, NASAA)

**Key Features:**
- Query all scrapers in parallel (or sequential)
- Deduplication by (franchise_name, fdd_year)
- Provenance tracking (which state provided each FDD)
- Coverage statistics
- Smart precedence rules

**Deduplication Logic:**
```python
def _is_better_version(new_fdd, existing_fdd):
    """
    Determine which FDD version to keep.

    Precedence:
    1. More recent year (2025 > 2024)
    2. Has PDF downloaded (vs no PDF)
    3. Has Item 19 extracted (vs no Item 19)
    4. Larger state (CA > NY > MN > WI)
    """
    if new_fdd['year'] > existing_fdd['year']:
        return True
    if new_fdd['year'] == existing_fdd['year']:
        if new_fdd['has_pdf'] and not existing_fdd['has_pdf']:
            return True
        if new_fdd['has_item19'] and not existing_fdd['has_item19']:
            return True
    return False
```

**API:**
```python
class FDDAggregator:
    def search_all(
        self,
        industry: str,
        max_results_per_source: int = 10,
        download_pdfs: bool = False,
        extract_item19: bool = False,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """Search ALL FDD databases"""

    def search_by_states(
        self,
        industry: str,
        states: List[str],
        **kwargs
    ) -> Dict[str, Any]:
        """Search specific states only"""

    def get_coverage_stats(self) -> Dict[str, Any]:
        """Return market coverage statistics"""
```

**Estimated Size:** 200 lines
**Implementation Time:** 1-2 days (agent loop)

---

### 5. BizBuySell Scraper (Enhancement) (`tools/bizbuysell_tool.py`)

**Purpose:** Enhance existing BizBuySell scraper for market comparables

**Current State:** Basic implementation (100 lines, untested)

**Enhancements Needed:**
- Add proper error handling
- Improve parsing robustness
- Add caching consistency
- Test with real queries
- Documentation

**API:** Already defined, just needs testing/refinement

**Estimated Size:** 150 lines (50 lines added)
**Implementation Time:** 1 day (agent loop)

---

## Common Patterns (All Scrapers)

### Base Class Inheritance

```python
from tools.base import Tool

class NewScraper(Tool):
    """All scrapers inherit from Tool base class"""

    BASE_URL = "https://..."
    CACHE_TTL_DAYS = 90

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.output_dir = Path("outputs/fdds/state")
        self.output_dir.mkdir(parents=True, exist_ok=True)
```

### Chrome Driver Setup (Anti-Detection)

```python
def _get_driver(self):
    """Standard Chrome setup with anti-detection"""
    options = webdriver.ChromeOptions()
    options.add_argument('--headless=new')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    # CDP anti-detection
    driver.execute_cdp_cmd('Network.setUserAgentOverride', {
        "userAgent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'
    })
    driver.execute_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    )

    return driver
```

### Rate Limiting

```python
import time
import random

# Between searches
time.sleep(random.uniform(2.0, 5.0))

# Between PDF downloads
time.sleep(random.uniform(1.0, 3.0))
```

### Caching

```python
# Check cache (90-day TTL)
cache_key = f"state_{industry.replace(' ', '_')}_{max_results}"
if use_cache:
    cached = self.load_cache(cache_key)
    if cached:
        return cached["data"]

# ... scraping logic ...

# Save cache
self.save_cache(cache_key, response, self.CACHE_TTL_DAYS)
```

---

## Success Criteria

### Per-Scraper Success

**Functional Requirements:**
- [ ] Can search by industry keyword
- [ ] Returns 10+ results for "car wash" query
- [ ] Extracts franchise name, document ID, PDF URL, year
- [ ] Follows minnesota_fdd.py pattern (449 lines reference)
- [ ] Inherits from Tool base class
- [ ] Has 90-day caching working
- [ ] Handles errors gracefully (timeouts, no results, rate limits)

**Quality Requirements:**
- [ ] >80% success rate on 10 test queries
- [ ] <5 minutes per 10 results
- [ ] >50% cache hit rate on repeated queries
- [ ] Code follows PEP 8 style
- [ ] Comprehensive docstrings
- [ ] Test suite passes

### Aggregator Success

- [ ] Queries all 4 scrapers successfully
- [ ] Deduplicates correctly (no duplicate franchise+year combos)
- [ ] Returns 50+ unique FDDs for "car wash" query
- [ ] Tracks provenance (which state provided each FDD)
- [ ] Coverage statistics accurate (market %)
- [ ] <10 minutes for full multi-state search

### System-Level Success

- [ ] Total coverage: 90%+ U.S. franchise market
- [ ] Total brands: 15,000-20,000 unique franchises
- [ ] Total documents: 30,000-40,000 FDDs
- [ ] States covered: 10 (MN, WI, CA, NY, IL, MD, VA, WA, ND, RI)
- [ ] Zero cost (public data, no API fees)

---

## Non-Functional Requirements

### Performance
- Search latency: <5 minutes per 10 results per state
- Cache hit rate: >50% for repeated queries
- PDF download: <30 seconds per PDF
- Item 19 extraction: <10 seconds per PDF

### Reliability
- Success rate: >80% of searches return results
- Error recovery: Graceful handling of timeouts, 429s, 404s
- Retry logic: Exponential backoff on failures
- No data loss: Failed searches don't corrupt cache

### Maintainability
- Code style: PEP 8 compliant
- Documentation: Comprehensive docstrings
- Testing: >80% code coverage
- Logging: Clear error messages and progress indicators

### Security
- No credentials stored in code
- Respect robots.txt
- Rate limiting to avoid server overload
- No CAPTCHA circumvention
- Public data only (no auth bypass)

---

## Testing Strategy

### Unit Tests (Per Scraper)

```python
def test_search_cached():
    """Fast test using cached data"""
    scraper = WisconsinFDDScraper()
    results = scraper.search("car wash", max_results=5, use_cache=True)
    assert results['total_found'] > 0

def test_parse_html():
    """Test parsing with fixture HTML"""
    html = load_fixture('wisconsin_results.html')
    parsed = scraper._parse_results(html)
    assert len(parsed) > 0

@pytest.mark.slow
def test_live_search():
    """Only 1 live test (hits real website)"""
    scraper = WisconsinFDDScraper()
    results = scraper.search("car wash", max_results=2, use_cache=False)
    assert results['source'] == 'wisconsin_dfi'
```

### Integration Tests

```python
def test_aggregator_all_states():
    """Test searching all states"""
    aggregator = FDDAggregator()
    results = aggregator.search_all(
        industry="car wash",
        max_results_per_source=3
    )
    assert results['states_covered'] == 10
    assert 'minnesota' in results['by_state']

def test_deduplication():
    """Test cross-state deduplication"""
    # Search for "mcdonald's" (likely in all states)
    aggregator = FDDAggregator()
    results = aggregator.search_all(industry="mcdonald's")

    # Check no duplicates
    seen = set()
    for state_results in results['by_state'].values():
        for fdd in state_results['results']:
            key = (fdd['franchise_name'].lower(), fdd['fdd_year'])
            assert key not in seen
            seen.add(key)
```

### Validation Queries

Standard queries for testing each scraper:

1. **"car wash"** - Should find 10+ results in every state
2. **"mcdonald's"** - Should find in all databases
3. **"hvac"** - Should find 5+ results
4. **"laundromat"** - Should find 3+ results
5. **"mosquito control"** - Edge case (niche industry)

---

## Timeline & Milestones

### Phase 1: Wisconsin Scraper (Days 1-3)
- **Goal:** Validate agent loop pattern on simplest new scraper
- **Deliverable:** tools/wisconsin_fdd.py (400 lines)
- **Success Gate:** Can search "car wash" and get 10+ Wisconsin FDDs

### Phase 2: California Scraper (Days 3-6)
- **Goal:** Implement largest state database
- **Deliverable:** tools/california_fdd.py (450 lines)
- **Success Gate:** Can handle pagination and get 20+ California FDDs

### Phase 3: NASAA FRED Scraper (Days 6-9)
- **Goal:** Cover 7 states in one implementation (highest ROI)
- **Deliverable:** tools/nasaa_fred_fdd.py (500 lines)
- **Success Gate:** Can tag FDDs by state and get 30+ results

### Phase 4: FDD Aggregator (Days 9-11)
- **Goal:** Unify all scrapers with deduplication
- **Deliverable:** tools/fdd_aggregator.py (200 lines)
- **Success Gate:** Returns 50+ unique FDDs across all states

### Phase 5: BizBuySell Enhancement (Days 11-12)
- **Goal:** Add market comps data source
- **Deliverable:** Enhanced tools/bizbuysell_tool.py (150 lines)
- **Success Gate:** Can get 10+ market comp listings

**Total Timeline:** 12 days (agent loop autonomous implementation)

---

## Risk Assessment

### Technical Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Site structure changes | High | Medium | Version detection, fallback modes |
| Bot detection / IP blocking | High | Low | Anti-detection (CDP), rate limiting |
| Slow performance | Medium | Medium | Aggressive caching (90-day TTL) |
| Inconsistent data quality | Medium | High | Graceful degradation, validation |
| PDF downloads fail | Medium | Medium | Session management, retries |
| Item 19 not in all FDDs | Low | High | Expected, track has_item19 flag |

### Business Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Legal concerns | High | Low | Public data only, respect robots.txt |
| Data freshness | Medium | Medium | 90-day cache TTL, manual refresh option |
| Incomplete coverage | Medium | Low | 90%+ coverage target exceeded |

---

## Dependencies

### External Dependencies
- **Selenium** (web scraping)
- **BeautifulSoup** (HTML parsing)
- **PyMuPDF** (PDF text extraction)
- **webdriver-manager** (Chrome driver management)
- **httpx** (HTTP requests)

### Internal Dependencies
- **tools/base.py** (Tool base class) - Already exists ✅
- **tools/minnesota_fdd.py** (Reference implementation) - Already exists ✅

### Infrastructure
- Chrome browser (for Selenium)
- Python 3.8+
- Git (version control)
- 20GB disk space (PDF storage)

---

## Rollout Plan

### Phase 1: MVP (Metadata Only)
**Goal:** Get all scrapers working for metadata extraction (no PDFs)

**Features:**
- Search by industry
- Extract franchise names, IDs, URLs, years
- Caching
- Deduplication

**Timeline:** Days 1-8
**Value:** 80% of use cases (analysts can get FDD URLs)

### Phase 2: PDF Download
**Goal:** Enable automatic PDF downloads

**Features:**
- Session-preserved downloads
- Rate limit handling
- Storage management

**Timeline:** Days 9-10
**Value:** Full offline access to FDDs

### Phase 3: Item 19 Extraction
**Goal:** Extract Item 19 financial data automatically

**Features:**
- PyMuPDF extraction
- Regex pattern matching
- Structured text output

**Timeline:** Days 11-12
**Value:** Immediate access to financial benchmarks

---

## Maintenance Plan

### Monitoring
- Weekly: Run validation queries on all scrapers
- Monthly: Check success rate metrics
- Quarterly: Review site structure changes

### Updates
- Site changes: Update selectors/parsers as needed
- Cache refresh: Manual refresh option for stale data
- New states: Add scrapers for additional states if needed

### Support
- Documentation: Comprehensive README and docstrings
- Error messages: Clear, actionable error reporting
- Debugging: Screenshots and HTML dumps on failures

---

## Appendices

### Appendix A: Market Coverage Calculation

```
Total U.S. Franchises: ~4,000 brands

State Coverage:
- Minnesota: 15% (2,000 brands)
- Wisconsin: 11% (1,500 brands)
- California: 30% (4,500 brands)
- NASAA FRED (7 states):
  - New York: 15%
  - Illinois: 8%
  - Maryland: 3%
  - Virginia: 3%
  - Washington: 3%
  - North Dakota: 2%
  - Rhode Island: 2%

Total: ~92% coverage (with overlap, deduplicated to ~90%)
Unique brands: 15,000-20,000
Total documents: 30,000-40,000 FDDs
```

### Appendix B: Reference Implementation

**Gold Standard:** `tools/minnesota_fdd.py` (449 lines)

All new scrapers should follow this pattern:
- Lines 23-52: Chrome driver setup
- Lines 67-98: Form filling and result parsing
- Lines 143-178: PDF download with session preservation
- Lines 180-212: Item 19 extraction with PyMuPDF

### Appendix C: State Database URLs

- Minnesota CARDS: https://www.cards.commerce.state.mn.us/
- Wisconsin DFI: https://apps.dfi.wi.gov/apps/FranchiseSearch/MainSearch.aspx
- California DocQNet: https://docqnet.dfpi.ca.gov/search/
- NASAA FRED: https://www.nasaaefd.org/Franchise/Search
- BizBuySell: https://www.bizbuysell.com/

---

## Approval

**Product Owner:** ___________
**Engineering Lead:** ___________
**Date:** ___________

---

**End of Product Specification**
