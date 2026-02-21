"""Helpers for loading mock data into the UI."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from scout.domain.models import Business, Benchmark, MarketSummary, ResearchResult


DEFAULT_MOCK_PATH = Path(__file__).resolve().parents[1] / "fixtures" / "mock_research.json"


def load_mock_result(path: str | Path | None = None) -> ResearchResult:
    """Load mock data from JSON into a ResearchResult."""
    data_path = Path(path) if path else DEFAULT_MOCK_PATH
    payload = json.loads(data_path.read_text())

    summary_payload: dict[str, Any] = payload.get("summary", {})
    industry = summary_payload.get("industry", "Mock Industry")
    location = summary_payload.get("location", "Mock Location")

    benchmarks = []
    for b in summary_payload.get("benchmarks", []) or []:
        benchmarks.append(
            Benchmark(
                industry=b.get("industry", industry),
                median_revenue=b.get("median_revenue"),
                median_cash_flow=b.get("median_cash_flow"),
                median_multiple=b.get("median_multiple"),
                margin_pct=b.get("margin_pct"),
                sample_size=b.get("sample_size", 0),
                source=b.get("source", "mock"),
            )
        )

    summary = MarketSummary(
        industry=industry,
        location=location,
        total_businesses=summary_payload.get("total_businesses", 0),
        query=summary_payload.get("query", f"{industry} businesses in {location}"),
        benchmarks=benchmarks,
    )

    base_keys = {
        "name",
        "address",
        "phone",
        "website",
        "category",
        "rating",
        "reviews",
        "place_id",
        "lat",
        "lng",
        "estimated_revenue",
        "estimated_cash_flow",
        "estimated_value",
        "confidence",
    }

    businesses = []
    for b in payload.get("businesses", []) or []:
        biz = Business(
            name=b.get("name", ""),
            address=b.get("address", ""),
            phone=b.get("phone", ""),
            website=b.get("website", ""),
            category=b.get("category", industry),
            rating=b.get("rating"),
            reviews=b.get("reviews"),
            place_id=b.get("place_id"),
            lat=b.get("lat"),
            lng=b.get("lng"),
            estimated_revenue=b.get("estimated_revenue"),
            estimated_cash_flow=b.get("estimated_cash_flow"),
            estimated_value=b.get("estimated_value"),
            confidence=b.get("confidence"),
        )
        # Allow extra mock-only fields for UI iteration (no schema changes required).
        for key, value in b.items():
            if key not in base_keys:
                setattr(biz, key, value)
        businesses.append(biz)

    pulse = payload.get("pulse", {})
    market_overview = payload.get("market_overview", {})

    return ResearchResult(
        summary=summary,
        businesses=businesses,
        pulse=pulse,
        market_overview=market_overview,
    )
