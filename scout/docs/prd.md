# Scout PRD

**Product:** Scout
**Positioning:** Terminal-native market-sourcing engine for SMB acquisition search
**Status:** Planning baseline
**Last Updated:** 2026-03-10

## 1. Product Definition

Scout is a terminal-first system for finding, researching, enriching, and actioning SMB acquisition targets at scale.

Scout is not a CRM, not a spreadsheet replacement, and not a marketplace. It is the operating system for market sourcing.

Scout should own five things:

1. Turning a plain-English market thesis into a repeatable search object.
2. Building and refreshing a target universe from live data sources.
3. Letting power users scan that universe quickly in a dense terminal UI.
4. Triggering agent workflows against businesses and leads.
5. Syncing curated leads into a familiar collaboration tool for non-technical teammates.

The core split is:

- `Scout TUI` for search, triage, workflow triggering, and outbound operations.
- `Scout DB` as the canonical system of record.
- `Linear` and later `Asana` as collaboration surfaces.

## 2. Problem

Search funds and small acquisition teams still do market sourcing with a brittle stack:

1. Search intent lives in someone's head or a spreadsheet tab.
2. Business discovery is manual and inconsistent.
3. Research artifacts are scattered across notes, spreadsheets, and browser tabs.
4. There is no durable queue for enrichment, research, and outbound work.
5. Non-technical collaborators cannot participate without either using the terminal or waiting for exports.
6. Re-running a market later does not produce a clean change set.

A spreadsheet is good at tracking a curated list. It is weak at:

1. source provenance
2. repeated search runs
3. large raw universes
4. queued agent workflows
5. artifact storage
6. collaboration sync with operational state

Scout exists to solve that layer.

## 3. Goals

### Primary Goals

1. Make `market thesis -> target universe` a repeatable system.
2. Let an operator scan hundreds or thousands of businesses quickly.
3. Make research, enrichment, and outbound prep agent-triggerable from the terminal.
4. Keep curated leads accessible to non-technical teammates in a familiar tool.
5. Preserve source context, workflow state, and search history inside Scout.

### Secondary Goals

1. Make it easy to export and dump filtered sets.
2. Make reruns and market diffs first-class.
3. Keep the architecture simple enough that autonomous agents can implement features independently.

## 4. Non-Goals

Scout v1 should not be:

1. a general-purpose CRM
2. a full web app
3. a valuation engine pretending to be precise
4. a broker marketplace
5. a fully autonomous deal execution agent
6. a score-heavy recommendation system

## 5. Target Users

### Operator / Searcher

The technical user running searches, scanning businesses, saving leads, and triggering workflows.

### Non-Technical Partner

A teammate who wants to review leads, add notes, discuss targets, assign owners, and request follow-up without using the terminal.

### Principal / Manager

A person who wants visibility into throughput, funnel state, and which markets are being worked.

## 6. Jobs To Be Done

### Operator Jobs

1. When I have a thesis, help me build a usable target universe quickly.
2. When I am looking at a large result set, let me scan and shortlist quickly.
3. When I find something worth work, let me trigger research, enrichment, call prep, or outbound immediately.
4. When I want to hand work to the broader team, let me push curated leads into Linear without losing context.
5. When I rerun a market later, show me what changed.

### Non-Technical Partner Jobs

1. Let me see the important context for a lead without using a technical tool.
2. Let me comment, assign, discuss, and request follow-up.
3. Let me work from a familiar collaboration surface.

### Principal Jobs

1. Show me what markets are active.
2. Show me how much of the funnel is moving.
3. Show me where agents and operators are blocked.

## 7. Product Principles

1. `Search runs are first-class.`
   A search is a durable object, not a one-off CLI string.

2. `Scout DB is canonical.`
   Linear and Asana are projections for collaboration, not the source of truth.

3. `Dense operator UX beats decorative UI.`
   The default operator experience should feel closer to a terminal or Bloomberg workflow than a dashboard.

4. `Agent workflows are first-class.`
   Research, enrich, call prep, and email draft are durable queued operations with artifacts.

