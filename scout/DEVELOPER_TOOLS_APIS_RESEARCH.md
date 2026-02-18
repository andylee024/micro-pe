# Developer Tools & Financial APIs Research - Technical Exemplars for Scout

**Research Date:** February 17, 2026
**Purpose:** Study developer tools and financial APIs to inform Scout's technical architecture

---

## Executive Summary

**Key Finding:** The financial dev tools landscape has matured significantly (2024-2026). Open-source terminals (OpenBB), autonomous agents (Dexter), and affordable APIs ($0-500/mo) have democratized financial product development.

**Relevance to Scout:**
- **Dexter** (GitHub: virattt/dexter) = Perfect architectural template for Scout
- **OpenBB** = Open-source terminal shows it's possible
- **Financial APIs** = Proven patterns for data aggregation

---

## EXEMPLAR 1: Dexter - Autonomous Financial Research Agent

**Source:** [GitHub: virattt/dexter](https://github.com/virattt/dexter) | [Medium: Dexter Deep Dive](https://medium.com/coding-nexus/dexter-the-200-line-open-source-financial-agent-that-thinks-for-itself-b22031a5c66f)

### What It Is

**Positioning:** "Think Claude Code, but built specifically for financial research"

**Released:** 2024
**Language:** Python
**Lines of Code:** ~200 (core logic)
**Architecture:** Autonomous agent with self-reflection

### How It Works

```python
# Simplified Dexter workflow:

def dexter_research(question):
    """
    Autonomous research agent that:
    1. Breaks question into tasks
    2. Executes tasks using tools
    3. Validates its own work
    4. Refines until confident
    """

    # Step 1: Task Planning
    tasks = llm.generate_research_plan(question)
    # e.g., "What's Apple's revenue?"
    # → ["Get Apple ticker", "Fetch financials", "Extract revenue"]

    # Step 2: Execute Tasks
    results = []
    for task in tasks:
        result = execute_tool(task)  # Calls APIs, scrapes data
        results.append(result)

    # Step 3: Self-Reflection
    confidence = llm.validate_results(results)

    if confidence < 0.8:
        # Refine and retry
        refined_tasks = llm.refine_plan(tasks, results)
        return dexter_research(refined_tasks)

    # Step 4: Final Answer
    return llm.synthesize_answer(results)
```

### Technical Architecture

```
┌─────────────────────────────────────────────────┐
│ CLI Interface (cli.py)                          │
│ - Accepts user question                         │
│ - Streams progress updates                      │
│ - Logs to scratchpad.jsonl                      │
└─────────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────────┐
│ Agent Core (agent.py)                           │
│ - Task planning                                 │
│ - Self-reflection                               │
│ - Tool orchestration                            │
└─────────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────────┐
│ Tool Layer (tools/)                             │
│ - Stock data (Alpha Vantage, Finnhub)          │
│ - SEC filings (Edgar)                           │
│ - News (NewsAPI)                                │
│ - Calculator                                    │
└─────────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────────┐
│ LLM (Claude/GPT)                                │
│ - Reasoning engine                              │
│ - Multi-agent validation                        │
└─────────────────────────────────────────────────┘
```

### Key Features to Borrow

#### 1. **Autonomous Task Planning**

**Dexter's approach:** LLM breaks complex question into sub-tasks

**Scout Application:**
```
User Query: "Should I acquire ABC Backflow in Houston?"

Scout Task Planning:
┌────────────────────────────────────────────────┐
│ Generated Research Plan (5 tasks):             │
├────────────────────────────────────────────────┤
│ 1. Find business in Google Maps                │
│ 2. Get Houston HVAC benchmarks from BizBuySell│
│ 3. Analyze competition (5-mile radius)         │
│ 4. Check Reddit for operator insights          │
│ 5. Estimate valuation & compare to benchmarks  │
└────────────────────────────────────────────────┘

Auto-executing tasks...

[1/5] ✓ Found ABC Backflow (4.7⭐, 203 reviews)
[2/5] ✓ Scraped 18 HVAC deals → Median: $650K rev, 3.5x multiple
[3/5] ✓ Found 89 competitors, ABC ranks #23
[4/5] ✓ Reddit: 12 threads, "backflow profitable but competitive"
[5/5] ✓ Est. value: $900K (asking 3.75x, market 3.5-4.5x = FAIR)

Final Answer: ✅ PURSUE
Confidence: 85% (based on 5 validated data points)
```

#### 2. **Self-Reflection & Validation**

**Dexter's approach:** Multi-agent validation (agents check each other's work)

