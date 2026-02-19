# Scout Terminal UI Design

**Vision:** Multi-screen terminal interface for SMB market intelligence
**Inspiration:** Bloomberg Terminal's multi-panel layout

---

## Screen Layout (4-Panel Setup)

```
┌─────────────────────────────────┬─────────────────────────────────┐
│                                 │                                 │
│   SCREEN 1: MARKET OVERVIEW     │   SCREEN 2: TARGET LIST         │
│   (Industry Dashboard)          │   (Ranked Opportunities)        │
│                                 │                                 │
├─────────────────────────────────┼─────────────────────────────────┤
│                                 │                                 │
│   SCREEN 3: BUSINESS PROFILE    │   SCREEN 4: MARKET PULSE        │
│   (Deep Dive Analysis)          │   (Sentiment & Trends)          │
│                                 │                                 │
└─────────────────────────────────┴─────────────────────────────────┘
```

---

## SCREEN 1: Market Overview

**Purpose:** High-level industry intelligence at a glance
**Updates:** Real-time as you research new markets

```
╔══════════════════════════════════════════════════════════════════════╗
║  SCOUT - MARKET OVERVIEW                          Updated: 2m ago   ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  Current Market: HVAC Services — Los Angeles, CA                    ║
║  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ║
║                                                                      ║
║  📊 MARKET SIZE                                                      ║
║  ├─ Total Businesses:        487                                    ║
║  ├─ Market Density:          High (3.2 per sq mi)                   ║
║  ├─ Competitive Index:       8.2/10 ████████░░                      ║
║  └─ Est. Market Value:       $584M total revenue                    ║
║                                                                      ║
║  💰 FINANCIAL BENCHMARKS                                             ║
║  ├─ Median Revenue:          $1.2M  (Range: $400K - $3.5M)         ║
║  ├─ EBITDA Margin:           18%    (Range: 12% - 24%)             ║
║  ├─ Valuation Multiple:      2.5x EBITDA                            ║
║  └─ Typical Acquisition:     $540K - $2.1M                          ║
║                                                                      ║
║  ⭐ QUALITY METRICS                                                  ║
║  ├─ Avg Rating:              4.1 ★★★★☆                             ║
║  ├─ Review Volume:           High (avg 180 reviews/business)        ║
║  ├─ Sentiment:               72% Positive, 18% Neutral, 10% Neg    ║
║  └─ Top Complaint:           "Pricing transparency"                 ║
║                                                                      ║
║  📈 MARKET TRENDS (30 days)                                          ║
║  ├─ New Entrants:            ↑ 3 new businesses                     ║
║  ├─ Job Postings:            ↑ 45 open positions (growth signal)    ║
║  ├─ Reddit Mentions:         ↑ 23 threads (high interest)           ║
║  └─ Google Search Volume:    ↑ 12% vs last month                    ║
║                                                                      ║
║  🎯 ACQUISITION OUTLOOK                                              ║
║  ├─ Entry Difficulty:        Medium ████░░░░░░                      ║
║  ├─ Competition:             High   ████████░░                      ║
║  ├─ Margins:                 Good   ██████░░░░                      ║
║  └─ Overall Rating:          B+ (Good opportunity, competitive)     ║
║                                                                      ║
║  [R]efresh  [C]hange Market  [E]xport  [H]elp                       ║
╚══════════════════════════════════════════════════════════════════════╝
```

**Key Features:**
- **Market sizing** - How big is this market?
- **Financial benchmarks** - What should I expect to pay and earn?
- **Quality metrics** - Are these good businesses?
- **Trends** - Is the market growing or declining?
- **Acquisition outlook** - Quick assessment of opportunity

---

## SCREEN 2: Target List

**Purpose:** Ranked list of acquisition targets
**Sortable by:** Score, Revenue, Rating, Location

