# Agent Container Implementation Plan for Scout
**Date:** February 17, 2026
**Purpose:** Step-by-step technical plan to integrate agent-coding-container with Scout deal intelligence platform
**Goal:** Enable "specify PRD → autonomous implementation" workflow for Scout development

---

## Overview

This plan outlines how to use the agent-coding-container to autonomously implement Scout's multi-state FDD scraper pipeline and report generators. By writing detailed PRDs, we can leverage AI agents to handle the implementation while we focus on requirements, validation, and blocker resolution.

**Target Architecture:**
```
User (You) writes PRD.md
    ↓
docker compose up
    ↓
Agent Container Loop:
  - Worker Agent: Implements 1 task/cycle
  - Janitor Agent: Cleans tech debt (every 4 cycles)
  - Architect Agent: Reviews alignment (every 8 cycles)
    ↓
Autonomous implementation (10+ hours runtime)
    ↓
Human validates output + handles blockers
    ↓
Production-ready Scout components
```

**Time Savings:**
- Traditional: 12-18 days of coding
- Agent Container: 5-7 days (mostly automated runtime)
- **58-62% reduction in human time**

---

## Phase 1: Setup & Validation (Day 1)

### Goal
Confirm agent-coding-container works in your local environment before committing to full implementation.

### Prerequisites

