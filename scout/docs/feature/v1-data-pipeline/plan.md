# v1-data-pipeline: Workflow Plan (Pre-Implementation)

**Status:** Draft (pre-implementation)
**Date:** 2026-03-02
**Scope:** Data pipeline architecture only (UI out of scope)

---

## Goal

Define one simple, robust, shared mental model for Scout's data pipeline before code changes:

- Use one execution flow
- Use one set of terms
- Use one canonical data path from query to dataset

---

## Canonical Terms

Use these names consistently in docs and code:

1. **Model**: typed data shape shared between components.
2. **Workflow**: stage-based orchestration engine.
3. **Runner**: entrypoint that starts one workflow run.
4. **DataSource**: source-specific fetch component.
5. **DataStore**: persistence layer for raw + canonical data.

### Model Types

The first canonical model set:

1. `Query`
2. `Listing`
3. `Business`
4. `MarketDataset`

---

## ETL Workflow (ASCII)

```text
[CLI / Scheduler / API]
          |
          v
       [Runner]
  (build Query, run_id)
          |
          v
      [Workflow]
   -----------------
   1) plan
   2) fetch via DataSources
   3) persist raw payloads
   4) normalize to Models
   5) validate + confidence
   6) upsert canonical tables
   7) build MarketDataset
          |
          +------------------------------+
          |                              |
          v                              v
[DataStore: raw snapshots]     [DataStore: canonical SQLite]
  (audit/replay/debug)         (listings/businesses/signals)
           \                            /
            \                          /
             +-----------v------------+
                         |
                  [MarketDataset]
```

### DataSource fan-out in step 2

```text
Workflow -> GoogleMapsDataSource  -> Business records
Workflow -> BizBuySellDataSource  -> Listing records
Workflow -> RedditDataSource      -> Sentiment signals
```

---

## Target Directory Layout

```text
scout/scout/pipeline/
├── runner.py                 # Runner
├── workflow.py               # Workflow
├── models/
│   ├── query.py              # Query
│   ├── listing.py            # Listing
│   ├── business.py           # Business
│   └── market_dataset.py     # MarketDataset
├── data_sources/
│   ├── base.py               # DataSource interface
│   ├── google_maps.py        # GoogleMapsDataSource
│   ├── bizbuysell.py         # BizBuySellDataSource
│   └── reddit.py             # RedditDataSource
└── data_store/
    ├── base.py               # DataStore interface
    ├── raw_snapshot.py       # raw payload persistence
    └── sqlite.py             # canonical persistence
```

This is a target-state structure for the refactor, not a claim that it already exists.

---

## Robustness Rules

1. Fail soft by DataSource: one source failure must not kill the whole run.
2. Persist raw payloads before normalization for replay/debug.
3. Keep idempotent upserts in canonical tables.
4. Emit per-stage status and timings for each run.
5. Return partial `MarketDataset` with explicit coverage metadata.

---

## Implementation Sequence (Before UI Changes)

1. Freeze Models and naming.
2. Implement Runner + Workflow skeleton with stage status events.
3. Standardize one DataSource interface and wrap existing source logic.
4. Implement DataStore split (raw + canonical).
5. Move existing market/listing path to the new Workflow.
6. Keep UI integration as a thin consumer of `MarketDataset`.

---

## Out of Scope

1. UI redesign
2. Assistant behavior changes
3. Scoring/watchlist workflows
4. New paid/external providers

