#!/usr/bin/env python3
"""Validate the BizBuySell scraper by running 3 test queries and printing a report.

Exits 1 if any query returns 0 results.

Usage:
    python scripts/validate_listings.py
"""

import sys
import logging

from data_sources.marketplaces.base import ListingQuery
from data_sources.marketplaces.bizbuysell import BizBuySellProvider
from data_sources.marketplaces.validation import validate_batch, check_financial_sanity

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("validate_listings")

TEST_QUERIES = [
    ListingQuery("hvac", "texas", 20),
    ListingQuery("car wash", "california", 20),
    ListingQuery("plumbing", "florida", 20),
]


def main() -> int:
    provider = BizBuySellProvider()
    any_failed = False

    for query in TEST_QUERIES:
        print(f"\n{'='*60}")
        print(f"Query: {query.industry} / {query.location} (max {query.max_results})")
        print(f"{'='*60}")

        try:
            listings = provider.search(query, use_cache=True)
        except Exception as e:
            print(f"  ERROR: {e}")
            any_failed = True
            continue

        if not listings:
            print("  FAIL: 0 listings returned")
            any_failed = True
            continue

        # Validation
        report = validate_batch(listings, query.industry)
        print(f"  Total:     {report.total}")
        print(f"  Relevant:  {report.relevant}")
        print(f"  Precision: {report.precision_pct}%")

        if report.irrelevant_names:
            print(f"  Irrelevant ({len(report.irrelevant_names)}):")
            for name in report.irrelevant_names[:5]:
                print(f"    - {name}")

        # Financial sanity
        warning_count = 0
        for listing in listings:
            warnings = check_financial_sanity(listing)
            warning_count += len(warnings)

        print(f"  Financial warnings: {warning_count}")

        # Sample listings
        print(f"\n  Sample listings:")
        for listing in listings[:3]:
            price_str = f"${listing.asking_price:,.0f}" if listing.asking_price else "N/A"
            cf_str = f"${listing.cash_flow:,.0f}" if listing.cash_flow else "N/A"
            print(f"    [{listing.source_id}] {listing.name}")
            print(f"      Price: {price_str} | CF: {cf_str} | {listing.location}")

    print(f"\n{'='*60}")
    if any_failed:
        print("RESULT: FAIL - one or more queries returned 0 results")
        return 1
    else:
        print("RESULT: PASS - all queries returned results")
        return 0


if __name__ == "__main__":
    sys.exit(main())
