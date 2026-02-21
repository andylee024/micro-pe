# Scout V1: Research & Findings

**Status:** Research complete — ready for prioritization
**Date:** 2026-02-21
**Branch:** `feature/scout-v1`
**Author:** Andy Lee + Claude Sonnet 4.6

---

## Overview

V0 shipped a complete 4-pane Bloomberg-style terminal UI with mock data, keyboard navigation, pane focus, source drill-down, and a chat input scaffolding. The layout and interaction model are validated. V1's job is to make every pane live — real data, real AI responses, real benchmarks — and fix the gaps in the current shell.

This document catalogs everything that needs to change, organized by theme, with an honest assessment of effort and dependency.

---

## 1. Bugs (Pre-existing, fix immediately)

These are defects in the current V0 code that should be corrected before any V1 work begins.

### B1 — "total" duplication in market overview
`mock_research.json` has `"est_market_value": "$58M total market"` and the rendering code appends ` total` again, producing: `$58M total market total`.
**Fix:** Remove ` total` from the `create_market_overview_panel` render call.
**Effort:** 1 line.

### B2 — Trend value spacing inconsistency
`job_postings` shows `↑ 45` (space between arrow and number) but `search_volume` shows `↑12%` (no space) because the mock data embeds the arrow. `_trend_style()` looks for `↑` in the value to apply color, which works, but the display is visually inconsistent.
**Fix:** Standardize — store raw numbers in data, let the renderer apply arrow + color. Or ensure all arrow-prefixed values use consistent spacing (`↑ 12%` not `↑12%`).
**Effort:** Small — data + render change.

### B3 — Reddit thread count mismatch
`pulse.sources.reddit` says `15` but `pulse.sources.reddit_threads` only contains 4 entries. The summary count and drill-down array are independently maintained and will always drift.
**Fix:** In the drill-down view, show "showing N of M" rather than implying completeness. Long-term: derive the count from the array length.
**Effort:** 1 line in components.py.

### B4 — `review_volume` missing thousands separator
`market_overview.quality.review_volume` renders as `8400` instead of `8,400`.
**Fix:** Format with `f"{n:,}"`.
**Effort:** 1 line.

---

## 2. Opening / Onboarding Screen

### Current state
The CLI requires a full query argument before anything opens:
`scout research "HVAC businesses in Los Angeles"`
There is no friction-reducing entry point. The 4-pane layout cold-starts immediately.

### What it needs to be

A two-stage pre-terminal flow:

**Stage 1: Splash + thesis input**
Full-terminal single pane. ASCII wordmark, one text input for the thesis statement, recent queries list. Pressing Enter transitions to stage 2.

```
  ████████  ██████  ██████  ██  ██  ████████
  ██        ██      ██  ██  ██  ██     ██
  ███████   ██      ██  ██  ██  ██     ██
       ██   ██      ██  ██  ██  ██     ██
  ████████  ██████  ██████  ██████     ██

  Bloomberg Terminal for Small Business Acquisition

  ──────────────────────────────────────────

  > HVAC businesses in Los Angeles▌

  recent:   HVAC · Los Angeles
            plumbing · Chicago
            auto repair · Phoenix
```

**Stage 2: Processing / progress screen**
Shows pipeline stages with live status updates as each data source completes. This is the moment where Scout feels like a real intelligence platform rather than a slow CLI.

```
  SCOUT  hvac businesses  ·  los angeles, ca  ·  researching...

  ✓  Google Maps — 12 businesses found
  ✓  BizBuySell — 34 listings (last 90 days)
  ⠸  Reddit — sourcing threads...
  ◻  FDD filings
  ◻  AI analysis (Claude Sonnet)
```

**Implementation notes:**
- Add a `screen` state to `ScoutTerminal`: `splash → loading → ready`
- Splash screen handles its own keyboard input (text entry, arrow keys for recent queries, Enter to submit)
- Recent queries stored in `~/.scout/history.json` (max 10 entries)
- `scout research` with no argument opens the splash; with an argument, skips to loading
- The `--mock-data` flag should still bypass both stages and go straight to ready

---

## 3. Live AI Assistant (Claude Sonnet)

### Current state
`chat_submit()` appends `{"q": ..., "a": "..."}` — literal three dots. The assistant pane is fully inert. The input scaffolding, history rendering, and chat mode UX are all in place.

