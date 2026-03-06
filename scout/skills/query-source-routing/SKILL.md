---
name: query-source-routing
description: Deconstruct natural-language market search requests into concrete Google Maps and BizBuySell data-source inputs for Scout's data pipeline. Use when a user asks to search an industry/location market, tighten query targeting, improve source precision, or understand how query text maps to `GoogleMapsDataSource` and `BizBuySellDataSource`.
---

# Query Source Routing

## Overview

Use this skill to convert a user query like "fire protection businesses in Los Angeles" into source-specific fetch inputs for:

1. `GoogleMapsDataSource` (operating business universe)
2. `BizBuySellDataSource` (for-sale listings universe)

Keep `Workflow` source-agnostic. Keep all provider routing logic in source-specific layers.

## Workflow

1. Parse query text into canonical fields:
   - `industry`
   - `location`
2. Build Google Maps fetch input from parsed fields.
3. Build BizBuySell fetch input from parsed fields, including slug/state resolution.
4. Validate that BizBuySell route is precise enough; if not, apply fallback strategy.
5. Return an explicit routing plan before execution.

Use this reference when executing the steps:

- `references/query-deconstruction.md`

Use this reference when choosing BizBuySell category slugs:

- `references/bizbuysell-slugs.md`

## Output Contract

Return a routing plan in this structure:

```json
{
  "parsed_query": {
    "industry": "fire protection",
    "location": "Los Angeles"
  },
  "google_maps": {
    "method": "GoogleMapsTool.search",
    "industry": "fire protection",
    "location": "Los Angeles",
    "max_results": 10,
    "use_cache": false
  },
  "bizbuysell": {
    "method": "BizBuySellProvider.search",
    "listing_query": {
      "industry": "fire protection",
      "location": "Los Angeles",
      "max_results": 10
    },
    "resolved": {
      "industry_slug": "security-established-businesses",
      "state_slug": "california",
      "url": "https://www.bizbuysell.com/california/security-established-businesses-for-sale/"
    }
  }
}
```

If there is uncertainty, include `assumptions` with explicit fallback decisions.
