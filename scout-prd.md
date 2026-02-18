# Product Requirements Document: Scout Deal Flow Intelligence System

**Version:** 1.0
**Date:** February 14, 2026
**Status:** Draft
**Owner:** Holt Ventures

---

## Executive Summary

Scout is a dual-agent intelligence system that generates calibrated acquisition target lists for small business buyers. The system discovers all businesses in a target industry/geography while simultaneously learning market benchmarks from actual deal transactions, producing prioritized outreach lists in under 10 minutes.

### Problem Statement

When evaluating an industry for small business acquisition, searchers face:
- **Weeks of manual research** to find all potential targets in a geography
- **No baseline data** for what constitutes a "normal" business in that industry
- **Guesswork on valuations** without comparable transaction data
- **Analysis paralysis** from incomplete or inconsistent information

### Solution

A two-agent system that:
1. **Universe Builder Agent** - Discovers all businesses matching thesis criteria
2. **Market Calibrator Agent** - Builds financial benchmarks from actual deal data
3. **Orchestration Layer** - Combines outputs to generate calibrated, prioritized target lists

### Success Criteria

- Reduce thesis validation time from 2-3 weeks to <10 minutes
- Generate 30-50 qualified acquisition targets per industry
- Provide data-backed financial estimates (revenue, valuation) for each target
- Enable immediate outreach with exportable contact lists

---

## Goals & Objectives

### Primary Goals

1. **Accelerate Deal Sourcing**
   - Reduce time to generate target lists by 95%
   - Eliminate manual research grunt work
   - Enable testing multiple industries per day

2. **Improve Target Quality**
   - Provide financial estimates calibrated to real market data
   - Identify businesses matching "typical" deal profiles
   - Prioritize by acquisition attractiveness

3. **Enable Data-Driven Decisions**
   - Answer "Is there enough deal flow?" quantitatively
   - Provide market intelligence (typical valuations, multiples)
   - Support go/no-go thesis decisions with evidence

### Secondary Goals

4. **Build Proprietary Intelligence**
   - Accumulate industry benchmark database
   - Create reusable market intelligence
   - Establish competitive advantage through data

5. **Scale Research Capacity**
   - Enable one person to evaluate 10+ industries/week
   - Support geographic expansion efficiently
   - Facilitate portfolio approach to search

---

## User Personas

### Primary User: Solo Searcher / Independent Sponsor

**Profile:**
- Acquiring first small business ($500K-$3M)
- Limited time for research (nights/weekends)
- No research team or analysts
- Needs high-quality deal flow quickly

**Pain Points:**
- Overwhelmed by manual research
- Unsure where to focus efforts
- Can't evaluate if thesis is viable
- Wastes time on dead-end industries

**Use Case:**
"I think backflow testing looks interesting. Are there enough businesses in Texas? What do they typically sell for? Which specific companies should I contact?"

### Secondary User: Search Fund / Small PE Firm

**Profile:**
- Team of 2-3 people
- Evaluating 20-30 industries simultaneously
- Need systematic, repeatable process
- Focused on off-market deal sourcing

**Pain Points:**
- Can't scale research across industries
- Inconsistent evaluation methodology
- No benchmark data for exotic industries
- Manual processes don't scale

**Use Case:**
"We need to evaluate 5 new industries this week across 3 states each. We need standardized market intelligence and target lists."

---

## Product Requirements

### Functional Requirements

#### FR-1: Universe Discovery

**Description:** Find all businesses matching industry and geography criteria

**Requirements:**
- FR-1.1: Accept industry type (e.g., "HVAC contractor", "backflow testing")
- FR-1.2: Accept geography (city, state, radius in miles, or ZIP codes)
- FR-1.3: Accept optional search term synonyms
- FR-1.4: Search Google Maps API for all matching businesses
- FR-1.5: Deduplicate results by place_id and address similarity
- FR-1.6: Extract standard fields: name, address, phone, website, rating, reviews
- FR-1.7: Filter to operational businesses only
- FR-1.8: Handle radius expansion for nearby cities
- FR-1.9: Complete search in <5 minutes
- FR-1.10: Cost <$5 in API calls per search

**Output:** UniverseSnapshot containing 100-500 businesses with standard fields

---

#### FR-2: Market Benchmark Generation

**Description:** Build financial distributions from actual deal transactions

**Requirements:**
- FR-2.1: Accept industry/business type as input
- FR-2.2: Scrape BizBuySell for active listings (minimum 15 listings)
- FR-2.3: Scrape SMB Deal Machine for closed deals (minimum 5 deals)
- FR-2.4: Extract financial metrics: revenue, cash flow, asking/sale price
- FR-2.5: Extract business details: age, employees, location
- FR-2.6: Clean and normalize extracted data (handle format variations)
- FR-2.7: Calculate statistical distributions: mean, median, stdDev, percentiles
- FR-2.8: Calculate derived metrics: multiples (price/cash flow), margins (cash flow/revenue)
- FR-2.9: Identify and remove outliers (>2.5 standard deviations)
- FR-2.10: Generate visualizations (distribution charts)
- FR-2.11: Complete analysis in <3 minutes
- FR-2.12: Provide confidence scoring based on sample size

**Output:** MarketBenchmark containing distributions and typical business profile

---

#### FR-3: Metric Estimation

**Description:** Estimate financial metrics for discovered businesses using benchmark data

**Requirements:**
- FR-3.1: Accept business data from Universe Builder
- FR-3.2: Accept benchmark distributions from Market Calibrator
- FR-3.3: Estimate revenue using review count as proxy (calibrated to benchmark median)
- FR-3.4: Estimate cash flow using estimated revenue × benchmark median margin
- FR-3.5: Estimate valuation using estimated cash flow × benchmark median multiple
- FR-3.6: Assign confidence level (high/medium/low) based on data completeness
- FR-3.7: Flag businesses as small/medium/large relative to benchmark percentiles
- FR-3.8: Identify outliers (significantly above/below typical ranges)

**Output:** Enhanced business records with estimated financial metrics

---

#### FR-4: Scoring & Ranking

**Description:** Score and prioritize businesses by acquisition attractiveness

**Requirements:**
- FR-4.1: Score businesses on benchmark fit (matches typical profile)
- FR-4.2: Score businesses on quality signals (rating, review engagement)
- FR-4.3: Score businesses on data completeness (has website, phone, etc.)
- FR-4.4: Calculate composite score (0-100 scale)
- FR-4.5: Rank all businesses by score (highest first)
- FR-4.6: Categorize by probability: high/medium/low/investigation-needed
- FR-4.7: Generate reasoning/signals for each score

**Output:** Ranked business list with scores and rationale

---

#### FR-5: Output Generation

**Description:** Produce actionable reports and exportable data files

**Requirements:**
- FR-5.1: Generate Universe Report (JSON, CSV, Markdown)
- FR-5.2: Generate Benchmark Report (JSON, Markdown with charts)
- FR-5.3: Generate Deal Flow Analysis (combined insights, Markdown)
- FR-5.4: Generate Target Lists (CSV for spreadsheet/CRM, prioritized)
- FR-5.5: Include metadata: timestamp, costs, execution time, search parameters
- FR-5.6: Include summary statistics: counts, distributions, key insights
- FR-5.7: Include actionable recommendations: next steps, warnings, opportunities
- FR-5.8: All outputs timestamped and organized by industry-geography-date

**Output:** Complete report package in multiple formats

---

#### FR-6: Multi-Geography Support

**Description:** Search and analyze across multiple geographies efficiently

**Requirements:**
- FR-6.1: Accept multiple cities in single request
- FR-6.2: Execute searches in parallel across geographies
- FR-6.3: Aggregate results across all geographies
- FR-6.4: Break down results by geography in summary
- FR-6.5: Reuse benchmark across geographies (same industry)

**Output:** Combined universe spanning multiple geographies

---

#### FR-7: Multi-Industry Comparison

**Description:** Compare deal flow across multiple industries

**Requirements:**
- FR-7.1: Accept multiple industry types
- FR-7.2: Execute universe building and benchmarking in parallel
- FR-7.3: Generate comparison table: deal flow count, typical size, benchmarks
- FR-7.4: Rank industries by deal flow viability
- FR-7.5: Highlight key differences and trade-offs

**Output:** Comparative analysis across industries

---

### Non-Functional Requirements

#### NFR-1: Performance
- System must complete full analysis (both agents) in <10 minutes
- Universe Builder must complete in <5 minutes
- Market Calibrator must complete in <3 minutes
- System must handle 500+ business records efficiently

#### NFR-2: Cost
- Total cost per industry evaluation must be <$10
- Google Maps API costs must be <$5 per search
- System must track and report all API costs

#### NFR-3: Reliability
- System must handle API failures gracefully (retry logic)
- System must handle incomplete data (missing fields)
- System must handle web scraping failures (timeout, rate limits)
- System must validate all outputs before returning

#### NFR-4: Data Quality
- Universe coverage: 90%+ of businesses vs manual search
- Benchmark sample size: minimum 10 deals per industry
- Deduplication accuracy: 95%+ (no significant duplicates)
- Estimated metrics: within ±30% of actual (where verifiable)

#### NFR-5: Usability
- Terminal interface must be conversational (natural language input)
- Progress must be visible (streaming updates)
- Errors must be clear and actionable
- Outputs must be immediately actionable (ready for outreach)

#### NFR-6: Maintainability
- Web scrapers must be resilient to site changes
- API integrations must handle version changes
- Code must be modular (agents, tools, separate concerns)
- Configuration must be external (API keys, settings)

---

## Technical Architecture

### System Components

```
┌─────────────────────────────────────────────────────┐
│           Terminal Interface (Ink + React)          │
│  Natural language input, streaming progress display │
└─────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────┐
│              Orchestration Layer                    │
│  Agent coordination, result combination, insights   │
└─────────────────────────────────────────────────────┘
                         ↓
        ┌────────────────┴────────────────┐
        ↓                                  ↓
┌──────────────────┐            ┌──────────────────┐
│  Universe        │            │  Market          │
│  Builder Agent   │            │  Calibrator      │
│                  │            │  Agent           │
│  • Google Maps   │            │  • BizBuySell    │
│  • Dedup         │            │  • SMB Deal      │
│  • Filter        │            │  • Statistics    │
└──────────────────┘            └──────────────────┘
                         ↓
┌─────────────────────────────────────────────────────┐
│              Output Generation                      │
│  JSON, CSV, Markdown, Visualizations                │
└─────────────────────────────────────────────────────┘
```

### Agent Architecture

**Universe Builder Agent:**
- Role: Business discovery
- Tools: Google Maps API, Deduplication, Filtering
- Input: Thesis (industry, geography)
- Output: UniverseSnapshot (list of businesses)

**Market Calibrator Agent:**
- Role: Benchmark intelligence
- Tools: BizBuySell scraper, SMB Deal Machine scraper, Statistical analysis
- Input: Industry type
- Output: MarketBenchmark (financial distributions)

**Orchestrator:**
- Role: Coordination and synthesis
- Functions: Launch agents, combine outputs, estimate metrics, score/rank
- Output: Deal Flow Analysis + Target Lists

### Data Flow

```
1. User Input (Thesis)
   ↓
2. Orchestrator launches both agents in parallel
   ↓
3. Agent 1: Universe Building (5 min)
   - Search Google Maps
   - Deduplicate
   - Return business list
   ↓
4. Agent 2: Benchmark Building (3 min)
   - Scrape marketplaces
   - Calculate distributions
   - Return benchmarks
   ↓
5. Orchestrator combines results
   - Estimate metrics for each business
   - Score and rank
   - Generate insights
   ↓
6. Output Generation
   - Write files (JSON, CSV, MD)
   - Display summary in terminal
   - Provide recommendations
```

### Data Models

**Business Entity:**
```
{
  place_id: string
  name: string
  address: string
  city: string
  state: string
  zip: string
  coordinates: { lat, lng }
  phone?: string
  website?: string
  rating?: number
  review_count?: number
  business_status: string
  operational: boolean
  has_website: boolean
  estimated_size: 'small' | 'medium' | 'large'
  estimated_revenue?: number
  estimated_cash_flow?: number
  estimated_valuation?: number
  score?: number
  signals?: string[]
}
```

**Deal Entity:**
```
{
  source: 'bizbuysell' | 'smbdealmachine'
  deal_id: string
  business_type: string
  location: { city, state }
  revenue?: number
  cash_flow?: number
  price: number
  multiple?: number
  margin?: number
  year_established?: number
  employees?: number
  listed_date: string
  close_date?: string
}
```

**Distribution Entity:**
```
{
  metric: string
  count: number
  mean: number
  median: number
  stdDev: number
  p25: number
  p50: number
  p75: number
  p90: number
  min: number
  max: number
  outliers_removed: number
  confidence: 'high' | 'medium' | 'low'
}
```

### Technology Stack

**Runtime:**
- Node.js / Bun
- TypeScript

**Agent Framework:**
- LangChain (agent orchestration)
- Anthropic Claude / OpenAI (LLM for agent reasoning)

**Terminal UI:**
- Ink (React for terminal)
- React 19

**Data Sources:**
- Google Maps Places API
- BizBuySell (web scraping)
- SMB Deal Machine (web scraping)

**Web Scraping:**
- Playwright (headless browser)
- Cheerio (HTML parsing)

**Data Processing:**
- Zod (schema validation)
- csv-writer (CSV export)

---

## User Stories

### US-1: Thesis Validation
**As a** solo searcher
**I want to** validate if an industry has enough deal flow
**So that** I don't waste time pursuing dead-end theses

**Acceptance Criteria:**
- System finds all businesses in industry/geography
- System provides count and summary statistics
- System shows typical deal characteristics
- System gives clear go/no-go recommendation
- Completes in <10 minutes

---

### US-2: Target List Generation
**As a** searcher
**I want to** get a prioritized list of businesses to contact
**So that** I can start outreach immediately

**Acceptance Criteria:**
- System ranks businesses by acquisition attractiveness
- System provides contact information (phone, address)
- System estimates financial metrics (revenue, valuation)
- System exports to CSV for mail merge
- Top 30-50 targets clearly identified

---

### US-3: Market Intelligence
**As a** searcher
**I want to** understand what's "normal" for an industry
**So that** I can recognize good vs. bad opportunities

