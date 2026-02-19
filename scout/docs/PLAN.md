# Agent Team Plan: Multi-State FDD Scraper System

**Created:** 2026-02-18
**Approach:** Agent Teams (Parallel Development)
**Goal:** Build 3 FDD scrapers + aggregator + comprehensive tests

---

## Executive Summary

Use **Claude Code Agent Teams** to build the remaining FDD scraper infrastructure in parallel:
- 3 state scrapers (NASAA FRED, California, Wisconsin enhancement)
- 1 unified aggregator
- Comprehensive test suite
- 4-5 agents working simultaneously

**Estimated time:** 2-4 hours (vs. 10-15 hours sequential)
**Coverage:** 90%+ U.S. franchise market
**Total output:** ~2,500 lines of production code

---

## Current State

### ✅ Completed
- **Minnesota FDD Scraper** (449 lines) - 15% market coverage
- **Wisconsin FDD Scraper** (378 lines) - 11% market coverage
- **Wisconsin Test Suite** (374 lines) - validation queries, edge cases
- **Base Tool Class** (72 lines) - caching, standardized API
- **Agent Loop System** - autonomous coding infrastructure
- **Ralph Loop System** - stateless story execution

### 🎯 Remaining Work
1. **NASAA FRED Scraper** - 7 states (46% market coverage)
2. **California Scraper** - largest market (30% coverage)
3. **FDD Aggregator** - unified interface, deduplication
4. **Integration Tests** - cross-scraper validation
5. **Documentation** - usage examples, API docs

**Current Coverage:** 26% → **Target Coverage:** 90%+

---

## Agent Team Structure

### Team Lead (Coordinator)
**Role:** Orchestrate team, review code, synthesize results, manage shared task list
**Model:** Sonnet 4.5
**Responsibilities:**
- Create and assign tasks to teammates
- Review completed code for quality and consistency
- Resolve conflicts or blockers
- Synthesize findings across teammates
- Final integration and testing

### Teammate 1: NASAA FRED Developer
**Role:** Build multi-state NASAA FRED scraper
**Model:** Sonnet 4.5
**Files:** `tools/nasaa_fred_fdd.py`, `tests/test_nasaa_fred_fdd.py`
**Tasks:**
- Implement NASAA FRED scraper class (~500 lines)
- Multi-state search (NY, IL, MD, VA, WA, ND, RI)
- State provenance tracking (tag each FDD with filing state)
- PDF download with session preservation
- Item 19 extraction
- 90-day caching
- Write comprehensive tests

**Key Challenges:**
- Handle 7 states in one scraper
- Deduplicate cross-state filings
- Track which state each FDD came from

### Teammate 2: California Developer
**Role:** Build California DocQNet scraper
**Model:** Sonnet 4.5
**Files:** `tools/california_fdd.py`, `tests/test_california_fdd.py`
**Tasks:**
- Implement California scraper class (~450 lines)
- Handle slow database (7-10 second waits)
- Implement pagination for multi-page results
- Document type filtering (FDD vs blacklines vs applications)
- PDF download and Item 19 extraction
- 90-day caching
- Write comprehensive tests

**Key Challenges:**
- Slow database requires longer timeouts
- Pagination across multiple result pages
- Filter for FDD documents only (not other doc types)

### Teammate 3: Aggregator Developer
**Role:** Build FDD Aggregator with deduplication
**Model:** Sonnet 4.5
**Files:** `tools/fdd_aggregator.py`, `tests/test_fdd_aggregator.py`
**Tasks:**
- Implement FDDAggregator class (~200 lines)
- `search_all()` - query all scrapers in parallel
- `search_by_states()` - filter by state codes
- Deduplication logic (same franchise, different states)
- Coverage statistics and reporting
- Write integration tests

**Key Challenges:**
- Deduplicate FDDs across states (same franchise, different years/states)
- Determine best version (most recent, most complete)
- Aggregate results cleanly

