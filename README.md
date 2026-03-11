# Scout

Scout is a pipeline-first codebase with a Textual terminal shell for SMB acquisition research.

## Current Focus

- Data pipeline architecture with a terminal app shell
- Canonical concepts:
  - `Model` (`Query`, `Listing`, `Business`, `MarketDataset`)
  - `Workflow`
  - `Runner`
  - `DataSource`
  - `DataStore`

See:
- `docs/feature/v1-data-pipeline/plan.md`
- `docs/architecture.md`

## Install

```bash
cd scout
pip install -e .
```

## Run

```bash
scout run "HVAC businesses in Los Angeles"
```

The command executes one workflow run and prints source coverage plus record counts.

```bash
scout research "HVAC businesses in Los Angeles"
```

The command launches the Textual terminal shell with Universe, Queue, Lead Set, History, and
Command modes backed by pipeline service state.

## Repository Layout

```text
scout/
├── scout/pipeline/          # runner/workflow/models/data_sources/data_store
├── data_sources/            # concrete external source implementations
├── tests/data_sources/      # source-level tests
├── tests/pipeline/          # pipeline-core tests
└── docs/                    # active docs + archive summaries
```
