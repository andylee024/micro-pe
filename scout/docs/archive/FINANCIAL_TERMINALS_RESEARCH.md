# Financial Terminal Products Research - Exemplars for SMB Deal Sourcing

**Research Date:** February 17, 2026
**Purpose:** Study modern financial terminal products and due diligence platforms to inform Scout's design

---

## Executive Summary

The financial terminal market has undergone massive disruption (2024-2026), shifting from monolithic $32K/year platforms (Bloomberg Terminal) to specialized, AI-powered, cloud-native tools at 1/10th the cost. **Key trend:** Multi-source data aggregation + AI-powered analysis + collaborative workflows + terminal-style UX.

**Relevance to Scout:** These platforms solve the same problem for public markets that Scout solves for SMB acquisitions:
- Aggregate fragmented data sources
- Automate research and due diligence
- Present complex data clearly
- Enable faster, better investment decisions

---

## The Landscape: Bloomberg Terminal Alternatives

### **The Old Guard: Bloomberg Terminal**
- **Cost:** $32,000/year per user
- **Launched:** 1981 (44 years old)
- **Market Position:** Still dominant for institutional investors
- **Problem:** Outdated UX, expensive, overkill for most users

### **The Disruption (2024-2026)**

New wave of tools offering "institutional-quality data at fraction of cost":
- [Koyfin]($468/year), [AlphaSense](enterprise), [FactSet](competitive), [Refinitiv LSEG]($3,600-22,000/year)

**Why this matters for Scout:**
- Proves market for affordable, specialized tools
- Shows how to compete with expensive incumbents (BizBuySell, Grata = $50-150K/year)
- Demonstrates viable product patterns

---

## Exemplar 1: Koyfin - "Bloomberg for Everyone"

