# Scout 5-Scraper Implementation - Execution Plan

**Date:** February 17, 2026
**Status:** Ready to Execute
**Timeline:** 10-12 days autonomous implementation

---

## 📋 What We've Prepared

### 1. Product Specification (✅ Complete)
**File:** `docs/SCRAPER_PRODUCT_SPEC.md` (35KB)

Comprehensive product spec covering:
- Executive summary & business value
- System architecture
- 5 component specifications (Wisconsin, California, NASAA FRED, Aggregator, BizBuySell)
- Technical patterns & success criteria
- Testing strategy & timeline
- Risk assessment & dependencies

### 2. Implementation PRD (✅ Complete)
**File:** `workspace-5-scrapers/PRD.md` (25KB)

Detailed implementation instructions for autonomous agent:
- Goal & reference implementation (minnesota_fdd.py)
- Per-component requirements with code examples
- State-specific details (form IDs, table structures, quirks)
- Testing requirements & validation queries
- Deliverables checklist

### 3. LEARNINGS.md (✅ Complete)
**File:** `workspace-5-scrapers/LEARNINGS.md` (10KB)

Pattern library for agents:
- Tool pattern (inheritance, API structure)
- Chrome driver setup with anti-detection
- Rate limiting strategies
- FDD domain knowledge (Item 19 extraction)
- State-specific quirks & workarounds
- Testing strategies & common mistakes

---

## 🎯 The 5 Components

| Component | Lines | Complexity | Timeline | Coverage |
|-----------|-------|------------|----------|----------|
| 1. Wisconsin FDD Scraper | ~400 | Medium | 2-3 days | 11% (1.5K brands) |
| 2. California FDD Scraper | ~450 | High | 3-4 days | 30% (4-5K brands) |
| 3. NASAA FRED Scraper | ~500 | Medium-High | 3-4 days | 46% (7 states) |
| 4. FDD Aggregator | ~200 | Medium | 1-2 days | - (unifies all) |
| 5. BizBuySell Enhancement | ~150 | Low | 1 day | Market comps |
| **TOTAL** | **~1,700 lines** | **Mixed** | **10-12 days** | **92% market** |

---

## 🚀 Execution Steps

### Step 1: Run Autonomous Agent Loop (10-12 days)

```bash
cd /Users/andylee/Projects/micro-pe/scout

# Run agent loop for 50 cycles (continuous implementation)
python agent_loop.py \
    --workspace ./workspace-5-scrapers \
    --cycles 100 \
    --interval 300  # 5 min between cycles

# Or run unlimited until .done file appears
python agent_loop.py \
    --workspace ./workspace-5-scrapers \
    --interval 300
```

**What Happens:**
- **Bootstrap (Cycle 0):** Architect creates TODO.md with ~50 tasks
- **Cycles 1-20:** Wisconsin scraper implementation
- **Cycles 21-40:** NASAA FRED scraper (highest ROI)
- **Cycles 41-65:** California scraper (largest, most complex)
- **Cycles 66-80:** FDD Aggregator
- **Cycles 81-90:** BizBuySell enhancement
- **Cycles 91-100:** Testing, refinement, documentation

**Monitoring:**
```bash
# Terminal 2: Watch TODO progress
watch -n 30 'cat workspace-5-scrapers/TODO.md | head -30'

# Terminal 3: Watch git commits
watch -n 30 'cd workspace-5-scrapers && git log --oneline | head -10'

# Terminal 4: Check current state
watch -n 30 'cat workspace-5-scrapers/.state.json'
```

### Step 2: Validate Implementation

After agent loop completes, run validation tests:

```bash
cd workspace-5-scrapers

# Test each scraper
python -c "
from tools.wisconsin_fdd import WisconsinFDDScraper
scraper = WisconsinFDDScraper()
results = scraper.search('car wash', max_results=5)
print(f'Wisconsin: {results[\"total_found\"]} FDDs')
"

python -c "
from tools.california_fdd import CaliforniaFDDScraper
scraper = CaliforniaFDDScraper()
results = scraper.search('car wash', max_results=5)
print(f'California: {results[\"total_found\"]} FDDs')
"

python -c "
from tools.nasaa_fred_fdd import NASAAFredFDDScraper
scraper = NASAAFredFDDScraper()
results = scraper.search('car wash', max_results=5)
print(f'NASAA FRED (7 states): {results[\"total_found\"]} FDDs')
"

# Test aggregator
python -c "
from tools.fdd_aggregator import FDDAggregator
aggregator = FDDAggregator()
results = aggregator.search_all('car wash', max_results_per_source=10)
print(f'Total unique FDDs: {results[\"total_deduplicated\"]}')
print(f'Market coverage: {results[\"market_coverage\"]}')
"
```

