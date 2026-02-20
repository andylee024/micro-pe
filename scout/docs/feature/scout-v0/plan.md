# Scout V0: Technical Implementation Plan

**Goal:** Build terminal-based universe builder with Rich UI
**Timeline:** Week 1-2 (parallel development with agent teams)
**Outcome:** Working terminal app that finds 500+ businesses and exports to CSV

---

## Executive Summary

V0 brings Scout to life with a terminal UI from day 1. Users will see a professional, Bloomberg-style interface (simple version) that displays business data in a scrollable table with live progress updates.

**What We're Building:**
- Terminal UI using Rich library (not just CLI print-and-exit)
- Google Maps integration to find 500+ businesses
- Scrollable table with keyboard navigation
- CSV export functionality
- 90-day caching for instant repeated searches

**What We're NOT Building (saved for V1+):**
- Multi-screen layout (comes in V3)
- FDD data (comes in V1)
- Google Reviews (comes in V2)
- Reddit sentiment (comes in V3)

---

## Product Specification

### User Experience

**Command:**
```bash
$ scout research "HVAC businesses in Los Angeles"
```

**Terminal Output:**
```
┌──────────────────────────────────────────────────────────────────┐
│ SCOUT - Market Research                                          │
│ Query: HVAC businesses in Los Angeles                            │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│ 📊 Building universe...                                          │
│    ✓ Searching Google Maps                                       │
│    ✓ Found 487 HVAC businesses in Los Angeles area              │
│                                                                  │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│                                                                  │
│ 📋 HVAC Businesses in Los Angeles                  487 results  │
│                                                                  │
│  Name                     Phone             Website              │
│  ────────────────────────────────────────────────────────────────│
│  Cool Air HVAC           (310) 555-0100    coolair.com          │
│  Premier Climate         (310) 555-0200    premierclimate.com   │
│  SoCal Heating & Air     (626) 555-0300    socalheating.com     │
│  Valley Air Experts      (818) 555-0400    valleyairexperts.com │
│  West Coast Climate      (424) 555-0500    westcoastclimate.com │
│  Air Masters Inc         (213) 555-0600    airmastersinc.com    │
│  Quick Cool HVAC         (310) 555-0700    quickcool.com        │
│  Elite Climate Control   (626) 555-0800    eliteclimate.com     │
│  Pro Air Services        (818) 555-0900    proairservices.com   │
│  Golden State HVAC       (424) 555-1000    goldenstateHVAC.com  │
│  ...                                                             │
│                                                                  │
│  Showing 20 of 487 businesses                                    │
│  [↑↓] Scroll  [E]xport CSV  [Q]uit  [H]elp                      │
│                                                                  │
├──────────────────────────────────────────────────────────────────┤
│ Status: Ready • 487 businesses found • Cached for 90 days       │
└──────────────────────────────────────────────────────────────────┘
```

**Key Features:**
1. **Live UI** - Terminal stays open, user can scroll
2. **Progress indicators** - Show what's happening
3. **Keyboard shortcuts** - [↑↓] scroll, [E] export, [Q] quit, [H] help
4. **Status bar** - Shows cache status, result count
5. **Professional look** - Bloomberg-style box drawing, clean layout

---

## Technical Architecture

### File Structure

```
scout/
├── scout/
│   ├── __init__.py
│   ├── main.py                    # CLI entry point (Click)
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── terminal.py           # Rich terminal UI controller
│   │   ├── components.py         # Reusable UI components (panels, tables)
│   │   └── keyboard.py           # Keyboard event handling
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── base.py               # Tool base class (already exists)
│   │   └── google_maps_tool.py   # Google Maps API (already exists)
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── query_parser.py       # Parse "HVAC in Los Angeles"
│   │   └── export.py             # CSV export logic
│   └── config.py                  # Configuration management
├── outputs/                       # CSV exports go here
├── tests/
│   ├── test_main.py
│   ├── test_terminal.py
│   ├── test_query_parser.py
│   └── test_export.py
├── pyproject.toml                 # Package metadata, dependencies
├── README.md
└── .env                           # API keys (GOOGLE_MAPS_API_KEY)
```

### Core Components

#### 1. CLI Entry Point (`scout/main.py`)