### Teammate 4: Test Engineer
**Role:** Comprehensive testing and validation
**Model:** Sonnet 4.5
**Files:** `tests/test_integration.py`, `tests/test_end_to_end.py`
**Tasks:**
- Integration tests (all scrapers together)
- End-to-end pipeline tests
- Performance benchmarks
- Error handling and edge cases
- Real-world validation queries
- Success rate tracking (>80% threshold)

**Key Challenges:**
- Test cross-scraper deduplication
- Validate coverage statistics
- Performance testing (response times)

---

## Shared Task List

Tasks are designed to be independent and can be worked on simultaneously:

### Phase 1: Core Scrapers (Parallel)
1. **NASAA FRED Scraper** - Teammate 1
   - [ ] Create skeleton following minnesota_fdd.py pattern
   - [ ] Implement multi-state search form handling
   - [ ] Parse results table with state detection
   - [ ] Implement PDF download
   - [ ] Implement Item 19 extraction
   - [ ] Add 90-day caching
   - [ ] Write unit tests

2. **California Scraper** - Teammate 2
   - [ ] Create skeleton following minnesota_fdd.py pattern
   - [ ] Handle slow database with longer waits
   - [ ] Implement pagination logic
   - [ ] Add document type filtering
   - [ ] Implement PDF download
   - [ ] Implement Item 19 extraction
   - [ ] Add 90-day caching
   - [ ] Write unit tests

### Phase 2: Aggregator (Depends on Phase 1 completion)
3. **FDD Aggregator** - Teammate 3
   - [ ] Create FDDAggregator class
   - [ ] Implement search_all() method
   - [ ] Implement search_by_states() method
   - [ ] Add deduplication logic
   - [ ] Add coverage statistics
   - [ ] Write integration tests

### Phase 3: Testing & Validation (Parallel with Phase 2)
4. **Integration Tests** - Teammate 4
   - [ ] Test all scrapers individually
   - [ ] Test aggregator deduplication
   - [ ] Test cross-state queries
   - [ ] Performance benchmarks
   - [ ] Real-world validation (5 test queries)

---

## Technical Specifications

### Common Pattern (All Scrapers)

All scrapers follow the same structure from `minnesota_fdd.py`:

```python
class StateFDDScraper(Tool):
    """Scrape FDD documents from [State] database"""

    BASE_URL = "https://..."
    CACHE_TTL_DAYS = 90

    def __init__(self):
        super().__init__()
        self.cache_dir = Path("cache/[state]_fdd")
        self.pdf_dir = Path("data/[state]_fdds")

    def search(
        self,
        industry: str,
        max_results: int = 10,
        download_pdfs: bool = True,
        extract_item19: bool = True,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """Unified search API"""
        # 1. Check cache
        # 2. Scrape with Selenium + BeautifulSoup
        # 3. Download PDFs (optional)
        # 4. Extract Item 19 (optional)
        # 5. Save cache
        # 6. Return standardized response

    def _scrape_fdds(self, industry: str, max_results: int) -> List[Dict]:
        """State-specific scraping logic"""

    def _download_pdf(self, fdd: Dict, driver):
        """PDF download with session preservation"""

    def _extract_item19(self, fdd: Dict):
        """PyMuPDF + regex extraction"""
```

### NASAA FRED Specific

**URL:** https://www.nasaaefd.org/Franchise/Search

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
  "states_searched": ["NY", "IL", "MD", "VA", "WA", "ND", "RI"],
  "total_found": 45,
  "results": [
    {
      "franchise_name": "Splash Car Wash",
      "document_id": "NASAA-2024-12345",
      "filing_state": "NY",  # NEW: Track which state
      "fdd_year": 2024,
      "pdf_url": "https://...",
      ...
    }
  ]
}
```

### California Specific

**URL:** https://docqnet.dfpi.ca.gov/search/

**Key Implementation Details:**
- Use longer timeouts (7-10 seconds after search)
- Implement pagination: `_handle_pagination(soup, max_results)`
- Filter documents: `_filter_document_type(results)` to get FDDs only

### FDD Aggregator

**Purpose:** Unified interface to query all scrapers

```python
class FDDAggregator:
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
        """Search ALL FDD databases"""

    def search_by_states(
        self,
        industry: str,
        states: List[str],
        **kwargs
    ) -> Dict[str, Any]:
        """Search specific states only"""

    def deduplicate_results(self, results: Dict) -> List[Dict]:
        """Remove duplicate FDDs across states"""
