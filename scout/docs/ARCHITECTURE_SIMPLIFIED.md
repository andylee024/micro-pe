# Technical Architecture: Data Collection Tools
**Version:** 1.0 (Simplified)
**Date:** February 16, 2026
**Focus:** Raw data collection only

---

## 1. System Overview

### What We're Building
**Two standalone data collection tools that agents can use:**

1. **Minnesota FDD Scraper** - Download FDDs, extract Item 19 text
2. **Google Maps Competition Finder** - Find competing businesses

### What We're NOT Building
- ❌ Aggregation/synthesis layer
- ❌ Report generation
- ❌ LLM-based parsing
- ❌ CLI orchestration
- ❌ Benchmark calculation

**Agents handle all synthesis. We provide clean raw data.**

---

## 2. Architecture Diagram

```
┌─────────────────────────────────────────┐
│  AGENT                                  │
│  (Claude Code, Custom Agent, etc.)      │
└────┬─────────────────────┬──────────────┘
     │                     │
     │ uses tools          │ uses tools
     │                     │
     ▼                     ▼
┌────────────────┐    ┌────────────────┐
│ Minnesota FDD  │    │ Google Maps    │
│ Scraper Tool   │    │ Finder Tool    │
└────┬───────────┘    └────┬───────────┘
     │                     │
     │ outputs             │ outputs
     │                     │
     ▼                     ▼
┌────────────────┐    ┌────────────────┐
│ FDD Data       │    │ Competitor     │
│ (JSON)         │    │ Data (JSON)    │
│                │    │                │
│ - PDFs         │    │ - Place IDs    │
│ - Metadata     │    │ - Addresses    │
│ - Item 19 text │    │ - Ratings      │
│ - Raw data     │    │ - Coordinates  │
└────────────────┘    └────────────────┘
```

---

## 3. Tool Specifications

### 3.1 Minnesota FDD Scraper

#### **Purpose**
Download FDD PDFs from Minnesota CARDS database and extract raw text.

#### **Technology**
- **Playwright** (headless browser)
- **PyMuPDF** (PDF text extraction)
- **httpx** (HTTP client)
- **Pydantic** (data validation)

#### **Process Flow**
```
1. Navigate to Minnesota CARDS search
   └─> https://www.cards.commerce.state.mn.us/

2. Search by keyword (e.g., "car wash")
   └─> Parse search results

3. For each FDD found:
   ├─> Download PDF to outputs/fdds/
   ├─> Extract metadata (brand, year, size)
   └─> Extract Item 19 text (if present)

4. Return JSON with all data
```

#### **Input Schema**
```python
class FDDSearchInput(BaseModel):
    industry: str                    # "car wash"
    max_results: int = 10            # Max FDDs to return
    download_pdfs: bool = True       # Download PDFs?
    extract_item19: bool = True      # Extract Item 19 text?
```

#### **Output Schema**
```python
class FDDSearchResult(BaseModel):
    source: str = "minnesota_cards"
    search_date: datetime
    industry: str
    total_found: int
    results: List[FDDDocument]

class FDDDocument(BaseModel):
    franchise_name: str
    fdd_year: int
    fdd_date: Optional[date]
    pdf_url: str
    pdf_path: Optional[str]           # Local path if downloaded
    pdf_size_mb: Optional[float]
    has_item_19: bool
    item_19_text: Optional[str]       # Raw text, no parsing
    item_19_length: Optional[int]     # Character count
    registrant_info: RegistrantInfo

class RegistrantInfo(BaseModel):
    name: str
    address: Optional[str]
    city: Optional[str]
    state: Optional[str]
    registration_date: Optional[date]
```