**Responsibilities:**
- Parse command-line arguments with Click
- Initialize configuration
- Launch terminal UI

**API:**
```python
@click.group()
def cli():
    """Scout - Bloomberg Terminal for SMB Acquisition"""
    pass

@cli.command()
@click.argument('query', required=True)
@click.option('--no-cache', is_flag=True, help='Bypass cache')
@click.option('--max-results', default=500, help='Max businesses to fetch')
def research(query: str, no_cache: bool, max_results: int):
    """Research a market: scout research "HVAC in Los Angeles" """
    # Parse query
    industry, location = parse_query(query)

    # Launch terminal UI
    terminal = ScoutTerminal(industry, location, use_cache=not no_cache, max_results=max_results)
    terminal.run()
```

**Dependencies:**
- `click` - CLI framework
- Configuration from `config.py`

---

#### 2. Terminal UI Controller (`scout/ui/terminal.py`)

**Responsibilities:**
- Manage Rich Live display
- Coordinate data fetching and UI updates
- Handle keyboard events
- Control application lifecycle

**API:**
```python
class ScoutTerminal:
    def __init__(
        self,
        industry: str,
        location: str,
        use_cache: bool = True,
        max_results: int = 500
    ):
        self.industry = industry
        self.location = location
        self.use_cache = use_cache
        self.max_results = max_results

        self.console = Console()
        self.businesses = []
        self.status = "Initializing..."
        self.scroll_offset = 0

    def run(self):
        """Main entry point - launch terminal UI"""
        with Live(self._build_layout(), console=self.console, refresh_per_second=4) as live:
            self._fetch_data(live)
            self._handle_keyboard_loop(live)

    def _fetch_data(self, live):
        """Fetch data from Google Maps with progress updates"""
        # Update progress: "Searching Google Maps..."
        # Call google_maps_tool.search()
        # Update progress: "Found 487 businesses"

    def _build_layout(self) -> Layout:
        """Build Rich Layout with header, table, footer"""

    def _handle_keyboard_loop(self, live):
        """Handle keyboard events: ↑↓ scroll, E export, Q quit"""
```

**Key Technical Details:**
- **Rich Live Display:** Use `rich.live.Live` for updating UI without clearing screen
- **Layout:** Use `rich.layout.Layout` to organize panels (header, table, footer)
- **Tables:** Use `rich.table.Table` for business data
- **Panels:** Use `rich.panel.Panel` for bordered sections
- **Progress:** Use `rich.progress.Progress` during data fetch
- **Keyboard:** Use `readchar` or `pynput` for non-blocking key events

**Challenges:**
1. **Keyboard input in Live display** - Rich Live blocks by default
   - Solution: Use `live.update()` in keyboard event loop, not continuous refresh
   - Or: Use threads (fetch data in background, keyboard in foreground)

2. **Scrolling** - Rich doesn't have built-in scrolling
   - Solution: Track `scroll_offset`, slice businesses list, redraw table
   - `businesses[scroll_offset:scroll_offset+20]` for display

---

#### 3. UI Components (`scout/ui/components.py`)

**Responsibilities:**
- Reusable UI building blocks
- Consistent styling across screens

**API:**
```python
def create_header(query: str) -> Panel:
    """Create header panel with query"""
    return Panel(
        f"[bold cyan]SCOUT - Market Research[/bold cyan]\n"
        f"Query: {query}",
        style="bold white on blue"
    )

def create_business_table(businesses: List[Dict], offset: int = 0, limit: int = 20) -> Table:
    """Create scrollable business table"""
    table = Table(title=f"Businesses ({len(businesses)} results)", show_header=True)
    table.add_column("Name", style="cyan", no_wrap=False)
    table.add_column("Phone", style="green")
    table.add_column("Website", style="blue")

    for biz in businesses[offset:offset+limit]:
        table.add_row(
            biz['name'],
            biz.get('phone', 'N/A'),
            biz.get('website', 'N/A')
        )

    return table

def create_status_bar(num_businesses: int, cached: bool) -> Panel:
    """Create status bar at bottom"""
    cache_status = "Cached for 90 days" if cached else "Fresh data"
    return Panel(
        f"Status: Ready • {num_businesses} businesses found • {cache_status}",
        style="dim"
    )

def create_progress_panel(message: str) -> Panel:
    """Create progress indicator"""
    return Panel(
        f"📊 {message}",
        style="yellow"
    )
```

