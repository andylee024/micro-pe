# Scout V1: Implementation Plan

**Status:** Draft — pending prioritization review
**Date:** 2026-02-21
**Branch:** `feature/scout-v1`
**Depends on:** `research.md` in this directory

---

## Guiding Principle

V1 makes every pane live. V0 proved the layout; V1 fills it with real intelligence. The four pillars are:
1. **Onboarding** — A real entry point that sets context before the UI loads
2. **Intelligence** — A live Claude assistant that can answer questions and manipulate the target list
3. **Data** — Real benchmarks, real sentiment, real financial estimates per business
4. **Polish** — Fix bugs, wire the orphaned detail panel, clean dead code

Ship in milestone order. Each milestone is independently useful.

---

## Milestone 0 — Bugs & Tech Debt
**Goal:** Clean slate before any new feature work.
**Can be done in a single PR by one person in <1 day.**

### Tasks

| ID | Task | File(s) | Notes |
|---|---|---|---|
| B1 | Fix "total" duplication | `components.py` | Remove ` total` suffix from est_market_value render |
| B2 | Fix trend spacing | `mock_research.json`, `components.py` | Standardize raw numbers in data, arrow added by renderer |
| B3 | Fix Reddit count display | `components.py` | "showing N of M" in sources view |
| B4 | Fix review_volume formatting | `components.py` | `f"{n:,}"` |
| T1 | Remove dead component code | `components.py` | Delete `create_overview_pulse_panel`, `create_assistant_panel`, `create_header`, `create_business_table`, `create_status_bar`, `create_footer_instructions` (~150 lines) |
| T2 | Remove fake score field | `components.py`, `terminal.py` | Remove `score` from profile panel subtitle |
| D1 | Add `query` to MarketSummary | `models.py`, `mock_data.py`, `terminal.py` | `query: str = ""` field |
| U3 | Esc → home pane | `terminal.py`, `keyboard.py` | When nothing open, Esc sets `focused_pane = "target_list"` |
| U4 | Footer hint for assistant pane | `components.py` | Add `/ chat` to `scout_assistant` focused footer state |
| U7 | Export path confirmation | `terminal.py` | Log full path to status bar on export |

**Success criteria:** `pytest` still green, mock demo looks clean, no visible bugs.

---

## Milestone 1 — Opening Experience
**Goal:** A proper entry point. First impressions matter.

### M1.1 — Splash screen

**New file:** `scout/ui/splash.py`

```python
class SplashScreen:
    def __init__(self, recent_queries: List[str]):
        ...
    def run(self) -> Optional[str]:
        """Blocking — returns thesis string or None if user quit."""
        ...
```

- Full-terminal single pane using Rich `Live`
- ASCII wordmark via `pyfiglet` (add to dependencies) or hard-coded string
- Single text input line with cursor (reuse chat input pattern from `KeyboardHandler`)
- Recent queries list (up to 5, navigable with arrow keys)
- `Enter` → return query string; `Esc` → return None (quit)

**New file:** `scout/shared/history.py`

```python
HISTORY_PATH = Path.home() / ".scout" / "history.json"

def load_history() -> List[str]: ...
def save_query(query: str) -> None: ...  # prepend, dedupe, max 10
```

### M1.2 — Loading / progress screen

**Modify:** `terminal.py` — add `screen` state machine

```python
# States
SCREEN_SPLASH = "splash"
SCREEN_LOADING = "loading"
SCREEN_READY = "ready"
```

- New `_build_loading_layout()` renders a single-pane progress view
- `ResearchMarket` use case emits progress callbacks (pass a `on_progress` callable)
- Each data source reports status: `pending | running | done | error`
- Display updates in real time as sources complete

**Modify:** `main.py`
- `scout research` with no argument → open splash screen first
- `scout research "query"` → skip splash, go straight to loading
- `--mock-data` → skip both splash and loading, go straight to ready

### M1.3 — Entry point flow

```
scout (no args)        → splash → loading → ready
scout research         → splash → loading → ready
scout research "query" → loading → ready
scout research "query" --mock-data → ready (instant)
```

**Files to modify:** `main.py`, new `splash.py`, new `history.py`
**New dependency:** `pyfiglet` (or hard-code the wordmark)
**Effort:** M (1 day)

---

## Milestone 2 — Live AI Assistant
**Goal:** The assistant pane actually works. This is the product's core differentiator.

### M2.1 — Claude API integration

**Modify:** `terminal.py` — `chat_submit()` method

```python
def chat_submit(self) -> None:
    q = self.chat_input.strip()
    if not q:
        self.exit_chat_mode()
        return
    # Optimistic UI: show question with loading indicator
    self.chat_history.append({"q": q, "a": "..."})
    self.chat_input = ""
    self.chat_mode = False
    self._update_display()
    # Fire async request
    threading.Thread(target=self._run_assistant, args=(q,), daemon=True).start()
```