### What's needed

**3a — Claude API integration**
Wire `chat_submit()` to the Anthropic API. The assistant should receive a full system prompt containing the current market context (businesses, benchmarks, pulse, market overview) and respond to natural-language questions.

System prompt structure:
```
You are Scout, a research assistant for small business acquisition.

MARKET CONTEXT:
Industry: HVAC | Location: Los Angeles, CA
12 businesses found. Median revenue $1.2M. B+ outlook.

BUSINESSES:
1. Cool Air HVAC — 4.8★ 350 reviews — est. $1.5M revenue
2. Precision Comfort — 4.9★ 420 reviews — est. $1.9M revenue
...

MARKET PULSE:
Opportunities: [...]
Risks: [...]
Reddit threads: [...]

Answer in 1-3 sentences. Be specific. Cite business names and numbers.
```

**3b — Filter/sort capability**
The assistant should be able to mutate the target list. When a user asks "show me businesses with 150+ reviews" the assistant should:
1. Identify the filter intent
2. Apply it to `self.businesses` → `self.filtered_businesses`
3. Return a response confirming the filter was applied
4. The target list rerenders with only matching businesses

This requires:
- `filtered_businesses` state on `ScoutTerminal` (initially `None`, meaning show all)
- A `set_filter(predicate_fn)` method
- The assistant response can include a structured action alongside the prose reply

**3c — Response streaming**
For a terminal that feels live, responses should stream token-by-token rather than appearing all at once after a delay. The assistant pane needs to handle a partial-response state and update the display as tokens arrive.

**3d — Chat history scroll**
If a user asks 5+ questions, earlier ones scroll off. Need `chat_scroll_offset` state and `Ctrl+Up/Down` bindings when focused on the assistant pane.

**3e — Action hints in responses**
When the assistant applies a filter, the response should include a visible `[Enter] apply filter` or `[Esc] clear filter` affordance (already stubbed in the mock chat history). This needs to be a real action, not cosmetic.

---

## 4. Business Detail View

### Current state
Pressing Enter on a business opens a 2-line inline expansion within the target list showing phone + website + `[W]` `[R]` links. `create_business_profile_panel` exists in `components.py` and renders a full detail view with contact, financials, review themes, and next steps — but it's not wired to anything.

### What's needed

**4a — Full profile panel on Enter**
When a business is opened, the target list pane should transform into (or be replaced by) the full `create_business_profile_panel`. The bottom-left pane becomes the detail view; the target list is recoverable via Esc or `B`.

This is already partly designed — `opened_business` state exists, `close_detail()` exists. The panel just needs to be rendered into `target_list` when `opened_business` is set.

**4b — Financial estimates in the detail view**
`Business.estimated_revenue`, `estimated_cash_flow`, `estimated_value`, `confidence` are populated in mock data and mapped in `_business_to_dict()` but the target list renders none of it. The profile panel should show:
- Estimated revenue vs. median benchmark
- Estimated cash flow / EBITDA margin
- Estimated valuation range
- Confidence indicator (high/medium/low with color)

**4c — Confidence badge in the target list**
Even in the list view, confidence should be visible. A subtle badge on the right side of each row: `·  high` in green, `medium` in yellow, `low` in dim would give quick signal.

---

## 5. Market Data — Real Sources

### Current state
Both `market_overview` and `pulse` are seeded entirely from mock JSON. The `_market_overview_from_result()` and `_market_pulse_placeholder()` fallbacks in `terminal.py` produce empty/placeholder data when no mock is loaded.

### What's needed

**5a — BizBuySell benchmarks (market overview)**
The `data-pipeline-v0` feature branch has a BizBuySell scraper. It needs to be wired into the `ResearchMarket` use case so that `market_overview.financial` is populated from real listing data for any industry/location query.

Fields to populate: `median_revenue`, `ebitda_margin`, `typical_acquisition`, `fdd_count`, `confidence`, `revenue_range`, `margin_range`.

**5b — FDD filings (market overview sources)**
The Minnesota + Wisconsin FDD scrapers exist. They need to be queried at search time and their results surfaced in `market_overview.sources.fdd_filings`. Industry matching is the hard part — "HVAC" needs to map to the right FDD category.

