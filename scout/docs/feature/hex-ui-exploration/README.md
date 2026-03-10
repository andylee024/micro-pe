# Hex UI Exploration

Concrete web UI artifacts for the Scout research and outreach workflow.

## Files

- `web/index.html` — entry page linking both concepts.
- `web/concept-a-thesis-canvas.html` — thesis canvas + evidence explorer surface for `A24-83`.
- `web/concept-b-target-workbench.html` — target workbench + outreach studio surface for `A24-84`.
- `artifacts/screenshots/` — rendered PNGs for PR review.
- `a24-83-web-concept.md` — interaction notes, model mapping, and tradeoffs for concept A.
- `a24-84-web-concept.md` — interaction notes, writeback boundaries, and tradeoffs for concept B.

## Source Data

These concepts use real Scout output from:

- `outputs/pipeline/raw/e6f9fd974664/google_maps.json`
- `outputs/pipeline/raw/e6f9fd974664/bizbuysell.json`

## Render Screenshots

From `scout/`:

```bash
./scripts/render_ui_exploration_screenshots.sh
```

## Review Intent

The previous UI PR evidence only showed CLI screenshots. These artifacts replace that with actual
web-product-style surfaces so `A24-83` and `A24-84` can be reviewed against what the tasks
described.
