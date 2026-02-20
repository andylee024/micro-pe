# Scout: Current Architecture

**Last Updated:** 2026-02-19
**Current Version:** V0 (MVP)
**Status:** Working terminal with Google Maps integration

---

## System Overview

```
┌──────────────────────────────────────────────────────────────────┐
│  USER                                                             │
│  $ scout research "HVAC in Los Angeles"                          │
└──────────────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────────────┐
│  CLI LAYER (Click)                                               │
│  File: scout/scout/main.py                                       │
│                                                                   │
│  • Parse command arguments                                        │
│  • Validate API keys                                              │
│  • Route to terminal UI or simple CLI mode                       │
└──────────────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────────────┐
│  QUERY PARSER                                                     │
│  File: scout/scout/utils/query_parser.py                         │
│                                                                   │
│  "HVAC in Los Angeles" → industry="HVAC", location="Los Angeles"│
└──────────────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────────────┐
│  TERMINAL UI (Rich + Prompt Toolkit)                             │
│  File: scout/scout/ui/terminal.py                                │
│                                                                   │
│  ┌────────────────────────────────────────────────┐             │
│  │ Scout - Market Research                        │             │
│  │ Query: HVAC in Los Angeles                     │             │
│  ├────────────────────────────────────────────────┤             │
│  │                                                 │             │
│  │ 📊 Building universe...                         │             │
│  │    ✓ Found 487 businesses                      │             │
│  │                                                 │             │
│  │ # Name              Phone         Website      │             │
│  │ 1 Cool Air HVAC     555-0100     coolair.com  │             │
│  │ 2 Premier Climate   555-0200     premier.com  │             │
│  │                                                 │             │
│  │ [↑↓] Navigate [E] Export [Q] Quit [H] Help    │             │
│  └────────────────────────────────────────────────┘             │
│                                                                   │
│  Components:                                                      │
│  • BusinessTable (scrollable list)                               │
│  • StatusBar (cache status, count)                               │
│  • HelpPanel (keyboard shortcuts)                                │
│  • Keyboard handler (j/k, E, Q, H)                               │
└──────────────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────────────┐
│  DATA LAYER                                                       │
│                                                                   │
│  Google Maps Tool                                                 │
│  File: tools/google_maps_tool.py                                 │
│  ├─ Search Google Maps Places API                                │
│  ├─ Get place details                                             │
│  ├─ Cache results (90 days)                                       │
│  └─ Return: name, address, phone, website, rating, reviews       │
│                                                                   │
│  Cache Storage                                                    │
│  Location: ~/.scout/cache/                                        │
│  Format: JSON files                                               │
│  TTL: 90 days                                                     │
└──────────────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────────────┐
│  OUTPUT                                                           │
│                                                                   │
│  CSV Export                                                       │
│  File: scout/scout/utils/export.py                               │
│  Location: outputs/{industry}_{location}_{date}.csv              │
│  Format: name,address,phone,website,category                     │
└──────────────────────────────────────────────────────────────────┘
```

---

## Component Details

### 1. CLI Layer

**File:** `scout/scout/main.py`

**Purpose:** Command-line interface entry point

**Framework:** Click (Python CLI framework)

**Commands:**
```bash
scout research "HVAC in Los Angeles"
  --no-cache        # Bypass cache, fetch fresh data
  --max-results N   # Limit results (default: 60)
  --no-ui           # Simple CLI mode (no terminal UI)
```

**Flow:**
1. Parse command arguments
2. Validate environment (API keys, config)
3. Parse query into industry + location
4. Launch terminal UI OR simple CLI mode
5. Handle errors gracefully

**Key Functions:**
- `cli()` - Main command group
- `research()` - Research command handler

---

### 2. Query Parser

**File:** `scout/scout/utils/query_parser.py`

**Purpose:** Extract structured data from natural language queries

**Examples:**
```python
"HVAC in Los Angeles"           → industry="HVAC", location="Los Angeles"
"backflow testing Houston TX"   → industry="backflow testing", location="Houston, TX"
"car washes in San Francisco"   → industry="car washes", location="San Francisco"
```

**Algorithm:**
- Split on "in" keyword
- Fallback: Last 1-2 words = location, rest = industry
- Handles variations (with/without "in", different formats)

---

### 3. Terminal UI

**File:** `scout/scout/ui/terminal.py`

**Purpose:** Interactive terminal interface for browsing results

