# A24-84 Web Concept

## Goal

Provide a simple saved-items screen that helps partners review a small set of leads and listings
without returning to the full results page.

## Artifact

- `docs/feature/hex-ui-exploration/web/concept-b-target-workbench.html`
- `docs/feature/hex-ui-exploration/artifacts/screenshots/concept-b-target-workbench.png`

## What The Screen Shows

1. Saved businesses worth discussing.
2. Saved listings kept as market context.
3. Simple statuses to show what still needs review.
4. Notes that frame what the meeting should accomplish.
5. A lightweight next-action list instead of a full outreach workstation.

## Interaction Walkthrough

1. Save a business from the results screen.
2. Save a listing if it helps explain current market inventory.
3. Open the saved-items page in a partner meeting.
4. Review which businesses deserve more research or outreach.
5. Export the short list and continue work outside the UI if needed.

## Model Mapping

- `Business` -> saved business rows.
- `Listing` -> saved listing rows.
- `MarketDataset` -> list counts and review context.

## Future Writebacks

If Scout adds persistence later, the minimum useful writebacks would be:

1. `saved`
2. `review_status`
3. `partner_note`
4. `exported_at`

## Tradeoffs

### Strengths

1. Very easy to explain in a partner meeting.
2. Keeps the saved state separate from the main search screen.
3. Does not force Scout to become a CRM too early.

### Risks

1. Some teams may want notes and saved rows embedded directly in the results page.
2. The screen only works well if the saved list stays short.

### Unknowns

1. Whether saving should be personal or shared by default.
2. Whether the product should add simple notes before adding any outreach workflow.
