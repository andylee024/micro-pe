# Scout: Product Requirements Document

**Product Vision:** Bloomberg Terminal for Small Business Acquisition
**Target User:** Hobby searchers and small PE firms evaluating SMB acquisitions
**Product Type:** Terminal-based intelligence platform
**Created:** 2026-02-19

---

## Executive Summary

Scout transforms small business acquisition research from weeks of manual work into minutes of actionable intelligence. By aggregating data from Google Maps, Google Reviews, FDD filings, and Reddit, Scout provides searchers with the same level of market intelligence that Bloomberg provides to financial professionals.

**The Transformation:**
- **Before Scout:** 11-20 hours of manual research per market → scattered Excel sheets → unclear which businesses to call
- **After Scout:** 5 minutes to comprehensive intelligence → ranked target list → clear next steps

**Core Value:** Input a thesis ("HVAC businesses in Los Angeles") → Output ranked targets with financial benchmarks, quality scores, and market sentiment.

---

## The Problem

### Current Experience (Manual Research)

When a searcher wants to evaluate "HVAC businesses in Los Angeles," they must:

1. **Build Universe (4-8 hours)**
   - Google "HVAC businesses Los Angeles"
   - Manually copy 487 business names, phones, websites into Excel
   - Visit websites to understand each business
   - No way to know which are good targets

2. **Financial Benchmarking (2-4 hours)**
   - Navigate 10+ state FDD databases
   - Download 30+ PDFs manually
   - Extract Item 19 financial data by hand
   - Calculate median revenue, EBITDA margins

3. **Quality Assessment (2-3 hours)**
   - Look up each business on Google Maps
   - Read 50-100 reviews per business
   - Note ratings and themes
   - Identify high-quality businesses

4. **Market Intelligence (2-3 hours)**
   - Search Reddit for "HVAC business" discussions
   - Read 20+ threads about operator experiences
   - Synthesize sentiment and insights

5. **Target Prioritization (1-2 hours)**
   - Build spreadsheet combining all data
   - Create scoring system
   - Rank targets manually
   - Identify top 10 to call

**Total Time:** 11-20 hours per market
**Result:** Incomplete data, unclear priorities, stale by time it's finished

### The Pain Points

1. **Time to Conviction:** Weeks to go from thesis → "I should call these businesses"
2. **Scattered Data:** Information across 10+ sources, no single view
3. **Manual Process:** Copy/paste, spreadsheets, no automation
4. **Incomplete Picture:** Financial data without quality metrics, or vice versa
5. **Not Scalable:** Can't research 5 markets simultaneously
6. **No Benchmarking:** Hard to know if a business is typical or exceptional
7. **Blind Outreach:** Calling businesses without knowing if they're good targets

---

## The Vision: Final State

### The Scout Experience

A searcher evaluating "HVAC businesses in Los Angeles":

```bash
$ scout research "HVAC businesses in Los Angeles"
```

**2 minutes later**, Scout displays a 4-screen terminal interface:

```
┌─────────────────────────────────┬─────────────────────────────────┐
│ MARKET OVERVIEW                 │ TARGET LIST (487)               │
│                                 │                                 │
│ 487 businesses                  │ 1. Cool Air HVAC        92      │
│ Median: $1.2M, 18% EBITDA      │    (310) 555-0100               │
│ Typical acq: $540K - $2.1M     │    $1.5M | 4.8★ | Hiring        │
│ Grade: B+ (competitive)         │                                 │
│                                 │ 2. Premier Climate      88      │
│ Market density: High            │    (310) 555-0200               │
│ Quality: 4.1★ average           │    $1.2M | 4.6★ | Stable        │
│ Trend: ↑ 45 job openings        │                                 │
│                                 │ 3. SoCal Heating        85      │
│                                 │    (626) 555-0300               │
│                                 │    $980K | 4.7★ | Fast growing  │
├─────────────────────────────────┼─────────────────────────────────┤
│ BUSINESS PROFILE                │ MARKET PULSE                    │
│                                 │                                 │
│ Cool Air HVAC                   │ Reddit: Mixed 😐 (23 threads)  │
│ Los Angeles, CA                 │                                 │
│                                 │ "Maintenance contracts = higher │
│ Est. Revenue: $1.5M ±20%       │  multiple" - r/sweatystartup    │
│ EBITDA: $270K (18%)            │                                 │
│ Valuation: $675K - $810K       │ Key insight:                    │
│                                 │ "80% profit from 20% customers" │
│ Rating: 4.8★ (350 reviews)     │                                 │
│ Top themes:                     │ Trends (30d):                   │
│ • "reliable" (89 mentions)     │ ↑ Hiring up 15%                │
│ • "professional" (76)          │ ↑ Search volume +12%           │
│ • "fair pricing" (52)          │ → Review activity stable        │
│                                 │                                 │
│ Next steps:                     │ Red flags to avoid:             │
│ 1. Cold call (310) 555-0100    │ • 100% owner-operated           │
│ 2. Ask about maintenance       │ • No recurring revenue          │
│    contracts                    │ • Aging equipment               │
└─────────────────────────────────┴─────────────────────────────────┘
```