**Framework:**
- Rich (rendering tables, panels, progress)
- Prompt Toolkit (keyboard input, screen management)

**Components:**

#### BusinessTable
- Scrollable list of businesses
- Columns: Name, Phone, Website
- Keyboard navigation (↑↓ or j/k)
- Row highlighting

#### StatusBar
- Shows cache status
- Total business count
- Keyboard shortcuts reminder

#### HelpPanel
- Toggles with H key
- Shows all keyboard shortcuts
- Instructions for export

**Keyboard Bindings:**
- `↑` / `k` - Scroll up
- `↓` / `j` - Scroll down
- `E` - Export to CSV
- `Q` - Quit
- `H` - Toggle help panel

**State Management:**
- `current_row` - Selected row index
- `scroll_offset` - Viewport scroll position
- `show_help` - Help panel visibility
- `businesses` - Data array

---

### 4. Google Maps Integration

**File:** `tools/google_maps_tool.py`

**Purpose:** Fetch business data from Google Maps Places API

**API Used:** Google Maps Places API (New)

**Flow:**
1. Text search for "{industry} in {location}"
2. Extract place IDs from results
3. Fetch place details for each ID
4. Cache results locally
5. Return normalized data

**Data Extracted:**
```python
{
    'name': 'Cool Air HVAC',
    'address': '1234 Wilshire Blvd, Los Angeles, CA',
    'phone': '(310) 555-0100',
    'website': 'https://coolair.com',
    'rating': 4.5,
    'reviews': 245,
    'place_id': 'ChIJ...',
    'lat': 34.0522,
    'lng': -118.2437
}
```

**API Costs:**
- Text search: $32 per 1,000 requests
- Place details: $17 per 1,000 requests
- ~$1.05 per 60 businesses

**Caching:**
- Location: `~/.scout/cache/`
- Format: JSON files
- TTL: 90 days
- Cache key: `{industry}_{location}_hash.json`

---

### 5. Cache System

**Location:** `~/.scout/cache/`

**Structure:**
```
~/.scout/
├── cache/
│   ├── hvac_los_angeles_abc123.json
│   ├── backflow_houston_def456.json
│   └── ...
└── config/
    └── settings.json
```

**Cache File Format:**
```json
{
    "query": {
        "industry": "HVAC",
        "location": "Los Angeles",
        "timestamp": "2026-02-19T10:30:00Z"
    },
    "results": [
        {
            "name": "Cool Air HVAC",
            "address": "...",
            ...
        }
    ],
    "metadata": {
        "total_found": 487,
        "api_cost": 1.05
    }
}
```

**Cache Strategy:**
- Write through (cache on first fetch)
- Check freshness (90-day TTL)
- Invalidate on `--no-cache` flag

---

### 6. CSV Export

**File:** `scout/scout/utils/export.py`

**Purpose:** Export business data to CSV for mail merge / CRM import

**Format:**
```csv
name,address,phone,website,category
Cool Air HVAC,"1234 Wilshire Blvd, Los Angeles, CA",(310) 555-0100,coolair.com,HVAC
Premier Climate,"456 Main St, Santa Monica, CA",(310) 555-0200,premierclimate.com,HVAC
```

**File Naming:**
- Pattern: `{industry}_{location}_{YYYY-MM-DD}.csv`
- Example: `hvac_los_angeles_2026-02-19.csv`
- Location: `outputs/`

**Features:**
- Unicode support
- Handles missing fields (N/A)
- Creates output directory if doesn't exist
- Returns export path for user feedback

---

### 7. Error Handling

**File:** `scout/scout/utils/errors.py`

**Purpose:** User-friendly error messages, no stack traces

**Custom Exceptions:**
```python
ConfigurationError  # Missing API keys, bad config
ValidationError     # Invalid query format
APIError           # Google Maps API failures
NetworkError       # Connection issues
FileIOError        # Can't write CSV
```

**Error Formatting:**
```
❌ Error: Google Maps API key not found

   Please add GOOGLE_MAPS_API_KEY to your .env file

   Get API key: https://console.cloud.google.com/
```

**Features:**
- Emoji indicators (❌ ✅)
- Clear error messages
- Actionable hints
- No stack traces shown to users

---

## Data Flow

### Happy Path (Cached Query)