**Scout Application:**
```python
class ValidationAgent:
    def validate_estimate(self, business, estimate):
        """Check if revenue estimate is reasonable"""

        # Validation 1: Compare to benchmarks
        if estimate['revenue'] > benchmark['p95']:
            return {
                'valid': False,
                'reason': 'Estimate exceeds 95th percentile',
                'action': 'Revise downward'
            }

        # Validation 2: Check against multiple proxies
        proxies = {
            'review_count': business.reviews * 3500,  # $3500/review
            'rating_adjusted': business.reviews * 4000 * (business.rating / 5.0),
            'industry_median': benchmark['median']
        }

        if max(proxies.values()) / min(proxies.values()) > 2:
            return {
                'valid': False,
                'reason': 'Proxies diverge >2x (low confidence)',
                'action': 'Flag as uncertain, request more data'
            }

        # Validation 3: Sanity check
        if estimate['revenue'] < 100000:  # $100K minimum
            return {
                'valid': False,
                'reason': 'Below minimum viable business size',
                'action': 'Recheck data quality'
            }

        return {'valid': True, 'confidence': 0.85}
```

#### 3. **JSONL Scratchpad Logging**

**Dexter feature:** Every tool call logged to JSONL file

```jsonl
{"timestamp": "2026-02-17T10:15:00Z", "tool": "google_maps", "query": "backflow testing houston", "results": 89}
{"timestamp": "2026-02-17T10:15:05Z", "tool": "bizbuysell", "industry": "HVAC", "deals_found": 18}
{"timestamp": "2026-02-17T10:15:12Z", "tool": "calculator", "operation": "median_multiple", "result": 3.5}
{"timestamp": "2026-02-17T10:15:15Z", "tool": "validator", "confidence": 0.85, "flags": []}
```

**Scout Application:**
- Debug failed research queries
- Audit trail for investors
- Improve prompts based on logs
- Replay queries

#### 4. **Streaming Progress Updates**

**Dexter feature:** Real-time CLI updates as agent works

```bash
$ dexter "What's Apple's revenue growth?"

🤔 Planning research...
   → Task 1: Get Apple's ticker symbol
   → Task 2: Fetch last 3 years financials
   → Task 3: Calculate YoY growth

🔍 Executing tasks...
   ✓ Task 1 complete: AAPL
   ✓ Task 2 complete: Downloaded 10-Ks
   ⏳ Task 3 in progress...

📊 Results:
   FY2023: $383B (+7.8%)
   FY2022: $365B (+2.5%)
   FY2021: $356B (+33.3%)

   Avg 3-year growth: 14.5% CAGR

🎯 Confidence: 95% (validated against SEC filings)
```

**Scout Application:** Same streaming UX

---

## EXEMPLAR 2: OpenBB - Open Source Financial Terminal

