# Product Specification: Data Collection Tools
**Version:** 1.0
**Date:** February 16, 2026
**Status:** Ready for Implementation

---

## 1. Product Vision

**Build best-in-class data collection tools that AI agents can use to gather raw business intelligence data.**

### Core Principle
**We collect raw data. Agents synthesize it.**

---

## 2. What We Build

### Tool 1: Minnesota FDD Scraper
**Purpose:** Download FDD PDFs and extract basic metadata from Minnesota CARDS database

**Input:**
```python
{
    "industry": "car wash",
    "max_results": 10
}
```

**Output:**
```json
{
    "source": "minnesota_cards",
    "search_date": "2026-02-16",
    "industry": "car wash",
    "results": [
        {
            "franchise_name": "Mister Car Wash",
            "fdd_year": 2024,
            "fdd_date": "2024-03-15",
            "pdf_path": "outputs/fdds/mister_car_wash_2024.pdf",
            "pdf_size_mb": 2.3,
            "pdf_url": "https://...",
            "has_item_19": true,
            "item_19_text": "ITEM 19: FINANCIAL PERFORMANCE...",
            "registrant_info": {
                "name": "Mister Car Wash Holdings, Inc.",
                "address": "123 Main St, Tucson AZ",
                "registration_date": "2024-02-01"
            }
        }
    ]
}
```

**What It Does:**
1. Search Minnesota CARDS by keyword
2. Download FDD PDFs
3. Extract basic metadata (brand, year, size)
4. Extract Item 19 text if present (raw text, no parsing)
5. Save to JSON

**What It Doesn't Do:**
- ❌ Parse financial data (agent does this)
- ❌ Aggregate across brands (agent does this)
- ❌ Calculate benchmarks (agent does this)

---

### Tool 2: Google Maps Competition Finder
**Purpose:** Find all competing businesses in a geography using Google Maps API

**Input:**
```python
{
    "query": "car wash",
    "location": "Los Angeles, CA",
    "radius_miles": 25
}
```

**Output:**
```json
{
    "source": "google_maps",
    "search_date": "2026-02-16",
    "query": "car wash",
    "location": "Los Angeles, CA",
    "radius_miles": 25,
    "total_results": 87,
    "results": [
        {
            "place_id": "ChIJgdBtJhRDk4ARGXWdlhwARgM",
            "name": "Mister Car Wash - Downtown LA",
            "address": "123 Main St, Los Angeles, CA 90012",
            "lat": 34.0522,
            "lng": -118.2437,
            "rating": 4.2,
            "review_count": 156,
            "phone": "+1-323-555-0123",
            "website": "https://mistercarwash.com",
            "google_maps_url": "https://www.google.com/maps/place/?q=place_id:...",
            "business_status": "OPERATIONAL",
            "types": ["car_wash", "point_of_interest"],
            "price_level": 2
        }
    ]
}
```

**What It Does:**
1. Search Google Maps Places API
2. Get detailed info for each place
3. Return raw JSON with all available data
4. Include clickable Google Maps URLs

**What It Doesn't Do:**
- ❌ Calculate density metrics (agent does this)
- ❌ Analyze competition (agent does this)
- ❌ Filter or rank results (agent does this)

---

## 3. Tool Design Principles

### ✅ Good Tool Design
1. **Single Responsibility** - Each tool does ONE thing well
2. **Raw Data Out** - No interpretation, no synthesis
3. **Complete Metadata** - Include source, timestamp, search params
4. **Idempotent** - Same input = same output (with caching)
5. **Error Transparent** - Clear error messages, partial results OK
6. **Agent-Friendly** - JSON output, well-typed, documented

### ❌ Bad Tool Design
1. Trying to be smart (let agents be smart)
2. Aggregating or synthesizing data
3. Making decisions (agents decide)
4. Complex configuration (simple inputs only)
5. Black-box operations (be transparent)

---

## 4. Usage by Agents

### Example: Agent researching car washes

**Step 1: Get FDD data**
```python
from tools import MinnesotaFDDScraper

scraper = MinnesotaFDDScraper()
fdd_data = scraper.search(industry="car wash", max_results=5)
# Agent now has 5 FDDs with Item 19 text

# Agent analyzes Item 19 text with LLM
for fdd in fdd_data["results"]:
    item19 = fdd["item_19_text"]
    # Agent extracts metrics, calculates benchmarks, etc.
```

**Step 2: Get competition data**
```python
from tools import GoogleMapsCompetitionFinder

finder = GoogleMapsCompetitionFinder()
competition = finder.search(
    query="car wash",
    location="Los Angeles, CA",
    radius_miles=25
)
# Agent now has 87 competitors with full details

# Agent analyzes density, calculates saturation, etc.
```

**Step 3: Agent synthesizes**
```
Agent combines FDD benchmarks + competition data + own analysis
Agent writes report/memo/recommendations
```

---

## 5. File Structure

```
scout/
├── tools/
│   ├── __init__.py
│   ├── minnesota_fdd.py        # FDD scraper tool
│   ├── google_maps.py          # Maps finder tool
│   └── base.py                 # Base tool class
│
├── models/
│   ├── __init__.py
│   ├── fdd.py                  # FDD data models
│   └── maps.py                 # Maps data models
│
├── outputs/
│   ├── fdds/                   # Downloaded PDFs
│   ├── cache/                  # Cached API responses
│   └── raw_data/               # Raw JSON outputs
│
├── tests/
│   ├── test_minnesota_fdd.py
│   └── test_google_maps.py
│
└── config/
    ├── settings.py
    └── __init__.py
```