```
╔══════════════════════════════════════════════════════════════════════╗
║  SCOUT - TARGET LIST                                 487 businesses  ║
╠══════════════════════════════════════════════════════════════════════╣
║  Showing: Top 20 by Acquisition Score | Sort: [Score] Rev Rating   ║
║  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ║
║                                                                      ║
║  #  Business Name             Score  Est.Rev  Rating  Signals       ║
║  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ║
║  1  Cool Air HVAC             92     $1.5M    4.8★   🟢🟢🟢         ║
║     Los Angeles, CA                  ±20%     (350)   Growth signal ║
║     📞 (310) 555-0100  🌐 coolair.com                              ║
║     → Established 15yr | Hiring | Top reviews                       ║
║  ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─  ║
║  2  Premier Climate Control   88     $1.2M    4.6★   🟢🟢🟡         ║
║     Santa Monica, CA                 ±20%     (220)   Stable        ║
║     📞 (310) 555-0200  🌐 premierclimate.com                       ║
║     → Strong margins | Commercial focus                             ║
║  ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─  ║
║  3  SoCal Heating & Air       85     $980K    4.7★   🟢🟢🟢         ║
║     Pasadena, CA                     ±25%     (180)   High volume   ║
║     📞 (626) 555-0300  🌐 socalheating.com                         ║
║     → Fast growing | Low overhead                                   ║
║  ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─  ║
║  4  Valley Air Experts        82     $1.1M    4.5★   🟢🟡🟡         ║
║     Van Nuys, CA                     ±20%     (150)   Moderate      ║
║     📞 (818) 555-0400  🌐 valleyairexperts.com                     ║
║     → Residential focus | Owner retiring (signal!)                  ║
║  ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─  ║
║  5  West Coast Climate        80     $890K    4.6★   🟢🟢🟡         ║
║     Culver City, CA                  ±25%     (140)   Stable        ║
║     📞 (424) 555-0500  🌐 westcoastclimate.com                     ║
║     → Good reviews | Limited online presence                        ║
║  ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─  ║
║                                                                      ║
║  [↑↓] Navigate  [Enter] Analyze  [F]ilter  [E]xport CSV  [H]elp    ║
╚══════════════════════════════════════════════════════════════════════╝

Legend:
  🟢 Positive signal  🟡 Neutral  🔴 Negative
  Score: Acquisition attractiveness (0-100)
  Est.Rev: Estimated from FDD benchmarks ±confidence interval
```

**Key Features:**
- **Ranked by score** - Best opportunities at the top
- **Quick contact info** - Phone and website right there
- **Visual signals** - Green/yellow/red indicators
- **Action signals** - "Owner retiring", "Hiring", "Fast growing"
- **One-line summary** - Quick decision making

---

## SCREEN 3: Business Profile

**Purpose:** Deep dive on a specific target
**Triggered by:** Selecting a business from Screen 2

```
╔══════════════════════════════════════════════════════════════════════╗
║  SCOUT - BUSINESS PROFILE                                           ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  Cool Air HVAC Services                          Acq. Score: 92/100 ║
║  Los Angeles, CA                                                     ║
║  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ║
║                                                                      ║
║  📍 LOCATION & CONTACT                                               ║
║  Address:     1234 Wilshire Blvd, Los Angeles, CA 90010            ║
║  Phone:       (310) 555-0100                                        ║
║  Website:     www.coolair.com                                       ║
║  Established: 2009 (15 years in business)                           ║
║  Service Area: 25-mile radius (LA County)                           ║
║                                                                      ║
║  💰 FINANCIAL PROFILE (Estimated from FDD benchmarks)               ║
║  ┌────────────────────────────────────────────────────────────────┐ ║
║  │ Revenue:        $1.5M   ±20%  ████████████░░░░                 │ ║
║  │                 (vs industry median $1.2M)  ↑ Above average     │ ║
║  │                                                                 │ ║
║  │ EBITDA:         $270K   18% margin                              │ ║
║  │                 (vs industry median 18%)    → At benchmark      │ ║
║  │                                                                 │ ║
║  │ Valuation Est:  $675K - $810K  (2.5x EBITDA)                   │ ║
║  │ Confidence:     Medium (based on 12 comparable FDDs)            │ ║
║  └────────────────────────────────────────────────────────────────┘ ║
║                                                                      ║
║  ⭐ CUSTOMER SENTIMENT (350 reviews)                                ║
║  Overall Rating: 4.8 ★★★★★  (Top 5% in market)                     ║
║  ┌────────────────────────────────────────────────────────────────┐ ║
║  │ Distribution:  5★ ████████████████ 68%                         │ ║
║  │                4★ ████████ 22%                                  │ ║
║  │                3★ ██ 6%                                         │ ║
║  │                2★ ░ 3%                                          │ ║
║  │                1★ ░ 1%                                          │ ║
║  │                                                                 │ ║
║  │ Positive Themes (mentioned often):                              │ ║
║  │  • "reliable" (89 mentions)                                     │ ║
║  │  • "professional" (76 mentions)                                 │ ║
║  │  • "fast response" (64 mentions)                                │ ║
║  │  • "fair pricing" (52 mentions)                                 │ ║
║  │                                                                 │ ║
║  │ Negative Themes (rare):                                         │ ║
║  │  • "scheduling delays" (8 mentions)                             │ ║
║  │  • "upselling" (5 mentions)                                     │ ║
║  └────────────────────────────────────────────────────────────────┘ ║
║                                                                      ║
║  📈 GROWTH SIGNALS                                                   ║
║  ├─ Job Postings:       2 open positions (HVAC Technician, Admin)  ║
║  ├─ Recent Activity:    Responded to 95% of reviews (engaged)      ║
║  ├─ Online Presence:    Website modern, active Google Business     ║
║  └─ Equipment:          Recent photos show newer fleet (3 trucks)  ║
║                                                                      ║
║  🎯 ACQUISITION ASSESSMENT                                           ║
║  Strengths:                                                          ║
║  ✓ Top-tier reputation (4.8★)                                       ║
║  ✓ Strong margins (18% EBITDA)                                      ║
║  ✓ Growth signals (hiring, modern operations)                       ║
║  ✓ Established customer base (15 years)                             ║
║                                                                      ║
║  Considerations:                                                     ║
║  ⚠ Competitive market (487 competitors)                             ║
║  ⚠ Owner involvement unclear (check during diligence)               ║
║                                                                      ║
║  Recommended Next Steps:                                             ║
║  1. Cold outreach via phone/website                                 ║
║  2. Request financials (P&L, customer list)                         ║
║  3. Check licensing & certifications                                 ║
║  4. Evaluate owner's willingness to sell                            ║
║                                                                      ║
║  [B]ack to List  [E]xport Report  [N]otes  [C]ontact Log  [H]elp   ║
╚══════════════════════════════════════════════════════════════════════╝
```

