# UI Concept B: Target Workbench + Outreach Studio

**Issue:** A24-84  
**Status:** Draft concept artifact  
**Date:** 2026-03-06

## Goal

Design one Hex-style concept for shortlisting, prioritization, and outreach execution using Scout pipeline evidence.

## Scope

In scope:
1. Workbench layout for compare and shortlist actions.
2. Outreach Studio flow with progression states.
3. Concrete interactions mapped to current pipeline outputs and future writebacks.

Out of scope:
1. CRM integration implementation.
2. Email sending implementation.
3. Persistent workflow engine implementation.

## Evidence Inputs

This concept uses currently available Scout evidence sources:
1. `MarketDataset` contract in pipeline models (`query`, `businesses`, `listings`, `signals`, `coverage`).
2. CLI run output shape in `scout/scout/main.py` (business/listing counts, per-source status).
3. Live-validation listing example in `docs/feature/v1-data-pipeline/bizbuysell-notes.md`.
4. Ranked-target interaction style in `docs/prd.md`.

## Layout Wireframe (Workbench + Outreach Panel Flow)

```text
SCOUT  thesis: "HVAC in Los Angeles"   run_id: 20260306-1842   47 targets   1 listing match

+-----------------------------------------------------------------------------------------------+
| TARGET WORKBENCH (left, 65%)                                  | OUTREACH STUDIO (right, 35%) |
|---------------------------------------------------------------|-------------------------------|
| Filters: [Rating >= 4.5] [Reviews >= 100] [Has phone] [BBS]  | Queue Stages                  |
| Sort: [Priority score v]                                      | Drafted (4)                   |
|                                                               | Ready to Send (3)             |
| Shortlist (12)                                                | Sent (5)                      |
| 1) Cool Air HVAC          score 84                            | Replied (2)                   |
|    4.8 stars | 350 reviews | phone | website                 | Qualified (1)                 |
|    Why: high reviews, recurring service mix, BBS comp anchor | Pass (1)                      |
|                                                               |                               |
| 2) SoCal Heating and Air  score 79                            | Selected Queue Item           |
|    4.7 stars | 180 reviews | phone | website                 | Target: SoCal Heating and Air |
|    Why: strong reputation, dense service area                | Stage: Ready to Send          |
|                                                               | Last touch: none              |
| Compare Drawer (up to 3 targets)                              |                               |
| [Cool Air] [SoCal] [Valley Air]                               | Outreach Brief                |
| - Quality: 4.8 / 4.7 / 4.5                                    | - Thesis fit: Residential HVAC|
| - Demand proxy (reviews): 350 / 180 / 72                      | - Evidence: 3 supporting cues |
| - Listing comp: $1.8M ask, $625k cash flow                    | - Risk flags: owner unknown   |
|                                                               |                               |
| Actions: [Add to Queue] [Mark Priority] [Exclude] [Open Notes]| Actions                       |
|                                                               | [Generate Draft] [Advance]    |
|                                                               | [Mark Replied] [Pass]         |
+-----------------------------------------------------------------------------------------------+
```

## Outreach Progression States

```text
Drafted -> Ready to Send -> Sent -> Replied -> Qualified
                           \-> Pass
```

State intent:
1. `Drafted`: target selected, no outbound text finalized.
2. `Ready to Send`: message is approved by user for sending.
3. `Sent`: outbound sent via external channel.
4. `Replied`: inbound response received.
5. `Qualified`: response indicates real opportunity.
6. `Pass`: no further outreach for now.

## Sample Target Rows (UI Artifact Data)

| Target | Market Evidence (current read) | Listing Comp Signal | Priority Rationale |
|---|---|---|---|
| Cool Air HVAC | rating `4.8`, reviews `350`, category `HVAC` | Nearby BBS comp ask `$1.8M`, cash flow `$625k` | High social proof + comp anchor for valuation |
| SoCal Heating and Air | rating `4.7`, reviews `180`, phone + website present | No direct listing match, same metro comparables | Strong quality, contact-ready, likely owner-operator |
| Valley Air Experts | rating `4.5`, reviews `72` | No direct listing match | Lower urgency but strong backup target |
| Fire Inspection Business (listing) | BizBuySell listing in Los Angeles | ask `$1.8M`, cash flow `$625k` | Use as benchmark context for pricing expectations |

## Sample Outreach Queue Rows

