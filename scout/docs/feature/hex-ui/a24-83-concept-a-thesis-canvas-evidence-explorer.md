# A24-83: UI Concept A - Hex-style Thesis Canvas + Evidence Explorer

## Goal
Design one Hex-inspired exploration surface for Scout that helps users:
1. Define a thesis quickly.
2. Slice evidence across runs and sources.
3. Inspect source provenance and failures before making decisions.

## Inputs Used
Primary evidence source:
- `docs/feature/hex-ui/a24-83-query-evidence.md`

Representative real runs captured on 2026-03-06:
1. `run_id=51659aeb9299` - HVAC in Los Angeles
2. `run_id=127e80490228` - Car wash in Houston
3. `run_id=900537e810a8` - Plumbing in Miami

Observed source coverage from real output:
- `google_maps`: `failed` (missing API key)
- `bizbuysell`: `failed` (no Chrome binary in runtime)
- `reddit`: `empty` (0 posts)

## Concept Summary
The interface uses a three-zone model:
1. Thesis Canvas (left) to define and branch hypotheses.
2. Evidence Lattice (center) to pivot across run slices (industry, location, source, status).
3. Provenance Drawer (right) to inspect exact source status/error/latency for trust and debugging.

The UI is intentionally useful in both high-data and low-data states. In this environment, low-data behavior is grounded by the real run snapshots above.

## Full Screen Wireframe (ASCII)

```text
+----------------------------------------------------------------------------------------------------------------------+
| SCOUT LAB: THESIS CANVAS + EVIDENCE EXPLORER                                                  runbook: A24-83 sample |
+--------------------------------------------+---------------------------------------------------+-----------------------+
| THESIS CANVAS                              | EVIDENCE LATTICE                                  | PROVENANCE DRAWER     |
|--------------------------------------------|---------------------------------------------------|-----------------------|
| Thesis input                               | Slice chips                                       | Selected node          |
| [ HVAC businesses in Los Angeles       ]   | [Industry: HVAC] [Location: Los Angeles]         | source: google_maps    |
| [ Compare to Car wash in Houston      ]    | [Source: all] [Status: failed+empty]             | status: failed         |
| [ + Add branch ]                           | [Time: 2026-03-06]                                | records: 0             |
|                                            |                                                   | duration_ms: 98        |
| Thesis branches                            | Hex cards (one per run/source pair)              | error: API key missing |
| (A) HVAC / Los Angeles                     |                                                   |-----------------------|
| (B) Car wash / Houston                     |        / run 5165 \       / run 127e \          | Related nodes          |
| (C) Plumbing / Miami                       |       / gm:failed  \     / gm:failed  \         | - bizbuysell: failed   |
|                                            |       \ bbs:failed /     \ bbs:failed /         | - reddit: empty        |
| Active hypothesis                           |        \ reddit:0 /       \ reddit:0 /          |-----------------------|
| "Which theses have enough evidence         |                                                   | Compare panel          |
|  quality to prioritize outreach?"          |        / run 9005 \                                | Run A vs Run B         |
|                                            |       / gm:failed  \                               | gm: failed vs failed   |
| Confidence rule                             |       \ bbs:failed /                               | bbs: failed vs failed  |
| if failed_sources >= 2 => confidence LOW   |        \ reddit:0 /                                | reddit: 0 vs 0         |
+--------------------------------------------+---------------------------------------------------+-----------------------+
| DETAIL STRIP                                                                                                         |
| Businesses (Business) | Listings (Listing) | Coverage timeline (MarketDataset.coverage) | Notes & next action    |
| 0 rows (empty state)  | 0 rows (empty)     | gm failed -> bbs failed -> reddit empty      | "Fix keys/env first"  |
+----------------------------------------------------------------------------------------------------------------------+
```

## Panel Definitions

| Panel | Purpose | Data shown | Why it matters |
|---|---|---|---|
| Thesis Canvas | Capture thesis and branch alternatives | Query text, parsed industry/location, active hypothesis, confidence rule | Makes the analytical intent explicit before browsing rows |
| Evidence Lattice | Fast visual slicing across runs/sources | Run IDs, source statuses, record counts, filter chips | Lets user see evidence quality at a glance |
| Provenance Drawer | Deep inspection of trust/debug details | `source`, `status`, `records`, `duration_ms`, `error` | Prevents acting on data without understanding gaps |
| Detail Strip | Row-level payload + run timeline | `Business[]`, `Listing[]`, and coverage sequence | Bridges overview to operational next steps |