**Decision Made in 5 Minutes:**
1. This market is attractive (good margins, reasonable valuation)
2. There are 487 targets, 20+ are excellent (score >85)
3. Cool Air HVAC is the #1 target to call
4. Expect to pay $675K - $810K
5. Should ask about maintenance contracts during first call

**Next Action:** Export top 20 targets to CSV, start calling today.

**Time Saved:** 19 hours → 5 minutes (228x faster)

---

## Product Principles

1. **Time to Conviction Over Perfection**
   Every feature accelerates: "Should I pursue this market and which businesses should I call?"

2. **Data Fusion Over Data Collection**
   Value comes from connecting data sources: "Median revenue is $1.2M, this business is above average"

3. **Actionable Over Informative**
   Every screen suggests next action: "Call these top 10 first, here's why"

4. **Terminal-First Design**
   Bloomberg-style density and keyboard-driven efficiency

5. **Honest Uncertainty**
   Show confidence intervals: "Est. revenue: $1.5M ±20% (based on 12 comparable FDDs)"

6. **Incremental Value**
   Each milestone delivers immediate value to users

---

## Milestone Roadmap

### State 0: Current State (Today)

**What We Have:**
- ✅ Google Maps tool (working) - 500+ businesses per search
- ✅ BizBuySell tool (working) - listings data
- ✅ Minnesota FDD scraper (449 lines, 15% market coverage)
- ✅ Wisconsin FDD scraper (378 lines, 11% market coverage)
- ✅ Tool base class (caching, standardized API)

**What We Don't Have:**
- ❌ Any terminal UI
- ❌ Google Reviews integration
- ❌ Remaining FDD scrapers (California, NASAA FRED)
- ❌ FDD Aggregator
- ❌ Scoring engine
- ❌ Reddit scanner

**Current Capability:**
- Can search Google Maps for businesses
- Can scrape some FDD data manually
- No unified interface, no intelligence layer

---

### V0: Terminal Universe Builder (Week 1-2)

**Goal:** Bring the product to life with a terminal UI from day 1

**What the UI Looks Like:**

```bash
$ scout research "HVAC businesses in Los Angeles"
```

**Terminal launches with live Rich display:**

```
┌──────────────────────────────────────────────────────────────────┐
│ SCOUT - Market Research                                          │
│ Query: HVAC businesses in Los Angeles                            │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│ 📊 Building universe...                                          │
│    ✓ Searching Google Maps                                       │
│    ✓ Found 487 HVAC businesses in Los Angeles area              │
│                                                                  │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│                                                                  │
│ 📋 HVAC Businesses in Los Angeles                  487 results  │
│                                                                  │
│  Name                     Phone             Website              │
│  ────────────────────────────────────────────────────────────────│
│  Cool Air HVAC           (310) 555-0100    coolair.com          │
│  Premier Climate         (310) 555-0200    premierclimate.com   │
│  SoCal Heating & Air     (626) 555-0300    socalheating.com     │
│  Valley Air Experts      (818) 555-0400    valleyairexperts.com ║
│  West Coast Climate      (424) 555-0500    westcoastclimate.com │
│  Air Masters Inc         (213) 555-0600    airmastersinc.com    │
│  Quick Cool HVAC         (310) 555-0700    quickcool.com        │
│  Elite Climate Control   (626) 555-0800    eliteclimate.com     │
│  Pro Air Services        (818) 555-0900    proairservices.com   │
│  Golden State HVAC       (424) 555-1000    goldenstateHVAC.com  │
│  ...                                                             │
│                                                                  │
│  Showing 20 of 487 businesses                                    │
│  [↑↓] Scroll  [E]xport CSV  [Q]uit  [H]elp                      │
│                                                                  │
├──────────────────────────────────────────────────────────────────┤
│ Status: Ready • 487 businesses found • Cached for 90 days       │
└──────────────────────────────────────────────────────────────────┘
```

**When user presses 'E' to export:**

```
✅ Exported to: outputs/hvac_los_angeles_2026-02-19.csv
   Columns: name, address, phone, website, category
   Rows: 487 businesses

📂 File location: /Users/you/scout/outputs/hvac_los_angeles_2026-02-19.csv
```

**Data Sources:**
- ✅ Google Maps API (business listings, contact info)

**Capabilities:**
- Natural language search parsing ("HVAC businesses in Los Angeles")
- Google Maps integration (find 500+ businesses)
- **Rich terminal UI** - live, interactive display (not just print-and-exit)
- **Scrollable table** - navigate through all 487 businesses with arrow keys
- **Keyboard shortcuts** - [E]xport, [Q]uit, [H]elp
- **Status bar** - shows cache status, result count
- CSV export with contact info
- 90-day caching (repeated searches are instant)

