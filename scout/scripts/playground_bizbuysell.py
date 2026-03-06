#!/usr/bin/env python3
"""Playground for tuning BizBuySell query strategies.

Example:
    python scripts/playground_bizbuysell.py "fire protection businesses in Los Angeles" --no-cache
"""

from __future__ import annotations

import argparse
import sys
import time
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from data_sources.marketplaces.base import ListingQuery
from data_sources.marketplaces.bizbuysell import BizBuySellProvider
from scout.shared.query_parser import parse_query

FIRE_KEYWORDS = (
    "fire protection",
    "fire alarm",
    "fire sprinkler",
    "sprinkler",
    "fire suppression",
    "suppression system",
    "extinguisher",
    "alarm system",
)


@dataclass(frozen=True)
class Strategy:
    industry: str
    location: str
    slug: str
    state_slug: str
    url: str


def _is_fire_relevant(name: str, description: str) -> bool:
    text = f"{name} {description}".lower()
    return any(keyword in text for keyword in FIRE_KEYWORDS)


def _candidate_industries(industry: str) -> list[str]:
    provider = BizBuySellProvider()
    normalized = provider._normalize_industry(industry)
    candidates = [normalized or industry]

    if "fire" in normalized or "protection" in normalized:
        candidates.extend(
            [
                "fire protection",
                "fire suppression",
                "fire alarm",
                "security services",
            ]
        )

    # Keep order while removing duplicates.
    deduped: list[str] = []
    seen: set[str] = set()
    for candidate in candidates:
        key = candidate.strip().lower()
        if key and key not in seen:
            deduped.append(candidate.strip())
            seen.add(key)
    return deduped


def build_strategies(industry: str, location: str, max_results: int, limit: int) -> list[Strategy]:
    provider = BizBuySellProvider()
    state_slug = provider._to_state_slug(location) or ""
    location_candidates = [location.strip()]
    if state_slug:
        location_candidates.append(state_slug.replace("-", " "))

    strategies: list[Strategy] = []
    seen_keys: set[tuple[str, str]] = set()
    for industry_candidate in _candidate_industries(industry):
        slug = provider._to_industry_slug(industry_candidate) or "service-businesses"
        for location_candidate in location_candidates:
            state_candidate = provider._to_state_slug(location_candidate) or ""
            key = (slug, state_candidate)
            if key in seen_keys:
                continue
            seen_keys.add(key)
            listing_query = ListingQuery(
                industry=industry_candidate,
                location=location_candidate,
                max_results=max_results,
            )
            strategies.append(
                Strategy(
                    industry=industry_candidate,
                    location=location_candidate,
                    slug=slug,
                    state_slug=state_candidate,
                    url=provider._build_url(listing_query, page=1),
                )
            )
            if len(strategies) >= limit:
                return strategies

    return strategies


def run() -> int:
    parser = argparse.ArgumentParser(description="BizBuySell query playground")
    parser.add_argument("query", help='Natural query, e.g. "fire protection businesses in Los Angeles"')
    parser.add_argument("--max-results", type=int, default=20)
    parser.add_argument("--strategy-limit", type=int, default=4)
    parser.add_argument("--top", type=int, default=10)
    parser.add_argument("--urls-only", action="store_true")
    parser.add_argument("--use-cache", dest="use_cache", action="store_true")
    parser.add_argument("--no-cache", dest="use_cache", action="store_false")
    parser.set_defaults(use_cache=True)
    args = parser.parse_args()

    industry, location = parse_query(args.query)
    print(f"Parsed query -> industry='{industry}', location='{location}'")

    strategies = build_strategies(
        industry=industry,
        location=location,
        max_results=args.max_results,
        limit=args.strategy_limit,
    )
    if not strategies:
        print("No query strategies produced.")
        return 1

    print("\nStrategy plan:")
    for i, strategy in enumerate(strategies, start=1):
        state_part = strategy.state_slug or "(none)"
        print(
            f"{i}. industry='{strategy.industry}' slug='{strategy.slug}' "
            f"state='{state_part}' url={strategy.url}"
        )

    if args.urls_only:
        return 0

    provider = BizBuySellProvider()
    all_hits = []
    seen_ids: set[str] = set()
    print("")
    for i, strategy in enumerate(strategies, start=1):
        query = ListingQuery(
            industry=strategy.industry,
            location=strategy.location,
            max_results=args.max_results,
        )
        started = time.perf_counter()
        try:
            listings = provider.search(query, use_cache=args.use_cache)
        except Exception as exc:  # noqa: BLE001
            elapsed = int((time.perf_counter() - started) * 1000)
            print(f"[{i}] ERROR after {elapsed}ms: {exc}")
            continue

        elapsed = int((time.perf_counter() - started) * 1000)
        fire_hits = [
            listing
            for listing in listings
            if _is_fire_relevant(listing.name, listing.description)
        ]
        print(
            f"[{i}] got {len(listings)} listings ({len(fire_hits)} fire-relevant) "
            f"in {elapsed}ms"
        )

        for listing in fire_hits:
            if listing.id in seen_ids:
                continue
            seen_ids.add(listing.id)
            all_hits.append(listing)

    print(f"\nMerged fire-relevant listings: {len(all_hits)}")
    for listing in all_hits[: args.top]:
        price = f"${listing.asking_price:,.0f}" if listing.asking_price else "N/A"
        print(f"- [{listing.source_id}] {listing.name} | {listing.location} | {price}")

    return 0


if __name__ == "__main__":
    raise SystemExit(run())
