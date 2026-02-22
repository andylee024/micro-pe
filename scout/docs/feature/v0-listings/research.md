# v0-listings: Research & Technical Strategy

**Author:** Scout Engineering
**Date:** 2026-02-22
**Status:** Draft — For CTO Review
**Scope:** Data pipeline design for SMB acquisition listings aggregation

---

## Executive Summary

Scout needs to answer one question reliably: *"Given a thesis, what businesses are for sale right now?"*

The current architecture cannot answer this. Google Maps tells us who *exists*; it cannot tell us who is *for sale*. BizBuySell — our intended primary source — is returning zero results due to a broken scraper. The benchmark pipeline is built on empty data.

This document examines the marketplace landscape, evaluates technical approaches to multi-source aggregation, and recommends an architecture for v0-listings: the pipeline that consistently fetches, stores, and serves for-sale listings matched to a user thesis.

**Key findings:**
1. BizBuySell is the dominant source (40–45k active listings) and is **less protected than we assumed** — third-party scrapers confirm it does not require Cloudflare bypass; standard Selenium works
2. The BizBuySell scraper failed because its CSS selectors are wrong, not because of bot detection — this is a simpler fix than we planned
3. A **scheduled ETL + local SQLite store** is the right V1 architecture — not live agent queries
4. Vector search for thesis matching is premature; structured SQL filters + LLM query parsing is sufficient for V1
5. Cross-source deduplication is important but not blocking; V1 should ingest one source cleanly first

---

## 1. Problem Definition

### 1.1 The Two Problems

**Problem A — Listings Aggregation:** The user submits a thesis ("HVAC businesses in Texas, asking price under $1M") and expects to see a list of businesses currently for sale matching that thesis. Today we have no pipeline that does this.

**Problem B — Synthesis:** Once the user sees the listings, they need context: are these listings priced fairly? Is this a buyer's market? What are the red flags? This requires AI synthesis on top of the data. **Problem B is out of scope for V0.**

### 1.2 What "Consistently Getting Listings" Requires

A reliable listings pipeline must:
- Fetch listings from one or more marketplace sources on a schedule
- Normalize listings to a common data model (name, price, revenue, cash flow, location, broker)
- Store listings locally so queries are fast and don't depend on live source availability
- Support filtered queries: by industry, location, price range, revenue, cash flow multiple
- Handle source failures gracefully (retry, fallback to cached data)
- Deduplicate when the same business appears on multiple sources

### 1.3 What We're Not Solving Yet

- Synthesis / AI analysis of listings (V1+)
- Natural language thesis → complex query translation (V1+)
- Cross-source deduplication at scale (V1+)
- Real-time listing updates (V1+)
- Full-text / semantic search on descriptions (V1+)

---

## 2. Marketplace Landscape

### 2.1 Platform Overview

| Platform | Active Listings | Geography | Financial Fields | Accessibility |
|---|---|---|---|---|
| **BizBuySell** | 40–45k | US + some intl | Price, Revenue, Cash Flow, SDE, Days Listed | ✅ Scrapable, no Cloudflare |
| **BizQuest** | ~17k | North America | Price, Revenue, Cash Flow (partial) | ✅ Scrapable |
| **BusinessBroker.net** | 28–30k | US (all states) | Price, limited financials | ✅ Standard protection |
| **BusinessesForSale** | 57–59k | Global (130 countries) | Price, partial financials | ✅ Standard protection |
| **BizBen** | ~4k | California only | Price, Revenue, Cash Flow | ✅ Scrapable |
| **DealStream** | ~15k | Global (200 countries) | Price, financial metrics | ⚠️ API deprecated |
| **Sunbelt Network** | 10k+ | Global (250 offices) | Limited public data | ❌ Broker network only |
| **LoopNet** | 100k+ | US commercial RE | Price, lease terms | ⚠️ Commercial RE only, not SMB |
| **Axial** | 10k+/yr | North America (LMM) | Gated | ❌ Private network, membership required |

### 2.2 The Critical Finding on BizBuySell

Our prior assumption was that BizBuySell was protected by Cloudflare and required `undetected-chromedriver`. **This is incorrect.**

Multiple lines of evidence contradict this:
- Third-party Apify scrapers for BizBuySell are widely documented and actively maintained (as of 2026), which would be impossible if the site deployed serious bot mitigation
- GitHub documentation from scraper builders describes BizBuySell as "not too difficult to scrape compared to others"
- ScrapingBee has a documented BizBuySell endpoint, implying standard HTTP-level accessibility
- No Cloudflare challenge pages are mentioned in any scraper documentation