**Expected Output:**
```
Wisconsin: 12 FDDs
California: 25 FDDs
NASAA FRED (7 states): 31 FDDs
Total unique FDDs: 67
Market coverage: 92%
```

### Step 3: Push to GitHub

```bash
cd /Users/andylee/Projects/micro-pe

# Stage all changes
git add scout/tools/wisconsin_fdd.py
git add scout/tools/california_fdd.py
git add scout/tools/nasaa_fred_fdd.py
git add scout/tools/fdd_aggregator.py
git add scout/tools/bizbuysell_tool.py
git add scout/tools/__init__.py
git add scout/tests/

# Commit with descriptive message
git commit -m "Add 5-scraper FDD data collection system

- Wisconsin FDD scraper (11% market coverage)
- California FDD scraper (30% market coverage, largest state)
- NASAA FRED scraper (46% coverage, 7 states)
- FDD Aggregator (unified interface, deduplication)
- BizBuySell market comps (enhanced)

Total coverage: 92% U.S. franchise market
Brands: 15,000-20,000
Documents: 30,000-40,000 FDDs

Implements autonomous data collection for SMB due diligence.
All scrapers follow minnesota_fdd.py pattern.
Includes comprehensive test suites and documentation.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"

# Push to GitHub
git push origin main
```

### Step 4: Create Mock Report

Generate example report showing system capabilities:

```bash
cd workspace-5-scrapers

# Create mock report script
cat > generate_mock_report.py <<'EOF'
#!/usr/bin/env python3
"""Generate mock Scout FDD Aggregator Report"""

from datetime import datetime

# Mock data (would come from aggregator in production)
mock_results = {
    "search_date": datetime.now().isoformat(),
    "industry": "car wash",
    "total_deduplicated": 67,
    "states_covered": 10,
    "market_coverage": "92%",
    "by_state": {
        "minnesota": {"total_found": 18, "brands": ["Tommy's Express", "Quick Quack", "Mister Car Wash"]},
        "wisconsin": {"total_found": 12, "brands": ["Tommy's Express", "Tidal Wave", "Rocket Wash"]},
        "california": {"total_found": 25, "brands": ["Elephant Car Wash", "Clean Ride", "Shine Car Wash"]},
        "nasaa_fred": {
            "total_found": 31,
            "states": ["NY", "IL", "MD", "VA", "WA", "ND", "RI"],
            "brands": ["Zips Car Wash", "Cobblestone", "Mister Car Wash"]
        }
    },
    "item19_stats": {
        "fdds_with_item19": 42,
        "percentage": "63%",
        "avg_revenue_range": "$1.2M - $2.8M",
        "avg_ebitda_range": "$280K - $650K (23-24% margin)"
    }
}

# Generate markdown report
report = f"""# Scout FDD Aggregator Report
**Industry:** Car Wash
**Date:** {mock_results['search_date'][:10]}
**Market Coverage:** {mock_results['market_coverage']} of U.S. franchise market

---

## Executive Summary

Successfully aggregated **{mock_results['total_deduplicated']} unique FDD documents** for the car wash industry across **{mock_results['states_covered']} states**, covering an estimated **92% of the U.S. franchise market**.

**Key Findings:**
- {mock_results['item19_stats']['fdds_with_item19']} FDDs ({mock_results['item19_stats']['percentage']}) contain Item 19 financial data
- Average revenue range: {mock_results['item19_stats']['avg_revenue_range']}
- Average EBITDA range: {mock_results['item19_stats']['avg_ebitda_range']}
- Data quality: High (verified PDF downloads, extracted text)

---

## Data Collection Summary

### By State Breakdown

| State | FDDs Found | Sample Brands |
|-------|------------|---------------|
| California | {mock_results['by_state']['california']['total_found']} | {', '.join(mock_results['by_state']['california']['brands'][:3])} |
| NASAA FRED (7 states) | {mock_results['by_state']['nasaa_fred']['total_found']} | {', '.join(mock_results['by_state']['nasaa_fred']['brands'][:3])} |
| Minnesota | {mock_results['by_state']['minnesota']['total_found']} | {', '.join(mock_results['by_state']['minnesota']['brands'][:3])} |
| Wisconsin | {mock_results['by_state']['wisconsin']['total_found']} | {', '.join(mock_results['by_state']['wisconsin']['brands'][:3])} |

**Total:** {mock_results['total_deduplicated']} unique FDDs (after deduplication)

### NASAA FRED Multi-State Coverage

NASAA FRED database covers 7 states in a single query:
- New York (NY) - 15% market share
- Illinois (IL) - 8% market share
- Maryland (MD) - 3% market share
- Virginia (VA) - 3% market share
- Washington (WA) - 3% market share
- North Dakota (ND) - 2% market share
- Rhode Island (RI) - 2% market share

---

## Financial Benchmarks (Item 19 Data)

### Revenue Benchmarks

```
Car Wash Industry - Unit Economics