**New method:** `_run_assistant(query: str)`

```python
def _run_assistant(self, query: str) -> None:
    """Call Claude API with market context, update last chat entry."""
    from anthropic import Anthropic
    client = Anthropic()

    system_prompt = self._build_assistant_context()
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=300,
        system=system_prompt,
        messages=[{"role": "user", "content": query}],
    )
    answer = response.content[0].text
    # Optionally parse structured action from response
    action = self._parse_assistant_action(answer)
    self.chat_history[-1]["a"] = answer
    if action:
        self._apply_assistant_action(action)
    self._update_display()
```

**New method:** `_build_assistant_context() -> str`
Builds a structured system prompt from `self.businesses`, `self.market_overview`, `self.market_pulse`.

### M2.2 — Filter/sort from assistant

The assistant can apply filters to the target list. Approach: structured response format.

**Design:** Claude is instructed to optionally return a JSON action block at the end of its response:

```
3 businesses match: Cool Air HVAC (350 reviews), Precision Comfort (420), Rapid Response (310).

ACTION:{"type":"filter","field":"reviews","op":"gte","value":150}
```

The UI strips the ACTION block before display, then applies it.

**New state on ScoutTerminal:**
```python
self.active_filter: Optional[str] = None         # human-readable description
self.filtered_businesses: Optional[List[Dict]] = None  # None = show all
```

**Filter application:** `_apply_assistant_action(action: dict)` mutates `filtered_businesses` and updates the `scope_count` + `active_filter` shown in the assistant pane footer.

**Key binding:** `Esc` (in assistant pane) clears the active filter in addition to exiting chat mode.

### M2.3 — Response streaming

For perceived performance, stream tokens rather than waiting for the full response.

```python
with client.messages.stream(...) as stream:
    buffer = ""
    for text in stream.text_stream:
        buffer += text
        self.chat_history[-1]["a"] = buffer + "▌"  # streaming cursor
        self._update_display()
    self.chat_history[-1]["a"] = buffer  # final, no cursor
    self._update_display()
```

### M2.4 — Chat history scroll

**New state:** `self.chat_scroll_offset: int = 0`
**New bindings** (when `focused_pane == "scout_assistant"`):
- `Ctrl+Up` / `k` when in assistant pane → `chat_scroll_up()`
- `Ctrl+Down` / `j` when in assistant pane → `chat_scroll_down()`
- Auto-scroll to bottom on new message

**Files:** `terminal.py`, `keyboard.py`, `components.py`
**New dependency:** `anthropic` Python SDK
**Effort:** L (1.5 days including streaming + filter)

---

## Milestone 3 — Business Detail View
**Goal:** The full profile panel is wired and financials are visible.

### M3.1 — Wire the profile panel

**Modify:** `terminal.py` — `_build_layout()`

When `self.opened_business` is set, render the target list slot with `create_business_profile_panel` instead of `create_target_list_panel`:

```python
if self.opened_business:
    layout["target_list"].update(
        create_business_profile_panel(
            self.opened_business,
            market_data=self.market_overview,
        )
    )
else:
    layout["target_list"].update(create_target_list_panel(...))
```

`close_detail()` already handles Esc to go back to the list. No keyboard changes needed.

### M3.2 — Financial estimates in profile

`create_business_profile_panel` already renders `revenue`, `ebitda`, `valuation` fields. `_business_to_dict()` already maps `estimated_revenue` → `revenue`. The data is there — it just needs real numbers behind it.

For V1 (before real per-business estimates exist), show estimates with explicit confidence caveat:
- `$1.5M rev  (estimated · medium confidence)`
- Color-code the confidence: green = high, yellow = medium, dim = low

### M3.3 — Confidence badge in target list

In `create_target_list_panel`, add a right-aligned confidence indicator to selected rows:

```
  ▶ 5  Precision Comfort                             high
       ★★★★★  4.9  420 reviews
```

- `high` in green, `medium` in yellow, `low` in dim white
- Only show on selected row to reduce visual noise

**Files:** `components.py`, `terminal.py`
**Effort:** M (half day)

---

## Milestone 4 — Real Data Sources
**Goal:** Every pane shows real data for real queries.

### M4.1 — BizBuySell benchmarks

**Existing:** `sources/marketplaces/bizbuysell.py` (scraper exists)
**Gap:** Not called from `ResearchMarket` use case

**Modify:** `application/research_market.py`
- Call BizBuySell scraper with industry + location
- Map results → `market_overview.financial` and `market_overview.sources.bizbuysell`
- Add to loading progress display

Industry mapping is the key challenge: "HVAC" → BizBuySell category "Heating & Air Conditioning". Need a mapping table for the top 20 industries.

### M4.2 — FDD filings

**Existing:** `sources/fdd/minnesota.py`, `sources/fdd/wisconsin.py`
**Gap:** Not called from `ResearchMarket`; industry mapping missing