**Styling Decisions:**
- **Colors:** Cyan for names, green for phones, blue for websites
- **Borders:** Use box drawing characters for professional look
- **Alignment:** Left-align text, right-align status info
- **Spacing:** 1-line padding inside panels

---

#### 4. Keyboard Handler (`scout/ui/keyboard.py`)

**Responsibilities:**
- Capture keyboard events without blocking
- Map keys to actions

**API:**
```python
class KeyboardHandler:
    def __init__(self, terminal: ScoutTerminal):
        self.terminal = terminal
        self.running = True

    def handle_event_loop(self):
        """Non-blocking keyboard event loop"""
        while self.running:
            key = readchar.readkey()

            if key == readchar.key.UP:
                self.terminal.scroll_up()
            elif key == readchar.key.DOWN:
                self.terminal.scroll_down()
            elif key.lower() == 'e':
                self.terminal.export_csv()
            elif key.lower() == 'q':
                self.terminal.quit()
                self.running = False
            elif key.lower() == 'h':
                self.terminal.show_help()
```

**Key Mappings:**
- `↑` / `↓` - Scroll through businesses
- `E` - Export to CSV
- `Q` - Quit application
- `H` - Show help panel

**Dependencies:**
- `readchar` - Cross-platform keyboard input

---

#### 5. Query Parser (`scout/shared/query_parser.py`)

**Responsibilities:**
- Parse natural language query into industry + location
- Handle variations and edge cases

**API:**
```python
def parse_query(query: str) -> Tuple[str, str]:
    """
    Parse natural language query into (industry, location)

    Examples:
    - "HVAC businesses in Los Angeles" → ("HVAC", "Los Angeles, CA")
    - "car wash in San Diego" → ("car wash", "San Diego, CA")
    - "laundromats near me" → ("laundromat", <current location>)
    """
    # Simple regex-based parsing
    # Look for patterns: "X in Y", "X near Y", "Y X"

    # Extract industry keywords
    # Extract location keywords

    return industry, location
```

**Test Cases:**
- "HVAC businesses in Los Angeles" → ("HVAC", "Los Angeles, CA")
- "car wash in San Diego" → ("car wash", "San Diego, CA")
- "HVAC Los Angeles" → ("HVAC", "Los Angeles, CA")
- "laundromats" → ERROR: location required
- "in Los Angeles" → ERROR: industry required

---

#### 6. CSV Exporter (`scout/shared/export.py`)

**Responsibilities:**
- Export businesses to CSV format
- Generate timestamped filenames
- Handle file I/O errors

**API:**
```python
def export_to_csv(
    businesses: List[Dict],
    industry: str,
    location: str,
    output_dir: Path = Path("outputs")
) -> Path:
    """
    Export businesses to CSV file

    Returns:
        Path to exported CSV file
    """
    # Generate filename: hvac_los_angeles_2026-02-19.csv
    filename = f"{industry.lower().replace(' ', '_')}_{location.lower().replace(' ', '_').replace(',', '')}_{datetime.now().strftime('%Y-%m-%d')}.csv"

    output_path = output_dir / filename
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['name', 'address', 'phone', 'website', 'category'])
        writer.writeheader()
        writer.writerows(businesses)

    return output_path
```

**CSV Format:**
```csv
name,address,phone,website,category
Cool Air HVAC,"1234 Wilshire Blvd, Los Angeles, CA 90010",(310) 555-0100,coolair.com,HVAC
Premier Climate,"456 Main St, Santa Monica, CA 90401",(310) 555-0200,premierclimate.com,HVAC
```

---

#### 7. Configuration (`scout/config.py`)

**Responsibilities:**
- Load environment variables
- Manage API keys
- Define constants

**API:**
```python
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

# API Keys
GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
OUTPUT_DIR = PROJECT_ROOT / "outputs"
CACHE_DIR = PROJECT_ROOT / "cache"

# Constants
CACHE_TTL_DAYS = 90
MAX_RESULTS_DEFAULT = 500

# Validation
if not GOOGLE_MAPS_API_KEY:
    raise ValueError("GOOGLE_MAPS_API_KEY not found in .env file")
```

