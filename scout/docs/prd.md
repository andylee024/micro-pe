# Scout: Product Requirements Document (PRD)

**Product Vision:** Bloomberg Terminal for Small Business Acquisition
**Target Users:** Solo searchers and small PE firms evaluating SMB acquisitions
**Product Type:** Terminal-based intelligence platform
**Last Updated:** 2026-02-21
**Status:** Active

---

## 1) Vision & Value

Scout transforms small business acquisition research from weeks of manual work into minutes of actionable intelligence. By aggregating data from Google Maps, Google Reviews, FDD filings, BizBuySell, and Reddit, Scout gives searchers Bloomberg‑like market intelligence tailored for SMB acquisition.

**Before Scout**
- 11–20 hours of manual research per market
- Scattered spreadsheets and ad‑hoc sources
- Unclear which businesses to contact
- No benchmark context for pricing or quality

**After Scout**
- 5 minutes to a ranked target list
- One terminal interface for all sources
- Clear benchmarks and confidence ranges
- Immediate next steps (who to call, why)

**Core Value Proposition**
Input a thesis (e.g., “HVAC businesses in Los Angeles”) → output a ranked list of targets with financial benchmarks, quality signals, and market sentiment.

---

## 2) Problem & User Jobs

**Pain Points**
1. Time to conviction is slow (weeks).
2. Data is fragmented across sources.
3. Manual copy/paste makes research error‑prone.
4. Financial benchmarks are hard to obtain.
5. No scalable way to evaluate multiple markets.

**Primary Jobs to Be Done**
- Determine whether a market is attractive.
- Identify the best 10–20 targets to contact.
- Understand expected pricing and margins.
- Gain market sentiment and operator context.

---

## 3) Target Experience

```bash
$ scout research "HVAC businesses in Los Angeles"
```

**Outcome:** A 4-pane terminal UI that answers three questions within minutes:
- Is this market attractive?
- Which businesses to contact first?
- What does the operator landscape actually look like?

### Layout: Two-Row Hierarchy

The UI is organized around a deliberate information hierarchy. The top row is **context** (read-only reference). The bottom row is **work** (interactive).

```
  SCOUT  hvac businesses  ·  los angeles, ca    47 targets  ·  B+  ·  live
  ┌──────────────────────────────────────────────┬─────────────────────────────────────────┐
  │ market overview                        B+    │ market pulse                 23 threads │
  │                                              │                                         │
  │  47 businesses  ·  high density              │  BUSINESS MODEL                         │
  │  est. $58M total market                      │    Customers: Residential + commercial  │
  │                                              │    Revenue: Recurring + one-off          │
  │  FINANCIALS  12 FDDs · medium                │                                         │
  │    Median revenue    $1.2M                   │  OPERATING MODELS                       │
  │    EBITDA margin     18%  (12–24%)           │    • Owner-operator (solo/crew)          │
  │    Typical acq.      $540K – $2.1M           │    • Multi-tech local operator           │
  │                                              │    • Commercial-leaning operator         │
  │  QUALITY                                     │    • Franchise / multi-location          │
  │    Avg rating   ★★★★☆  4.1                   │                                         │
  │    Sentiment    72% positive                 │  OPPORTUNITIES                          │
  │    Review vol   8,400 total                  │    ▲ Recurring contracts expand margins  │
  │                                              │    ▲ Fragmented market enables roll-up   │
  │  TRENDS  30d                                 │    ▲ Essential demand supports resilience│
  │    Job postings  ↑ 45                        │                                         │
  │    New entrants  3                           │  RISKS                                  │
  │    Search vol.   ↑ 12%                       │    ▼ Tech shortage limits scale         │
  │                                              │    ▼ Price pressure compresses margin    │
  │  OUTLOOK  Grade B+                           │    ▼ Best operators rarely sell          │
  │                                              │                                         │
  │                                              │  SOURCES                                │
  │                                              │    Reddit[15] · Reviews[420] · Reports[8]│
  └──────────────────────────────────────────────┴─────────────────────────────────────────┘
  ┌──────────────────────────────────────────────┬─────────────────────────────────────────┐
  │ target list                    1–8 of 47     │ scout assistant          claude sonnet  │
  │                                              │                                         │
  │  1  Cool Air HVAC                            │  ─ ─ ─ ─ ─ ─  feb 21  ─ ─ ─ ─ ─ ─ ─  │
  │     4.8★  350 reviews                        │                                         │
  │                                              │  you  Companies with 150+ reviews?      │
  │  2  Premier Climate Control                  │   ◆   3 match: Cool Air HVAC (350),     │
  │     4.6★  210 reviews                        │       SoCal Heating (180), Rapid (310). │
  │                                              │       [Enter] apply filter              │
  │ ▶3  SoCal Heating & Air                      │                                         │
  │     4.7★  180 reviews                        │  you  Summarize the key risks.          │
  │     (626) 555-0300  ·  socalheating.com      │   ◆   3 risks: tech shortage limits     │
  │     [W] website  ·  [R] reviews              │       scale, price pressure compresses  │
  │                                              │       margins, top operators rarely sell.│
  │  4  Valley Air Experts                       │                                         │
  │     4.5★   72 reviews                        │                                         │
  │                                              │  [/] > _           47 in scope · no filter│
  └──────────────────────────────────────────────┴─────────────────────────────────────────┘
  ↑↓/j/k  navigate    Enter  open    /  chat    E  export    H  help    Q  quit
```

