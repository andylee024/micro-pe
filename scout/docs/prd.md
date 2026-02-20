# Scout: Product Requirements Document (PRD)

**Product Vision:** Bloomberg Terminal for Small Business Acquisition
**Target Users:** Solo searchers and small PE firms evaluating SMB acquisitions
**Product Type:** Terminal-based intelligence platform
**Last Updated:** 2026-02-20
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

**Outcome:** terminal UI with a market overview, a ranked target list, a detail pane, and a market‑pulse pane. The user should know within minutes:
- Is this market attractive?
- Which businesses to call first?
- What price range is reasonable?

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

**Now (V0)**
- Google Maps universe building
- Terminal UI with list + export
- Query parsing and caching

**Next (V1)**
- Benchmarks from BizBuySell and FDDs
- Business detail view + financial estimates
- Market pulse signals (Reddit)

**Later (V2+)**
- Scoring engine
- Watchlists + workflow
- Multi‑source enrichment (web, property, licensing)

---

## 6) Roadmap (Phases)

### ✅ Phase 0: MVP Terminal (Completed)
**Goal:** prove the terminal experience for market research.

**Shipped**
- Terminal UI with Rich
- Google Maps integration
- CSV export
- Keyboard navigation
- Query parser
- 90‑day caching

**Success Criteria**
- <5 seconds for cached queries
- Reliable export and navigation

---

### 🔨 Phase 1: Intelligence Layer (Current)
**Goal:** add financial benchmarks and multi‑source intelligence.

**Planned**
- BizBuySell benchmarks (revenue, cash flow, multiples)
- FDD benchmarks (Item 19 extraction + aggregation)
- Detail view with estimated financials
- Benchmarks panel

**Success Criteria**
- Benchmarks available for 10+ industries
- Estimated revenue for 80%+ of businesses
- Confidence scores on estimates

---

### 📋 Phase 2: Scoring Engine (Next)
**Goal:** rank businesses by acquisition attractiveness.

**Planned**
- Composite scoring model (0–100)
- Signals: review velocity, business age, margin estimates
- Sort, filter, and export with score
- Watchlist + outreach workflow

**Success Criteria**
- Top 20 scored businesses are consistently strong targets
- Users can build a pipeline directly from the UI

---

### 🚀 Phase 3: Advanced Intelligence (Future)
**Goal:** richer market intelligence and enrichment.

**Planned**
- Reddit sentiment summaries
- Local database + sync
- Bloomberg‑style 4‑pane layout
- Enrichment tools (owner info, licensing, property)

**Success Criteria**
- Full market intelligence in <5 minutes
- 90%+ coverage on scored businesses

---

### 🤖 Phase 4: AI Agent Layer (Vision)
**Goal:** conversational research assistant.

**Planned**
- Natural language interface
- Automated workflows (weekly deal lists)
- Agent tool‑calling for multi‑step research

**Success Criteria**
- Multi‑turn research and synthesis
- Proactive insights and recommendations

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