---

## Technical Milestones

### Milestone 1: CLI Framework (Day 1)

**Goal:** Get basic CLI working with Click

**Tasks:**
1. Set up project structure
2. Create `scout/main.py` with Click commands
3. Create `scout/config.py` for configuration
4. Create `scout/shared/query_parser.py`
5. Write tests for query parser

**Deliverable:**
```bash
$ scout research "HVAC in Los Angeles"
Industry: HVAC
Location: Los Angeles, CA
(no UI yet, just prints parsed query)
```

**Acceptance Criteria:**
- `scout research` command exists
- Query parsing works for 5+ test cases
- Config loads API key from .env
- All tests pass

---

### Milestone 2: Google Maps Integration (Day 2-3)

**Goal:** Fetch business data from Google Maps

**Tasks:**
1. Ensure `data_sources/maps/google_maps.py` works (already exists)
2. Test with real API call: "HVAC in Los Angeles"
3. Verify 500+ businesses returned
4. Add caching (90-day TTL)
5. Write integration tests

**Deliverable:**
```bash
$ scout research "HVAC in Los Angeles"
Searching Google Maps...
Found 487 businesses
(prints list to console, no UI yet)
```

**Acceptance Criteria:**
- Google Maps API returns 500+ businesses
- Results cached for 90 days (2nd call instant)
- Data structure: List[Dict] with name, address, phone, website
- Integration test passes

---

### Milestone 3: Rich UI - Basic Layout (Day 4-5)

**Goal:** Terminal UI displays business data in table

**Tasks:**
1. Create `scout/ui/terminal.py` with ScoutTerminal class
2. Create `scout/ui/components.py` with UI helpers
3. Implement Rich Live display
4. Build header panel, table, status bar
5. Display first 20 businesses

**Deliverable:**
```bash
$ scout research "HVAC in Los Angeles"
(Terminal launches with Rich UI showing table)
```

**Acceptance Criteria:**
- Terminal UI displays with header, table, status bar
- Shows first 20 businesses in table
- Professional look with borders and colors
- UI updates don't flicker

---

### Milestone 4: Keyboard Navigation & Scrolling (Day 6-7)

**Goal:** User can scroll through all businesses

**Tasks:**
1. Create `scout/ui/keyboard.py` for keyboard handling
2. Implement scroll up/down (↑↓ keys)
3. Track scroll offset, update table display
4. Add keyboard shortcuts (E, Q, H)
5. Handle edge cases (scroll past end)

**Deliverable:**
```bash
$ scout research "HVAC in Los Angeles"
(Terminal UI with working scroll, export, quit)
User presses ↓ → next 20 businesses
User presses E → CSV exported
User presses Q → exits cleanly
```

**Acceptance Criteria:**
- ↑↓ keys scroll through all 487 businesses
- E key exports to CSV
- Q key quits cleanly
- H key shows help panel
- No crashes or UI glitches

---

### Milestone 5: CSV Export (Day 8)

**Goal:** Export businesses to CSV file

**Tasks:**
1. Create `scout/shared/export.py`
2. Implement CSV export with proper formatting
3. Generate timestamped filenames
4. Display success message in UI
5. Write tests

**Deliverable:**
```bash
$ scout research "HVAC in Los Angeles"
(User presses E)
✅ Exported to: outputs/hvac_los_angeles_2026-02-19.csv
   Columns: name, address, phone, website, category
   Rows: 487 businesses
```

**Acceptance Criteria:**
- CSV file created in `outputs/` directory
- Proper format with headers
- All 487 businesses exported
- Filename includes industry, location, date
- Success message shown in UI

---

### Milestone 6: Polish & Testing (Day 9-10)

**Goal:** Production-ready V0

**Tasks:**
1. Error handling (API failures, network issues)
2. Loading states and progress indicators
3. Help panel ([H] key)
4. Comprehensive testing (unit + integration)
5. Documentation (README, inline comments)
6. Performance optimization (lazy loading?)