```

**Deduplication Logic:**
```python
def _is_better_version(new_fdd, existing_fdd):
    """
    Determine which FDD version to keep.

    Priority:
    1. More recent year
    2. Has PDF downloaded
    3. Has Item 19 extracted
    4. Larger state (CA > NY > MN > WI)
    """
```

---

## Anti-Detection (All Scrapers)

All scrapers use consistent anti-detection measures:

```python
# Chrome options
options.add_argument('--headless=new')
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_experimental_option("excludeSwitches", ["enable-automation"])

# CDP overrides
driver.execute_cdp_cmd('Network.setUserAgentOverride', {...})
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

# Rate limiting
time.sleep(random.uniform(2.0, 5.0))  # Between searches
```

---

## Communication Protocol

### Teammate → Lead Messages

**Progress updates:**
```
NASAA FRED Developer → Lead: "Completed multi-state search form handling. Moving to PDF download."
```

**Blockers:**
```
California Developer → Lead: "Hitting timeout on slow database. Need to adjust wait times. Recommend 10s instead of 7s."
```

**Questions:**
```
Aggregator Developer → Lead: "Should deduplication prefer CA over NY if years are equal?"
```

### Lead → Teammate Messages

**Task assignments:**
```
Lead → NASAA FRED Developer: "Start on task #1: Create NASAA FRED scraper skeleton"
```

**Feedback:**
```
Lead → California Developer: "Great work on pagination. Can you add a fallback if no results found?"
```

**Coordination:**
```
Lead → All: "NASAA and California scrapers are complete. Aggregator can start Phase 2."
```

---

## Testing Strategy

### Per-Scraper Tests

Each scraper has unit tests in `tests/test_[state]_fdd.py`:

```python
def test_basic_search():
    """Test basic search functionality"""
    scraper = WisconsinFDDScraper()
    results = scraper.search("car wash", max_results=5)
    assert results['source'] == 'wisconsin_dfi'
    assert results['total_found'] > 0

def test_caching():
    """Test cache hit"""
    scraper = WisconsinFDDScraper()
    results1 = scraper.search("car wash", max_results=5)
    results2 = scraper.search("car wash", max_results=5)
    # Second call should be instant (cached)
```

### Integration Tests

`tests/test_integration.py` tests cross-scraper functionality:

```python
def test_aggregator_all_states():
    """Test searching all states"""
    aggregator = FDDAggregator()
    results = aggregator.search_all("car wash", max_results_per_source=3)
    assert len(results['by_state']) == 4  # MN, WI, CA, NASAA

def test_deduplication():
    """Test deduplication across states"""
    # McDonald's should be in all databases
    aggregator = FDDAggregator()
    results = aggregator.search_all("mcdonald's", max_results_per_source=5)
    deduplicated = aggregator.deduplicate_results(results)
    # Should have far fewer results after dedup
