# Data Pipeline V0: Refactoring Plan

**Status:** Review Only - DO NOT IMPLEMENT YET

---

## Executive Summary

The data pipeline implementation is **functionally complete and tested** (44/44 tests passing), but has significant **code quality issues** that should be addressed before production:

- **~1,200 lines of duplicated code** across 4 FDD scrapers
- **Inconsistent patterns** (custom caching vs base class)
- **Poor logging** (print statements instead of logging)
- **Large files** (California: 866 lines, NASAA: 703 lines)
- **Testing gaps** (no end-to-end validation tests)

**Estimated refactoring effort:** 1-2 days
**Risk:** Low (tests ensure no regressions)

---

## Critical Issues

### 1. **MASSIVE CODE DUPLICATION** ⚠️ **HIGH PRIORITY**

**Problem:** All 4 FDD scrapers duplicate ~300 lines of Selenium setup, PDF download, and Item 19 extraction.

**Evidence:**
```python
# Duplicated in minnesota.py, wisconsin.py, nasaa_fred.py, california.py

# Selenium setup (~40 lines)
options = Options()
options.add_argument('--headless=new')
options.add_argument('--disable-blink-features=AutomationControlled')
# ... 30 more lines

# Chrome driver setup (~10 lines)
driver = webdriver.Chrome(...)
driver.execute_cdp_cmd('Network.setUserAgentOverride', {...})
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

# PDF download (~80 lines)
def _download_pdf_with_selenium(self, fdd, driver):
    # Identical logic in all 4 scrapers

# Item 19 extraction (~100 lines)
def _extract_item19(self, fdd):
    # Identical logic in all 4 scrapers
```

**Impact:**
- Hard to maintain (fix bug in 4 places)
- Inconsistent behavior across scrapers
- Violates DRY principle

**Solution:** Create `FDDScraperBase` class with shared Selenium, PDF, and Item 19 logic.

---

### 2. **INCONSISTENT CACHING** ⚠️ **HIGH PRIORITY**

**Problem:** Wisconsin and California implement custom caching instead of using `Tool` base class.

**Evidence:**
```python
# Wisconsin/California - custom implementation
def _get_cache_key(self, ...):
    return hashlib.md5(params.encode()).hexdigest()

def _load_cache(self, cache_key):
    # Custom JSON loading with TTL check

# Minnesota/NASAA - use base class
cached = self.load_cache(cache_key)
if cached:
    return cached["data"]
```

**Impact:**
- Two different caching systems in same codebase
- Wisconsin/California cache format incompatible with base class
- Harder to test

**Solution:** Unify all scrapers to use `Tool.load_cache()` / `Tool.save_cache()`.

---

### 3. **POOR LOGGING** ⚠️ **MEDIUM PRIORITY**

**Problem:** Using `print()` statements everywhere instead of proper logging.

**Evidence:**
```python
print(f"🔍 Searching Minnesota CARDS for: {industry}")
print(f"   Max results: {max_results}")
print(f"✅ Using cached results from {cached['cached_at']}")
print(f"⚠️  No FDDs found")
```

**Impact:**
- Can't control log levels (debug, info, error)
- Can't redirect logs to files
- Hard to debug production issues
- Emojis may break in some terminals

**Solution:** Use Python `logging` module with proper levels.

```python
import logging

logger = logging.getLogger(__name__)

logger.info(f"Searching Minnesota CARDS for: {industry}")
logger.debug(f"Max results: {max_results}")
logger.warning("No FDDs found")
```

---

### 4. **LARGE FILES** ⚠️ **MEDIUM PRIORITY**

**Problem:** California (866 lines) and NASAA (703 lines) are too large.

**File sizes:**
```
866 lines - data_sources/fdd/california.py
703 lines - data_sources/fdd/nasaa_fred.py
449 lines - data_sources/fdd/minnesota.py
402 lines - data_sources/fdd/wisconsin.py
```

**Impact:**
- Hard to navigate and understand
- Violates Single Responsibility Principle
- Long files indicate lack of abstraction

**Solution:** Extract shared logic to base classes and mixins.

---

### 5. **NO CONFIGURATION MANAGEMENT** ⚠️ **MEDIUM PRIORITY**