**Deliverable:**
- Fully working V0 terminal app
- All tests passing (>80% coverage)
- README with installation and usage
- Handles errors gracefully

**Acceptance Criteria:**
- Graceful error messages (no crashes)
- Help panel accessible via [H]
- All tests pass
- README complete
- 5 manual test cases validated

---

## Agent Team Structure

### Team Lead (Coordinator)
**Role:** Orchestrate development, review code, integrate components

**Responsibilities:**
- Create and assign tasks
- Review PRs from teammates
- Resolve blockers
- Final integration and testing
- Ensure consistency across codebase

---

### Teammate 1: CLI & Configuration Developer
**Focus:** Milestones 1 & 2 (CLI framework, Google Maps integration)

**Files to Create:**
- `scout/main.py`
- `scout/config.py`
- `scout/shared/query_parser.py`
- `tests/test_query_parser.py`

**Tasks:**
1. Set up project structure (pyproject.toml, folder layout)
2. Implement Click CLI with `research` command
3. Build query parser (natural language → industry + location)
4. Set up configuration (load API keys from .env)
5. Integrate Google Maps tool (already exists, ensure it works)
6. Add caching (90-day TTL)
7. Write tests

**Success Criteria:**
- `scout research "HVAC in Los Angeles"` fetches 500+ businesses
- Query parser handles 10+ test cases
- Results cached for 90 days

---

### Teammate 2: Terminal UI Developer
**Focus:** Milestones 3 & 4 (Rich UI, keyboard navigation)

**Files to Create:**
- `scout/ui/terminal.py`
- `scout/ui/components.py`
- `scout/ui/keyboard.py`
- `tests/test_terminal.py`

**Tasks:**
1. Create ScoutTerminal class with Rich Live display
2. Build UI components (header, table, status bar)
3. Implement keyboard handling (↑↓ scroll, E export, Q quit, H help)
4. Add scrolling logic (track offset, slice businesses list)
5. Ensure professional look (colors, borders, layout)
6. Write tests

**Success Criteria:**
- Terminal UI displays business table
- User can scroll through all 487 businesses with ↑↓
- Keyboard shortcuts work (E, Q, H)
- UI is responsive and doesn't flicker

---

### Teammate 3: Export & Polish Developer
**Focus:** Milestones 5 & 6 (CSV export, error handling, polish)

**Files to Create:**
- `scout/shared/export.py`
- `tests/test_export.py`
- Additional error handling in existing files
- README.md

**Tasks:**
1. Implement CSV export functionality
2. Generate timestamped filenames
3. Add error handling (API failures, network issues, file I/O)
4. Create help panel ([H] key)
5. Write comprehensive tests (unit + integration)
6. Write README with installation and usage instructions
7. Performance testing and optimization

**Success Criteria:**
- CSV export works correctly (all businesses, proper format)
- Graceful error messages (no crashes)
- Help panel accessible
- README complete
- >80% test coverage

---

## Dependencies

### Python Packages

**Required:**
```toml
[project]
dependencies = [
    "click>=8.0",           # CLI framework
    "rich>=13.0",           # Terminal UI
    "readchar>=4.0",        # Keyboard input
    "requests>=2.28",       # HTTP requests (for Google Maps)
    "python-dotenv>=1.0",   # Environment variables
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",          # Testing framework
    "pytest-cov>=4.0",      # Coverage reporting
    "black>=23.0",          # Code formatting
    "ruff>=0.1",            # Linting
]
```

**Already Available:**
- `data_sources/maps/google_maps.py` - Google Maps integration (existing)
- `tools/base.py` - Tool base class with caching (existing)

---

## Testing Strategy

### Unit Tests

**Query Parser (`test_query_parser.py`):**
```python
def test_parse_standard_query():
    assert parse_query("HVAC in Los Angeles") == ("HVAC", "Los Angeles, CA")

def test_parse_variations():
    assert parse_query("car wash near San Diego") == ("car wash", "San Diego, CA")
    assert parse_query("HVAC Los Angeles") == ("HVAC", "Los Angeles, CA")

def test_parse_errors():
    with pytest.raises(ValueError):
        parse_query("in Los Angeles")  # Missing industry
```