**Technical Stack:**
- **Rich library** - Terminal UI framework (tables, panels, live display)
- **Click** - CLI argument parsing
- **Google Maps tool** - Already working from existing code
- **Simple architecture** - Single-screen, scrollable table

**Value Delivered:**
- **Product comes to life** - terminal UI from day 1 (not just CLI)
- **Saves 6 hours** of manual Google searching and copy/pasting
- **Professional feel** - Bloomberg-style terminal interface (simple version)
- **Complete universe** - no businesses missed
- **Foundation** for adding screens and intelligence

**User Feedback Loop:**
- Share with teammates acquiring businesses
- Ask: "Does the terminal feel good? Does this save you time?"
- Validate: Is scrolling through 487 businesses useful?
- Learn: Should we add filtering? Sorting?

---

### V1: Financial Intelligence (Week 3-5)

**Goal:** Add financial context - "What should I expect to pay and earn?"

**What the UI Looks Like:**

```bash
$ scout research "HVAC businesses in Los Angeles"
```

**Terminal launches with enhanced UI:**

```
┌──────────────────────────────────────────────────────────────────┐
│ SCOUT - Market Research                                          │
│ Query: HVAC businesses in Los Angeles                            │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│ 📊 Building universe...                                          │
│    ✓ Searching Google Maps                                       │
│    ✓ Found 487 HVAC businesses                                   │
│                                                                  │
│ 💰 Gathering financial benchmarks...                             │
│    ✓ Searching Minnesota FDD database                            │
│    ✓ Searching Wisconsin FDD database                            │
│    ✓ Searching California FDD database                           │
│    ✓ Searching NASAA FRED (7 states)                            │
│    ✓ Found 45 HVAC-related FDD filings                           │
│    ✓ Analyzed Item 19 from 12 comparable franchises             │
│                                                                  │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│                                                                  │
│ 📊 MARKET OVERVIEW                                               │
│                                                                  │
│ Market Size:        487 businesses                               │
│ Est. Market Value:  $584M total revenue                          │
│                                                                  │
│ 💰 FINANCIAL BENCHMARKS (from 12 comparable FDD filings)         │
│ Median Revenue:     $1.2M  (Range: $400K - $3.5M)               │
│ EBITDA Margin:      18%    (Range: 12% - 24%)                   │
│ Valuation Multiple: 2.5x EBITDA (industry standard)             │
│ Typical Acquisition: $540K - $2.1M                               │
│                                                                  │
│ Confidence: Medium (12 FDDs, 90%+ market coverage)               │
│                                                                  │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│                                                                  │
│ 📋 BUSINESSES (487 results)                                      │
│                                                                  │
│  Name                  Est.Revenue  Phone          Website       │
│  ────────────────────────────────────────────────────────────────│
│  Cool Air HVAC         $1.5M ±20%  (310) 555-0100 coolair.com   │
│                        ↑ Above median                            │
│  Premier Climate       $1.2M ±25%  (310) 555-0200 premier...    │
│                        → At median                               │
│  SoCal Heating         $980K ±25%  (626) 555-0300 socal...      │
│                        ↓ Below median                            │
│  Valley Air            $1.1M ±20%  (818) 555-0400 valley...     │
│                        → At median                               │
│  West Coast Climate    $890K ±25%  (424) 555-0500 westcoast...  │
│                        ↓ Below median                            │
│  ...                                                             │
│                                                                  │
│  [↑↓] Scroll  [F]ilter by revenue  [E]xport  [Q]uit  [H]elp     │
│                                                                  │
├──────────────────────────────────────────────────────────────────┤
│ Status: Ready • 487 businesses • Financial data: 12 FDDs         │
└──────────────────────────────────────────────────────────────────┘
```

**Data Sources:**
- ✅ Google Maps API (business listings)
- ✅ Minnesota FDD scraper (15% coverage) - already exists
- ✅ Wisconsin FDD scraper (11% coverage) - already exists
- ✅ California FDD scraper (30% coverage) - NEW
- ✅ NASAA FRED scraper (46% coverage, 7 states) - NEW
- ✅ FDD Aggregator (unified interface) - NEW

**Capabilities:**
- All capabilities from V0, plus:
- **Enhanced terminal UI** - Market overview panel above business list
- **Live progress** - Shows FDD scraping progress in real-time
- Complete FDD scraper infrastructure (4 scrapers, 10 states)
- FDD Aggregator (query all databases simultaneously)
- Financial benchmark calculation (median, P25, P75)
- Revenue estimation per business (using review volume, years in business as proxies)
- Confidence intervals (±20% typical, ±40% if few comparables)
- **Visual indicators** - ↑ Above median, → At median, ↓ Below median
- **Filter capability** - [F] to filter by revenue range