```

### Real-World Validation Queries

5 validation queries to test end-to-end:

1. **"car wash"** - Should find 50+ results across all states
2. **"mcdonald's"** - Should find in all 4 databases, test dedup
3. **"hvac"** - Should find 30+ results
4. **"laundromat"** - Should find 10+ results
5. **"mosquito control"** - Specific franchise test

**Success Criteria:**
- >80% of searches return results
- >90% PDF download success rate
- >60% Item 19 extraction success (not all FDDs have Item 19)
- <5 minutes per 10 results per state
- >50% cache hit rate on repeated queries

---

## Coordination Mechanisms

### Shared Task List
- All agents can see task status
- Agents claim available tasks (file locking prevents conflicts)
- Dependencies tracked automatically (Phase 2 waits for Phase 1)

### Messaging
- Agents send direct messages to each other
- Lead broadcasts to all teammates for coordination
- Automatic delivery (no polling required)

### Quality Gates
- Lead reviews completed code before marking tasks done
- Teammates can request plan approval for complex changes
- Test engineer validates each scraper before integration

---

## Risk Mitigation

**Risk: File conflicts (2 agents editing same file)**
Mitigation: Clear file ownership per agent, no overlap

**Risk: Inconsistent patterns across scrapers**
Mitigation: All follow minnesota_fdd.py reference, lead reviews for consistency

**Risk: Teammate gets stuck or blocked**
Mitigation: Progress updates every 15-20 minutes, lead can reassign work

**Risk: Integration issues when combining scrapers**
Mitigation: Aggregator developer tests with stubs first, real integration at end

**Risk: Agent coordination overhead**
Mitigation: Tasks sized for 30-60 minute completion, minimal inter-dependencies

---

## Success Metrics

### Code Quality
- [ ] All scrapers follow Tool pattern consistently
- [ ] 90-day caching implemented in all scrapers
- [ ] Anti-detection measures in all scrapers
- [ ] Consistent error handling across scrapers

### Coverage
- [ ] 4 total scrapers (MN, WI, CA, NASAA FRED)
- [ ] 10 states covered
- [ ] 90%+ U.S. franchise market coverage
- [ ] 15,000-20,000 unique franchise brands

### Testing
- [ ] >80% search success rate
- [ ] >90% PDF download success rate
- [ ] >60% Item 19 extraction success rate
- [ ] <5 minutes per 10 results
- [ ] All validation queries pass

### Deliverables
- [ ] 3 new scrapers (~1,200 lines)
- [ ] 1 aggregator (~200 lines)
- [ ] Comprehensive test suite (~800 lines)
- [ ] Documentation and examples (~200 lines)
- [ ] **Total: ~2,400 lines of production code**

---

## Timeline Estimate

**With Agent Teams (Parallel):**
- Phase 1 (Scrapers): 1-2 hours (parallel)
- Phase 2 (Aggregator): 30-60 minutes
- Phase 3 (Testing): 30-60 minutes (parallel with Phase 2)
- Integration & Review: 30 minutes
- **Total: 2.5-4 hours**

**Without Agent Teams (Sequential):**
- NASAA FRED: 3-4 hours
- California: 3-4 hours
- Aggregator: 1-2 hours
- Testing: 1-2 hours
- **Total: 10-15 hours**

**Speedup: 3-4x faster with agent teams**

---

## Next Steps

1. **Review this plan** - Approve or provide feedback
2. **Enable agent teams** - ✅ Already enabled in settings.json
3. **Start the team** - Lead spawns 4 teammates
4. **Monitor progress** - Check task list and agent messages
5. **Review code** - Lead synthesizes and validates all work
6. **Integration** - Combine all scrapers with aggregator
7. **Testing** - Run validation queries
8. **Push to GitHub** - Commit to `fdd-scrapers` branch
9. **Create PR** - Merge to main when ready

---

## Reference Files

**Existing Code:**
- `/tools/minnesota_fdd.py` (449 lines) - GOLD STANDARD reference
- `/tools/wisconsin_fdd.py` (378 lines) - Recent implementation
- `/tools/base.py` (72 lines) - Tool base class
- `/tests/test_wisconsin_fdd.py` (374 lines) - Test pattern

**Documentation:**
- `/docs/RESEARCH.md` - State-by-state scrapability assessment
- `/docs/SCRAPER_PRODUCT_SPEC.md` - Product requirements

**Agent Systems:**
- `/agent_loop.py` - Autonomous coding system (Worker/Janitor/Architect)
- `/ralph/` - Stateless story-based execution system

---

## Questions for Review

Before starting the agent team, please confirm:

1. **Team structure**: 4 teammates (NASAA FRED, California, Aggregator, Test Engineer) - OK?
2. **Parallel approach**: Build scrapers simultaneously instead of sequentially - OK?
3. **File ownership**: Each agent owns specific files, no conflicts - OK?
4. **Success criteria**: >80% search success, >90% PDF download, >60% Item 19 extraction - OK?
5. **Timeline**: Expect 2.5-4 hours for completion - OK?

Please review and approve or provide feedback before we start the agent team.
