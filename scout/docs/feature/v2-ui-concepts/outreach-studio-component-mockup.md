# Outreach Studio Component Mockup

**Issue:** A24-87  
**Status:** Draft artifact for design review  
**Purpose:** Initial component design for managing Scout leads and campaigns in one focused workspace.

## 1) Component Intent

The Outreach Studio is the execution surface that turns Scout evidence into outreach actions:

1. Select and prioritize leads.
2. Enroll leads into campaigns/sequences.
3. Track progression from first touch to meeting/closed outcome.
4. Keep rationale visible (why this lead, why now).

This mockup is scoped to component design only (no backend or CRM integration implementation).

## 2) Desktop Mockup (ASCII)

```text
+--------------------------------------------------------------------------------------------------------------------+
| OUTREACH STUDIO                                           Query: "HVAC businesses in Los Angeles"       47 leads |
+---------------------------------------+----------------------------------------------+-------------------------+
| A) Lead Queue                         | B) Campaign Board                            | C) Lead Detail + Draft |
| Filter: [Hot] [No Touch 14d] [Owner?] | Campaign: [Q2 Owner Intro] [v]              | Lead: SoCal Heating    |
| Sort: [Scout Score desc]              |                                              | Stage: Contacted       |
|                                       | New (8)      Contacted (12)  Replied (6)    | Last touch: 9d ago     |
| 1. SoCal Heating           92         | +---------+  +------------+  +----------+   | Confidence: High       |
|    4.7* 180 rev | LA | +12% rev vel   | |Cool Air |  |SoCal Heat. |  |Valley Air|   |                         |
|    Why now: review spike + owner age  | |score 88 |  |score 92    |  |score 75  |   | Why this lead          |
|                                       | |3d idle  |  |9d idle !   |  |reply +   |   | - Top quartile rating  |
| 2. Cool Air HVAC          88          | +---------+  +------------+  +----------+   | - High review velocity |
|    4.8* 350 rev | Pasadena            |                                              | - Dense target geo     |
|                                       | Meeting (3)       Nurture (11)              |                         |
| 3. Valley Air Experts      75         | +----------+      +----------+              | Campaign timeline      |
|    4.5* 72 rev | Glendale             | |Rapid HVAC|      |Metro Air |              | 03/02 Added to seq A   |
|                                       | |meeting set      |hold 30d  |              | 03/04 Email #1 sent    |
| ...                                   | +----------+      +----------+              | 03/06 Follow-up due !  |
|                                       |                                              |                         |
| [Bulk select] [Add to campaign]       | [Drag card] [Mark stage] [Create campaign]  | Message Draft           |
| [Set owner] [Snooze]                  |                                              | Subject: HVAC intro     |
|                                       |                                              | Body: Hi {{owner_name}} |
|                                       |                                              | ...                     |
|                                       |                                              | [Send] [Save draft]     |
+---------------------------------------+----------------------------------------------+-------------------------+
```

## 3) Mobile/Tablet Adaptation

```text
[Top tabs] Queue | Board | Draft

Queue:
- Compact lead list with score + stage + "next action" chip.
- Multi-select enters sticky action bar: Add to campaign / Snooze / Assign.

Board:
- Horizontal swipe between stages.
- Tap card opens bottom sheet with timeline + quick actions.

Draft:
- Full-screen composer with variable chips ({{owner_name}}, {{city}}, {{thesis_hook}}).
```

## 4) Component Anatomy

1. `Lead Queue`: ranked list from Scout evidence with rationale snippets and bulk actions.
2. `Campaign Board`: stage-based progression for campaign execution.
3. `Lead Detail + Draft`: provenance-aware context + timeline + outbound message composer.

## 5) Core Interactions

1. `Enroll from queue`: user selects leads and clicks `Add to campaign`; leads appear in `New`.
2. `Advance stage`: user drags a card or uses `Mark stage` to move `Contacted -> Replied -> Meeting`.
3. `Idle risk surfacing`: cards older than SLA threshold show `!` and are filterable (`No Touch 14d`).
4. `Personalized drafting`: template variables auto-fill from lead profile and query context.
5. `Follow-up logging`: sending/saving a draft writes timeline events and updates `last_touch_at`.
6. `Reason visibility`: every lead retains a `Why this lead` panel to prevent outreach without evidence.

## 6) Campaign and Lead States

| Entity | States | Notes |
|---|---|---|
| Lead | `new`, `contacted`, `replied`, `meeting`, `nurture`, `closed_won`, `closed_lost` | State badges visible in queue + board |
| Campaign | `draft`, `active`, `paused`, `completed` | Campaign-level state gates sending actions |
| Message | `draft`, `scheduled`, `sent`, `bounced` | Bounced messages trigger risk chip |

## 7) Mapping to Current Scout Models

| UI Field / Behavior | Current pipeline source | Notes |
|---|---|---|
| Lead identity (name, location, rating, reviews) | `Business` in `MarketDataset.businesses` | Directly available now |
| For-sale signals, asking/SDE context | `Listing` in `MarketDataset.listings` | Used for prioritization context |
| Query context chip | `Query` | Shown in header + template variables |
| Coverage/quality confidence hints | `MarketDataset` source metadata | Displayed as confidence/quality chips |

## 8) Required Future Writebacks

The current architecture is pipeline-first/read-focused, so Outreach Studio needs a lightweight writeback model:

1. `outreach_leads` table: stage, owner, priority, last touch, snooze.
2. `campaigns` table: campaign metadata and status.
3. `campaign_members` table: lead enrollment + per-lead sequence progress.
4. `message_events` table: drafts/sends/replies/bounces with timestamps.
5. `activity_log` table: normalized timeline entries per lead.

## 9) Design Tradeoffs

1. `Strength`: keeps evidence and execution on one screen, reducing context switching.
2. `Strength`: stage board makes pipeline health and bottlenecks obvious.
3. `Risk`: can become dense for first-time users; onboarding hints are likely needed.
4. `Risk`: without clear SLAs, stage movement may be inconsistent across users.
5. `Unknown`: best default stage taxonomy for different industry playbooks.
