# A24-86: Scout Research Canvas Component Mockup

## Goal

Design an initial research-canvas component where users can shape a thesis and explore Scout evidence without leaving one focused surface.

## Scope

- In: component-level mockup, interaction model, and data mapping to current pipeline outputs.
- Out: production frontend implementation, backend/API changes, or persistence workflows.

## Component Definition

The **Research Canvas** is a composition component that sits between query execution and target actioning.
It should let users:

1. Define or revise a market thesis.
2. Slice evidence from businesses, listings, and source coverage.
3. Inspect provenance before promoting findings to shortlist/outreach flows.

## Mockup (ASCII)

```text
+-------------------------------------------------------------------------------------------+
| Research Canvas                                                                           |
| Thesis: "HVAC businesses in Los Angeles"   Run: 8f3c91aa27d1   Updated: 2m ago           |
+-----------------------+-----------------------------------------+-------------------------+
| Lens / Filters        | Evidence Stream                         | Provenance Inspector    |
|                       |                                         |                         |
| Focus Lens            | [Business Card] Cool Air HVAC          | Selected: Cool Air HVAC |
| (*) Quality           | rating 4.8 | reviews 350 | source maps | source: google_maps     |
| ( ) Valuation         | "High rating + high review density"    | coverage: success       |
| ( ) Market Heat       | [Pin] [Compare] [Ask Assistant]        | records: 47             |
|                       |                                         | duration: 1800ms        |
| Evidence Types        | [Listing Card] HVAC Service Co         |                         |
| [x] Businesses        | ask $1.2M | rev $980k | multiple 2.6x  | Raw Fields              |
| [x] Listings          | "Recurring contracts noted"            | - name                  |
| [x] Coverage          | [Pin] [Compare] [Ask Assistant]        | - location              |
|                       |                                         | - rating/reviews        |
| Thresholds            | [Coverage Card] bizbuysell: success    | - asking_price          |
| Reviews >= 150        | records 14 | duration 2200ms           | - annual_revenue        |
| Rating >= 4.3         | "Coverage adequate for benchmarking"   |                         |
| [Apply Filters]       | [Pin] [Compare] [Ask Assistant]        | [Open Raw Snapshot]     |
|                       |                                         | [View Source Trail]     |
+-----------------------+-----------------------------------------+-------------------------+
```

## Data Contract (Current Models)

| Canvas Element | Backing Model | Fields Used |
|---|---|---|
| Thesis bar | `Query` | `industry`, `location`, `run_id`, `created_at` |
| Business evidence cards | `Business` | `name`, `location`, `rating`, `reviews`, `category`, `source` |
| Listing evidence cards | `Listing` | `name`, `asking_price`, `annual_revenue`, `asking_multiple`, `days_on_market`, `source`, `url` |
| Coverage evidence cards | `Coverage` | `source`, `status`, `records`, `duration_ms`, `error` |
| Source/summary tags | `MarketDataset` | `signals`, `coverage`, `created_at` |

## Interaction Model

1. `Edit Thesis`: user updates thesis text; canvas refreshes cards after the next run.
2. `Switch Lens`: toggle between Quality, Valuation, and Market Heat to reprioritize evidence ordering.
3. `Toggle Evidence Type`: show/hide Businesses/Listings/Coverage to reduce noise.
4. `Apply Threshold Filters`: enforce review/rating cutoffs and update visible evidence set.
5. `Pin Evidence`: pin card into a temporary "working set" for compare/export.
6. `Compare`: open side-by-side view for pinned cards (business vs listing vs coverage context).
7. `Ask Assistant`: send selected card context to assistant prompt scaffold.
8. `Open Raw Snapshot`: jump to persisted raw source payload for trust/provenance checks.

## Component States

1. **Empty**: no run selected; show thesis input and starter prompts.
2. **Loading**: query in progress; show source-level progress rows from `coverage`.
3. **Populated**: evidence cards rendered from `businesses`, `listings`, and `coverage`.
4. **Partial Failure**: one or more sources failed; cards remain visible with explicit failure badges.

## Example View-Model Payload

```json
{
  "query": {"industry": "HVAC businesses", "location": "Los Angeles", "run_id": "8f3c91aa27d1"},
  "businesses": [{"name": "Cool Air HVAC", "rating": 4.8, "reviews": 350, "source": "google_maps"}],
  "listings": [{"name": "HVAC Service Co", "asking_price": 1200000, "annual_revenue": 980000, "source": "bizbuysell"}],
  "coverage": [{"source": "google_maps", "status": "success", "records": 47}, {"source": "bizbuysell", "status": "success", "records": 14}],
  "signals": {"google_maps": {"top_themes": ["response time", "pricing"]}}
}
```

## Tradeoffs

- Strength: keeps thesis, evidence, and provenance in one inspection loop.
- Risk: evidence density can overwhelm users without clear default lens ordering.
- Unknown: whether users prefer card stream or table-first exploration for early market triage.

## Handoff Notes

- This artifact is intentionally implementation-agnostic and ready for Concept A/B consolidation.
- Next step after concept selection: convert this component contract into concrete UI props/state for the chosen frontend surface.
