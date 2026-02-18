# Research Business Type Skill

## Overview
This skill conducts institutional-grade private equity research on SMB business types for acquisition evaluation. It's specifically calibrated for Holt Ventures' investment thesis: $200k capital, process-driven businesses with regulatory moats, recurring revenue, and remote management potential.

## Quick Start

### Basic Usage
```bash
/research-business-type [business-type-name]
```

### Examples
```bash
# Research specific business types from holt-ventures.md
/research-business-type backflow-testing
/research-business-type calibration-services
/research-business-type specialty-insurance-brokers
/research-business-type government-contract-administration
/research-business-type ndt-services
```

## What This Skill Does

### Inputs
- **Business type name** (required): E.g., "backflow-testing", "calibration-services"
- Auto-loads Holt Ventures investment context (capital, thesis, returns target)

### Process (4-8 hours of research)
1. **Market Intelligence:** TAM/SAM, growth rates, regulations, competition
2. **Deal Flow Validation:** BizBuySell search, actual businesses for sale
3. **Operational Analysis:** Licensing, staffing, equipment, technology
4. **Risk Assessment:** AI disruption, macro exposure, regulatory changes
5. **Financial Modeling:** 5-year IRR/MOIC calculation, scenario analysis

### Outputs
- **11,000-word comprehensive report** covering:
  - Executive summary with investment rating (STRONG BUY/BUY/HOLD/AVOID)
  - Business model & operations deep dive
  - Market analysis (quantified TAM/SAM/SOM)
  - Competitive landscape assessment
  - Operational requirements (licensing, staffing, equipment)
  - Financial analysis (margins, multiples, IRR model)
  - Strategic fit with Holt Ventures thesis
  - Risk register (10+ risks with mitigations)
  - Actionable 30-day deal sourcing plan
  - Complete source citations (15-20+ sources)

- **Saved to:** `/industry-research/[business-type]/report.md`

## Business Types from Holt Ventures

### Category 1: Paper-Heavy Regulatory Services
- `government-contract-administration`
- `regulatory-reporting-services`
- `permit-expediting`
- `compliance-auditing`
- `environmental-compliance-consulting`

### Category 2: Insurance & Risk Management
- `specialty-insurance-brokers`
- `insurance-adjusters`
- `risk-management-consulting`
- `surety-bond-services`

### Category 3: Industrial Support Services
- `calibration-services` (ISO 17025)
- `ndt-services` (Non-Destructive Testing)
- `fire-protection-inspection`
- `industrial-equipment-inspection`
- `environmental-testing`

### Category 4: Critical Infrastructure & Facilities
- `building-commissioning`
- `backflow-testing`
- `fire-alarm-sprinkler-inspection`
- `elevator-service`

## Expected Output Format

### Executive Briefing (Immediate)
After research completion, you'll receive:
```
✅ Research complete: [Business Type Name]

Investment Recommendation: STRONG BUY / BUY / HOLD / AVOID (X/10 conviction)

Key Findings:
- [3-5 bullet points on strengths]
- [2-3 bullet points on risks]

Top Risks:
1. [Critical risk with mitigation]
2. [Critical risk with mitigation]
3. [Critical risk with mitigation]

Recommended Next Action: [Specific guidance]

📄 Full report: [file path]
```

### Full Report Sections
1. Executive Summary (investment rating, thesis, financials)
2. Business Model & Operations (what, how, revenue model, costs)
3. Market Analysis (TAM/SAM/SOM, growth drivers, regulations)
4. Competitive Landscape (fragmentation, barriers, intensity)
5. Operational Deep Dive (licensing, insurance, equipment, staffing, tech)
6. Financial Analysis (benchmarks, deal flow, model, scenarios)
7. Strategic Assessment (thesis fit, tailwinds, value creation)
8. Risk Analysis (risk register, red flags, SWOT)
9. Actionable Next Steps (sourcing strategy, diligence, 30-day plan)
10. Appendix (sources, assumptions, comparables)

## Quality Standards

Every report includes:
- ✅ 8,000-12,000 words
- ✅ 15-20+ cited sources with dates
- ✅ Quantified metrics (no vague "large market" - must be "$X-Y billion")
- ✅ BizBuySell deal flow analysis (actual listings found)
- ✅ 5-year financial model with IRR calculation
- ✅ Specific licensing requirements (exact license names, transferability)
- ✅ Risk register (10+ risks with probability/impact/mitigation)
- ✅ 30-day action plan with weekly tasks

## Use Cases

### 1. Initial Screening (Research 5-6 types)
Pick your most interesting business types and research them:
```bash
/research-business-type backflow-testing
/research-business-type calibration-services
/research-business-type specialty-insurance-brokers
/research-business-type fire-protection-inspection
/research-business-type ndt-services
```

Compare conviction levels → Focus on highest-rated (8+/10)

### 2. Deep Validation (Compare alternatives)
Research similar business types to make informed choice:
```bash
/research-business-type backflow-testing
/research-business-type fire-alarm-sprinkler-inspection
# Both are mandated inspection services - which is better fit?
```

### 3. Full Portfolio Analysis (All 18 types)
Systematically research every business type:
- Week 1: Research Category 1 (Regulatory Services) - 5 types
- Week 2: Research Category 2 (Insurance) - 4 types
- Week 3: Research Category 3 (Industrial Support) - 5 types
- Week 4: Research Category 4 (Infrastructure) - 4 types
- Week 5: Compare and select THE ONE sector

## Time & Resource Requirements