### Pane Roles

| Pane | Row | Interactive | Purpose |
|---|---|---|---|
| **Market Overview** | Top-left | No | Financial benchmarks, quality metrics, trends, outlook grade |
| **Market Pulse** | Top-right | No | Business model, operating models, opportunities, risks, sources |
| **Target List** | Bottom-left | Yes — `↑↓`, `Enter` | Scrollable ranked business list; `Enter` expands contact detail |
| **Scout Assistant** | Bottom-right | Yes — `/` to type | Chat interface for querying the market; powered by Claude Sonnet |

**Design principle:** the top row informs, the bottom row acts. Market Overview and Market Pulse are read-only reference panels — you interact with their content through the Scout Assistant (`/`).

---

## 4) Product Principles

1. **Time to Conviction Over Perfection**
2. **Data Fusion Over Data Collection**
3. **Actionable Over Informative**
4. **Terminal‑First Design**
5. **Honest Uncertainty** (show confidence intervals)
6. **Incremental Value** (each milestone is useful)

---

## 5) Capabilities (Now → Next → Later)

**Now (V0) ✅**
- Google Maps universe building
- 4-pane terminal UI — market overview, market pulse, target list, scout assistant
- Keyboard navigation + CSV export
- Query parsing and 90-day caching
- Scout assistant chat interface (input scaffolding; AI backend in V1)

**Next (V1)**
- Live AI responses in scout assistant (Claude Sonnet)
- Benchmarks from BizBuySell and FDDs (financial estimates per business)
- Market pulse from real data sources (Reddit, reviews)
- Filter target list from assistant queries

**Later (V2+)**
- Scoring engine and ranked targets
- Watchlists + outreach workflow
- Multi‑source enrichment (owner info, licensing, property)

---

## 6) Roadmap (Phases)

### ✅ V0: Terminal UI (Completed — Feb 2026)
**Goal:** prove the terminal experience and establish the full UI shell.

**Shipped**
- 4-pane Bloomberg-style layout (market overview, market pulse, target list, scout assistant)
- Two-row hierarchy: context row (top) + work row (bottom)
- Google Maps universe building
- Keyboard navigation (`↑↓`, `j/k`, `Enter`, `gg/G`, `Esc`)
- CSV export
- Query parser + 90-day caching
- Scout assistant panel with chat input scaffolding (`/` to activate)

**Success Criteria**
- <5 seconds for cached queries ✅
- Reliable export and navigation ✅
- Full UI shell navigable with mock data ✅

---

### 🔨 V1: Intelligence Layer (Current)
**Goal:** make every pane live — real data, real assistant responses.

**Planned**
- Scout assistant: live Claude Sonnet responses via API
- Assistant can filter and sort the target list from natural language
- Market overview populated from real benchmarks (BizBuySell + FDDs)
- Market pulse from real sources (Reddit, reviews, reports)
- Per-business financial estimates with confidence ranges

**Success Criteria**
- Assistant answers market questions with cited sources
- Assistant can apply filters to target list ("show me 150+ reviews")
- Benchmarks available for 10+ industries
- Estimated revenue for 80%+ of businesses

---

### 📋 V2: Scoring & Workflow (Next)
**Goal:** rank businesses and support an outreach workflow.

**Planned**
- Composite acquisition score (0–100) per business
- Signals: review velocity, business age, margin vs benchmark
- Sort and filter by score
- Watchlist + outreach tracking

**Success Criteria**
- Top 20 scored businesses are consistently strong targets
- Users build a contact pipeline directly from the UI

---

### 🚀 V3: Enrichment (Future)
**Goal:** deeper intelligence per business.

**Planned**
- Owner signals (LinkedIn, property records, licensing)
- Secretary of State filings (age, registered agent)
- Google Street View / photos
- Proactive alerts (new listings, review spikes)

**Success Criteria**
- Full market intelligence in <5 minutes
- 90%+ coverage on enrichment fields for top targets

---

## 7) Success Metrics

**User Impact**
- Time savings: 11–20 hours → 5 minutes per market
- Decision quality: data‑driven target selection
- Deal flow: 3x more qualified targets

**Product Metrics**
- <5s response for cached queries
- 90%+ coverage of target markets
- ±20% accuracy on financial estimates

---

## 8) Non‑Goals

Scout is not:
- A CRM (use HubSpot/Pipedrive)
- A marketplace (not BizBuySell)
- A formal valuation tool (not an appraiser)

Scout is:
- An intelligence and decision support layer

---

## 9) Appendix

**Competitive Landscape**
- Grata, Sourcescrub (enterprise)
- DIY spreadsheets or VAs

**Why Now**
- Seller supply rising (retirements)
- Data access improving (APIs/scraping)
- Terminal UI toolkits are mature