**5c — Reddit sentiment (market pulse)**
The `_archive/reddit-sentiment/` research exists. Reddit's pushshift or direct API needs to be queried for threads mentioning the industry. The AI should summarize opportunities, risks, and operating models from the thread content.

**5d — Review aggregation (market pulse quality)**
`quality.sentiment_positive` is currently hardcoded. Actual Google review content (scraped alongside business data) should feed a sentiment score.

**5e — Trend data**
`trends.job_postings`, `trends.new_entrants`, `trends.search_volume` are static mock values. These could come from Indeed/LinkedIn job postings, Google Trends API, or BizBuySell new listing counts. Lowest-effort: Google Trends API for `search_volume`, BizBuySell listing count delta for `new_entrants`.

---

## 6. Data Model Problems

### 6a — No original query stored
`ResearchResult` stores `summary.industry` and `summary.location` (parsed) but not the original freeform query. When displaying the header or recent history, the app reconstructs `"HVAC businesses · Los Angeles, CA"` from parts, losing the user's original phrasing.
**Fix:** Add `query: str = ""` to `MarketSummary`.

### 6b — Untyped `market_overview` and `pulse` dicts
Both are `dict = field(default_factory=dict)` in `ResearchResult`. Every consumer must guess at key names and handle missing keys with `.get()` everywhere. This will cause subtle bugs as real data sources add and remove fields.
**Fix (V1.5):** Define `MarketOverview` and `MarketPulse` dataclasses. Keep dict as the wire format but parse into typed objects at the boundary.

### 6c — Duplicate benchmark sources of truth
`summary.benchmarks[0]` and `market_overview.financial` contain overlapping data. When real BizBuySell data arrives, which one is authoritative? The mapping needs to be explicit and one-directional.
**Fix:** `market_overview.financial` is the UI source of truth. `summary.benchmarks` feeds it via a mapping function. Don't read `summary.benchmarks` directly in UI code.

### 6d — Multiple sessions / thesis history
Running a second query creates a completely fresh `ScoutTerminal` session. There is no in-app mechanism to:
- Switch between saved searches
- Compare two markets side-by-side
- Re-open a previous session without re-fetching
**Fix (V1 minimum):** Recent queries on splash screen, each backed by a cache file. Full session management is V2+.

---

## 7. UX / Interaction Gaps

### 7a — No "home" escape hatch
If you Tab to market overview and want to return to the target list quickly, you must Tab 2 more times. There's no single "go home" key.
**Fix:** `Esc` (when no sources or detail is open) → `focused_pane = "target_list"`.

### 7b — Footer doesn't show `/` when assistant is focused
The footer shows `/ chat` only when `target_list` is focused. When `scout_assistant` is focused, the `/` key still works but there's no hint.
**Fix:** Include `/ chat` in the assistant-focused footer state.

### 7c — Tab during chat mode swallows keypress silently
If you're typing in chat mode and press Tab, nothing happens (correctly blocked) but there's no feedback. Fine for now, but worth noting.

### 7d — Progress panel in target list has no focused state
When businesses are loading and the target list shows `create_progress_panel()`, the focused state is not passed — the pane border won't be cyan even if target_list is the focused pane.

### 7e — Page size is hardcoded
`self.page_size = 8` doesn't adapt to terminal height. On a large display, the bottom row wastes significant space.
**Fix (V1.5):** Compute page size from `console.size.height` at startup and on resize.

### 7f — No confirmation on quit
Pressing `Q` immediately kills the session. If the user has a filter applied or active chat context, this is lossy.
**Fix (optional):** Brief "Press Q again to quit" confirmation on first press. Or just accept this — Bloomberg terminal users expect hard exits.

### 7g — Export is silent
`export_csv()` updates the header status bar briefly. There's no path display or confirmation that the file actually exists.
**Fix:** Flash a message with the full output path.

---

## 8. Dead Code / Technical Debt

### 8a — Orphaned components in `components.py`
These functions exist but are called from zero live code paths (only legacy compatibility stubs):
- `create_overview_pulse_panel()` — replaced by separate overview/pulse panels
- `create_assistant_panel()` — replaced by `create_scout_assistant_panel()`
- `create_business_profile_panel()` — exists but unwired (this one should be wired, not deleted)
- `create_header()` — replaced by `create_header_text()`
- `create_business_table()` — old table-based list, replaced by `create_target_list_panel()`
- `create_status_bar()` — unused
- `create_footer_instructions()` — unused
- `create_progress_panel()` — used in one place (target list loading state); keep this one