5. `Curate before sync.`
   Raw universes stay in Scout. External tools only receive curated leads or action-ready work.

6. `Evidence over opinion.`
   Scout should store facts, source references, artifacts, and state. Scoring can come later.

7. `Refresh over static lists.`
   A key product advantage over spreadsheets is the ability to rerun a market and see changes.

## 8. Core Product Experience

### End-to-End Flow

1. Operator creates or reruns a market thesis.
2. Scout resolves the query and runs the ingestion workflow.
3. Scout stores raw payloads and canonical records.
4. Operator scans the universe in the TUI.
5. Operator saves businesses into a lead set.
6. Operator queues workflows on one lead or a filtered batch.
7. Scout stores workflow artifacts and state.
8. Operator pushes curated leads into Linear.
9. Non-technical teammates collaborate there.
10. Scout syncs external comments, ownership, and requests back into the canonical record.
11. Operator reruns the search later and reviews the diff.

### TUI North Star

The TUI should be an operator console, not a reporting surface.

It should optimize for:

1. throughput
2. keyboard-first interaction
3. dense scanning
4. queue visibility
5. fast workflow triggering
6. quick export and handoff

### Recommended Main Screen

```text
Scout
Query: fire protection businesses in usa
1248 found | 83 saved | 41 researched | 12 call-ready | 7 emailed | 4 replied

/filter state:ca reviews>20 has:web has:phone

+---------------------------------------------+------------------------------------------+
| UNIVERSE                                    | SELECTED                                 |
|                                             |                                          |
| > CITY OF ANGELS FIRE PROTECTION  LA   406  | CITY OF ANGELS FIRE PROTECTION           |
|   Black Bird Fire Protection       Br   408 | Los Angeles                              |
|   FireProTech                      Gln  194 | [web] [phone]                            |
|   Reliable Fire Protection         LA    30 | 4284 Union Pacific Ave                   |
|   Sure Fire Protection             LA    14 | 4.9 rating · 406 reviews                 |
|                                             |                                          |
| j/k move  space save  r research            | c call   m email   e enrich   x skip     |
| b batch on filtered set                      | o open artifacts                         |
+---------------------------------------------+------------------------------------------+

+--------------------------------------------------------------------------------+
| QUEUE / OUTBOUND                                                               |
| running: enrich FireProTech | queued: call Reliable | done: email City of Angels |
+--------------------------------------------------------------------------------+

+--------------------------------------------------------------------------------+
| MARKET                                                                         |
| Fire Inspection Business | Los Angeles, CA | $1.8M | $625k CF | 2.88x           |
+--------------------------------------------------------------------------------+
```

### Required Modes

1. `Universe`
   Dense result scanning, filtering, selection, save/remove, trigger workflows.

2. `Queue`
   Running, queued, completed, failed workflows with lightweight logs and artifact links.

3. `Lead Set`
   Curated saved leads with status, next action, sync status, and export surfaces.

4. `History`
   Search runs, rerun history, and diffs.

5. `Command`
   Command line for filters, saved queries, batch actions, export, and sync.

### Required Hotkeys

1. `j` / `k` move selection
2. `space` save or unsave lead
3. `/` open command or filter line
4. `r` queue research
5. `e` queue enrichment
6. `c` queue call prep or call workflow
7. `m` queue email draft workflow
8. `b` apply a workflow to the current filtered set
9. `o` open latest artifact
10. `d` dump filtered set
11. `g` switch mode
12. `?` show hotkeys

## 9. What Scout Owns vs External Tools

### Scout Owns

1. search objects and search runs
2. raw source payloads
3. canonical business and listing records
4. lead records
5. workflow runs and artifacts
6. outbound attempts and outcomes
7. search history and diffs
8. sync metadata to external systems

### Linear Owns

1. comments and discussion
2. assignment / ownership
3. lightweight status review
4. coordination for non-technical teammates
5. requests for follow-up

### Product Rule

Linear should never become the database. It is a collaboration surface on top of Scout.

## 10. Canonical Data Model

### Search

