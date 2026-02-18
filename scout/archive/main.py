#!/usr/bin/env python3
"""
Scout - Deal Flow Intelligence System

Main CLI interface for finding and evaluating businesses
"""

import sys
import json
import os
from datetime import datetime

from config import Config
from scrapers.google_maps import (
    search_google_maps,
    estimate_api_cost,
    get_summary_stats
)
from scrapers.bizbuysell import (
    scrape_bizbuysell,
    calculate_benchmarks
)
from utils.financials import (
    apply_benchmarks,
    rank_businesses
)


def print_header(title):
    """Print formatted header"""
    print(f'\n{"="*60}')
    print(f'{title}')
    print(f'{"="*60}\n')


def save_json(data, filename):
    """Save data to JSON file in outputs directory"""
    os.makedirs(Config.OUTPUT_DIR, exist_ok=True)
    filepath = os.path.join(Config.OUTPUT_DIR, filename)

    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)

    return filepath


def command_universe(industry, location):
    """
    Build business universe using Google Maps

    Usage: python main.py universe "HVAC contractor" "Houston, TX"
    """
    print_header(f'Building Universe: {industry} in {location}')

    # Validate config
    try:
        Config.validate()
    except ValueError as e:
        print(f'❌ Configuration Error:\n{e}\n')
        return

    # Search Google Maps
    print(f'Searching Google Maps...')
    businesses = search_google_maps(
        industry=industry,
        city=location,
        api_key=Config.GOOGLE_MAPS_API_KEY,
        max_results=Config.MAX_GOOGLE_MAPS_RESULTS
    )

    if not businesses:
        print(f'❌ No businesses found\n')
        return

    print(f'✓ Found {len(businesses)} businesses\n')

    # Show first 5
    print('Preview (first 5):')
    for business in businesses[:5]:
        print(f'{business["rank"]}. {business["name"]}')
        print(f'   Address: {business["address"]}')
        print(f'   Phone: {business["phone"] or "N/A"}')
        print(f'   Rating: {business["rating"]}⭐ ({business["review_count"]} reviews)')
        print()

    # Summary stats
    stats = get_summary_stats(businesses)
    cost = estimate_api_cost(len(businesses))

    print_header('Summary')
    print(f'Total businesses: {stats["total"]}')
    print(f'With phone: {stats["with_phone"]}')
    print(f'With website: {stats["with_website"]}')
    print(f'Average rating: {stats["avg_rating"]:.2f}⭐')
    print(f'Estimated API cost: ${cost:.2f}')

    # Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'universe_{industry.replace(" ", "_")}_{timestamp}.json'
    filepath = save_json(businesses, filename)

    print(f'\n✓ Saved to: {filepath}\n')

    return businesses


def command_benchmarks(industry, max_listings=None):
    """
    Build financial benchmarks using BizBuySell

    Usage: python main.py benchmarks "HVAC" 20
    """
    max_listings = max_listings or Config.MAX_BIZBUYSELL_LISTINGS

    print_header(f'Building Benchmarks: {industry}')
    print(f'Scraping up to {max_listings} BizBuySell listings...\n')

    # Scrape BizBuySell
    try:
        deals = scrape_bizbuysell(industry, max_listings)
    except Exception as e:
        print(f'❌ Error scraping BizBuySell: {e}\n')
        return

    if not deals:
        print(f'❌ No deals found\n')
        return

    print(f'\n✓ Scraped {len(deals)} deals\n')

    # Show first 3
    print('Preview (first 3):')
    for deal in deals[:3]:
        print(f'{deal["rank"]}. {deal["title"]}')
        print(f'   Location: {deal["location"]}')
        if deal.get('revenue'):
            print(f'   Revenue: ${deal["revenue"]:,.0f}')
        if deal.get('cash_flow'):
            print(f'   Cash Flow: ${deal["cash_flow"]:,.0f}')
        if deal.get('asking_price'):
            print(f'   Asking Price: ${deal["asking_price"]:,.0f}')
        if deal.get('multiple'):
            print(f'   Multiple: {deal["multiple"]}x')
        if deal.get('margin'):
            print(f'   Margin: {deal["margin"]:.0%}')
        print()

    # Calculate benchmarks
    benchmarks = calculate_benchmarks(deals)

    if 'error' in benchmarks:
        print(f'⚠ Warning: {benchmarks["error"]}\n')
    else:
        print_header('Benchmarks')
        print(f'Complete deals: {benchmarks["complete_deals"]}/{benchmarks["total_deals"]}')
        print(f'\nRevenue (median): ${benchmarks["revenue"]["median"]:,.0f}')
        print(f'Cash Flow (median): ${benchmarks["cash_flow"]["median"]:,.0f}')
        if benchmarks["multiple"]["median"]:
            print(f'EBITDA Multiple (median): {benchmarks["multiple"]["median"]:.1f}x')
        if benchmarks["margin"]["median"]:
            print(f'Margin (median): {benchmarks["margin"]["median"]:.0%}')

    # Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    deals_file = f'deals_{industry.replace(" ", "_")}_{timestamp}.json'
    benchmarks_file = f'benchmarks_{industry.replace(" ", "_")}_{timestamp}.json'

    deals_path = save_json(deals, deals_file)
    benchmarks_path = save_json(benchmarks, benchmarks_file)

    print(f'\n✓ Saved deals to: {deals_path}')
    print(f'✓ Saved benchmarks to: {benchmarks_path}\n')

    return deals, benchmarks


