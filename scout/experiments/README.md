# Experiments Directory

This directory contains raw data and debug artifacts from development and testing.

## Structure

```
experiments/
├── raw_data/          # Sample data from scraper runs
│   ├── google_maps_results.json      # HVAC contractors in Arcadia, CA
│   ├── bizbuysell_results.json       # BizBuySell scraping attempt
│   ├── carwash_urls.json             # Early experiment URLs
│   └── target_carwash.json           # Early experiment data
│
└── debug_html/        # HTML snapshots for debugging scrapers
    ├── bizbuysell_debug.html         # BizBuySell page structure
    ├── ca_sos_results.html            # CA SOS search results
    └── carwash_page.html              # Early experiment page
```

## Purpose

These files are kept for:
- Understanding scraper behavior during development
- Debugging when scrapers break due to site changes
- Reference examples of data structures
- Historical record of what we tried

## Status

**google_maps_results.json** - ✅ Working scraper
Sample output from successful Google Maps API call for HVAC contractors

**bizbuysell_results.json** - ⚠️ Empty
BizBuySell scraper blocked by Akamai bot protection during early tests

**Debug HTML files** - 📸 Snapshots
Saved page HTML for analyzing site structure and CSS selectors

## Not Used in Production

These are **development artifacts only**.

Production code uses:
- `scrapers/google_maps.py` - For universe building
- `scrapers/bizbuysell.py` - For benchmark scraping (with undetected-chromedriver)
- `main.py` - CLI interface

Results are saved to: `outputs/`