**Acceptance Criteria:**
- System provides typical revenue, multiples, margins
- System shows distribution visualizations
- System identifies outliers (above/below normal)
- System based on actual transaction data
- Confidence level indicated

---

### US-4: Geographic Expansion
**As a** searcher
**I want to** expand my search to multiple cities
**So that** I can build a larger pipeline

**Acceptance Criteria:**
- System searches multiple geographies efficiently
- System reuses benchmark across geographies
- System shows breakdown by city/state
- System identifies geographic clusters
- No need to re-run benchmark for each city

---

### US-5: Multi-Industry Comparison
**As a** searcher
**I want to** compare deal flow across industries
**So that** I can prioritize my efforts

**Acceptance Criteria:**
- System evaluates multiple industries in parallel
- System provides side-by-side comparison
- System ranks industries by deal flow quality
- System highlights key differences
- Clear recommendation on which to pursue

---

## Success Metrics

### Primary Metrics (MVP)

**Efficiency:**
- Time to generate target list: <10 minutes (vs 2-3 weeks manual)
- Cost per evaluation: <$10
- User can evaluate 5+ industries per day

**Quality:**
- Universe coverage: 90%+ of businesses found (vs manual search)
- Benchmark sample size: 10+ deals per industry
- Target list actionability: 30-50 qualified targets generated

**User Outcomes:**
- Go/no-go decision made with confidence (data-backed)
- Immediate outreach capability (exportable contact list)
- Time saved: 95% reduction in research time

### Secondary Metrics (Future)

**Accuracy:**
- Estimated metrics within ±30% of actual (when verified)
- High-probability targets have 2x response rate vs. random

**Adoption:**
- User evaluates 10+ industries in first month
- User generates 100+ target contacts in first month
- User makes first acquisition within 6 months (influenced by system)

---

## Phased Roadmap

### Phase 1: MVP (Week 1-2)
**Scope:** Two-agent system with basic capabilities

**Deliverables:**
- Universe Builder Agent (Google Maps integration)
- Market Calibrator Agent (BizBuySell + SMB Deal Machine scrapers)
- Orchestration layer (combine outputs)
- Basic scoring and ranking
- Output generation (JSON, CSV, Markdown)
- Terminal interface (conversational)

**Success Criteria:**
- Can evaluate one industry/geography in <10 minutes
- Generates actionable target list (30-50 businesses)
- Provides market benchmarks with visualizations
- Costs <$10 per evaluation

---

### Phase 2: Enrichment (Week 3-4)
**Scope:** Add owner data and business intelligence

**New Capabilities:**
- Owner name enrichment (State SOS, licensing databases)
- Owner age estimation (LinkedIn, property records)
- Business age verification (SOS filing dates)
- Property ownership verification (county records)
- Enhanced scoring (retirement signals)

**Success Criteria:**
- Owner names found for 70%+ of businesses
- Retirement signals identified (age 60+, business 15+ years)
- Target list quality improves (higher response rates)

---

### Phase 3: Deep Intelligence (Week 5-6)
**Scope:** Detailed business research and competitive analysis

**New Capabilities:**
- Website scraping (services, team, founding story)
- Review sentiment analysis (positive/negative trends)
- Competitive landscape mapping (nearby competitors)
- Financial modeling (detailed revenue estimates)
- Valuation analysis (comparable sales)

**Success Criteria:**
- Deep dive profiles available for top targets
- Competitive context for each business
- Valuation estimates within ±20% of asking prices

---

### Phase 4: Automation & Learning (Month 2+)
**Scope:** Pipeline management and continuous improvement

**New Capabilities:**
- Pipeline tracking (watchlist, contacted, LOI stages)
- Outreach material generation (personalized letters)
- Response tracking (who replied, conversion rates)
- Learning loop (improve scoring from outcomes)
- Multi-thesis portfolio management

**Success Criteria:**
- Full deal pipeline visibility
- Outreach automation (letters generated)
- Scoring model improves over time (learning)
- Portfolio-level analytics

---

## Out of Scope (MVP)

The following capabilities are **not included in MVP** but are candidates for future phases:

❌ Owner enrichment (names, ages) - Phase 2
❌ Deep business research (website scraping) - Phase 3
❌ Competitive intelligence - Phase 3
❌ Financial modeling - Phase 3
❌ Valuation analysis - Phase 3
❌ Outreach letter generation - Phase 4
❌ Pipeline/CRM tracking - Phase 4
❌ Learning from outcomes - Phase 4
❌ Multi-thesis portfolio analytics - Phase 4

---

## Future: Data Sources & Business Sizing Proxies

### Philosophy

**Core Insight:** Geographic business lists are always valuable, but their value multiplies when we can accurately estimate business size/quality. Since financial data isn't publicly available for small businesses, we need **proxy signals** that correlate with revenue, profitability, and acquisition attractiveness.

**Goal:** Develop a portfolio of proxies that:
1. Are accessible (API or scrapable)
2. Correlate with actual business performance
3. Are cost-effective to acquire at scale
4. Can be validated against benchmark data
5. Work across different industry types

**Strategy:** Start with simple proxies (reviews), validate against benchmarks, then layer in additional signals to improve accuracy over time.

---

### Proxy Data Sources: Current & Future

#### TIER 1: Currently Implemented

**1. Google Reviews (Review Count + Rating)**

**What it measures:**
- Review count → Customer volume proxy
- Rating → Quality/satisfaction proxy
- Review velocity → Growth/activity signals

**Hypothesis:**
- More reviews = more customers = higher revenue
- Higher rating = better operation = higher margins

**Validation approach:**
- Map review percentile → benchmark revenue percentile
- Test correlation: Does P75 review count = P75 revenue?
- Measure accuracy: ±30% of actual?

**Strengths:**
- ✅ Free (included in Google Maps API)
- ✅ Available for 90%+ of businesses
- ✅ Updated continuously

**Weaknesses:**
- ❌ B2B businesses have fewer reviews than B2C
- ❌ Review culture varies by industry (plumbers get more reviews than industrial services)
- ❌ Doesn't capture contract vs. one-time revenue
- ❌ Older businesses may have accumulated reviews over decades

**Improvement ideas:**
- Normalize by business age (reviews per year)
- Adjust by industry (car washes expect 500+ reviews, backflow testers expect 20)
- Weight recent reviews higher (last 12 months)

---

#### TIER 2: High-Priority Future Sources

**2. Foot Traffic Data**

**What it measures:**
- Physical visits to location
- Traffic patterns (daily, weekly, seasonal)
- Dwell time
- Customer return rate

**Providers:**
- **SafeGraph** (now Dewey) - $500-2000/month
- **Placer.ai** - $1000+/month
- **Foursquare (FSQ)** - API pricing
- **Unacast** - Enterprise pricing

**Use cases:**
- Car washes: Daily visits → cars washed/day → revenue estimate
- Retail: Foot traffic → sales conversion → revenue
- Salvage yards: Visits → parts sales volume

**Validation approach:**
- Get foot traffic for 10 businesses
- Compare to benchmark revenue data
- Calculate correlation coefficient
- Build conversion formula (visits → revenue by industry)

**Strengths:**
- ✅ Direct activity measurement
- ✅ Works great for B2C businesses (car washes, retail)
- ✅ Captures seasonality

**Weaknesses:**
- ❌ Expensive at scale
- ❌ Less useful for B2B (commercial recycling, medical waste)
- ❌ Requires ongoing subscription
- ❌ Privacy concerns, data quality issues

**Priority:** HIGH for car washes, express businesses, retail-facing operations
**Timeline:** Phase 2-3 (after MVP validates core concept)

---

**3. Web Traffic & Online Presence**

**What it measures:**
- Website monthly visitors
- SEO ranking
- Social media following
- Online advertising presence

**Providers:**
- **SimilarWeb** - $200+/month
- **SEMrush** - $120+/month
- **Ahrefs** - $100+/month
- Free: Scrape meta tags, estimate from social followers

**Use cases:**
- Businesses with online lead gen (addiction treatment, HVAC)
- E-commerce components (auto parts sales online)
- Marketing sophistication proxy

**Validation approach:**
- Scrape website traffic estimates for sample businesses
- Compare high-traffic vs. low-traffic to benchmark revenues
- Test hypothesis: More traffic = more leads = more revenue

**Strengths:**
- ✅ Indicates marketing sophistication
- ✅ Proxy for lead generation volume
- ✅ Can be scraped for free (estimates)

**Weaknesses:**
- ❌ 25% of businesses have no website
- ❌ B2B businesses may have low traffic but high contract values
- ❌ Traffic ≠ revenue (depends on conversion)

**Priority:** MEDIUM for businesses with online lead gen
**Timeline:** Phase 2

---

**4. Employee Count**

**What it measures:**
- Business size/capacity
- Labor intensity
- Growth trajectory

**Sources:**
- **LinkedIn company page** - Free to scrape
- **Indeed job listings** - Active hiring signals
- **ZoomInfo/RocketReach** - $1000+/year
- **State unemployment insurance filings** - Public but hard to access

**Use cases:**
- Industrial services: More employees = more crews = more capacity
- Treatment centers: Staff count = patient capacity
- Salvage yards: Dismantlers + counter staff = throughput

**Validation approach:**
- Scrape LinkedIn employee counts
- Compare to benchmark employee distributions
- Build formula: Employees → revenue (by industry, varies widely)

**Strengths:**
- ✅ Strong correlation with revenue (especially labor-intensive businesses)
- ✅ Can be scraped for free (LinkedIn)
- ✅ Indicates capacity/scale

**Weaknesses:**
- ❌ Not all businesses have LinkedIn pages
- ❌ LinkedIn counts may be outdated
- ❌ Varies wildly by industry (automated car wash: 3 employees, $1M revenue vs. consulting: 3 employees, $300K revenue)

**Priority:** HIGH for labor-intensive businesses (waste hauling, laundry services)
**Timeline:** Phase 2

---

**5. Equipment & Asset Indicators**

**What it measures:**
- Capital intensity
- Fleet size (for route-based businesses)
- Real estate footprint

**Sources:**
- **Google Street View** - Free, can see trucks/equipment
- **DOT vehicle registrations** - Public, business name → fleet size
- **Property records** - County assessor, real estate owned
- **Business license applications** - Vehicle/equipment declarations

**Use cases:**
- Waste hauling: # of trucks visible = route capacity
- Car washes: Tunnel length, bay count = throughput
- Salvage yards: Lot size (acres) = inventory capacity
- Equipment rental: Inventory visible in photos

**Validation approach:**
- Manually count trucks/equipment from Street View for 20 businesses
- Compare to their benchmark revenue estimates
- Build formula: Trucks → routes → revenue

**Strengths:**
- ✅ Free data (Street View, public records)
- ✅ Strong correlation for equipment-intensive businesses
- ✅ Hard to fake (physical assets visible)

**Weaknesses:**
- ❌ Labor-intensive to collect (manual counting)
- ❌ Street View may be outdated
- ❌ Can't see equipment stored inside/off-site

**Priority:** MEDIUM-HIGH for equipment-heavy businesses
**Timeline:** Phase 3 (deep intelligence)

---

**6. Licensing & Regulatory Data**

**What it measures:**
- Capacity/authorization levels
- Business scope
- Compliance/legitimacy

**Sources:**
- **State licensing databases** - Free, public
- **EPA permits** - Free, public (waste, medical, hazmat)
- **DOT authorities** - Free, public (hauling, transport)
- **Professional certifications** - Industry-specific

**Examples:**
- Medical waste: EPA permit capacity (tons/year authorized)
- Treatment centers: State license capacity (beds, patient slots)
- Waste hauling: Permit for specific waste types, geographies
- Fire inspection: Number of certified inspectors

**Use cases:**
- Treatment centers: Licensed beds = revenue capacity
- Waste/medical: Permit capacity = theoretical max revenue
- Inspection services: # of certified inspectors = service capacity

**Validation approach:**
- Scrape state license databases
- Extract capacity indicators (beds, tonnage, vehicles)
- Compare to benchmark revenues

**Strengths:**
- ✅ Free, public data
- ✅ Indicates legal capacity/authorization
- ✅ Hard to inflate (regulatory oversight)

**Weaknesses:**
- ❌ Capacity ≠ utilization (licensed for 30 beds, only fill 20)
- ❌ Data is fragmented (50 state databases, different formats)
- ❌ Not updated frequently

**Priority:** HIGH for regulated industries (treatment, waste, medical)
**Timeline:** Phase 2 (enrichment)

---

#### TIER 3: Experimental / Future Research

**7. Utility Data (Electricity, Water, Gas)**

**What it measures:**
- Operational activity
- Throughput (water = car washes, electricity = manufacturing)

**Hypothesis:**
- Car wash water usage → cars washed → revenue
- Industrial electricity → production volume → revenue

**Challenge:** Not publicly available, privacy concerns
**Feasibility:** LOW unless partnerships with utilities
**Timeline:** Not near-term

---

**8. Job Posting Activity**

**What it measures:**
- Growth signals
- Staffing needs
- Business health

**Sources:**
- Indeed, LinkedIn, Glassdoor (free scraping)

**Use cases:**
- Hiring = growth or turnover
- Job descriptions reveal service offerings
- Salary ranges indicate profitability

**Priority:** LOW (noisy signal)
**Timeline:** Phase 4+

---

**9. Yelp Check-ins / OpenTable Reservations (Limited applicability)**

**What it measures:**
- Customer volume (restaurants, retail)

