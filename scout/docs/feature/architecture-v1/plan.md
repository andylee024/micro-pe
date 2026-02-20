# Architecture V1: Implementation Plan

**Created:** 2026-02-20
**Owner:** Architecture Lead
**Status:** Ready
**Goal:** Implement clean architecture foundations while continuing Phase 1 feature delivery.

---

## Strategy: Dual-Track Execution

We will deliver Phase 1 features and architecture hardening in parallel using a 4-person team. The architecture work will be incremental, with backwards-compatible seams so features can ship without waiting for full refactor.

**Track A: Architecture Hardening (parallel)**
- Establish new layers and interfaces
- Unify config, error handling, and logging
- Create domain models and normalization

**Track B: Phase 1 Feature Delivery (parallel)**
- Stabilize BizBuySell/FDD integration
- Enhance UI for benchmarks and detail view
- Build benchmark computation pipeline

---

## Target Architecture (V1)

**Layering**
- `scout/domain/` — core models and invariants
- `scout/application/` — use-cases, orchestration
- `scout/adapters/` — external systems, scraping, storage
- `scout/interfaces/` — CLI + terminal UI
- `scout/shared/` — config, errors, logging, utils

**Primary Use-Case**
- `ResearchMarket`
  - Build universe
  - Compute benchmarks
  - Enrich + score (Phase 2)

---

## File Structure Changes

**New directories**
- `scout/domain/`
- `scout/application/`
- `scout/adapters/`
- `scout/interfaces/`
- `scout/shared/`

**Planned moves (incremental)**
- `scout/scout/main.py` → `scout/interfaces/cli.py`
- `scout/scout/ui/terminal.py` → `scout/interfaces/terminal/`
- `data_sources/*` → `scout/adapters/*`
- Merge `scout/scout/config.py` + `data_sources/shared/config.py` → `scout/shared/settings.py`
- Merge `data_sources/shared/errors.py` + `scout/shared/errors.py` → `scout/shared/errors.py`
- Preserve legacy imports temporarily with shim modules.

---

## Implementation Steps

### 1) Establish Shared Foundation (Week 1)
- Add `scout/shared/settings.py` (single source of truth)
- Add `scout/shared/errors.py` (unified error model)
- Add minimal `scout/domain/models.py`
- Create shim compatibility modules to avoid breaking existing code

**Success Criteria**
- CLI runs without import-time config failures
- All tools read config from shared settings

### 2) Introduce Use-Case Layer (Week 1–2)
- Create `scout/application/research_market.py`
- Implement a use-case API that returns normalized domain models
- Update UI to call the use-case instead of tools directly

**Success Criteria**
- `ScoutTerminal` uses `ResearchMarket` use-case
- `--no-ui` path also uses use-case

### 3) Adapter Normalization (Week 2)
- Wrap existing sources with adapter interfaces
- Normalize output into domain models
- Introduce adapter tests that verify normalization

**Success Criteria**
- Google Maps adapter returns `Business` models
- FDD/BizBuySell adapters return `Benchmark` models

### 4) Phase 1 Feature Integration (Week 2–4)
- Implement benchmark computation and display
- UI enhancements for detail view, benchmarks panel
- Ensure benchmarks are computed for 10+ industries

**Success Criteria**
- Benchmarks shown for 80%+ of businesses
- Business detail view renders estimates

---

## Team Plan (4 People)

**Engineer 1: Architecture Lead**
- Owns layer boundaries, use-case APIs, shims
- Creates `shared/` and `domain/`
- Provides migration guide and interface contracts

**Engineer 2: Data/Adapters**
- Wraps existing sources into adapters
- Fixes BizBuySell missing dependency
- Normalizes FDD output into benchmark models

**Engineer 3: Backend/Pipeline**
- Implement `ResearchMarket` use-case
- Benchmark computation and aggregation
- Scoring stub interface (Phase 2 ready)

**Engineer 4: UI/CLI**
- Move CLI/terminal into interfaces layer
- Integrate use-case output into UI
- Add benchmark + detail view panels

---

## Milestones

**Milestone 1 (End Week 1)**
- Shared settings + errors done
- `ResearchMarket` use-case wired to UI (Google Maps only)

**Milestone 2 (End Week 2)**
- Adapters layer wraps Maps + FDD + BizBuySell
- UI calling use-case with normalized results

**Milestone 3 (End Week 4)**
- Benchmarks integrated in UI
- Phase 1 success criteria met

---

## Testing Strategy

- Unit tests for domain model validation
- Adapter tests for normalization
- Use-case tests for orchestration
- UI smoke test (headless) for CLI flow

---

## Dependencies and Risks

**Dependencies**
- Resolve BizBuySell scraping dependency
- Confirm FDD scraper stability (Selenium/DocQNet)

**Risks**
- Refactor introduces regressions
- Phase 1 features slip

**Mitigations**
- Shims for legacy imports
- Incremental replacement, not big-bang

---

## Deliverables

- New layered architecture scaffold
- Unified settings/errors/logging
- Use-case orchestration
- Benchmark integration in UI
- Updated docs with architecture v1
