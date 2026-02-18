#!/usr/bin/env python3
"""
Generate a new Scout research run PRD.

Usage:
    python ralph/new_run.py "<industry>" "<location>" [output_path]

Examples:
    python ralph/new_run.py "HVAC" "Houston, TX"
    python ralph/new_run.py "car wash" "Dallas, TX" prds/carwash_dallas.json

Stories generated (in dependency order):
    S-001  Build business universe         (Google Maps)
    S-002  Build financial benchmarks      (BizBuySell)
    S-003  Calibrate universe              (apply S-002 to S-001)
    S-004  Collect UCC filings             (top 20 from S-003)
    S-005  Collect SBA loan data           (top 20 from S-003)
    S-006  Collect job postings            (top 20 from S-003)
    S-007  Score and rank                  (all signals from S-003–S-006)
    S-008  Generate acquisition report     (from S-007)
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def generate(industry: str, location: str, output: str = None) -> str:
    slug = (
        f"{industry.lower().replace(' ', '_')}_"
        f"{location.lower().replace(',', '').replace(' ', '_')}"
    )
    ts = datetime.now().strftime("%Y%m%d")

    prd = {
        "project": f"Scout — {industry} in {location}",
        "industry": industry,
        "location": location,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "stories": [
            {
                "id": "S-001",
                "title": f"Build business universe: {industry} in {location}",
                "description": (
                    f"Use the Google Maps tool to find all {industry} businesses in {location}. "
                    f"Run: python main.py universe \"{industry}\" \"{location}\"\n"
                    f"Save the full results list to the output file."
                ),
                "status": "open",
                "depends_on": [],
                "output_file": f"outputs/universe/{slug}_{ts}.json",
            },
            {
                "id": "S-002",
                "title": f"Build financial benchmarks: {industry}",
                "description": (
                    f"Scrape BizBuySell to build financial benchmarks for {industry} businesses. "
                    f"Run: python main.py benchmarks \"{industry}\" 20\n"
                    f"Extract and save: median revenue, cash flow, margin, EBITDA multiple."
                ),
                "status": "open",
                "depends_on": [],
                "output_file": f"outputs/benchmarks/{slug}_{ts}.json",
            },
            {
                "id": "S-003",
                "title": "Calibrate universe with benchmarks",
                "description": (
                    "Read the universe from S-001 and benchmarks from S-002. "
                    "Apply benchmarks to estimate revenue, EBITDA, and enterprise value "
                    "for each business. Use utils/financials.py apply_benchmarks() and rank_businesses(). "
                    "Output the full ranked list (all businesses, not just top 20)."
                ),
                "status": "open",
                "depends_on": ["S-001", "S-002"],
                "output_file": f"outputs/calibrated/{slug}_{ts}.json",
            },
            {
                "id": "S-004",
                "title": "Collect UCC filings for top 20",
                "description": (
                    "Read the calibrated list from S-003. Take the top 20 by estimated value.\n"
                    "For each business, search the relevant state SOS UCC database for filings. "
                    "Start with the state from the business address.\n"
                    "Record per filing: filing_number, filing_date, lapse_date, status "
                    "(active/lapsed/terminated), secured_party_name, collateral_description.\n"
                    "Flag: is_sba_backed (secured party contains 'SBA' or 'Small Business'), "
                    "is_all_assets ('all assets' in collateral).\n"
                    "Useful starting points: state SOS websites vary — try searching "
                    "\"<state> UCC search\" or use opencorporates.com as a fallback."
                ),
                "status": "open",
                "depends_on": ["S-003"],
                "output_file": f"outputs/signals/ucc_{slug}_{ts}.json",
            },
            {
                "id": "S-005",
                "title": "Collect SBA loan data for top 20",
                "description": (
                    "Read the calibrated list from S-003. Take the top 20 by estimated value.\n"
                    "Search SBA loan records at: https://data.sba.gov/dataset/7-a-504-foia\n"
                    "Or use the SBA FOIA bulk CSV files (7a and 504 approvals are public).\n"
                    "Match by: borrower_name (fuzzy) + borrower_city + borrower_state.\n"
                    "Record per loan: loan_number, program (7a/504), approval_date, "
                    "approved_amount, term_months, bank_name, jobs_supported, naics_code.\n"
                    "Note: SBA data is available in bulk CSV — download and search locally "
                    "rather than scraping the website."
                ),
                "status": "open",
                "depends_on": ["S-003"],
                "output_file": f"outputs/signals/sba_{slug}_{ts}.json",
            },
            {
                "id": "S-006",
                "title": "Collect job postings for top 20",
                "description": (
                    "Read the calibrated list from S-003. Take the top 20 by estimated value.\n"
                    "For each business, search for active job postings:\n"
                    "  1. Search Indeed: https://www.indeed.com/jobs?q=<company_name>&l=<city>\n"
                    "  2. Check the business website careers page if available\n"
                    "  3. Search LinkedIn if accessible\n"
                    "Record per posting: job_title, posted_date, salary_min, salary_max, "
                    "pay_type (hourly/salary), is_active.\n"
                    "Categorize each role: technician / sales / management / admin / driver / other.\n"
                    "Key insight: hiring = growth signal; zero postings = stable or stagnant."
                ),
                "status": "open",
                "depends_on": ["S-003"],
                "output_file": f"outputs/signals/jobs_{slug}_{ts}.json",
            },
            {
                "id": "S-007",
                "title": "Score and rank all businesses",
                "description": (
                    "Read calibrated businesses from S-003 and signals from S-004, S-005, S-006.\n"
                    "Compute an acquisition attractiveness score (0–100) for each business.\n\n"
                    "Scoring weights:\n"
                    "  40%  Estimated enterprise value (scaled within industry range)\n"
                    "  20%  UCC signals: active SBA loan = positive; tax liens = negative; "
                    "       'all assets' collateral = business has real assets\n"
                    "  20%  SBA loan history: has 7(a)/504 = bankable, established\n"
                    "  20%  Job posting activity: hiring = growth; zero postings = stable\n\n"
                    "Output all businesses with scores and a brief signal_summary per business."
                ),
                "status": "open",
                "depends_on": ["S-003", "S-004", "S-005", "S-006"],
                "output_file": f"outputs/scored/{slug}_{ts}.json",
            },
            {
                "id": "S-008",
                "title": "Generate acquisition target report",
                "description": (
                    "Read scored businesses from S-007. Generate a Markdown report.\n\n"
                    "Report structure:\n"
                    "  1. Market Summary: total businesses found, estimated market size, "
                    "     typical valuation range, median revenue/margin\n"
                    "  2. Top 10 Targets: for each — name, location, estimated financials, "
                    "     score breakdown, UCC/SBA/jobs signals, recommended outreach angle\n"
                    "  3. Data Notes: confidence levels, data gaps, methodology\n\n"
                    "The report should be ready to share with a potential investor or acquirer."
                ),
                "status": "open",
                "depends_on": ["S-007"],
                "output_file": f"outputs/reports/{slug}_{ts}.md",
            },
        ],
    }

    out = output or f"prds/{slug}_{ts}.json"
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w") as f:
        json.dump(prd, f, indent=2)
        f.write("\n")

    return out


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python ralph/new_run.py <industry> <location> [output]")
        print('Example: python ralph/new_run.py "HVAC" "Houston, TX"')
        sys.exit(1)

    industry = sys.argv[1]
    location = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) > 3 else None

    path = generate(industry, location, output)

    print(f"✓  PRD created: {path}")
    print(f"")
    print(f"   Check status:  python ralph/prd_utils.py status {path}")
    print(f"   Start loop:    bash ralph/loop.sh {path}")
    print(f"   Dry run (1):   bash ralph/loop.sh {path} 1")
