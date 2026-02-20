# Data Pipeline V0: Implementation Plan

**Goal:** Implement 4 new data sources with multi-agent team

**Timeline:** 2 weeks (agents work in parallel)

**Architect:** Ensure unified architecture, review all implementations

---

## Architecture Standards

All scrapers MUST follow this pattern:

```python
from data_sources.shared.base import Tool

class SourceName(Tool):
    """One-line description"""

    BASE_URL = "https://..."
    CACHE_TTL_DAYS = 90  # or 7 for fast-changing data

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.output_dir = Path("outputs/source_name")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def search(self, industry: str, max_results: int = 10, use_cache: bool = True) -> Dict[str, Any]:
        """
        Main search method - REQUIRED

        Returns:
            {
                "source": "source_name",
                "search_date": "2026-02-19T...",
                "industry": "car wash",
                "total_found": 15,
                "results": [...]
            }
        """
        # 1. Check cache
        cache_key = f"{industry.replace(' ', '_')}_{max_results}"
        if use_cache:
            cached = self.load_cache(cache_key)
            if cached:
                return cached["data"]

        # 2. Scrape/API
        results = self._scrape(industry, max_results)

        # 3. Build response
        response = self._build_response(industry, results)

        # 4. Cache
        if use_cache:
            self.save_cache(cache_key, response, self.CACHE_TTL_DAYS)

        return response

    def _scrape(self, industry: str, max_results: int) -> List[Dict]:
        """Internal scraping/API logic"""
        pass

    def _build_response(self, industry: str, results: List[Dict]) -> Dict:
        """Standardized response format"""
        return {
            "source": "source_name",
            "search_date": datetime.now().isoformat(),
            "industry": industry,
            "total_found": len(results),
            "results": results
        }
```

**Reference Implementation:** `data_sources/fdd/minnesota.py` (449 lines)

---

## Current State

### ✅ Complete
- Google Maps: `data_sources/maps/google_maps.py`
- Minnesota FDD: `data_sources/fdd/minnesota.py`
- Wisconsin FDD: `data_sources/fdd/wisconsin.py`
- BizBuySell: `data_sources/marketplaces/bizbuysell.py`

### 📋 To Implement (4 sources)
1. NASAA FRED FDD (7 states)
2. California FDD
3. Google Reviews + NLP
4. Reddit Sentiment

---

## Agent 1: NASAA FRED Scraper

**File:** `data_sources/fdd/nasaa_fred.py`

**URL:** https://www.nasaaefd.org/Franchise/Search

**Coverage:** 7 states (NY, IL, MD, VA, WA, ND, RI)

### TODO List

- [ ] Copy `data_sources/fdd/minnesota.py` as starting template
- [ ] Update class name to `NASAAFredScraper`
- [ ] Update `BASE_URL = "https://www.nasaaefd.org/Franchise/Search"`
- [ ] Add `STATES = ["NY", "IL", "MD", "VA", "WA", "ND", "RI"]`
- [ ] Implement `search()` method with signature:
  ```python
  def search(
      self,
      industry: str,
      max_results: int = 10,
      states: Optional[List[str]] = None,  # NEW: filter by states
      download_pdfs: bool = False,
      extract_item19: bool = False,
      use_cache: bool = True
  ) -> Dict[str, Any]:
  ```
