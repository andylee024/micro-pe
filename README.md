# Scout

Scout is a data pipeline for SMB (small and medium business) acquisition research. Given a natural-language query like *"HVAC businesses in Los Angeles"*, it pulls data from multiple sources, normalizes it into a unified dataset, and stores it locally in SQLite.

## What it does

Scout runs an ETL pipeline that fans out across three data sources in parallel:

| Source | What it collects |
|---|---|
| **BizBuySell** | Business-for-sale listings (price, cash flow, broker, etc.) |
| **Google Maps** | Nearby businesses (address, phone, website, rating, reviews) |
| **Reddit** | Community sentiment signals for the industry/location |

Each source is scraped, normalized into canonical `Listing` or `Business` models, validated, and persisted to a local SQLite database. The output is a `MarketDataset` containing businesses, listings, sentiment signals, and per-source coverage stats.

## Quick start

```bash
# Clone and set up
cd scout
python3 -m venv venv && source venv/bin/activate
pip install -e .

# Configure API keys
cp .env.example .env
# Edit .env with your Google Maps, OpenCorporates, and Anthropic keys

# Run a query
scout run "HVAC businesses in Los Angeles"
```

Output looks like:

```
run_id: abc123
industry: hvac
location: los angeles
businesses: 42
listings: 18
source=google_maps status=success records=42 duration_ms=3200
source=bizbuysell status=success records=18 duration_ms=5100
source=reddit status=success records=0 duration_ms=1800
```

## Project structure

```
scout/
├── scout/                  # Application package
│   ├── main.py             # CLI entry point (Click)
│   ├── pipeline/
│   │   ├── runner.py       # Configures sources + store, kicks off a run
│   │   ├── workflow.py     # ETL orchestration (fetch → normalize → persist)
│   │   ├── models/         # Domain models (Query, Business, Listing, MarketDataset)
│   │   ├── data_sources/   # Pipeline-level source adapters
│   │   └── data_store/     # Persistence layer (SQLite)
│   ├── domain/             # Shared domain types
│   └── shared/             # Utilities (query parsing, etc.)
├── data_sources/           # Raw scraper implementations
│   ├── marketplaces/       # BizBuySell scraper + validation + SQLite store
│   ├── maps/               # Google Maps / Places API
│   ├── fdd/                # Franchise Disclosure Document extractors
│   ├── sentiment/          # Reddit sentiment analysis
│   ├── registry/           # State business registries
│   └── shared/             # Shared scraper utilities
├── tests/                  # Pytest suite (mirrors source structure)
├── scripts/                # One-off validation and playground scripts
├── docs/                   # Architecture notes and feature specs
├── outputs/                # Cached results and exports (gitignored)
├── pyproject.toml          # Package config, tool settings
└── requirements.txt        # Pinned dependencies
```

## Key concepts

- **Query** -- A parsed user request (industry + location + options).
- **DataSource** -- An adapter that can `fetch` raw data and `normalize` it into domain models.
- **Workflow** -- Iterates over data sources, runs fetch/normalize/persist for each one, and assembles the final `MarketDataset`.
- **Runner** -- Top-level entry point that wires up the default sources and store, then calls the workflow.
- **MarketDataset** -- The output of a pipeline run: businesses, listings, signals, and coverage stats.

## API keys

Copy `.env.example` to `.env` and fill in:

| Key | Required for | Where to get it |
|---|---|---|
| `GOOGLE_MAPS_API_KEY` | Google Maps source | [Google Cloud Console](https://console.cloud.google.com/) (enable Places API) |
| `OPENCORPORATES_API_TOKEN` | Business registry lookups | [OpenCorporates](https://opencorporates.com/api_accounts/new) (free: 500 req/day) |
| `ANTHROPIC_API_KEY` | FDD document extraction | [Anthropic Console](https://console.anthropic.com/) |

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest -v

# Run live integration tests (hits real APIs)
SCOUT_LIVE_TESTS=1 pytest tests/data_sources/test_smoke.py -v

# Format and lint
black .
ruff check .
```

## CLI reference

```bash
scout run "HVAC businesses in Los Angeles"       # default: up to 100 results, cache enabled
scout run "plumbing in Texas" --max-results 50    # limit results
scout run "car wash in California" --no-cache     # skip cache, force fresh scrape
```
