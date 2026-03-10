# A24-83 Web Concept

## Goal

Provide a much simpler web surface for the main Scout loop: search, review the two source lists,
and click for details.

## Artifact

- `docs/feature/hex-ui-exploration/web/index.html`
- `docs/feature/hex-ui-exploration/web/concept-a-thesis-canvas.html`
- `docs/feature/hex-ui-exploration/artifacts/screenshots/concept-a-thesis-canvas.png`

## What The Screen Shows

1. A plain-English search entrypoint.
2. One results page with Google Maps businesses on one side and BizBuySell listings on the other.
3. A details area that explains the selected lead and the selected listing without over-claiming.
4. Honest empty-state treatment when only one listing exists.
5. Lightweight actions such as save, export, and copy contact info.

## Interaction Walkthrough

1. Enter a query on the home screen.
2. Land on a single results page that is easy to scan in a meeting.
3. Click a business row to inspect address, phone, website, rating, and reviews.
4. Click a listing row to inspect price, cash flow, and multiple.
5. Save or export the interesting rows for later review.

## Model Mapping

- `Query` -> search input and query summary header.
- `Business` -> Google Maps results table and business detail block.
- `Listing` -> BizBuySell results table and listing detail block.
- `MarketDataset` -> count summaries and selected-row context.

## Tradeoffs

### Strengths

1. Preserves the clarity of the TUI while making it web-accessible.
2. Gives non-technical partners a very obvious mental model.
3. Stays tightly aligned to the current pipeline outputs.

### Risks

1. The UI is intentionally narrow and may feel too plain for deeper research work.
2. Extra filters or advanced analysis would need to be layered in carefully later.

### Unknowns

1. Whether the detail panel should live below the lists or in a side drawer.
2. How much filtering is helpful before the page stops feeling simple.