- [ ] Implement `_scrape_fdds()`:
  - Setup Selenium with anti-detection (copy from Minnesota)
  - Navigate to NASAA FRED search page
  - Fill search form (inspect HTML to find form field IDs)
  - Submit form and wait for results
  - Parse results table with BeautifulSoup
  - **NEW:** Extract `filing_state` for each FDD (which state it's filed in)
  - Return list of FDD dicts
- [ ] Add state filtering logic (if `states` param provided, filter results)
- [ ] Implement PDF download (copy `_download_pdf_with_selenium()` from Minnesota)
- [ ] Implement Item 19 extraction (copy `_extract_item19()` from Minnesota)
- [ ] Update `_build_response()` to include `states_searched` field
- [ ] Create `tests/data_sources/fdd/test_nasaa_fred.py`
- [ ] Write 4 tests:
  - `test_nasaa_fred_search()` - basic search works
  - `test_state_filtering()` - filtering by states works
  - `test_caching()` - cache hit on second call
  - `test_empty_results()` - handles no results gracefully
- [ ] Run tests and verify all pass
- [ ] Test manually: `search("car wash", max_results=5)` returns 5 results with `filing_state` field

**Estimated Time:** 6-8 hours

**Validation Query:** `search("McDonald's", max_results=10)` should find results from multiple states

---

## Agent 2: California FDD Scraper

**File:** `data_sources/fdd/california.py`

**URL:** https://docqnet.dfpi.ca.gov/search/

**Challenge:** Slow database (7-10 sec waits), pagination

### TODO List

- [ ] Copy `data_sources/fdd/minnesota.py` as starting template
- [ ] Update class name to `CaliforniaFDDScraper`
- [ ] Update `BASE_URL = "https://docqnet.dfpi.ca.gov/search/"`
- [ ] Implement `search()` with same signature as Minnesota
- [ ] Implement `_scrape_fdds()`:
  - Setup Selenium with anti-detection
  - Navigate to CA DocQNet search page
  - Fill search form
  - Submit and **wait 7-10 seconds** (CA database is slow)
  - Parse results table
  - **NEW:** Filter for document type = "FDD" (not blacklines, applications)
  - Handle pagination if needed (check for "Next Page" button)
  - Return list of FDD dicts
- [ ] Implement `_handle_pagination()` helper method
- [ ] Implement `_filter_document_type()` to ensure only FDDs
- [ ] Copy PDF download and Item 19 extraction from Minnesota
- [ ] Create `tests/data_sources/fdd/test_california.py`
- [ ] Write 4 tests:
  - `test_california_search()` - basic search works
  - `test_document_filtering()` - only FDDs returned
  - `test_caching()` - cache works
  - `test_pagination()` - can fetch >10 results (requires pagination)
- [ ] Run tests and verify all pass
- [ ] Test manually: `search("car wash", max_results=10)` returns CA FDDs only

**Estimated Time:** 6-8 hours

**Validation Query:** `search("HVAC", max_results=20)` should handle pagination

---

## Agent 3: Google Reviews Scraper

**File:** `data_sources/maps/google_reviews.py`

**API:** Google Places API (reviews endpoint)

**Features:** Fetch reviews, extract themes, sentiment analysis

### TODO List

- [ ] Create new file `data_sources/maps/google_reviews.py`
- [ ] Import: `from data_sources.shared.base import Tool`, `googlemaps`, `textblob`, `collections.Counter`
- [ ] Create class `GoogleReviewsScraper(Tool)`
- [ ] Set `CACHE_TTL_DAYS = 7` (reviews change frequently)
- [ ] Add `__init__(self, api_key: str, **kwargs)` - store Google API key
- [ ] Initialize Google Maps client: `self.client = googlemaps.Client(key=api_key)`
- [ ] Implement `search()` method with signature:
  ```python
  def search(
      self,
      place_id: str,  # Google Place ID (from google_maps.py)
      extract_themes: bool = True,
      use_cache: bool = True
  ) -> Dict[str, Any]:
  ```
- [ ] Fetch reviews: `self.client.place(place_id, fields=['reviews', 'rating'])`
- [ ] Implement `_extract_themes()`:
  - Combine all review texts
  - Remove stopwords ('the', 'a', 'is', 'was', etc.)
  - Count word frequency with `Counter`
  - Return top 20 words
- [ ] Implement `_analyze_sentiment()`:
  - Use TextBlob on each review: `TextBlob(text).sentiment.polarity`
  - Calculate average sentiment (-1 to 1)
  - Count positive/neutral/negative reviews
- [ ] Build response with format:
  ```json
  {
    "source": "google_reviews",
    "place_id": "...",
    "total_reviews": 150,
    "average_rating": 4.5,
    "themes": {"reliable": 89, "professional": 67, ...},
    "sentiment": {"average": 0.65, "positive": 120, "neutral": 20, "negative": 10},
    "reviews": [...]
  }
  ```
- [ ] Create `tests/data_sources/maps/test_google_reviews.py`
- [ ] Write 4 tests:
  - `test_google_reviews_fetch()` - fetches reviews for place_id
  - `test_theme_extraction()` - themes dict returned
  - `test_sentiment_analysis()` - sentiment scores valid (-1 to 1)
  - `test_caching()` - cache works
- [ ] Run tests with test API key
- [ ] Test manually: use place_id from Google Maps search

**Dependencies:** `googlemaps`, `textblob`, `nltk`

**Estimated Time:** 6-8 hours

**Validation Query:** Get reviews for "Cool Air HVAC Los Angeles" place_id

---

## Agent 4: Reddit Sentiment Scraper

**File:** `data_sources/sentiment/reddit.py`

**API:** Reddit API via PRAW

**Subreddits:** r/sweatystartup, r/smallbusiness, r/Entrepreneur

### TODO List

- [ ] Create new file `data_sources/sentiment/reddit.py`
- [ ] Import: `from data_sources.shared.base import Tool`, `praw`, `textblob`
- [ ] Create class `RedditSentimentScraper(Tool)`
- [ ] Set `CACHE_TTL_DAYS = 7`
- [ ] Add `SUBREDDITS = ['sweatystartup', 'smallbusiness', 'Entrepreneur']`
- [ ] Add `__init__(self, client_id: str, client_secret: str, user_agent: str, **kwargs)`
- [ ] Initialize PRAW client:
  ```python
  self.reddit = praw.Reddit(
      client_id=client_id,
      client_secret=client_secret,
      user_agent=user_agent
  )
  ```
- [ ] Implement `search()` method with signature:
  ```python
  def search(
      self,
      industry: str,
      max_posts: int = 50,
      days_back: int = 90,
      extract_quotes: bool = True,
      use_cache: bool = True
  ) -> Dict[str, Any]:
  ```
- [ ] Implement `_scrape_posts()`:
  - Loop through each subreddit
  - Search by industry keyword: `subreddit.search(industry, limit=...)`
  - Filter by date (only posts from last `days_back` days)
  - Extract: title, text, url, score, num_comments, subreddit
  - Return list of post dicts
- [ ] Implement `_analyze_sentiment()`:
  - Use TextBlob on each post title + text
  - Calculate average sentiment
  - Count positive/neutral/negative posts
- [ ] Implement `_extract_quotes()`:
  - Find posts mentioning financial keywords ('revenue', 'profit', 'margin', '$')
  - Sort by score (upvotes)
  - Return top 5 quotes
- [ ] Build response with format:
  ```json
  {
    "source": "reddit_sentiment",
    "industry": "HVAC",
    "total_posts": 35,
    "subreddits_searched": ["sweatystartup", "smallbusiness", "Entrepreneur"],
    "sentiment": {"average": 0.45, "positive": 25, "neutral": 8, "negative": 2},
    "top_quotes": [...],
    "posts": [...]
  }
  ```
- [ ] Create `tests/data_sources/sentiment/test_reddit.py`
- [ ] Write 4 tests:
  - `test_reddit_search()` - searches and returns posts
  - `test_sentiment_analysis()` - sentiment valid
  - `test_quote_extraction()` - quotes extracted
  - `test_caching()` - cache works
- [ ] Run tests with test Reddit API credentials
- [ ] Test manually: `search("HVAC", max_posts=20)`

**Dependencies:** `praw`, `textblob`

**Estimated Time:** 6-8 hours

**Validation Query:** `search("car wash", max_posts=50)` should find relevant posts

---

## Architect Tasks (Me)

### Before Implementation
- [ ] Review this plan with user
- [ ] Create agent team
- [ ] Assign one source per agent
- [ ] Provide architecture standards to all agents

### During Implementation
- [ ] Review each agent's code before marking complete
- [ ] Ensure all follow Tool base class pattern
- [ ] Verify consistent response formats:
  ```json
  {
    "source": "source_name",
    "search_date": "ISO timestamp",
    "industry": "search term",
    "total_found": 0,
    "results": []
  }
  ```
- [ ] Verify caching implementation matches base class
- [ ] Ensure proper error handling (graceful degradation)
- [ ] Check all tests pass

### After All Agents Complete
- [ ] Create FDD Aggregator (`data_sources/fdd/aggregator.py`)
- [ ] Implement integration test (`tests/integration/test_pipeline.py`)
- [ ] Verify BizBuySell scraper still works
- [ ] Run full validation queries:
  - "car wash" across all sources
  - "HVAC" across all sources
  - "McDonald's" for FDD sources
- [ ] Update documentation
- [ ] Add dependencies to `pyproject.toml`:
  ```toml
  dependencies = [
      "googlemaps>=4.10.0",
      "praw>=7.7.0",
      "textblob>=0.17.0",
      "nltk>=3.8.0"
  ]
  ```

---

## FDD Aggregator (After Agents Complete)

**File:** `data_sources/fdd/aggregator.py`

**Purpose:** Unified interface to query all 4 FDD sources

### TODO List

- [ ] Create class `FDDAggregator` (does NOT inherit from Tool)
- [ ] Initialize all 4 FDD scrapers in `__init__()`:
  ```python
  self.scrapers = {
      'minnesota': MinnesotaFDDScraper(),
      'wisconsin': WisconsinFDDScraper(),
      'nasaa_fred': NASAAFredScraper(),
      'california': CaliforniaFDDScraper()
  }
  ```
- [ ] Implement `search_all()` method:
  - Loop through all scrapers
  - Call `search()` on each
  - Collect all results
  - Deduplicate by (franchise_name, fdd_year)
  - Return combined results
- [ ] Implement `_deduplicate()`:
  - Keep most complete version (has PDF > has Item 19 > larger state)
- [ ] Create `tests/data_sources/fdd/test_aggregator.py`
- [ ] Write 2 tests:
  - `test_aggregator_all_states()` - queries all 4 states
  - `test_deduplication()` - removes duplicates

**Estimated Time:** 4-6 hours

---

## Integration Testing

**File:** `tests/integration/test_pipeline.py`

### TODO List

- [ ] Create test that searches "car wash" across all 6 sources
- [ ] Verify each source returns data
- [ ] Verify response formats are consistent
- [ ] Verify caching works across sources
- [ ] Test error handling (one source fails, others continue)

---

## Timeline

**Parallel Execution (Agents work simultaneously):**

| Week | Agents | Task | Output |
|------|--------|------|--------|
| 1 | Agent 1 | NASAA FRED scraper | `data_sources/fdd/nasaa_fred.py` + tests |
| 1 | Agent 2 | California scraper | `data_sources/fdd/california.py` + tests |
| 1 | Agent 3 | Google Reviews scraper | `data_sources/maps/google_reviews.py` + tests |
| 1 | Agent 4 | Reddit scraper | `data_sources/sentiment/reddit.py` + tests |
| 2 | Architect | FDD Aggregator | `data_sources/fdd/aggregator.py` + tests |
| 2 | Architect | Integration tests | Verify all 6 sources work together |
| 2 | Architect | Documentation | Update README, deps |

**Total:** 2 weeks (agents work in parallel, not sequential)

---

## Success Criteria

### Code Quality
- ✅ All scrapers inherit from `Tool` base class
- ✅ All implement `search()` method with consistent signature
- ✅ All return standardized response format
- ✅ All use caching via `load_cache()` / `save_cache()`
- ✅ All handle errors gracefully (no crashes)

### Testing
- ✅ Every scraper has 4 tests minimum
- ✅ All tests pass
- ✅ Integration test passes

### Functionality
- ✅ Can search "car wash" across all 6 sources
- ✅ Results returned in <5 minutes (with caching)
- ✅ 90%+ success rate on validation queries

### Data Coverage
- ✅ 10 states of FDD data (via aggregator)
- ✅ Review sentiment for any business
- ✅ Market pulse from Reddit

---

## Validation Queries (Run After All Complete)

Test all sources with:

1. **"car wash"** - Should find 20+ FDDs, 100+ businesses, reviews, Reddit posts
2. **"HVAC"** - Should find 30+ FDDs, 200+ businesses
3. **"McDonald's"** - Should find in all FDD databases
4. **"laundromat"** - Should find 10+ FDDs
5. **"plumbing"** - Should find sentiment data

**Success =** 4/5 queries return useful data from all sources

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| NASAA FRED different form structure | Inspect HTML, try common patterns, debug screenshots |
| California too slow | Increase wait times (7-10 sec), aggressive caching |
| Google API rate limits | 7-day cache TTL, limit requests |
| Reddit API rate limits | Limit to 50 posts per search, cache results |

---

## Dependencies to Install

```bash
pip install googlemaps praw textblob nltk
python -m textblob.download_corpora
```

Add to `pyproject.toml`:
```toml
dependencies = [
    "googlemaps>=4.10.0",
    "praw>=7.7.0",
    "textblob>=0.17.0",
    "nltk>=3.8.0"
]
```

---

**Status:** Ready for review
**Last Updated:** 2026-02-19
**Next Step:** Review plan → Create agent team → Start parallel implementation
