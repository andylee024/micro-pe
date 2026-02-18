# Scout - Deal Flow Intelligence System

Automated system for finding and evaluating small businesses for acquisition.

## Architecture

```
scout/
├── scrapers/              # Data collection modules
│   ├── google_maps.py     # Universe builder (find all businesses)
│   └── bizbuysell.py      # Benchmark builder (financial distributions)
│
├── utils/                 # Helper functions
│   └── financials.py      # Calculate multiples, apply benchmarks
│
├── outputs/               # All results saved here
│
├── config.py              # Configuration management
├── main.py                # CLI entry point
└── requirements.txt       # Dependencies
```

## How It Works

### The Core Concept

**Use BizBuySell deals to calibrate estimates for Google Maps businesses**

```
1. Google Maps → Find ALL HVAC companies in Houston (100 businesses)
2. BizBuySell → Scrape 20 HVAC deals to build financial benchmarks:
   - Median revenue: $650K
   - Median cash flow: $195K (30% margin)
   - Median multiple: 3.5x EBITDA

3. Apply benchmarks → Estimate financials for all 100 Google Maps businesses
```

### Data Flow

```
Universe (Google Maps)          Benchmarks (BizBuySell)
──────────────────────         ────────────────────────
• Business name                • Revenue distributions
• Location                     • Cash flow / EBITDA
• Phone, website               • Valuation multiples
• Rating, review count         • Profit margins

                  ↓

         Calibrated Businesses
         ─────────────────────
         • All Google Maps data
         • Estimated revenue
         • Estimated cash flow
         • Estimated value
         • Confidence level
```

## Setup

### 1. Install Dependencies

```bash
cd scout
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure API Keys

```bash
cp .env.example .env
# Edit .env and add your Google Maps API key
```

Get Google Maps API key:
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Enable **Places API (New)**
3. Create API key
4. Add billing (has $200/month free tier)

## Usage

### Command: `universe`

Find all businesses in a category/location using Google Maps.

```bash
python main.py universe "HVAC contractor" "Houston, TX"
```

**Output:**
- Lists all businesses found
- Summary statistics
- Saves to: `outputs/universe_HVAC_contractor_YYYYMMDD_HHMMSS.json`
- Cost: ~$1 per 60 businesses

**Example:**
```
Building Universe: HVAC contractor in Houston, TX
✓ Found 60 businesses

Preview (first 5):
1. ABC Heating & Air
   Address: 123 Main St, Houston, TX 77001
   Phone: (713) 555-1234
   Rating: 4.8⭐ (245 reviews)

Summary:
Total businesses: 60
With phone: 58
With website: 42
Average rating: 4.35⭐
Estimated API cost: $1.05
```

### Command: `benchmarks`

Build financial benchmarks by scraping BizBuySell deals.

```bash
python main.py benchmarks "HVAC" 20
```

**Output:**
- Scrapes up to 20 BizBuySell listings
- Calculates benchmark distributions
- Saves deals and benchmarks to `outputs/`

**Example:**
```
Building Benchmarks: HVAC
✓ Scraped 18 deals

Benchmarks:
Complete deals: 15/18
Revenue (median): $650,000
Cash Flow (median): $195,000
EBITDA Multiple (median): 3.5x
Margin (median): 30%
```

### Command: `pipeline`

Run full pipeline: universe + benchmarks + calibration.

```bash
python main.py pipeline "HVAC" "Houston, TX" 20
```

**Output:**
- Builds business universe
- Builds financial benchmarks
- Applies benchmarks to estimate values
- Ranks businesses by estimated value
- Saves calibrated results

**Example:**
```
Full Pipeline: HVAC in Houston, TX

[1/3] Building business universe...
✓ Found 60 businesses

[2/3] Building financial benchmarks...
✓ Scraped 18 deals
Benchmarks: $650K revenue, 3.5x multiple, 30% margin

[3/3] Applying benchmarks to universe...

Top 10 Businesses (by estimated value):
1. Premium HVAC Services
   Location: Houston, TX
   Rating: 4.9⭐ (450 reviews)
   Est. Revenue: $975,000
   Est. Cash Flow: $292,500
   Est. Value: $1,023,750
   Confidence: medium

✓ Saved calibrated results to: outputs/calibrated_HVAC_20260213_143052.json
```

## Output Files

All results saved to `outputs/` directory:

- `universe_*.json` - Google Maps search results
- `deals_*.json` - BizBuySell scraped deals
- `benchmarks_*.json` - Calculated financial benchmarks
- `calibrated_*.json` - Businesses with estimated values

## Cost Estimates

**Google Maps API:**
- $0.032 per search + $0.017 per business
- ~$1.05 for 60 businesses
- With $200/month free tier: ~11,000 businesses/month free

**BizBuySell:**
- Free (web scraping)
- Rate limited to ~1 request/second
- Uses undetected-chromedriver to bypass bot detection

## Examples

### Find backflow testing companies in Texas

```bash
# Build universe
python main.py universe "backflow testing" "Houston, TX"

# Get financial benchmarks
python main.py benchmarks "backflow testing" 15

# Full pipeline with calibration
python main.py pipeline "backflow testing" "Houston, TX" 15
```

### Compare multiple locations

```bash
python main.py universe "HVAC" "Houston, TX"
python main.py universe "HVAC" "Dallas, TX"
python main.py universe "HVAC" "Austin, TX"

# Use same benchmarks for all
python main.py benchmarks "HVAC" 30
```

## Troubleshooting

### Google Maps API Errors

**"Invalid API key"**
- Check `.env` file has correct key
- Verify Places API is enabled in Google Cloud Console

**"Billing must be enabled"**
- Add billing account (has $200/month free tier)

### BizBuySell Scraping Issues

**"Could not find any listing links"**
- Site structure may have changed
- Check if site is accessible in browser
- Try with fewer listings first

**Bot detection / Access denied**
- Script uses undetected-chromedriver to bypass
- If still blocked, try again later
- Consider using slower rate limiting

## FDD Extraction (NEW)

Extract unit economics from Franchise Disclosure Documents automatically.

See: **[README_FDD.md](README_FDD.md)** for full documentation.

```bash
# Quick start
python download_sample_fdd.py  # Get sample FDDs
python fdd_extractor_poc.py    # Extract financial data
```

**Extracts from Item 19:**
- Revenue metrics (median, quartiles, ranges)
- EBITDA margins and profitability
- Operating expenses breakdown
- Sample sizes and confidence levels

## Roadmap

**Current (MVP):**
- ✅ Google Maps universe building
- ✅ BizBuySell benchmark scraping
- ✅ Financial calibration
- ✅ JSON output
- ✅ FDD extraction (Proof of Concept)

**Next Steps:**
- [ ] FDD database integration (alternative to California DFPI)
- [ ] Multi-franchise FDD batch processing
- [ ] SQLite database storage
- [ ] CSV export for mail merge
- [ ] Multi-state searches
- [ ] Business age enrichment
- [ ] Scoring and ranking algorithms
- [ ] Terminal UI (Dexter-style)

## Technical Details

**Dependencies:**
- `googlemaps` - Google Maps Places API client
- `selenium` - Web browser automation
- `undetected-chromedriver` - Bypasses bot detection
- `python-dotenv` - Environment variable management

**Python Version:** 3.11+

**Platform:** macOS, Linux (Windows untested)

## License

Internal use only - Holt Ventures