**Value Delivered:**
- **Saves 12 hours total** (6h universe + 6h financial research)
- **Financial context** - know what to expect before calling
- **Valuation estimates** - prepare for price negotiations
- **Prioritization** - focus on above-median businesses
- **Confidence** - backed by regulatory FDD data (not guesses)

**User Feedback Loop:**
- Share with teammates
- Ask: "Do financial estimates help you prioritize? Are confidence intervals clear?"
- Validate: Are valuations close to reality (±30%)?

---

### V2: Quality Ranking (Week 6-8)

**Goal:** Add quality intelligence - "Which businesses are actually good?"

**What the UI Looks Like:**

```bash
$ scout research "HVAC businesses in Los Angeles"

📊 Building universe...
   ✓ Found 487 HVAC businesses in Los Angeles area

💰 Gathering financial benchmarks...
   ✓ Found 45 FDD filings across 4 state databases
   ✓ Median revenue: $1.2M | EBITDA margin: 18%

⭐ Analyzing reviews...
   ✓ Fetched reviews for 487 businesses
   ✓ Analyzed 52,000+ customer reviews
   ✓ Average rating: 4.1★ (range: 2.8★ - 5.0★)

🎯 Calculating acquisition scores...
   ✓ Scored 487 businesses on quality, financials, and growth signals

╔══════════════════════════════════════════════════════════════════╗
║  MARKET OVERVIEW - HVAC Services in Los Angeles                 ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  📊 MARKET SIZE                                                  ║
║  Total Businesses:        487                                    ║
║  Market Density:          High (3.2 per sq mi)                   ║
║  Competitive Index:       8.2/10 ████████░░                      ║
║                                                                  ║
║  💰 FINANCIAL BENCHMARKS                                         ║
║  Median Revenue:          $1.2M  (Range: $400K - $3.5M)         ║
║  EBITDA Margin:           18%    (Range: 12% - 24%)             ║
║  Typical Acquisition:     $540K - $2.1M                          ║
║                                                                  ║
║  ⭐ QUALITY METRICS                                              ║
║  Avg Rating:              4.1 ★★★★☆                             ║
║  Review Volume:           High (avg 108 reviews/business)        ║
║  Sentiment:               72% Positive, 18% Neutral, 10% Neg    ║
║                                                                  ║
║  🎯 ACQUISITION OUTLOOK                                          ║
║  Overall Rating:          B+ (Good opportunity, competitive)     ║
╚══════════════════════════════════════════════════════════════════╝

╔══════════════════════════════════════════════════════════════════╗
║  TARGET LIST - Top Acquisition Targets           487 businesses ║
╠══════════════════════════════════════════════════════════════════╣
║  Sorted by: Acquisition Score (0-100)                            ║
║                                                                  ║
║  Rank  Name                    Score  Revenue  Rating  Signals  ║
║  ───────────────────────────────────────────────────────────────║
║  1     Cool Air HVAC             92   $1.5M    4.8★   🟢🟢🟢   ║
║        Los Angeles, CA                ±20%     (350)            ║
║        📞 (310) 555-0100  🌐 coolair.com                        ║
║        → Established 15yr | Hiring | Top reviews                ║
║                                                                  ║
║  2     Premier Climate Control   88   $1.2M    4.6★   🟢🟢🟡   ║
║        Santa Monica, CA               ±20%     (220)            ║
║        📞 (310) 555-0200  🌐 premierclimate.com                 ║
║        → Strong margins | Commercial focus                      ║
║                                                                  ║
║  3     SoCal Heating & Air       85   $980K    4.7★   🟢🟢🟢   ║
║        Pasadena, CA                   ±25%     (180)            ║
║        📞 (626) 555-0300  🌐 socalheating.com                   ║
║        → Fast growing | Low overhead                            ║
║                                                                  ║
║  4     Valley Air Experts        82   $1.1M    4.5★   🟢🟡🟡   ║
║        Van Nuys, CA                   ±20%     (150)            ║
║        📞 (818) 555-0400  🌐 valleyairexperts.com               ║
║        → Owner retiring (signal!) | Residential focus           ║
║                                                                  ║
║  ...                                                             ║
║                                                                  ║
║  Showing 20 of 487 businesses                                    ║
║  [↑↓] More  [E]xport CSV  [H]elp                                ║
╚══════════════════════════════════════════════════════════════════╝

✅ Exported to: outputs/hvac_los_angeles.csv
   Columns: rank, name, score, est_revenue, rating, reviews, phone, website, signals

Next steps:
1. Call top 10 businesses (score ≥85) this week
2. Cool Air HVAC (#1) - mention their excellent reviews in outreach
3. Valley Air Experts (#4) - owner retiring is a buy signal, prioritize
4. Focus on businesses with 🟢🟢🟢 signals (high growth/quality)

Time saved: ~15 hours (universe + financials + quality research)
```