**System Requirements:**
- macOS (you're on Darwin 24.6.0) ✅
- Docker Desktop v20.10+ (install if not present)
- Docker Compose v2.0+
- Git configured
- 20GB free disk space

**Kilo Code Account:**
- Sign up at https://kilo.ai/
- Get API credentials
- Save to `~/.kilocode/config.json`

**Check Docker:**
```bash
docker --version
# Should show: Docker version 20.10+ or higher

docker compose version
# Should show: Docker Compose version v2.0+ or higher
```

### Step 1.1: Clone Agent Container Repo

```bash
cd ~/Projects
git clone https://github.com/kkingsbe/agent-coding-container.git
cd agent-coding-container

# Review the structure
ls -la
# Should see: Cargo.toml, docker-compose.yml, agent_instructions/, etc.
```

### Step 1.2: Configure Kilo Code

**Create Kilo Code config:**
```bash
mkdir -p ~/.kilocode
cat > ~/.kilocode/config.json <<EOF
{
  "api_key": "YOUR_KILO_CODE_API_KEY",
  "default_model": "claude-sonnet-4-5",
  "max_tokens": 8000
}
EOF
```

**Get API Key:**
1. Visit https://kilo.ai/account/api-keys
2. Generate new API key
3. Replace `YOUR_KILO_CODE_API_KEY` in config above

### Step 1.3: Create Test Workspace

**Simple test PRD (not Scout-related yet):**
```bash
mkdir -p workspace-test
cd workspace-test

cat > PRD.md <<'EOF'
# Product Requirements: Simple Calculator

## Goal
Build a Python calculator module with basic arithmetic operations.

## Requirements
1. Create `calculator.py` module
2. Implement functions:
   - add(a, b) - returns a + b
   - subtract(a, b) - returns a - b
   - multiply(a, b) - returns a * b
   - divide(a, b) - returns a / b (handle divide by zero)
3. Write test suite in `test_calculator.py`
4. All tests must pass

## Success Criteria
- All 4 functions work correctly
- Test coverage >90%
- Handles edge cases (divide by zero, negative numbers)
- Code follows PEP 8 style

## Deliverables
- calculator.py (implementation)
- test_calculator.py (test suite)
- README.md (usage documentation)
EOF
```

### Step 1.4: Run Test Build

```bash
cd ~/Projects/agent-coding-container

# Set workspace
export MOUNT_HOST_DIR=$(pwd)/workspace-test

# Run agent container (10 cycles only for test)
docker compose up

# Watch for:
# - TODO.md created
# - Git commits happening
# - ARCHITECTURE.md, LEARNINGS.md created
# - src/calculator.py implemented
# - Tests passing
```

### Step 1.5: Validate Output

**After 1-2 hours (10 cycles), check results:**
```bash
cd workspace-test

# Check generated files
ls -la
# Should see: PRD.md, TODO.md, ARCHITECTURE.md, LEARNINGS.md, src/, .state.json

# Check TODO.md
cat TODO.md
# Should show tasks marked complete: [x]

# Check git commits
git log --oneline
# Should show 10-20 commits from Worker Agent

# Check implementation
python src/calculator.py
# Should have working functions

# Run tests
python -m pytest tests/
# Should pass
```

### Phase 1 Success Criteria

✅ **Must Have (Go/No-Go):**
- [ ] Docker container runs without errors
- [ ] TODO.md created and updates each cycle
- [ ] Git commits happening automatically
- [ ] ARCHITECTURE.md and LEARNINGS.md exist
- [ ] src/ directory has implementation files
- [ ] No Kilo Code authentication errors

⚠️ **Nice to Have (Can Debug):**
- [ ] Tests pass (agent might need guidance)
- [ ] Code quality excellent (janitor cleans over time)
- [ ] Full PRD implemented (might need more cycles)

**Decision Point:**
- **If "Must Have" all pass:** ✅ Proceed to Phase 2 (Scout integration)
- **If any "Must Have" fails:** ❌ Debug or abort, fall back to traditional implementation

---

## Phase 2: Scout Workspace Setup (Day 2)

### Goal
Prepare Scout project for agent-driven development with proper structure and reference materials.

### Step 2.1: Create Scout Agent Workspace

```bash
cd ~/Projects/agent-coding-container
mkdir -p workspace-scout
cd workspace-scout

# Initialize git
git init
git config user.name "Agent Worker"
git config user.email "agent@scout.local"

# Copy existing Scout codebase
cp -r ~/Projects/micro-pe/scout/tools ./tools
cp -r ~/Projects/micro-pe/scout/tests ./tests
cp ~/Projects/micro-pe/scout/.env .env
cp ~/Projects/micro-pe/scout/pyproject.toml ./pyproject.toml

# Create directory structure
mkdir -p {outputs/cache,outputs/fdds,outputs/raw_data,docs,reports}

# Initial commit
git add .
git commit -m "Initial Scout codebase import"
```

### Step 2.2: Create LEARNINGS.md Foundation

**This file teaches agents Scout-specific patterns:**
```bash
cat > LEARNINGS.md <<'EOF'
# Scout Project Learnings

## Last Updated
2026-02-17 by Human (Initial setup)

---

## Architecture Overview

Scout is an SMB due diligence platform that collects FDD (Franchise Disclosure Document) and business intelligence data.

**Key Directories:**
- `tools/` - Data collection tools (scrapers)
- `tools/base.py` - Abstract base class all tools inherit from
- `outputs/` - Cache and downloaded data (DO NOT LOAD IN CONTEXT)
- `tests/` - Test suites
- `reports/` - Report generators (to be built)

**Reference Implementation:**
- `tools/minnesota_fdd.py` (449 lines) - Complete working FDD scraper
- This is the GOLD STANDARD for all new scrapers

---

## Tool Pattern (CRITICAL)

All data collection tools MUST follow this pattern:

```python
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

try:
    from .base import Tool
except ImportError:
    from base import Tool

class NewTool(Tool):
    """Tool description"""

    CACHE_TTL_DAYS = 90  # 90 days for FDD scrapers, 7 for volatile data

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.output_dir = Path("outputs/category")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def search(
        self,
        industry: str,
        max_results: int = 10,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Search for data by industry.

        Args:
            industry: Business type (e.g., "car wash")
            max_results: Max results to return
            use_cache: Whether to use cached results

        Returns:
            Dict with search results
        """
        cache_key = f"source_{industry.replace(' ', '_')}_{max_results}"

        # Check cache
        if use_cache:
            cached = self.load_cache(cache_key)
            if cached:
                print(f"✅ Using cached results from {cached['cached_at']}")
                return cached["data"]

        # Implement search logic here
        results = self._scrape_data(industry, max_results)

        # Build response
        response = {
            "source": "tool_name",
            "search_date": datetime.now().isoformat(),
            "industry": industry,
            "total_found": len(results),
            "results": results
        }

        # Cache results
        if use_cache:
            self.save_cache(cache_key, response, self.CACHE_TTL_DAYS)

        return response
```

**Why This Pattern:**
1. Consistent API across all tools (`search()` method)
2. Automatic caching (reduces API calls, prevents rate limits)
3. Clean JSON responses
4. Type hints for clarity
5. Error transparency

---

## Web Scraping Patterns (SELENIUM)

**Chrome Driver Setup (ALWAYS USE THIS):**
```python
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def _get_driver(self):
    """Get configured Chrome driver"""
    options = webdriver.ChromeOptions()
    options.add_argument('--headless=new')  # New headless mode
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    # CRITICAL: Use webdriver-manager (avoids version mismatches)
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    # Anti-detection via CDP
    driver.execute_cdp_cmd('Network.setUserAgentOverride', {
        "userAgent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    })
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    return driver
```

**Why:**
- webdriver-manager auto-downloads correct ChromeDriver version
- Anti-detection prevents bot blocking
- --headless=new is latest Chrome headless mode

**Rate Limiting (ALWAYS IMPLEMENT):**
```python
import time
import random

# Between searches
time.sleep(random.uniform(2.0, 5.0))

# Between PDF downloads
time.sleep(random.uniform(1.0, 3.0))
```

**HTMX/Dynamic Content (Wait for Load):**
```python
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

# Wait for specific element
WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, "results"))
)
```

---

## FDD Domain Knowledge

**What is an FDD?**
Franchise Disclosure Document - legally required for all U.S. franchises (FTC Rule).

**Key Items (23 total):**
- **Item 19**: Financial Performance Representations (MOST IMPORTANT)
  - Revenue, EBITDA, unit economics
  - Top/bottom performers
  - Usually pages 80-120 in PDF
- **Item 7**: Initial Investment Estimates
- **Item 6**: Ongoing Fees (royalties, advertising)
- **Item 20**: Outlet Information (number of locations, openings/closings)

**Extraction Pattern:**
```python
import fitz  # PyMuPDF

def _extract_item19(self, pdf_path: Path) -> str:
    """Extract Item 19 text from FDD PDF"""
    doc = fitz.open(pdf_path)
    full_text = ""

    for page in doc:
        full_text += page.get_text()

    # Find Item 19 start and Item 20 start (end marker)
    import re
    item19_match = re.search(r'Item\s+19[:\.]?\s*Financial Performance', full_text, re.IGNORECASE)
    item20_match = re.search(r'Item\s+20[:\.]?\s*Outlets', full_text, re.IGNORECASE)

    if item19_match and item20_match:
        start = item19_match.start()
        end = item20_match.start()
        return full_text[start:end].strip()

    return ""  # Item 19 not found (not all FDDs have it)
```

**Important:** Not all FDDs have Item 19 (it's optional). Gracefully handle absence.

---

## State-Specific FDD Database Quirks

### Minnesota CARDS (DONE ✅)
- URL: https://www.cards.commerce.state.mn.us/CARDS/security/search.do
- **HTMX dynamic loading** - Must wait for `#results` div
- **Rate Limiting:** Aggressive (10 requests = blocked for 15-60 min)
- **Table Structure:** Standard <table> with <tr> rows
- **PDF Download:** Requires session cookies (use CDP or Selenium download)

### Wisconsin DFI (TO BUILD)
- URL: https://apps.dfi.wi.gov/apps/FranchiseSearch/MainSearch.aspx
- **ASP.NET GridView** - Different table structure than Minnesota
- **Form IDs:** `ctl00_MainContent_txtSearch`, `ctl00_MainContent_btnSearch`
- **Easier than Minnesota** - Direct PDF downloads work (no session issues)
- **Well-documented** - Standard ASP.NET form handling

### California DocQNet (TO BUILD)
- URL: https://docqnet.dfpi.ca.gov/search/
- **SLOW DATABASE** - Need 7-10 second waits (not 2-5 like others)
- **Pagination Required** - Results span multiple pages
- **Document Filtering** - Must filter for FDDs vs blacklines vs applications
- **Largest Market** - 30% of U.S. franchises

### NASAA FRED (TO BUILD)
- URL: https://www.nasaaefd.org/Franchise/Search
- **Multi-State** - Covers 7 states (NY, IL, MD, VA, WA, ND, RI)
- **State Tagging** - Each FDD has filing state, must track provenance
- **Deduplication** - Same franchise may file in multiple states
- **46% Market Share** - Highest ROI implementation

---

## Testing Strategy

**Cache-First Tests (FAST):**
```python
def test_search_with_cache():
    """Use cached data, don't hit real website"""
    tool = NewTool()
    results = tool.search("car wash", max_results=5, use_cache=True)
    assert results['total_found'] > 0
```

**Mocked Tests (FAST):**
```python
def test_parse_html():
    """Test parsing logic with fixture HTML"""
    html = load_fixture('sample_results.html')
    parsed = tool._parse_results(html)
    assert len(parsed) == 10
```

**Live Tests (SLOW - Mark with pytest.mark.slow):**
```python
@pytest.mark.slow
def test_live_search():
    """Only 1 live test per tool (hits real website)"""
    tool = NewTool()
    results = tool.search("car wash", max_results=2, use_cache=False)
    assert results['source'] == 'expected_source'
```

**Why:**
- Avoid rate limits in CI/CD
- Fast test suite for rapid iteration
- Live tests only when necessary

---

## Common Mistakes to Avoid

❌ **Don't** use `git add -A` or `git add .` blindly
✅ **Do** add specific files: `git add tools/new_tool.py`

❌ **Don't** load outputs/ directory in context (huge cache files)
✅ **Do** only load tools/, tests/, docs/

❌ **Don't** skip anti-detection in Selenium
✅ **Do** always use CDP overrides, user-agent spoofing

❌ **Don't** use hardcoded waits (`time.sleep(5)`)
✅ **Do** use WebDriverWait with expected conditions

❌ **Don't** assume Item 19 exists in all FDDs
✅ **Do** gracefully handle absence (return empty string)

❌ **Don't** hit real websites in every test
✅ **Do** use cached/mocked data for fast tests

---

## Success Validation Queries

Test each new tool with these standard queries:

1. **"car wash"** - Should find 10+ results in every state
2. **"mcdonald's"** - Should find in all FDD databases (ubiquitous franchise)
3. **"hvac"** - Should find 5+ results
4. **"laundromat"** - Should find 3+ results

**Example Usage:**
```python
tool = WisconsinFDDScraper()
results = tool.search(industry="car wash", max_results=10)

print(f"Found {results['total_found']} results")
for fdd in results['results'][:3]:
    print(f"  - {fdd['franchise_name']} ({fdd['fdd_year']})")
```

---

## Questions? Create Blocker!

If you (Worker Agent) encounter:
- Unclear requirements
- Missing API keys
- Test failures you can't resolve
- Architecture decisions

**Create file in comms/outbox/blocker-XXX.md** with:
1. Clear description of blocker
2. What you've tried
3. Specific question for human
4. Options you're considering

Human will respond in comms/inbox/ and you can continue next cycle.

---

**End of LEARNINGS.md**
**This file will be updated by agents as new patterns emerge**
EOF
```

### Step 2.3: Create ARCHITECTURE.md Foundation

```bash
cat > ARCHITECTURE.md <<'EOF'
# Scout Architecture

## System Purpose

Scout is an SMB due diligence platform that aggregates FDD (Franchise Disclosure Document) and business intelligence data to help analysts evaluate small businesses for acquisition.

## High-Level Architecture

```
User Query (e.g., "car wash" in "Texas")
    ↓
Data Collection Layer (tools/)
    ├── FDD Aggregator
    │   ├── Minnesota CARDS Scraper (✅ DONE)
    │   ├── Wisconsin DFI Scraper (⏳ TO BUILD)
    │   ├── California DocQNet Scraper (⏳ TO BUILD)
    │   └── NASAA FRED Scraper (⏳ TO BUILD)
    ├── Google Maps Tool (✅ DONE)
    └── BizBuySell Tool (⏳ UNTESTED)
    ↓
Cache Layer (outputs/cache/)
    - 90-day TTL for FDD data
    - 7-day TTL for volatile data
    ↓
Report Generation Layer (reports/)
    ├── Market Overview Report (⏳ TO BUILD)
    ├── Target List CSV (⏳ TO BUILD)
    ├── Benchmark Summary (⏳ TO BUILD)
    ├── Competition Heat Map (⏳ TO BUILD)
    └── Due Diligence Checklist (⏳ TO BUILD)
    ↓
Output (ASCII tables, JSON, CSV)
```

## Directory Structure

```
scout/
├── tools/              # Data collection tools
│   ├── base.py         # Abstract base class (72 lines) ✅
│   ├── minnesota_fdd.py (449 lines) ✅
│   ├── google_maps_tool.py (100 lines) ✅
│   ├── bizbuysell_tool.py (100 lines) ⏳
│   └── (to build: wisconsin_fdd, california_fdd, nasaa_fred, fdd_aggregator)
├── outputs/
│   ├── cache/          # JSON cache files (90-day TTL)
│   ├── fdds/           # Downloaded PDF files
│   └── raw_data/       # JSON exports
├── tests/              # Test suites for tools
├── reports/            # Report generators (to build)
└── docs/               # Documentation (reference only)
```

## Current Status

✅ **Done:**
- Minnesota FDD scraper (working, 70 car wash FDDs found)
- Google Maps integration (working, Houston car washes tested)
- Tool base class with caching

⏳ **To Build:**
- Wisconsin FDD scraper (~400 lines)
- California FDD scraper (~450 lines)
- NASAA FRED FDD scraper (~500 lines)
- FDD aggregator (~200 lines)
- 5 report generators (~200 lines each)

## Design Principles

1. **Separation of Concerns:** Tools collect data, reports analyze/present
2. **Caching First:** Avoid unnecessary API calls and scraping
3. **Graceful Degradation:** Partial data OK, don't fail hard
4. **Consistent APIs:** All tools have `search()` method, return JSON
5. **No Synthesis in Tools:** Tools return raw data, reports do analysis

## Key Technologies

- **Web Scraping:** Selenium + BeautifulSoup + webdriver-manager
- **PDF Extraction:** PyMuPDF (fitz)
- **HTTP Requests:** httpx (for non-Selenium calls)
- **Caching:** JSON files with TTL metadata
- **Testing:** pytest with cache/mock fixtures

## Reference Implementation

**tools/minnesota_fdd.py (449 lines) - GOLD STANDARD**

This file demonstrates:
- Chrome driver setup with anti-detection
- Form filling and dynamic content handling
- PDF download with session preservation
- Item 19 extraction with PyMuPDF
- Caching, error handling, logging
- Clean JSON responses

**All new tools should follow this pattern.**

## Context Loading Rules (FOR AGENTS)

**LOAD in fresh context:**
- tools/base.py
- Current task file (e.g., tools/wisconsin_fdd.py)
- LEARNINGS.md
- This ARCHITECTURE.md
- Recent git log (last 20 commits)
- Test file for current task

**DO NOT LOAD:**
- outputs/* (huge cache files, PDFs)
- data/* (large downloaded PDFs)
- archive/* (old POC code)
- docs/RESEARCH.md (17KB, reference only)

## Integration Points

**FDD Aggregator (to build) will:**
- Query all 4 FDD scrapers
- Deduplicate results (franchise_name + year)
- Track provenance (which state provided which FDD)
- Return unified response

**Report Generators (to build) will:**
- Consume FDD Aggregator + Google Maps + BizBuySell data
- Generate ASCII tables, JSON exports, CSV exports
- No LLM-based synthesis (raw data only)

---

**End of ARCHITECTURE.md**
**Updated by Architect Agent every 8 cycles**
EOF
```

### Step 2.4: Create Initial TODO.md

```bash
cat > TODO.md <<'EOF'
# Scout TODO List

## Phase 2: Wisconsin FDD Scraper

- [ ] Implement tools/wisconsin_fdd.py following minnesota_fdd.py pattern (#1)
- [ ] Add Chrome driver setup with anti-detection (#2)
- [ ] Implement form filling for Wisconsin DFI search (#3)
- [ ] Parse ASP.NET GridView results table (#4)
- [ ] Extract franchise name, document ID, PDF URL, year (#5)
- [ ] Implement PDF download (direct HTTP, no session issues) (#6)
- [ ] Implement Item 19 extraction with PyMuPDF (#7)
- [ ] Add caching (90-day TTL) (#8)
- [ ] Create test suite: test_wisconsin_fdd.py (#9)
- [ ] Test with "car wash" query (should find 10+ results) (#10)
- [ ] Update __init__.py to export WisconsinFDDScraper (#11)

## Future Phases

- [ ] California FDD scraper (Phase 3)
- [ ] NASAA FRED FDD scraper (Phase 4)
- [ ] FDD Aggregator (Phase 5)
- [ ] Report generators (Phase 6)

---

**Notes:**
- Each task should be 1-2 hours of work
- Worker Agent implements 1 task per cycle
- Mark complete with [x] when done
- Janitor will clean up completed tasks every 4 cycles
EOF
```

---

## Phase 3: Wisconsin FDD Scraper (Days 3-4)

### Goal
Use agent container to autonomously implement Wisconsin FDD scraper, validating the full "PRD → Code" workflow.

### Step 3.1: Create Wisconsin Scraper PRD

```bash
cd ~/Projects/agent-coding-container/workspace-scout

cat > PRD-wisconsin-fdd.md <<'EOF'
# Product Requirements: Wisconsin FDD Scraper

## Goal
Implement `tools/wisconsin_fdd.py` following the Minnesota FDD scraper pattern to search and extract FDD documents from Wisconsin Department of Financial Institutions.

## Reference Implementation
**CRITICAL:** Use `tools/minnesota_fdd.py` (449 lines) as the template.
This file has all the patterns you need: Chrome setup, form handling, PDF download, Item 19 extraction, caching.

**Copy the structure, adapt for Wisconsin-specific details.**

## Wisconsin DFI Details

**URL:** https://apps.dfi.wi.gov/apps/FranchiseSearch/MainSearch.aspx

**Form Structure (ASP.NET):**
- Search input ID: `ctl00_MainContent_txtSearch`
- Search button ID: `ctl00_MainContent_btnSearch`
- Results table: ASP.NET GridView (class: `GridView`)

**Differences from Minnesota:**
- ✅ EASIER: Direct PDF downloads work (no session cookie issues)
- ✅ EASIER: No HTMX (standard page load)
- ⚠️ DIFFERENT: ASP.NET form structure (not standard HTML form)
- ⚠️ DIFFERENT: GridView table structure (not standard table)

## Requirements

### 1. Class Structure
```python
from pathlib import Path
from typing import Dict, Any
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import fitz  # PyMuPDF

try:
    from .base import Tool
except ImportError:
    from base import Tool

class WisconsinFDDScraper(Tool):
    """Search for FDD documents from Wisconsin DFI"""

    BASE_URL = "https://apps.dfi.wi.gov/apps/FranchiseSearch/MainSearch.aspx"
    CACHE_TTL_DAYS = 90

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.output_dir = Path("outputs/fdds/wisconsin")
        self.output_dir.mkdir(parents=True, exist_ok=True)
```

### 2. Search Method API
```python
def search(
    self,
    industry: str,
    max_results: int = 10,
    download_pdfs: bool = True,
    extract_item19: bool = True,
    use_cache: bool = True
) -> Dict[str, Any]:
    """
    Search for FDD documents by industry.

    Args:
        industry: Business type (e.g., "car wash")
        max_results: Max FDD documents to return
        download_pdfs: Whether to download PDF files
        extract_item19: Whether to extract Item 19 text
        use_cache: Whether to use cached results

    Returns:
        Dict with FDD search results
    """
```

### 3. Chrome Driver Setup
**Copy from minnesota_fdd.py lines 66-90:**
- Use webdriver-manager (avoids version issues)
- Add anti-detection (CDP overrides, user-agent)
- Use --headless=new mode
- Add --disable-blink-features=AutomationControlled

### 4. Form Filling
```python
# Navigate to Wisconsin DFI
driver.get(self.BASE_URL)

# Wait for page load
time.sleep(2)

# Fill search form (ASP.NET IDs)
search_input = driver.find_element(By.ID, "ctl00_MainContent_txtSearch")
search_input.clear()
search_input.send_keys(industry)

# Click search button
search_button = driver.find_element(By.ID, "ctl00_MainContent_btnSearch")
search_button.click()

# Wait for results
time.sleep(3)
```

### 5. Parse ASP.NET GridView
```python
# Get page source
html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')

# Find GridView table
table = soup.find('table', class_='GridView')
if not table:
    print("⚠️  No results found")
    return []

# Parse rows (skip header)
rows = table.find_all('tr')[1:]  # Skip header row

for row in rows:
    cells = row.find_all('td')
    # Extract: franchise name, document ID, PDF link, year
    # (Exact cell indices need inspection of actual HTML)
```

### 6. PDF Download
**EASIER than Minnesota (direct downloads work):**
```python
import httpx

def _download_pdf(self, fdd: Dict):
    """Download PDF via direct HTTP GET"""
    pdf_url = fdd['pdf_url']
    filename = f"{fdd['franchise_name']}_{fdd['document_id']}.pdf"
    filepath = self.output_dir / filename

    response = httpx.get(pdf_url, follow_redirects=True)
    if response.status_code == 200:
        with open(filepath, 'wb') as f:
            f.write(response.content)
        fdd['pdf_path'] = str(filepath)
        fdd['pdf_downloaded'] = True
```

### 7. Item 19 Extraction
**Copy from minnesota_fdd.py lines 180-212:**
```python
def _extract_item19(self, fdd: Dict):
    """Extract Item 19 text from PDF"""
    if not fdd.get('pdf_path'):
        return

    pdf_path = Path(fdd['pdf_path'])
    doc = fitz.open(pdf_path)
    full_text = ""

    for page in doc:
        full_text += page.get_text()

    # Find Item 19 (between "Item 19" and "Item 20")
    import re
    item19_match = re.search(r'Item\s+19[:\.]?\s*Financial Performance', full_text, re.IGNORECASE)
    item20_match = re.search(r'Item\s+20[:\.]?\s*Outlets', full_text, re.IGNORECASE)

    if item19_match and item20_match:
        start = item19_match.start()
        end = item20_match.start()
        fdd['item_19_text'] = full_text[start:end].strip()
        fdd['has_item_19'] = True
    else:
        fdd['has_item_19'] = False
```

### 8. Response Format
```python
response = {
    "source": "wisconsin_dfi",
    "search_date": datetime.now().isoformat(),
    "industry": industry,
    "total_found": len(fdds),
    "results": fdds  # List of FDD dicts
}
```

### 9. Test Suite
Create `tests/test_wisconsin_fdd.py`:

```python
import pytest
from tools.wisconsin_fdd import WisconsinFDDScraper

def test_search_cached():
    """Test search with cached data (fast)"""
    scraper = WisconsinFDDScraper()
    results = scraper.search("car wash", max_results=5, use_cache=True)
    assert results['source'] == 'wisconsin_dfi'
    assert results['total_found'] >= 0

@pytest.mark.slow
def test_search_live():
    """Test live search (hits real website)"""
    scraper = WisconsinFDDScraper()
    results = scraper.search("car wash", max_results=3, use_cache=False, download_pdfs=False)
    assert results['source'] == 'wisconsin_dfi'
    assert results['total_found'] > 0
    assert len(results['results']) > 0

def test_pdf_download():
    """Test PDF download (if results exist)"""
    # Test with cached data containing PDF URLs
    pass

def test_item19_extraction():
    """Test Item 19 extraction (if PDFs exist)"""
    # Test with actual downloaded PDF
    pass
```

## Success Criteria

### Must Have (Validation Gate)
- [ ] Can import WisconsinFDDScraper without errors
- [ ] search("car wash", max_results=10) returns results
- [ ] Returns JSON format matching minnesota_fdd.py structure
- [ ] Has 90-day caching working (check outputs/cache/)
- [ ] Follows Tool base class pattern
- [ ] At least 1 test passes

### Nice to Have (Can Refine Later)
- [ ] PDF downloads working
- [ ] Item 19 extraction working
- [ ] Full test suite passing
- [ ] Handles edge cases (no results, timeouts, etc.)

## Validation Queries

Test the scraper with these:
1. **"car wash"** - Should find 10+ Wisconsin FDDs
2. **"mcdonald's"** - Should find results (ubiquitous franchise)
3. **"hvac"** - Should find 5+ results

## Deliverables

1. `tools/wisconsin_fdd.py` (~400 lines)
2. `tests/test_wisconsin_fdd.py` (test suite)
3. Update `tools/__init__.py` to export WisconsinFDDScraper
4. Update LEARNINGS.md with Wisconsin-specific patterns

## Implementation Notes

**FOR WORKER AGENT:**
- Start by copying minnesota_fdd.py structure
- Replace Minnesota-specific details with Wisconsin details
- Test incrementally (search → parse → PDF → Item 19)
- Use validation queries to confirm each step
- If blocked (can't find GridView structure, etc.), create blocker in comms/outbox/

**FOR JANITOR AGENT:**
- Clean up any debug print statements
- Remove unused imports
- Ensure consistent code style

**FOR ARCHITECT AGENT:**
- Verify wisconsin_fdd.py follows minnesota_fdd.py pattern
- Check TODO.md reflects actual progress
- Update ARCHITECTURE.md if design evolved

---

**End of PRD**
EOF
```

### Step 3.2: Run Agent Container for Wisconsin Scraper

```bash
cd ~/Projects/agent-coding-container

# Set Scout workspace
export MOUNT_HOST_DIR=$(pwd)/workspace-scout

# Copy Wisconsin PRD to main PRD (agent reads PRD.md)
cp workspace-scout/PRD-wisconsin-fdd.md workspace-scout/PRD.md

# Start agent container
docker compose up

# This will run 24-48 hours (10+ hours runtime × 2 days)
# Worker Agent implements 4-6 tasks/hour = 40-60 tasks total
```

### Step 3.3: Monitor Progress

**Check every few hours:**
```bash
cd workspace-scout

# View TODO.md progress
cat TODO.md
# Should see tasks marked [x] as complete

# Check git commits
git log --oneline | head -20
# Should see Worker Agent commits

# Check implementation
ls -la tools/
# Should see wisconsin_fdd.py appearing and growing

# Check test results (if agent ran pytest)
cat test-results.log  # If agent created it
```

### Step 3.4: Handle Blockers

**Agent will create files in comms/outbox/ when stuck:**
```bash
ls comms/outbox/
# Example: blocker-001-gridview-parsing.md

cat comms/outbox/blocker-001-gridview-parsing.md
```

**Example Blocker:**
```markdown
# Blocker: ASP.NET GridView Structure Unclear

I'm trying to parse the Wisconsin DFI search results table,
but the GridView structure is different than expected.

**What I've tried:**
- `table.find('table', class_='GridView')` - returns None
- `table.find('table', id='ctl00_MainContent_GridView1')` - returns None

**Question:**
Can you inspect the actual HTML and provide the correct selector?

Or should I use a different approach (XPath, CSS selector)?

**Options:**
1. Provide correct GridView selector
2. Save sample HTML to comms/inbox/ for reference
3. Use Selenium's find_element instead of BeautifulSoup

- Worker Agent, Cycle 23
```

**Your Response:**
```bash
# Inspect Wisconsin DFI HTML manually
# Then provide answer:

cat > comms/inbox/response-001-gridview-parsing.md <<'EOF'
# Re: ASP.NET GridView Structure

I inspected the Wisconsin DFI results page. Use this selector:

```python
table = soup.find('table', id='ctl00_MainContent_gvResults')
rows = table.find_all('tr', class_='GridRowStyle')
```

The GridView ID is `gvResults` (not just `GridView`), and rows
have class `GridRowStyle` (not just `tr`).

Also, cell structure:
- Cell 0: Franchise Name
- Cell 1: Document ID
- Cell 2: PDF Link (in <a> tag)
- Cell 3: Filing Year

- Andy, 2026-02-18 14:30
EOF
```

**Agent picks up response next cycle and continues.**

### Step 3.5: Validate Output

**After 24-48 hours, check results:**
```bash
cd workspace-scout

# 1. Check if wisconsin_fdd.py exists and is complete
wc -l tools/wisconsin_fdd.py
# Should be ~400 lines

# 2. Test manually
python -c "
from tools.wisconsin_fdd import WisconsinFDDScraper
scraper = WisconsinFDDScraper()
results = scraper.search('car wash', max_results=5, download_pdfs=False)
print(f\"Found {results['total_found']} Wisconsin FDDs\")
"

# 3. Run test suite
pytest tests/test_wisconsin_fdd.py -v

# 4. Check cache
ls outputs/cache/
# Should see wisconsin_* cache files

# 5. Review git history
git log --oneline
# Should show 20-40 commits from agents
```

### Phase 3 Success Criteria

✅ **Must Have (Go/No-Go for Phase 4):**
- [ ] tools/wisconsin_fdd.py exists and is runnable
- [ ] search("car wash") returns 5+ Wisconsin FDDs
- [ ] JSON format matches minnesota_fdd.py structure
- [ ] Caching works (second call uses cache)
- [ ] At least 1 test passes

⚠️ **Nice to Have (Can Refine):**
- [ ] PDF downloads working (may need debugging)
- [ ] Item 19 extraction working
- [ ] Full test suite passing
- [ ] Handles all edge cases

**Decision Point:**
- **If "Must Have" all pass:** ✅ Wisconsin scraper working! Proceed to California + NASAA (Phase 4)
- **If "Must Have" mostly pass:** ⚠️ Human refinement needed (2-4 hours), then proceed
- **If "Must Have" mostly fail:** ❌ Agent approach not working for web scraping, revert to traditional

---

## Phase 4: California + NASAA FRED Scrapers (Days 5-7)

### Goal
Scale agent container approach to remaining scrapers using refined patterns from Wisconsin.

### Step 4.1: Create California PRD

```bash
cd workspace-scout

cat > PRD-california-fdd.md <<'EOF'
# Product Requirements: California FDD Scraper

## Goal
Implement `tools/california_fdd.py` following Minnesota/Wisconsin patterns.

## Reference
- tools/minnesota_fdd.py (449 lines) - GOLD STANDARD
- tools/wisconsin_fdd.py (~400 lines) - Recently completed

## California DocQNet Details

**URL:** https://docqnet.dfpi.ca.gov/search/

**Key Differences:**
- ⚠️ SLOW DATABASE: Need 7-10 second waits (not 2-5)
- ⚠️ PAGINATION: Results span multiple pages (need "Next" button handling)
- ⚠️ DOCUMENT TYPES: Must filter for FDD documents (not blacklines/applications)
- ✅ LARGEST MARKET: 30% of U.S. franchises

## Requirements

[Similar structure to Wisconsin PRD, adapted for California specifics]

### Pagination Handling
```python
def _handle_pagination(self, soup, max_results):
    """Navigate through multiple pages of results"""
    all_results = []
    page = 1

    while len(all_results) < max_results:
        # Parse current page
        results = self._parse_results_page(soup)
        all_results.extend(results)

        # Find "Next" button
        next_button = soup.find('a', text='Next')
        if not next_button:
            break  # No more pages

        # Click next (via Selenium, not BeautifulSoup)
        driver.find_element(By.LINK_TEXT, "Next").click()
        time.sleep(7)  # SLOW DATABASE - wait longer

        # Get new page
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        page += 1

    return all_results[:max_results]
```

### Document Type Filtering
```python
def _filter_fdd_documents(self, results):
    """Filter for FDD documents only"""
    fdds = []
    for doc in results:
        # Check document type field
        doc_type = doc.get('document_type', '').lower()
        if 'fdd' in doc_type or 'disclosure document' in doc_type:
            fdds.append(doc)
    return fdds
```

## Success Criteria
- [ ] search("car wash") finds 20+ California FDDs
- [ ] Handles pagination correctly
- [ ] Filters for FDD documents only
- [ ] 90-day caching works

[Rest of PRD similar to Wisconsin]

EOF
```

### Step 4.2: Create NASAA FRED PRD

```bash
cat > PRD-nasaa-fred-fdd.md <<'EOF'
# Product Requirements: NASAA FRED FDD Scraper

## Goal
Implement `tools/nasaa_fred_fdd.py` for multi-state FDD search.

## Reference
- tools/minnesota_fdd.py (449 lines)
- tools/wisconsin_fdd.py (~400 lines)
- tools/california_fdd.py (~450 lines)

## NASAA FRED Details

**URL:** https://www.nasaaefd.org/Franchise/Search

**Key Features:**
- ✅ MULTI-STATE: Covers 7 states (NY, IL, MD, VA, WA, ND, RI)
- ✅ HIGHEST ROI: 46% combined market share
- ⚠️ STATE TAGGING: Must track which state each FDD filed in
- ⚠️ DEDUPLICATION: Same franchise may file in multiple states

## Requirements

### Enhanced API (State Filtering)
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
    """
    Search NASAA FRED for FDD documents.

    Args:
        industry: Business type
        max_results: Max results across all states
        states: Optional state filter (e.g., ["NY", "IL"])
        download_pdfs: Whether to download PDFs
        extract_item19: Whether to extract Item 19
        use_cache: Whether to use cache

    Returns:
        Dict with FDD results tagged by filing state
    """
```

### State Provenance Tracking
```python
# Each FDD must include filing state
fdd = {
    "franchise_name": "TOMMY'S EXPRESS",
    "document_id": "NASAA-2024-12345",
    "pdf_url": "https://...",
    "fdd_year": 2024,
    "filing_state": "NY",  # NEW: Track state provenance
    "filing_date": "2024-03-15",
    "source": "nasaa_fred"
}
```

### Multi-State Search
```python
def _search_by_state(self, industry: str, state: str) -> List[Dict]:
    """Search NASAA FRED for specific state"""
    # Fill form with state filter
    state_dropdown = driver.find_element(By.ID, "stateFilter")
    state_dropdown.select_by_value(state)

    # Fill industry
    search_input = driver.find_element(By.ID, "searchInput")
    search_input.send_keys(industry)

    # Submit and parse results
    # ...
```

## Success Criteria
- [ ] search("car wash") finds 30+ FDDs across 7 states
- [ ] Each FDD tagged with filing_state
- [ ] Can filter by states: search("car wash", states=["NY", "IL"])
- [ ] No duplicates within same state

[Rest of PRD]

EOF
```

### Step 4.3: Run California + NASAA (Parallel or Sequential)

**Option A: Sequential (Safer)**
```bash
# Run California first (24-48 hours)
cp PRD-california-fdd.md PRD.md
docker compose up
# Wait for completion, validate

# Then run NASAA (24-48 hours)
cp PRD-nasaa-fred-fdd.md PRD.md
docker compose up
# Wait for completion, validate
```

**Option B: Parallel (Faster, More Complex)**
```bash
# Create two separate workspaces
cp -r workspace-scout workspace-california
cp -r workspace-scout workspace-nasaa

# Terminal 1: California
export MOUNT_HOST_DIR=$(pwd)/workspace-california
cp workspace-california/PRD-california-fdd.md workspace-california/PRD.md
docker compose up

# Terminal 2: NASAA
export MOUNT_HOST_DIR=$(pwd)/workspace-nasaa
cp workspace-nasaa/PRD-nasaa-fred-fdd.md workspace-nasaa/PRD.md
docker compose -p nasaa up

# Merge completed code back to workspace-scout after both finish
```

### Step 4.4: Validation (Same as Phase 3)

Test each scraper:
```python
# California
from tools.california_fdd import CaliforniaFDDScraper
scraper = CaliforniaFDDScraper()
results = scraper.search("car wash", max_results=10)
print(f"California: {results['total_found']} FDDs")

# NASAA
from tools.nasaa_fred_fdd import NASAAFredFDDScraper
scraper = NASAAFredFDDScraper()
results = scraper.search("car wash", max_results=10)
print(f"NASAA (7 states): {results['total_found']} FDDs")
```

---

## Phase 5: FDD Aggregator (Days 8-9)

### Goal
Build unified interface to query all 4 FDD scrapers.

### Step 5.1: Create Aggregator PRD

```bash
cat > PRD-fdd-aggregator.md <<'EOF'
# Product Requirements: FDD Aggregator

## Goal
Create `tools/fdd_aggregator.py` that queries all 4 FDD scrapers and deduplicates results.

## Reference
See /Users/andylee/.claude/plans/tender-launching-sparkle.md Section 4 for design.

## Requirements

### Unified Interface
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
        """Search all FDD databases"""
```

### Deduplication Logic
```python
def deduplicate_results(self, results: Dict) -> List[Dict]:
    """
    Remove duplicate FDDs across states.

    Deduplication key: (franchise_name.lower(), fdd_year)

    Precedence (if duplicate):
    1. More recent year
    2. Has PDF downloaded (vs no PDF)
    3. Has Item 19 extracted (vs no Item 19)
    4. Larger state (CA > NY > MN > WI)
    """
```

## Success Criteria
- [ ] search_all("car wash") queries all 4 scrapers
- [ ] Deduplicates correctly (no duplicate franchise+year combos)
- [ ] Tracks provenance (which state provided each FDD)
- [ ] Returns unified JSON response

[Rest of PRD]

EOF
```

### Step 5.2: Run Aggregator Build

```bash
cp PRD-fdd-aggregator.md PRD.md
docker compose up
# Runs 12-24 hours (simpler than scrapers)
```

### Step 5.3: Test Full Pipeline

```python
from tools.fdd_aggregator import FDDAggregator

aggregator = FDDAggregator()

# Search all states
results = aggregator.search_all(
    industry="car wash",
    max_results_per_source=10,
    download_pdfs=False,  # Fast, metadata only
    use_cache=True
)

print(f"Total FDDs found: {results['total_deduplicated']}")
print(f"States searched: {results['states_searched']}")
print(f"Coverage: {results['market_coverage_pct']}%")

# By state breakdown
for state, data in results['by_state'].items():
    print(f"  {state}: {data['total_found']} FDDs")
```

**Expected Output:**
```
Total FDDs found: 67 (after deduplication)
States searched: 10 (MN, WI, CA, NY, IL, MD, VA, WA, ND, RI)
Coverage: 92% of U.S. franchise market
  minnesota: 18 FDDs
  wisconsin: 12 FDDs
  california: 25 FDDs (largest)
  nasaa_fred: 31 FDDs (7 states combined)
```

---

## Phase 6: Report Generators (Days 10-12)

### Goal
Build 5 report types consuming FDD + Google Maps data.

### Step 6.1: Report Generator PRDs

**Create 5 separate PRDs (one per report type):**
1. PRD-report-market-overview.md
2. PRD-report-target-list-csv.md
3. PRD-report-benchmark-summary.md
4. PRD-report-competition-heatmap.md
5. PRD-report-due-diligence-checklist.md

**Example (Market Overview):**
```markdown
# PRD: Market Overview Report

## Goal
Generate comprehensive market overview report combining FDD + Google Maps data.

## Data Sources
- FDD Aggregator (Item 19 financial data)
- Google Maps Tool (business density, locations)
- BizBuySell Tool (market comps)

## Output Format
ASCII table for terminal display + JSON export

## Example Output
```
═══════════════════════════════════════════════════
         MARKET OVERVIEW: Car Wash Industry
═══════════════════════════════════════════════════

FRANCHISED BRANDS (FDD Data)
  Total Brands Found: 67
  With Item 19 Data: 42 (63%)
  States Covered: 10 (MN, WI, CA, NY, IL, MD, VA, WA, ND, RI)

FINANCIAL BENCHMARKS (Item 19 Averages)
  Average Revenue: $1.2M - $2.8M
  Average EBITDA: $280K - $650K (23-24% margin)
  Top Performer: Tommy's Express ($3.5M avg revenue)
  Bottom 25%: <$800K revenue

INDEPENDENT BUSINESSES (Google Maps)
  Total Found: 245 in Texas
  Houston Metro: 87 locations
  Dallas Metro: 63 locations
  Austin Metro: 42 locations

MARKET COMPS (BizBuySell)
  Recent Sales: 12 transactions
  Price Range: $400K - $2.8M
  Avg Multiple: 2.5-3.5x EBITDA
```

[Detailed PRD for implementation]
```

### Step 6.2: Run Report Builds

**Sequential approach (5 reports):**
```bash
for report in market-overview target-list benchmark-summary competition-heatmap due-diligence-checklist; do
    cp PRD-report-$report.md PRD.md
    docker compose up
    # Each report: 12-24 hours
done
```

**Or parallel (faster):**
Create 5 workspaces, run 5 Docker containers simultaneously.

### Step 6.3: Validate Reports

```python
from reports.market_overview import MarketOverviewReport

report = MarketOverviewReport()
output = report.generate(industry="car wash", location="Texas")

print(output['ascii_table'])  # Terminal display
output['json_data']  # For programmatic use
output['csv_path']  # For spreadsheet import
```

---

## Success Metrics & Timeline

### Overall Project Timeline

| Phase | Duration | Human Time | Agent Runtime | Deliverable |
|-------|----------|------------|---------------|-------------|
| Phase 1: Setup | 1 day | 8 hours | 2 hours | Agent container validated |
| Phase 2: Scout Workspace | 1 day | 4 hours | - | PRDs, LEARNINGS.md, ARCHITECTURE.md |
| Phase 3: Wisconsin Scraper | 2 days | 4 hours | 24-48 hours | tools/wisconsin_fdd.py |
| Phase 4: CA + NASAA Scrapers | 3 days | 6 hours | 48-72 hours | tools/california_fdd.py, tools/nasaa_fred_fdd.py |
| Phase 5: FDD Aggregator | 1-2 days | 2 hours | 12-24 hours | tools/fdd_aggregator.py |
| Phase 6: Report Generators | 2-3 days | 4 hours | 60-120 hours | 5 report generators |
| **Total** | **10-12 days** | **28-32 hours** | **146-266 hours** | Complete Scout platform |

### Cost Analysis

**Traditional Implementation:**
- 12-18 days × 8 hours/day = 96-144 hours
- At $100/hour: **$9,600 - $14,400**

**Agent Container Implementation:**
- Human time: 28-32 hours
- At $100/hour: **$2,800 - $3,200**
- AI costs (Kilo Code): ~$500-800
- **Total: $3,300 - $4,000**

**Savings: $5,600 - $10,400 (61-72% reduction)**

### Quality Metrics

**Success Criteria (End-to-End):**
- [ ] All 4 FDD scrapers working (MN ✅, WI, CA, NASAA)
- [ ] FDD Aggregator deduplicates correctly
- [ ] Can query "car wash" and get 50+ unique FDDs
- [ ] >80% success rate on 20 test queries
- [ ] All 5 reports generate successfully
- [ ] Test suite passes (>80% coverage)
- [ ] Code follows Scout patterns (Tool base class, caching, etc.)

---

## Risk Mitigation & Troubleshooting

### Common Issues & Solutions

**Issue: Agent Gets Stuck on Web Scraping**
- **Solution:** Provide HTML samples in comms/inbox/, give exact selectors
- **Fallback:** Human implements specific scraping logic (2-4 hours), agent continues with rest

**Issue: Tests Failing Due to Rate Limits**
- **Solution:** Update PRD to use cached data for tests, only 1 live test per tool
- **Fallback:** Disable live tests, validate manually

**Issue: Context Too Large (Slow Iterations)**
- **Solution:** Update ARCHITECTURE.md to explicitly exclude outputs/ and data/ directories
- **Fallback:** Reduce workspace size, move outputs outside workspace

**Issue: Agent Produces Low-Quality Code**
- **Solution:** Janitor Agent refactors (runs every 4 cycles), or human refines after completion
- **Fallback:** Use hybrid approach (agent scaffolds, human refines)

**Issue: Kilo Code API Costs Too High**
- **Solution:** Reduce TICK_INTERVAL (slower iterations = fewer API calls), use smaller model for Worker
- **Fallback:** Switch to manual implementation for remaining components

### Emergency Abort Procedure

**If agent container consistently failing:**
1. Stop Docker container
2. Review git history: `git log --oneline`
3. Keep working code, discard broken attempts
4. Switch to traditional implementation for remaining components
5. Still saved time on completed components

**Partial success is still valuable:**
- If Wisconsin + California work but NASAA fails → 65% of market coverage achieved
- If all scrapers work but reports fail → Data collection complete, reports can be built traditionally

---

## Next Steps (Your Action Items)

### Immediate Decision (Day 1)

**Review this plan and decide:**
1. ✅ **Proceed with agent container POC** → Go to Phase 1 setup
2. ⚠️ **Modify plan first** → What changes do you want?
3. ❌ **Stick with traditional** → Resume manual implementation from tender-launching-sparkle.md plan

### If Proceeding (Day 1 Afternoon)

**Phase 1 Setup Checklist:**
```bash
# 1. Install Docker (if not present)
brew install --cask docker  # macOS
open -a Docker  # Start Docker Desktop

# 2. Clone agent-coding-container
cd ~/Projects
git clone https://github.com/kkingsbe/agent-coding-container.git
cd agent-coding-container

# 3. Set up Kilo Code
# - Sign up at https://kilo.ai/
# - Get API key
# - Save to ~/.kilocode/config.json

# 4. Run test build
mkdir workspace-test
# (Create simple PRD as shown in Phase 1.3)
export MOUNT_HOST_DIR=$(pwd)/workspace-test
docker compose up

# 5. Validate (after 1-2 hours)
# - Check TODO.md updating
# - Check git commits
# - Check generated files

# 6. Go/No-Go decision
# - If success → Phase 2
# - If fail → Debug or abort
```

### Day 2 Onwards

Follow phases sequentially:
- Day 2: Scout workspace setup (Phase 2)
- Days 3-4: Wisconsin scraper (Phase 3)
- Days 5-7: California + NASAA (Phase 4)
- Days 8-9: FDD Aggregator (Phase 5)
- Days 10-12: Report generators (Phase 6)

---

## Appendix: PRD Template

**Use this template for future Scout components:**

```markdown
# Product Requirements: [Component Name]

## Goal
[One sentence: what you're building]

## Reference
- tools/minnesota_fdd.py (if relevant)
- [Other working examples]

## Requirements

### 1. [Requirement Category]
[Detailed description]

```python
# Code examples showing expected structure
```

### 2. [Next Requirement]
[...]

## Success Criteria
- [ ] Must-have criterion 1
- [ ] Must-have criterion 2
- [ ] Nice-to-have criterion 3

## Validation Queries
1. Test case 1
2. Test case 2

## Deliverables
1. File 1 (estimated lines)
2. File 2 (estimated lines)
3. Tests

---

**FOR WORKER AGENT:**
[Specific guidance for implementation]

**FOR JANITOR AGENT:**
[What to clean up]

**FOR ARCHITECT AGENT:**
[What to verify]
```

---

**End of Implementation Plan**
**Author:** Claude Sonnet 4.5
**Date:** February 17, 2026

**Ready to proceed? Say "Start Phase 1" to begin setup.**