---

## 6. API Design

### Tool Interface (Base Class)
```python
from abc import ABC, abstractmethod
from typing import Dict, Any
from pydantic import BaseModel

class Tool(ABC):
    """Base class for all data collection tools"""

    @abstractmethod
    def search(self, **kwargs) -> Dict[str, Any]:
        """Execute search and return raw data"""
        pass

    @abstractmethod
    def get_schema(self) -> BaseModel:
        """Return Pydantic schema for output"""
        pass

    def save(self, data: Dict, path: str):
        """Save raw data to JSON"""
        with open(path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
```

### Minnesota FDD Tool
```python
class MinnesotaFDDScraper(Tool):
    def search(
        self,
        industry: str,
        max_results: int = 10,
        download_pdfs: bool = True,
        extract_item19: bool = True
    ) -> Dict[str, Any]:
        """
        Search Minnesota CARDS for FDDs

        Args:
            industry: Search keyword (e.g., "car wash")
            max_results: Max number of FDDs to return
            download_pdfs: Whether to download PDFs
            extract_item19: Whether to extract Item 19 text

        Returns:
            Dict with raw FDD data and metadata
        """
        pass
```

### Google Maps Tool
```python
class GoogleMapsCompetitionFinder(Tool):
    def search(
        self,
        query: str,
        location: str,
        radius_miles: float = 25,
        max_results: int = 100
    ) -> Dict[str, Any]:
        """
        Search Google Maps for businesses

        Args:
            query: Search query (e.g., "car wash")
            location: Center point (e.g., "Los Angeles, CA")
            radius_miles: Search radius
            max_results: Max results to return

        Returns:
            Dict with raw competitor data
        """
        pass
```

---

## 7. Success Criteria

### v1.0 Launch Checklist

**Minnesota FDD Tool:**
- [ ] Can search Minnesota CARDS by keyword
- [ ] Can download FDD PDFs
- [ ] Can extract Item 19 text (raw, no parsing)
- [ ] Returns clean JSON with all metadata
- [ ] Caches results (90-day TTL)
- [ ] Clear error messages
- [ ] Works reliably (95%+ success rate)

**Google Maps Tool:**
- [ ] Can search by query + location + radius
- [ ] Returns all available place data
- [ ] Includes Google Maps URLs
- [ ] Returns clean JSON
- [ ] Caches results (7-day TTL)
- [ ] Handles API errors gracefully
- [ ] Works reliably (95%+ success rate)

**General:**
- [ ] Both tools have unit tests
- [ ] Both tools have integration tests
- [ ] Clear documentation for each tool
- [ ] Example usage in README
- [ ] Type hints throughout
- [ ] Pydantic models for all outputs

---

## 8. Non-Goals (Out of Scope)

### What We're NOT Building
- ❌ Report generation
- ❌ Benchmark calculation
- ❌ Data aggregation
- ❌ LLM-based extraction/parsing
- ❌ CLI interface (tools are Python-only)
- ❌ Web dashboard
- ❌ Orchestration layer
- ❌ BizBuySell scraper (future)
- ❌ Reddit scraper (future)

**Why:** Agents handle all synthesis and decision-making. We just provide raw data tools.

---

## 9. Future Tools (Backlog)

When ready, we can add more tools using the same pattern:

1. **BizBuySell Listings Tool** - Get marketplace listings
2. **Reddit Discussion Tool** - Get operator discussions
3. **Public Company Filings Tool** - Get 10-K data
4. **Industry Association Tool** - Get industry reports
5. **Franchise Registry Tool** - Get registration data

Each tool follows same pattern: raw data in, raw JSON out.

---

## 10. Timeline

### Week 1: Minnesota FDD Tool
- [ ] Build scraper with Playwright
- [ ] PDF download + caching
- [ ] Item 19 text extraction
- [ ] JSON output with metadata
- [ ] Tests + documentation

### Week 2: Google Maps Tool
- [ ] Places API integration
- [ ] Location + radius search
- [ ] Full place details
- [ ] JSON output with URLs
- [ ] Tests + documentation

### Week 3: Polish & Testing
- [ ] Integration tests
- [ ] Error handling refinement
- [ ] Documentation
- [ ] Example usage for agents
- [ ] Validation with real searches

**Total:** 3 weeks to production-ready tools

---

## 11. Cost Estimate

**Per Search:**
- Minnesota FDD: Free (public database)
- Google Maps: $0.032 per text search + $0.017 per place detail
  - Example: 100 competitors = $0.032 + (100 × $0.017) = $1.73

**Monthly (assuming 20 searches):**
- FDD searches: $0
- Maps searches: ~$35/month

**Very affordable.** Caching reduces costs significantly.

---

## 12. Questions for Review

1. **Tool Interface:** Does the Tool base class make sense?
2. **Output Format:** Is raw JSON the right format for agents?
3. **Caching:** 90 days for FDDs, 7 days for Maps - OK?
4. **Scope:** Anything missing from Minnesota FDD or Google Maps tools?
5. **Future Tools:** Priority order for BizBuySell, Reddit, etc.?

---

**Status:** Ready for Review → Implementation

**Next Step:** Review and approve, then start Week 1 (Minnesota FDD Tool)