**Source:** [Koyfin](https://www.koyfin.com/) | [Comparison vs Bloomberg](https://www.koyfin.com/blog/best-bloomberg-terminal-alternatives/)

### What They Built

**Positioning:** "Swiss army knife of financial research" - rated 9.5/10 for value

**Core Features:**
```
Data Coverage:
├── 100K+ global securities
├── Historical financials (10+ years)
├── Wall Street estimates
├── Company filings & transcripts
├── ETF holdings
└── Economic indicators

Analysis Tools:
├── Equity Screener (5,900+ filters)
├── Advanced charting
├── Custom dashboards
├── Portfolio tracking
└── Comp analysis

Output:
├── Export to Excel
├── Share dashboards
├── Alerts
└── API access
```

**Pricing Model:**
- Free: 2 years historical data, 2 watchlists, limited features
- Pro: $468/year (vs Bloomberg $32K)

### Design Patterns to Borrow for Scout

#### 1. **Multi-Panel Dashboard Layout**
```
┌─────────────────────────────────────────────────────┐
│ Top Nav: Search | Screener | Watchlist | Settings │
├─────────────────────────────────────────────────────┤
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐   │
│ │ Company     │ │ Financials  │ │ Comparables │   │
│ │ Overview    │ │ Charts      │ │ Analysis    │   │
│ │             │ │             │ │             │   │
│ │ - Name      │ │ [Revenue]   │ │ Similar:    │   │
│ │ - Industry  │ │ [Margins]   │ │ • Comp 1    │   │
│ │ │ Location  │ │ [Multiples] │ │ • Comp 2    │   │
│ │ - Rating    │ │             │ │ • Comp 3    │   │
│ └─────────────┘ └─────────────┘ └─────────────┘   │
└─────────────────────────────────────────────────────┘
```

**Scout Application:**
```
┌─────────────────────────────────────────────────────┐
│ Scout: Search | Universe | Benchmarks | Watchlist  │
├─────────────────────────────────────────────────────┤
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐   │
│ │ Business    │ │ Financials  │ │ Competition │   │
│ │ Profile     │ │ (Estimated) │ │ Analysis    │   │
│ │             │ │             │ │             │   │
│ │ ABC Backflow│ │ Revenue:    │ │ 89 Houston  │   │
│ │ Houston, TX │ │ $800K       │ │ competitors │   │
│ │ 4.7⭐ (203) │ │ Margin: 30% │ │             │   │
│ │ Est: $1.2M  │ │ Multiple:3.5│ │ Your rank:  │   │
│ │             │ │             │ │ #23 of 89   │   │
│ └─────────────┘ └─────────────┘ └─────────────┘   │
└─────────────────────────────────────────────────────┘
```

#### 2. **Powerful Screener with 5,900+ Filters**

**Koyfin's approach:**
- Pre-built screens ("High Growth Tech", "Dividend Aristocrats")
- Custom screens with complex logic (AND/OR/NOT)
- Save screens, get alerts when new matches

**Scout Application:**
```
Screener: Find Acquisition Targets

Industry: [HVAC] [Backflow] [Portable Sanitation]
Geography: [Texas] [Houston] [Within 50mi]

Financials:
├── Revenue: $500K - $2M
├── Margin: >25%
└── Multiple: <4.0x

Signals:
├── Owner Age: 60+ ✓
├── Business Age: 15+ years ✓
├── Rating: 4.0+ stars ✓
└── Property Owned: Yes ✓

Results: 12 businesses match
[Save Screen] [Set Alert] [Export CSV]
```

#### 3. **Time-Series Charting**

**Koyfin feature:** Chart any metric over time, compare to peers

**Scout Application:**
```
Review Velocity Chart:

Reviews/Month
  12 ┤         ╭──╮
  10 ┤       ╭─╯  ╰─╮
   8 ┤    ╭──╯      ╰──╮
   6 ┤ ╭──╯            ╰─
   4 ┤─╯
   2 ┤
   0 └───────────────────────→
     2020  2021  2022  2023  2024

Interpretation: Declining review velocity →
possible owner disengagement (acquisition signal!)
```

---

## Exemplar 2: AlphaSense - AI-Powered Research Platform

**Source:** [AlphaSense](https://www.alpha-sense.com/) | [Due Diligence Guide](https://www.alpha-sense.com/solutions/due-diligence-platform/)

### What They Built

**Positioning:** "#8 on CNBC 2025 Disruptor 50" - AI search for institutional investors

**Unique Capability:** Combines multiple data sources in ONE search
```
Single search query across:
├── Company filings (10-K, 10-Q)
├── Earnings transcripts
├── Broker research reports
├── News articles
├── Expert call transcripts
└── Private data feeds

AI Features:
├── Semantic search (understands synonyms)
├── Smart Summaries (auto-generated insights)
├── Sentiment analysis
├── Topic extraction
└── Q&A on documents
```

**Market Penetration:**
- 90% of top asset management firms
- 80% of top investment banks
- 80% of top private equity firms

### Design Patterns to Borrow

#### 1. **Unified Search Across Multiple Sources**

**AlphaSense approach:** One search box → searches everything

**Scout Application:**
```
Search: "backflow testing Houston owner retiring"

Results across all sources:

📍 Google Maps (89 results)
├── ABC Backflow (4.7⭐, owner age 62)
├── Texas Backflow (4.8⭐, founded 1998)
└── [See all 89...]

📊 BizBuySell Benchmarks (18 deals)
├── Median revenue: $650K
├── Median multiple: 3.5x
└── [View details...]

💬 Reddit Discussions (12 threads)
├── r/entrepreneur: "Buying a backflow business AMA"
├── r/smallbusiness: "Backflow testing profitable?"
└── [View all threads...]

🏢 FDD Data (3 franchises)
├── Mosquito Joe (similar service): $285K median
├── Precision Door Service: $420K median
└── [View comparisons...]

💼 PE Ownership (2 roll-ups detected)
├── Holt Services owns 12 TX backflow companies
├── Neighbor Holdings expanding into TX
└── [Competitive intel...]
```

#### 2. **Smart Summaries (AI-Generated)**

**AlphaSense feature:** AI reads 100+ documents, generates executive summary

**Scout Application:**
```
Market Summary: Backflow Testing - Houston

Generated from: 89 Google Maps businesses, 18 BizBuySell deals,
47 reviews analyzed, 12 Reddit threads, 3 FDDs

🎯 Key Insights:

Market Structure:
• Highly fragmented (no dominant player)
• 89 active competitors, avg 4.3⭐ rating
• Market leader: Lone Star Backflow (4.9⭐, 312 reviews)

Financial Benchmarks:
• Typical revenue: $500-800K (service companies)
• Typical margin: 25-35% EBITDA
• Typical multiple: 3.5-4.5x EBITDA
• Est. market size: $45-65M total annual revenue

Acquisition Opportunities:
• 25% of owners age 60+ (retirement window)
• 64% of businesses 15+ years old (established)
• Low tech adoption (75% no online booking)
• Property ownership: 33% own real estate

Competitive Threats:
• PE consolidation: Holt Services buying competitors
• Regulatory: TX law requires annual testing (stable demand)
• Barriers: RME license required (moat intact)

Recommendation: ✅ STRONG ACQUISITION MARKET
Estimated viable targets: 20-30 businesses
```

#### 3. **Document Q&A**

**AlphaSense feature:** Ask questions about documents using AI

**Scout Application:**
```
You: "What percentage of revenue is recurring?"

Scout AI (analyzing website + reviews + benchmarks):
"Based on TX regulations requiring annual backflow testing,
estimated 60-70% of revenue is recurring annual contracts.
This is consistent with FDD data for similar service franchises
(Mosquito Joe: 65% recurring). One-time revenue comes from
repairs (~20%) and new installations (~15%)."

Sources: TX Water Code §12.013, 47 analyzed reviews mentioning
"annual service", Mosquito Joe FDD Item 19
```

---

## Exemplar 3: FactSet - Enterprise Data Platform

**Source:** [FactSet](https://www.factset.com/) | [Comparison](https://slashdot.org/software/comparison/AlphaSense-vs-FactSet/)

### What They Built

**Positioning:** Enterprise-grade financial data + analytics platform

**Architecture:**
```
Data Layer:
├── Real-time market data
├── Company fundamentals (10+ years)
├── Earnings estimates
├── Ownership data
├── News feeds
└── Alternative data

Integration Layer:
├── Excel add-in (seamless)
├── Python API
├── REST API
├── CRM integrations (Salesforce)
└── Custom workflows

Analysis Layer:
├── Screening engines
├── Portfolio analytics
├── Risk modeling
├── Quantitative research
└── Report generation
```

### Design Patterns to Borrow

#### 1. **Excel Integration**

**FactSet approach:** All data accessible in Excel via formulas

**Scout Application:**
```excel
In Excel:

=SCOUT.BUSINESS("ABC Backflow", "revenue_estimate")
  → Returns: $800,000

=SCOUT.INDUSTRY("HVAC", "Houston", "median_multiple")
  → Returns: 3.5

=SCOUT.COMPETITION("ABC Backflow", "count_5mi")
  → Returns: 12

Build financial models using Scout data directly in Excel
```

#### 2. **API-First Architecture**

**FactSet pattern:** Everything accessible via API

**Scout Application:**
```python
# Scout Python SDK
import scout

# Search for businesses
businesses = scout.search(
    industry="backflow testing",
    location="Houston, TX",
    min_rating=4.0
)

# Get estimates
for biz in businesses:
    revenue = scout.estimate_revenue(biz.id)
    valuation = scout.estimate_value(biz.id)

    print(f"{biz.name}: ${revenue:,.0f} → ${valuation:,.0f}")

# Export to Airtable/Notion/whatever
scout.export(businesses, format="airtable", table_id="xyz")
```

#### 3. **Customizable Workflows**

**FactSet feature:** Build custom research workflows

**Scout Application:**
```
Workflow: "Thesis Validation"

Step 1: Define Criteria
├── Industry: [Input]
├── Geography: [Input]
└── Target Count: >30 ✓/✗

Step 2: Universe Building
├── Google Maps search → [Auto]
├── Deduplicate → [Auto]
└── Store results → [Auto]

Step 3: Benchmarking
├── BizBuySell scrape → [Auto]
├── FDD extraction → [Auto]
└── Calculate benchmarks → [Auto]

Step 4: Scoring
├── Rank by signals → [Auto]
├── Filter by criteria → [Auto]
└── Generate report → [Auto]

Step 5: Export
├── Top 50 to CSV → [Auto]
├── Watchlist → [Manual Review]
└── Email report → [Auto]

[Save Workflow] [Run Now] [Schedule Daily]
```

---

## Exemplar 4: Due Diligence Platforms (M&A)

**Sources:** [V7 Labs Guide](https://www.v7labs.com/blog/due-diligence-software) | [Papermark](https://www.papermark.com/blog/m-and-a-due-diligence-software)

### What They Built

**Modern M&A diligence platforms combine:**
- Virtual data rooms (secure document sharing)
- AI document analysis
- Workflow automation
- Risk flagging
- Collaboration tools

### Key Platforms:

**1. V7 AI Agents**
```
Specialized agents:
├── Financial Due Diligence Agent
├── Data Room Analysis Agent
├── Contract Review Agent
└── Risk Assessment Agent

Capabilities:
• Extract key clauses from 1000+ contracts
• Flag indemnities, exclusivity, non-solicit
• Generate structured summaries
• Detect anomalies in financials
```

**2. Datasite (formerly Merrill)**
```
End-to-end deal management:
├── Virtual data room
├── Project management
├── Analytics dashboard
├── Compliance tracking
└── Post-close integration

Used for: IPOs, M&A, restructuring, sell-side auctions
```

**3. DealRoom**
```
Combines:
├── VDR (virtual data room)
├── Project management (checklists, tasks)
├── Pipeline tracking
├── Real-time reporting
└── Integration (Slack, Excel, CRM)
```

### Design Patterns to Borrow

#### 1. **Automated Checklist System**

**M&A Platform Approach:** Pre-built diligence checklists

**Scout Application:**
```
Due Diligence Checklist: ABC Backflow

Financial Documents:
☑ 3 years tax returns (uploaded)
☑ P&L statements (uploaded)
☐ Balance sheet (MISSING - request)
☐ Aged receivables (MISSING)
☑ Customer list (received)
☑ SDE recast (uploaded)

Legal Documents:
☑ Articles of incorporation
☐ Operating agreement (MISSING)
☐ Material contracts (requested)
☑ Lease agreement (uploaded)
☑ Licenses (TX RME-12345 verified)

Operational:
☑ Employee list (5 employees)
☐ Equipment list (requested)
☑ Technology stack (WordPress, QuickBooks)
☐ SOPs (not available)

Scout Auto-Status:
🔴 BLOCKERS: Missing balance sheet, receivables (can't complete valuation)
🟡 WARNINGS: No SOPs documented, lease expires 2027
🟢 READY: All critical docs received

Progress: 12/18 items complete (67%)
Est. time to close: 30-45 days
```

#### 2. **Red Flag Detection**

**M&A Platforms:** AI scans docs for risk factors

**Scout Application:**
```
Red Flags Detected: ABC Backflow

🚩 CRITICAL (3):

1. Revenue Discrepancy
   Tax returns show: $520K (2023)
   Recast P&L shows: $800K (2023)
   ⚠️ Difference: $280K (54% jump!)
   → Action: Request reconciliation from broker

2. Customer Concentration
   Top 3 customers = 67% of revenue
   → Risk: Lose one, business worth 30% less
   → Action: Request customer contracts, cancellation clauses

3. Pending Litigation
   Found in: Google search "ABC Backflow lawsuit"
   Filed: Nov 2024, unpaid invoice dispute
   → Action: Request details from seller

⚠️ MODERATE (2):

4. Aggressive SDE Add-backs
   Owner salary: $120K ✓ reasonable
   "One-time repairs": $80K ⚠️ May be recurring
   → Action: Ask if equipment repairs are actually annual

5. Lease Expiring Soon
   Current lease expires: Dec 2027 (3 years)
   → Action: Negotiate extension before closing

ℹ️ INFORMATIONAL (3):
[6-8: Minor items...]

Overall Risk Score: 42/100 (MODERATE)
Recommendation: Proceed with caution, address critical items
```

#### 3. **Collaboration Features**

**M&A Platforms:** Multiple stakeholders, comments, tasks

**Scout Application:**
```
Deal Room: ABC Backflow

Team Members:
├── You (Owner)
├── advisor@example.com (Advisor - view only)
├── investor@fund.com (Investor - comment)
└── lawyer@firm.com (Attorney - full access)

Activity Feed:
─────────────────────────────────
Today, 2:15 PM
Investor commented on "Revenue Discrepancy":
"This is concerning. Won't proceed until reconciled."

Today, 11:30 AM
You uploaded: tax_returns_2023.pdf

Yesterday, 4:45 PM
Advisor flagged: "Check lease terms before LOI"

Yesterday, 2:00 PM
Attorney updated checklist: ✓ Articles of incorporation

[Add Comment] [Assign Task] [Upload Document]
```

---

## Exemplar 5: YC-Backed Modern Terminals (2024-2025)

**Sources:** [YC Finance Portfolio](https://www.ycombinator.com/companies/industry/finance) | [Bayesline](https://bayesline.com/) | [Dataglade](https://www.ycombinator.com/companies/dataglade)

### What's Being Built NOW

#### **Bayesline (YC 2024)** - GPU-Powered Analytics
```
Problem: Bloomberg/FactSet don't let you build custom analytics
Solution: GPU-accelerated, fully customizable analytics

Features:
├── Custom dashboards in seconds (not weeks)
├── Real-time data processing
├── Tailored to your investment strategy
└── 100x faster than traditional platforms

Founders: Ex-Bloomberg Quant + Ex-BlackRock MD
Target: Hedge funds, asset managers
```

**Scout Application:** Same principle - let users customize for their thesis

```python
# User defines custom acquisition score
def my_acquisition_score(business):
    score = 0

    # My priorities (customizable)
    if business.owner_age >= 60:
        score += 25

    if business.property_owned:
        score += 20

    if business.rating >= 4.5:
        score += 15

    if business.tech_score < 30:  # Low tech = opportunity
        score += 15

    if business.margin > 0.30:  # High margin
        score += 15

    if business.competition_count < 10:  # Low competition
        score += 10

    return score

# Apply to entire universe
scout.rank_by(my_acquisition_score)
```

#### **Dataglade (YC)** - AI-Generated Stock Analysis
```
Problem: Manual research is slow
Solution: AI generates analysis + financial models automatically

Workflow:
Input: Stock ticker (AAPL)
Output:
├── Executive summary
├── Bull/bear cases
├── 3-statement model (auto-built)
├── Valuation (DCF, comps)
└── Investment recommendation

Speed: Seconds (not hours)
Use: Saves institutional investors hours per day
```

**Scout Application:** Same for SMB acquisition

```
Input: "ABC Backflow Testing, Houston"

Scout AI Output (generated in 30 seconds):

INVESTMENT MEMO: ABC Backflow Testing

Business Overview:
Independent backflow testing company serving Houston metro
Founded 2001 (25 years), owner Mike Rodriguez (age 62)

Financial Profile (estimated):
Revenue: $800K (67th percentile for Houston HVAC)
EBITDA: $240K (30% margin - good for industry)
EBITDA Multiple: 3.75x asking (vs market 3.5-4.5x)
Valuation: $900K asking (fair)

Competitive Position:
Market: 89 competitors, fragmented
Rank: #23 by review count (mid-tier)
Rating: 4.7⭐ (above avg 4.3⭐)
Key threat: Lone Star Backflow (2.3mi, 4.9⭐, larger)

Investment Thesis:
✅ Retirement-age owner (exit motivated)
✅ Established business (25 years)
✅ Above-average margins (30% vs 22% median)
✅ Fair pricing (3.75x middle of range)
⚠️ Moderate competition
⚠️ No property ownership (lease risk)

Recommendation: PURSUE
Risk-adjusted score: 73/100 (B+ opportunity)

Suggested offer: $850K (3.5x), with seller note if needed
Est. ROI: 15-20% cash-on-cash return
```

#### **Trata (YC)** - AI Research Desk for Hedge Funds
```
Agents interview analysts → Generate research → Distribute

For Scout: Agents could interview SMB owners, generate acquisition profiles
```

---

## Key Design Patterns Summary

### 1. **Multi-Source Data Aggregation**
- Unify disparate sources (Google Maps, BizBuySell, FDD, Reddit, PE data)
- Single search across all sources
- Deduplicate and merge records

### 2. **AI-Powered Analysis**
- Auto-generate summaries and insights
- Flag red flags automatically
- Answer questions about businesses/markets
- Build financial models automatically

### 3. **Screening & Filtering**
- Pre-built screens for common use cases
- Custom screens with complex logic
- Save screens, set alerts for new matches
- 100s-1000s of filter criteria

### 4. **Time-Series Analytics**
- Chart metrics over time (review velocity, ratings, etc.)
- Detect trends (growth, decline, stagnation)
- Compare to benchmarks and peers

### 5. **Collaborative Workflows**
- Multi-user access (owner, advisors, investors)
- Comments, tasks, assignments
- Activity feeds, notifications
- Version control on documents

### 6. **Checklists & Automation**
- Pre-built due diligence checklists
- Auto-detect missing documents
- Track progress (X of Y items complete)
- Estimate time to close

### 7. **Export & Integration**
- Export to Excel, CSV, PDF
- API access for programmatic use
- Integrate with CRM, Notion, Airtable
- Webhooks for automation (Zapier, Make.com)

### 8. **Risk Detection**
- Automatically flag anomalies
- Compare to market norms
- Severity levels (critical, moderate, informational)
- Suggested actions

---

## Scout-Specific Applications

### **Terminal-Style UI for SMB Acquisition**

```
┌─────────────────────────────────────────────────────────────┐
│ SCOUT - Deal Sourcing Intelligence Terminal                │
├─────────────────────────────────────────────────────────────┤
│ Search: [backflow testing houston ____________] 🔍         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ ┌─────────────────┐ ┌─────────────────┐ ┌──────────────┐ │
│ │ Universe        │ │ Benchmarks      │ │ Watchlist    │ │
│ │                 │ │                 │ │              │ │
│ │ 89 businesses   │ │ Revenue: $650K  │ │ 7 targets    │ │
│ │ 4.3⭐ avg       │ │ Margin: 30%     │ │ 2 contacted  │ │
│ │ $550K median    │ │ Multiple: 3.5x  │ │ 1 NDA signed │ │
│ │                 │ │                 │ │              │ │
│ │ [View All]      │ │ [18 deals]      │ │ [Manage]     │ │
│ └─────────────────┘ └─────────────────┘ └──────────────┘ │
│                                                             │
│ ┌───────────────────────────────────────────────────────┐ │
│ │ Top Targets (by acquisition score)                    │ │
│ ├───────────────────────────────────────────────────────┤ │
│ │ 1. ABC Backflow (87/100) 🟢                          │ │
│ │    Owner: Mike Rodriguez, 62 | Rev: $800K | 4.7⭐    │ │
│ │    [View Profile] [Add to Watchlist] [Generate Memo] │ │
│ │                                                        │ │
│ │ 2. Texas Backflow (84/100) 🟢                        │ │
│ │    Owner: James Wilson, 67 | Rev: $900K | 4.8⭐      │ │
│ │    [View Profile] [Add to Watchlist] [Generate Memo] │ │
│ │                                                        │ │
│ │ 3. Premium Backflow (79/100) 🟡                      │ │
│ │    Owner: Unknown | Rev: $650K | 4.6⭐               │ │
│ │    [View Profile] [Need More Data] [Generate Memo]   │ │
│ └───────────────────────────────────────────────────────┘ │
│                                                             │
│ ┌───────────────────────────────────────────────────────┐ │
│ │ Market Intelligence                                    │ │
│ ├───────────────────────────────────────────────────────┤ │
│ │ • 25% of owners age 60+ (62 potential sellers)        │ │
│ │ • PE consolidation: Holt Services active (12 acq)     │ │
│ │ • Low tech: 75% lack online booking (opportunity)     │ │
│ │ • Regulation: TX law requires annual testing (stable) │ │
│ └───────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘

Bottom Bar: [Export CSV] [Run Screener] [Settings] [Help]
```

---

## Implementation Priorities for Scout

Based on exemplar research, build in this order:

### **Phase 1: Core Data Terminal (Weeks 1-4)**
```
1. Multi-source aggregation ✓
   - Google Maps ✓
   - BizBuySell benchmarks (fix scraper)
   - FDD extraction ✓

2. Basic terminal UI
   - Dashboard with panels
   - Search box (single search → all sources)
   - Business profile view
   - Export to CSV

3. Simple scoring
   - Rule-based (not ML)
   - Rank by acquisition attractiveness
   - Top 20 list
```

### **Phase 2: Intelligence Layer (Weeks 5-8)**
```
4. AI summaries
   - Market overview (auto-generated)
   - Business profiles (auto-generated)
   - Investment memos (auto-generated)

5. Screening engine
   - Pre-built screens (retirement age, etc.)
   - Custom screens with filters
   - Save screens, set alerts

6. Red flag detection
   - Financial anomalies
   - Risk scoring
   - Suggested actions
```

### **Phase 3: Collaboration (Weeks 9-12)**
```
7. Deal rooms
   - Multi-user access
   - Comments, tasks
   - Document sharing
   - Activity feed

8. Diligence checklists
   - Pre-built templates
   - Progress tracking
   - Auto-detect missing docs

9. API & integrations
   - Python SDK
   - Excel add-in
   - CRM exports
   - Webhooks (Zapier)
```

---

## Competitive Positioning vs Incumbents

### **Scout vs BizBuySell**
```
BizBuySell:
├── On-market deals only
├── Everyone watches (no edge)
├── No analysis tools
├── Just a listing site
└── Cost: ~$500/year (for brokers)

Scout:
├── Off-market + on-market combined
├── Proprietary sourcing (Google Maps)
├── Full analysis suite
├── Intelligence platform
└── Cost: <$1K/year
```

### **Scout vs Grata ($50-150K/year)**
```
Grata:
├── 19M+ companies
├── Enterprise platform
├── General purpose
└── Cost: $50-150K/year

Scout:
├── Focused on SMB acquisition
├── Solo searcher friendly
├── Thesis-specific
└── Cost: <$1K/year
```

**Scout's edge:** Grata for public markets = Scout for SMB acquisition (1/50th the cost)

---

## Technical Architecture Lessons

### From FactSet/Bloomberg:
- **API-first:** Everything accessible programmatically
- **Real-time updates:** Data refreshes automatically
- **Excel integration:** Analysts live in Excel
- **Customizable:** Build your own workflows

### From AlphaSense:
- **Semantic search:** Understands intent, not just keywords
- **Multi-source:** Search across everything at once
- **AI summaries:** Auto-generate insights
- **Q&A:** Ask questions, get answers

### From DealRoom/Datasite:
- **Checklists:** Track diligence progress
- **Collaboration:** Multiple stakeholders
- **Version control:** Track document changes
- **Audit trail:** Who did what when

### From Koyfin:
- **Free tier:** Hook users before they pay
- **Beautiful UI:** Finance can be visual
- **Fast:** Responsiveness matters
- **Exports:** Let users take data elsewhere

---

## Next Steps

1. **Study these platforms hands-on:**
   - Sign up for Koyfin free tier
   - Try AlphaSense demo
   - Watch Datasite product videos

2. **Borrow their best patterns:**
   - Multi-panel dashboard layout
   - Unified search across sources
   - AI-generated summaries
   - Screening engine
   - Diligence checklists

3. **Adapt for SMB acquisition:**
   - Google Maps instead of stock tickers
   - BizBuySell instead of Edgar filings
   - Acquisition score instead of stock rating
   - Owner age instead of CEO tenure

4. **Build Scout as "Koyfin for SMB Acquisition"**
   - Terminal-style UI
   - Multi-source data aggregation
   - AI-powered analysis
   - $468/year pricing (vs $50K Grata)

---

## Conclusion

**The financial terminal market proves:**
- ✅ Disrupting $32K platforms with $500 tools works (Koyfin)
- ✅ AI-powered analysis is table stakes (AlphaSense, Bayesline)
- ✅ Beautiful UI matters in finance (everyone copying Koyfin)
- ✅ APIs/integrations > walled gardens (FactSet pattern)
- ✅ Collaboration features essential for deals (DealRoom)

**Scout should be:**
- "AlphaSense for SMB acquisition" (AI-powered research)
- "Koyfin for small businesses" (affordable terminal)
- "DealRoom for micro PE" (collaboration + diligence)

**The opportunity:** These patterns have been proven for public markets. No one has applied them to SMB acquisition yet. **Scout can be first.**

---

**Sources:**
1. [Koyfin Bloomberg Alternatives Guide](https://www.koyfin.com/blog/best-bloomberg-terminal-alternatives/)
2. [AlphaSense Platform](https://www.alpha-sense.com/)
3. [V7 Labs Due Diligence Guide](https://www.v7labs.com/blog/due-diligence-software)
4. [YC Finance Startups 2024-2025](https://www.ycombinator.com/companies/industry/finance)
5. [FactSet vs AlphaSense Comparison](https://slashdot.org/software/comparison/AlphaSense-vs-FactSet/)