| Target | Stage | Channel | Last Outcome | Next Action | Owner |
|---|---|---|---|---|---|
| SoCal Heating and Air | Ready to Send | Email | Draft generated | Review and send | User |
| Cool Air HVAC | Sent | Phone + Email | Awaiting response | Follow up in 3 days | User |
| Valley Air Experts | Drafted | Email | Not sent | Personalize intro with local proof points | User |
| Metro Climate Services | Replied | Email | Requested details | Qualify with 3 follow-up questions | User |

## Concrete Interactions (Action -> Expected Outcome)

1. Click `Add to Queue` on a shortlisted target.
Outcome: target appears in Outreach Studio with stage `Drafted` and a generated evidence brief.

2. Toggle `Mark Priority` on a target.
Outcome: target moves higher in shortlist ordering and is tagged `priority=true` for queue views.

3. Open `Compare Drawer` for 2-3 targets.
Outcome: side-by-side metrics render (rating, reviews, listing comps) with a clear best-next-contact recommendation.

4. Click `Generate Draft` for selected queue item.
Outcome: outreach draft template is produced using thesis + target evidence snippets and stored as latest draft revision.

5. Click `Advance` from `Drafted` to `Ready to Send`.
Outcome: queue stage updates, timestamp is recorded, and item appears in "ready" bucket.

6. Click `Mark Replied` on a `Sent` target.
Outcome: stage changes to `Replied`, response summary field opens, and next-step prompt appears.

7. Click `Pass` on any queue item.
Outcome: item exits active queue, reason is required, and target is suppressed from default shortlist recommendations.

## Action Mapping: Current Reads vs Future Writebacks

| UI Action | Current Pipeline Reads (already available) | Required Future Writeback |
|---|---|---|
| Build shortlist table | `MarketDataset.businesses[]` (`name`, `rating`, `reviews`, `phone`, `website`, `location`) | `shortlist_items` (`target_key`, `priority`, `status`, `notes`) |
| Show listing comp anchor | `MarketDataset.listings[]` (`asking_price`, `cash_flow`, `industry`, `location`) | `target_listing_links` (`target_key`, `listing_id`, `confidence`) |
| Display source reliability badge | `MarketDataset.coverage[]` (`source`, `status`, `records`, `duration_ms`) | none (read-only) |
| Render rationale bullets | `businesses`, `listings`, `signals` fusion in view model | `rationale_overrides` (user-edited rationale text) |
| Add target to outreach queue | selected shortlist row + thesis from `MarketDataset.query` | `outreach_queue` (`target_key`, `stage`, `created_at`, `owner`) |
| Advance outreach stage | queue row state | `outreach_events` (`target_key`, `from_stage`, `to_stage`, `at`, `actor`) |
| Save draft message | thesis + evidence snippets | `outreach_drafts` (`target_key`, `version`, `body`, `updated_at`) |
| Mark replied / qualified / pass | queue row state + user input | `outreach_outcomes` (`target_key`, `outcome`, `summary`, `next_step`) |

## Proposed Writeback Entities (Future)

1. `shortlist_items`: persistent shortlist curation state.
2. `outreach_queue`: current outreach stage per target.
3. `outreach_events`: immutable timeline for stage transitions.
4. `outreach_drafts`: editable outbound message revisions.
5. `outreach_outcomes`: response notes and disposition.

## Tradeoffs (Strengths, Risks, Unknowns)

Strengths:
1. Keeps market evidence and outreach execution in one screen.
2. Makes rationale visible at decision time, not hidden in drill-downs.
3. Uses current pipeline outputs immediately, with additive writeback tables later.

Risks:
1. Priority scoring can look precise without enough signal quality calibration.
2. Queue-state UX can become noisy without strong defaults and filtering.
3. No native sender integration means manual channel switching in early versions.

Unknowns:
1. Best heuristic for linking businesses to listings (`target_listing_links.confidence`).
2. Minimum fields needed for "ready to send" quality threshold.
3. How much draft generation should be deterministic templates vs LLM-assisted.

## Acceptance Criteria Coverage

1. Workbench layout + outreach flow: covered in wireframe and progression sections.
2. Shortlist actions, rationale visibility, progression states: covered in interactions and state model.
3. At least 5 concrete interactions: 7 interactions documented with outcomes.
4. Sample target and outreach rows: provided in two tables.
5. Data mapping to current outputs + future writebacks: explicit mapping table included.