**Data Sources:**
- ✅ Google Maps API
- ✅ FDD Aggregator (4 scrapers, 90%+ coverage)
- ✅ Google Reviews API (rating, review text, review count) - NEW

**Capabilities:**
- All capabilities from V1, plus:
- Google Reviews integration (fetch reviews for each business)
- Sentiment analysis (extract positive/negative themes from reviews)
- Growth signals (hiring indicators, review recency, owner engagement)
- Acquisition scoring engine (0-100 score combining quality + financials + signals)
- Ranked target list (best opportunities first)
- Visual signals (🟢🟡🔴 indicators for growth, stability, decline)
- Action signals ("Owner retiring", "Hiring", "Fast growing")
- Enhanced market overview (quality metrics, acquisition outlook)

**Scoring Algorithm:**
```
Score = Quality (40%) + Financials (30%) + Signals (20%) + Fit (10%)

Quality:    Rating, review volume, sentiment, response rate
Financials: Est. revenue vs median, margin strength
Signals:    Hiring, recent activity, online presence
Fit:        Business age, location, ownership structure
```

**Value Delivered:**
- **Saves 15 hours total** (universe + financials + quality research)
- **Clear prioritization** - call top 10 first (score ≥85)
- **Confidence in targets** - backed by 350 reviews, not gut feel
- **Action signals** - "Owner retiring" = opportunity
- **Ready for outreach** - phone numbers right there, know why each is ranked

**User Feedback Loop:**
- Share with teammates
- Ask: "Does ranking help you focus outreach? Are top 10 actually better?"
- Validate: Do high-score businesses convert to deals more often?

---

### V3: Multi-Screen Terminal (Week 9-11)

**Goal:** Deliver the full vision - Bloomberg-style 4-screen interface

**What the UI Looks Like:**

```
┌─────────────────────────────────┬─────────────────────────────────┐
│ SCOUT - MARKET OVERVIEW         │ SCOUT - TARGET LIST             │
│                    Updated: 2m  │                    487 businesses│
├─────────────────────────────────┼─────────────────────────────────┤
│ Current Market:                 │ Showing: Top 20 by Acq. Score   │
│ HVAC Services — Los Angeles, CA │ Sort: [Score] Rev Rating        │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│                                 │                                 │
│ 📊 MARKET SIZE                  │ #  Business           Score Rev │
│ ├─ Total: 487 businesses       │ ───────────────────────────────│
│ ├─ Density: High (3.2/sq mi)   │ 1  Cool Air HVAC       92  $1.5M│
│ ├─ Competitive: 8.2/10 ████████│    Los Angeles, CA     4.8★     │
│ └─ Est. Value: $584M           │    (310) 555-0100               │
│                                 │    → Established | Hiring       │
│ 💰 FINANCIAL BENCHMARKS         │                                 │
│ ├─ Median Revenue: $1.2M       │ 2  Premier Climate     88  $1.2M│
│ │   (Range: $400K - $3.5M)     │    Santa Monica, CA    4.6★     │
│ ├─ EBITDA Margin: 18%          │    (310) 555-0200               │
│ │   (Range: 12% - 24%)         │    → Strong margins             │
│ ├─ Valuation: 2.5x EBITDA      │                                 │
│ └─ Typical Acq: $540K - $2.1M  │ 3  SoCal Heating       85  $980K│
│                                 │    Pasadena, CA        4.7★     │
│ ⭐ QUALITY METRICS              │    (626) 555-0300               │
│ ├─ Avg Rating: 4.1 ★★★★☆       │    → Fast growing               │
│ ├─ Review Vol: High (108/biz)  │                                 │
│ ├─ Sentiment: 72% Positive     │ 4  Valley Air          82  $1.1M│
│ └─ Top Issue: "Pricing"        │    Van Nuys, CA        4.5★     │
│                                 │    (818) 555-0400               │
│ 📈 MARKET TRENDS (30 days)      │    → Owner retiring!            │
│ ├─ New Entrants: ↑ 3           │                                 │
│ ├─ Job Postings: ↑ 45 (growth) │ 5  West Coast          80  $890K│
│ ├─ Reddit Mentions: ↑ 23       │    Culver City, CA     4.6★     │
│ └─ Search Vol: ↑ 12%           │    (424) 555-0500               │
│                                 │    → Good reviews               │
│ 🎯 ACQUISITION OUTLOOK          │                                 │
│ ├─ Entry: Medium ████░░         │ ...                             │
│ ├─ Competition: High ████████   │                                 │
│ ├─ Margins: Good ██████░        │ [↑↓] Navigate  [Enter] Analyze │
│ └─ Rating: B+ (Good, compet.)  │ [F]ilter  [E]xport  [H]elp     │
│                                 │                                 │
│ [R]efresh [C]hange [E]xport [H] │                                 │
├─────────────────────────────────┼─────────────────────────────────┤
│ SCOUT - BUSINESS PROFILE        │ SCOUT - MARKET PULSE            │
│                                 │                   Last scan: 1h │
├─────────────────────────────────┼─────────────────────────────────┤
│ Select a business from Target   │ Market: HVAC Services —         │
│ List to view detailed profile   │ Los Angeles, CA                 │
│                                 │ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│ [Press Enter on any business]   │                                 │
│                                 │ 💬 REDDIT SENTIMENT             │
│                                 │ (23 threads, 180 comments/30d)  │
│                                 │                                 │
│                                 │ Overall: Mixed 😐               │
│                                 │ 52% Positive, 28% Neutral       │
│                                 │                                 │
│                                 │ Top Discussion:                 │
│                                 │ "Is HVAC worth buying in 2026?" │
│                                 │ r/sweatystartup • 45↑ • 28💬   │
│                                 │                                 │
│                                 │ Key points:                     │
│                                 │ ✓ Recession-resistant service   │
│                                 │ ✓ Good margins (15-25% EBITDA)  │
│                                 │ ⚠ High competition in cities    │
│                                 │ ⚠ Labor costs increasing        │
│                                 │                                 │
│                                 │ 📊 MARKET TRENDS (30d)          │
│                                 │ Job Postings:  ↑ 45 (+15%)     │
│                                 │ New Entrants:  3 businesses     │
│                                 │ Search Volume: ↑ 12%            │
│                                 │                                 │
│                                 │ 🎓 OPERATOR INSIGHTS            │
│                                 │ "Maintenance contracts = higher │
│                                 │  multiple" - Successful exit    │
│                                 │                                 │
│                                 │ "80% profit from 20% customers" │
│                                 │ - Focus on retention            │
│                                 │                                 │
│                                 │ ⚡ ACTIONABLE INSIGHTS          │
│                                 │ When evaluating HVAC:           │
│                                 │ 1. ✓ Recurring contracts (40%+) │
│                                 │ 2. ✓ Modern systems (CRM)       │
│                                 │ 3. ✓ Trained technicians        │
│                                 │                                 │
│                                 │ Red flags:                      │
│                                 │ 1. ✗ 100% owner-operated        │
│                                 │ 2. ✗ No recurring revenue       │
│                                 │ 3. ✗ Aging equipment            │
│                                 │                                 │
│ [B]ack [E]xport [N]otes [H]elp  │ [R]efresh [D]eep Dive [E]xport │
└─────────────────────────────────┴─────────────────────────────────┘
```