**Estimate:** ~150 lines of dead code to remove.

### 8b — `main.py` has emoji-heavy fallback CLI mode
The `--no-ui` mode in `main.py` is a rough debug path that won't be needed once V1 ships. It uses click.echo with emoji which is inconsistent with the terminal-first design philosophy.

### 8c — `create_business_profile_panel` has a `score` field
The profile panel renders `score {n}` in the subtitle, sourced from a calculated integer score. But the scoring engine doesn't exist yet (it's a V2 feature). The UI renders `score 96` for businesses in mock data because rating × 20 = score. This is a fake metric being displayed as if it's real.
**Fix:** Remove the `score` display from the profile panel until a real scoring engine exists.

---

## 9. What's Working Well — Don't Change

- **2-row hierarchy** (context top, work bottom) — validated UX pattern
- **Semantic color system** (green/red/yellow/cyan/dim white) — clean and coherent
- **Tab pane navigation + cyan focus border** — correct mental model
- **Source drill-down** (`s` → sources, `Esc` → back) — solid
- **Chat input** (`/` to enter, Esc to exit, green cursor) — reads naturally
- **Vim navigation** (`gg/G`, `j/k`) — power user friendly
- **Context-sensitive footer** — dynamically shows relevant keys
- **CSV export** — functional

---

## 10. External Dependencies / Research Needed

| Capability | Dependency | Status | Notes |
|---|---|---|---|
| Live assistant | Anthropic Claude API | Ready | Need API key + streaming support |
| BizBuySell benchmarks | BizBuySell scraper | Scraper built | Needs integration into ResearchMarket |
| FDD filings | MN/WI scrapers | Scrapers built | Industry mapping needed |
| Reddit sentiment | Reddit API or Pushshift | Researched (archived) | Rate limits are a concern |
| Google Trends | PyTrends (unofficial) | Not started | Low-effort, medium value |
| Job postings | Indeed/LinkedIn unofficial | Not started | High-effort, medium value |
| Session persistence | Local JSON files | Not started | Simple, needed for recent queries |
| ASCII wordmark | Rich or pyfiglet | Not started | `pyfiglet` can generate at runtime |

---

## Summary — Gap Inventory

| ID | Gap | Category | Effort | Priority |
|---|---|---|---|---|
| B1 | "total" duplication | Bug | XS | P0 |
| B2 | Trend spacing | Bug | XS | P0 |
| B3 | Reddit count mismatch | Bug | XS | P0 |
| B4 | review_volume formatting | Bug | XS | P0 |
| U1 | Opening splash screen | UX | L | P1 |
| U2 | Loading progress screen | UX | M | P1 |
| U3 | Esc → home pane | UX | XS | P1 |
| U4 | Assistant footer hint | UX | XS | P1 |
| U5 | Chat history scroll | UX | S | P2 |
| U6 | Page size adaptive | UX | S | P2 |
| U7 | Export confirmation | UX | XS | P2 |
| F1 | Claude API integration | Feature | L | P1 |
| F2 | Assistant filter/sort | Feature | L | P1 |
| F3 | Response streaming | Feature | M | P1 |
| F4 | Business detail panel (full) | Feature | M | P1 |
| F5 | Confidence badge in list | Feature | S | P1 |
| F6 | Financial estimates in detail | Feature | S | P1 |
| F7 | BizBuySell real data | Feature | M | P1 |
| F8 | FDD real data wired | Feature | M | P2 |
| F9 | Reddit sentiment | Feature | L | P2 |
| F10 | Recent query history | Feature | S | P2 |
| D1 | Original query stored | Data | XS | P1 |
| D2 | Typed market_overview/pulse | Data | M | P2 |
| D3 | Benchmark deduplication | Data | S | P2 |
| D4 | Session management | Data | L | P3 |
| T1 | Dead code cleanup | Tech debt | S | P1 |
| T2 | Fake score field removed | Tech debt | XS | P1 |
| T3 | No-UI CLI cleanup | Tech debt | S | P3 |

**Effort key:** XS = <1hr, S = 1-4hrs, M = 4-8hrs (half day), L = 1-2 days

---

*This research document is the basis for `plan.md`. Prioritization review with stakeholders recommended before implementation begins.*