**Source:** [GitHub: OpenBB-finance/OpenBB](https://github.com/OpenBB-finance/OpenBB) | [TechCrunch](https://techcrunch.com/2024/10/07/fintech-openbb-aims-to-be-more-than-an-open-source-bloomberg-terminal/)

### What It Is

**Positioning:** "Free alternative to the $20,000 Bloomberg Terminal"

**Launched:** 2021
**Users:** 50,000+
**Funding:** $8.5M seed (OSS Capital, Google angel Ram Shriram)
**License:** AGPLv3

### Architecture: "Connect Once, Consume Everywhere"

```
┌─────────────────────────────────────────────────┐
│ Open Data Platform (ODP)                        │
│ - Unified data layer                            │
│ - Proprietary + licensed + public data          │
│ - Single integration point                      │
└─────────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────────┐
│ Data Connectors (50+ sources)                   │
│ - Alpha Vantage, Polygon, Finnhub              │
│ - SEC Edgar, News APIs                          │
│ - Crypto exchanges                              │
│ - Alternative data                              │
└─────────────────────────────────────────────────┘
              ↓
┌────────────────────────────────────────────────┐
│ Consumption Interfaces                         │
├────────────────────────────────────────────────┤
│ • Python SDK (for quants)                      │
│ • CLI Terminal (for power users)               │
│ • Excel Add-In (for analysts)                  │
│ • REST API (for apps)                          │
│ • MCP Server (for AI agents)                   │
└────────────────────────────────────────────────┘
```

### Key Features to Borrow

#### 1. **Unified Data Layer**

**OpenBB pattern:** Abstract data sources behind single API

**Scout Application:**
```python
# Scout Unified Data API

from scout import DataPlatform

scout = DataPlatform()

# Single interface for all sources
business = scout.get_business("ABC Backflow", location="Houston")

# Behind the scenes, Scout queries:
# - Google Maps (basic info)
# - BizBuySell (benchmarks)
# - Reddit (sentiment)
# - FDD database (franchise comps)
# - PE ownership database (consolidation intel)

# User doesn't care WHERE data came from
print(business.revenue_estimate)  # $800K
print(business.data_sources)  # ['google_maps', 'bizbuysell_benchmark', 'fdd_comp']
```

#### 2. **Multi-Interface Support**

**OpenBB offers:** Python, CLI, Excel, REST API, AI agents

**Scout Application:**
```python
# Interface 1: Python SDK
import scout
biz = scout.search("backflow houston")[0]
print(biz.valuation)

# Interface 2: CLI
$ scout search "backflow houston" --top 5

# Interface 3: Excel Add-In
=SCOUT("ABC Backflow", "revenue")

# Interface 4: REST API
GET /api/v1/businesses?industry=backflow&location=houston

# Interface 5: MCP Server (for Claude, etc.)
# Claude: "Find backflow businesses in Houston"
# → Calls Scout MCP server → Returns results
```

#### 3. **Plugin Architecture**

**OpenBB pattern:** Community can add data sources

**Scout Application:**
```python
# Scout plugin for new data source

from scout.plugins import DataSourcePlugin

class YelpPlugin(DataSourcePlugin):
    name = "yelp"
    priority = 3  # Lower priority than Google Maps

    def search(self, query):
        # Scrape Yelp for businesses
        return results

    def enrich(self, business):
        # Add Yelp reviews, photos
        return enriched_data

# Register plugin
scout.register_plugin(YelpPlugin())

# Now Scout automatically queries Yelp too
```

#### 4. **Open Source but Monetizable**

**OpenBB model:**
- Core platform: Open source (AGPLv3)
- Premium data feeds: Paid
- Enterprise features: Paid (hosted, SSO, priority support)

**Scout Application:**
```
Free (Open Source):
├── Google Maps data
├── Basic benchmarks
├── CLI & Python SDK
└── Export to CSV

Pro ($39/mo):
├── All free features
├── BizBuySell real-time scraping
├── Reddit sentiment analysis
├── AI-generated memos
└── Excel add-in

Enterprise ($499/mo):
├── All Pro features
├── API access (unlimited)
├── Multi-user team accounts
├── Deal rooms & collaboration
└── Priority support
```

---

## EXEMPLAR 3: Financial Data APIs

### API Comparison Matrix (2025-2026)

| API | Free Tier | Paid Plans | Best For | Status |
|-----|-----------|------------|----------|--------|
| **Alpha Vantage** | 25 req/day | $49-899/mo | Fundamentals, indicators | Active |
| **Polygon.io** | 5 req/min | $199-999/mo | Real-time, WebSockets | Active |
| **Finnhub** | 60 req/min | $59-399/mo | Global markets, generous free tier | Active |
| **Twelve Data** | 800 req/day | $29-299/mo | Reliability, international | Active |
| **IEX Cloud** | - | - | - | **SHUT DOWN Aug 2024** |

### Deep Dive: Financial API Patterns

#### **Alpha Vantage** - Fundamental Data API

**Source:** [Alpha Vantage API Guide](https://alphalog.ai/blog/alphavantage-api-complete-guide)

```python
# Alpha Vantage pattern

import requests

API_KEY = "your_key"
BASE_URL = "https://www.alphavantage.co/query"

# Time series data
response = requests.get(BASE_URL, params={
    'function': 'TIME_SERIES_DAILY',
    'symbol': 'AAPL',
    'apikey': API_KEY
})

data = response.json()
# Returns: {"Meta Data": {...}, "Time Series (Daily)": {...}}

# Technical indicators (50+ built-in)
response = requests.get(BASE_URL, params={
    'function': 'SMA',  # Simple Moving Average
    'symbol': 'AAPL',
    'interval': 'daily',
    'time_period': 50,
    'apikey': API_KEY
})

# Company fundamentals
response = requests.get(BASE_URL, params={
    'function': 'OVERVIEW',
    'symbol': 'AAPL',
    'apikey': API_KEY
})
# Returns: Revenue, EBITDA, PE ratio, etc.
```

**Scout Equivalent:**
```python
# Scout API (similar pattern)

import scout

API_KEY = "your_key"
scout_client = scout.Client(api_key=API_KEY)

# Business search
businesses = scout_client.search(
    industry='backflow testing',
    location='Houston, TX'
)

# Business details
business = scout_client.get_business('ChIJ...')  # place_id
# Returns: {name, address, rating, reviews, estimated_revenue, ...}

# Industry benchmarks
benchmarks = scout_client.get_benchmarks(industry='HVAC')
# Returns: {median_revenue, median_margin, median_multiple, ...}

# Market analysis
market = scout_client.analyze_market(
    industry='backflow testing',
    geography='Texas'
)
# Returns: {total_businesses, competition_level, pe_activity, ...}
```

#### **Finnhub** - Real-Time Market Data

**Source:** [Finnhub API Docs](https://finnhub.io/docs/api)

**Key Pattern:** WebSocket streaming for real-time data

```python
import websocket

def on_message(ws, message):
    print(f"Received: {message}")

def on_error(ws, error):
    print(f"Error: {error}")

# WebSocket connection for real-time data
ws = websocket.WebSocketApp(
    f"wss://ws.finnhub.io?token={API_KEY}",
    on_message=on_message,
    on_error=on_error
)

# Subscribe to stock updates
ws.send('{"type":"subscribe","symbol":"AAPL"}')

ws.run_forever()
```

**Scout Equivalent:**
```python
# Scout WebSocket for real-time deal alerts

import scout

ws = scout.WebSocket(api_key=API_KEY)

# Subscribe to new businesses matching criteria
ws.subscribe('new_businesses', filters={
    'industry': 'backflow testing',
    'location': 'Texas',
    'owner_age': '>60',
    'rating': '>4.0'
})

# Real-time callback
def on_new_target(business):
    print(f"🎯 New target: {business.name} (score: {business.acquisition_score})")
    # Auto-add to watchlist, send Slack alert, etc.

ws.on('new_business', on_new_target)
ws.connect()
```

#### **Twelve Data** - Comprehensive Market Data

**Source:** [Twelve Data API](https://twelvedata.com/)

**Key Feature:** 99.95% uptime, ultra-low latency (~170ms)

```python
import requests

BASE_URL = "https://api.twelvedata.com"

# Multiple symbols in single request
response = requests.get(f"{BASE_URL}/time_series", params={
    'symbol': 'AAPL,MSFT,GOOGL',
    'interval': '1day',
    'apikey': API_KEY
})

# ETF holdings
response = requests.get(f"{BASE_URL}/etf", params={
    'symbol': 'SPY',
    'apikey': API_KEY
})

# Economic indicators
response = requests.get(f"{BASE_URL}/economic_indicator", params={
    'country': 'US',
    'indicator': 'GDP',
    'apikey': API_KEY
})
```

**Scout Pattern:** Batch requests for efficiency

```python
# Scout batch API

# Search multiple industries at once
results = scout_client.batch_search([
    {'industry': 'HVAC', 'location': 'Houston'},
    {'industry': 'backflow', 'location': 'Dallas'},
    {'industry': 'portable sanitation', 'location': 'Austin'}
])

# Get benchmarks for multiple industries
benchmarks = scout_client.batch_benchmarks([
    'HVAC', 'backflow', 'portable sanitation'
])

# More efficient than 3 separate API calls
```

---

## EXEMPLAR 4: Fintech Infrastructure APIs

### Plaid - Banking Data Connectivity

**Source:** [Plaid API](https://plaid.com/)

**Use Case:** Connect to bank accounts, get transaction data

```python
from plaid import Client
from plaid.api import plaid_api

# Initialize Plaid client
client = plaid_api.PlaidApi(plaid.ApiClient(configuration))

# Link user's bank account
link_token_request = LinkTokenCreateRequest(
    user=LinkTokenCreateRequestUser(client_user_id='user-123'),
    client_name="Scout",
    products=[Products("transactions")],
    country_codes=[CountryCode('US')],
    language='en'
)

response = client.link_token_create(link_token_request)
link_token = response['link_token']

# User completes Plaid Link flow in UI
# You get an access_token

# Fetch transactions
transactions_request = TransactionsGetRequest(
    access_token=access_token,
    start_date='2025-01-01',
    end_date='2025-02-17'
)

response = client.transactions_get(transactions_request)
transactions = response['transactions']
```

**Scout Equivalent (for post-acquisition):**

```python
# Scout: Connect acquired business's bank account

scout.link_business_bank(
    business_id='abc-backflow',
    plaid_token=access_token
)

# Auto-track financial performance
performance = scout.get_performance('abc-backflow')
# Returns: {
#   'revenue_ytd': 650000,
#   'vs_previous_year': '+8.3%',
#   'vs_acquisition_model': '+2.1%',
#   'alerts': ['Revenue trending above forecast']
# }
```

### Stripe - Payment Infrastructure

**Pattern:** Not directly applicable to Scout, but shows how to build developer-friendly APIs

```python
import stripe

stripe.api_key = "sk_test_..."

# Create customer
customer = stripe.Customer.create(
    email="customer@example.com",
    source=token  # Card token from Stripe.js
)

# Charge customer
charge = stripe.Charge.create(
    amount=2000,  # $20.00
    currency="usd",
    customer=customer.id,
    description="Scout Pro Subscription"
)
```

**Lesson for Scout:** Simple, intuitive API design

---

## Technical Architecture for Scout (Based on Exemplars)

### Recommended Stack

**Core Framework:**
```
Language: Python 3.11+
CLI Framework: Click or Typer
Agent Framework: LangChain or custom (like Dexter)
LLM: Claude 3.5 Sonnet (Anthropic API)
Database: SQLite (local-first, like OpenBB)
```

**Data Sources:**
```
Primary:
├── Google Maps API (business discovery)
├── Custom scrapers (BizBuySell, FDD, Reddit)
└── Manual curation (PE ownership)

Future:
├── Plaid (post-acquisition financial tracking)
├── Clearbit/ZoomInfo (contact enrichment)
└── Crunchbase (PE/VC intelligence)
```

**Infrastructure:**
```
API Server: FastAPI (REST + WebSocket)
Caching: Redis (for expensive API calls)
Task Queue: Celery (for background scraping)
Deployment: Docker + Fly.io (like OpenBB)
```

### Architecture Diagram

```
┌────────────────────────────────────────────────────┐
│ CLI Interface (cli.py)                             │
│ - Typer framework                                  │
│ - Rich formatting (tables, progress bars)          │
│ - JSONL logging (like Dexter)                      │
└────────────────────────────────────────────────────┘
              ↓
┌────────────────────────────────────────────────────┐
│ Agent Core (agent.py)                              │
│ - Task planning (Claude API)                       │
│ - Self-reflection & validation                     │
│ - Tool orchestration                               │
│ - Streaming updates                                │
└────────────────────────────────────────────────────┘
              ↓
┌────────────────────────────────────────────────────┐
│ Unified Data Platform (data.py)                    │
│ - Like OpenBB's ODP                                │
│ - Abstract all data sources                        │
│ - Caching layer (Redis)                            │
│ - Rate limiting                                    │
└────────────────────────────────────────────────────┘
              ↓
┌────────────────────────────────────────────────────┐
│ Data Sources                                       │
├────────────────────────────────────────────────────┤
│ • Google Maps API (googlemaps Python package)     │
│ • BizBuySell Scraper (Selenium + undetected-chrome)│
│ • Reddit API (PRAW)                                │
│ • FDD Extractor (PyMuPDF + Claude)                │
│ • PE Database (manual curation → SQLite)          │
└────────────────────────────────────────────────────┘
              ↓
┌────────────────────────────────────────────────────┐
│ Storage Layer                                      │
├────────────────────────────────────────────────────┤
│ • SQLite (local database, like OpenBB)            │
│ • JSONL logs (audit trail, like Dexter)          │
│ • CSV exports (mail merge, CRM import)            │
└────────────────────────────────────────────────────┘
```

### Code Structure (Inspired by Dexter + OpenBB)

```
scout/
├── cli.py                  # CLI entry point (Typer)
├── agent.py                # Autonomous agent (like Dexter)
├── data_platform.py        # Unified data layer (like OpenBB ODP)
│
├── sources/                # Data source connectors
│   ├── google_maps.py
│   ├── bizbuysell.py
│   ├── reddit.py
│   ├── fdd.py
│   └── pe_database.py
│
├── tools/                  # Agent tools
│   ├── universe_builder.py    # Find all businesses
│   ├── benchmark_engine.py    # Calculate benchmarks
│   ├── valuation.py           # Estimate values
│   ├── competitor_analysis.py # Analyze competition
│   └── memo_generator.py      # Generate investment memos
│
├── validators/             # Self-reflection agents
│   ├── data_quality.py
│   ├── estimate_validator.py
│   └── red_flag_detector.py
│
├── api/                    # REST API (FastAPI)
│   ├── server.py
│   ├── routes/
│   └── websocket.py
│
├── db/                     # Database
│   ├── schema.sql
│   ├── queries.py
│   └── scout.db
│
└── logs/                   # JSONL logs
    └── scratchpad_*.jsonl
```

---

## Implementation Plan

### Phase 1: Core Agent (Weeks 1-2)

**Goal:** Build Dexter-style autonomous agent

```python
# Minimal viable agent

from anthropic import Anthropic
import json

client = Anthropic(api_key="...")

def scout_agent(question):
    """Autonomous research agent for SMB acquisition"""

    # 1. Task Planning
    planning_prompt = f"""
    Question: {question}

    Break this into research tasks using these tools:
    - google_maps(industry, location) → Find businesses
    - bizbuysell_benchmarks(industry) → Get financial benchmarks
    - reddit_insights(topic) → Market sentiment
    - estimate_value(business, benchmarks) → Valuation

    Return JSON task list.
    """

    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        messages=[{"role": "user", "content": planning_prompt}],
        max_tokens=1024
    )

    tasks = json.loads(response.content[0].text)

    # 2. Execute Tasks
    results = []
    for task in tasks:
        result = execute_tool(task)
        results.append(result)
        print(f"✓ {task['name']}: {result['summary']}")

    # 3. Synthesize Answer
    synthesis_prompt = f"""
    Question: {question}
    Research Results: {json.dumps(results)}

    Provide a clear, actionable answer with:
    - Key findings
    - Recommendation (pursue/pass)
    - Confidence level (0-100%)
    """

    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        messages=[{"role": "user", "content": synthesis_prompt}],
        max_tokens=2048
    )

    return response.content[0].text
```

### Phase 2: Data Platform (Weeks 3-4)

**Goal:** Build OpenBB-style unified data layer

```python
# Unified data platform

class ScoutDataPlatform:
    def __init__(self):
        self.sources = {
            'google_maps': GoogleMapsSource(),
            'bizbuysell': BizBuySellSource(),
            'reddit': RedditSource(),
            'fdd': FDDSource()
        }
        self.cache = RedisCache()

    def search(self, industry, location):
        """Search across all sources"""

        cache_key = f"{industry}:{location}"
        if cached := self.cache.get(cache_key):
            return cached

        # Query all sources in parallel
        from concurrent.futures import ThreadPoolExecutor

        with ThreadPoolExecutor() as executor:
            futures = {
                name: executor.submit(source.search, industry, location)
                for name, source in self.sources.items()
            }

            results = {
                name: future.result()
                for name, future in futures.items()
            }

        # Merge and deduplicate
        merged = self.merge_results(results)

        self.cache.set(cache_key, merged, ttl=86400)  # 24 hours

        return merged
```

### Phase 3: API Layer (Weeks 5-6)

**Goal:** FastAPI REST + WebSocket (like Finnhub pattern)

```python
from fastapi import FastAPI, WebSocket
from fastapi.responses import StreamingResponse

app = FastAPI(title="Scout API")
scout = ScoutDataPlatform()

@app.get("/api/v1/businesses")
async def search_businesses(industry: str, location: str):
    """Search for businesses"""
    results = scout.search(industry, location)
    return results

@app.get("/api/v1/benchmarks/{industry}")
async def get_benchmarks(industry: str):
    """Get financial benchmarks"""
    return scout.get_benchmarks(industry)

@app.websocket("/ws/alerts")
async def websocket_endpoint(websocket: WebSocket):
    """Real-time deal alerts"""
    await websocket.accept()

    # Subscribe to new targets
    async for business in scout.stream_new_businesses():
        if business.acquisition_score > 75:
            await websocket.send_json({
                'type': 'new_target',
                'business': business.dict()
            })
```

---

## Key Takeaways

### 1. **Dexter Pattern = Perfect for Scout**
- Autonomous agent with task planning
- Self-reflection and validation
- JSONL logging for debugging
- Streaming CLI updates
- **Borrow this architecture directly**

### 2. **OpenBB Pattern = Data Aggregation**
- Unified data platform ("connect once")
- Multi-interface (CLI, API, Excel)
- Plugin architecture
- Open source core + paid premium

### 3. **Financial APIs = Proven Patterns**
- Simple REST APIs (Alpha Vantage style)
- WebSocket streaming (Finnhub style)
- Batch requests (Twelve Data style)
- Generous free tiers (all of them)

### 4. **Tech Stack Recommendation**
```
Frontend: CLI (Typer + Rich)
Backend: Python 3.11+ (FastAPI)
Agent: Claude 3.5 Sonnet (Anthropic API)
Database: SQLite (local-first)
Caching: Redis
Deployment: Docker + Fly.io
```

### 5. **Monetization Strategy**
```
Free (Open Source):
├── CLI tool
├── Python SDK
├── Basic features
└── Community support

Pro ($39/mo):
├── All free features
├── API access
├── Real-time scraping
└── AI features

Enterprise ($499/mo):
├── All Pro features
├── Multi-user
├── Deal rooms
└── Priority support
```

---

## Next Steps

1. **Clone Dexter** ([virattt/dexter](https://github.com/virattt/dexter))
   - Study the code (~200 lines core)
   - Understand task planning pattern
   - Adapt for SMB acquisition

2. **Clone OpenBB** ([OpenBB-finance/OpenBB](https://github.com/OpenBB-finance/OpenBB))
   - Study data platform architecture
   - Understand plugin system
   - Adapt unified data layer

3. **Test Financial APIs**
   - Sign up for Alpha Vantage (free tier)
   - Try Finnhub (60 req/min free)
   - Understand API patterns

4. **Build Scout MVP**
   - Week 1-2: Agent core (Dexter pattern)
   - Week 3-4: Data platform (OpenBB pattern)
   - Week 5-6: API layer (FastAPI + WebSocket)

---

## Full Source Code Examples

### Dexter-Style Agent Implementation

```python
# scout/agent.py

from anthropic import Anthropic
import json
from typing import List, Dict
from rich.console import Console
from rich.progress import Progress

console = Console()
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

class ScoutAgent:
    """Autonomous research agent for SMB acquisition"""

    def __init__(self):
        self.tools = {
            'search_businesses': self.search_businesses,
            'get_benchmarks': self.get_benchmarks,
            'analyze_competition': self.analyze_competition,
            'estimate_value': self.estimate_value
        }

    def research(self, question: str) -> Dict:
        """Main research loop"""

        # Step 1: Plan
        console.print("🤔 Planning research...", style="bold blue")
        tasks = self._plan_tasks(question)

        for i, task in enumerate(tasks, 1):
            console.print(f"   → Task {i}: {task['description']}")

        # Step 2: Execute
        console.print("\n🔍 Executing tasks...", style="bold green")
        results = []

        with Progress() as progress:
            task_progress = progress.add_task(
                "[green]Processing...",
                total=len(tasks)
            )

            for task in tasks:
                result = self._execute_task(task)
                results.append(result)
                console.print(f"   ✓ Task {task['name']} complete")
                progress.update(task_progress, advance=1)

        # Step 3: Validate
        console.print("\n🔬 Validating results...", style="bold yellow")
        confidence = self._validate_results(results)

        if confidence < 0.7:
            console.print("   ⚠️ Low confidence, refining...", style="yellow")
            # Refine and retry
            return self.research(question)

        # Step 4: Synthesize
        console.print("\n📊 Synthesizing answer...", style="bold magenta")
        answer = self._synthesize_answer(question, results)

        console.print(f"\n🎯 Confidence: {confidence*100:.0f}%", style="bold green")

        return {
            'answer': answer,
            'confidence': confidence,
            'tasks_executed': len(tasks),
            'results': results
        }

    def _plan_tasks(self, question: str) -> List[Dict]:
        """Use Claude to plan research tasks"""
        # Implementation...
        pass

    def _execute_task(self, task: Dict) -> Dict:
        """Execute a single research task"""
        tool_name = task['tool']
        tool_func = self.tools.get(tool_name)

        if not tool_func:
            raise ValueError(f"Unknown tool: {tool_name}")

        return tool_func(**task['params'])

    def _validate_results(self, results: List[Dict]) -> float:
        """Validate research results, return confidence score"""
        # Implementation...
        pass

    def _synthesize_answer(self, question: str, results: List[Dict]) -> str:
        """Synthesize final answer from research results"""
        # Implementation...
        pass
```

---

**Full research document saved to:**
`/Users/andylee/Projects/micro-pe/scout/DEVELOPER_TOOLS_APIS_RESEARCH.md`

---

## Sources

1. [GitHub: virattt/dexter](https://github.com/virattt/dexter) - Autonomous financial research agent
2. [GitHub: OpenBB-finance/OpenBB](https://github.com/OpenBB-finance/OpenBB) - Open-source financial platform
3. [TechCrunch: OpenBB Funding](https://techcrunch.com/2024/10/07/fintech-openbb-aims-to-be-more-than-an-open-source-bloomberg-terminal/)
4. [Alpha Vantage API Guide](https://www.alphavantage.co/iexcloud_shutdown_analysis_and_migration/)
5. [Finnhub API Docs](https://finnhub.io/docs/api)
6. [Twelve Data API](https://twelvedata.com/)
7. [Plaid Developer Docs](https://plaid.com/)
8. [Financial Data APIs 2025 Comparison](https://www.ksred.com/the-complete-guide-to-financial-data-apis-building-your-own-stock-market-data-pipeline-in-2025/)