**Key Features:**
- **Financial estimates** - Revenue, EBITDA, valuation range
- **Review analysis** - Not just ratings, but themes
- **Growth signals** - Is this business growing?
- **Acquisition assessment** - Pros/cons for acquisition
- **Next steps** - Actionable recommendations

---

## SCREEN 4: Market Pulse

**Purpose:** Sentiment, trends, and market intelligence
**Sources:** Reddit, news, job postings, seasonal trends

```
╔══════════════════════════════════════════════════════════════════════╗
║  SCOUT - MARKET PULSE                              Last scan: 1h ago ║
╠══════════════════════════════════════════════════════════════════════╣
║  Market: HVAC Services — Los Angeles, CA                            ║
║  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ║
║                                                                      ║
║  💬 REDDIT SENTIMENT (23 threads, 180 comments in last 30 days)     ║
║  Overall: Mixed 😐  (52% Positive, 28% Neutral, 20% Negative)       ║
║  ┌────────────────────────────────────────────────────────────────┐ ║
║  │ Top Discussion: "Is an HVAC business worth buying in 2026?"    │ ║
║  │ r/sweatystartup • 45 upvotes • 28 comments                      │ ║
║  │ Sentiment: Cautiously optimistic                                │ ║
║  │ Key points:                                                      │ ║
║  │  ✓ Recession-resistant, essential service                       │ ║
║  │  ✓ Good margins if managed well (15-25% EBITDA)                │ ║
║  │  ⚠ High competition in major cities                            │ ║
║  │  ⚠ Labor costs increasing (hard to find techs)                 │ ║
║  │  ⚠ Seasonality (summer peaks)                                  │ ║
║  │                                                                 │ ║
║  │ Top Discussion: "Sold my HVAC company for 2.8x EBITDA"         │ ║
║  │ r/Entrepreneur • 89 upvotes • 52 comments                       │ ║
║  │ Sentiment: Positive (successful exit)                           │ ║
║  │ Key points:                                                      │ ║
║  │  ✓ Built recurring maintenance contracts (60% of revenue)      │ ║
║  │  ✓ Invested in modern dispatch/CRM software                    │ ║
║  │  ✓ Hired strong GM, made business owner-independent            │ ║
║  │  💡 Buyers love recurring revenue + systems                     │ ║
║  └────────────────────────────────────────────────────────────────┘ ║
║                                                                      ║
║  📊 MARKET TRENDS (30-day analysis)                                 ║
║  ┌────────────────────────────────────────────────────────────────┐ ║
║  │ Job Postings:        ↑ 45 open positions across market         │ ║
║  │                      (15% increase vs last month)               │ ║
║  │                      Signal: Market is growing/expanding        │ ║
║  │                                                                 │ ║
║  │ New Entrants:        3 new businesses in last 30 days           │ ║
║  │                      Signal: Market still attractive            │ ║
║  │                                                                 │ ║
║  │ Google Search Vol:   ↑ 12% vs last month                       │ ║
║  │                      Peak season approaching (summer heat)      │ ║
║  │                                                                 │ ║
║  │ Yelp Activity:       Normal (steady review volume)              │ ║
║  └────────────────────────────────────────────────────────────────┘ ║
║                                                                      ║
║  🎓 OPERATOR INSIGHTS                                                ║
║  From Reddit discussions and forums:                                 ║
║  ┌────────────────────────────────────────────────────────────────┐ ║
║  │ "Biggest challenge: Finding and retaining good techs"          │ ║
║  │ "Residential is competitive, commercial is goldmine"            │ ║
║  │ "Maintenance contracts = recurring revenue = higher multiple"   │ ║
║  │ "Software makes huge difference (ServiceTitan, Housecall Pro)" │ ║
║  │ "80% profit comes from 20% customers (focus on retention)"     │ ║
║  └────────────────────────────────────────────────────────────────┘ ║
║                                                                      ║
║  ⚡ ACTIONABLE INSIGHTS                                              ║
║  When evaluating HVAC businesses, prioritize:                       ║
║  1. ✓ Recurring maintenance contracts (40%+ of revenue ideal)      ║
║  2. ✓ Modern systems & software (dispatch, CRM, accounting)        ║
║  3. ✓ Trained technicians on payroll (not contractors)             ║
║  4. ✓ Commercial mix (less price-sensitive than residential)       ║
║  5. ✓ Owner-independent operations (strong GM/ops manager)         ║
║                                                                      ║
║  Red flags to avoid:                                                 ║
║  1. ✗ 100% owner-operated (hard transition)                        ║
║  2. ✗ No recurring revenue (one-time service only)                 ║
║  3. ✗ Aging equipment/fleet (CapEx needed)                         ║
║  4. ✗ No digital presence (hard to grow)                           ║
║                                                                      ║
║  [R]efresh  [D]eep Dive Thread  [E]xport  [H]elp                    ║
╚══════════════════════════════════════════════════════════════════════╝
```

