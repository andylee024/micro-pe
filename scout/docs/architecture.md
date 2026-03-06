# Scout Architecture

**Purpose:** Keep one simple, implementation-ready data pipeline architecture.
**Last Updated:** 2026-03-06

## Canonical Terms

1. **Model**: typed data shape shared between components.
2. **Workflow**: stage-based orchestration engine.
3. **Runner**: entrypoint that starts one workflow run.
4. **DataSource**: source-specific fetch component.
5. **DataStore**: persistence layer for raw + canonical data.

## Canonical Models

1. `Query`
2. `Listing`
3. `Business`
4. `MarketDataset`

## ETL Flow

```text
[CLI / Scheduler / API]
          |
          v
       [Runner]
          |
          v
      [Workflow]
   plan -> fetch -> persist raw -> normalize -> validate -> upsert -> build dataset
          |
          +------------------------------+
          |                              |
          v                              v
[DataStore: raw snapshots]     [DataStore: canonical SQLite]
           \                            /
            \                          /
             +-----------v------------+
                         |
                  [MarketDataset]
```

## DataSource Roles

1. `GoogleMapsDataSource` -> discovers operating businesses (`Business` records).
2. `BizBuySellDataSource` -> discovers businesses-for-sale (`Listing` records).
3. `RedditDataSource` -> optional sentiment signals.

### BizBuySell Fit (Current)

BizBuySell cleanly fits the current architecture as a provider-specific `DataSource` implementation:

1. Query-to-route mapping (slug resolution) remains inside the BizBuySell provider.
2. `Workflow` stays source-agnostic and only handles orchestration/persistence.
3. Canonical `Listing` model stays shared across all listing sources.

Reference notes:

- `docs/feature/v1-data-pipeline/bizbuysell-notes.md`

## Code Layout

```text
scout/scout/pipeline/
├── runner.py
├── workflow.py
├── models/
│   ├── query.py
│   ├── listing.py
│   ├── business.py
│   └── market_dataset.py
├── data_sources/
│   ├── base.py
│   ├── google_maps.py
│   ├── bizbuysell.py
│   └── reddit.py
└── data_store/
    ├── base.py
    ├── raw_snapshot.py
    └── sqlite.py
```

## Cleanup Outcome

- Legacy terminal UI and UI-driven application layers were removed.
- Pipeline runtime is now the primary internal architecture.
- Existing source connectors remain under `data_sources/` and are wrapped by pipeline `DataSource` implementations.

## Architecture Hygiene Rules

To keep this simple, extensible, and robust:

1. Keep provider-specific logic (slugs, anti-bot behavior, parsing quirks) inside provider/DataSource code.
2. Keep `Workflow` generic: orchestration, fail-soft handling, and dataset assembly only.
3. Persist raw payloads before normalization for replay/debug.
4. Normalize into canonical models before writing to canonical tables.
5. Treat each source as optional: partial dataset is valid when one source fails.