┌─────────────────────┬──────────────────────────────────────┐
│ Metric              │ Range                                │
├─────────────────────┼──────────────────────────────────────┤
│ Average Revenue     │ $1.2M - $2.8M per location          │
│ Top 25% Performers  │ $3.5M+ per location                  │
│ Bottom 25%          │ <$800K per location                  │
│ Median              │ $1.8M per location                   │
└─────────────────────┴──────────────────────────────────────┘
```

### EBITDA Benchmarks

```
┌─────────────────────┬──────────────────────────────────────┐
│ Metric              │ Range                                │
├─────────────────────┼──────────────────────────────────────┤
│ Average EBITDA      │ $280K - $650K per location           │
│ EBITDA Margin       │ 23-24%                               │
│ Top Performers      │ 28-30% margins                       │
│ Bottom Performers   │ 15-18% margins                       │
└─────────────────────┴──────────────────────────────────────┘
```

### Top Performing Brands (Item 19 Data Available)

1. **Tommy's Express**
   - Average Revenue: $3.5M per location
   - EBITDA Margin: ~28%
   - Locations: 150+ (growing)
   - FDD Year: 2025

2. **Mister Car Wash**
   - Average Revenue: $2.8M per location
   - EBITDA Margin: ~25%
   - Locations: 400+ (established)
   - FDD Year: 2024

3. **Zips Car Wash**
   - Average Revenue: $2.2M per location
   - EBITDA Margin: ~24%
   - Locations: 250+
   - FDD Year: 2024

---

## Data Quality Assessment

### Coverage Statistics

```
┌────────────────────────────┬─────────────┬──────────────┐
│ Metric                     │ Count       │ Percentage   │
├────────────────────────────┼─────────────┼──────────────┤
│ Total FDDs Collected       │ 67          │ 100%         │
│ FDDs with Item 19          │ 42          │ 63%          │
│ FDDs with PDF Downloaded   │ 67          │ 100%         │
│ Cross-State Duplicates     │ 8           │ Deduplicated │
│ Failed Extractions         │ 3           │ 4%           │
└────────────────────────────┴─────────────┴──────────────┘
```

### Deduplication Summary

- **Original records:** 75 FDDs found across all states
- **Duplicates identified:** 8 (same franchise, same year, different states)
- **Unique records:** 67 FDDs after deduplication
- **Deduplication rate:** 11% (expected for multi-state coverage)

**Deduplication Rules Applied:**
1. Keep most recent year
2. Prefer FDDs with Item 19 extracted
3. Prefer larger states (CA > NY > MN > WI)
4. Track provenance (source state recorded)

---

## Use Cases Enabled

### 1. Target Valuation
**Scenario:** Valuing a 5-location car wash business in Texas

**Analysis:**
- Target claims $1.5M revenue per location
- Item 19 benchmarks: $1.2M - $2.8M (within range ✓)
- Target EBITDA margin: 22%
- Benchmark margin: 23-24% (slightly below)

**Conclusion:** Revenue claims are credible. EBITDA margin slightly below industry average—investigate operational efficiency.

### 2. Market Entry Analysis
**Scenario:** Assessing car wash franchise opportunity in Florida

**Available Data:**
- 67 FDD documents for car wash industry
- 42 with Item 19 financial data
- Top performers: Tommy's Express, Mister Car Wash
- Average unit economics: $1.8M revenue, $430K EBITDA

**Decision:** Sufficient data to model returns. Recommend focusing on top-performing brands with proven unit economics.

### 3. Competitive Benchmarking
**Scenario:** Comparing 3 potential acquisition targets

**FDD Benchmark Comparison:**
```
Target A: $2.1M revenue, 26% margin → Top 25% performer
Target B: $1.4M revenue, 20% margin → Below average
Target C: $3.0M revenue, 28% margin → Top 10% performer
```

**Recommendation:** Target C best-in-class, Target A solid performer, Target B requires turnaround.

---

## System Performance

### Execution Metrics

```
┌────────────────────────────────┬─────────────────────────┐
│ Metric                         │ Result                  │
├────────────────────────────────┼─────────────────────────┤
│ Total Query Time               │ 8.3 minutes             │
│ Average Time per State         │ 2.1 minutes             │
│ Cache Hit Rate                 │ 0% (first query)        │
│ Success Rate                   │ 96% (64/67 successful)  │
│ PDF Download Success           │ 100% (67/67)            │
│ Item 19 Extraction Success     │ 100% (42/42 with Item19)│
└────────────────────────────────┴─────────────────────────┘
```

### Caching Impact

**Next Query (using 90-day cache):**
- Expected time: <10 seconds (vs 8.3 minutes)
- Cache hit rate: 100%
- No server requests needed

---

## Technical Implementation

### Components Used

1. **Minnesota FDD Scraper** (✅ Working)
   - Source: Minnesota CARDS database
   - Found: 18 car wash FDDs

2. **Wisconsin FDD Scraper** (🆕 New)
   - Source: Wisconsin DFI database
   - Found: 12 car wash FDDs

3. **California FDD Scraper** (🆕 New)
   - Source: California DocQNet database
   - Found: 25 car wash FDDs (largest)

4. **NASAA FRED FDD Scraper** (🆕 New)
   - Source: NASAA multi-state database
   - Found: 31 car wash FDDs across 7 states

5. **FDD Aggregator** (🆕 New)
   - Unified query interface
   - Cross-state deduplication
   - Provenance tracking

### Technology Stack

- **Web Scraping:** Selenium + BeautifulSoup
- **Anti-Detection:** Chrome CDP overrides, user-agent spoofing
- **PDF Extraction:** PyMuPDF (fitz)
- **Caching:** JSON files with 90-day TTL
- **Deduplication:** Key-based (franchise name + year)

---

## Recommendations

### For Analysts

1. **Use Cached Queries:** 90-day cache dramatically improves speed (8 min → 10 sec)
2. **Focus on Item 19:** 63% of FDDs have financial data—prioritize these
3. **Cross-Reference States:** Same franchise may file in multiple states with different data
4. **Verify Vintage:** Check FDD year—use most recent data (2024-2025)

### For Deal Teams

1. **Baseline Validation:** Use Item 19 data to validate target company claims
2. **Peer Comparison:** Compare target against top 25% performers in same industry
3. **Geographic Considerations:** State-specific data may reveal regional variations
4. **Due Diligence:** Request target's actual financials for comparison against benchmarks

### For Product Team

1. **Expand Coverage:** Add remaining states (Illinois, Indiana, etc.) for 95%+ coverage
2. **Automate Reports:** Build automated report generation from aggregator data
3. **Add Visualizations:** Charts for revenue/EBITDA distributions
4. **Item 19 Parsing:** Enhance text extraction to parse tables/numbers automatically

---

## Conclusion

**Status:** ✅ Multi-State FDD Scraper System Operational

**Coverage Achieved:**
- 92% of U.S. franchise market
- 67 unique FDD documents for car wash industry
- 42 FDDs with Item 19 financial performance data
- 10 states covered (MN, WI, CA, NY, IL, MD, VA, WA, ND, RI)

**Business Value:**
- Automated FDD collection (100x faster than manual)
- Comprehensive financial benchmarks for SMB due diligence
- Cross-state deduplication ensures data quality
- 90-day caching minimizes server load

**Next Steps:**
1. Expand to additional industries (HVAC, laundromat, etc.)
2. Build automated report generation
3. Integrate with deal flow pipeline
4. Add Item 19 table parsing for structured data extraction

---

**Generated by Scout FDD Aggregator System**
**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

print(report)

# Save to file
with open('MOCK_REPORT.md', 'w') as f:
    f.write(report)

print("\n✅ Mock report saved to MOCK_REPORT.md")
EOF

# Make executable
chmod +x generate_mock_report.py

# Generate report
python generate_mock_report.py > ../docs/SCOUT_FDD_REPORT_MOCK.md

echo "✅ Mock report created at docs/SCOUT_FDD_REPORT_MOCK.md"
```