**Key Features:**
- **Reddit sentiment** - What are operators saying?
- **Market trends** - Growth indicators (jobs, search volume)
- **Operator insights** - Real-world advice from owners
- **Actionable intel** - What to look for, what to avoid

---

## Workflow Example

### Starting a Research Session

```bash
# Launch Scout with 4-panel view
$ scout --panels

# Research a market
$ scout research "HVAC businesses in Los Angeles"

# System populates all 4 screens:
# Screen 1: Market Overview (industry stats)
# Screen 2: Target List (487 businesses, ranked)
# Screen 3: Empty (waiting for selection)
# Screen 4: Market Pulse (Reddit, trends)
```

### Exploring Targets

```bash
# In Screen 2, navigate with arrow keys
# Press Enter on "Cool Air HVAC"

# Screen 3 populates with deep dive analysis
# Screen 1 & 4 stay unchanged (context)
# Screen 2 highlights selected business
```

### Exporting Targets

```bash
# From Screen 2
$ [E] Export top 20 to CSV

# Generates: outputs/targets/hvac_los_angeles_top20.csv
# Columns: Name, Score, Est_Revenue, Rating, Phone, Website, Signals
```

---

## Alternative: Single Screen Mode

For users who prefer single-screen focus:

```bash
# Traditional single view
$ scout research "HVAC businesses in Los Angeles"

# Shows overview, then prompts:
[1] View targets  [2] Market pulse  [3] Export
```

---

## Key Design Principles

1. **Information Density** - Pack lots of data, but organized clearly
2. **Visual Hierarchy** - Important info stands out (scores, ratings, signals)
3. **Actionable** - Every screen suggests next steps
4. **Real-time Feel** - Update timestamps, fresh data indicators
5. **Scannable** - Can understand each screen in 5-10 seconds
6. **Color Coding** - 🟢 Green = positive, 🟡 Yellow = neutral, 🔴 Red = warning
7. **Keyboard-driven** - Fast navigation without mouse

---

## Tech Stack for Multi-Panel UI

**Terminal Multiplexer:**
- `tmux` - Split terminal into 4 panes
- `screen` - Alternative to tmux
- `iTerm2` - Native split panes (Mac)

**Python Libraries:**
- `rich` - Beautiful terminal formatting, tables, progress bars
- `textual` - TUI framework for complex layouts
- `blessed` - Terminal control, colors, positioning
- `asciimatics` - Animation and complex UIs

**Recommended Approach:**
1. Build with `rich` first (simple, beautiful tables/panels)
2. If need interactivity, upgrade to `textual` (TUI framework)
3. Use `tmux` for 4-panel layout initially

---

## Next Steps

1. **Review this design** - Do these screens make sense?
2. **Prioritize screens** - Which one is most valuable to build first?
3. **Choose UI library** - Start with `rich` for MVP?
4. **Build iteratively** - Start with Screen 1 (Market Overview)?

Which screen do you find most useful? Should we adjust the layout or add/remove anything?