def command_pipeline(industry, location, max_bizbuysell=None):
    """
    Full pipeline: Build universe + benchmarks + apply calibration

    Usage: python main.py pipeline "HVAC" "Houston, TX" 20
    """
    max_bizbuysell = max_bizbuysell or Config.MAX_BIZBUYSELL_LISTINGS

    print_header(f'Full Pipeline: {industry} in {location}')

    # Step 1: Build universe
    print('\n[1/3] Building business universe...')
    businesses = command_universe(industry, location)

    if not businesses:
        return

    # Step 2: Build benchmarks
    print('\n[2/3] Building financial benchmarks...')
    deals, benchmarks = command_benchmarks(industry, max_bizbuysell)

    if not benchmarks or 'error' in benchmarks:
        print('\n⚠ Skipping calibration (no benchmarks available)')
        return

    # Step 3: Apply benchmarks
    print('\n[3/3] Applying benchmarks to universe...')
    calibrated = apply_benchmarks(businesses, benchmarks)

    # Rank by estimated value
    ranked = rank_businesses(calibrated, sort_by='estimated_value')

    # Show top 10
    print_header('Top 10 Businesses (by estimated value)')
    for business in ranked[:10]:
        print(f'{business["rank"]}. {business["name"]}')
        print(f'   Location: {business["city"]}, {business["state"]}')
        print(f'   Rating: {business["rating"]}⭐ ({business["review_count"]} reviews)')
        if business.get('estimated_revenue'):
            print(f'   Est. Revenue: ${business["estimated_revenue"]:,.0f}')
        if business.get('estimated_cash_flow'):
            print(f'   Est. Cash Flow: ${business["estimated_cash_flow"]:,.0f}')
        if business.get('estimated_value'):
            print(f'   Est. Value: ${business["estimated_value"]:,.0f}')
        print(f'   Confidence: {business.get("confidence", "N/A")}')
        print()

    # Save calibrated results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'calibrated_{industry.replace(" ", "_")}_{timestamp}.json'
    filepath = save_json(ranked, filename)

    print(f'✓ Saved calibrated results to: {filepath}\n')

    return ranked


def print_usage():
    """Print usage instructions"""
    print("""
Scout - Deal Flow Intelligence System

Usage:
    python main.py <command> [arguments]

Commands:

    universe <industry> <location>
        Build business universe using Google Maps
        Example: python main.py universe "HVAC contractor" "Houston, TX"

    benchmarks <industry> [max_listings]
        Build financial benchmarks using BizBuySell
        Example: python main.py benchmarks "HVAC" 20

    pipeline <industry> <location> [max_bizbuysell]
        Run full pipeline (universe + benchmarks + calibration)
        Example: python main.py pipeline "HVAC" "Houston, TX" 20

Setup:
    1. Copy .env.example to .env
    2. Add your GOOGLE_MAPS_API_KEY to .env
    3. Run: pip install -r requirements.txt

Output:
    All results saved to: outputs/
    """)


def main():
    """Main CLI entry point"""
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)

    command = sys.argv[1]

    try:
        if command == 'universe':
            if len(sys.argv) < 4:
                print('Usage: python main.py universe "<industry>" "<location>"')
                sys.exit(1)
            command_universe(sys.argv[2], sys.argv[3])

        elif command == 'benchmarks':
            if len(sys.argv) < 3:
                print('Usage: python main.py benchmarks "<industry>" [max_listings]')
                sys.exit(1)
            max_listings = int(sys.argv[3]) if len(sys.argv) > 3 else None
            command_benchmarks(sys.argv[2], max_listings)

        elif command == 'pipeline':
            if len(sys.argv) < 4:
                print('Usage: python main.py pipeline "<industry>" "<location>" [max_bizbuysell]')
                sys.exit(1)
            max_bizbuysell = int(sys.argv[4]) if len(sys.argv) > 4 else None
            command_pipeline(sys.argv[2], sys.argv[3], max_bizbuysell)

        else:
            print(f'Unknown command: {command}')
            print_usage()
            sys.exit(1)

    except KeyboardInterrupt:
        print('\n\n⚠ Interrupted by user\n')
        sys.exit(0)
    except Exception as e:
        print(f'\n❌ Error: {e}\n')
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