---

## 📊 Success Criteria Checklist

### Pre-Launch
- [✅] Product spec written (SCRAPER_PRODUCT_SPEC.md)
- [✅] Implementation PRD written (workspace-5-scrapers/PRD.md)
- [✅] LEARNINGS.md pattern library created
- [ ] Agent loop workspace initialized
- [ ] Anthropic API key in .env

### During Implementation (Agent Loop)
- [ ] Bootstrap complete (TODO.md created with ~50 tasks)
- [ ] Wisconsin scraper implemented and tested
- [ ] NASAA FRED scraper implemented and tested
- [ ] California scraper implemented and tested
- [ ] FDD Aggregator implemented and tested
- [ ] BizBuySell enhanced and tested
- [ ] All validation queries pass (>80% success rate)
- [ ] Test suites pass (>80% coverage)

### Post-Implementation
- [ ] Manual validation: search("car wash") returns 50+ FDDs
- [ ] Deduplication works (no duplicate franchise+year)
- [ ] All components pushed to GitHub
- [ ] Mock report generated (SCOUT_FDD_REPORT_MOCK.md)
- [ ] Documentation complete (README, docstrings)
- [ ] System ready for production use

---

## 🚨 Contingency Plans

### If Agent Loop Fails

**Option 1: Hybrid Approach**
- Agent generates scaffolding (70-80% complete)
- Human refines edge cases (2-4 hours per scraper)
- Still 60-70% time savings

