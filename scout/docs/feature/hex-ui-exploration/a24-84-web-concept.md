# A24-84 Web Concept

## Goal

Provide a Hex-style target workbench and outreach studio for Scout data with a concrete web surface
that stays grounded in the current pipeline outputs.

## Artifact

- `docs/feature/hex-ui-exploration/web/concept-b-target-workbench.html`
- `docs/feature/hex-ui-exploration/artifacts/screenshots/concept-b-target-workbench.png`

## What The Screen Shows

1. A shortlist of current targets from the business universe.
2. A workbench detail area for the selected target.
3. A compare view that keeps the evidence trail visible.
4. An outreach drafting surface grounded in observed evidence.
5. Queue states that make writeback needs explicit.

## Interaction Walkthrough

1. Move a business into the shortlist from the evidence explorer.
2. Compare shortlisted targets without losing address, website, and review proof.
3. Attach a market listing as context instead of claiming a direct sale match.
4. Draft a first-touch note from the evidence stack.
5. Move the target through queue states such as `Research hold`, `Draft now`, and `Owner enrichment pending`.

## Model Mapping

- `Business` -> shortlist rows and selected target details.
- `Listing` -> market sale context card.
- `MarketDataset` -> compare table and active queue counts.

## Future Writebacks

The current pipeline does not own these yet, but the UI clearly points to them:

1. `target_state`
2. `owner_enrichment_status`
3. `outreach_draft`
4. `outreach_channel`
5. `last_action_at`

## Tradeoffs

### Strengths

1. Keeps prioritization and outreach in the same workspace.
2. Prevents the UI from inventing certainty the pipeline does not have.
3. Gives the team a concrete action surface instead of only a ranked report.

### Risks

1. Outreach state implies future persistence work that does not exist yet.
2. The concept assumes a human-in-the-loop workflow rather than full automation.

### Unknowns

1. Whether the queue should live in the same page as compare mode.
2. How far Scout should go into CRM behavior versus staying a research system.