**The actual failure mode:** Our scraper uses CSS selectors (`[class*='listing']`, `.listing-price`) that don't match BizBuySell's actual HTML. The site uses a Next.js React frontend — the selectors were written for a different page structure.

**What works:** BizBuySell embeds page data in a `<script id="__NEXT_DATA__">` JSON block (standard Next.js behavior). Extracting this JSON is more reliable than parsing HTML and requires only standard Selenium, not stealth mode.

### 2.3 Data Quality by Source

**BizBuySell** is the highest-quality source for our use case:
- 150+ industry categories with standardized taxonomy
- Financial fields (revenue, cash flow, SDE) disclosed on a high percentage of listings
- Days-on-market tracking
- Broker information
- Active benchmarking data (their "Insight Reports" validate data quality)

**BizQuest** is a good secondary source:
- Owned by the same parent (Network Media Group) but different listings database
- Financials disclosed but less consistently than BizBuySell
- Good for cross-source deduplication validation

**BusinessBroker.net** is acceptable but lower priority:
- Decent volume but financial disclosure is sparse
- Broker-driven; listing quality varies

**For V0, BizBuySell alone is sufficient.** Add BizQuest in V1.

### 2.4 Third-Party Data Access Options

Beyond building our own scraper, two alternatives exist:

**Option A: Apify Marketplace (managed scrapers)**
Apify has BizBuySell, BizQuest, and BusinessBroker.net scrapers maintained by the community. You pay per compute unit consumed (~$5–15/run depending on volume). Advantages: zero scraper maintenance, we consume JSON outputs. Disadvantages: cost, external dependency, less control over scheduling and fields.

**Option B: BizBuySell Data Partnership**
BizBuySell distributes their listings to partners (USA Today, WSJ Business, trade associations). A data partnership agreement would give us a structured feed rather than a scraped HTML page. This is likely a formal business relationship requiring a legal agreement. Worth pursuing at scale, not for V0.

**Recommendation for V0:** Build the scraper ourselves. The fix is simpler than we thought (target `__NEXT_DATA__` JSON, not HTML selectors). This gives us full control over scheduling, field extraction, and caching. Apify is a fallback if the in-house scraper proves unstable.

---

## 3. Technical Architecture Options

### 3.1 The Core Design Question

There are two fundamentally different architectures for serving thesis-based listing queries:

**Architecture A: Scheduled ETL → Local Store → Query**
```
[Scheduled job, nightly]
  BizBuySell scraper → normalize → SQLite store
                           ↓
[User query, real-time]
  "HVAC Texas under $1M" → SQL query against store → results in <100ms
```

**Architecture B: Live Agent (query-time fetch)**
```
[User query]
  "HVAC Texas under $1M" → agent calls BizBuySell live → results in 10–30s
```

### 3.2 Architecture Comparison