**CSV Export (`test_export.py`):**
```python
def test_export_creates_file():
    businesses = [{"name": "Test HVAC", "phone": "123-456-7890", ...}]
    path = export_to_csv(businesses, "HVAC", "Los Angeles")
    assert path.exists()
    assert "hvac" in path.name.lower()
```

### Integration Tests

**End-to-End (`test_integration.py`):**
```python
def test_full_pipeline():
    # Mock Google Maps API
    # Run scout research command
    # Verify terminal UI launches
    # Verify businesses displayed
    # Simulate export
    # Verify CSV created
```

### Manual Test Cases

1. **Happy Path:** `scout research "HVAC in Los Angeles"` → 500+ businesses, export works
2. **Cache Hit:** Run same query twice → 2nd run instant (cached)
3. **Scrolling:** Scroll through all 487 businesses → no crashes
4. **Export:** Press E → CSV created with all businesses
5. **Error Handling:** Disconnect internet → graceful error message

---

## Success Metrics

### Code Quality
- [ ] All tests pass (>80% coverage)
- [ ] No lint errors (ruff passes)
- [ ] Code formatted (black passes)
- [ ] Type hints on public APIs

### User Experience
- [ ] Terminal UI looks professional (Bloomberg-style)
- [ ] Keyboard shortcuts intuitive (↑↓, E, Q, H)
- [ ] Fast (<2 seconds for cached query)
- [ ] No crashes or glitches

### Functional Requirements
- [ ] Finds 500+ businesses for typical query
- [ ] Exports all businesses to CSV
- [ ] Caching works (90-day TTL)
- [ ] Error messages helpful

### Validation
- [ ] 5 teammates test and approve
- [ ] Works on macOS, Linux, Windows (WSL)
- [ ] README clear enough for new users

---

## Risk Mitigation

**Risk: Rich Live display blocks keyboard input**
- Mitigation: Use threading or event-driven architecture
- Alternative: Use `rich.console.Console` without Live (refresh manually)

**Risk: Google Maps API rate limits**
- Mitigation: Implement caching aggressively (90-day TTL)
- Alternative: Batch requests, use API key with higher quota

**Risk: Scrolling performance with 500+ businesses**
- Mitigation: Only render visible slice (20 businesses at a time)
- Alternative: Implement pagination instead of scrolling

**Risk: Team coordination overhead**
- Mitigation: Clear file ownership (no overlapping files)
- Teammate 1: CLI/config, Teammate 2: UI, Teammate 3: Export/polish

**Risk: Testing terminal UI is hard**
- Mitigation: Separate business logic from UI (testable in isolation)
- Use mocks for terminal output in tests

---

## Timeline Estimate

**With Agent Teams (Parallel):**
- Milestone 1-2 (CLI + Google Maps): Day 1-3 - Teammate 1
- Milestone 3-4 (Rich UI + keyboard): Day 3-7 - Teammate 2
- Milestone 5-6 (Export + polish): Day 7-10 - Teammate 3
- Integration & Testing: Day 9-10 - Team Lead
- **Total: 10 days (2 weeks)**

**Without Agent Teams (Sequential):**
- Milestones 1-6 done sequentially: 15-20 days

**Speedup: 1.5-2x faster with agent teams**

---

## Next Steps

1. **Review this plan** - Approve or provide feedback
2. **Spawn agent team** - 3 teammates + lead
3. **Assign milestones** - Each teammate claims their focus area
4. **Parallel development** - All work simultaneously
5. **Daily standups** - Progress updates, blocker resolution
6. **Integration** - Team lead integrates all components (Day 9-10)
7. **Testing** - Validate with 5 teammates
8. **Ship V0** - Release to teammates, gather feedback
9. **Plan V1** - Use feedback to scope financial intelligence features

---

## Questions Before Starting

1. **Google Maps API** - Do we have API key with sufficient quota (500 requests/day)?
2. **Terminal Compatibility** - Should we support Windows natively or only WSL?
3. **Export Format** - CSV only, or also JSON/Excel?
4. **Caching Strategy** - SQLite or just pickle files?
5. **Help Panel** - Inline or separate screen?

---

**Ready to build V0?** Let's spawn the agent team and start coding!