**Option 2: Traditional Implementation**
- Follow original tender-launching-sparkle.md plan
- 10-15 days manual coding
- Proven approach, full control

### If Specific Scraper Fails

**Wisconsin/California fail:**
- Continue with Minnesota + NASAA FRED (60% coverage)
- Still valuable for benchmarking

**NASAA FRED fails:**
- Continue with state scrapers (40% coverage)
- Add more states individually

**Aggregator fails:**
- Use scrapers independently
- Manual deduplication for now

---

## 📞 Support & Questions

**Workspace:** `/Users/andylee/Projects/micro-pe/scout/workspace-5-scrapers/`

**Check Agent Status:**
```bash
cat workspace-5-scrapers/.state.json
```

**Check TODO Progress:**
```bash
cat workspace-5-scrapers/TODO.md | grep -c "\[x\]"  # Completed
cat workspace-5-scrapers/TODO.md | grep -c "\[ \]"  # Remaining
```

**View Recent Commits:**
```bash
cd workspace-5-scrapers && git log --oneline -20
```

**Check for Blockers:**
```bash
ls workspace-5-scrapers/comms/outbox/
```

---

## 🎉 Expected Outcome

**After 10-12 days:**

1. **5 Production-Ready Components**
   - tools/wisconsin_fdd.py (~400 lines)
   - tools/california_fdd.py (~450 lines)
   - tools/nasaa_fred_fdd.py (~500 lines)
   - tools/fdd_aggregator.py (~200 lines)
   - tools/bizbuysell_tool.py (~150 lines enhanced)

2. **Comprehensive Test Suites**
   - Unit tests for each component
   - Integration tests for aggregator
   - >80% code coverage

3. **Documentation**
   - README with usage examples
   - Comprehensive docstrings
   - Mock report demonstrating capabilities

4. **GitHub Repository**
   - All code committed
   - Clear commit history
   - Ready for team review

5. **Production System**
   - 92% U.S. market coverage
   - 15,000-20,000 brands accessible
   - Automated FDD collection for SMB due diligence

---

**Ready to execute? Start with:**

```bash
cd /Users/andylee/Projects/micro-pe/scout
python agent_loop.py --workspace ./workspace-5-scrapers --cycles 100 --interval 300
```

**Let the autonomous agents build your scraper system!** 🚀
