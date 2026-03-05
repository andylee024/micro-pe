# Scout Architecture

**Purpose:** Keep one simple, implementation-ready data pipeline architecture.
**Last Updated:** 2026-03-02

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
