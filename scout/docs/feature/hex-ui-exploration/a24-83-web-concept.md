# A24-83 Web Concept

## Goal

Provide a Hex-style thesis canvas and evidence explorer for Scout data with a full-screen web
artifact and concrete interaction model.

## Artifact

- `docs/feature/hex-ui-exploration/web/concept-a-thesis-canvas.html`
- `docs/feature/hex-ui-exploration/artifacts/screenshots/concept-a-thesis-canvas.png`

## What The Screen Shows

1. A working thesis area that stays editable.
2. Reusable lenses that let the user pivot without changing the underlying run.
3. A business universe table backed by real Google Maps output.
4. Separate sale evidence from BizBuySell, shown without a false business-to-listing match.
5. Inline source provenance and raw payload inspection.

## Interaction Walkthrough

1. Edit the thesis line to change the working question for the team.
2. Click a saved lens such as `High review density` to re-sort and filter the explorer.
3. Select a business row to pin it into the right-side inspector.
4. Turn on the sale-evidence overlay to keep market listings beside the operating universe.
5. Open the raw snippet block to verify source provenance before acting on the observation.

## Model Mapping

- `Query` -> top query pill and thesis framing.
- `Business` -> main evidence explorer rows.
- `Listing` -> market sale context card and raw snippet.
- `MarketDataset` -> summary cards and source coverage section.

## Tradeoffs

### Strengths

1. Keeps the product fluid: the thesis can move without losing evidence context.
2. Does not overstate matching confidence where the pipeline does not have it.
3. Makes source coverage and freshness visible in the same surface as the data.

### Risks

1. Without a real interaction backend, saved lenses are still concept-level behavior.
2. The page shows one query deeply, not multiple queries side by side.

### Unknowns

1. Whether the team wants notebook-style cells or a tighter table-first surface for daily use.
2. How much provenance detail should stay visible by default versus on demand.