A durable market thesis.

Suggested fields:

- `id`
- `query_text`
- `normalized_industry`
- `normalized_location`
- `created_at`
- `created_by`

### SearchRun

A concrete execution of a Search.

Suggested fields:

- `id`
- `search_id`
- `started_at`
- `completed_at`
- `status`
- `source_counts_json`
- `business_count`
- `listing_count`
- `filters_json`

### Business

Canonical operating business discovered from sources like Google Maps.

Suggested fields:

- `id`
- `canonical_name`
- `city`
- `state`
- `country`
- `phone`
- `website`
- `rating`
- `review_count`
- `latest_source_payload_ref`
- `first_seen_at`
- `last_seen_at`

### Listing

Canonical business-for-sale listing discovered from sources like BizBuySell.

Suggested fields:

- `id`
- `canonical_title`
- `source`
- `source_listing_id`
- `location`
- `asking_price`
- `cash_flow`
- `multiple`
- `first_seen_at`
- `last_seen_at`

### Lead

A curated business selected out of a universe for further work.

Suggested fields:

- `id`
- `business_id`
- `search_id`
- `search_run_id`
- `status`
- `saved_at`
- `saved_by`
- `owner`
- `next_action`
- `priority`

### WorkflowRun

A queued or completed agent task against a business or lead.

Suggested fields:

- `id`
- `lead_id`
- `business_id`
- `workflow_type`
- `status`
- `queued_at`
- `started_at`
- `completed_at`
- `requested_by`
- `requested_via`
- `input_json`
- `result_summary`

### WorkflowArtifact

A durable output from a workflow.

Suggested fields:

- `id`
- `workflow_run_id`
- `artifact_type`
- `storage_ref`
- `preview_text`
- `created_at`

### OutboundAttempt

A concrete email, call, or other outbound action.

Suggested fields:

- `id`
- `lead_id`
- `channel`
- `provider`
- `status`
- `started_at`
- `completed_at`
- `transcript_ref`
- `draft_ref`
- `outcome_summary`

### ExternalRecordLink

A mapping from a Lead to a collaboration-system record.

Suggested fields:

- `id`
- `lead_id`
- `provider`
- `external_id`
- `external_url`
- `sync_status`
- `last_push_at`
- `last_pull_at`

### Note

An internal or synced note tied to a lead.

Suggested fields:

- `id`
- `lead_id`
- `source`
- `body`
- `author`
- `created_at`

### SearchDiff

A materialized summary of what changed between two runs.

Suggested fields:

- `id`
- `search_id`
- `previous_run_id`
- `current_run_id`
- `new_business_count`
- `removed_business_count`
- `changed_business_count`
- `summary_json`

## 11. Status Models

### Lead Statuses

1. `saved`
2. `researching`
3. `researched`
4. `enriched`
5. `call_ready`
6. `contacted`
7. `responded`
8. `archived`

### Workflow Statuses

1. `queued`
2. `running`
3. `completed`
4. `failed`
5. `canceled`

### Search Run Statuses

1. `queued`
2. `running`
3. `completed`
4. `partial`
5. `failed`

## 12. Workflow Catalog

### `research_business`

Purpose: produce a concise research summary and capture evidence about what the business appears to do.

### `enrich_business`

Purpose: collect structured details not available in the discovery source.

### `prepare_call`

Purpose: produce a call brief and suggested talking points.

### `call_business`

Purpose: attempt a call, persist transcript, and record the outcome.

### `draft_email`

Purpose: generate an outbound email draft using current context.

### `sync_linear`

Purpose: push or update curated leads in Linear and record the sync result.

### `dump_list`

Purpose: export the current filtered set to CSV, markdown, or another sink.

Each workflow must produce:

1. a durable status
2. a durable artifact or explicit no-artifact outcome
3. a short result summary visible in the TUI
4. structured failure information on error

## 13. Technical Architecture

### Existing Ingestion Kernel To Preserve

Scout already has the correct ingestion nucleus documented in `scout/docs/architecture.md`:

