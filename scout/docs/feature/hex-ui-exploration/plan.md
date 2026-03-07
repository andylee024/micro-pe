# Hex UI Exploration: Parent Plan and Review Pack

**Status:** In progress  
**Date:** 2026-03-06  
**Parent issue:** `A24-81`  
**Scope:** Decomposition + review artifacts only (no product implementation)

## Goal

Define and validate Hex-inspired UI options for Scout's research + outreach workflows using real
Scout query evidence, then select a recommended direction for follow-on implementation issues.

## Child Task Map

| Issue | Focus | Required output |
| --- | --- | --- |
| `A24-82` | Query evidence snapshots | 3+ realistic query runs with source coverage + summary artifact |
| `A24-83` | Concept A: Thesis Canvas + Evidence Explorer | Full-screen concept, interactions, model mapping |
| `A24-84` | Concept B: Target Workbench + Outreach Studio | Workbench layout, outreach flow, model/writeback mapping |
| `A24-85` | Hex pattern research | Notes on reusable Hex interaction and layout principles |
| `A24-86` | Research canvas component mockup | Focused component mockup for exploration workflows |
| `A24-87` | Outreach studio component mockup | Focused component mockup for leads + campaign workflows |

## Artifact Packaging

Store all artifacts for this parent effort under:

`docs/feature/hex-ui-exploration/artifacts/`

Use one markdown artifact per child issue, named with issue identifier prefix.
See `artifacts/README.md` for the canonical file list.

## Evaluation Rubric

Score each concept from `1` (weak) to `5` (strong):

| Criterion | What to verify |
| --- | --- |
| Thesis-to-evidence speed | Can users go from idea to evidence quickly without context switching? |
| Provenance clarity | Are source origin, confidence, and dataset lineage obvious at a glance? |
| Cross-source synthesis | Does the layout support side-by-side interpretation of `Business` + `Listing` data? |
| Workflow continuity | Can users move cleanly from research to targeting to outreach planning? |
| Actionability | Are next actions explicit and grounded in available pipeline outputs? |
| Implementation fit | Does the concept align with current `Query`, `Business`, `Listing`, and `MarketDataset` models? |
| Extensibility risk | How much rework is likely when adding writebacks, CRM sync, or campaign states? |

## Review Workflow

1. Verify each child issue has its artifact committed and linked in Linear.
2. Confirm evidence grounding by checking references to real outputs from `A24-82`.
3. Run rubric scoring for Concept A (`A24-83`) and Concept B (`A24-84`).
4. Use component mockups (`A24-86`, `A24-87`) to evaluate composability inside each concept.
5. Publish a short recommendation with:
   - chosen direction (A, B, or hybrid),
   - top 3 reasons,
   - top risks and mitigation follow-ups.

## Parent Decision Record Template

```md
## A24-81 Review Decision

### Recommendation
- Direction:
- Why:

### Evidence Reviewed
- A24-82:
- A24-83:
- A24-84:
- A24-85:
- A24-86:
- A24-87:

### Key Tradeoffs
- Strengths:
- Risks:
- Unknowns:

### Follow-up Implementation Scope
- Candidate child issues:
```

## Exit Criteria For `A24-81`

- All child artifacts are present and reviewable.
- Rubric scoring is completed for both concept directions.
- One recommendation is documented with explicit tradeoffs.
- Follow-up implementation issues are identified (out of scope to execute here).
