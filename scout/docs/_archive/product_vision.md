# Scout: Product Vision

**Product Vision:** Bloomberg Terminal for Small Business Acquisition
**Target User:** Hobby searchers and small PE firms evaluating SMB acquisitions
**Product Type:** Terminal-based intelligence platform

---

## The Vision

Scout transforms small business acquisition research from weeks of manual work into minutes of actionable intelligence. By aggregating data from Google Maps, Google Reviews, FDD filings, and Reddit, Scout provides searchers with the same level of market intelligence that Bloomberg provides to financial professionals.

### The Transformation

**Before Scout:**
- 11-20 hours of manual research per market
- Scattered Excel sheets across multiple tools
- Unclear which businesses to contact
- No benchmark data for decision-making

**After Scout:**
- 5 minutes to comprehensive intelligence
- Unified terminal interface
- Ranked target list with scores
- Clear next steps based on data

### Core Value Proposition

**Input:** A thesis ("HVAC businesses in Los Angeles")
**Output:** Ranked targets with financial benchmarks, quality scores, and market sentiment

---

## Target Experience

When a searcher types:
```bash
$ scout research "HVAC businesses in Los Angeles"
```

Scout provides:
1. **Universe** - All 487 HVAC businesses in the area
2. **Benchmarks** - Typical revenue ($1.2M), EBITDA (18%), multiples (3.5x)
3. **Scores** - Each business ranked 0-100 on acquisition attractiveness
4. **Intelligence** - Market sentiment from Reddit, quality signals from reviews
5. **Next Steps** - Top 20 targets to call with personalized outreach recommendations

---

## Core Capabilities (When Fully Built)

### 1. Market Intelligence
- Complete business universe (Google Maps)
- Financial benchmarks (FDD data, BizBuySell)
- Quality signals (reviews, ratings, trends)
- Competitive landscape mapping

### 2. Deal Scoring
- Quantitative scoring (0-100 scale)
- Retirement signals (owner age, business age)
- Strategic fit assessment
- Risk/opportunity identification

### 3. Sentiment Analysis
- Reddit operator insights
- Review sentiment trends
- Market timing indicators
- Industry-specific intelligence

### 4. Terminal Interface
- Bloomberg-style 4-screen layout
- Keyboard-driven navigation
- Real-time updates
- Export to CSV/CRM

---

## Success Metrics

### User Impact
- **Time savings:** 11-20 hours → 5 minutes per market
- **Decision quality:** Data-driven vs gut feel
- **Deal flow:** 3x more qualified targets identified

### Product Metrics
- **Response time:** <5 seconds for cached queries
- **Data coverage:** 90%+ of target markets
- **Accuracy:** ±20% on financial estimates

---

## Strategic Positioning

**Scout is not:**
- ❌ A CRM (use Pipedrive, HubSpot for that)
- ❌ A deal sourcing marketplace (not BizBuySell)
- ❌ A valuation tool (not a business appraiser)

**Scout is:**
- ✅ Intelligence layer (find and understand targets)
- ✅ Research automation (eliminate manual work)
- ✅ Decision support (score and rank opportunities)

---

## Competitive Landscape

### Enterprise Tools
- **Grata** ($50-150K/year) - Private company intelligence
- **Sourcescrub** (Enterprise) - M&A sourcing platform
- **Inven/Udu** (Enterprise) - AI-powered deal sourcing

**Scout's advantage:** Affordable (<$1K/year), purpose-built for micro PE

### DIY Approaches
- **Excel + Google** (Free) - Manual, slow, incomplete
- **Virtual assistants** ($5-20/hour) - Variable quality, not scalable

**Scout's advantage:** Automated, consistent, fast

---

## Phase Roadmap

See [roadmap.md](roadmap.md) for detailed phases and timeline.

**High-level progression:**
1. ✅ **Phase 0 (MVP):** Terminal UI + Google Maps search
2. 🔨 **Phase 1 (Intelligence):** Benchmarks + FDD data
3. 📋 **Phase 2 (Scoring):** Quantitative scoring engine
4. 🚀 **Phase 3 (Advanced):** Reddit sentiment + AI agent

---

## Target Users

### Primary: Solo Searchers
- Individual entrepreneurs acquiring their first business
- Need: Fast, affordable intelligence
- Budget: <$1K/year on tools

### Secondary: Small PE Firms
- 1-5 person teams evaluating deals
- Need: Consistent research process
- Budget: $5-20K/year on tools

### Tertiary: Search Funds
- Funded searchers with investor backing
- Need: Data-driven thesis validation
- Budget: $50K+ on tools (competitive with Grata)

---

## Why Now?

**Market Shifts:**
1. Baby boomers retiring (10K/day) → seller supply increasing
2. Remote work enabling location-independent acquisition
3. AI making data aggregation feasible at low cost
4. Google Maps API making business data accessible

**Technical Enablers:**
1. LLM APIs (Claude, GPT-4) for extraction and analysis
2. Terminal UI frameworks (Rich, Textual) for professional UX
3. Cloud databases (Supabase) for multi-device sync
4. Web scraping tools bypassing bot detection

---

## Long-term Vision (3-5 years)

**Scout becomes the operating system for small business acquisition:**
- Every searcher starts with Scout to find targets
- Industry benchmarks become standardized (via FDD aggregation)
- Deal flow quality improves (data beats cold calling)
- Acquisition market becomes more efficient

**Network effects:**
- More users → more data → better benchmarks
- Better benchmarks → better decisions → more success stories
- Success stories → more users (virtuous cycle)

---

_Last updated: 2026-02-19_
_Status: Vision document - see [architecture.md](architecture.md) for current implementation_