## Sample Data Views (From Real Query Output)

### View 1: Query Coverage Matrix

| run_id | industry | location | google_maps | bizbuysell | reddit | businesses | listings |
|---|---|---|---|---|---|---:|---:|
| `51659aeb9299` | HVAC | Los Angeles | failed | failed | empty | 0 | 0 |
| `127e80490228` | Car wash | Houston | failed | failed | empty | 0 | 0 |
| `900537e810a8` | Plumbing | Miami | failed | failed | empty | 0 | 0 |

### View 2: Provenance Detail (selected node)

| Field | Value |
|---|---|
| source | `google_maps` |
| status | `failed` |
| records | `0` |
| duration_ms | `98` |
| error | `Google Maps API key not found in environment variables` |

### View 3: Confidence Gate (derived)

| Rule | Evaluation |
|---|---|
| failed_sources >= 2 => LOW | true for all three runs |
| any source success => MEDIUM+ candidate | false |
| businesses > 0 or listings > 0 => Outreach-ready | false |

## Interaction Walkthrough (7 Interactions)

1. Enter thesis in Thesis Canvas.
Expected outcome: creates a `Query` candidate and immediately parses `industry` + `location` chips.

2. Add a branch thesis using `+ Add branch`.
Expected outcome: second query branch appears side-by-side for comparison in the Evidence Lattice.

3. Click `Status: failed+empty` filter chip.
Expected outcome: lattice narrows to low-confidence nodes so user can diagnose blockers first.

4. Select one hex node (example: `run 5165 / google_maps`).
Expected outcome: Provenance Drawer opens exact source metadata and error string.

5. Toggle compare mode (Run A vs Run B).
Expected outcome: right panel shows per-source deltas (`status`, `records`, `duration_ms`).

6. Open Detail Strip -> Coverage timeline.
Expected outcome: user sees stage ordering by source and can identify the first failure point.

7. Trigger `Create next action` from drawer.
Expected outcome: app generates an operational action card (for this sample: set Google API key, install Chrome runtime, rerun).

## Widget -> Pipeline Model Mapping

| Widget / UI object | Pipeline model(s) | Field mapping |
|---|---|---|
| Thesis input + branch list | `Query` | `industry`, `location`, `max_results`, `use_cache`, `run_id` |
| Evidence hex card | `MarketDataset`, `Coverage` | `query.run_id`, `coverage[*].source/status/records/duration_ms/error` |
| Businesses table | `Business` | `name`, `address`, `phone`, `website`, `category`, `rating`, `reviews`, `source` |
| Listings table | `Listing` | `source`, `source_id`, `url`, `name`, `industry`, `location`, `state`, `asking_price`, `annual_revenue`, `cash_flow`, `asking_multiple`, `days_on_market`, `broker`, `listed_at` |
| Provenance drawer metadata | `MarketDataset.coverage` | per-source provenance + runtime errors |
| Confidence gate | Derived from `MarketDataset` | aggregate over `coverage` + `len(businesses)` + `len(listings)` |

## Tradeoffs

Strengths:
1. Makes evidence quality visible before users over-trust rankings.
2. Supports both rich-data and sparse-data scenarios without changing layout.
3. Keeps model-to-UI mapping direct and implementation-ready.

Risks:
1. Hex lattice may feel dense for first-time users without progressive disclosure.
2. Over-emphasis on failures can overshadow value when data is healthy.
3. Requires consistent source status semantics to avoid misleading confidence gates.

Unknowns:
1. Whether users prefer hex cards over simpler table slices for speed.
2. Optimal threshold rules for confidence gating across mixed-source datasets.
3. How much provenance detail should be visible by default vs collapsed.

## Acceptance Criteria Mapping

- One full-screen concept artifact with ASCII wireframe + panel definitions: covered in `Full Screen Wireframe` and `Panel Definitions`.
- Thesis input, evidence slicing, and provenance inspection: covered in `Concept Summary` and `Interaction Walkthrough`.
- At least 5 concrete interactions with outcomes: 7 interactions documented.
- Explicit widget-to-model mapping: covered in `Widget -> Pipeline Model Mapping`.
- Tradeoffs comment (strengths, risks, unknowns): covered in `Tradeoffs`.