```
User: scout research "HVAC in Los Angeles"
  ↓
Parse: industry="HVAC", location="Los Angeles"
  ↓
Check cache: FOUND (age: 2 days)
  ↓
Load from cache: 487 businesses
  ↓
Terminal UI: Display table
  ↓
User: Press E (export)
  ↓
Export to CSV: outputs/hvac_los_angeles_2026-02-19.csv
  ↓
Success: ✅ Exported 487 businesses
```

**Total time:** <1 second

---

### Happy Path (Fresh Query)

```
User: scout research "backflow testing in Houston"
  ↓
Parse: industry="backflow testing", location="Houston"
  ↓
Check cache: NOT FOUND
  ↓
Google Maps API: Search for "backflow testing in Houston"
  ↓
Found 67 businesses
  ↓
Fetch details for 67 businesses (batched)
  ↓
Write to cache: ~/.scout/cache/backflow_houston_xyz.json
  ↓
Terminal UI: Display table
```

**Total time:** ~3-5 seconds

---

## Technology Stack

### Core Dependencies

**Python Libraries:**
- `click` - CLI framework
- `rich` - Terminal rendering (tables, panels, progress)
- `prompt_toolkit` - Keyboard input, screen management
- `python-dotenv` - Environment variable management
- `googlemaps` - Google Maps API client

**APIs:**
- Google Maps Places API (New)

**File Formats:**
- JSON (cache storage)
- CSV (export format)
- ENV (configuration)

---

## Configuration

**File:** `.env` in project root

```bash
# Required
GOOGLE_MAPS_API_KEY=your_key_here

# Optional
CACHE_DIR=~/.scout/cache
CACHE_TTL_DAYS=90
MAX_RESULTS_DEFAULT=60
```

**Config Loading:**
1. Check `.env` file
2. Fall back to environment variables
3. Use defaults if not set

---

## Testing

**Framework:** pytest

**Coverage:**
- Unit tests: `scout/tests/test_export.py`
- Integration tests: `scout/tests/test_integration.py`
- Total: 29 tests passing

**Test Categories:**
- CSV export functionality
- Error handling
- Query parsing
- Large datasets (500+ businesses)
- Unicode handling

---

## Deployment

**Installation:**
```bash
cd scout
pip install -e .
```

**Creates command:**
```bash
scout research "HVAC in Los Angeles"
```

**Requirements:**
- Python 3.11+
- Google Maps API key (with billing enabled)
- Terminal with Unicode support

---

## Performance

**Current Metrics:**

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Cached query | <1 sec | <1 sec | ✅ |
| Fresh query | <5 sec | 3-5 sec | ✅ |
| Export 500 businesses | <1 sec | <1 sec | ✅ |
| Terminal responsiveness | Instant | Instant | ✅ |

**Bottlenecks:**
- Google Maps API latency (3-5 sec for 60+ businesses)
- Rate limits: None yet (under free tier)

---

## Limitations (Current V0)

### What's Missing

**No financial data:**
- Can't estimate revenue
- Can't show benchmarks
- Can't calculate valuations

**No scoring:**
- Businesses not ranked
- No quality assessment
- No acquisition signals

**No multi-source:**
- Google Maps only
- No Reddit sentiment
- No FDD data

**Simple UI:**
- Table view only
- No business detail screen
- No 4-screen layout

### Known Issues

1. **Windows untested** (should work with WSL)
2. **Large result sets** (500+) not optimized
3. **No pagination** in terminal UI
4. **No filtering/sorting** beyond what's displayed

---

## What's Next

See [roadmap.md](roadmap.md) for Phase 1 features:
- BizBuySell integration
- FDD database
- Enhanced terminal UI with benchmarks

---

## Architecture Decisions

### Why Rich + Prompt Toolkit?
- **Pro:** Fast to implement, good for MVP
- **Pro:** Python ecosystem (matches existing code)
- **Con:** Not as polished as Ink (TypeScript)
- **Decision:** Right choice for MVP, can upgrade later

### Why JSON cache instead of SQLite?
- **Pro:** Simpler (no schema migrations)
- **Pro:** Human-readable
- **Con:** No querying capabilities
- **Decision:** Fine for MVP, will migrate to SQLite in Phase 2

### Why Click instead of Typer?
- **Pro:** Mature, well-documented
- **Pro:** Simple for basic CLI needs
- **Con:** Typer has better type hints
- **Decision:** Click is sufficient for current needs

---

_For strategic direction, see [product_vision.md](product_vision.md)_
_For feature plans, see [roadmap.md](roadmap.md)_