#### **Caching**
- **PDFs:** Cache for 90 days (FDDs don't change)
- **Search results:** Cache for 30 days
- **Cache key:** `{industry}_{max_results}_{date}`

#### **Error Handling**
```python
# If search returns no results
→ Return empty results list, log warning

# If PDF download fails
→ Retry 3x with exponential backoff
→ If still fails, skip PDF but return metadata

# If Item 19 extraction fails
→ Set has_item_19=False, item_19_text=None
→ Continue processing

# If entire search fails
→ Raise clear exception with diagnostic info
```

#### **Rate Limiting**
- 2-3 seconds between page requests
- 5 seconds between PDF downloads
- Respect robots.txt

---

### 3.2 Google Maps Competition Finder

#### **Purpose**
Find all competing businesses in a geography using Google Maps Places API.

#### **Technology**
- **Google Maps Places API** (Text Search + Place Details)
- **googlemaps** Python library
- **Pydantic** (data validation)

#### **Process Flow**
```
1. Text Search: Find businesses by query + location
   └─> API: places.text_search(query, location, radius)

2. For each place returned:
   └─> Get Place Details (ratings, reviews, contact info)

3. Return JSON with all data
```

#### **Input Schema**
```python
class MapsSearchInput(BaseModel):
    query: str                       # "car wash"
    location: str                    # "Los Angeles, CA"
    radius_miles: float = 25         # Search radius
    max_results: int = 100           # Max places to return
```

#### **Output Schema**
```python
class MapsSearchResult(BaseModel):
    source: str = "google_maps"
    search_date: datetime
    query: str
    location: str
    radius_miles: float
    total_results: int
    results: List[PlaceData]

class PlaceData(BaseModel):
    place_id: str
    name: str
    address: str
    formatted_address: str
    lat: float
    lng: float
    rating: Optional[float]           # 0-5 stars
    review_count: Optional[int]
    phone: Optional[str]
    website: Optional[str]
    google_maps_url: str              # Clickable link
    business_status: str              # OPERATIONAL, CLOSED, etc.
    types: List[str]                  # ["car_wash", "point_of_interest"]
    price_level: Optional[int]        # 0-4 (0=free, 4=expensive)
    opening_hours: Optional[dict]     # If available
    photos: Optional[List[str]]       # Photo URLs if available
```

#### **Caching**
- **Search results:** Cache for 7 days (competition changes)
- **Cache key:** `{query}_{location}_{radius}_{date}`

#### **Error Handling**
```python
# If API quota exceeded
→ Raise QuotaExceededError with clear message
→ Agent decides whether to retry later

# If location not found
→ Raise LocationNotFoundError
→ Suggest alternative location formats

# If no results found
→ Return empty results list
→ Log search params for debugging

# If API error
→ Retry 3x with exponential backoff
→ If still fails, raise with diagnostic info
```

#### **Rate Limiting**
- Google Maps API limit: 10 requests/second
- Batch place details requests when possible
- Use pagination for large result sets

---

## 4. Implementation Details

### 4.1 Project Structure

```
scout/
├── tools/
│   ├── __init__.py
│   ├── base.py                    # Base Tool class
│   ├── minnesota_fdd.py          # FDD scraper implementation
│   └── google_maps.py            # Maps finder implementation
│
├── models/
│   ├── __init__.py
│   ├── fdd.py                    # FDD Pydantic models
│   └── maps.py                   # Maps Pydantic models
│
├── utils/
│   ├── __init__.py
│   ├── cache.py                  # Caching utilities
│   ├── retry.py                  # Retry logic
│   └── pdf.py                    # PDF extraction helpers
│
├── config/
│   ├── __init__.py
│   └── settings.py               # Configuration
│
├── tests/
│   ├── __init__.py
│   ├── test_minnesota_fdd.py
│   ├── test_google_maps.py
│   └── fixtures/                 # Test data
│
├── outputs/
│   ├── fdds/                     # Downloaded PDFs
│   ├── cache/                    # Cached responses
│   └── raw_data/                 # Raw JSON outputs
│
├── requirements.txt
└── README.md
```

### 4.2 Base Tool Class

```python
# tools/base.py

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pydantic import BaseModel
import json
from datetime import datetime
from pathlib import Path

class Tool(ABC):
    """Base class for all data collection tools"""

    def __init__(self, cache_dir: Optional[Path] = None):
        self.cache_dir = cache_dir or Path("outputs/cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    @abstractmethod
    def search(self, **kwargs) -> Dict[str, Any]:
        """
        Execute search and return raw data.

        All search methods should return a dict with:
        - source: str (tool identifier)
        - search_date: datetime
        - results: List[dict] (raw data)
        """
        pass

    @abstractmethod
    def get_output_schema(self) -> type[BaseModel]:
        """Return Pydantic model for output validation"""
        pass

    def save(self, data: Dict, filename: str):
        """Save raw data to JSON file"""
        output_path = Path("outputs/raw_data") / filename
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)

        return output_path

    def load_cache(self, cache_key: str) -> Optional[Dict]:
        """Load cached data if available and not expired"""
        cache_file = self.cache_dir / f"{cache_key}.json"
        if not cache_file.exists():
            return None

        with open(cache_file, 'r') as f:
            cached = json.load(f)

        # Check if cache is expired
        if self._is_cache_expired(cached):
            return None

        return cached

    def save_cache(self, cache_key: str, data: Dict, ttl_days: int):
        """Save data to cache with expiration"""
        cache_file = self.cache_dir / f"{cache_key}.json"

        cached_data = {
            "cached_at": datetime.now().isoformat(),
            "ttl_days": ttl_days,
            "data": data
        }

        with open(cache_file, 'w') as f:
            json.dump(cached_data, f, indent=2, default=str)

    def _is_cache_expired(self, cached: Dict) -> bool:
        """Check if cached data is expired"""
        cached_at = datetime.fromisoformat(cached["cached_at"])
        ttl_days = cached["ttl_days"]
        age_days = (datetime.now() - cached_at).days
        return age_days > ttl_days
```

### 4.3 Minnesota FDD Tool Implementation

```python
# tools/minnesota_fdd.py

from playwright.sync_api import sync_playwright
import fitz  # PyMuPDF
from pathlib import Path
from typing import Dict, Any, Optional
from .base import Tool
from models.fdd import FDDSearchResult, FDDDocument

class MinnesotaFDDScraper(Tool):
    """Scrape FDD documents from Minnesota CARDS database"""

    BASE_URL = "https://www.cards.commerce.state.mn.us/"
    CACHE_TTL_DAYS = 90  # FDDs don't change often

    def search(
        self,
        industry: str,
        max_results: int = 10,
        download_pdfs: bool = True,
        extract_item19: bool = True
    ) -> Dict[str, Any]:
        """
        Search for FDDs by industry keyword.

        Returns raw dict (use get_output_schema() for Pydantic validation)
        """
        cache_key = f"fdd_{industry}_{max_results}"

        # Check cache
        cached = self.load_cache(cache_key)
        if cached:
            return cached["data"]

        # Scrape
        results = self._scrape_fdds(industry, max_results)

        # Download PDFs if requested
        if download_pdfs:
            for fdd in results:
                self._download_pdf(fdd)

        # Extract Item 19 if requested
        if extract_item19:
            for fdd in results:
                if fdd.get("pdf_path"):
                    self._extract_item19(fdd)

        # Build response
        response = {
            "source": "minnesota_cards",
            "search_date": datetime.now().isoformat(),
            "industry": industry,
            "total_found": len(results),
            "results": results
        }

        # Cache results
        self.save_cache(cache_key, response, self.CACHE_TTL_DAYS)

        return response

    def _scrape_fdds(self, industry: str, max_results: int) -> List[Dict]:
        """Use Playwright to scrape Minnesota CARDS"""
        results = []

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            # Navigate and search
            page.goto(self.BASE_URL)
            page.fill("input[name='search']", industry)
            page.click("button[type='submit']")
            page.wait_for_selector(".results")

            # Parse results
            items = page.query_selector_all(".fdd-item")[:max_results]

            for item in items:
                fdd_data = self._parse_fdd_item(item)
                results.append(fdd_data)

                # Rate limiting
                time.sleep(2)

            browser.close()

        return results

    def _parse_fdd_item(self, element) -> Dict:
        """Parse a single FDD result element"""
        return {
            "franchise_name": element.query_selector(".brand-name").text_content(),
            "fdd_year": int(element.query_selector(".year").text_content()),
            "pdf_url": element.query_selector("a.download").get_attribute("href"),
            # ... extract other metadata
        }

    def _download_pdf(self, fdd: Dict):
        """Download PDF and save to outputs/fdds/"""
        url = fdd["pdf_url"]
        filename = f"{fdd['franchise_name']}_{fdd['fdd_year']}.pdf"
        path = Path("outputs/fdds") / filename

        # Download with retry logic
        response = httpx.get(url, timeout=60)
        path.write_bytes(response.content)

        fdd["pdf_path"] = str(path)
        fdd["pdf_size_mb"] = round(path.stat().st_size / 1024 / 1024, 2)

    def _extract_item19(self, fdd: Dict):
        """Extract Item 19 text from PDF"""
        pdf_path = fdd["pdf_path"]

        with fitz.open(pdf_path) as doc:
            full_text = ""
            for page in doc:
                full_text += page.get_text()

        # Find Item 19 section
        item19_text = self._find_item19_section(full_text)

        if item19_text:
            fdd["has_item_19"] = True
            fdd["item_19_text"] = item19_text
            fdd["item_19_length"] = len(item19_text)
        else:
            fdd["has_item_19"] = False
            fdd["item_19_text"] = None

    def _find_item19_section(self, text: str) -> Optional[str]:
        """Find Item 19 section using pattern matching"""
        import re

        # Pattern: ITEM 19 ... ITEM 20 (or end)
        pattern = r"ITEM\s+19[\s\S]*?(?=ITEM\s+20|$)"
        match = re.search(pattern, text, re.IGNORECASE)

        if match:
            return match.group(0).strip()

        return None

    def get_output_schema(self):
        return FDDSearchResult
```

### 4.4 Google Maps Tool Implementation

```python
# tools/google_maps.py

import googlemaps
from datetime import datetime
from typing import Dict, Any
from .base import Tool
from models.maps import MapsSearchResult, PlaceData

class GoogleMapsCompetitionFinder(Tool):
    """Find competing businesses using Google Maps Places API"""

    CACHE_TTL_DAYS = 7  # Competition data changes

    def __init__(self, api_key: str, **kwargs):
        super().__init__(**kwargs)
        self.client = googlemaps.Client(key=api_key)

    def search(
        self,
        query: str,
        location: str,
        radius_miles: float = 25,
        max_results: int = 100
    ) -> Dict[str, Any]:
        """
        Search for businesses by query + location.

        Returns raw dict with full place data.
        """
        cache_key = f"maps_{query}_{location}_{radius_miles}"

        # Check cache
        cached = self.load_cache(cache_key)
        if cached:
            return cached["data"]

        # Convert miles to meters for API
        radius_meters = int(radius_miles * 1609.34)

        # Text search
        places = self.client.places(
            query=query,
            location=location,
            radius=radius_meters
        )

        # Get details for each place
        results = []
        for place in places.get("results", [])[:max_results]:
            place_details = self._get_place_details(place["place_id"])
            results.append(place_details)

            # Rate limiting (10 req/sec max)
            time.sleep(0.1)

        # Build response
        response = {
            "source": "google_maps",
            "search_date": datetime.now().isoformat(),
            "query": query,
            "location": location,
            "radius_miles": radius_miles,
            "total_results": len(results),
            "results": results
        }

        # Cache results
        self.save_cache(cache_key, response, self.CACHE_TTL_DAYS)

        return response

    def _get_place_details(self, place_id: str) -> Dict:
        """Get full details for a place"""
        details = self.client.place(place_id)["result"]

        return {
            "place_id": place_id,
            "name": details.get("name"),
            "address": details.get("vicinity"),
            "formatted_address": details.get("formatted_address"),
            "lat": details["geometry"]["location"]["lat"],
            "lng": details["geometry"]["location"]["lng"],
            "rating": details.get("rating"),
            "review_count": details.get("user_ratings_total"),
            "phone": details.get("formatted_phone_number"),
            "website": details.get("website"),
            "google_maps_url": details.get("url"),
            "business_status": details.get("business_status"),
            "types": details.get("types", []),
            "price_level": details.get("price_level"),
            "opening_hours": details.get("opening_hours"),
        }

    def get_output_schema(self):
        return MapsSearchResult
```

---

## 5. Usage Examples

### Example 1: Agent researching car washes

```python
from tools import MinnesotaFDDScraper, GoogleMapsCompetitionFinder

# Initialize tools
fdd_scraper = MinnesotaFDDScraper()
maps_finder = GoogleMapsCompetitionFinder(api_key=os.getenv("GOOGLE_MAPS_API_KEY"))

# Get FDD data
fdd_data = fdd_scraper.search(
    industry="car wash",
    max_results=5,
    download_pdfs=True,
    extract_item19=True
)

print(f"Found {fdd_data['total_found']} FDDs")
for fdd in fdd_data['results']:
    print(f"- {fdd['franchise_name']} ({fdd['fdd_year']})")
    if fdd['has_item_19']:
        print(f"  Item 19: {fdd['item_19_length']} chars")

# Get competition data
competition = maps_finder.search(
    query="car wash",
    location="Los Angeles, CA",
    radius_miles=25
)

print(f"\nFound {competition['total_results']} competitors")
for place in competition['results'][:5]:
    print(f"- {place['name']}")
    print(f"  {place['address']}")
    print(f"  Rating: {place['rating']} ({place['review_count']} reviews)")

# Agent now has raw data and can synthesize
```

### Example 2: Saving results

```python
# Search and save to JSON
fdd_data = fdd_scraper.search(industry="hvac", max_results=10)
fdd_scraper.save(fdd_data, "hvac_fdds_2026-02-16.json")

competition = maps_finder.search(query="hvac", location="San Diego, CA")
maps_finder.save(competition, "hvac_competition_sandiego_2026-02-16.json")
```

---

## 6. Testing Strategy

### Unit Tests

```python
# tests/test_minnesota_fdd.py

def test_fdd_search():
    scraper = MinnesotaFDDScraper()
    results = scraper.search(industry="test", max_results=1)

    assert results["source"] == "minnesota_cards"
    assert "search_date" in results
    assert "results" in results

def test_item19_extraction():
    # Test with fixture PDF
    fdd = {"pdf_path": "tests/fixtures/sample_fdd.pdf"}
    scraper._extract_item19(fdd)

    assert fdd["has_item_19"] == True
    assert len(fdd["item_19_text"]) > 100

# tests/test_google_maps.py

def test_maps_search():
    finder = GoogleMapsCompetitionFinder(api_key="test_key")
    results = finder.search(query="car wash", location="Los Angeles")

    assert results["source"] == "google_maps"
    assert results["query"] == "car wash"
    assert len(results["results"]) > 0
```

### Integration Tests

```python
@pytest.mark.integration
def test_full_fdd_pipeline():
    """Test complete FDD scraping flow"""
    scraper = MinnesotaFDDScraper()

    results = scraper.search(
        industry="car wash",
        max_results=1,
        download_pdfs=True,
        extract_item19=True
    )

    assert results["total_found"] >= 1
    fdd = results["results"][0]
    assert Path(fdd["pdf_path"]).exists()
    assert fdd["has_item_19"] in [True, False]
```

---

## 7. Configuration

### Environment Variables

```bash
# .env
GOOGLE_MAPS_API_KEY=AIza...
```

### Settings

```python
# config/settings.py

from pathlib import Path

# Directories
OUTPUT_DIR = Path("outputs")
FDD_DIR = OUTPUT_DIR / "fdds"
CACHE_DIR = OUTPUT_DIR / "cache"
RAW_DATA_DIR = OUTPUT_DIR / "raw_data"

# Cache TTLs
FDD_CACHE_DAYS = 90
MAPS_CACHE_DAYS = 7

# Rate limiting
MINNESOTA_REQUEST_DELAY = 2  # seconds
MINNESOTA_PDF_DELAY = 5      # seconds
GOOGLE_MAPS_REQUEST_DELAY = 0.1  # seconds

# Retry settings
MAX_RETRIES = 3
RETRY_BACKOFF = 2  # exponential backoff multiplier
```

---

## 8. Error Handling

### Exception Hierarchy

```python
class ToolError(Exception):
    """Base exception for all tool errors"""
    pass

class ScraperError(ToolError):
    """Error during web scraping"""
    pass

class PDFDownloadError(ToolError):
    """Error downloading PDF"""
    pass

class ExtractionError(ToolError):
    """Error extracting data"""
    pass

class APIError(ToolError):
    """Error calling external API"""
    pass

class QuotaExceededError(APIError):
    """API quota exceeded"""
    pass
```

### Retry Decorator

```python
# utils/retry.py

from functools import wraps
import time

def retry(max_attempts=3, backoff=2):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
                    wait = backoff ** attempt
                    time.sleep(wait)
            return None
        return wrapper
    return decorator
```

---

## 9. Performance

### Targets

| Operation | Target | Notes |
|-----------|--------|-------|
| FDD search (5 results) | <60 seconds | Including downloads |
| FDD PDF download | <10 seconds | Per PDF |
| Item 19 extraction | <5 seconds | Per PDF |
| Maps search (100 results) | <30 seconds | Including details |

### Optimizations

1. **Caching** - Cache everything aggressively
2. **Parallel downloads** - Download PDFs in parallel when possible
3. **Lazy loading** - Only download/extract what's requested
4. **Connection pooling** - Reuse HTTP connections

---

## 10. Security

### API Keys
- Store in `.env` file
- Never commit to git
- Use environment variables in production

### PDF Downloads
- Validate URLs before downloading
- Scan for malware (future)
- Limit file sizes

### Rate Limiting
- Respect robots.txt
- Don't hammer servers
- Use delays between requests

---

## 11. Success Criteria

**v1.0 Ready When:**

**Minnesota FDD Tool:**
- [ ] Can search and return results
- [ ] Can download PDFs reliably
- [ ] Can extract Item 19 text
- [ ] Returns clean JSON
- [ ] Has caching working
- [ ] 95%+ success rate on 20 test searches

**Google Maps Tool:**
- [ ] Can search and return results
- [ ] Returns complete place data
- [ ] Includes Google Maps URLs
- [ ] Returns clean JSON
- [ ] Has caching working
- [ ] 95%+ success rate on 20 test searches

**Both Tools:**
- [ ] Unit tests passing
- [ ] Integration tests passing
- [ ] Documentation complete
- [ ] Example usage documented

---

## 12. Timeline

**Week 1: Minnesota FDD Tool** (5 days)
- Day 1-2: Build Playwright scraper
- Day 3: Add PDF download + caching
- Day 4: Add Item 19 extraction
- Day 5: Tests + documentation

**Week 2: Google Maps Tool** (5 days)
- Day 1-2: Build Maps API integration
- Day 3: Add place details fetching
- Day 4: Add caching
- Day 5: Tests + documentation

**Week 3: Polish** (3 days)
- Day 1: Integration tests
- Day 2: Error handling refinement
- Day 3: Final documentation + examples

**Total: ~3 weeks to production-ready tools**

---

**Status:** Ready for implementation

**Next Step:** Start Week 1 - Build Minnesota FDD Tool