**Use cases:**
- Very limited for our thesis (we're not buying restaurants)

**Priority:** LOW
**Timeline:** N/A

---

**10. Building Permits & Construction Activity**

**What it measures:**
- Expansion/growth
- Capital investment

**Sources:**
- City/county building permit databases (free)

**Use cases:**
- Recent permits = expansion = growth
- Large investments = confidence in business

**Priority:** LOW (nice-to-have context)
**Timeline:** Phase 3+

---

### Proxy Validation Methodology

**The Challenge:** How do we know if a proxy is reliable?

**Approach:** Calibrate proxies against benchmark data

#### Step 1: Hypothesis Formation
```
Example:
H1: Review count correlates with revenue
H2: Higher percentile in reviews = higher percentile in revenue
H3: This relationship is consistent within an industry
```

#### Step 2: Data Collection
```
1. Get benchmark data (BizBuySell)
   - 30 HVAC businesses with known revenues

2. Find those businesses on Google Maps
   - Get their review counts

3. Create dataset:
   Business A: 250 reviews, $1.2M revenue
   Business B: 80 reviews, $600K revenue
   Business C: 400 reviews, $1.8M revenue
   ...
```

#### Step 3: Statistical Analysis
```
1. Calculate correlation coefficient (Pearson's r)
   - r > 0.7 = strong correlation
   - r = 0.4-0.7 = moderate
   - r < 0.4 = weak

2. Plot scatter: Reviews (x) vs. Revenue (y)
   - Look for linear relationship
   - Identify outliers

3. Build regression model:
   Revenue = β0 + β1 × (Review Count) + ε

4. Test on holdout set:
   - Predict revenue for 10 businesses
   - Calculate MAPE (Mean Absolute Percentage Error)
   - Target: <30% error
```

#### Step 4: Industry Adjustment
```
Test if relationship varies by industry:
- HVAC: 100 reviews = $800K revenue
- Car wash: 500 reviews = $1.2M revenue
- Backflow testing: 20 reviews = $400K revenue

Build industry-specific formulas
```

#### Step 5: Composite Scoring
```
Don't rely on single proxy - combine signals:

Revenue estimate = f(
  review_count,
  rating,
  employee_count,
  website_traffic,
  equipment_visible
)

Weighted by:
- Proxy reliability (correlation strength)
- Data availability (what % have this signal)
- Industry type (B2C vs. B2B)
```

#### Step 6: Confidence Levels
```
Assign confidence based on:
- High confidence: Multiple strong proxies agree
- Medium confidence: Single strong proxy OR multiple weak
- Low confidence: Only weak proxies OR conflicting signals
- Unknown: Insufficient data

Example:
Business A:
- 200 reviews (suggests $900K)
- 12 employees (suggests $950K)
- Website traffic: 5K/mo (suggests $850K)
→ Confidence: HIGH, estimate: $900K ±15%

Business B:
- 15 reviews (suggests $400K)
- No website (no data)
- No LinkedIn (no employee count)
→ Confidence: LOW, estimate: $400K ±40%
```

---

### Research Plan: Testing Proxies

**Phase 1: Validate Review-Based Estimation (Week 1-2)**

**Goal:** Prove (or disprove) that review count → revenue

**Tasks:**
1. Scrape BizBuySell for 50 businesses with known revenues
2. Find those businesses on Google Maps, get review counts
3. Calculate correlation, build formula
4. Test on holdout set of 10 businesses
5. Document accuracy (MAPE)

**Success criteria:** MAPE <30% or discover it doesn't work

---

**Phase 2: Add Employee Count Proxy (Week 3-4)**

**Goal:** Improve estimates with LinkedIn employee data

**Tasks:**
1. Scrape LinkedIn for employee counts (100 businesses)
2. Compare to revenue benchmarks
3. Build composite model: reviews + employees
4. Test if accuracy improves

**Success criteria:** Combined model beats single-proxy model

---

**Phase 3: Test Foot Traffic (Month 2)**

**Goal:** Evaluate if foot traffic is worth paying for

**Tasks:**
1. Get free trial from SafeGraph/Placer.ai
2. Pull foot traffic for 30 car washes
3. Compare to revenue estimates from reviews
4. Calculate incremental accuracy gain
5. ROI analysis: Is it worth $500-2000/month?

**Success criteria:** Foot traffic improves accuracy by >15% AND ROI is positive

---

**Phase 4: Industry-Specific Proxy Research (Month 3+)**

**Goal:** Develop specialized proxies per business type

**Tasks:**
1. Waste/recycling: Scrape DOT vehicle registrations → truck count
2. Treatment centers: Scrape state licenses → bed capacity
3. Car washes: Scrape building permits → tunnel length/bays
4. Salvage yards: Google Earth → lot size (acres)

**Success criteria:** Specialized proxies beat generic proxies for each industry

---

### Proxy Maturity Roadmap

**MVP (Phase 1):**
```
✓ Review count (percentile mapping)
✓ Rating (quality adjustment)
✓ Has website (completeness signal)
→ Accuracy target: ±30-40%
→ Confidence: Medium for most businesses
```

**Phase 2 (Enrichment):**
```
✓ Employee count (LinkedIn scraping)
✓ Licensing data (capacity indicators)
✓ Equipment visibility (Street View counts)
→ Accuracy target: ±20-30%
→ Confidence: High for 60% of businesses
```

**Phase 3 (Deep Intelligence):**
```
✓ Foot traffic (paid data for select industries)
✓ Website traffic (SEO tools)
✓ Industry-specific proxies
→ Accuracy target: ±15-25%
→ Confidence: High for 80% of businesses
```

**Phase 4 (Continuous Learning):**
```
✓ User feedback loop (actual valuations from acquired businesses)
✓ Machine learning models (train on actual outcomes)
✓ Proprietary database (accumulate ground truth data)
→ Accuracy target: ±10-20%
→ Confidence: High for 90% of businesses
```

---

### Cost-Benefit Analysis: Data Sources

| Data Source | Cost/Month | Coverage | Accuracy Gain | ROI | Priority |
|-------------|------------|----------|---------------|-----|----------|
| Google Reviews | $0 | 95% | Baseline | ∞ | ✅ NOW |
| Employee Count (LinkedIn) | $0 | 60% | +10-15% | ∞ | ✅ Phase 2 |
| Licensing Data | $0 | 40% | +15-20% (regulated industries) | ∞ | ✅ Phase 2 |
| Equipment Visible (Street View) | $0 | 80% | +5-10% | ∞ | ✅ Phase 2 |
| Foot Traffic | $500-2000 | 70% | +15-25% (B2C only) | ? | ⚠️ Test Phase 3 |
| Web Traffic | $100-200 | 70% | +5-10% | ? | ⚠️ Phase 3 |
| ZoomInfo (employee/revenue) | $1000+ | 30% | +20-30% | ? | ⚠️ Phase 4 |

**Strategy:** Exhaust free sources first, then selectively pay for high-ROI signals

---

### Open Questions for Proxy Research

**Q1: Industry Variance**
- Do proxies work across all industries or need industry-specific models?
- Action: Test correlation by industry type (B2B vs. B2C, service vs. retail)

**Q2: Geographic Variance**
- Does review culture vary by region (coastal vs. rural)?
- Action: Compare review-to-revenue ratios in different metros

**Q3: Business Age Effects**
- Do older businesses have inflated review counts (accumulated over decades)?
- Action: Control for business age (reviews per year in business)

**Q4: Proxy Decay**
- How quickly do proxies become stale (6 months, 1 year, 3 years)?
- Action: Track when data was collected, flag for refresh

**Q5: Composite vs. Single**
- Is composite score always better or do diminishing returns kick in?
- Action: Test 1-proxy vs. 2-proxy vs. 3-proxy models

**Q6: Human Validation**
- At what point should we recommend manual research instead of estimates?
- Action: Set confidence thresholds (e.g., "investigate" if confidence <40%)

---

### Success Metrics: Proxy System

**Accuracy Metrics:**
- Mean Absolute Percentage Error (MAPE) <30% for revenue estimates
- 70%+ of businesses have "medium" or "high" confidence estimates
- Estimates fall within benchmark ranges (P25-P75) for 80% of businesses

**Coverage Metrics:**
- 90%+ of businesses have at least 1 proxy signal
- 60%+ of businesses have 2+ proxy signals
- <10% flagged as "insufficient data"

**Validation Metrics:**
- Proxies tested against 100+ known-revenue businesses
- Industry-specific formulas for top 5 industries
- Quarterly re-calibration as more benchmark data collected

**User Feedback:**
- When users acquire businesses, capture actual revenue → validate estimates
- Build proprietary training set (100+ actual deals)
- Retrain models quarterly, improve accuracy over time

---

## Future: Sentiment & Regulatory Intelligence

### Philosophy

**The Gap:** Quantitative proxies tell you business *size*, but not industry *health*, owner *readiness*, or regulatory *tailwinds*. Sentiment analysis and legislative monitoring can provide:

1. **Industry Health Signals** - Is this industry growing, stable, or dying?
2. **Owner Exit Signals** - Are owners burned out, retiring, or under pressure?
3. **Regulatory Moats** - Are new laws strengthening or weakening barriers to entry?
4. **Market Timing** - Is this the right time to enter this industry?
5. **Competitive Intelligence** - What are operators struggling with?

**Goal:** Build intelligence layer that answers "Should we pursue this industry NOW?" and "What will make owners want to sell?"

---

### Intelligence Source Categories

#### 1. Owner Sentiment Mining

**Goal:** Detect retirement readiness, burnout, succession concerns

**Sources:**

**Reddit Communities:**
- r/smallbusiness (200K+ members)
- r/entrepreneur (3M+ members)
- r/Buysmallbusiness (8K+ members)
- r/ExitStrategy (niche, owner exits)
- Industry-specific subs (r/AutoDetailing, r/HVAC, etc.)

**Facebook Groups:**
- "Small Business Owners" groups (100K+ members)
- Industry-specific groups ("Car Wash Owners," "Waste Management Professionals")
- Local business groups by city

**Forums:**
- BizBuySell forums (buyers/sellers)
- Industry trade forums (Waste360, CarWashNews, etc.)
- LinkedIn groups (industry-specific)

**What to look for:**
```
🔴 SELLER SIGNALS (High priority):
- "Thinking about selling my [business type]"
- "How do I find a buyer for my [business]?"
- "Retiring soon, no one to take over"
- "Kids don't want the business"
- "Burned out after 20 years"
- "New regulations are killing me"
- "Can't find good employees anymore"

🟡 STRESS SIGNALS (Medium priority):
- "This business is harder than it used to be"
- "Margins getting squeezed"
- "Competition from [big player]"
- "Insurance costs doubled"
- "Thinking about getting out"

🟢 OPPORTUNITY SIGNALS:
- "Looking to buy a [business type]"
- "This industry is undervalued"
- "Boomers retiring, no successors"
```

**Analysis Approach:**
1. **Keyword Monitoring**
   - Set up alerts for industry keywords + "selling," "retiring," "burnout"
   - Track sentiment over time (% negative vs. positive)

2. **Pain Point Clustering**
   - What are the top 10 complaints in each industry?
   - Are they systematizable problems (good) or fundamental issues (bad)?

3. **Retirement Trend Tracking**
   - How often do "retirement" and "succession" appear?
   - Increasing mentions = more sellers coming to market

**Implementation:**
```
Tools:
- Reddit API (free for reading)
- Pushshift.io (Reddit archive search)
- Custom scraper for forums
- GPT-4 for sentiment classification

Output:
- "Owner Sentiment Score" per industry (0-100)
- Top 10 pain points
- Recent seller signals (last 30 days)
- Trend: Sentiment improving or worsening?
```

**Use Case:**
```
Example: Auto Salvage Yards

Reddit search: "junk yard" OR "auto salvage" + "sell" OR "retire"
Found: 47 posts in last 6 months

Sentiment analysis:
- 34 posts (72%) mention difficulty finding successors
- 23 posts (49%) mention EPA compliance burden
- 18 posts (38%) mention "getting out soon"

Insight:
→ HIGH seller motivation (succession crisis)
→ EPA compliance is a pain point (we can systematize)
→ TIMING: Now is a good time to approach owners
```

---

#### 2. Industry Health Scoring

**Goal:** Determine if industry is growing, stable, or declining

**Sources:**

**Reddit/Forum Activity:**
- Post volume trends (growing community = healthy industry)
- Sentiment trends (more positive = optimism, more negative = stress)
- New entrant posts ("Starting a car wash business" = competitive threat)

**Google Trends:**
- Search volume for "[industry] business for sale"
- Search volume for "[industry] near me" (demand side)
- Geographic hotspots (which cities searching most?)

**Industry Publications:**
- Trade magazines (Waste360, Professional Carwashing)
- Conference attendance (growing or shrinking?)
- Job postings in industry (hiring = growth)

**Economic Indicators:**
- BLS employment data by NAICS code
- Industry association membership trends
- New business formations (Secretary of State data)

**Analysis Framework:**
```
Industry Health Score (0-100):

1. Community Activity (20 points)
   - Reddit post volume trend (+/- 20%)
   - New members joining groups

2. Sentiment (20 points)
   - % positive posts about industry
   - Operator optimism vs. pessimism

3. Market Demand (20 points)
   - Google search trends (demand for services)
   - Job posting volume (need for workers)

4. Competition (20 points)
   - New entrant mentions (fewer = better)
   - Consolidation activity (PE roll-ups)

5. Economic Tailwinds (20 points)
   - Regulatory support
   - ESG/sustainability trends
   - Demographic shifts
```

**Scoring Examples:**
```
Commercial Recycling: 85/100
✓ Strong ESG tailwinds
✓ Municipal mandates increasing
✓ Positive sentiment from operators
⚠ Some consolidation by large players

Car Washes: 78/100
✓ Growing consumer demand
✓ Membership model momentum
⚠ New entrants (PE-backed chains)
⚠ Real estate costs rising

Auto Salvage: 72/100
✓ Stable demand (cars still crash)
✓ Low new entrant threat
⚠ Aging owner base (succession crisis)
⚠ EV parts market uncertain

Addiction Treatment: 68/100
✓ Massive societal need (opioid crisis)
⚠ Reimbursement pressure (insurance rates)
⚠ Burnout common among operators
⚠ Regulatory compliance burden
```

**Use Case:**
```
Question: "Should we pursue commercial recycling or medical waste?"

Industry Health Analysis:
- Commercial recycling: 85/100 (strong tailwinds)
- Medical waste: 75/100 (stable, regulatory moat)

Recommendation:
→ Commercial recycling has stronger momentum
→ But medical waste has higher barriers (better defensibility)
→ Depends on your priority: growth vs. moat
```

---

#### 3. Regulatory Intelligence

**Goal:** Identify legislative changes that create opportunities or risks

**Why This Matters:**
- New regulations = barriers to entry = moat strengthening
- Compliance costs = small players exit = consolidation opportunity
- Regulatory tailwinds = market growth
- Regulatory risk = avoid or wait

**Sources:**

**Federal Level:**
- **EPA regulations** (waste, recycling, hazmat, water)
  - EPA.gov newsroom, Federal Register
- **DOT regulations** (commercial vehicles, hazmat transport)
  - FMCSA.gov
- **OSHA standards** (workplace safety)
  - OSHA.gov
- **Healthcare regulations** (treatment centers, medical waste)
  - HHS.gov, CMS.gov

**State Level:**
- **State legislatures** (track bills by keyword)
  - LegiScan.com (API for bill tracking)
  - State government websites
- **State environmental agencies** (permits, compliance)
- **State licensing boards** (new requirements)
- **Attorney General consumer protection** (enforcement trends)

**Local Level:**
- **Municipal ordinances** (recycling mandates, water restrictions)
- **Zoning changes** (car washes, salvage yards, treatment centers)
- **Local news** (regulatory actions, enforcement)

**Industry Associations:**
- Trade groups often track legislation
- Lobbying updates, position papers
- Member newsletters

**Analysis Framework:**

**Regulatory Event Types:**
```
🟢 POSITIVE TAILWINDS (Opportunity signals):
1. New barrier to entry
   - Example: "New EPA permit required for medical waste"
   - Impact: Deters new competitors, existing businesses more valuable

2. Mandate for services
   - Example: "California requires commercial recycling"
   - Impact: Guaranteed demand, market expansion

3. Compliance upgrades required
   - Example: "All car washes must install water reclaim by 2027"
   - Impact: Small operators can't afford, consolidation opportunity

4. Tax incentives
   - Example: "EV charging stations at car washes get tax credit"
   - Impact: Subsidizes improvements, boosts profitability

🟡 NEUTRAL/MIXED (Monitor):
5. Clarification of existing rules
   - May help or hurt, depends on interpretation

6. Enforcement increases
   - Non-compliant operators face pressure
   - Compliant operators benefit

🔴 NEGATIVE RISKS (Avoid or wait):
7. Deregulation
   - Example: "Licensing requirements eliminated"
   - Impact: Flood of new entrants, erodes moat

8. Service bans
   - Example: "Single-use plastics banned"
   - Impact: Industry decline

9. Punitive costs
   - Example: "Waste disposal fees triple"
   - Impact: Margin compression, customer flight
```

**Regulatory Event Monitoring:**
```
Setup:
1. Keyword alerts on LegiScan
   - "waste management," "recycling," "car wash," "salvage"
   - "treatment center," "medical waste"

2. Google Alerts for news
   - "[Industry] + regulation"
   - "[Industry] + EPA"
   - "[Industry] + legislation"

3. RSS feeds from:
   - EPA newsroom
   - State environmental agencies
   - Industry trade publications

4. Quarterly review of:
   - Federal Register (new rules)
   - State legislative calendars
```

**Output Format:**
```
Regulatory Intelligence Report - Commercial Recycling

Recent Events (Last 6 months):

🟢 TAILWIND: California AB 1234 (Jan 2026)
   - Mandates recycling for all commercial buildings >10K sqft
   - Impact: +30K potential customers in CA
   - Timing: Takes effect July 2026
   - Opportunity: Acquire CA recycling businesses before mandate

🟢 TAILWIND: Texas HB 567 (Dec 2025)
   - New permit required for commercial waste hauling
   - Impact: Raises barrier to entry, $15K permit + 6 months
   - Timing: Effective now
   - Opportunity: Existing permit holders more valuable

🟡 MIXED: EPA announces stricter contamination standards (Feb 2026)
   - Impact: Requires better sorting (operational challenge)
   - But also: Reduces competition from low-quality operators
   - Timing: 2027 implementation
   - Action: Build sorting efficiency playbook

🔴 RISK: None identified

Overall Assessment:
→ STRONG regulatory tailwinds for commercial recycling
→ Barriers to entry increasing (good for acquisitions)
→ Market expansion from mandates (growing demand)
→ TIMING: Excellent time to acquire (before mandate impact)
```

**Use Case - Acquisition Timing:**
```
Scenario: Texas passes new waste hauling permit requirement

Analysis:
- Existing operators: Have permits (grandfathered)
- New entrants: Must wait 6 months + $15K
- Small operators: May not afford compliance

Strategy:
→ Acquire existing permit holders NOW (before market reprices)
→ Consolidate multiple permits in target geography
→ Barrier to entry just increased = moat strengthened
→ Our acquisitions just became more valuable
```

---

#### 4. Competitive Intelligence from Operator Forums

**Goal:** Understand what's actually hard about these businesses

**Why This Matters:**
- If operators complain about systematizable problems (routing, scheduling, billing) = opportunity for us
- If operators complain about fundamental problems (demand declining, impossible margins) = avoid

**What to Look For:**

**🟢 GOOD PROBLEMS (Systematizable):**
```
- "Can't optimize routes efficiently"
  → We can build route optimization software

- "Billing insurance is a nightmare"
  → We can hire billing specialists, build systems

- "Hard to find good employees"
  → We can build training programs, better pay

- "Spending too much time on admin"
  → We can centralize back-office, hire ops manager

- "Don't know which customers are profitable"
  → We can build analytics, margin analysis

- "Equipment breaks down, don't have maintenance schedule"
  → We can build preventive maintenance systems
```

**🔴 BAD PROBLEMS (Structural):**
```
- "Customers switching to [substitute product]"
  → Industry in decline, avoid

- "Amazon/Uber/BigCo entering our market"
  → Competitive threat, avoid or wait

- "Margins compressed 50% in last 3 years"
  → Structural pricing pressure, avoid

- "Regulatory compliance is impossible"
  → If operators can't comply, we probably can't either

- "Customer demand falling off a cliff"
  → Market decline, avoid
```

**Analysis Approach:**
```
1. Scrape industry forums/subreddits
2. Extract top 20 pain points (by mention frequency)
3. Classify each:
   - Operational (we can fix)
   - Strategic (harder, but possible)
   - Structural (avoid)
4. Calculate "Systematization Score"
   - % of complaints that are operational
   - High score = good acquisition target
```

**Example Output:**
```
Industry: Car Washes
Pain Points (Last 12 months):

Top Complaints:
1. "Chemical costs are killing margins" (127 mentions)
   - Classification: OPERATIONAL
   - Fix: Negotiate bulk purchasing, optimize dosing

2. "Can't keep equipment running" (98 mentions)
   - Classification: OPERATIONAL
   - Fix: Preventive maintenance schedule, parts inventory

3. "Staffing is impossible" (89 mentions)
   - Classification: STRATEGIC
   - Fix: Automate more, better pay/benefits, training

4. "Membership churn is high" (76 mentions)
   - Classification: OPERATIONAL
   - Fix: Customer feedback loops, service quality monitoring

5. "Real estate costs too high" (54 mentions)
   - Classification: STRUCTURAL
   - Risk: Location-dependent, can't fix

Systematization Score: 78/100
- 78% of complaints are operational (fixable)
- Only 22% are structural
→ VERDICT: Good acquisition target, problems are systematizable
```

---

#### 5. Geographic Hotspot Detection

**Goal:** Identify which cities/regions have regulatory tailwinds or seller pressure

**Approach:**

**Regulatory Hotspots:**
```
Monitor:
- Which states passing favorable legislation?
- Which cities mandating services (recycling, inspections)?
- Which regions have recent compliance deadlines?

Output:
"California has 3 new recycling mandates in last year
→ LA, SF, San Diego = priority markets"
```

**Seller Pressure Hotspots:**
```
Monitor:
- Reddit mentions of selling by geography
- BizBuySell listing density by metro
- Aging owner demographics by region (census data)

Output:
"Phoenix has 2x more 'thinking about selling' mentions than average
→ Phoenix = hot market for deal flow"
```

**Market Timing Signals:**
```
Combine:
- Regulatory tailwinds (new mandates coming)
- Seller pressure (owners want out)
- Deal flow density (listings available)

Output:
"Houston + New EPA permit requirement + 23 sellers on BizBuySell
→ TIMING: Acquire in Houston NOW (before permit requirement prices in)"
```

---

### Implementation Plan

#### Phase 1: Manual Research (Month 1)
**Goal:** Prove concept with manual analysis

**Tasks:**
1. Manually search Reddit/forums for 3 industries
2. Catalog top 20 pain points per industry
3. Manually track 5 relevant pieces of legislation
4. Write up "Industry Intelligence Report" template

**Output:**
- 3 industry intelligence reports
- Proof that sentiment/regulatory data is valuable
- Template for future automation

---

#### Phase 2: Semi-Automated Monitoring (Month 2-3)
**Goal:** Build tools to streamline intelligence gathering

**Tools to Build:**
1. **Reddit Sentiment Scraper**
   - Use Reddit API + Pushshift
   - Pull posts by keyword, classify sentiment
   - Generate weekly digest

2. **Legislative Alert System**
   - Set up LegiScan alerts
   - Google Alerts for regulatory news
   - Weekly review of new legislation

3. **Pain Point Analyzer**
   - Scrape forums, extract common complaints
   - Use GPT-4 to classify (operational vs. structural)
   - Generate "systematization score"

**Output:**
- Automated weekly intelligence digest
- Per-industry sentiment scores
- Regulatory event tracker

---

#### Phase 3: Intelligence Dashboard (Month 4+)
**Goal:** Real-time intelligence for all target industries

**Dashboard Features:**
```
Industry Intelligence Dashboard

Industry: Commercial Recycling

1. Owner Sentiment: 🟢 68/100
   - Seller signals: 🔴 High (47 mentions in 6mo)
   - Burnout signals: 🟡 Medium
   - Trend: ↗️ Improving

2. Industry Health: 🟢 85/100
   - Growth: ✓ Strong ESG tailwinds
   - Competition: ⚠️ Some PE consolidation
   - Trend: ↗️ Growing

3. Regulatory Environment: 🟢 Favorable
   - Recent tailwinds: CA recycling mandate (Jan 2026)
   - Upcoming changes: TX permit requirement (2027)
   - Risk level: Low
   - Trend: ↗️ Strengthening

4. Systematization Score: 🟢 82/100
   - Top pain points: Route optimization (fixable)
   - Structural risks: Low
   - Opportunity: ✓ High

VERDICT: ✅ STRONG BUY SIGNAL
- High seller motivation (succession crisis)
- Regulatory tailwinds (barriers increasing)
- Problems are systematizable (we can fix)
- TIMING: Acquire now, before mandate impact
```

---

### Use Cases: Deal Exploration & Thesis Validation

**Use Case 1: Industry Selection (Comparative Analysis)**
```
Question: "Which 2 industries from our Tier 1 list should we deep-dive on?"

Intelligence Analysis:

COMMERCIAL RECYCLING:
- Industry Health: 85/100 (strong ESG tailwinds, municipal mandates)
- Systematization Score: 82/100 (route optimization, scheduling = fixable)
- Regulatory: 🟢 Tailwinds (CA/TX mandates, barriers increasing)
- Operator Sentiment: 68/100 (stressed but optimistic)
- Key problems: Operational (routes, sorting, labor)
- Market timing: ✓ Excellent (mandates coming, acquire before repricing)

CAR WASHES:
- Industry Health: 78/100 (growing demand, membership momentum)
- Systematization Score: 81/100 (throughput, chemical efficiency = fixable)
- Regulatory: 🟡 Neutral (some water restrictions = good, zoning challenges)
- Operator Sentiment: 72/100 (stressed about labor, equipment)
- Key problems: Operational (staffing, maintenance, churn)
- Market timing: ✓ Good (steady, but PE entering)

ADDICTION TREATMENT:
- Industry Health: 68/100 (massive need, but reimbursement pressure)
- Systematization Score: 64/100 (billing = fixable, burnout = structural)
- Regulatory: 🔴 Mixed (compliance heavy, reimbursement declining)
- Operator Sentiment: 61/100 (high burnout, regulatory fatigue)
- Key problems: Mixed (billing = fixable, insurance rates = structural)
- Market timing: ⚠️ Uncertain (rates declining, regulatory burden rising)

AUTO SALVAGE:
- Industry Health: 72/100 (stable demand, low competition)
- Systematization Score: 78/100 (inventory, pricing = fixable)
- Regulatory: 🟢 Stable (EPA moat strong, no major changes)
- Operator Sentiment: 66/100 (succession crisis, but stable operations)
- Key problems: Operational (inventory management, cataloging)
- Market timing: ✓ Good (steady, succession crisis = deal flow)

THESIS VALIDATION VERDICT:
→ RECYCLING: Highest conviction (health + timing + tailwinds)
→ CAR WASHES: Second choice (solid fundamentals, watch PE)
→ SALVAGE: Steady but less upside
→ TREATMENT: Wait (structural headwinds)

RECOMMENDATION: Deep-dive on Recycling + Car Washes
```

**Use Case 2: Thesis Validation (Is There Really an Opportunity?)**
```
Question: "Is commercial recycling actually a good thesis or just theoretical?"

Quantitative Analysis (from Scout):
- Universe: 89 businesses in target geography
- Benchmarks: Typical $1.2M revenue, $260K cash flow, 3.2x multiple
- Deal flow: Sufficient (30+ high-probability targets)

Qualitative Analysis (Sentiment/Regulatory):
- Reddit analysis: 47 "thinking about selling" posts (6 months)
  → 72% mention succession concerns
  → 34% mention EPA compliance burden
  → Conclusion: MOTIVATED SELLERS exist

- Forum pain points: "Route optimization," "EPA paperwork," "staffing"
  → 82% are operational problems (we can fix)
  → 18% are structural (commodity pricing volatility)
  → Conclusion: SYSTEMATIZABLE

- Regulatory landscape:
  → CA AB 1234: Mandates commercial recycling (July 2026)
  → TX HB 567: New permit requirements (raises barriers)
  → EPA: Contamination standards tightening (2027)
  → Conclusion: TAILWINDS strong, barriers increasing

THESIS VALIDATION:
✓ Quantitative: Deal flow exists (89 businesses, 30 targets)
✓ Qualitative: Sellers motivated (succession crisis)
✓ Systematizable: 82% of problems are operational
✓ Timing: Strong (regulatory tailwinds incoming)
✓ Moat: Strengthening (barriers to entry rising)

VERDICT: VALIDATED - Proceed with deep dive and owner conversations
```

**Use Case 3: Risk Assessment (What Could Go Wrong?)**
```
Question: "What are the risks with car wash acquisitions?"

Sentiment Intelligence:

Forum Pain Points Analysis:
1. "Real estate dependent - bad location = doomed" (54 mentions)
   - Risk Level: HIGH (structural)
   - Mitigation: Only acquire proven locations (3+ years, traffic data)

2. "Equipment breaks constantly, expensive to fix" (98 mentions)
   - Risk Level: MEDIUM (operational)
   - Mitigation: Build preventive maintenance, parts inventory

3. "PE-backed chains opening everywhere" (31 mentions)
   - Risk Level: MEDIUM (competitive)
   - Mitigation: Focus on express/membership model, avoid competition

4. "Weather kills revenue in winter" (22 mentions)
   - Risk Level: LOW (geographic)
   - Mitigation: Focus on warm climates (SoCal, AZ, TX)

5. "Water/chemical costs rising" (18 mentions)
   - Risk Level: LOW (operational)
   - Mitigation: Water reclaim systems, chemical optimization

Regulatory Intelligence:
- Some cities restricting car wash water usage
- But also: Home washing bans (good for us)
- Zoning: Hard to get new permits (protects existing)

RISK ASSESSMENT:
🔴 HIGH RISK: Location dependency (can't fix)
🟡 MEDIUM RISK: PE competition (structural), equipment (operational)
🟢 LOW RISK: Input costs, weather (manageable)

THESIS ADJUSTMENT:
→ Only acquire in high-traffic locations (proven >3 years)
→ Avoid markets with PE saturation
→ Focus on warm weather geographies
→ Budget for equipment CapEx (10-15% revenue)

VERDICT: Thesis still viable, but be selective on location
```

**Use Case 4: Understanding the Business (Before Deep Dive)**
```
Question: "We've never run a medical waste business. What should we know?"

Forum Deep Dive (r/MedicalWaste, Waste360 forums):

Operator Experience:
- "Route efficiency is EVERYTHING" (highest mention)
  → Insight: This is a logistics/optimization business

- "Compliance is 24/7 stress" (second highest)
  → Insight: Need systems for documentation, audits, tracking

- "Customer retention is high once you have contract"
  → Insight: Sticky revenue, focus on service quality

- "Hard to break into hospital contracts" (established players win)
  → Insight: Acquiring existing contracts is key

- "Pricing pressure from Stericycle, others" (consolidated industry)
  → Insight: Focus on small/medium clinics, not hospitals

What Makes Good Operators:
- GPS tracking, route optimization software
- Meticulous compliance documentation
- Quick response to customer calls
- Regular training on regulations

What Makes Bad Operators:
- Manual routing (inefficient)
- Compliance violations (fines, loss of permits)
- Poor customer service (lose contracts)
- No backup plans (truck breaks, customer churns)

Regulatory Landscape:
- EPA permits (state-level, takes 6-12 months)
- DOT hazmat (federal, strict)
- OSHA (employee safety, training)
- State health departments (facility inspections)

BUSINESS MODEL INSIGHT:
→ This is a ROUTE OPTIMIZATION business with regulatory moat
→ Win by: Better routing, better compliance, better service
→ Lose by: Violations, poor service, inefficiency
→ Moat: Permits + contracts are hard to replicate

THESIS VALIDATION:
✓ Matches our profile (equipment + licensing moat)
✓ Problems are systematizable (routing, compliance)
✓ Sticky revenue (contracts)
⚠ Watch out for: Consolidated industry (Stericycle competition)

NEXT STEPS:
→ Run Scout to find medical waste businesses in target geography
→ Talk to 3-5 operators (informational, not buying yet)
→ Understand: What do permit applications look like? How long?
→ Validate: Is deal flow sufficient? Are owners retiring?
```

**Use Case 5: Market Timing (Now vs. Later?)**
```
Question: "Should we pursue addiction treatment now or wait 2 years?"

Current State Analysis:

Industry Health Trend:
- 2024: Sentiment 67/100
- 2025: Sentiment 63/100
- 2026: Sentiment 61/100
→ Declining trend

Why Sentiment is Declining:
- "Insurance reimbursement rates cut again" (increasing mentions)
- "Medi-Cal rates haven't increased in 5 years" (inflation squeeze)
- "Compliance burden getting worse" (licensing audits up)
- "Staff burnout epidemic" (counselor turnover high)

Regulatory Trajectory:
- Some states increasing oversight (more audits)
- Federal mental health parity enforcement weak
- No meaningful reimbursement increases proposed

Operator Sentiment:
- "Getting out while we can" (increasing)
- "Margins compressed 40% in 3 years" (structural)
- "Can't make the math work anymore" (troubling)

TIMING ANALYSIS:
🔴 Structural headwinds (reimbursement pressure)
🔴 Sentiment worsening (not improving)
🔴 No regulatory catalysts (no positive changes coming)
🟡 Deal flow may increase (distressed sellers) but for bad reasons

VERDICT: WAIT or AVOID
- Problems are becoming MORE structural, not less
- Unless reimbursement rates improve, margins will compress further
- Even systematizing operations won't fix pricing pressure

RECOMMENDATION:
→ Keep monitoring (quarterly intelligence check)
→ If reimbursement landscape changes, re-evaluate
→ For now, focus on industries with tailwinds (recycling, car washes)
```

---

### Success Metrics

**Sentiment Intelligence:**
- Track 5+ industries continuously
- Weekly sentiment scores updated
- Identify 10+ seller signals per month per industry

**Regulatory Intelligence:**
- Monitor 10+ relevant regulations per industry
- Catch 90%+ of relevant legislative changes before they pass
- Identify 2+ regulatory tailwinds per quarter

**Competitive Intelligence:**
- Catalog top 20 pain points per industry
- 80%+ classified as operational (good) vs. structural (bad)
- Systematization score >70 for target industries

**Strategic Impact:**
- Intelligence informs 100% of industry selection decisions
- Identify optimal timing for acquisitions (regulatory events)
- Value creation playbook based on real operator pain points

---

## Competitive Analysis: PE Firm Approach vs. Scout

### How PE Firms Approach Deal Sourcing & Thesis Validation

#### Traditional PE Process (Lower Middle Market / Search Funds)

**Phase 1: Top-Down Industry Research (2-4 weeks)**

**Resources Used:**
- **Industry Research Reports**
  - IBISWorld ($1,500-3,000 per report)
  - Pitchbook market reports
  - McKinsey/BCG industry analyses
  - Trade publications

- **Market Data Providers**
  - Capital IQ (enterprise pricing, ~$30K+/year)
  - PitchBook ($20-40K/year)
  - PrivCo ($10K+/year)
  - D&B Hoovers

- **Human Capital**
  - Junior analyst does research (40-80 hours)
  - Associate reviews and refines
  - Partner validates thesis

**Analysis Framework:**
```
1. Market Sizing
   - TAM (Total Addressable Market)
   - SAM (Serviceable Addressable Market)
   - SOM (Serviceable Obtainable Market)

   Example:
   "Commercial HVAC services is a $15B market
    Fragmented (top 10 = 20% share)
    SoCal represents ~8% = $1.2B
    Target: 1-2% market share = $12-24M revenue"

2. Industry Structure Analysis (Porter's 5 Forces)
   - Competitive rivalry
   - Threat of new entrants
   - Supplier/buyer power
   - Threat of substitutes
   - Regulatory environment

3. Growth Drivers & Trends
   - Industry growth rate (past 5 years, projected 5 years)
   - Regulatory tailwinds/headwinds
   - Technology disruption
   - Demographic shifts

4. Fragmentation Analysis
   - # of competitors
   - Market share concentration
   - Roll-up potential (can we consolidate?)
```

**Output:** 30-50 page industry thesis document

**Cost:** $10-20K in analyst time + $2-5K in data/reports

**Time:** 2-4 weeks

---

**Phase 2: Deal Sourcing (Ongoing, 3-12 months)**

**Primary Channels:**

**1. Business Brokers (40-50% of deal flow)**
```
Approach:
- Build relationships with brokers (Sunbelt, Transworld, local)
- Get on their "buyer list" for target industries
- Review listings as they come
- Move quickly on good opportunities

Pros:
✓ Curated opportunities (brokers pre-qualify)
✓ Seller is ready (actively marketed)
✓ Professional process (LOI, DD, closing)

Cons:
✗ Competitive (multiple bidders)
✗ Higher valuations (broker fees = 10-12%)
✗ Limited universe (only actively selling)
✗ Retail pricing (market knows it's for sale)
```

**2. Investment Bankers (20-30% of deal flow)**
```
Approach:
- Relationship-driven (need credibility, track record)
- Proprietary deal flow (off-market processes)
- Invited to "managed auctions"

Pros:
✓ Larger, higher-quality businesses
✓ Professional sellers (clean financials)
✓ Structured process

Cons:
✗ Highly competitive (5-10+ bidders typical)
✗ Higher valuations (4-6x EBITDA)
✗ Requires credibility (not accessible to first-time buyers)
✗ Larger check sizes ($5M+)
```

**3. Direct Outreach (20-30% of deal flow)**
```
Approach:
- Build target list (manual research, databases)
- Cold outreach (letters, calls, emails)
- Relationship cultivation (6-18 months)
- "We're buyers in your industry"

Pros:
✓ Off-market (no competition)
✓ Better pricing (3-4x vs. 5-6x)
✓ Control timing (seller moves at their pace)

Cons:
✗ Time-intensive (months of cultivation)
✗ Low conversion (1-2% response, <0.5% close)
✗ Manual research (building target lists is slow)
✗ Requires patience (long sales cycles)
```

**4. Industry Conferences/Networks (5-10%)**
```
Approach:
- Attend trade shows
- Join industry associations
- Build operator relationships
- "Buyer of choice" positioning

Pros:
✓ Trusted relationships
✓ Industry expertise gained
✓ Deal flow from insiders

Cons:
✗ Slow (relationship building takes years)
✗ Not scalable
✗ Geography-limited
```

**Typical PE Sourcing Metrics:**
```
- 100 opportunities reviewed
- 20 management meetings
- 10 LOIs submitted
- 5 enter due diligence
- 1-2 close

Timeline: 6-12 months per acquisition
Cost: $50-100K in time + expenses
```

---

**Phase 3: Initial Screening (1-2 weeks per opportunity)**

**When a deal comes in:**

**Quick Screen (1-2 days):**
```
Analyst reviews:
- CIM (Confidential Information Memorandum)
- Financials (P&L, balance sheet, 3 years)
- Customer concentration
- Owner involvement
- Reason for sale

Red flags:
✗ Customer concentration >25%
✗ Revenue declining
✗ Owner IS the business (can't transition)
✗ Regulatory issues
✗ Litigation
```

**Deeper Analysis (1 week):**
```
If passes screen:
- Build financial model (projections)
- Compare to industry benchmarks (where do they get these? IBISWorld, their own data)
- Estimate valuation range
- Identify value creation levers
- Preliminary diligence questions

Output: Investment memo (10-20 pages)
Recommendation: Pass, More Info, or Pursue
```

**Management Meeting:**
```
If pursuing:
- Meet owner/management
- Tour facility
- Ask operational questions
- Assess cultural fit
- Understand seller motivation

Goal: Build conviction or kill deal early
```

---

**Phase 4: LOI & Due Diligence (4-8 weeks)**

**LOI (Letter of Intent):**
```
Terms:
- Purchase price: $X (based on valuation model)
- Structure: Cash vs. seller note vs. earnout
- Due diligence period: 30-60 days
- Exclusivity: 60-90 days
- Key contingencies

Negotiation:
- Back and forth on price, terms
- Goal: Lock up deal, enter exclusivity
```

**Due Diligence (4-8 weeks):**
```
Teams involved:
- Financial DD: Accounting firm does QofE (Quality of Earnings)
  - Normalize EBITDA (add-backs, one-time items)
  - Validate revenue recognition
  - Identify working capital needs
  - Cost: $15-50K

- Legal DD: Law firm reviews
  - Corporate structure, contracts
  - Leases, real estate
  - Litigation, liabilities
  - Environmental (Phase I/II if applicable)
  - Cost: $20-50K

- Commercial DD: Internal team + consultants
  - Customer interviews (top 10-20 customers)
  - Competitive analysis
  - Market validation
  - Pricing analysis
  - Cost: $10-30K in time

- Operational DD: Internal team
  - Process mapping
  - IT systems review
  - HR/employee assessment
  - Equipment/asset condition
  - Cost: Internal time

Total DD Cost: $50-150K
Total Time: 4-8 weeks
```

**Outcome:**
- Confirm or adjust valuation
- Identify value creation opportunities
- Build 100-day plan
- Proceed to close or walk

---

**Phase 5: Value Creation Planning (During DD)**

**Typical PE Value Creation Levers:**

**1. Revenue Growth**
```
- Geographic expansion
- New services/offerings
- Sales/marketing professionalization
- Pricing optimization
- Customer acquisition
```

**2. Operational Efficiency**
```
- Process improvements
- Technology/software implementation
- Labor optimization
- Supply chain improvements
- Vendor consolidation
```

**3. Financial Engineering**
```
- Add-on acquisitions (roll-up)
- Debt refinancing
- Working capital optimization
- Tax structuring
```

**4. Professionalization**
```
- Hire professional management
- Implement KPIs/dashboards
- Formalize processes (SOPs)
- Upgrade systems (ERP, CRM)
- Board governance
```

**100-Day Plan:**
```
Output: Detailed plan for first 100 days
- Quick wins (immediate improvements)
- Key hires (GM, CFO, etc.)
- Systems to implement
- Metrics to track

Goal: Set foundation for 3-5 year value creation
```

---

### PE Firm Advantages

**What They Do Better:**

**1. Access to Capital**
```
- Can write $5-50M+ checks
- Debt financing relationships (banks)
- Can do roll-ups (buy 5-10 businesses)
```

**2. Expertise & Networks**
```
- Industry experts (consultants, advisors)
- Operational partners (interim CEOs, CFOs)
- Legal/accounting firms on retainer
- Board members with domain expertise
```

**3. Professionalization**
```
- Know how to build management teams
- Systems implementation (ERP, BI tools)
- Best practices from portfolio companies
- Playbooks for common issues
```

**4. Deal Experience**
```
- Closed 50-100+ deals (pattern recognition)
- Negotiation expertise
- DD checklists (know what to look for)
- Understand seller psychology
```

**5. Exit Planning**
```
- Know what strategics/PE will pay for
- Build businesses for resale (multiple expansion)
- Relationships with exit buyers
```

---

### PE Firm Disadvantages (Your Opportunities)

**What They DON'T Do Well:**

**1. Speed (They're Slow)**
```
PE Timeline:
- Industry research: 2-4 weeks
- Deal sourcing: 3-12 months
- Screening: 1-2 weeks per deal
- DD: 4-8 weeks
- Total: 6-18 months per acquisition

Scout Timeline:
- Industry research: 10 minutes
- Universe discovery: 5 minutes
- Benchmarking: 3 minutes
- Intelligence: 2 hours (manual)
- Total: 1 day for thesis validation

→ 50-100x faster
```

**2. Cost (They're Expensive)**
```
PE Cost per Thesis:
- Analyst time: $10-20K
- Industry reports: $2-5K
- Data subscriptions: $30-40K/year
- DD per deal: $50-150K
- Total: $100K+ per acquisition

Scout Cost per Thesis:
- Google Maps API: $5
- Web scraping: Free
- Intelligence research: 2 hours manual
- Total: <$10 for thesis validation

→ 10,000x cheaper for exploration
```

**3. Comprehensiveness (Blind Spots)**
```
PE Approach:
- Only see what brokers/bankers show them
- Only find businesses actively for sale
- Miss 80-90% of universe (not listed)
- Rely on intermediaries (filtered view)

Scout Approach:
- Find ALL businesses (Google Maps)
- Off-market universe (not just listings)
- Direct data (not filtered by brokers)
- 100% coverage of geography

→ 10x more comprehensive
```

**4. Small Deals (Not Economical)**
```
PE Economics:
- Need $5M+ EBITDA to justify fees
- Can't spend $100K DD on $500K deal
- Pass on small businesses (not worth time)

Your Economics:
- $500K deals are perfect size
- Scout makes small deals economical
- Automation reduces research costs
- Can evaluate 10x more opportunities

→ You can compete where they can't
```

**5. Operational Distance**
```
PE Approach:
- Hire consultants to understand operations
- Rely on management teams
- Board-level involvement only
- Don't get hands dirty

Your Approach:
- Will operate businesses directly
- Deeply understand operations
- Implement systems yourself
- Hands-on value creation

→ You can create value they can't
```

**6. Technology/Automation**
```
PE Approach:
- Manual research (analysts in Excel)
- Manual outreach (spreadsheets)
- Relationship-dependent (not scalable)
- Legacy processes

Your Approach:
- Automated research (APIs, scrapers)
- Data-driven (benchmarks, intelligence)
- Scalable (can evaluate 10 industries/day)
- Modern tech stack

→ You have a tech advantage
```

---

### Scout vs. PE Firm: Comparison Table

| Dimension | PE Firm | Scout (You) | Winner |
|-----------|---------|-------------|--------|
| **Industry Research** | 2-4 weeks, $10-20K | 10 minutes, <$10 | 🏆 Scout (100x faster, 1000x cheaper) |
| **Universe Coverage** | 10-20% (only listings) | 100% (all businesses) | 🏆 Scout (complete coverage) |
| **Deal Flow Sources** | Brokers, bankers, conferences | Direct research, off-market | 🏆 Scout (proprietary data) |
| **Speed to Thesis** | 6-12 months | 1 day | 🏆 Scout (50-100x faster) |
| **Cost per Thesis** | $100K+ | <$10 | 🏆 Scout (10,000x cheaper) |
| **Deal Size Focus** | $5M+ EBITDA | $100K-500K EBITDA | 🏆 Scout (underserved market) |
| **Capital Access** | $50M+ funds | Personal/SBA | 🏆 PE (more capital) |
| **Expertise/Networks** | Deep (consultants, advisors) | Building | 🏆 PE (more experience) |
| **DD Capabilities** | Professional (QofE, legal) | DIY + professionals | 🏆 PE (more thorough) |
| **Operational Involvement** | Hands-off (board level) | Hands-on (operator) | 🏆 Scout (closer to business) |
| **Technology** | Legacy/manual processes | Modern (APIs, automation) | 🏆 Scout (tech advantage) |
| **Exit Planning** | Sophisticated (strategic buyers) | Building | 🏆 PE (exit expertise) |

---

### What You Can Learn from PE

**Best Practices to Adopt:**

**1. Structured Thesis Development**
```
PE Approach: Industry research → market sizing → fragmentation analysis
Your Approach: Scout quantitative + sentiment intelligence → validation

Adopt:
✓ Structured frameworks (health score, systematization score)
✓ Comparative analysis (rank industries objectively)
✓ Risk assessment (identify deal-breakers early)
```

**2. Screening Rigor**
```
PE Approach: Quick screen (1-2 days) kills 80% of deals
Your Approach: Intelligence scoring flags red flags

Adopt:
✓ Clear go/no-go criteria
✓ Red flag checklist
✓ Kill bad opportunities fast (don't chase losers)
```

**3. Value Creation Planning**
```
PE Approach: Identify 3-5 levers during DD
Your Approach: Sentiment intelligence reveals pain points

Adopt:
✓ 100-day plan template
✓ Systematization roadmap
✓ KPI dashboards from day 1
```

**4. Process Discipline**
```
PE Approach: Checklists, stage gates, investment committee
Your Approach: Systematize your own process

Adopt:
✓ Due diligence checklist
✓ Financial model template
✓ Decision criteria (when to pursue vs. pass)
```

**5. Portfolio Thinking**
```
PE Approach: Build portfolio of 5-10 businesses
Your Approach: Acquire 1-2/year, build platform

Adopt:
✓ Portfolio allocation (diversify by industry/geography)
✓ Centralized back-office (accounting, HR)
✓ Roll-up strategy (consolidate fragmented industries)
```

---

### What PE Firms Get Wrong (Your Advantages)

**Where You Can Beat Them:**

**1. They Overpay**
```
PE Reality:
- Brokers = competitive auctions = 5-6x EBITDA
- Deal fatigue (need to close deals, pressure to deploy capital)
- Multiple expansion thesis (need to pay up to sell higher)

Your Reality:
- Off-market = negotiated = 3-4x EBITDA
- Patient capital (no fund timeline pressure)
- Hold long-term (don't need exit in 5 years)

→ You can buy 30-40% cheaper
```

**2. They Miss Small Deals**
```
PE Reality:
- $500K EBITDA business = too small
- DD costs $50-150K = not economical
- Analysts cost $100K/year = can't justify

Your Reality:
- $500K EBITDA = perfect size ($1.5M valuation)
- Scout DD costs <$10 for exploration
- You are the analyst (sweat equity)

→ 90% of small businesses are yours to target
```

**3. They're Slow**
```
PE Reality:
- Investment committee approvals
- Multiple layers (analyst → associate → VP → partner)
- Institutional processes (slow)

Your Reality:
- You are the decision-maker
- Move fast when you see opportunity
- Nimble (can pivot quickly)

→ You can close deals they lose to speed
```

**4. They Rely on Brokers**
```
PE Reality:
- Wait for brokers to bring deals
- See same deals as 5-10 competitors
- Pay retail pricing

Your Reality:
- Scout finds off-market universe
- Direct outreach (no intermediaries)
- Wholesale pricing (no broker fees)

→ You see opportunities they never find
```

**5. They Don't Understand Operations**
```
PE Reality:
- Hire consultants to understand business
- Rely on incumbent management
- "Strategic" not operational

Your Reality:
- You will run the business
- Deep operational understanding
- Hands-on improvements

→ You can create value they can't
```

---

### Scout's Competitive Positioning

**Your Unfair Advantages:**

```
1. SPEED
   PE: 6-12 months to validate thesis
   You: 1 day with Scout
   → Test 10 industries in time PE tests 1

2. COST
   PE: $100K+ per acquisition process
   You: <$10 for thesis validation
   → Evaluate 100 theses for cost of 1 PE deal

3. COVERAGE
   PE: 10-20% of market (only listings)
   You: 100% of market (all businesses)
   → 5-10x more deal flow

4. SIZE
   PE: Won't touch <$5M EBITDA
   You: Target $100K-500K EBITDA
   → 90% of market is uncontested

5. TECHNOLOGY
   PE: Manual, legacy processes
   You: Automated, data-driven
   → Tech moat (hard for PE to replicate)
```

**Where You're Building a Moat:**

```
→ Proprietary data (universe databases)
→ Benchmark intelligence (accumulated over time)
→ Sentiment analysis (Reddit/forum insights)
→ Regulatory monitoring (legislative arbitrage)
→ Industry expertise (operational playbooks)

5 years from now:
- You have data on 10,000+ businesses
- You have benchmarks on 50+ industries
- You have playbooks for each business type
- You know which operators are retiring (relationships)
- PE firms can't replicate this data advantage
```

---

## Data Sources: Unit Economics & Benchmarks

### Overview: The Benchmark Challenge

**The Problem:**
Small businesses don't disclose financials publicly. Unlike public companies with SEC filings, you can't just look up a car wash's revenue or margins.

**The Opportunity:**
Multiple data sources reveal unit economics indirectly. By triangulating across sources, you can build accurate benchmarks.

**Strategy:**
1. Start with free/cheap sources (BizBuySell, FDDs)
2. Validate with paid sources (IBISWorld, RMA)
3. Supplement with alternative sources (forums, case studies)
4. Accumulate proprietary data over time (your acquisitions)

---

### TIER 1: Free & Essential Sources

#### 1. **Business-For-Sale Listings** (FREE, HIGH VALUE)

**BizBuySell.com**
```
What you get:
- Asking price
- Revenue (gross sales)
- Cash flow (SDE or EBITDA)
- Year established
- # of employees
- Brief description
- Sometimes: Equipment details, lease terms

Quality:
✓ Real businesses currently for sale
✓ Owner-verified financials (brokers check)
✓ 100,000+ active listings
⚠ Asking price ≠ sale price (typically sell for 10-20% less)
⚠ Financials may be "optimistic" (add-backs)

How to use:
1. Search by industry keyword
2. Filter by geography if needed
3. Export to spreadsheet (manual or scrape)
4. Calculate distributions (median revenue, cash flow, multiple, margin)
5. Build benchmark per industry

Example - Car Washes:
Search: "car wash"
Found: 47 listings
Median revenue: $1,350,000
Median cash flow: $425,000 (31% margin)
Median asking price: $1,487,500 (3.5x multiple)

Cost: FREE (scraping is gray area, but data is public)
Coverage: Excellent for most industries
Update frequency: Daily (new listings)
```

**BizQuest.com**
```
Similar to BizBuySell, smaller dataset
- ~30,000 listings vs. 100,000
- Use as supplemental source
- Sometimes has listings not on BizBuySell

Cost: FREE
```

**LoopNet.com (for real estate-heavy businesses)**
```
Commercial real estate listings
- Car washes (real estate included)
- Storage facilities
- Industrial properties
- Sometimes includes business financials

Cost: FREE
```

---

#### 2. **Closed Deal Data** (FREE, HIGH VALUE)

**SMB Deal Machine (smbdealmachine.com)**
```
What you get:
- Actual sale prices (closed deals)
- Revenue and cash flow (if disclosed)
- Industry type
- Geography
- Date of sale

Quality:
✓ Real closed deals (not asking prices)
✓ More accurate pricing (actual transactions)
⚠ Limited data per listing (many fields missing)
⚠ Smaller dataset than BizBuySell

How to use:
- Search by industry
- Filter by deal size, geography
- Export data for benchmarking
- Use as validation against BizBuySell (do asking prices match sale prices?)

Cost: FREE (some data), $49/mo for full access
Coverage: Growing database, ~10K deals
```

**Axial.net**
```
M&A platform for small/mid-market
- Some closed deal data
- More focused on $5M+ deals
- Limited for micro-businesses

Cost: FREE to browse
```

---

#### 3. **Franchise Disclosure Documents (FDDs)** (FREE, GOLD MINE)

**FranchiseDisclosures.com, Franchisor websites**
```
What you get:
- Item 19: Financial Performance Representations
- Actual franchisee unit economics:
  • Average revenue per location
  • Revenue ranges (top 25%, median, bottom 25%)
  • Sometimes: COGS, labor costs, rent
  • Sometimes: EBITDA margins
- Initial investment costs (equipment, real estate)
- Franchisee count (how many units)

Quality:
✓✓✓ BEST DATA for unit economics
✓ Audited/verified (FTC regulation)
✓ Shows distributions (not just averages)
✓ Comparable to independent businesses
⚠ Only ~30% of franchisors disclose Item 19
⚠ May be optimistic (best performers)

How to use:
1. Find franchise brands in your target industry
   - Car washes: Mister Car Wash, Zips, Tommy's Express
   - Addiction treatment: AAC (American Addiction Centers)
   - Industrial laundry: Cintas, Unitex
2. Download FDD (Google "[brand name] FDD")
3. Jump to Item 19
4. Extract unit economics data
5. Apply to independent businesses as baseline

Example - Express Car Washes (Zips FDD):
Item 19 shows:
- Top 25% locations: $2.1M revenue, $672K EBITDA (32%)
- Median locations: $1.4M revenue, $420K EBITDA (30%)
- Bottom 25%: $950K revenue, $247K EBITDA (26%)

Insight:
→ Independent car washes likely have similar economics
→ Use as benchmark for estimating independents

Cost: FREE (FDDs are public disclosure)
Coverage: Excellent for franchised industries
Update frequency: Annually (FDDs updated yearly)
```

**Best Industries with FDD Data:**
```
✓ Car washes (many franchises)
✓ Quick-service restaurants (not your focus, but reference)
✓ Fitness/gyms (not your focus)
✓ Senior care (reference for treatment centers)
✓ Home services (HVAC, plumbing - franchises exist)
✓ Automotive (quick lube, transmission, etc.)

Limited FDD data:
✗ Recycling/waste (few franchises)
✗ Auto salvage (no franchises)
✗ Most industrial services (B2B, not franchised)
```

---

#### 4. **Industry Association Reports** (FREE to CHEAP)

**Trade Associations:**
```
Most industries have trade groups that publish benchmarks

Examples:

Car Washes:
- International Carwash Association (ICA)
- Reports: "Industry Statistics & Trends"
- Data: Average revenue per location, labor %, chemical costs
- Cost: FREE for members ($500-1000/year membership)

Waste Management:
- National Waste & Recycling Association (NWRA)
- Reports: Industry benchmarks, trends
- Cost: Member-only

Addiction Treatment:
- National Association of Addiction Treatment Providers (NAATP)
- Reports: Reimbursement rates, occupancy rates
- Cost: Member-only

Auto Recyclers:
- Automotive Recyclers Association (ARA)
- Reports: Industry benchmarks
- Cost: $300-500/year membership

How to find:
1. Google "[industry] trade association"
2. Look for "Industry Reports" or "Benchmarks"
3. Join as member if valuable ($300-1000/year)
4. Download reports

Quality:
✓ Industry-specific (very relevant)
✓ Aggregated from many businesses
⚠ Often high-level (averages, not distributions)
⚠ May require membership to access

Cost: FREE to $1,000/year per industry
```

---

#### 5. **SBA Loan Data** (FREE, LIMITED)

**SBA.gov - 7(a) and 504 Loan Data**
```
What you get:
- Loan amounts by industry (NAICS code)
- Average loan size
- Approval rates
- Sometimes: Revenue ranges (to qualify)

How it helps:
- Typical loan = 80-90% of purchase price
- Reverse engineer: If avg loan is $600K, avg business = $667-750K

Quality:
⚠ Aggregated only (no individual deals)
⚠ Not all businesses use SBA loans
✓ Large dataset (trends are accurate)

Cost: FREE
Use: Supplemental validation
```

---

### TIER 2: Paid Data Sources (ROI Varies)

#### 6. **Industry Research Reports**

**IBISWorld ($1,500-3,000 per report)**
```
What you get:
- Industry size, growth rate
- Market share concentration
- Profit margins by segment
- Cost structure (% COGS, labor, rent, etc.)
- Benchmarks:
  • Revenue per employee
  • Revenue per establishment
  • Gross margin, EBITDA margin

Quality:
✓ Comprehensive industry analysis
✓ Well-researched (analysts compile data)
✓ Cost structure breakdowns useful
⚠ Focuses on larger businesses (may not apply to small)
⚠ Expensive ($1,500-3,000 per report)

Best for:
- Understanding industry dynamics
- Validating cost structures
- Market sizing

ROI:
🟡 MEDIUM - Good for initial research, but expensive
→ Use for 2-3 core industries, not all

Example - Car Washes (IBISWorld):
Report shows:
- Industry revenue: $11B
- Average profit margin: 28%
- Revenue per employee: $85K
- Cost structure: Labor 18%, Chemicals 8%, Utilities 12%

Cost: $1,500-3,000 per report
Coverage: 700+ industries
```

**Statista**
```
Similar to IBISWorld, more affordable
- Basic industry data: $49/mo subscription
- Premium reports: $500-1,000 each

Quality: Good for high-level trends
Cost: $49-99/mo
```

---

#### 7. **Financial Benchmarking Databases**

**RMA Annual Statement Studies ($200-400)**
```
What you get:
THE GOLD STANDARD for financial benchmarks

- Financial ratios by industry (NAICS code)
- Broken down by revenue size:
  • $0-1M
  • $1-3M
  • $3-5M
  • etc.
- Metrics include:
  • Gross margin
  • Operating margin
  • Net margin
  • Asset turnover
  • Inventory turns
  • Days receivable
  • Debt/equity ratios
- Percentile distributions (25th, 50th, 75th)

Quality:
✓✓✓ HIGHEST QUALITY financial data
✓ From actual bank loan applications (verified)
✓ Size segmentation (relevant to small businesses)
✓ Percentile distributions (not just averages)

Example - Commercial Waste Collection (NAICS 562111):
$1-3M revenue businesses:
- Gross margin: 38% (median)
- Operating margin: 12% (median)
- Net margin: 5% (median)
- Revenue per employee: $125K

Cost: $200-400 for annual book
Coverage: 800+ industries by NAICS code
Update: Annually
```

**Sageworks (now Abrigo) - Financial benchmarks**
```
Similar to RMA
- $500-1,000/year subscription
- Online access (easier than RMA book)
- Financial ratios, industry benchmarks

Cost: $500-1,000/year
Quality: Excellent (from CPA firm data)
```

**BizMiner ($99-299/year)**
```
What you get:
- Industry financial benchmarks
- Startup costs
- Revenue/profit projections
- Market research data

Quality:
✓ Affordable ($99-299/year)
⚠ Less comprehensive than RMA
⚠ Data quality varies by industry

Best for:
- Budget option for benchmarks
- Startup cost estimates

Cost: $99-299/year
```

**ProfitCents (FREE to $49/mo)**
```
Financial benchmarking for accountants
- Industry profit margins
- Expense ratios
- KPIs by industry

Cost: FREE basic, $49/mo premium
Quality: Good for high-level benchmarks
```

---

### TIER 3: Alternative & Creative Sources

#### 8. **Operator Self-Disclosure** (FREE, HIGH VALUE)

**Reddit Communities**
```
Operators share real numbers

Subreddits:
- r/smallbusiness
- r/entrepreneur
- r/sweatystartup (service businesses)
- Industry-specific subs

Example searches:
"car wash revenue" site:reddit.com
"how much does a car wash make" site:reddit.com

What you find:
"I own 2 express car washes in Texas:
Location 1: $1.8M revenue, $540K net (30%)
Location 2: $1.2M revenue, $360K net (30%)
60% membership, 40% retail"

Quality:
✓ Real operators, real numbers
✓ Often includes specific details (throughput, pricing)
⚠ Self-reported (unverified)
⚠ May be cherry-picked (successful operators share more)
⚠ Fragmented (need to compile many posts)

How to use:
1. Search Reddit for "[industry] + revenue/profit/income"
2. Compile posts with numbers
3. Extract data points
4. Validate against other sources
5. Look for patterns (consistent margins, ratios)

Cost: FREE
Time: 2-4 hours per industry
Value: HIGH (real operator insights)
```

**Operator Forums**
```
Industry-specific forums where operators talk shop

Examples:
- CarwashForum.com
- Waste360 forums
- Auto Recyclers forums

Operators share:
- Revenue benchmarks
- Cost structures (chemicals, labor)
- Throughput (cars per day, tons hauled)
- Pricing strategies

How to find:
Google: "[industry] forum" or "[industry] operator community"

Cost: FREE (some require registration)
Value: HIGH for operational insights
```

**Facebook Groups**
```
Private groups for operators

Examples:
- "Car Wash Owners"
- "Waste Management Professionals"
- "Small Business Owners [Industry]"

Operators share:
- P&L statements (sometimes)
- Revenue updates
- Operational challenges

How to access:
1. Join groups (may need to prove you're in industry)
2. Search post history for financial discussions
3. Ask questions (if you're credible)

Cost: FREE
Value: MEDIUM (less structured than forums)
```

---

#### 9. **Content Creators** (FREE, MIXED VALUE)

**YouTube - "Income Reports"**
```
Some operators create content about their businesses

Search terms:
- "car wash income"
- "how much my car wash makes"
- "[industry] business income report"
- "[industry] profit margins"

Example channels:
- Car wash operators showing monthly revenue
- Service business owners doing "income reports"
- "A day in the life" operational videos

What you learn:
- Revenue ranges
- Unit economics (per car, per route, per job)
- Cost breakdowns (sometimes)
- Operational metrics (cars per day, etc.)

Quality:
✓ Visual (see actual operations)
⚠ Often aspirational/promotional
⚠ May not be representative
⚠ Cherry-picked data

Cost: FREE
Value: MEDIUM (good for context, not hard data)
```

**Podcasts**
```
Business podcasts interview operators

Examples:
- "Small Business War Stories"
- "The $100 MBA Show"
- Industry-specific podcasts

Operators discuss:
- How they got started
- Revenue/profit when they sold
- Operational challenges
- Unit economics (sometimes)

How to find:
1. Search Apple Podcasts: "[industry] business"
2. Listen for financial disclosures
3. Take notes on numbers mentioned

Cost: FREE
Value: LOW to MEDIUM (inconsistent data)
```

---

#### 10. **Case Studies & Success Stories** (FREE)

**SBA.gov Case Studies**
```
SBA publishes success stories
- Businesses that used SBA loans
- Sometimes disclose revenue, growth
- Industry variety

Cost: FREE
Value: LOW (limited financial detail)
```

**Lender Case Studies**
```
Equipment lenders, SBA lenders publish case studies

Examples:
- "How we financed a $1.2M car wash acquisition"
- Details: Revenue, loan amount, equipment value

Where to find:
- Bank websites (SBA lender case studies)
- Equipment financing companies

Cost: FREE
Value: MEDIUM (real deal examples)
```

**Broker Success Stories**
```
Business brokers publish closed deals

Example:
"Sold: Express Car Wash in Phoenix
Sale price: $1.8M
Revenue: $1.5M
Cash flow: $475K
Multiple: 3.8x"

Where to find:
- Broker websites (recent sales)
- Broker newsletters

Cost: FREE
Value: MEDIUM (validates pricing)
```

---

#### 11. **Franchise Operations Manuals** (HARD TO GET, HIGH VALUE)

**Operations Manuals (if you can access)**
```
Franchisors give franchisees operations manuals

What's inside:
- Unit economics expectations
- Pricing guidance
- Cost targets (labor %, COGS %)
- Throughput benchmarks (cars/day, tons/month)
- Staffing models

How to get:
- Buy a franchise (expensive, but you get manual)
- Know a franchisee (ask to see manual)
- Former franchisees (sometimes willing to share)

Quality:
✓✓✓ BEST operational data
✓ Specific targets and benchmarks
⚠ Extremely hard to access (proprietary)

Cost: N/A (can't easily obtain)
Value: VERY HIGH if accessible
```

---

#### 12. **Expert Interviews** (FREE, HIGH VALUE)

**Talk to Industry Insiders**
```
People who know the numbers:

1. Equipment Lenders
   - Finance car wash equipment, waste trucks, etc.
   - See hundreds of businesses
   - Know typical revenue ranges, loan-to-revenue ratios
   - "Typical car wash at $1.5M revenue can support $400K equipment loan"

2. Insurance Brokers
   - Price policies based on revenue
   - See many businesses in industry
   - Know typical revenue by size/type

3. Accountants/Bookkeepers
   - Serve multiple businesses in industry
   - Know typical margins, expenses
   - May share aggregated insights (not client-specific)

4. Industry Consultants
   - Hired to improve businesses
   - See financials of clients
   - Publish benchmarks or share in conversations

5. Business Brokers
   - List businesses for sale
   - Know typical financials for industry
   - May share aggregated data

How to approach:
- Informational interviews
- "I'm researching acquisitions in [industry], trying to understand typical economics"
- Ask for ranges, not specific client data
- Build relationships (they may send you deals later)

Cost: FREE (your time)
Value: HIGH (expert knowledge)
```

---

### TIER 4: Hard-to-Access Sources

#### 13. **Court Records** (FREE but TEDIOUS)

**Divorce Proceedings**
```
Business owners getting divorced disclose financials

What's disclosed:
- Business valuation reports
- P&L statements
- Asset lists
- Revenue, profit

How to access:
- County court records (public)
- PACER (federal courts) - $0.10/page
- Search by business name or owner name

Quality:
✓ Accurate (under oath, verified)
✓ Detailed (full financials)
⚠ Time-consuming to find
⚠ Not scalable

Cost: FREE to cheap
Value: HIGH if you find them, but not scalable
```

**Bankruptcy Proceedings**
```
Businesses in bankruptcy disclose everything

What's disclosed:
- Complete financial statements
- Asset schedules
- Debts, liabilities
- Revenue, expenses

How to access:
- PACER (federal bankruptcy courts)
- Search by business name

Quality:
✓ Complete financial picture
⚠ Businesses are failing (not representative)
⚠ Time-consuming

Cost: $0.10/page on PACER
Value: MEDIUM (interesting but biased sample)
```

---

#### 14. **State/Local Records** (FREE to CHEAP)

**Secretary of State Business Filings**
```
Some states require revenue disclosure

California (example):
- Statement of Information (SI-550)
- Some LLCs/Corps disclose revenue range

What you get:
- Revenue ranges (not exact)
  • $0-$250K
  • $250K-$500K
  • $500K-$1M
  • etc.

How to access:
- State SOS website
- Business entity search

Quality:
⚠ Most states don't require revenue disclosure
⚠ Ranges only (not exact)
✓ Free and public

Cost: FREE
Value: LOW (limited data)
```

**Business License Applications**
```
Some cities require revenue estimates for licensing

What you might find:
- Estimated annual revenue (on application)
- Number of employees

How to access:
- City clerk's office
- Public records request

Quality:
⚠ Self-reported estimates (not actuals)
⚠ May be inflated or deflated
⚠ Hard to access (many jurisdictions)

Cost: FREE to small records request fee
Value: LOW (not worth the effort)
```

---

### Data Source Strategy & ROI

#### Recommended Approach (Prioritized)

**Phase 1: Free Essential Sources (Week 1)**
```
1. BizBuySell scraping (FREE)
   → Benchmark 5-10 industries
   → Time: 4 hours
   → Value: HIGH

2. FDD research (FREE)
   → Find 3-5 franchises per industry
   → Extract Item 19 data
   → Time: 2 hours per industry
   → Value: VERY HIGH (when available)

3. Reddit/Forum mining (FREE)
   → Search operator discussions
   → Compile financial disclosures
   → Time: 2 hours per industry
   → Value: HIGH

Output: Solid benchmarks for 3-5 industries
Cost: $0
Time: 20-30 hours
```

**Phase 2: Validate with Paid Sources (Month 1-2)**
```
4. RMA Annual Statement Studies ($200-400)
   → Buy once, use for all industries
   → Cross-reference with BizBuySell data
   → Time: 1 hour per industry
   → Value: HIGH (validation)

5. Trade association membership (optional)
   → Join 1-2 associations for core industries
   → Cost: $300-1,000/year per association
   → Value: MEDIUM (reports + networking)

Output: Validated benchmarks, confidence levels
Cost: $500-1,500
Time: 10 hours
```

**Phase 3: Expert Interviews (Month 2-3)**
```
6. Talk to industry insiders
   → Equipment lenders (5 interviews)
   → Business brokers (5 interviews)
   → Accountants (3 interviews)
   → Time: 15-20 hours
   → Value: HIGH (expert insights + relationships)

Output: Insider knowledge, deal flow relationships
Cost: $0
Time: 20 hours
```

**Phase 4: Expensive Sources (Only if needed)**
```
7. IBISWorld reports (if gaps remain)
   → $1,500-3,000 per report
   → Only buy for core industries (2-3 max)
   → Value: MEDIUM (expensive, not always small-business relevant)

Output: Industry context, cost structures
Cost: $3,000-9,000
Time: 5 hours
```

---

### Benchmark Quality Matrix

| Source | Cost | Quality | Coverage | Effort | ROI |
|--------|------|---------|----------|--------|-----|
| BizBuySell | Free | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Low | 🏆 Excellent |
| FDDs (Item 19) | Free | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | Medium | 🏆 Excellent |
| Reddit/Forums | Free | ⭐⭐⭐ | ⭐⭐⭐⭐ | Medium | ✅ Good |
| RMA | $200-400 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Low | 🏆 Excellent |
| Expert Interviews | Free | ⭐⭐⭐⭐ | ⭐⭐⭐ | High | ✅ Good |
| IBISWorld | $1,500+ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Low | ⚠️ Medium |
| Trade Associations | $300-1K | ⭐⭐⭐⭐ | ⭐⭐⭐ | Low | ✅ Good |
| SMB Deal Machine | $49/mo | ⭐⭐⭐⭐ | ⭐⭐⭐ | Low | ✅ Good |
| Court Records | Free | ⭐⭐⭐⭐⭐ | ⭐ | Very High | ❌ Poor |

---

### Example: Building Car Wash Benchmarks

**Step-by-Step Process:**

**Step 1: BizBuySell Scraping (1 hour)**
```
Search: "car wash"
Found: 47 listings

Extract:
- Revenue range: $400K - $3.5M
- Cash flow range: $120K - $980K
- Asking price range: $450K - $3.2M

Calculate distributions:
- Median revenue: $1,350,000
- Median cash flow: $425,000
- Median margin: 31% (cash flow / revenue)
- Median multiple: 3.5x (price / cash flow)

Segment by size:
- Small (<$1M revenue): 3.8x multiple, 28% margin
- Medium ($1-2M): 3.5x multiple, 31% margin
- Large (>$2M): 3.2x multiple, 33% margin

Insight: Larger car washes have better margins, lower multiples
```

**Step 2: FDD Research (1 hour)**
```
Find franchise brands:
1. Mister Car Wash (public company, no FDD)
2. Zips Car Wash (FDD available)
3. Tommy's Express (FDD available)

Download Zips FDD, find Item 19:

Top 25% locations (2023 data):
- Average revenue: $2,148,000
- Average EBITDA: $687,360 (32%)

Median locations:
- Average revenue: $1,412,000
- Average EBITDA: $423,600 (30%)

Bottom 25%:
- Average revenue: $952,000
- Average EBITDA: $247,520 (26%)

Validation:
→ BizBuySell medians match Zips franchise medians
→ Margin range: 26-32% (consistent)
→ Confidence: HIGH
```

**Step 3: Reddit Mining (1 hour)**
```
Search: "car wash revenue" site:reddit.com

Found 12 posts with numbers:

Post 1 (r/sweatystartup):
"I own 2 express car washes in Texas:
- Location 1: $1.8M revenue, $540K net
- Location 2: $1.2M revenue, $360K net
- Both are 60% membership, 40% retail"

Post 2 (r/Entrepreneur):
"My car wash did $95K last month ($1.14M annual run rate)
Net profit around $28K/month ($336K annual, 29% margin)"

Post 3 (r/smallbusiness):
"Sold my car wash after 10 years:
$1.5M revenue, $420K SDE (28% margin)
Sold for $1.4M (3.3x multiple)"

Compile 12 posts:
- Revenue range: $850K - $2.1M
- Margin range: 26% - 35%
- Multiple range: 3.0x - 4.2x

Validation:
→ Consistent with BizBuySell and FDD data
→ Confidence: HIGH
```

**Step 4: RMA Validation (30 min)**
```
Look up NAICS 811192 (Car Washes)

RMA data ($1-3M revenue segment):
- Gross profit margin: 62%
- Operating expenses: 35%
- EBITDA margin: 27%

Compare to our data:
- Our median: 31% (slightly higher than RMA 27%)
- Could be: Express washes more profitable than full-service
- Or: RMA includes lower-margin businesses

Adjustment:
→ Use 27-31% range (be conservative)
→ Confidence: HIGH
```

**Step 5: Expert Interview (1 hour)**
```
Call equipment lender (Car Wash Loans Inc.)

Questions:
Q: "What's typical revenue for express car washes you finance?"
A: "$1-2M for most, $2-3M for high-traffic locations"

Q: "What debt-service coverage ratio do you look for?"
A: "1.25x minimum, so if loan payment is $200K/year, need $250K+ cash flow"

Q: "What's typical loan as % of revenue?"
A: "We'll lend up to 80% of purchase price, typical purchase = 3-4x cash flow"

Validation:
→ Confirms 3-4x multiple range
→ Confirms $1-2M revenue typical
→ Confirms ~30% margins (if $1.5M revenue → $450K cash flow → 30%)

Confidence: VERY HIGH
```

**Final Benchmark:**
```
CAR WASHES (Express, membership model)

Typical Business:
- Revenue: $1,200,000 - $1,500,000 (median: $1,350,000)
- Cash Flow (EBITDA): $360,000 - $450,000 (median: $405,000)
- Margin: 27% - 31% (median: 30%)
- Multiple: 3.2x - 3.8x (median: 3.5x)
- Valuation: $1,150,000 - $1,700,000 (median: $1,418,000)

By Size Segment:
Small (<$1M revenue):
- Cash flow: $240K - $300K (28% margin)
- Valuation: $900K - $1.2M (3.8x multiple)

Medium ($1-2M revenue):
- Cash flow: $360K - $580K (31% margin)
- Valuation: $1.3M - $2.0M (3.5x multiple)

Large (>$2M revenue):
- Cash flow: $620K - $990K (33% margin)
- Valuation: $2.0M - $3.2M (3.2x multiple)

Operational Benchmarks:
- Cars washed per day: 150-250 (from forums)
- Membership %: 50-70% of revenue
- Labor cost: 18-22% of revenue (from FDD)
- Chemical cost: 8-10% of revenue
- Utilities: 10-12% of revenue

Confidence Level: VERY HIGH
Sample Size: 47 BizBuySell listings + 2 FDDs + 12 Reddit posts + RMA data
Sources: 4 independent sources, all consistent

Last Updated: 2026-02-16
```

---

## Risks & Mitigation

### Risk 1: Data Quality from Web Scraping
**Risk:** BizBuySell/SMB Deal Machine change site structure, breaking scrapers

**Impact:** High - Cannot build benchmarks without deal data

**Mitigation:**
- Build resilient scrapers with fallbacks
- Regular monitoring and updates
- Have multiple data sources (BizBuySell + SMB Deal Machine)
- Manual fallback: use cached benchmark data

---

### Risk 2: Google Maps API Cost Overruns
**Risk:** High-volume usage exceeds budget

**Impact:** Medium - System becomes too expensive to use

**Mitigation:**
- Implement cost tracking and warnings
- Set per-search budget limits
- Cache results (reuse for geographic expansion)
- Rate limiting to prevent runaway costs

---

### Risk 3: Benchmark Sample Size Too Small
**Risk:** Some industries have <10 deals available

**Impact:** Medium - Benchmarks unreliable for exotic industries

**Mitigation:**
- Set minimum sample size threshold (10 deals)
- Provide confidence scoring (low confidence warning)
- Allow user to proceed with caveat
- Expand to broader industry categories if needed

---

### Risk 4: Estimated Metrics Inaccurate
**Risk:** Review count doesn't correlate well with revenue

**Impact:** Medium - Target quality suffers if estimates are wrong

**Mitigation:**
- Use benchmark calibration (not absolute estimates)
- Provide confidence ranges (±30%)
- Focus on relative ranking (not absolute values)
- Validate with user feedback (improve over time)

---

### Risk 5: User Misinterprets Data
**Risk:** User treats estimates as fact, makes poor decisions

**Impact:** High - Damages user trust and outcomes

**Mitigation:**
- Clear labeling of estimates vs. facts
- Always show confidence levels
- Provide ranges instead of point estimates
- Educational documentation on limitations
- Emphasize estimates are for prioritization, not valuation

---

## Open Questions

### Q1: Data Source Access
- **Question:** Do we have legal access to scrape BizBuySell and SMB Deal Machine?
- **Impact:** Critical - Core functionality depends on this
- **Action:** Review ToS, consult legal if needed, identify alternative sources

### Q2: Benchmark Freshness
- **Question:** How often do benchmarks need to be refreshed?
- **Impact:** Medium - Stale data reduces accuracy
- **Action:** Monitor benchmark stability, establish refresh cadence (quarterly?)

### Q3: Geographic Scope
- **Question:** Should MVP support only US, or international?
- **Impact:** Low - Can start with US only
- **Action:** Start with US, add international in Phase 2+ if needed

### Q4: Industry Taxonomy
- **Question:** How do we standardize industry names (HVAC vs. air conditioning vs. heating)?
- **Impact:** Medium - Affects search quality and benchmark matching
- **Action:** Build industry synonym mapping, allow user to provide terms

### Q5: Multi-User Support
- **Question:** Does this need to support teams (shared data, collaboration)?
- **Impact:** Low for MVP - Can be single-user initially
- **Action:** Design data models to support multi-user in future

---

## Appendix: Example Outputs

### Example 1: Universe Snapshot Summary
```
HVAC Contractors - Arcadia, CA (20-mile radius)
Generated: 2026-02-14 10:30:00
Execution Time: 4m 32s | Cost: $4.25

UNIVERSE SUMMARY:
✓ Total businesses found: 118
✓ With website: 89 (75%)
✓ With phone: 115 (97%)
✓ Average rating: 4.3 ⭐
✓ Average reviews: 67

BY CITY:
• Arcadia: 45 businesses
• Pasadena: 38 businesses
• Monrovia: 22 businesses
• Temple City: 13 businesses

BY RATING:
• Excellent (4.5+): 42 businesses
• Good (4.0-4.5): 51 businesses
• Average (3.5-4.0): 18 businesses
• Poor (<3.5): 7 businesses

NEXT STEPS:
→ Run Market Calibrator to build HVAC benchmark
→ Review top-rated businesses for immediate outreach
→ Export to CSV for mail merge
```

### Example 2: Market Benchmark Summary
```
HVAC Contractors - Market Benchmark
Generated: 2026-02-14 10:33:00
Execution Time: 2m 47s

DATA SOURCES:
• BizBuySell: 23 active listings (Aug 2025 - Feb 2026)
• SMB Deal Machine: 8 closed deals (Jun 2024 - Nov 2025)
• Total sample: 31 deals

TYPICAL HVAC BUSINESS:
Revenue: $1,150,000 (median)
Cash Flow: $241,500 (21% margin)
Valuation Multiple: 3.2x
Estimated Price: $772,800

DISTRIBUTIONS:
Revenue:
  P25: $850K | Median: $1.15M | P75: $1.6M | P90: $2.1M

Multiple:
  P25: 2.8x | Median: 3.2x | P75: 3.8x | P90: 4.2x

Margin:
  P25: 17% | Median: 21% | P75: 26% | P90: 32%

CONFIDENCE: HIGH (31 deals analyzed)

INSIGHTS:
• Small businesses (<$850K revenue) typically sell for $400-500K
• Medium businesses ($850K-$1.6M) typically sell for $600K-$1.2M
• Large businesses (>$1.6M) typically sell for $1M-$2M+
• Multiples range 2.8x-4.2x (median 3.2x)
• Margins typically 17%-32% (median 21%)
```

### Example 3: Deal Flow Analysis
```
DEAL FLOW ANALYSIS: HVAC - Arcadia, CA
Generated: 2026-02-14 10:35:00

UNIVERSE VS. BENCHMARK:
✓ 118 businesses found in universe
✓ 31 deals analyzed for benchmark

ESTIMATED SIZE DISTRIBUTION:
• Small (<$850K revenue): 42 businesses (36%)
• Medium ($850K-$1.6M): 58 businesses (49%)
• Large (>$1.6M): 18 businesses (15%)

QUALITY MATCH:
• Above benchmark rating (>4.3): 67 businesses (57%)
• Below benchmark rating: 51 businesses (43%)

TARGET PRIORITIZATION:
✓ High-probability targets: 45 businesses
  → Good rating + medium size + complete data
  → Estimated valuations: $600K-$1.2M
  → Recommended for immediate outreach

⚠ Medium-probability targets: 52 businesses
  → Mixed signals (good rating but small, or large but lower rating)
  → Estimated valuations: $400K-$2M
  → Recommended for secondary outreach

⚠ Investigation-needed: 21 businesses
  → Outliers (very large or very small)
  → Missing data (no website, few reviews)
  → Requires manual validation

DEAL FLOW VIABILITY: STRONG
→ 45 high-probability targets is sufficient for 6-12 month pipeline
→ Medium size ($850K-$1.6M revenue) is sweet spot
→ Market is mature (many 15+ year old businesses)

RECOMMENDATIONS:
1. Focus initial outreach on 45 high-probability targets
2. Typical deal size: $750K-$1.2M valuation
3. Expect 4-6 serious conversations from 30 contacts (10-15% response rate)
4. Consider expanding to 30-mile radius for more targets
5. Next: Enrich high-probability targets with owner data
```

---

## Approval & Sign-Off

**Product Owner:** ___________________ Date: ___________

**Technical Lead:** ___________________ Date: ___________

**Stakeholder:** ___________________ Date: ___________

---

**Document History:**
- v1.0 (2026-02-14): Initial draft