**When user presses Enter on "Cool Air HVAC" in Screen 2:**

```
┌─────────────────────────────────┬─────────────────────────────────┐
│ SCOUT - MARKET OVERVIEW         │ SCOUT - TARGET LIST             │
│                    Updated: 2m  │                    487 businesses│
├─────────────────────────────────┼─────────────────────────────────┤
│ (Same content as above)         │ #  Business           Score Rev │
│                                 │ ───────────────────────────────│
│                                 │ ►1 Cool Air HVAC       92  $1.5M│
│                                 │    Los Angeles, CA     4.8★     │
│                                 │    (310) 555-0100               │
│                                 │    → Established | Hiring       │
│                                 │                                 │
│                                 │  2  Premier Climate    88  $1.2M│
│                                 │     Santa Monica, CA   4.6★     │
│                                 │                                 │
│                                 │  3  SoCal Heating      85  $980K│
│                                 │     Pasadena, CA       4.7★     │
│                                 │                                 │
│                                 │ ...                             │
├─────────────────────────────────┼─────────────────────────────────┤
│ SCOUT - BUSINESS PROFILE        │ SCOUT - MARKET PULSE            │
│                  Acq. Score: 92 │                   Last scan: 1h │
├─────────────────────────────────┼─────────────────────────────────┤
│ Cool Air HVAC Services          │ (Same content as above)         │
│ Los Angeles, CA                 │                                 │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │                                 │
│                                 │                                 │
│ 📍 LOCATION & CONTACT           │                                 │
│ Address: 1234 Wilshire Blvd    │                                 │
│          Los Angeles, CA 90010  │                                 │
│ Phone:   (310) 555-0100        │                                 │
│ Website: www.coolair.com       │                                 │
│ Est.:    2009 (15 years)       │                                 │
│ Service: 25-mile radius        │                                 │
│                                 │                                 │
│ 💰 FINANCIAL PROFILE            │                                 │
│ Revenue:  $1.5M ±20%           │                                 │
│           (vs median $1.2M)    │                                 │
│           ↑ Above average      │                                 │
│                                 │                                 │
│ EBITDA:   $270K (18% margin)   │                                 │
│           (vs median 18%)      │                                 │
│           → At benchmark       │                                 │
│                                 │                                 │
│ Valuation: $675K - $810K       │                                 │
│            (2.5x EBITDA)       │                                 │
│ Confidence: Medium (12 FDDs)   │                                 │
│                                 │                                 │
│ ⭐ CUSTOMER SENTIMENT            │                                 │
│ Overall: 4.8 ★★★★★ (Top 5%)    │                                 │
│ Reviews: 350 total             │                                 │
│                                 │                                 │
│ Distribution:                   │                                 │
│ 5★ ████████████████ 68%        │                                 │
│ 4★ ████████ 22%                │                                 │
│ 3★ ██ 6%                       │                                 │
│ 2★ ░ 3%                        │                                 │
│ 1★ ░ 1%                        │                                 │
│                                 │                                 │
│ Positive Themes:                │                                 │
│ • "reliable" (89 mentions)     │                                 │
│ • "professional" (76)          │                                 │
│ • "fast response" (64)         │                                 │
│ • "fair pricing" (52)          │                                 │
│                                 │                                 │
│ Negative (rare):                │                                 │
│ • "scheduling delays" (8)      │                                 │
│                                 │                                 │
│ 📈 GROWTH SIGNALS               │                                 │
│ ├─ Jobs: 2 open positions      │                                 │
│ ├─ Activity: 95% review resp.  │                                 │
│ ├─ Online: Modern website      │                                 │
│ └─ Equipment: Newer fleet (3)  │                                 │
│                                 │                                 │
│ 🎯 ACQUISITION ASSESSMENT       │                                 │
│ Strengths:                      │                                 │
│ ✓ Top-tier reputation (4.8★)   │                                 │
│ ✓ Strong margins (18% EBITDA)  │                                 │
│ ✓ Growth signals (hiring)      │                                 │
│ ✓ Established (15 years)       │                                 │
│                                 │                                 │
│ Considerations:                 │                                 │
│ ⚠ Competitive market (487)     │                                 │
│ ⚠ Owner involvement unclear    │                                 │
│                                 │                                 │
│ Next Steps:                     │                                 │
│ 1. Cold call (310) 555-0100    │                                 │
│ 2. Request financials (P&L)    │                                 │
│ 3. Ask about maintenance mix   │                                 │
│ 4. Evaluate owner's interest   │                                 │
│                                 │                                 │
│ [B]ack [→]Next [E]xport [N]otes│                                 │
└─────────────────────────────────┴─────────────────────────────────┘
```