**Modify:** `application/research_market.py`
- Query both FDD scrapers in parallel
- Map industry name → FDD category keywords
- Aggregate results into `market_overview.sources.fdd_filings`

### M4.3 — Reddit sentiment

**Goal:** Populate `pulse.opportunities`, `pulse.risks`, `pulse.business_model`, `pulse.sources.reddit_threads`

**Approach (V1 — AI-synthesized):**
1. Fetch Reddit threads via Reddit API or Pushshift for `"{industry} acquisition"`, `"buying {industry} business"`, `"{industry} owner"` queries
2. Pass thread titles + top comments to Claude
3. Claude extracts: opportunities, risks, operating models, key excerpts
4. Store in pulse dict

**Alternative (lower effort):** Pre-generate pulse data for the top 20 industries using Claude offline and cache it. Real-time Reddit is V2.

### M4.4 — Per-business financial estimates

Currently estimates use a simple benchmark multiplication:
`estimated_revenue ≈ reviews_count × revenue_per_review_constant`

For V1, improve this:
- Use BizBuySell median revenue for the industry as base
- Apply rating multiplier (higher rating → more revenue proxy)
- Apply review count as volume signal
- Return confidence: `high` (>200 reviews + BizBuySell data), `medium`, `low`

**Files:** New `application/estimate_financials.py` use case
**Effort for M4:** L (2+ days, data pipeline work) — likely separate PR per source

---

## Milestone 5 — Polish & Robustness
**Backlog items to ship before V1 is declared done.**

| ID | Task | Effort |
|---|---|---|
| U5 | Chat history scroll | S |
| U6 | Adaptive page size | S |
| F10 | Recent query history on splash | S |
| D2 | Typed MarketOverview/Pulse dataclasses | M |
| D3 | Benchmark deduplication | S |

---

## File Change Summary

| File | Change type | Milestone |
|---|---|---|
| `scout/ui/components.py` | Bug fixes, dead code removal, confidence badge, profile wiring | M0, M3 |
| `scout/ui/terminal.py` | State machine, filter state, assistant API, progress callbacks | M1, M2, M3 |
| `scout/ui/keyboard.py` | Esc → home, chat scroll bindings | M0, M2 |
| `scout/ui/splash.py` | New file — splash screen component | M1 |
| `scout/shared/history.py` | New file — recent query persistence | M1 |
| `scout/shared/mock_data.py` | Add `query` field | M0 |
| `scout/domain/models.py` | Add `query: str` to MarketSummary | M0 |
| `scout/main.py` | Entry point flow, splash integration | M1 |
| `scout/application/research_market.py` | Progress callbacks, BizBuySell + FDD integration | M1, M4 |
| `scout/application/estimate_financials.py` | New file — per-business estimate logic | M4 |
| `sources/marketplaces/bizbuysell.py` | Integration fixes | M4 |
| `sources/fdd/minnesota.py`, `wisconsin.py` | Industry mapping | M4 |

---

## Dependencies to Add

| Package | Purpose | Milestone |
|---|---|---|
| `anthropic` | Claude API client | M2 |
| `pyfiglet` | ASCII wordmark for splash | M1 |

---

## Success Criteria for V1

- [ ] `scout` (no args) opens splash screen with wordmark and thesis input
- [ ] Loading screen shows per-source progress during a real query
- [ ] Assistant answers at least 5 common question types with cited data
- [ ] Assistant filter command mutates the target list visibly
- [ ] Market overview shows real BizBuySell benchmarks for a live query
- [ ] Business detail panel shows financial estimates with confidence
- [ ] All V0 tests still pass + new tests for assistant and data pipeline
- [ ] Zero placeholder `...` responses visible in normal use

---

## Questions for Prioritization Review

1. **Splash screen vs. live data first?** The splash is high-visibility but the live data is the core value. Which lands harder in a demo?
We'll need both for V1
2. **Reddit sentiment — real-time vs. pre-generated?** Real-time adds complexity; pre-generated for top 20 industries gets 80% of the value.
The reddit sentiment should be an internet search when the user types int he query to identify the most relevant reddit threads just as if they were doing a google search themselves. 
3. **Assistant filter capability** — this is the "wow moment" feature. How complex does it need to be for V1? (Natural language → filter vs. preset filter templates?)
Doesn't need to be that complex, what we need is for the assistant to be able to talk to a live database and query it and answer qeustions for the user. 
4. **Which industries to support at launch?** Benchmarks and FDD data quality varies widely. HVAC, plumbing, auto repair, landscaping, and food service are the highest-signal industries for SMB acquisition. That's fine it should be a best effort based on the query
5. **Session persistence** — is the ability to re-open a previous search important enough for V1, or is fresh-query-every-time acceptable?
fresy query each time is fine.

---

*Ready for prioritization. See `research.md` for full gap inventory with effort estimates.*