**Problem:** Constants scattered throughout code.

**Evidence:**
```python
# Duplicated in every FDD scraper
CACHE_TTL_DAYS = 90
time.sleep(5)  # Magic number
time.sleep(10)  # Different wait time in California
'--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)...'  # Duplicated
```

**Impact:**
- Hard to change wait times globally
- Inconsistent timeouts across scrapers
- Can't easily configure per-environment

**Solution:** Create `data_sources/shared/config.py` with centralized settings.

```python
# data_sources/shared/config.py
from dataclasses import dataclass

@dataclass
class ScraperConfig:
    CHROME_USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)..."
    DEFAULT_WAIT_SECONDS = 5
    SLOW_WAIT_SECONDS = 10  # For CA DocQNet
    FDD_CACHE_TTL_DAYS = 90
    SENTIMENT_CACHE_TTL_DAYS = 7
```

---

### 6. **MINIMAL BASE CLASS** ⚠️ **MEDIUM PRIORITY**

**Problem:** `Tool` base class only provides caching, nothing else.

**Current state:**
```python
class Tool(ABC):
    def __init__(self, cache_dir): ...
    def load_cache(self): ...
    def save_cache(self): ...
    @abstractmethod
    def search(self): ...
```

**Missing:**
- Logging setup
- Configuration management
- Retry logic
- Rate limiting
- Error handling helpers

**Solution:** Expand base class with more utilities.

---

### 7. **NO DEPENDENCY INJECTION** ⚠️ **LOW PRIORITY**

**Problem:** Hard-coded dependencies make testing difficult.

**Evidence:**
```python
# In every FDD scraper
driver = webdriver.Chrome(service=service, options=options)
# Can't inject mock driver for testing
```