**Data Sources:**
- ✅ Google Maps API
- ✅ FDD Aggregator (4 scrapers)
- ✅ Google Reviews API
- ✅ Reddit API (PRAW) - NEW
- ✅ Job Boards (Indeed/LinkedIn scraping) - NEW

**Capabilities:**
- All capabilities from V2, plus:
- Textual framework (full TUI with 4-panel layout)
- Keyboard navigation (arrow keys, Enter, shortcuts)
- Real-time screen updates
- Screen 3: Business Profile (deep dive on selected target)
- Screen 4: Market Pulse (Reddit sentiment, operator insights)
- Reddit integration (scan relevant subreddits, sentiment analysis)
- Job board integration (hiring trends, growth signals)
- Multi-panel simultaneous view (all context visible)
- Smooth transitions between screens

**Value Delivered:**
- **Complete intelligence** - all data in one view
- **Context always visible** - market overview + target list + details + sentiment
- **Professional workflow** - Bloomberg-style keyboard navigation
- **Operator intelligence** - learn from others who've done this ("maintenance contracts = higher multiple")
- **Market trends** - understand if market is growing or declining
- **Actionable insights** - specific green flags and red flags to look for
- **Time saved: 19+ hours** (complete research in 5 minutes)

**User Feedback Loop:**
- Share with teammates and broader community
- Ask: "Does 4-screen layout help or overwhelm? Is Reddit intelligence valuable?"
- Validate: Do users close deals faster with Scout?

---

### V4: Polish & Scale (Week 12+)

**Goal:** Production-ready for public release

**Additional Capabilities:**
- Contact tracking (log calls, emails, meeting notes)
- Deal pipeline (track businesses through stages)
- Historical data (track market changes over time)
- Alerts (notify when new businesses appear)
- Team collaboration (share research with partners)
- Performance optimizations (faster data fetching)
- Error recovery (graceful degradation if data source unavailable)
- Documentation (user guide, video tutorials)
- Community (Discord, GitHub discussions)

**Value Delivered:**
- Production-ready tool for public use
- Support for teams (not just individuals)
- Long-term tracking (not just point-in-time)
- Community building (searchers helping searchers)

---

## Value Summary by Milestone