- `Runner`
- `Workflow`
- `DataSource`
- `DataStore`
- canonical pipeline models: `Query`, `Business`, `Listing`, `MarketDataset`

This should remain the ingestion kernel.

### Product Architecture To Add

```text
               +----------------------+
               |      Scout TUI       |
               | search / scan / run  |
               +----------+-----------+
                          |
                          v
               +----------------------+
               |   App Services       |
               | searches / leads /   |
               | workflows / outbound |
               +----------+-----------+
                          |
                          v
+--------------------+  +----------------------+  +----------------------+
| Ingestion Workflow |->|      Scout DB        |<-| Collaboration Sync   |
| maps / marketplace |  | canonical source     |  | Linear / Asana       |
+--------------------+  +----------------------+  +----------------------+
                          |
                          v
               +----------------------+
               | Agent / Outbound     |
               | research enrich call |
               +----------------------+
```

### Recommended Code Layout

```text
scout/scout/
  app/
    models/
    services/
    repositories/
  operator/
    tui/
    commands/
    screens/
  workflows/
    queue.py
    handlers/
  sync/
    linear/
    asana/
  outbound/
    email/
    voice/
  pipeline/
    ...existing ingestion kernel...
```

## 14. Tech Stack

### Application Language

Python. Keep one language across ingestion, TUI, services, and workflow handlers.

### Terminal UI

Use `Textual`.

Reason:

1. Python-native and matches the current codebase.
2. Suitable for dense keyboard-first screens.
3. Good fit for worker-aware terminal interactions.

### Storage

Use two modes:

1. `SQLite + WAL` for local single-operator development.
2. `PostgreSQL` for shared and production environments.

### Workflow Queue

Use database-backed queued `workflow_runs` rather than introducing a separate orchestration product in v1.

### Collaboration

Ship `Linear` first because the team already uses it. Keep the sync surface abstract enough to add `Asana` later.

### Outbound Providers

Keep provider interfaces abstract:

1. `EmailProvider`
2. `VoiceProvider`
3. `ArtifactStore`

Scout should own the job state and result artifacts, not the outbound vendor.

## 15. MVP Definition

### Must Have

1. Search and rerun a market thesis.
2. Persist search runs, businesses, listings, and curated leads.
3. Dense TUI for scanning, saving, filtering, and batch actions.
4. Queue and view `research` and `enrich` workflows.
5. Store artifacts and workflow status.
6. Push curated leads to Linear.
7. Pull comments, owner, and requested action back into Scout.
8. Export filtered sets.
9. Show rerun diffs.

### Explicitly Not In MVP

1. complex scoring
2. full web UI
3. autonomous multi-step deal execution
4. raw-universe sync to Linear
5. full valuation modeling

## 16. Success Metrics

### Operator Metrics

1. time from search to first 25 saved leads
2. businesses reviewed per hour
3. percentage of saved leads with completed research artifacts
4. time from save to external task creation

### Team Metrics

1. percentage of curated leads reviewed by non-technical users
2. average time from collaborator request to workflow queue
3. percentage of external comments synced back into Scout

### System Metrics

1. search run success rate
2. workflow completion rate
3. sync error rate
4. average queue delay
5. rerun diff generation success rate

## 17. Risks

1. Letting Linear become the source of truth.
2. Syncing too much raw data into collaboration tools.
3. Starting with scoring before throughput and workflow are correct.
4. Weak canonicalization across repeated search runs.
5. Building a decorative TUI instead of an operator console.
6. Overcommitting to outbound providers before artifacts and queueing are stable.

## 18. Implementation Strategy

### Parent Feature 1: Search And Lead Foundation

**Goal:** turn the current ingestion output into durable product objects.

**Outcome:** Scout can persist searches, runs, businesses, listings, leads, and relationships between them.

**PR Shape:** one integration PR focused on storage schema, repositories, and app services.

**Planned Child Tasks:**

1. define and migrate canonical app tables for search, run, lead, workflow, artifact, outbound, external link, and note state
2. implement repository and service layer for searches, runs, leads, and exports
3. wire pipeline output into app-level persistence and search-run creation

