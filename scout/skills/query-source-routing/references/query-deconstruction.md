# Query Deconstruction Playbook

## Objective

Map one natural-language market query into two source-specific method calls:

1. Google Maps operating-business search
2. BizBuySell for-sale listing search

## Canonical Pipeline Context

1. User query is parsed into `industry` + `location`.
2. `Runner` builds `Query`.
3. `Workflow` invokes source adapters independently.
4. Each source normalizes output into canonical models.

## Step 1: Parse Query

Use:

- `scout.shared.query_parser.parse_query(query)`

Output:

- `industry: str`
- `location: str`

If parsing fails, ask for explicit `industry in location` format.

## Step 2: Build Google Maps Input

Target method:

- `data_sources.maps.google_maps.GoogleMapsTool.search(...)`

Map fields directly:

1. `industry <- parsed.industry`
2. `location <- parsed.location`
3. `max_results <- user override or default`
4. `use_cache <- user override or default`

Google Maps is the operating-universe source. Do not apply BizBuySell slug logic here.

## Step 3: Build BizBuySell Input

Target methods:

1. `BizBuySellDataSource.fetch()`
2. `BizBuySellProvider.search(ListingQuery(...))`

Build `ListingQuery`:

1. `industry <- parsed.industry`
2. `location <- parsed.location`
3. `max_results <- user override or default`

Resolve route:

1. `industry_slug = provider._to_industry_slug(industry)`
2. `state_slug = provider._to_state_slug(location)`
3. `url = provider._build_url(listing_query, page=1)`

If no industry slug resolves, provider falls back to `service-businesses`. Treat this as low precision.

## Step 4: Precision Rules

Apply these heuristics before running:

1. If BizBuySell slug is broad (`service-businesses`), call out lower precision.
2. If location resolves only to city and has no state slug, call out geo uncertainty.
3. For fire-related terms, prefer fire/security slug mapping and post-filtering.

## Step 5: Return Explicit Routing Plan

Always return:

1. Parsed fields
2. Google Maps method inputs
3. BizBuySell method inputs
4. Resolved BizBuySell slug + URL
5. Any assumptions/fallbacks

## Fire Protection Example

Input:

- `fire protection services businesses in Los Angeles`

Plan:

1. Parse -> `industry=fire protection`, `location=Los Angeles`
2. Google Maps:
   - `search(industry="fire protection", location="Los Angeles", ...)`
3. BizBuySell:
   - `ListingQuery(industry="fire protection", location="Los Angeles", ...)`
   - resolve -> `industry_slug=security-established-businesses`
   - resolve -> `state_slug=california`
   - URL -> `https://www.bizbuysell.com/california/security-established-businesses-for-sale/`

## Validation Checklist

1. Query parsed successfully.
2. Both source input objects built.
3. BizBuySell URL is explicit and reviewable.
4. Fallback reasoning is included when precision is degraded.