### V0: Terminal Universe Builder
- **Time Saved:** 6 hours → 10 minutes
- **Value:** "I have a complete list of businesses to call"
- **Wow Factor:** "This looks like a real product! And it saved me hours of Googling"
- **Product Feel:** Terminal UI from day 1 - product feels alive, not just a script

### V1: Financial Intelligence
- **Time Saved:** 12 hours → 10 minutes
- **Value:** "I know what revenue to expect and what price to pay"
- **Wow Factor:** "This is backed by regulatory data, not guesses"

### V2: Quality Ranking
- **Time Saved:** 15 hours → 10 minutes
- **Value:** "I know which businesses to call first"
- **Wow Factor:** "The scoring really helps me prioritize"

### V3: Multi-Screen Terminal
- **Time Saved:** 19 hours → 5 minutes
- **Value:** "I have complete intelligence to make a decision"
- **Wow Factor:** "This feels like Bloomberg for SMB acquisition"

---

## Success Metrics

### User Metrics
- **Adoption:** 10 teammates using by V1 → 100 users by V3
- **Engagement:** 3 markets researched per user per month
- **Retention:** 60% monthly active users

### Product Metrics
- **Search Success Rate:** >80% (businesses found)
- **Data Coverage:** >90% industries have FDD benchmarks
- **Performance:** <2 min uncached, <10 sec cached

### Business Metrics
- **Time Savings:** 15+ hours per market
- **Deals Sourced:** 5+ deals per user per year
- **User Satisfaction:** 8/10+ NPS score

---

## User Journey

### Discovery (Teammate Referral)
- Teammate: "I used Scout to research HVAC in LA, saved me 15 hours"
- User: "Show me"
- Teammate: Demos Scout terminal, exports CSV
- User: "I need this for my search"

### First Use (MVP)
- User: Installs Scout, runs first search
- Output: 500+ businesses in beautiful table, CSV export
- Reaction: "Wow, this actually works"

### Habit Formation (V1 → V2)
- User: Researches 5 markets in one afternoon
- Output: Financial benchmarks + ranked targets for each
- Reaction: "I can't go back to manual research"

### Advocacy (V3)
- User: Shows Scout to other searchers
- Output: Full 4-screen Bloomberg-style interface
- Reaction: "How did you build this?" → Community growth

---

## Open Questions

### Product
1. Should MVP be CLI-only or simple single-screen TUI?
2. Is 4-screen layout the right final state, or 2-3 screens better?
3. Should we add CRM features or stay focused on intelligence?

### Data
1. Google Reviews access - use official API (limited) or Outscraper (paid)?
2. Reddit API - will we get approval for API access?
3. Job boards - scrape or use official APIs?

### Go-to-Market
1. When to open source (MVP, V1, or V3)?
2. Pricing model (free, freemium, paid)?
3. Target market (hobby searchers or expand to search funds)?

---

## Next Steps

1. **Validate MVP scope** with teammates
   - Show wireframe, ask: "Would this save you time?"
   - Get commitment: "I'll use this if you build it"

2. **Build MVP (Week 1-2)**
   - Google Maps integration
   - Rich terminal output
   - CSV export
   - Ship to teammates

3. **Gather feedback**
   - What's working? What's missing?
   - Is universe building valuable?
   - Should we add financials next?

4. **Build V1 (Week 3-5)**
   - Complete FDD infrastructure
   - Financial benchmarks
   - Revenue estimation
   - Ship to teammates

5. **Iterate toward V3**
   - Add reviews + scoring (V2)
   - Add multi-screen UI (V3)
   - Gather feedback at each step

---

## Appendix: Why This Roadmap Works

### Incremental Value
Every milestone delivers standalone value:
- MVP solves universe building (6 hours saved)
- V1 adds financial context (12 hours saved)
- V2 adds prioritization (15 hours saved)
- V3 adds complete intelligence (19 hours saved)

### Momentum Building
- **Week 1:** Show MVP to teammates → "This is useful!"
- **Week 3:** Show V1 to teammates → "This is amazing!"
- **Week 6:** Show V2 to teammates → "I can't live without this"
- **Week 9:** Show V3 to world → "We need to open source this"

### Learning at Each Step
- MVP: Do users find 500+ businesses valuable or overwhelming?
- V1: Are financial estimates accurate enough (±30%)?
- V2: Does scoring help prioritize, or is it noise?
- V3: Is 4-screen layout powerful or confusing?

### Risk Mitigation
- If MVP doesn't resonate → stop, don't build V1
- If V1 estimates are wrong → fix before V2
- If V2 scoring is off → iterate before V3
- If V3 UI is confusing → simplify

### Clear Success Criteria
- MVP success: 10 teammates use it regularly
- V1 success: Estimates within ±30% of actual
- V2 success: Top 10 ranked businesses are objectively better
- V3 success: Users choose Scout over manual research 100% of the time

---

**End of PRD**

Questions or feedback? Let's refine this vision together.
