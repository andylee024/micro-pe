# Scout: Product Roadmap

---

## ✅ Phase 0: MVP Terminal (Completed)

**Goal:** Prove the concept with minimal viable terminal interface

**Status:** ✅ Shipped

### Features Delivered
- [x] Terminal UI with Rich library
- [x] Google Maps integration
- [x] CSV export functionality
- [x] Basic keyboard navigation (↑↓, E, Q, H)
- [x] Query parser ("HVAC in Los Angeles" → industry, location)
- [x] 90-day result caching
- [x] Error handling and validation

### What Works
```bash
$ scout research "HVAC in Los Angeles"
# Returns table of businesses with name, phone, website
# Export to CSV with E key
```

### Metrics
- **Time to first result:** ~3-5 seconds
- **Data coverage:** Google Maps universe only
- **User workflow:** Search → view table → export CSV

### Limitations
- No financial benchmarking
- No scoring/ranking
- No multi-source data
- Simple table view only

**Duration:** 2 weeks
**Documentation:** See [feature/scout-v0/](feature/scout-v0/)

---

## 🔨 Phase 1: Intelligence Layer (Current)

**Goal:** Add financial benchmarks and multi-source intelligence

**Status:** 🔨 In Progress

### Features Planned

#### 1.1 BizBuySell Integration
- [ ] Scrape BizBuySell deals for industry benchmarks
- [ ] Extract revenue, cash flow, multiples
- [ ] Calculate benchmark distributions (median, quartiles)
- [ ] Apply benchmarks to Google Maps universe
- [ ] Display estimated values in terminal

**Feature workspace:** [feature/bizbuysell-scraper/](feature/bizbuysell-scraper/)

#### 1.2 FDD Database
- [ ] Scrape state FDD databases (Minnesota, Wisconsin, California)
- [ ] Extract Item 19 financial data
- [ ] Build franchise financial benchmarks
- [ ] Apply to franchise businesses in universe

**Feature workspace:** [feature/fdd-integration/](feature/fdd-integration/)

#### 1.3 Enhanced Terminal UI
- [ ] Add business detail view (press Enter on row)
- [ ] Show estimated financials in detail view
- [ ] Display benchmarks panel
- [ ] Add filtering/sorting (by rating, estimated revenue)

### Success Criteria
- Benchmarks available for 10+ industries
- Estimated revenue shown for 80%+ of businesses
- Confidence scores on estimates

**Estimated Duration:** 4-6 weeks
**Target Completion:** March 2026

---

## 📋 Phase 2: Scoring Engine (Next)

**Goal:** Rank businesses by acquisition attractiveness

**Status:** 📋 Planned

### Features

#### 2.1 Quantitative Scoring
- [ ] Define scoring model (0-100 scale)
- [ ] Implement signal gathering:
  - Business age (from reviews, website scraping)
  - Owner age estimates (LinkedIn, property records)
  - Review velocity trends (growing vs declining)
  - Property ownership (public records)
  - Revenue estimates (from benchmarks)
- [ ] Calculate composite scores
- [ ] Rank businesses by score

**Feature workspace:** [feature/scoring-engine/](feature/scoring-engine/)

#### 2.2 Terminal Enhancements
- [ ] Sort by score (default view)
- [ ] Show score badges in list (🟢 85+ 🟡 70-85 ⚪ <70)
- [ ] Score breakdown in detail view
- [ ] Export scored CSV

#### 2.3 Watchlist Management
- [ ] Add businesses to watchlist (W key)
- [ ] View watchlist (separate tab)
- [ ] Track outreach status (contacted, LOI, passed)
- [ ] Notes per business

### Success Criteria
- Scores correlate with actual acquisition success
- Top 20 scored businesses = high-quality targets
- User can build pipeline from scored list

**Estimated Duration:** 3-4 weeks
**Target Completion:** April 2026

---

## 🚀 Phase 3: Advanced Intelligence (Future)

**Goal:** Multi-source aggregation and sentiment analysis

**Status:** 🚀 Future

### Features

#### 3.1 Reddit Sentiment
- [ ] Scrape Reddit for industry discussions
- [ ] Extract operator sentiment
- [ ] Identify common problems/opportunities
- [ ] Display market pulse in terminal

**Feature workspace:** [feature/reddit-sentiment/](feature/reddit-sentiment/)

#### 3.2 Database Layer
- [ ] SQLite database for local storage
- [ ] Supabase sync for cloud backup
- [ ] Multi-device access
- [ ] Historical tracking (watch businesses over time)

**Feature workspace:** [feature/database-layer/](feature/database-layer/)

