# Data Sources - Technical Architecture

**Focus:** Getting the right data from the right sources
**Priority:** Quality over quantity

---

## The Core Question

**What data do we NEED to make acquisition decisions?**

### Minimum Viable Data Set

For each business we want to contact:
1. **Who:** Name, owner (if possible)
2. **Where:** Address, city, state
3. **Contact:** Phone, website
4. **Size:** Revenue estimate (±50% accuracy is fine)
5. **Value:** Rough valuation estimate ($500K? $2M? $5M?)
6. **Maturity:** Business age (retirement window?)
7. **Quality:** Reputation signals (rating, reviews)

**That's it.** Everything else is nice-to-have.

---

## Data Source Analysis

### Source 1: Google Maps Places API ⭐ PRIMARY

**What We Get:**
```json
{
  "place_id": "ChIJ...",
  "name": "ABC Heating & Air",
  "formatted_address": "123 Main St, Houston, TX 77001",
  "formatted_phone_number": "(713) 555-1234",
  "website": "https://abchvac.com",
  "rating": 4.7,
  "user_ratings_total": 245,
  "geometry": {
    "location": { "lat": 29.7604, "lng": -95.3698 }
  }
}
```

**What We DON'T Get:**
- ❌ Revenue
- ❌ Employees
- ❌ Business age
- ❌ Owner name
- ❌ Financial data

**Reliability:** ⭐⭐⭐⭐⭐ (5/5)
- Official API, well-documented
- Stable schema
- High uptime
- Accurate data

**Cost:** $0.032 per search + $0.017 per business = ~$1.05 per 60 businesses

**Coverage:** Near-complete for brick-and-mortar businesses

**Technical Challenges:** None (just API calls)

**Status:** ✅ **PRODUCTION READY**

**Conclusion:** This is our **foundation**. Everything starts here.

---

### Source 2: BizBuySell (Web Scraping) ⭐⭐⭐ SUPPLEMENTARY

**What We Get (when successful):**
```json
{
  "title": "Established HVAC Company - Houston",
  "location": "Houston, TX",  // ⚠️ Just city/state, NO ADDRESS
  "asking_price": 1200000,
  "revenue": 800000,
  "cash_flow": 240000,      // SDE or EBITDA
  "description": "25 years in business...",
  "industry": "HVAC",
  "employees": "5-10",      // Sometimes available
  "real_estate": "Leased"   // Sometimes available
}
```

**What We DON'T Get:**
- ❌ Exact business identity (no address!)
- ❌ Phone number
- ❌ Owner name
- ❌ Reliable data (seller-reported, not audited)

**Reliability:** ⭐⭐⭐ (3/5)
- Data is seller-reported (may be inflated)
- Listings may be stale
- Many listings missing key fields
- Site structure changes break scrapers

**Cost:** Free (web scraping)

**Coverage:** Sparse
- Only ~20-50 active listings per industry nationwide
- Mostly businesses $500K-$5M range
- Geographic coverage patchy

**Technical Challenges:**
- ⚠️ **Bot detection** (Akamai WAF)
- ⚠️ **CSS selector changes** (site updates break scraper)
- ⚠️ **Rate limiting** (must go slow to avoid blocks)
- ⚠️ **Data extraction** (inconsistent formats)

**Status:** ⚠️ **FRAGILE - Needs undetected-chromedriver**

**The Matching Problem:**

```
Google Maps:     "ABC Heating & Air"
                 123 Main St, Houston, TX 77001

BizBuySell:      "HVAC Company - Houston"
                 Houston, TX
                 Revenue: $800K

→ How do we know if these are the same business?
→ Answer: WE DON'T, with high confidence

Without addresses, matching is ~70% confidence at best:
- Name might be anonymized ("HVAC Company" vs real name)
- Location is just city (Houston has 100+ HVAC companies)
- No phone/website to cross-reference
```

**Realistic Use Case:**

BizBuySell is NOT for matching individual businesses.

