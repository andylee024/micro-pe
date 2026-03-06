# BizBuySell Integration Notes (v1 Data Pipeline)

**Status:** Active implementation notes  
**Last Updated:** 2026-03-06  
**Scope:** Data pipeline only (UI out of scope)

## Why This Exists

Keep a durable record of:

1. How BizBuySell fits the current pipeline architecture.
2. What was implemented to make `fire protection` queries work.
3. What was validated live and what still needs cleanup.

## Current Architecture Fit

BizBuySell is implemented as a provider-specific `DataSource` adapter inside the shared pipeline:

1. `Query` (industry, location) is created by `Runner`.
2. `Workflow` calls `BizBuySellDataSource.fetch()`.
3. `BizBuySellDataSource` converts `Query` -> `ListingQuery`.
4. `BizBuySellProvider` resolves query text to route slugs and fetches pages.
5. Provider parses `BBS-state` JSON into canonical `Listing` model objects.
6. `Workflow` persists raw payload + upserts listings in `DataStore`.
7. `MarketDataset` returns listings + source coverage status.

This fits the current architecture because provider-specific logic remains inside one DataSource implementation and does not leak into `Workflow` or canonical models.

## Implementation Decisions (2026-03-06)

### 1) Slug Resolver Is Required

BizBuySell search routes are slug-based (`/<state>/<category>-for-sale/`), so natural-language query text must be resolved before fetch.

- Added industry mapping for fire-protection terms:
  - `fire protection`
  - `fire suppression`
  - `fire sprinkler`
  - `fire alarm`
  - `security services`
- Added city-to-state mapping so city-only queries can route to state search pages:
  - example: `Los Angeles` -> `california`

### 2) Fire-Relevance Filter

For fire-related queries, provider applies keyword filtering on listing name/description before returning results. If no keyword matches are found, provider falls back to unfiltered results (fail-soft behavior).

### 3) Driver Robustness Fix

Fixed undetected-chromedriver fallback path to avoid reusing `ChromeOptions` object across retries.

## Live Validation Record

### End-to-End Query

Command:

```bash
venv/bin/python -m scout.main run "fire protection services businesses in Los Angeles" --max-results 10 --no-cache
```

Observed result:

1. `google_maps`: success, `10` businesses
2. `bizbuysell`: success, `1` listing
3. `reddit`: empty

Listing observed:

- `2475706` — `Fire Inspection Business w/ State and multiple City licenses`  
  Location: `Los Angeles, CA`  
  Asking Price: `$1,800,000`  
  Cash Flow: `$625,000`

### Slug Probe (California)

Validated working slug routes with listing search data present:

1. `hvac-businesses`
2. `plumbing-businesses`
3. `pest-control-businesses`
4. `car-washes`
5. `security-businesses`
6. `security-established-businesses`
7. `service-businesses`

Negative control:

1. `not-a-real-category` -> no `BBS-state` search payload

### Enumerated Slugs Snapshot

Saved debug artifacts:

1. `outputs/pipeline/debug/bizbuysell_bbs_state_homepage.json`
2. `outputs/pipeline/debug/bizbuysell_slugs.txt` (current extracted count: `270`)

Skill-facing references:

1. `skills/query-source-routing/SKILL.md`
2. `skills/query-source-routing/references/bizbuysell-slugs.md`

Important: this list is derived from observed `urlStub` payloads and may not include every routable slug.

## Known Gaps

1. No explicit business-to-listing entity matching yet (cross-source join not implemented).
2. Industry slug mapping remains partially curated/manual.
3. Scraper reliability depends on anti-bot behavior and browser environment.

## Clean Extensibility Path

1. Introduce a small `QueryPlanner` for marketplace sources:
   - output: normalized industry, normalized state, primary slug, fallback slugs.
2. Move static mappings (industry aliases, city->state) into versioned config files.
3. Add a source capability contract:
   - `supports_city_input`, `supports_slug_fallback`, `supports_relevance_filter`.
4. Add structured source run telemetry in payload metadata:
   - route URL used, fallback reason, raw result count, filtered result count.
5. Keep fail-soft policy:
   - source-level failures should not stop the whole workflow.
