# UI Exploration

Concrete web UI artifacts for a simpler, partner-friendly Scout product surface.

## Files

- `web/index.html` — simple search / home screen.
- `web/concept-a-thesis-canvas.html` — simplified results screen with businesses, listings, and details.
- `web/concept-b-target-workbench.html` — saved-items review screen for partner discussion.
- `web/app.js` — client-side renderer for the sample dataset.
- `web/data/fire-protection-los-angeles.json` — real Scout snapshot used by the UI.
- `artifacts/screenshots/` — rendered PNGs for PR review.
- `a24-83-web-concept.md` — notes for the simple search + results flow.
- `a24-84-web-concept.md` — notes for the saved-items review flow.

## Source Data

These concepts use real Scout output from:

- `outputs/pipeline/raw/e6f9fd974664/google_maps.json`
- `outputs/pipeline/raw/e6f9fd974664/bizbuysell.json`

## Render Screenshots

From `scout/`:

```bash
./scripts/render_ui_exploration_screenshots.sh
```

## Vercel

The repo root now includes:

- `vercel.json` — routes `/`, `/results`, `/saved`, and supporting assets into the UI mock.
- `.vercelignore` — excludes large local-only directories from deploy upload.
- `../vercel.json` and `../.vercelignore` equivalents under `scout/` — support Vercel projects that use `scout/` as the Root Directory.

This lets the repo deploy from the repository root without changing Vercel's Root Directory.

## Design Direction

This version deliberately steps away from the busier notebook-style concept. The focus is:

1. one search box
2. one results page with two simple lists
3. one saved-items page for partner review

The intent is to preserve the clarity of the old TUI while making the product accessible to
non-technical teammates.