BizBuySell IS for building **industry benchmarks**:
- Scrape 20-30 HVAC deals in Texas
- Calculate median revenue: $650K
- Calculate median multiple: 3.5x EBITDA
- Calculate median margin: 30%

Then apply these benchmarks to ALL Google Maps businesses.

**Conclusion:** Use for **statistical distributions**, not individual matching.

---

### Source 3: Franchise Disclosure Documents (FDD) ⭐⭐⭐⭐ BENCHMARKS

**What We Get:**
```json
{
  "franchise_name": "Mosquito Joe",
  "fdd_year": 2024,
  "disclosure_date": "2024-03-15",
  "item19_data": {
    "sample_size": 487,
    "median_revenue": 285000,
    "top_quartile_revenue": 425000,
    "median_ebitda_margin": 0.35,
    "operating_expenses": {
      "labor": 0.25,
      "marketing": 0.08,
      "supplies": 0.15,
      ...
    }
  }
}
```

**What We DON'T Get:**
- ❌ Individual business identities
- ❌ Contact information
- ❌ Specific locations

**Reliability:** ⭐⭐⭐⭐⭐ (5/5)
- Legal documents (audited)
- Required by FTC
- Standardized format (Item 19)
- High accuracy

**Cost:** Free (public documents from state DFPI websites)

**Coverage:**
- ~3,000 franchises in US
- Many relevant to small business acquisition
- Limited to franchised businesses only

