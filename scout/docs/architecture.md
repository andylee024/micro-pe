# Scout Architecture

**Purpose:** Help new contributors understand how the codebase is organized and how it supports the PRD vision.
**Last Updated:** 2026-02-20

---

## 1) Overview

Scout is a terminal‑first intelligence tool for SMB acquisition. The architecture is layered to keep product logic separate from data acquisition, so we can evolve sources independently while preserving a stable app core.

**Core layers**
1. **CLI/UI** — terminal experience
2. **Application** — use‑case orchestration
3. **Domain** — core models
4. **Adapters** — translate external data into domain
5. **Data Sources** — concrete scrapers/APIs

---

## 2) Repository Layout

```
scout/
├── scout/                 # App package
│   ├── main.py            # CLI entry point
│   ├── ui/                # Terminal UI
│   ├── application/       # Use cases (orchestration)
│   ├── domain/            # Domain models
│   ├── adapters/          # Interfaces to data sources
│   └── shared/            # App‑level utilities (errors, export, parsing)
│
├── data_sources/          # Data acquisition (scrapers/tools)
│   ├── maps/
│   ├── marketplaces/
│   ├── fdd/
│   ├── sentiment/
│   └── shared/            # Data‑source infra (base, config, errors)
│
├── tests/                 # Tests mirror layout
│   ├── scout/
│   ├── data_sources/
│   └── shared/
│
└── docs/                  # Product + feature docs (see prd.md)
```

---

## 3) Runtime Flow (Scout Research)

```
CLI (scout/main.py)
  → parse query (scout/shared/query_parser.py)
  → ResearchMarket use case (scout/application/research_market.py)
    → GoogleMapsAdapter (scout/adapters/maps.py)
      → GoogleMapsTool (data_sources/maps/google_maps.py)
    → BizBuySellAdapter (scout/adapters/bizbuysell.py)
      → BizBuySellTool (data_sources/marketplaces/bizbuysell.py)
    → RedditSearchAdapter (scout/adapters/reddit.py)
  → UI render (scout/ui/terminal.py)
  → Export CSV (scout/shared/export.py)
```

This flow aligns with the PRD: input a thesis → multi‑source data → ranked/usable output via terminal UI.

---

## 4) Key Modules

**CLI**
- `scout/main.py` — Click commands and argument parsing.

**UI**
- `scout/ui/terminal.py` — Rich‑based UI controller.
- `scout/ui/components.py` — UI panels/layout.
- `scout/ui/keyboard.py` — input handling.
  - Vim‑like keys supported: `j/k`, `gg/G`, `Ctrl+U/Ctrl+D`.

**Application (Use Cases)**
- `scout/application/research_market.py` — core orchestration for research queries.
- `scout/application/benchmarking.py` — benchmark calculations.

**Domain**
- `scout/domain/models.py` — `Business`, `Benchmark`, `MarketSummary`, `ResearchResult`.

**Adapters**
- `scout/adapters/maps.py` — maps → `Business`.
- `scout/adapters/bizbuysell.py` — listings for benchmarks.
- `scout/adapters/reddit.py` — pulse summaries.

**Data Sources (Acquisition Layer)**
- `data_sources/maps/` — Google Maps search + reviews.
- `data_sources/marketplaces/` — BizBuySell scraping.
- `data_sources/fdd/` — state FDD scrapers + aggregator.
- `data_sources/sentiment/` — Reddit sentiment.
- `data_sources/shared/` — base `Tool`, config, errors.

**Data Source Smoke Tests**
- `tests/data_sources/test_smoke.py` — one live smoke test per data source.
- Run with `SCOUT_LIVE_TESTS=1 pytest tests/data_sources/test_smoke.py -v`.

---

## 5) Cross‑Cutting Concerns

**Caching**
- Implemented in `data_sources/shared/base.py`.
- Each tool controls TTLs; cache stored under `outputs/cache/`.

**Config & Secrets**
- Data‑source settings: `data_sources/shared/config.py`.
- App settings: `scout/shared/settings.py`.
- API keys via `.env` (Google Maps, Reddit, etc.).

**Errors**
- App errors: `scout/shared/errors.py`.
- Data‑source errors: `data_sources/shared/errors.py`.

---

## 6) How This Supports the PRD

The PRD emphasizes time‑to‑conviction and data fusion. This architecture enforces:
- **Separation of concerns** — data acquisition can evolve without breaking UI.
- **Composable use cases** — research workflow can add sources incrementally.
- **Terminal‑first UX** — UI is isolated and can iterate quickly.

---

## 7) Onboarding Quick Start

```bash
pip install -e .
scout research "HVAC in Los Angeles"
```

If you want to run without UI:
```bash
scout research "HVAC in Los Angeles" --no-ui
```

If you want to iterate on UI with mock data:
```bash
scout research "HVAC in Los Angeles" --mock-data
```

---

## 8) Where to Add New Work

- **New data source:** add under `data_sources/` and expose via an adapter in `scout/adapters/`.
- **New workflow:** create a use case in `scout/application/`.
- **New UI panel:** extend `scout/ui/components.py` and wire in `scout/ui/terminal.py`.

---

For product direction and roadmap, see `docs/prd.md`.