| Dimension | Scheduled ETL (A) | Live Agent (B) |
|---|---|---|
| **Query latency** | <100ms (local DB) | 10–30s (live scrape) |
| **Data freshness** | Stale by hours/days | Always current |
| **Reliability** | High (source downtime doesn't affect queries) | Low (depends on source availability) |
| **Implementation complexity** | Medium (ETL + store + query) | Low (one fetch per query) |
| **Infrastructure** | SQLite file (minimal) | Nothing extra |
| **Failure mode** | Stale data served | Query fails entirely |
| **Scalability** | Excellent (DB scales) | Rate-limited by source |

**For a CLI tool used by individual researchers, the trade-off is clear:** users will not wait 30 seconds for a query result. Source downtime cannot block the user. **Architecture A is correct for V0.**

Data freshness is less critical than it appears: business listings turn over slowly. A listing from two days ago is still actionable — the user is doing research, not bidding in real time. Nightly refresh is sufficient.

### 3.3 The OpenBB Insight: Provider Abstraction

OpenBB solves a structurally identical problem: multiple financial data sources (Polygon, Alpha Vantage, Intrinio) return the same conceptual data in incompatible schemas. Their solution is the **Transform-Extract-Transform (TET)** pipeline:

```
User query (normalized)
    → [Input Transform] → source-specific query params
    → [Extract] → raw response from source
    → [Output Transform] → normalized Listing object
```

Each data source is a self-contained "provider" module. The provider handles all source-specific quirks (field name differences, pagination, authentication). The rest of the application only sees normalized `Listing` objects.

**This is exactly what we need.** BizBuySell, BizQuest, and BusinessBroker.net all expose the same concepts — businesses for sale, with price/revenue/cash flow — but in different schemas, HTML structures, and URL patterns.

The right architecture has:
1. A `MarketplaceProvider` abstract base class (the interface)
2. A `BizBuySellProvider` implementation (BizBuySell-specific logic)
3. A `FetchPipeline` that calls all providers and stores normalized results
4. A `ListingStore` (SQLite) that the application queries

This decoupling means adding BizQuest in V1 is a matter of writing one new provider module, not changing the pipeline, the store, or the UI.

### 3.4 Storage: SQLite vs. Other Options

| Option | Size | Query capability | Ops complexity | Right for |
|---|---|---|---|---|
| **JSON file cache** | Any | None (load all into memory) | Zero | Current state; not sufficient for querying |
| **SQLite** | Any | Full SQL (range queries, filters, indexes) | Zero (single file) | ✅ V0 + V1 |
| **PostgreSQL** | Any | Full SQL + advanced indexes | Server required | Multi-user, team deployment |
| **Vector DB (Chroma, etc.)** | <1M records | Semantic similarity only | Python package | Semantic search, not structured filtering |
| **SQLite + sqlite-vec** | <1M records | SQL + vector similarity | Zero | V2+ when semantic thesis matching needed |

**SQLite is the correct choice for V0.** It requires no infrastructure, lives as a single file in `outputs/`, supports indexed range queries (price, revenue, location), and is already part of the Python standard library. If we later need vector search for semantic thesis matching, `sqlite-vec` extends SQLite without requiring a schema migration.

**Schema:**
```sql
CREATE TABLE listings (
    id TEXT PRIMARY KEY,            -- "{source}:{source_id}"
    source TEXT NOT NULL,           -- "bizbuysell"
    source_id TEXT NOT NULL,        -- BizBuySell's listing ID
    name TEXT NOT NULL,
    industry TEXT,                  -- from search query
    location TEXT,                  -- "Austin, TX"
    state TEXT,                     -- "TX" extracted for fast filtering
    asking_price REAL,              -- USD
    annual_revenue REAL,            -- USD
    cash_flow REAL,                 -- SDE or EBITDA, USD
    asking_multiple REAL,           -- asking_price / cash_flow
    days_on_market INTEGER,
    broker TEXT,
    url TEXT,
    description TEXT,
    listed_at TEXT,                 -- ISO date from source
    fetched_at TEXT NOT NULL        -- ISO datetime when we scraped it
);

-- Indexes for common query patterns
CREATE INDEX idx_industry_state ON listings(industry, state);
CREATE INDEX idx_asking_price ON listings(asking_price);
CREATE INDEX idx_cash_flow ON listings(cash_flow);
CREATE INDEX idx_fetched_at ON listings(fetched_at);

CREATE TABLE scrape_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT NOT NULL,
    industry TEXT NOT NULL,
    location TEXT NOT NULL,
    scraped_at TEXT NOT NULL,
    listing_count INTEGER,
    status TEXT                     -- "ok", "error", "empty"
);
```

### 3.5 Thesis Matching: How to Query Listings

Once we have listings in SQLite, we need to convert a user thesis into a query. There are three approaches:

**Option A: Structured filters (manual)**
The user specifies: `--industry "HVAC" --location "Texas" --max-price 1000000`. Simple SQL `WHERE` clause. Zero AI involvement.

**Option B: LLM query parsing**
User types: `"profitable HVAC businesses in Texas under $1M"`. Claude parses this into structured filters `{industry: "HVAC", state: "TX", max_asking_price: 1000000}`. Single API call (~$0.001), adds ~500ms latency.

**Option C: Semantic / vector search**
Embed user thesis as a vector. Query listings by description similarity. Catches "established customer base", "recurring revenue", "turnkey". Requires embedding model (~22MB), `sqlite-vec` extension, pre-embedded descriptions.

**Recommendation for V0: Option B (LLM query parsing) with Option A as fallback.**

Option A alone is too rigid — users think in natural language, not structured flags. Option C is premature — we don't have enough listing descriptions to make semantic search valuable yet, and the additional complexity isn't justified. Option B uses the AI capability we already have (Anthropic API), adds minimal latency, and unlocks natural language queries immediately.

In V1, add Option C alongside B for the cases where description-level matching matters.

### 3.6 Cross-Source Deduplication

When the same business is listed on BizBuySell and BizQuest, we want to show it once. Deduplication requires matching on imprecise data (business names vary, addresses are formatted differently).

**Three-tier matching:**
1. **Deterministic (exact):** phone number + normalized address. Zero false positives.
2. **Fuzzy:** Levenshtein/token-set similarity on name + address. Catches "Smith's HVAC" vs "Smiths HVAC Services".
3. **Probabilistic:** Weighted score across phone, name, address, industry. Returns a confidence level.

Key signals by strength:
- Phone number: Very strong (unique, stable, rarely changes)
- Address: Strong (stable, but formatting varies)
- Business name: Medium (many variations — abbreviations, punctuation, legal vs. trade name)
- Industry: Weak (confirmation only)
- Price: Very weak (can differ across sources — different asking prices on different platforms)

**Recommendation for V0: Skip deduplication entirely.** V0 ingests only BizBuySell. Deduplication is only needed when ingesting multiple sources. Add it when adding BizQuest in V1.

---

## 4. Freshness Strategy

### 4.1 How Stale is Too Stale?

Business listings typically stay active for 6–12 months. A listing from yesterday is still actionable. The right question isn't "how fresh?" but "how often does data change in ways that affect user decisions?"

| Data element | Change frequency | Impact | Recommended TTL |
|---|---|---|---|
| Listing exists / is active | Medium (~5% of listings change daily) | High (don't show sold businesses) | 1–3 days |
| Asking price | Low (10–20% adjust price during listing lifetime) | High | 3–7 days |
| Financial disclosures | Very low | Medium | 7–14 days |
| Broker contact | Low | Low | 7 days |
| Description | Very low | Low | 14–30 days |

**For V0: Nightly refresh per industry/location pair that has been queried.** Don't proactively scrape everything — only refresh cache for queries users have actually made. This keeps scrape volume low and focused.

### 4.2 Cache Invalidation

The simplest correct strategy: store `fetched_at` on every listing. When querying, check if the most recent `scrape_log` entry for this (source, industry, location) is older than TTL. If so, trigger a background refresh before returning results.

No event-driven invalidation (BizBuySell doesn't have webhooks). No complex cache management. Just: if data is older than N days, re-scrape.

---

## 5. Architecture Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| BizBuySell changes their HTML/Next.js structure | Medium | High — scraper breaks | Abstract the extraction (TET pattern), write regression tests against real output, monitor `scrape_log` empty results as alert |
| BizBuySell adds Cloudflare or stronger bot protection | Low | High | Have Apify as a drop-in fallback; same normalized `Listing` output |
| SQLite file corruption | Very low | Medium | Periodic backup to JSON; scraper can re-build the store from scratch |
| Listing data is incomplete (many listings lack revenue/CF) | High | Medium | Show listings without financial data; don't filter them out, just mark confidence as "unknown" |
| Thesis parsing returns wrong filters | Medium | Medium | Log all parsed queries; allow user to review/override structured filters |

---

## 6. Comparison to Alternatives We Considered

### Why not a pure live-agent approach?

The agent approach (agent fetches sources on each user request, then synthesizes) is compelling because it always returns fresh data and requires no persistent store. Tools like Perplexity for Finance and Dexter use this model for financial research.

However, for a listings product — where the user is **browsing and filtering** a result set, not asking a one-shot research question — an agent approach fails:
- 10–30s latency per query is unusable for interactive browsing
- The user may issue 20+ filter queries in a single session (can't re-scrape each time)
- If BizBuySell is down, the user can't work at all
- Pagination through large result sets is incompatible with live scraping

Agents are the right model for **synthesis** (generating a report, answering follow-up questions). They're the wrong model for **discovery** (browsing a filterable list). V0 is a discovery product.

### Why not Apify?

Apify is a reasonable production path. Paying $5–15 per scrape run in exchange for zero scraper maintenance is a good deal at scale. But:
- It adds an external service dependency and monthly cost for V0
- It reduces our visibility into the raw HTML (harder to debug when it breaks)
- The BizBuySell fix is now understood to be simple (wrong selectors, not bot detection)
- We should validate that we can get clean data ourselves before outsourcing it

Apify is a good fallback if our scraper continues to fail after the selector fix. It's not the right first move.

---

## 7. Recommended V0 Architecture

Based on the analysis above, the recommended V0 architecture is:

```
┌─────────────────────────────────────────────────────────────────────┐
│  FETCH PIPELINE (scheduled, per-industry/location pair)             │
│                                                                     │
│  BizBuySellProvider                                                 │
│   ├── Input transform: (industry, location) → BizBuySell URL       │
│   ├── Extract: undetected-chromedriver → __NEXT_DATA__ JSON        │
│   └── Output transform: JSON → List[Listing]                       │
│                              ↓                                      │
│  FetchPipeline.run(industry, location) → upsert → ListingStore      │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│  LISTING STORE (outputs/listings.db — SQLite)                       │
│                                                                     │
│  Tables: listings, scrape_log                                       │
│  Indexes on: (industry, state), asking_price, cash_flow             │
│  Upserts by id = "{source}:{source_id}" (deduplicates re-scrapes)  │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│  QUERY INTERFACE                                                    │
│                                                                     │
│  ListingStore.search(                                               │
│    industry="HVAC", location="Texas",                               │
│    max_asking_price=1_000_000,                                      │
│    min_cash_flow=150_000,                                           │
│  ) → List[Listing]                                                  │
│                                                                     │
│  Thesis parsing (V0): Claude → {industry, location, filters}       │
└─────────────────────────────────────────────────────────────────────┘
```

### Components to Build

| Component | File | Description |
|---|---|---|
| `Listing` | `scout/domain/listing.py` | Domain model: fields, from_dict/to_dict |
| `MarketplaceProvider` | `data_sources/marketplaces/base.py` | TET interface: input_transform, extract, output_transform |
| `BizBuySellProvider` | `data_sources/marketplaces/bizbuysell.py` | __NEXT_DATA__ extraction + HTML fallback |
| `ListingStore` | `data_sources/marketplaces/store.py` | SQLite upsert + filtered search |
| `FetchPipeline` | `data_sources/marketplaces/pipeline.py` | Orchestrate providers → store |

### What V0 Delivers

A user runs:
```bash
python -c "
from data_sources.marketplaces.pipeline import FetchPipeline
p = FetchPipeline()
listings = p.run('HVAC', 'Texas', max_results=50)
for l in listings:
    print(l.name, l.location, l.asking_price, l.cash_flow)
"
```

And sees 20–50 real HVAC businesses for sale in Texas, with asking prices and cash flow figures where disclosed. This is the foundation everything else is built on.

---

## 8. V1+ Roadmap

Once V0 is working:

**V1 — Second Source + Deduplication**
- Add `BizQuestProvider` (same interface, different HTML)
- Add cross-source deduplication on phone + fuzzy name
- BizBuySell + BizQuest combined → ~60k listings nationally

**V1.5 — Semantic Thesis Matching**
- Add `sqlite-vec` for description embeddings
- `sentence-transformers/all-MiniLM-L6-v2` (~22MB, no server) for local embedding
- Query by semantic similarity in addition to structured filters
- Handles: "established customer base", "recurring revenue", "turnkey operation"

**V2 — Synthesis Layer**
- Agent takes thesis + matching listings → generates research report
- Highlights pricing anomalies (over/underpriced vs. market)
- Synthesizes opportunities and risks from listing language
- Connects to FDD Item 19 for franchise benchmarks

**V3 — UI Integration**
- Terminal UI shows listings instead of (or alongside) Google Maps results
- Filter panel: price range, revenue, cash flow multiple, days listed
- Drill into a listing: full description, broker contact, comparable transactions

---

## Appendix: Key Sources

- [BizBuySell Insight Report (listing volume data)](https://www.bizbuysell.com/insight-report-data-tables/)
- [BizBuySell Apify Scraper documentation](https://apify.com/acquistion-automation/bizbuysell-scraper)
- [OpenBB TET Pipeline architecture](https://openbb.co/blog/the-openbb-platform-data-pipeline)
- [OpenBB Platform design overview](https://openbb.co/blog/exploring-the-architecture-behind-the-openbb-platform)
- [Dexter: autonomous financial research agent](https://github.com/virattt/dexter)
- [sqlite-vec: vector search extension for SQLite](https://github.com/asg017/sqlite-vec)
- [sentence-transformers/all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)