**Technical Challenges:**
- ✅ **PDF parsing** (solved with PyMuPDF)
- ✅ **Data extraction** (solved with Claude API + Instructor)
- ⚠️ **Item 19 not required** (some FDDs don't have financial data)

**Status:** ✅ **POC COMPLETE**

**Use Case:**

FDDs provide **industry benchmarks for franchised industries**:
- Mosquito Joe: $285K median revenue, 35% EBITDA margin
- Jan-Pro: $78K median revenue, 40% margin
- Visiting Angels: $1.2M median revenue, 12% margin

For **independent businesses** in same industry:
- Apply franchise benchmark ± 20% adjustment
- Franchises usually have higher revenue (brand recognition)
- Independents usually have higher margins (no royalties)

**Conclusion:** Excellent **benchmark source** for franchised industries.

---

### Source 4: State Business Registries ⭐⭐ ENRICHMENT ONLY

**What We Get (if we can scrape successfully):**
```json
{
  "entity_number": "C4567890",
  "legal_name": "ABC HEATING & AIR CONDITIONING INC",
  "incorporation_date": "2001-03-15",
  "entity_type": "DOMESTIC CORPORATION",
  "status": "ACTIVE",
  "registered_agent": "John Smith",
  "principal_address": "123 Main St, Houston, TX 77001"
}
```

**What We DON'T Get:**
- ❌ Revenue
- ❌ Employees
- ❌ Financial data
- ❌ Owner age
- ❌ Pretty much anything useful for valuation

**What We DO Get (useful):**
- ✅ Business age (incorporation date)
- ✅ Legal entity type (LLC, Corp, etc.)
- ✅ Status (active, dissolved)
- ⚠️ Owner name (sometimes, as registered agent)

**Reliability:** ⭐⭐⭐⭐ (4/5)
- Official government data
- Accurate legal information
- But often outdated (annual reports lag)

**Cost:**
- Free: California (API), Florida (bulk download), New York (API)
- Expensive: Texas ($1,350+ for bulk)
- Varies by state

**Coverage:** 50 states, but each has different access methods

**Technical Challenges:**
- ⚠️ **50 different systems** (each state different)
- ⚠️ **Session management** (many require login)
- ⚠️ **Bot detection** (automated access blocked)
- ⚠️ **Rate limiting** (slow down or get blocked)
- ⚠️ **Matching required** (legal name ≠ DBA name)

**Status:** ❌ **NOT WORTH IT YET**

**The Harsh Reality:**

State registries give us ONE useful field: **business age**

Is that worth:
- Building 50 different scrapers?
- Fighting bot detection?
- Dealing with session management?
- Matching legal names to DBAs?

**Alternative approach:**
- Estimate business age from:
  - Oldest Google review date
  - "Serving Houston since 2005" on website
  - Domain registration date (WHOIS)
  - Manual lookup for top 10 targets

**Conclusion:** Skip for MVP. Add later for high-priority targets only.

---

### Source 5: OpenCorporates API ⭐ PAID ALTERNATIVE

**What We Get:**
```json
{
  "company_number": "C4567890",
  "jurisdiction_code": "us_tx",
  "name": "ABC HEATING & AIR CONDITIONING INC",
  "incorporation_date": "2001-03-15",
  "company_type": "DOMESTIC CORPORATION",
  "current_status": "Active",
  "registered_address": "123 Main St, Houston, TX 77001"
}
```

**Reliability:** ⭐⭐⭐⭐ (4/5)
- Aggregates all 50 states
- Unified API
- Regularly updated

**Cost:**
- No free tier (API requires paid account)
- Pricing: ~$500-2000/month (estimated)

**Status:** ❌ **TOO EXPENSIVE FOR MVP**

**Conclusion:** Consider for production if state registry data proves valuable.

---

## DATA SOURCE STRATEGY

### Tier 1: FOUNDATION (Must Have)

**Google Maps API**
- **Use for:** Universe discovery (find all businesses)
- **Coverage:** Near-complete
- **Reliability:** Very high
- **Cost:** Cheap (~$1 per search)
- **Status:** ✅ Working

**Decision:** This is our PRIMARY source. Build everything around this.

---

### Tier 2: BENCHMARKS (High Value)

**BizBuySell Scraper**
- **Use for:** Industry financial benchmarks (NOT individual matching)
- **Coverage:** Sparse (20-50 deals per industry)
- **Reliability:** Medium (seller-reported data)
- **Cost:** Free
- **Status:** ⚠️ Needs testing (undetected-chromedriver)

**FDD Extractor**
- **Use for:** Franchise industry benchmarks
- **Coverage:** ~3,000 franchises
- **Reliability:** Very high (audited)
- **Cost:** Free (public docs) + $0.10/doc (Claude API)
- **Status:** ✅ POC complete

**Decision:** Use BOTH for benchmarks
- BizBuySell → Independent business benchmarks
- FDD → Franchise benchmarks
- Apply to Google Maps universe

---

### Tier 3: ENRICHMENT (Nice to Have)

**Website Scraping**
- **Use for:**
  - Find "Serving Houston since 2005" → Estimate age
  - Find owner name on About page
  - Verify business is operational
- **Coverage:** ~60% of businesses have websites
- **Reliability:** Medium (unstructured data)
- **Cost:** Free
- **Status:** ❌ Not built yet

**Decision:** Add for top 20 targets after initial ranking

---

**State Registries**
- **Use for:** Business age, legal status
- **Coverage:** All states
- **Reliability:** High (official data)
- **Cost:** Free to expensive (varies)
- **Status:** ❌ Too complex for MVP

**Decision:** Skip for now. Use website scraping + Google reviews for age estimates instead.

---

## RECOMMENDED DATA ARCHITECTURE

### Simple 2-Source Model (MVP)

```
SOURCE 1: Google Maps (Universe)
────────────────────────────────
For each business:
  ✓ Name, address, city, state
  ✓ Phone, website
  ✓ Rating, review count
  ✓ Coordinates

SOURCE 2: BizBuySell + FDD (Benchmarks)
────────────────────────────────────────
For entire industry:
  ✓ Median revenue
  ✓ Median cash flow
  ✓ Median multiple
  ✓ Median margin

CALIBRATION ENGINE
──────────────────
For each Google Maps business:
  1. Estimate revenue using review count proxy
  2. Apply industry median margin → cash flow
  3. Apply industry median multiple → valuation
  4. Assign confidence level

OUTPUT
──────
  ✓ 100 businesses with estimated values
  ✓ Ranked by acquisition attractiveness
  ✓ Export to CSV for outreach
```

**No database needed yet.**
**No entity matching needed.**
**Just two sources + simple math.**

---

## WHAT THIS MEANS FOR IMPLEMENTATION

### Phase 1: Prove It Works (1-2 weeks)

**Build:**
1. ✅ Google Maps scraper (DONE)
2. ⚠️ Fix BizBuySell scraper (test with undetected-chromedriver)
3. ✅ FDD extractor (DONE - just needs integration)
4. ✅ Calibration engine (basic version exists)

**Test:**
- Run on HVAC in Houston
- Google Maps → 100 businesses
- BizBuySell → 20 deals → Calculate benchmarks
- Apply benchmarks → Estimate values for all 100
- Rank by estimated value
- Export top 50 to CSV

**Success criteria:**
- Estimates seem reasonable (within 2x of reality)
- Top 20 targets look like good acquisition candidates
- Can complete entire process in <10 minutes
- Total cost <$5

---

### Phase 2: Scale It (weeks 3-4)

**Add:**
- Multiple geographies (Houston, Dallas, Austin)
- Multiple industries (HVAC, backflow, portable sanitation)
- Batch processing
- Better output formatting

**Don't add (yet):**
- ❌ Database (JSON files are fine for now)
- ❌ Entity matching (not needed for benchmark approach)
- ❌ State registries (too much work for one field)
- ❌ Complex deduplication (Google Maps mostly handles this)

---

### Phase 3: Add Enrichment (week 5+)

**Only if Phase 1-2 prove valuable:**
- Website scraping for top 20 targets
- Owner name lookup (LinkedIn, website)
- Business age verification
- Email finder tools

---

## CRITICAL INSIGHTS

### 1. BizBuySell is NOT for Matching

**Wrong approach:**
```
Google Maps: ABC Heating (Houston)
BizBuySell: HVAC Company (Houston) - $800K revenue

❌ Try to match these
❌ Merge revenue into ABC Heating
❌ High error rate, low confidence
```

**Right approach:**
```
BizBuySell: Scrape 20 HVAC deals in Texas
→ Calculate median revenue: $650K
→ Calculate median margin: 30%
→ Calculate median multiple: 3.5x

Apply to ALL Google Maps HVAC businesses:
→ Estimate revenue from review count
→ Apply 30% margin
→ Apply 3.5x multiple
→ Medium confidence (±50%)
```

### 2. We're Building Benchmarks, Not Spreadsheets

**We don't need:**
- Exact revenue for each business
- Perfect matches across sources
- Complete data for every business

**We need:**
- Reasonable estimates (±50% is fine)
- Relative ranking (which are bigger/better)
- Enough data to prioritize outreach

### 3. Quality > Completeness

**Better to have:**
- 100 businesses with medium-confidence estimates
- Clear about what's estimated vs actual
- Fast iteration (10 minutes per search)

**Than:**
- 100 businesses with 10% having perfect data
- 90% missing data
- 3 weeks of integration work

---

## NEXT STEPS

**Immediate (This Week):**
1. Test BizBuySell scraper with undetected-chromedriver
   ```bash
   python main.py benchmarks "HVAC" 20
   ```

2. If that works, run full pipeline:
   ```bash
   python main.py pipeline "HVAC" "Houston, TX" 20
   ```

3. Evaluate output:
   - Do estimates seem reasonable?
   - Are top-ranked businesses good targets?
   - Is this useful for decision-making?

**If YES → Build Phase 2 (scale to multiple markets)**

**If NO → Revisit data sources or calibration logic**

---

## CONCLUSION

**Start simple:**
- Google Maps (universe)
- BizBuySell (benchmarks)
- Simple calibration (review count proxy)

**Prove it works BEFORE:**
- Adding databases
- Building entity matching
- Integrating 5+ data sources
- Spending weeks on integration

**The hard part isn't the architecture.**
**The hard part is proving the estimates are useful.**

Let's test that first.