### Parent Feature 2: Dense Operator TUI

**Goal:** replace the simple CLI with a dense operator console.

**Outcome:** an operator can search, scan, save, filter, and queue actions without leaving the terminal.

**PR Shape:** one integration PR focused on terminal screens, state, and hotkeys.

**Planned Child Tasks:**

1. build the Textual app shell and mode layout
2. implement universe list filtering, selection, and save/remove actions
3. implement selected-business detail, command line, and lead-set mode

### Parent Feature 3: Workflow Queue And Agent Actions

**Goal:** make research, enrich, and outbound-prep actions durable and observable.

**Outcome:** workflows can be queued, executed, retried, and reviewed with artifacts.

**PR Shape:** one integration PR focused on workflow state, handlers, and queue execution.

**Planned Child Tasks:**

1. add workflow queue model, claiming logic, and worker runner
2. implement research and enrich handlers with stored artifacts
3. implement prepare-call and draft-email handlers with TUI and CLI triggers

### Parent Feature 4: Search History And Market Diffs

**Goal:** make reruns and changes a first-class part of the product.

**Outcome:** Scout can show what changed between runs for a market and surface that inside the terminal.

**PR Shape:** one integration PR focused on reruns, diff generation, and history screens.

**Planned Child Tasks:**

1. add rerun-aware persistence and first_seen / last_seen tracking
2. implement search diff generation and storage
3. add history and diff mode to the TUI and export surfaces

### Parent Feature 5: Collaboration Sync

**Goal:** let non-technical users work from curated leads in Linear while Scout stays canonical.

**Outcome:** saved leads can be pushed to Linear and synced back into Scout with discussion and ownership.

**PR Shape:** one integration PR focused on sync adapters and collaboration state.

**Planned Child Tasks:**

1. implement lead-to-Linear projection and idempotent upsert behavior
2. sync Linear comments, owner, and requested action back into Scout
3. expose sync status and push/sync commands in the TUI and CLI

### Parent Feature 6: Outbound Operations Surface

**Goal:** make Scout useful for moving leads into outbound work, not just research.

**Outcome:** operators can manage next action, outbound status, and export/action-ready batches from the terminal.

**PR Shape:** one integration PR focused on outbound queue state and operator actions.

**Planned Child Tasks:**

1. add outbound status model and queue strip to the terminal
2. add batch export, dump-list, and action-ready views
3. add notes, next-action editing, and operational summaries for lead review

## 19. Acceptance Bar By Parent Feature

### Feature 1 Acceptance

1. A search run creates durable records for search, run, businesses, listings, and coverage.
2. Leads can be saved and removed without re-running the pipeline.
3. Exporting a curated lead set works from services without TUI dependencies.

### Feature 2 Acceptance

1. An operator can move through a large universe with keyboard navigation.
2. Save/remove and workflow hotkeys work from the main screen.
3. The terminal stays dense and readable with minimal decorative UI.

### Feature 3 Acceptance

1. Workflows can be queued and picked up by a worker.
2. Completed workflows write result summaries and artifacts.
3. Failures are visible and retryable.

### Feature 4 Acceptance

1. Re-running a search does not destroy prior history.
2. New, removed, and changed businesses can be identified between runs.
3. Diffs are visible in the TUI and exportable.

### Feature 5 Acceptance

1. Curated leads can be projected to Linear idempotently.
2. Linear comments and owner changes sync back into Scout.
3. Sync failures are visible without breaking core Scout workflows.

### Feature 6 Acceptance

1. Operators can move leads through outbound-oriented statuses.
2. Batch dumps produce useful action-ready outputs.
3. The outbound queue is visible from the terminal without leaving the main workflow.

## 20. Open Questions

1. Should `Lead` belong to exactly one `Search`, or should it be reusable across searches?
2. Should outbound providers be dry-run only in the first release, or should one provider be fully wired?
3. Should collaboration requests map to comments, status changes, or both?
4. When should scoring re-enter the roadmap after the throughput and workflow basics are complete?
