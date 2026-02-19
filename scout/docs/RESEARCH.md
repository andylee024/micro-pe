# Scout: SMB Intelligence Platform

**Vision:** Bloomberg Terminal for Small Business Acquisition
**Created:** 2026-02-18

---

## Problem Statement

### The SMB Data Gap

Small and medium businesses (SMBs) lack the data infrastructure of public companies:
- **No public financials** - Revenue, margins, unit economics are private
- **No analyst coverage** - No equity research reports or market analysis
- **Fragmented information** - Data scattered across maps, reviews, forums, regulatory filings
- **No benchmarking** - Difficult to value a business without comparable data

**Result:** Private equity and individual buyers make acquisition decisions with incomplete information.

### What Bloomberg Does for Public Markets

Bloomberg Terminal aggregates:
- Real-time prices and financials
- Analyst research and ratings
- News and sentiment analysis
- Comparable company analysis
- Industry benchmarks

**Scout does this for SMBs.**

---

## User Journey

### Input: Investment Thesis
```
"HVAC businesses in CA"
"Car washes in SoCal"
"Laundromats in Houston"
```

### Output: Comprehensive Industry Report

**1. Universe Mapping**
- Total businesses in market (Google Maps)
- Geographic distribution and clustering

**2. Financial Benchmarks**
- Revenue ranges (FDD Item 19)
- EBITDA margins (FDD Item 19)
- Valuation multiples

**3. Customer Sentiment**
- Review scores (Google Reviews)
- Common themes and complaints

**4. Market Sentiment**
- Industry discussions (Reddit)
- Operator experiences and challenges

**5. Target Ranking**
- Businesses ranked by acquisition attractiveness
- Scoring: size, reviews, estimated financials

---

## Data Sources

### 1. Google Maps API
**Purpose:** Build business universe
**Data:** Name, address, phone, website
**Cost:** $5 per 1,000 searches

### 2. Google Reviews
**Purpose:** Customer sentiment
**Data:** Ratings, review text, themes
**Cost:** Included with Maps API

### 3. FDD Filings (State Databases)
**Purpose:** Financial benchmarks
**Data:** Item 19 (revenue, margins, unit economics)
**Coverage:** 90%+ of U.S. franchise market

**Current:**
- Minnesota: 15% coverage ✅
- Wisconsin: 11% coverage ✅
- Need: California (30%), NASAA FRED (46%)

### 4. Reddit
**Purpose:** Market sentiment
**Data:** Posts, comments from r/smallbusiness, r/Entrepreneur, etc.
**Cost:** Free

---

## Core Problems We're Solving

1. **Universe Building** - "How many HVAC businesses in LA?"
2. **Financial Benchmarking** - "What revenue should I expect?"
3. **Quality Assessment** - "Which businesses have good reputations?"
4. **Market Intelligence** - "Is this a good industry?"
5. **Target Identification** - "Which businesses should I contact?"

---

## Product Workflow

```bash
# Research an industry
$ scout research "HVAC businesses in Los Angeles"
📊 Found 487 businesses
📈 Median revenue: $1.2M, EBITDA: 18%
⭐ Average rating: 4.1 stars
💬 Market sentiment: Competitive, high labor costs

# Identify top targets
$ scout targets "HVAC businesses in Los Angeles" --top 20
1. Cool Air HVAC - $1.5M revenue, 4.8 stars, Score: 92/100
2. Premier Climate - $1.2M revenue, 4.6 stars, Score: 88/100
...

# Deep dive on specific business
$ scout analyze "Cool Air HVAC"
📊 Est. Revenue: $1.5M | EBITDA: $270K (18%)
⭐ 4.8 stars (350 reviews) - "reliable", "professional"
📈 Top 5% in market, 2 open positions
```

---

## What We Have vs. Need

### ✅ Already Built
- Google Maps Tool
- BizBuySell Tool
- Minnesota FDD Scraper (15%)
- Wisconsin FDD Scraper (11%)

### 🔨 Need to Build

**Phase 1: MVP (Core Research)**
1. FDD Aggregator - Query all scrapers, extract Item 19
2. Google Reviews Tool - Fetch reviews, sentiment analysis
3. Basic CLI - `scout research`
4. Report Generator - Terminal output

**Phase 2: Target Identification**
1. Scoring Engine - Rank businesses by attractiveness
2. Enhanced CLI - `scout targets`
3. CSV Export - Exportable lists

**Phase 3: Deep Dive**
1. Reddit Scanner - Market sentiment
2. Business Analysis - `scout analyze`
3. Professional Reports - Markdown export

**Phase 4: Coverage (Optional)**
1. California FDD Scraper (+30%)
2. NASAA FRED Scraper (+46%)

---

## Priority Questions

**Before we build, let's align:**

1. **MVP Scope** - Start with Phase 1 (Universe + FDD + Reviews)?
2. **FDD Coverage** - Do we need California + NASAA FRED scrapers now, or later?
3. **Reddit** - Must-have for MVP or can wait for Phase 3?
4. **Interface** - Terminal-only or build web UI too?
5. **User** - Who's the primary user? Individual buyers or PE firms?

Please review and let me know:
- Does this match your vision?
- Is the priority right?
- What should we build first?
