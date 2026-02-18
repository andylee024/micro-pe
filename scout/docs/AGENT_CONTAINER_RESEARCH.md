# Agent Coding Container: Research & Analysis
**Date:** February 17, 2026
**Purpose:** Evaluate autonomous coding container architecture for Scout deal intelligence platform
**Source:** [agent-coding-container](https://github.com/kkingsbe/agent-coding-container) architecture analysis

---

## 1. Executive Summary

**What It Is:**
A Docker-based autonomous software development system that reads a Product Requirements Document (PRD) and continuously implements features without human intervention using specialized AI agents operating in coordinated cycles.

**Core Innovation:**
Eliminates LLM context window bloat by using "fresh context" per iteration while maintaining project memory through git history and structured markdown files (TODO.md, ARCHITECTURE.md, LEARNINGS.md).

**Proven Results:**
- 10+ hours continuous operation without divergence
- 4-6 tasks completed per hour
- Minimal human oversight required
- Async communication model for blockers

**Key Value for Scout:**
Could enable "write PRD → auto-implement" workflow for Scout's SMB due diligence platform, dramatically accelerating feature development.

---

## 2. Architecture Deep Dive

### Three-Agent System Design

The system employs **separation of concerns** through specialized agents running at different intervals:

```
┌─────────────────────────────────────────────────────────┐
│                   MAIN LOOP (Docker)                    │
│                                                         │
│  ┌──────────────────────────────────────────────────┐ │
│  │ WORKER AGENT (Every 1 cycle)                     │ │
│  │ - Reads TODO.md                                  │ │
│  │ - Implements ONE task                            │ │
│  │ - Updates code + git commit                      │ │
│  │ - Marks task complete in TODO.md                 │ │
│  └──────────────────────────────────────────────────┘ │
│                                                         │
│  ┌──────────────────────────────────────────────────┐ │
│  │ JANITOR AGENT (Every 4 cycles)                   │ │
│  │ - Reviews completed tasks                        │ │
│  │ - Removes technical debt                         │ │
│  │ - Cleans up TODO.md                              │ │
│  │ - Prevents drift accumulation                    │ │
│  └──────────────────────────────────────────────────┘ │
│                                                         │
│  ┌──────────────────────────────────────────────────┐ │
│  │ ARCHITECT AGENT (Every 8 cycles)                 │ │
│  │ - Reviews ARCHITECTURE.md vs actual code         │ │
│  │ - Breaks down unclear/large tasks                │ │
│  │ - Updates technical roadmap                      │ │
│  │ - Ensures alignment with PRD                     │ │
│  └──────────────────────────────────────────────────┘ │
│                                                         │
│  State: .state.json (loop counter, blockers, flags)   │
│  Memory: git history + markdown documentation          │
│  Communication: comms/inbox + comms/outbox             │
└─────────────────────────────────────────────────────────┘
```

**Why This Works:**
- **No single agent plans AND executes** - prevents goal drift
- **Janitor prevents technical debt** - maintains code quality
- **Architect prevents divergence** - ensures long-term alignment
- **Fresh context prevents pollution** - no conversation history accumulation

### Memory System: No Context Window Bloat

**Traditional Problem:**
LLM context windows fill up with conversation history, causing:
- Context pollution (irrelevant information)
- Decreased quality over time
- Hard limits (200K token windows)

**Agent Container Solution:**
```
Each iteration starts with FRESH CONTEXT containing:
  ├── PRD.md (original requirements)
  ├── TODO.md (current task list)
  ├── ARCHITECTURE.md (system design)
  ├── LEARNINGS.md (key decisions/patterns)
  ├── BLOCKERS.md (open questions)
  ├── comms/inbox/* (human responses)
  └── git log + diff (recent changes)

NO conversation history from previous iterations!
```

**Project Memory Persists Via:**
1. **Git History** - All code changes + commit messages
2. **Markdown Documentation** - Structured knowledge
3. **JSON State** - Loop counters, flags, metadata
4. **File System** - Generated code, tests, configs

**Benefits:**
- Infinite operation time (no context limits)
- Consistent quality (no degradation)
- Clear audit trail (git history)
- Easy debugging (read markdown files)

---

## 3. Operational Flow

### Bootstrap Phase (First Run)

```
User provides PRD.md
    ↓
docker compose up
    ↓
Architect Agent initializes:
  ├── Reads PRD.md
  ├── Creates TODO.md (task breakdown)
  ├── Creates ARCHITECTURE.md (system design)
  ├── Creates LEARNINGS.md (empty)
  └── Initializes .state.json
    ↓
Main loop begins
```

### Normal Operation Cycle

```
CYCLE N:
  1. Read .state.json (determine which agents run)
  2. Load fresh context (PRD, TODO, ARCHITECTURE, git log)
  3. Run applicable agents:
     - Worker (every cycle) → implement 1 task
     - Janitor (every 4th) → clean tech debt
     - Architect (every 8th) → review alignment
  4. Update markdown files
  5. Git commit changes
  6. Update .state.json
  7. Sleep (default 600s = 10 min)
  8. Repeat

TERMINATION:
  - When .done file appears in workspace
  - Manual docker stop
  - Error threshold exceeded
```

### Human Communication Model

**Traditional:** Synchronous (human must respond immediately)
**Agent Container:** Asynchronous (human responds at convenience)

```
Agent encounters blocker
    ↓
Creates file in comms/outbox/
    ↓
Continues other work
    ↓
Human responds (anytime) by creating file in comms/inbox/
    ↓
Next iteration picks up response
    ↓
Agent unblocks and continues
```

**Example Blocker:**
```markdown
# comms/outbox/question-001.md
## Blocker: API Key Location

I need to implement Google Maps integration but can't find
the API key location in the environment config.

Options:
1. Use .env file (recommended)
2. Use environment variable
3. Use config.json

Please advise which approach to use.

- Worker Agent, Cycle 23
```

**Human Response:**
```markdown
# comms/inbox/response-001.md
## Re: API Key Location

Use .env file approach. See .env.example for template.
All third-party API keys should use this pattern.

- Andy, 2026-02-17 14:30
```

---

## 4. Technical Stack

### Core Technologies

**Runtime:**
- Docker + Docker Compose (isolation + orchestration)
- Rust (79.9%) - Main loop, state management, agent coordination
- JavaScript (19.3%) - Kilo Code integration, tooling

**AI Integration:**
- [Kilo Code](https://kilo.ai/docs) - AI coding agent platform
  - Open source VS Code extension
  - 400+ AI models via OpenRouter
  - 1.5M+ users, Apache 2.0 license
  - MCP-style server marketplace for custom tools

**State Management:**
- `.state.json` - Loop counter, flags, metadata
- `git` - Code history, commit messages
- Markdown files - Structured documentation

**File System Structure:**
```
workspace/
├── PRD.md                  # User-provided requirements
├── TODO.md                 # Task list (updated by agents)
├── ARCHITECTURE.md         # System design (updated by Architect)
├── LEARNINGS.md            # Key decisions/patterns
├── BLOCKERS.md             # Open questions/blockers
├── .state.json             # Loop state
├── .done                   # Termination flag (created when complete)
├── comms/
│   ├── inbox/              # Human responses
│   └── outbox/             # Agent questions
└── src/                    # Generated code
    └── (project-specific structure)
```

### Configuration

**Environment Variables:**
```bash
TICK_INTERVAL=600           # Seconds between cycles (default: 10 min)
MOUNT_HOST_DIR=/path/to/workspace  # Custom workspace location
WORKER_INTERVAL=1           # Worker runs every N cycles
JANITOR_INTERVAL=4          # Janitor runs every N cycles
ARCHITECT_INTERVAL=8        # Architect runs every N cycles
```

**Docker Compose:**
```yaml
services:
  agent-loop:
    build: .
    volumes:
      - ./workspace:/workspace
      - /var/run/docker.sock:/var/run/docker.sock  # For nested containers
    environment:
      - TICK_INTERVAL=${TICK_INTERVAL:-600}
    restart: unless-stopped
```

---

## 5. Agent Responsibilities

### Worker Agent (Every Cycle)

**Purpose:** Implement one task from TODO.md

**Input:**
- TODO.md (task list)
- ARCHITECTURE.md (system design)
- LEARNINGS.md (patterns to follow)
- git log (recent changes)
- src/ (current codebase)

**Process:**
1. Read TODO.md, find first incomplete task
2. Load relevant context (files, patterns)
3. Implement task (code changes, tests)
4. Run tests/validation
5. Git commit with descriptive message
6. Update TODO.md (mark complete)
7. Update LEARNINGS.md (if new patterns)

**Output:**
- Code changes (committed to git)
- Updated TODO.md
- Updated LEARNINGS.md (if applicable)
- Possible comms/outbox question (if blocked)

**Performance:** 4-6 tasks/hour (varies by complexity)

### Janitor Agent (Every 4 Cycles)

**Purpose:** Remove technical debt and prevent drift

**Input:**
- TODO.md (completed tasks)
- src/ (codebase)
- git log (recent commits)

**Process:**
1. Review completed tasks in TODO.md
2. Check for accumulated technical debt:
   - Unused imports
   - Dead code
   - Inconsistent naming
   - Missing error handling
   - Code duplication
3. Refactor/clean as needed
4. Remove completed tasks from TODO.md
5. Git commit cleanup changes

**Output:**
- Cleaner codebase
- Updated TODO.md (completed tasks removed)
- Git commits (refactoring/cleanup)

**Why Needed:** Prevents "drift" from accumulating over 10+ hour runs

### Architect Agent (Every 8 Cycles)

**Purpose:** Ensure alignment with PRD and break down complex tasks

**Input:**
- PRD.md (original requirements)
- ARCHITECTURE.md (current design)
- TODO.md (task list)
- src/ (actual implementation)
- git log (what's been built)

**Process:**
1. Compare PRD goals vs current TODO.md
2. Identify gaps or misalignments
3. Review ARCHITECTURE.md vs actual code structure
4. Find large/unclear tasks in TODO.md
5. Break down complex tasks into subtasks
6. Update ARCHITECTURE.md if design evolved
7. Update TODO.md with refined tasks

**Output:**
- Updated TODO.md (better task breakdown)
- Updated ARCHITECTURE.md (reflects reality)
- Possible BLOCKERS.md updates (ambiguities found)

**Why Needed:** Prevents long-term divergence from requirements

---

## 6. Key Design Patterns

### Pattern 1: Separation of Planning vs Execution

**Problem:** When one agent both plans and executes, it can drift from original goals.

**Solution:**
- Worker only executes (doesn't modify TODO)
- Architect only plans (doesn't write code)
- Janitor only cleans (doesn't add features)

**Result:** Goal alignment maintained over 10+ hours

### Pattern 2: Fresh Context Per Iteration

**Problem:** LLM context windows accumulate irrelevant conversation history.

**Solution:**
- Start each iteration with clean slate
- Load only: PRD + TODO + ARCHITECTURE + LEARNINGS + recent git log
- NO previous agent conversations

**Result:** Consistent quality, infinite runtime

### Pattern 3: Structured Knowledge in Markdown

**Problem:** Unstructured memory (conversation history) hard to parse.

**Solution:**
```markdown
# TODO.md
- [x] Implement Google Maps search (#1)
- [ ] Add caching layer (#2)
- [ ] Extract Item 19 from PDFs (#3)

# ARCHITECTURE.md
## Data Flow
User Query → Tool → Scraper → Cache → JSON Response

## Patterns
- All tools inherit from base.Tool
- 90-day cache TTL
- Selenium for web scraping

# LEARNINGS.md
## 2026-02-17: Chrome Driver
- Use webdriver-manager for auto-version management
- Avoids "version mismatch" errors
```

**Result:** Easy for agents to load relevant context, easy for humans to debug

### Pattern 4: Async Human Communication

**Problem:** Blocking on human responses stops all progress.

**Solution:**
- Agent deposits question in comms/outbox/
- Continues with other tasks
- Human responds asynchronously in comms/inbox/
- Next iteration picks up response

**Result:** Minimal human time required, no idle waiting

---

## 7. Comparison: Agent Container vs Traditional Development

| Aspect | Traditional Dev | Agent Container |
|--------|----------------|-----------------|
| **Planning** | Human writes tasks | Architect agent breaks down PRD |
| **Implementation** | Human codes | Worker agent implements |
| **Code Quality** | Manual reviews | Janitor agent cleans |
| **Context Management** | Human memory | Git + markdown files |
| **Runtime** | 8-hour workdays | 10+ hours continuous |
| **Throughput** | 2-4 tasks/day | 40-60 tasks/day (4-6/hour × 10 hours) |
| **Human Time** | 100% | <5% (only blockers/PRD writing) |
| **Drift Prevention** | Code reviews | Architect agent alignment checks |
| **Knowledge Retention** | Docs (if written) | LEARNINGS.md (automatic) |

**Key Insight:**
Agent container doesn't replace human developers—it automates the *execution* of well-defined tasks. Humans still define requirements (PRD) and handle ambiguity (blockers).

---

## 8. Relevance to Scout Project

### Current Scout Architecture

```
scout/
├── tools/
│   ├── base.py (Tool base class)
│   ├── minnesota_fdd.py (449 lines, working)
│   ├── google_maps_tool.py (100 lines, working)
│   ├── bizbuysell_tool.py (100 lines, not tested)
│   └── (planned: wisconsin_fdd, california_fdd, nasaa_fred, aggregator)
├── scrapers/ (legacy, to be refactored)
├── outputs/ (cache, PDFs, raw data)
└── docs/ (RESEARCH.md, STATUS_REVIEW.md, PRODUCT.md)

Current State:
- ✅ Minnesota FDD scraper working (70 car wash FDDs found)
- ✅ Google Maps integration working (Houston car washes)
- ⏳ Multi-state FDD scraper plan approved (10-15 days estimated)
- ⏳ Report generators (not started)
```

### How Agent Container Could Accelerate Scout

**Scenario 1: Multi-State FDD Scraper Implementation**

**Traditional Approach (Current Plan):**
- Human implements Wisconsin scraper (2-3 days)
- Human implements California scraper (3-4 days)
- Human implements NASAA FRED scraper (3-4 days)
- Human implements aggregator (1-2 days)
- Total: 10-15 days of human coding

**Agent Container Approach:**
```markdown
# PRD.md for FDD Scraper Pipeline

## Goal
Build 4 FDD scrapers (Wisconsin, California, NASAA FRED, aggregator)
covering 10 states and 90%+ U.S. franchise market.

## Requirements
1. Follow minnesota_fdd.py pattern (reference implementation)
2. Each scraper inherits from tools/base.py
3. Consistent API: search(industry, max_results, download_pdfs, extract_item19)
4. 90-day cache TTL
5. Selenium + BeautifulSoup for scraping
6. PyMuPDF for PDF text extraction
7. Anti-detection (user-agent, CDP overrides)
8. Aggregator deduplicates cross-state results

## Success Criteria
- All 4 scrapers pass test suite
- Can search "car wash" and get 50+ results across all states
- >80% success rate on 20 test queries
- <5 minutes per 10 results per state
```

**Result:**
- Write PRD → Agent container implements autonomously
- 10 hours runtime → 40-60 tasks completed
- Human only intervenes for blockers (API keys, test failures)
- Estimated completion: 24-48 hours (not 10-15 days)

**Scenario 2: Report Generator Implementation**

**Current Challenge:**
User requested report generators (market overview, target list CSV) but we pivoted to validate data pipeline first. Now we have multiple features to build.

**Agent Container PRD:**
```markdown
# PRD.md for Scout Report Generators

## Goal
Build 5 report generators consuming FDD + Google Maps data:
1. Market Overview Report (industry size, competition, growth)
2. Target List CSV (companies, contact info, scores)
3. Benchmark Summary (Item 19 financial data)
4. Competition Heat Map (geographic density)
5. Due Diligence Checklist (red flags, validation items)

## Data Sources
- tools/fdd_aggregator (FDD Item 19 financial data)
- tools/google_maps_tool (business universe)
- tools/bizbuysell_tool (market comps)

## Output Format
- ASCII tables for terminal display
- JSON exports for downstream analysis
- CSV exports for spreadsheet import

## Patterns
- All reports inherit from base.Report class
- Accept industry + location parameters
- Cache results (7-day TTL)
```

**Result:**
- Agent implements all 5 reports autonomously
- Human validates outputs, provides feedback
- Estimated completion: 24-48 hours

---

## 9. Implementation Considerations for Scout

### Strengths: Why Agent Container Fits Scout

✅ **Well-Defined Tasks:** Scout has clear patterns (Tool base class, scraper templates)
✅ **Modular Architecture:** Each scraper is independent (parallelizable)
✅ **Existing Reference:** minnesota_fdd.py is 449-line working example
✅ **Testing Infrastructure:** Can validate with real queries ("car wash", "hvac")
✅ **Structured Data:** FDD/maps data has clear schemas
✅ **Incremental Delivery:** Can build scrapers one at a time

### Challenges: Where Scout Differs from Typical Use Cases

⚠️ **Web Scraping Complexity:** Selenium-based scraping has timeouts, rate limits, anti-bot detection
⚠️ **External Dependencies:** Google Maps API keys, state website availability
⚠️ **Dynamic Sites:** HTMX, ASP.NET forms, pagination vary by state
⚠️ **Testing Friction:** Each test hits real websites (rate limits, flakiness)
⚠️ **Domain Knowledge:** Understanding FDD structure (Item 19, Item 7, etc.) requires context

### Mitigation Strategies

**1. Enhanced LEARNINGS.md:**
```markdown
# LEARNINGS.md for Scout

## Web Scraping Patterns
- Always use webdriver-manager for ChromeDriver
- Add 2-5 second delays between requests
- Use CDP overrides for anti-detection
- Handle rate limits with exponential backoff

## FDD Domain Knowledge
- Item 19: Financial performance (revenue, EBITDA)
- Item 7: Initial investment estimates
- Item 6: Ongoing fees (royalties, ad spend)
- Item 20: Outlet information (# locations)

## State-Specific Quirks
- Minnesota: HTMX dynamic loading, wait for #results
- Wisconsin: ASP.NET GridView, different table structure
- California: Slow database, need 7-10 second waits
- NASAA FRED: Multi-state, tag each FDD with filing state
```

**2. Reference Implementation in PRD:**
```markdown
# PRD.md

## Reference Implementation
See /Users/andylee/Projects/micro-pe/scout/tools/minnesota_fdd.py
for complete working example of the scraper pattern.

Key sections:
- Lines 23-52: Chrome setup with anti-detection
- Lines 67-98: Form filling and result parsing
- Lines 143-178: PDF download with session preservation
- Lines 180-212: Item 19 extraction with PyMuPDF
```

**3. Test Data for Validation:**
```markdown
# PRD.md

## Validation Queries
Test each scraper with these queries:
- "car wash" - Should find 50+ results across all states
- "mcdonald's" - Should find in all databases
- "hvac" - Should find 30+ results
- "laundromat" - Should find 10+ results
```

---

## 10. Proposed Integration Plan

### Phase 1: Setup & Validation (1 day)

**Goal:** Get agent container running locally with Scout workspace

**Steps:**
1. Clone agent-coding-container repo
2. Install dependencies (Docker, Kilo Code credentials)
3. Create `workspace/` directory for Scout project
4. Copy existing Scout codebase into workspace
5. Test basic loop with simple PRD
6. Validate git commits, markdown updates working

**Success Criteria:**
- Agent container runs 10 cycles without errors
- Can see TODO.md updating, git commits happening
- Markdown files (ARCHITECTURE, LEARNINGS) created

### Phase 2: Wisconsin FDD Scraper POC (2-3 days)

**Goal:** Validate agent container can build a complete scraper autonomously

**PRD:**
```markdown
# PRD.md - Wisconsin FDD Scraper

## Goal
Implement tools/wisconsin_fdd.py following the minnesota_fdd.py pattern.

## Reference
/Users/andylee/Projects/micro-pe/scout/tools/minnesota_fdd.py (449 lines)

## Requirements
1. Inherit from tools/base.py
2. URL: https://apps.dfi.wi.gov/apps/FranchiseSearch/MainSearch.aspx
3. Search by industry keyword
4. Parse ASP.NET GridView results
5. Download PDFs (optional flag)
6. Extract Item 19 (optional flag)
7. 90-day cache TTL
8. Return JSON format matching minnesota_fdd.py

## Success Criteria
- Search "car wash" finds 10+ Wisconsin FDDs
- Can download 1 PDF successfully
- Passes test suite (test_wisconsin_fdd.py)
- Follows minnesota_fdd.py anti-detection patterns
```

**Human Involvement:**
- Provide API keys if needed (in comms/inbox/)
- Validate test results (check PDFs downloaded)
- Answer blockers (e.g., "Should I handle pagination?")

**Expected Output:**
- tools/wisconsin_fdd.py (~400 lines)
- tests/test_wisconsin_fdd.py
- Updated LEARNINGS.md (Wisconsin-specific patterns)
- 10-20 git commits

**Timeline:**
- Agent runs: 24-48 hours (10+ hours runtime × 2 days)
- Human time: <2 hours (blockers + validation)

### Phase 3: California + NASAA FRED Scrapers (3-5 days)

**Goal:** Scale to remaining scrapers using refined patterns from Phase 2

**PRDs:**
- PRD-california-fdd.md
- PRD-nasaa-fred-fdd.md

**Human Involvement:**
- Less than Phase 2 (patterns established)
- Mainly validation and edge cases

**Expected Output:**
- tools/california_fdd.py (~450 lines)
- tools/nasaa_fred_fdd.py (~500 lines)
- Test suites for both
- Updated LEARNINGS.md

### Phase 4: FDD Aggregator (1-2 days)

**Goal:** Unified interface to query all FDD scrapers

**PRD:**
```markdown
# PRD.md - FDD Aggregator

## Goal
Create tools/fdd_aggregator.py that queries all 4 FDD scrapers
and deduplicates results across states.

## Requirements
1. search_all(industry) - queries all scrapers
2. search_by_states(industry, states) - queries specific states
3. Deduplication logic (franchise_name + year)
4. Provenance tracking (which state provided which FDD)
5. Coverage statistics

## Reference
See /Users/andylee/.claude/plans/tender-launching-sparkle.md
Section 4 for aggregator design.
```

**Expected Output:**
- tools/fdd_aggregator.py (~200 lines)
- Integration tests
- Example usage scripts

### Phase 5: Report Generators (3-5 days)

**Goal:** Build 5 reports consuming FDD + Maps data

**PRD:**
```markdown
# PRD.md - Scout Report Generators

## Goal
Build 5 report types combining FDD + Google Maps data.

## Reports
1. Market Overview (industry metrics)
2. Target List CSV (companies to contact)
3. Benchmark Summary (Item 19 financial data)
4. Competition Heat Map (geographic density)
5. Due Diligence Checklist (validation items)

## Data Sources
- tools/fdd_aggregator (Item 19 data)
- tools/google_maps_tool (business locations)
- tools/bizbuysell_tool (market comps)

## Output Formats
- ASCII tables (terminal display)
- JSON exports (downstream analysis)
- CSV exports (spreadsheet import)
```

**Expected Output:**
- reports/ directory with 5 report generators
- Test suite validating report outputs
- Example reports for "car wash" industry

---

## 11. Risks & Mitigation

### Risk 1: Agent Gets Stuck on Web Scraping Edge Cases

**Risk:** Selenium timeouts, rate limits, or site changes cause repeated failures.

**Mitigation:**
- **Detailed LEARNINGS.md:** Document exact wait times, selectors, patterns
- **Reference Implementation:** Point to minnesota_fdd.py as working example
- **Human Intervention:** Agent asks blocker questions, human provides quick fix
- **Graceful Degradation:** PRD specifies "metadata-only mode" as fallback

**Example Blocker:**
```markdown
# comms/outbox/blocker-wisconsin-timeout.md

I'm getting timeouts when searching Wisconsin DFI. The page loads
but the GridView doesn't appear within 10 seconds.

Current wait: WebDriverWait(driver, 10)
Should I increase timeout or try different approach?

- Worker Agent, Cycle 34
```

### Risk 2: Context Too Large (Complex Codebase)

**Risk:** Scout codebase grows large, fresh context loading becomes slow.

**Mitigation:**
- **Modular PRDs:** Build one scraper at a time (smaller context)
- **File Filtering:** Load only relevant files (tools/ directory, not data/)
- **Git Log Limits:** Only last 20 commits, not full history
- **ARCHITECTURE.md:** High-level overview, agent doesn't need every detail

**Example ARCHITECTURE.md for Scout:**
```markdown
# Scout Architecture

## Directory Structure
- tools/ - Scraper implementations (base.py + specific scrapers)
- outputs/ - Cache and downloaded data (DO NOT LOAD)
- tests/ - Test suites for tools
- docs/ - Research and documentation (REFERENCE ONLY)

## Key Files for Context
- tools/base.py (72 lines) - Tool base class
- tools/minnesota_fdd.py (449 lines) - Reference scraper
- Current task file only (e.g., tools/wisconsin_fdd.py)

## Ignore for Fresh Context
- outputs/* (large cache files)
- data/fdds/*.pdf (large PDFs)
- archive/* (old POC code)
```

### Risk 3: Domain Knowledge Gap (FDD Structure)

**Risk:** Agent doesn't understand FDD-specific concepts (Item 19, franchise law).

**Mitigation:**
- **LEARNINGS.md FDD Primer:** Document FDD structure, Item 19 location, extraction patterns
- **PRD Includes Examples:** Show sample Item 19 text, expected outputs
- **Reference Implementation:** minnesota_fdd.py already has working extraction logic

**Example LEARNINGS.md Section:**
```markdown
# FDD Domain Knowledge

## What is an FDD?
Franchise Disclosure Document - required by FTC for all franchises.
Contains 23 Items, most important for due diligence:

- **Item 19**: Financial Performance Representations (revenue, EBITDA)
  - Location: Usually pages 80-120 in PDF
  - Markers: "Item 19", "Financial Performance", "Average Sales"
  - Format: Tables with unit economics, top/bottom performers

- **Item 7**: Initial Investment
- **Item 6**: Ongoing Fees
- **Item 20**: Outlet Information (# locations)

## Extraction Pattern
1. Open PDF with PyMuPDF
2. Search for "Item 19" and "Item 20" (end marker)
3. Extract pages between markers
4. Return as plain text (no LLM parsing)
```

### Risk 4: Testing Friction (Rate Limits)

**Risk:** Automated tests hit real websites, trigger rate limits, fail CI/CD.

**Mitigation:**
- **Cache-First Tests:** Use cached data for most tests
- **Mocked Responses:** Test parsing logic without hitting real sites
- **Single Live Test:** Only one test per scraper hits real website
- **Rate Limit Handling:** PRD specifies exponential backoff, retry logic

**Example Test Strategy:**
```python
# tests/test_wisconsin_fdd.py

def test_search_with_cache():
    """Fast test using cached results"""
    scraper = WisconsinFDDScraper()
    results = scraper.search("car wash", max_results=5, use_cache=True)
    assert results['total_found'] > 0

def test_parse_gridview_html():
    """Test parsing logic with fixture HTML"""
    html = load_fixture('wisconsin_search_results.html')
    parsed = scraper._parse_results(html)
    assert len(parsed) == 10

@pytest.mark.slow
def test_live_search():
    """Only 1 live test per scraper (hits real website)"""
    scraper = WisconsinFDDScraper()
    results = scraper.search("car wash", max_results=2, use_cache=False)
    assert results['source'] == 'wisconsin_dfi'
```

### Risk 5: Docker/Kilo Code Setup Issues

**Risk:** Local environment differences cause agent container to fail.

**Mitigation:**
- **Phase 1 Validation:** Dedicate 1 full day to setup + simple test
- **Detailed Setup Docs:** Document exact versions, credentials, permissions
- **Fallback:** If agent container doesn't work, fall back to traditional implementation

**Setup Checklist:**
```markdown
## Phase 1 Validation Checklist

- [ ] Docker Desktop installed (v20.10+)
- [ ] Docker Compose installed (v2.0+)
- [ ] Kilo Code account created
- [ ] Kilo Code credentials in ~/.kilocode/
- [ ] Agent container runs simple test PRD
- [ ] Can see TODO.md updating
- [ ] Can see git commits happening
- [ ] Markdown files created (ARCHITECTURE, LEARNINGS)
- [ ] No errors after 10 cycles

**If any item fails: STOP and debug before proceeding.**
```

---

## 12. Cost Analysis

### Traditional Implementation (Current Plan)

**Human Time:**
- Wisconsin scraper: 16-24 hours (2-3 days)
- California scraper: 24-32 hours (3-4 days)
- NASAA FRED scraper: 24-32 hours (3-4 days)
- Aggregator: 8-16 hours (1-2 days)
- Report generators: 24-40 hours (3-5 days)
- **Total: 96-144 hours (12-18 days)**

**At $100/hour developer rate: $9,600 - $14,400**

### Agent Container Implementation

**Setup Time (Human):**
- Phase 1 setup: 8 hours (1 day)
- PRD writing: 2-4 hours per component
- Blocker responses: 2-4 hours per component
- Validation: 2-4 hours per component
- **Total: ~40-60 hours (5-7 days)**

**Agent Runtime (Automated):**
- Wisconsin: 24-48 hours (10+ hours runtime × 2 days)
- California: 24-48 hours
- NASAA FRED: 24-48 hours
- Aggregator: 12-24 hours
- Reports: 48-72 hours
- **Total: ~130-240 hours (but automated, not human time)**

**At $100/hour developer rate: $4,000 - $6,000**

**Savings: $5,600 - $8,400 (58-62% reduction in human time)**

### Kilo Code Costs

[Kilo Code](https://kilo.ai/) is open source (Apache 2.0), but uses third-party AI models:
- **OpenRouter:** ~$0.10-0.50 per 1K tokens (depends on model)
- **Estimated tokens per cycle:** 10K-20K input + 5K-10K output
- **Estimated cost per cycle:** $2-5
- **Total for 100 cycles (typical scraper build):** $200-500

**Total Agent Container Cost: $4,200 - $6,500 (human time + AI)**

**Still 46-55% cheaper than traditional implementation.**

---

## 13. Recommendations

### ✅ Proceed with Agent Container POC

**Why:**
1. **Clear Use Case:** Multi-state FDD scraper pipeline is well-defined, modular, has reference implementation
2. **Significant Time Savings:** 58-62% reduction in human coding time
3. **Low Setup Cost:** 1 day to validate, can abort if doesn't work
4. **Proven Technology:** Agent container has demonstrated 10+ hour runs, 4-6 tasks/hour
5. **Scout-Friendly Architecture:** Modular scrapers, clear patterns, existing reference (minnesota_fdd.py)

### Phase 1: Quick Validation (1 day)

**Goal:** Confirm agent container works in local environment

**Steps:**
1. Clone repo, install dependencies
2. Run simple test PRD (not Scout-related)
3. Verify loop runs 10 cycles successfully
4. Check markdown updates, git commits
5. **Decision point:** If Phase 1 succeeds → proceed to Phase 2. If fails → debug or fallback to traditional.

### Phase 2: Wisconsin FDD Scraper POC (2-3 days)

**Goal:** Validate agent can build real Scout component

**Why Wisconsin:**
- Simplest FDD scraper (well-documented API)
- Clear success criteria (find 10+ car wash FDDs)
- Low risk (can still build other scrapers traditionally if fails)

**Decision point:** If Wisconsin succeeds → continue with agent container for California + NASAA + aggregator. If fails → implement remaining scrapers traditionally.

### Phase 3+: Scale to Full Pipeline

**If Phase 2 succeeds:**
- Use agent container for California, NASAA FRED, aggregator
- Refine PRDs based on Wisconsin learnings
- Continue with report generators

**If Phase 2 fails:**
- Implement remaining scrapers traditionally (original plan)
- Still gained learning from POC
- Can revisit agent container for future projects

---

## 14. Alternative: Hybrid Approach

### If Full Automation Doesn't Work

**Option:** Use agent container for *scaffolding*, human for *refinement*

**Workflow:**
1. Agent generates 70-80% complete scraper (30 min - 2 hours)
2. Human reviews, fixes edge cases (2-4 hours)
3. Human writes tests, validates (2-4 hours)
4. **Total: 4-10 hours per scraper (vs 16-32 hours traditionally)**

**Example:**
- Agent implements Wisconsin scraper structure, form filling, basic parsing
- Human adds rate limit handling, fixes GridView parsing quirks, writes comprehensive tests
- Still 60-70% time savings, but human ensures quality

---

## 15. Success Metrics

### Phase 1 (Setup Validation)

- [ ] Agent container runs 10 cycles without errors
- [ ] TODO.md updates visible after each cycle
- [ ] Git commits happening automatically
- [ ] ARCHITECTURE.md and LEARNINGS.md created
- [ ] No Docker or Kilo Code credential issues

**Timeline:** 1 day
**Go/No-Go:** If fails, debug or abort. Don't proceed to Phase 2.

### Phase 2 (Wisconsin Scraper POC)

- [ ] tools/wisconsin_fdd.py created and runnable
- [ ] Can search "car wash" and find 10+ Wisconsin FDDs
- [ ] Follows minnesota_fdd.py pattern (inherits from base.py)
- [ ] Has 90-day caching working
- [ ] Passes basic test suite
- [ ] <5 human interventions (blocker questions)

**Timeline:** 2-3 days
**Go/No-Go:** If succeeds, continue to Phase 3. If fails, implement remaining scrapers traditionally.

### Phase 3 (Full Pipeline)

- [ ] All 4 FDD scrapers working (MN, WI, CA, NASAA)
- [ ] Aggregator deduplicates results correctly
- [ ] Can query "car wash" and get 50+ results across all states
- [ ] >80% success rate on 20 test queries
- [ ] <5 minutes per 10 results per state
- [ ] Total human time <60 hours (vs 96-144 traditional)

**Timeline:** 10-15 days total (including Phases 1-2)
**Success:** Achieved multi-state FDD pipeline in half the human time.

---

## 16. Sources & References

**Agent Coding Container Concept:**
- [Anthropic Claude Autonomous Coding](https://github.com/anthropics/claude-quickstarts/tree/main/autonomous-coding)
- [leonvanzyl/autonomous-coding](https://github.com/leonvanzyl/autonomous-coding) - Two-agent pattern (initializer + worker)
- [Multi-Agent Coding System](https://github.com/Danau5tin/multi-agent-coding-system) - Reached #13 on Stanford Terminal Bench

**Kilo Code Platform:**
- [Kilo Code Documentation](https://kilo.ai/docs)
- [Kilo Code GitHub](https://github.com/Kilo-Org/kilocode) - 1.5M+ users, Apache 2.0 license
- [Kilo Code Features](https://kilo.ai/features) - 400+ AI models via OpenRouter

**Container Isolation:**
- [Container Use by Dagger](https://www.infoq.com/news/2025/08/container-use/) - Parallel agent workflows

**Scout Project Context:**
- `/Users/andylee/Projects/micro-pe/scout/tools/minnesota_fdd.py` - Reference implementation (449 lines)
- `/Users/andylee/Projects/micro-pe/scout/docs/RESEARCH.md` - Multi-state FDD research (17KB)
- `/Users/andylee/.claude/plans/tender-launching-sparkle.md` - Multi-state scraper plan (10-15 days)

---

## 17. Next Steps

**Immediate (User Decision Required):**
1. Review this research document
2. Decide: Proceed with Phase 1 POC or stick with traditional implementation?
3. If proceed: Schedule 1 day for Phase 1 setup + validation

**If Approved:**
1. Clone agent-coding-container repo
2. Install Docker + Kilo Code credentials
3. Run Phase 1 validation (simple test PRD)
4. Report results → Go/No-Go for Phase 2

**If Rejected:**
1. Resume traditional implementation (Wisconsin scraper first)
2. Follow original plan from tender-launching-sparkle.md
3. Consider agent container for future projects

---

**End of Research Document**
**Author:** Claude Sonnet 4.5
**Date:** February 17, 2026