#### 3.3 4-Screen Bloomberg Layout
- [ ] Screen 1: Market overview
- [ ] Screen 2: Business list (scored)
- [ ] Screen 3: Business detail view
- [ ] Screen 4: Market pulse (Reddit, trends)
- [ ] Tab navigation between screens

#### 3.4 Enrichment Tools
- [ ] Website scraping for owner info
- [ ] LinkedIn search automation
- [ ] Property record lookup
- [ ] Licensing verification

### Success Criteria
- Complete market intelligence in <5 minutes
- 90%+ data coverage on scored businesses
- Users identify deals they wouldn't have found manually

**Estimated Duration:** 8-12 weeks
**Target Completion:** Q2-Q3 2026

---

## 🤖 Phase 4: AI Agent Layer (Vision)

**Goal:** Conversational AI-driven research assistant

**Status:** 🔮 Vision

### Features

#### 4.1 Natural Language Interface
- [ ] Replace CLI with conversational agent
- [ ] "Find all backflow testing companies in Texas" → Agent plans and executes
- [ ] Multi-turn conversations
- [ ] Agent suggests next steps

#### 4.2 Automated Workflows
- [ ] Weekly deal list generation
- [ ] Intelligence briefs (top 20 targets)
- [ ] Outreach recommendations
- [ ] Learning from feedback (response rates)

#### 4.3 Tool Calling Architecture
- [ ] Claude API integration
- [ ] Custom tools (universe-builder, scorer, enricher)
- [ ] Streaming progress updates
- [ ] Agent memory (remember preferences)

### Success Criteria
- Users prefer conversational interface over commands
- Agent autonomy: 80%+ of tasks require no clarification
- Response quality: 90%+ of suggestions are useful

**Estimated Duration:** 12+ weeks
**Target Completion:** Q4 2026+

---

## Timeline Overview

```
2026
├─ Q1 ───────────────────────────────────
│  ✅ Phase 0: MVP (Week 1-2)
│  🔨 Phase 1: Intelligence Layer (Week 3-8)
│
├─ Q2 ───────────────────────────────────
│  📋 Phase 2: Scoring Engine (Week 9-12)
│  🚀 Phase 3: Advanced Intelligence (Week 13-24)
│
├─ Q3 ───────────────────────────────────
│  🚀 Phase 3: Continued
│
└─ Q4+ ──────────────────────────────────
   🤖 Phase 4: AI Agent Layer (Future)
```

---

## Feature Priority Matrix

### Must Have (Core Value)
- ✅ Google Maps universe
- 🔨 Financial benchmarks
- 📋 Scoring/ranking
- 📋 CSV export (enhanced)

### Should Have (Significant Value)
- 🚀 Reddit sentiment
- 🚀 Database layer
- 🚀 Watchlist management
- 📋 Business detail views

### Nice to Have (Incremental Value)
- 🤖 AI agent interface
- 🚀 Property records
- 🚀 LinkedIn integration
- 🚀 4-screen layout

### Won't Have (Out of Scope)
- ❌ CRM features (use Pipedrive)
- ❌ Email outreach (use mail merge)
- ❌ Deal management (use spreadsheet)
- ❌ Valuation modeling (use Excel)

---

## Decision Framework

**When prioritizing features, ask:**

1. **Does it reduce research time?** (Core mission)
2. **Does it improve decision quality?** (Core value)
3. **Can users replicate it manually in <5 minutes?** (If yes, deprioritize)
4. **Does it require maintenance?** (Favor one-time builds)
5. **Is data reliable?** (Don't build on flaky data sources)

---

## Success Metrics by Phase

| Phase | Time to Intelligence | Data Sources | Decision Quality |
|-------|---------------------|--------------|-----------------|
| Phase 0 (MVP) | 5 min | 1 (Google Maps) | Low (no context) |
| Phase 1 (Intelligence) | 5 min | 3 (Maps, BizBuySell, FDD) | Medium (has benchmarks) |
| Phase 2 (Scoring) | 3 min | 3 + signals | High (ranked targets) |
| Phase 3 (Advanced) | 2 min | 5+ sources | Very High (complete picture) |
| Phase 4 (AI Agent) | <1 min | All sources | Exceptional (guided research) |

---

## How to Use This Roadmap

**For planning:**
- Check current phase status
- Review upcoming features
- Understand dependencies

**For feature work:**
- Navigate to feature workspace (e.g., `feature/scoring-engine/`)
- Read research.md (why we're building this)
- Read plan.md (how we'll build it)
- Track progress in feature-specific checklist

**For stakeholders:**
- See [product_vision.md](product_vision.md) for long-term vision
- See [architecture.md](architecture.md) for current technical state
- This document shows the path from current → vision

---

_Last updated: 2026-02-19_
_Current phase: Phase 1 (Intelligence Layer)_