**Impact:**
- Integration tests require real Selenium
- Slow tests (can't mock Selenium easily)
- Hard to test edge cases

**Solution:** Accept optional driver parameter for testing.

```python
def _scrape_fdds(self, industry: str, max_results: int, driver=None):
    if driver is None:
        driver = self._create_driver()
```

---

### 8. **INCONSISTENT ERROR HANDLING** ⚠️ **LOW PRIORITY**

**Problem:** Mix of silent failures, print statements, and exceptions.

**Evidence:**
```python
# Minnesota - print and continue
except Exception as e:
    print(f"❌ Failed: {e}")
    import traceback
    traceback.print_exc()

# Wisconsin - silent return
except Exception as e:
    return None

# NASAA - custom error dict
except Exception as e:
    return {"error": str(e)}
```

**Impact:**
- Unpredictable error behavior
- Hard to debug production issues
- Some errors swallowed silently

**Solution:** Define custom exceptions and handle consistently.

```python
# data_sources/shared/errors.py
class ScraperError(Exception):
    """Base exception for scrapers"""
    pass

class PDFDownloadError(ScraperError):
    """Failed to download PDF"""
    pass

class Item19ExtractionError(ScraperError):
    """Failed to extract Item 19"""
    pass
```

---

### 9. **TESTING GAPS** ⚠️ **LOW PRIORITY**

**Problem:** No end-to-end validation tests with real websites.

**Current tests:** All use mocks (good for unit tests, but no real validation)

**Missing:**
- Smoke tests that hit real websites (with VCR.py for caching)
- Performance tests (check scraping speed)
- Data quality tests (validate extracted fields)

**Solution:** Add validation test suite (run manually, not in CI).

```python
# tests/validation/test_fdd_scrapers_live.py
@pytest.mark.validation  # Skip in CI
def test_minnesota_live():
    scraper = MinnesotaFDDScraper()
    results = scraper.search("McDonald's", max_results=1, use_cache=False)
    assert results["total_found"] > 0
    assert "franchise_name" in results["results"][0]
```

---

### 10. **TYPE HINTS INCONSISTENCY** ⚠️ **LOW PRIORITY**

**Problem:** Some files use type hints, others don't.

**Evidence:**
```python
# Good - minnesota.py
def search(
    self,
    industry: str,
    max_results: int = 10,
    download_pdfs: bool = True,
    use_cache: bool = True
) -> Dict[str, Any]:

# Missing - some helper methods
def _scrape_fdds(self, industry, max_results):  # No type hints
```

**Impact:**
- Harder for IDE autocomplete
- No static type checking
- Inconsistent code style

**Solution:** Add type hints to all public methods and helpers.

---

## Proposed Refactoring

### Phase 1: Extract Shared FDD Base Class (HIGHEST IMPACT)

**Goal:** Eliminate ~1,200 lines of duplication

**Create:** `data_sources/fdd/base.py`

```python
"""Base class for all FDD scrapers"""

from abc import abstractmethod
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
# ... imports

from data_sources.shared.base import Tool
from data_sources.shared.config import ScraperConfig

logger = logging.getLogger(__name__)


class FDDScraperBase(Tool):
    """Base class for all FDD scrapers with shared Selenium/PDF/Item19 logic"""

    CACHE_TTL_DAYS = ScraperConfig.FDD_CACHE_TTL_DAYS

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.output_dir = Path("outputs/fdds")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    # ==================== SHARED SELENIUM SETUP ====================

    def _create_driver(self) -> webdriver.Chrome:
        """Create Chrome driver with anti-detection (SHARED LOGIC)"""
        options = self._get_chrome_options()
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        self._apply_anti_detection(driver)
        return driver

    def _get_chrome_options(self) -> Options:
        """Get Chrome options with anti-detection (SHARED LOGIC)"""
        options = Options()
        options.add_argument('--headless=new')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument(f'--user-agent={ScraperConfig.CHROME_USER_AGENT}')
        # ... all common options
        return options

    def _apply_anti_detection(self, driver: webdriver.Chrome):
        """Apply CDP anti-detection measures (SHARED LOGIC)"""
        driver.execute_cdp_cmd('Network.setUserAgentOverride', {
            "userAgent": ScraperConfig.CHROME_USER_AGENT
        })
        driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )

    # ==================== SHARED PDF DOWNLOAD ====================

    def _download_pdf_with_selenium(self, fdd: Dict, driver: webdriver.Chrome):
        """Download PDF using Selenium CDP (SHARED LOGIC)"""
        # Exact logic from Minnesota scraper
        # ~80 lines of shared code
        pass

    # ==================== SHARED ITEM 19 EXTRACTION ====================

    def _extract_item19(self, fdd: Dict):
        """Extract Item 19 financial data from PDF (SHARED LOGIC)"""
        # Exact logic from Minnesota scraper
        # ~100 lines of shared code
        pass

    def _find_item19_section(self, doc) -> Optional[str]:
        """Find Item 19 section in PDF (SHARED LOGIC)"""
        pass

    # ==================== ABSTRACT METHODS (STATE-SPECIFIC) ====================

    @abstractmethod
    def _scrape_fdds(self, industry: str, max_results: int) -> List[Dict]:
        """State-specific scraping logic - MUST BE IMPLEMENTED BY SUBCLASS"""
        pass

    # ==================== SHARED SEARCH TEMPLATE ====================

    def search(
        self,
        industry: str,
        max_results: int = 10,
        download_pdfs: bool = False,
        extract_item19: bool = False,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Template method for FDD search (SHARED LOGIC + STATE-SPECIFIC)

        Uses Template Method pattern:
        1. Check cache (shared)
        2. Call _scrape_fdds() (state-specific)
        3. Download PDFs (shared)
        4. Extract Item 19 (shared)
        5. Save cache (shared)
        """
        logger.info(f"Searching {self.__class__.__name__} for: {industry}")

        cache_key = f"fdd_{industry.replace(' ', '_')}_{max_results}"

        # 1. Check cache
        if use_cache:
            cached = self.load_cache(cache_key)
            if cached:
                logger.info(f"Cache hit from {cached['cached_at']}")
                return cached["data"]

        # 2. Scrape (state-specific - delegates to subclass)
        results = self._scrape_fdds(industry, max_results)

        if not results:
            logger.warning("No FDDs found")
            return self._build_response(industry, [])

        logger.info(f"Found {len(results)} FDDs")

        # 3. Download PDFs (shared)
        if download_pdfs:
            self._download_all_pdfs(results)

        # 4. Extract Item 19 (shared)
        if extract_item19:
            self._extract_all_item19(results)

        # 5. Build response and cache
        response = self._build_response(industry, results)

        if use_cache:
            self.save_cache(cache_key, response, self.CACHE_TTL_DAYS)

        return response
```

**Then refactor scrapers:**

```python
# data_sources/fdd/minnesota.py - AFTER REFACTORING
from data_sources.fdd.base import FDDScraperBase

class MinnesotaFDDScraper(FDDScraperBase):
    """Scrape Minnesota CARDS - only state-specific logic"""

    BASE_URL = "https://www.cards.commerce.state.mn.us/"

    def _scrape_fdds(self, industry: str, max_results: int) -> List[Dict]:
        """Minnesota-specific scraping logic (ONLY THIS IS UNIQUE)"""
        driver = self._create_driver()  # Use base class method
        try:
            driver.get(f"{self.BASE_URL}franchise-registrations")
            # ... Minnesota-specific form filling and parsing
            # All Selenium setup, PDF download, Item 19 handled by base class
        finally:
            driver.quit()
```

**Impact:**
- Reduces Minnesota from 449 → ~150 lines (66% reduction)
- Reduces Wisconsin from 402 → ~120 lines (70% reduction)
- Reduces NASAA from 703 → ~200 lines (72% reduction)
- Reduces California from 866 → ~250 lines (71% reduction)
- **Total: ~1,200 lines eliminated**

---

### Phase 2: Unified Configuration

**Create:** `data_sources/shared/config.py`

```python
"""Centralized configuration for all scrapers"""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class ScraperConfig:
    """Global scraper configuration"""

    # Chrome/Selenium settings
    CHROME_USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36"
    CHROME_HEADLESS = True
    DEFAULT_WAIT_SECONDS = 5
    SLOW_WAIT_SECONDS = 10  # For CA DocQNet

    # Cache settings
    FDD_CACHE_TTL_DAYS = 90
    SENTIMENT_CACHE_TTL_DAYS = 7
    REVIEWS_CACHE_TTL_DAYS = 7

    # Output directories
    OUTPUT_DIR = "outputs"
    FDD_OUTPUT_DIR = "outputs/fdds"
    CACHE_DIR = "outputs/cache"

    # API Keys (from env vars)
    GOOGLE_MAPS_API_KEY: Optional[str] = os.getenv("GOOGLE_MAPS_API_KEY")
    REDDIT_CLIENT_ID: Optional[str] = os.getenv("REDDIT_CLIENT_ID")
    REDDIT_CLIENT_SECRET: Optional[str] = os.getenv("REDDIT_CLIENT_SECRET")

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

**Usage:**
```python
from data_sources.shared.config import ScraperConfig

options.add_argument(f'--user-agent={ScraperConfig.CHROME_USER_AGENT}')
time.sleep(ScraperConfig.DEFAULT_WAIT_SECONDS)
```

---

### Phase 3: Proper Logging

**Update:** All scrapers to use `logging` module

**Before:**
```python
print(f"🔍 Searching for: {industry}")
print(f"✅ Found {len(results)} FDDs")
print(f"❌ Failed: {e}")
```

**After:**
```python
import logging

logger = logging.getLogger(__name__)

logger.info(f"Searching for: {industry}")
logger.info(f"Found {len(results)} FDDs")
logger.error(f"Failed: {e}", exc_info=True)
```

**Benefits:**
- Can set `LOG_LEVEL=DEBUG` for verbose output
- Logs go to files in production
- Better formatting and timestamps
- Stack traces on errors

---

### Phase 4: Custom Exceptions

**Create:** `data_sources/shared/errors.py`

```python
"""Custom exceptions for Scout scrapers"""

class ScoutError(Exception):
    """Base exception for all Scout errors"""
    pass

class ScraperError(ScoutError):
    """Base exception for scraper errors"""
    pass

class SeleniumSetupError(ScraperError):
    """Failed to setup Selenium driver"""
    pass

class FormNotFoundError(ScraperError):
    """Search form not found on page"""
    pass

class NoResultsError(ScraperError):
    """Search returned no results"""
    pass

class PDFDownloadError(ScraperError):
    """Failed to download PDF"""
    def __init__(self, url: str, reason: str):
        self.url = url
        self.reason = reason
        super().__init__(f"Failed to download {url}: {reason}")

class Item19ExtractionError(ScraperError):
    """Failed to extract Item 19 from PDF"""
    pass

class CacheError(ScoutError):
    """Cache operation failed"""
    pass

class APIError(ScoutError):
    """External API error"""
    def __init__(self, service: str, status_code: int, message: str):
        self.service = service
        self.status_code = status_code
        super().__init__(f"{service} API error ({status_code}): {message}")
```

**Usage:**
```python
from data_sources.shared.errors import PDFDownloadError, NoResultsError

if not results:
    raise NoResultsError(f"No FDDs found for '{industry}'")

if response.status_code != 200:
    raise PDFDownloadError(url, f"HTTP {response.status_code}")
```

---

### Phase 5: Enhanced Base Class

**Update:** `data_sources/shared/base.py`

```python
"""Enhanced base class for all data collection tools"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pathlib import Path
import json
import logging
from datetime import datetime

from data_sources.shared.config import ScraperConfig
from data_sources.shared.errors import CacheError

logger = logging.getLogger(__name__)


class Tool(ABC):
    """Enhanced base class for all data collection tools"""

    def __init__(self, cache_dir: Optional[Path] = None):
        self.cache_dir = cache_dir or Path(ScraperConfig.CACHE_DIR)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Setup logging for this tool
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def search(self, **kwargs) -> Dict[str, Any]:
        """Execute search and return standardized data"""
        pass

    # ==================== CACHING ====================

    def load_cache(self, cache_key: str) -> Optional[Dict]:
        """Load cached data if available and not expired"""
        cache_file = self.cache_dir / f"{cache_key}.json"

        if not cache_file.exists():
            self.logger.debug(f"Cache miss: {cache_key}")
            return None

        try:
            with open(cache_file, 'r') as f:
                cached = json.load(f)

            if self._is_cache_expired(cached):
                self.logger.debug(f"Cache expired: {cache_key}")
                return None

            self.logger.info(f"Cache hit: {cache_key}")
            return cached

        except Exception as e:
            self.logger.error(f"Cache load error: {e}")
            raise CacheError(f"Failed to load cache: {e}")

    def save_cache(self, cache_key: str, data: Dict, ttl_days: int):
        """Save data to cache with expiration"""
        cache_file = self.cache_dir / f"{cache_key}.json"

        cached_data = {
            "cached_at": datetime.now().isoformat(),
            "ttl_days": ttl_days,
            "data": data
        }

        try:
            with open(cache_file, 'w') as f:
                json.dump(cached_data, f, indent=2, default=str)

            self.logger.info(f"Cached: {cache_key} (TTL: {ttl_days} days)")

        except Exception as e:
            self.logger.error(f"Cache save error: {e}")
            raise CacheError(f"Failed to save cache: {e}")

    def _is_cache_expired(self, cached: Dict) -> bool:
        """Check if cached data is expired"""
        cached_at = datetime.fromisoformat(cached["cached_at"])
        ttl_days = cached["ttl_days"]
        age_days = (datetime.now() - cached_at).days
        return age_days > ttl_days

    # ==================== UTILITIES ====================

    def save(self, data: Dict, filename: str) -> Path:
        """Save raw data to JSON file"""
        output_path = Path(ScraperConfig.OUTPUT_DIR) / "raw_data" / filename
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)

        self.logger.info(f"Saved data: {output_path}")
        return output_path
```

---

## File Structure After Refactoring

```
scout/
├── data_sources/
│   ├── fdd/
│   │   ├── base.py                # NEW - FDDScraperBase
│   │   ├── minnesota.py           # REDUCED 449 → ~150 lines
│   │   ├── wisconsin.py           # REDUCED 402 → ~120 lines
│   │   ├── nasaa_fred.py          # REDUCED 703 → ~200 lines
│   │   ├── california.py          # REDUCED 866 → ~250 lines
│   │   └── aggregator.py          # UNCHANGED
│   │
│   ├── maps/
│   │   ├── google_maps.py         # UNCHANGED
│   │   └── google_reviews.py      # UPDATE logging
│   │
│   └── sentiment/
│       └── reddit.py              # UPDATE logging
│
├── data_sources/shared/           # Tooling (base, config, errors)
└── scout/shared/                  # App-level utilities (errors, export, parsing)
│
└── tests/
    ├── unit/                      # RENAME from tests/data_sources/
    ├── integration/               # KEEP as-is
    └── validation/                # NEW - Manual validation tests
        └── test_fdd_live.py       # NEW
```

---

## Implementation Plan

### Week 1: Core Refactoring (3-4 days)

**Day 1:**
- [ ] Create `data_sources/shared/config.py` with centralized settings
- [ ] Create `data_sources/shared/errors.py` with custom exceptions
- [ ] Update `data_sources/shared/base.py` with enhanced logging and utilities

**Day 2:**
- [ ] Create `data_sources/fdd/base.py` with `FDDScraperBase`
- [ ] Extract all shared Selenium logic
- [ ] Extract PDF download logic
- [ ] Extract Item 19 extraction logic

**Day 3:**
- [ ] Refactor Minnesota scraper to use base class
- [ ] Refactor Wisconsin scraper to use base class
- [ ] Run tests - ensure no regressions

**Day 4:**
- [ ] Refactor NASAA scraper to use base class
- [ ] Refactor California scraper to use base class
- [ ] Run tests - ensure no regressions

### Week 2: Polish & Validation (1-2 days)

**Day 5:**
- [ ] Update all scrapers to use `logging` instead of `print`
- [ ] Add type hints to all public methods
- [ ] Update docstrings

**Day 6:**
- [ ] Create validation test suite (manual tests with real websites)
- [ ] Run full test suite (should still be 44/44 passing)
- [ ] Update documentation

---

## Testing Strategy

**Critical:** All existing tests must pass after refactoring.

**Regression testing:**
```bash
# Before refactoring - baseline
pytest tests/ -v > baseline.txt

# After each phase
pytest tests/ -v > after_phase1.txt
diff baseline.txt after_phase1.txt  # Should be identical

# Final validation
pytest tests/ -v --cov=sources --cov=core
# Must show 44/44 passing, coverage >80%
```

**Manual validation:**
```bash
# Test each scraper with real website
python -c "
from data_sources.fdd.minnesota import MinnesotaFDDScraper
scraper = MinnesotaFDDScraper()
results = scraper.search('McDonald\\'s', max_results=1, use_cache=False)
print(f'Found: {results[\"total_found\"]} FDDs')
"
```

---

## Risks & Mitigation

### Risk 1: Breaking existing tests
**Probability:** Medium
**Impact:** High
**Mitigation:**
- Refactor incrementally (one scraper at a time)
- Run tests after each change
- Git commit after each successful refactor

### Risk 2: Performance regression
**Probability:** Low
**Impact:** Medium
**Mitigation:**
- Benchmark before/after (measure search time)
- Caching should remain fast
- Selenium overhead unchanged

### Risk 3: Scope creep
**Probability:** High
**Impact:** Medium
**Mitigation:**
- Stick to plan (don't add new features)
- Focus on refactoring, not new functionality
- Time-box: max 2 days

---

## Success Metrics

**Code quality:**
- ✅ Reduce total lines by ~1,200 (eliminate duplication)
- ✅ All files <300 lines
- ✅ Single caching implementation (no custom implementations)
- ✅ Consistent logging (no print statements)
- ✅ Centralized configuration (no magic numbers)

**Functional:**
- ✅ All 44 tests still passing
- ✅ No performance regression (search time ±10%)
- ✅ Manual validation passes for all scrapers

**Maintainability:**
- ✅ Fix bug in one place (base class) affects all scrapers
- ✅ Add new FDD scraper in <100 lines (just state-specific logic)
- ✅ Clear separation: base class (shared) vs scrapers (state-specific)

---

## Recommendation

**Proceed with refactoring?** ✅ **YES**

**Rationale:**
1. **High impact** - Eliminates ~1,200 lines of duplication
2. **Low risk** - Tests ensure no regressions
3. **Quick** - 1-2 days with clear plan
4. **Foundation** - Sets up clean architecture for future scrapers

**Next steps:**
1. Review this plan
2. Approve refactoring approach
3. Execute Week 1 (core refactoring)
4. Validate and merge

---

**Created:** 2026-02-20
**Status:** Awaiting approval
**Estimated effort:** 1-2 days
**Risk level:** Low
