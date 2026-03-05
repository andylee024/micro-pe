# UI History: Archive Summary

**Status:** Archived (UI docs)
**Original window:** 2026-02-19 to 2026-02-22
**Current focus:** Data pipeline architecture only

---

## Why this work existed

These docs tracked rapid iterations of terminal UX: initial V0 launch, V1 live-intelligence goals, and a listings-first side-by-side market view.

---

## Durable findings

1. Terminal-first interaction is viable and testable for Scout workflows.
2. Keyboard-driven navigation, drill-down, and export behaviors were validated early.
3. Side-by-side presentation of `for sale` vs `nearby` entities is a useful comparison pattern.
4. Assistant-driven filtering and contextual reasoning are valuable, but depend on stable underlying data.
5. UI speed and clarity benefit from precomputed, canonical datasets rather than ad-hoc source calls.

---

## Implication for current architecture

UI should be a thin consumer of pipeline outputs. The data pipeline should emit stable models/datasets (`Query`, `Listing`, `Business`, `MarketDataset`) that UI layers can render without source-specific logic.

---

## Cleanup note

Legacy UI planning/delivery docs from `v0-scout`, `v1-scout-ui`, and `v1-terminal-ui-listings` were consolidated into this archive summary while pipeline architecture is prioritized.
