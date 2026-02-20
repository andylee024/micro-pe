# Architecture V1: Research

**Created:** 2026-02-20
**Owner:** Architecture Lead
**Status:** Draft

---

## Problem Statement

The current Scout codebase delivers Phase 0 value (terminal UI + Google Maps universe), but architecture drift and coupling create risk as we scale into Phase 1+ (benchmarks, FDD integration, scoring, sentiment). We need a clean architecture that supports multi-source pipelines, reliable caching/storage, and UI evolution, without slowing down feature delivery.

## Business Value

- **Speed with safety:** enable rapid Phase 1 feature delivery without accruing structural debt.
- **Multi-source reliability:** stabilize ingestion and normalization so benchmarks and scoring are defensible.
- **Team throughput:** make parallel development possible without collisions.

## Current Architecture Summary (As Implemented)

- CLI entrypoint: `scout/scout/main.py`
- UI controller: `scout/scout/ui/terminal.py`
- Tools and caching: `data_sources/shared/base.py`, `data_sources/...`
- FDD pipeline: `data_sources/fdd/*` with `FDDScraperBase`
- Config split: `scout/scout/config.py` and `data_sources/shared/config.py`
- Error split: `data_sources/shared/errors.py` and `scout/shared/errors.py`

## Critical Findings

1. **UI/Data Coupling**
   - `ScoutTerminal` calls data tools directly.
   - Limits testability and orchestration across data_sources.

2. **Config Drift**
   - `scout/scout/config.py` uses `outputs/cache` while architecture docs mention `~/.scout/cache`.
   - `scout/scout/config.py` raises on import if key missing, preventing CLI from handling errors gracefully.

3. **Error Model Duplication**
   - Two error systems exist with different semantics.
   - Hard to provide consistent UX for failures.

4. **Missing/Legacy Dependencies**
   - `data_sources/marketplaces/bizbuysell.py` references `scrapers.bizbuysell` which is not present in repo.

5. **Inconsistent Logging**
   - `print()` usage in sources reduces debuggability and production readiness.

## Constraints

- Must continue shipping Phase 1 features (benchmarks + FDD integration + UI enhancements).
- Minimal disruption to CLI UX.
- Keep local-first development and storage in near term.

## Architectural Goal

Introduce a clean layering that allows:
- clear separation of domain logic vs external systems vs UI
- pluggable data sources
- consistent config, caching, and error handling
- parallel development across data, UI, and scoring

## Proposed Target Architecture (Summary)

**Layers**
- Domain: core models and business logic
- Application: use cases/orchestration
- Adapters: external APIs, scrapers, storage
- Interfaces: CLI + terminal UI

**Outcome**
- UI calls a single use-case: `ResearchMarket`
- Use-case orchestrates universe, benchmarks, scoring
- Adapters are swappable without touching UI

## Risks and Mitigations

- **Risk:** refactor slows Phase 1 delivery
  - **Mitigation:** incremental migration; keep legacy paths until replaced.

- **Risk:** parallel work breaks interfaces
  - **Mitigation:** define data contracts (DTOs) and interface boundaries early.

- **Risk:** regressions in CLI behavior
  - **Mitigation:** preserve CLI signature and add regression tests.

## Open Questions

- Should local cache move to SQLite in Phase 1 or Phase 2?
- Do we need per-source caching policies or a unified cache manager?
- How far do we push normalization now vs defer to scoring phase?