**Per Business Type:**
- Research time: 4-8 hours (automated web research)
- Report length: 8,000-12,000 words
- Sources: 15-20+ citations
- Cost: $0 (uses free sources: BizBuySell, Google, government sites)

**Full Portfolio (18 types):**
- Total time: 72-144 hours research
- Total output: 144,000-216,000 words
- Timeline: 3-6 weeks if running sequentially
- Faster: Run 3-5 in parallel batches

## Integration with Holt Ventures Workflow

### Phase 1: Screening (Pick 6 types to research)
```bash
# Choose most promising from intuition
/research-business-type backflow-testing
/research-business-type calibration-services
/research-business-type specialty-insurance-brokers
/research-business-type fire-protection-inspection
/research-business-type ndt-services
/research-business-type environmental-testing
```

### Phase 2: Review & Rank
- Read executive summaries
- Compare conviction levels (aim for 8+/10)
- Identify clear winner(s)

### Phase 3: Deal Sourcing (For top choice)
Use the 30-day action plan from report:
- Join industry associations
- Build target list (100 businesses)
- Start owner conversations
- Submit LOIs

### Phase 4: Decision Checkpoint
After 30 days:
- If 3+ LOIs submitted → Continue in this sector
- If <3 LOIs → Research next-best alternative sector

## Tips for Best Results

### 1. Use Specific Business Type Names
**Good:**
- `backflow-testing` (clear, specific)
- `calibration-services` (specific service)
- `specialty-insurance-brokers` (narrowed focus)

**Bad:**
- `inspection services` (too broad - which kind?)
- `testing` (too vague)
- `compliance` (many types of compliance)

### 2. Research Comparable Types Together
Compare related services to make informed choice:
- `backflow-testing` vs `fire-alarm-sprinkler-inspection` (both mandated inspections)
- `calibration-services` vs `ndt-services` (both industrial testing)
- `specialty-insurance-brokers` vs `risk-management-consulting` (both insurance-related)

### 3. Check Deal Flow First
If a report shows <10 BizBuySell listings, the market may be too thin. Research an alternative type.

### 4. Trust the Conviction Scores
- **9-10/10:** Clear winner, start deal sourcing immediately
- **7-8/10:** Strong candidate, validate with owner conversations
- **5-6/10:** Conditional, only pursue if no better options
- **<5/10:** Pass, research alternatives

## Output File Organization

Reports are automatically saved to organized directory structure:

```
/Users/andylee/Projects/micro-pe/industry-research/
├── backflow-testing/
│   └── report.md (11,000 words)
├── calibration-services/
│   └── report.md (10,500 words)
├── specialty-insurance-brokers/
│   └── report.md (9,800 words)
└── [etc...]
```

Each report is standalone - can be read independently or compared side-by-side.

## Troubleshooting

### Issue: "Not enough information available"
- Try alternate business type names (e.g., "backflow-testing" vs "cross-connection-control")
- Some niche types have less public data - use trade associations as primary source
- Consider this a signal: If research is hard, deal sourcing will be hard too

### Issue: "Can't find BizBuySell listings"
- Try broader search terms (e.g., "inspection services" not just "backflow testing")
- Expand geography beyond SoCal (try nationwide search)
- Low listing count (<10) is important data point: Market may be too thin

### Issue: "Conflicting data on market size"
- Use multiple sources, cite all, explain discrepancies
- Industry association data often most reliable (but optimistic)
- Triangulate: Market research firms + government data + trade groups

### Issue: "Can't determine licensing requirements"
- Call state licensing board directly (include in research notes)
- Search "[license type] California requirements" for official sources
- Trade association websites often have licensing FAQs

## Advanced Usage

### Compare to Previous Research
Reference earlier comprehensive reports:
```bash
# Check if business type overlaps with existing research
# Earlier reports in:
# - /industry-research/01-regulatory-services/report.md
# - /industry-research/02-insurance-risk-management/report.md
# - /industry-research/03-industrial-support-services/report.md
# - /industry-research/04-critical-infrastructure-facilities/report.md
```

### Build Comparison Matrix
After researching 5-6 types, create comparison:
```bash
# Manually create or request:
# /industry-research/comparison-matrix.md
#
# Compare across:
# - Deal flow (#listings)
# - Entry multiple (Xx SDE)
# - Exit multiple (Yx EBITDA)
# - Base case IRR
# - Recurring revenue %
# - AI disruption risk
# - Thesis alignment score
```

### Focus on Decision-Critical Sections
If time-constrained, prioritize reading:
1. Executive Summary (investment recommendation)
2. Section 2.2 (Deal Flow Validation) - Are businesses actually for sale?
3. Section 5.1 (Licensing Requirements) - Can we operate this?
4. Section 6.3 (Financial Model) - Will returns hit target?
5. Section 9 (Next Steps) - What do we do if we pursue this?

## Maintenance

### Keep Skill Updated
Update skill when:
- Investment thesis changes (different capital, return targets)
- Research methodology improves (better data sources)
- Output format needs adjustment (add/remove sections)

### Add New Business Types
To research types not in original 18:
```bash
/research-business-type [new-type-name]
# Skill will adapt research to any SMB service business type
```

## Support

For issues or questions:
1. Check report quality checklist - Is output complete?
2. Review research sources - Are 15-20+ sources cited?
3. Validate BizBuySell search - Were actual listings found?
4. Check file path - Is report saved to correct directory?

## Version
- **Created:** February 2026
- **Last Updated:** February 2026
- **Calibrated For:** Holt Ventures SMB acquisition strategy
- **Report Template Version:** 1.0
