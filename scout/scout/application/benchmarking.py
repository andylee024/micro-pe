"""Benchmark computation from listings/FDDs."""

from typing import List, Optional
from statistics import median
from scout.domain.models import Benchmark


def _to_number(value: Optional[str | int | float]) -> Optional[float]:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip().lower().replace(",", "")
    if not text:
        return None
    # Handle $ and suffixes
    text = text.replace("$", "")
    multiplier = 1.0
    if text.endswith("k"):
        multiplier = 1_000.0
        text = text[:-1]
    elif text.endswith("m"):
        multiplier = 1_000_000.0
        text = text[:-1]
    try:
        return float(text) * multiplier
    except ValueError:
        return None


def compute_benchmarks_from_listings(industry: str, listings: List[dict]) -> Benchmark | None:
    """Compute a benchmark from BizBuySell-style listings if fields exist."""
    revenues = []
    cash_flows = []
    multiples = []

    for listing in listings:
        revenue = _to_number(listing.get("revenue") or listing.get("annual_revenue"))
        cash_flow = _to_number(listing.get("cash_flow") or listing.get("ebitda"))
        multiple = _to_number(listing.get("multiple"))

        if revenue is not None:
            revenues.append(revenue)
        if cash_flow is not None:
            cash_flows.append(cash_flow)
        if multiple is not None:
            multiples.append(multiple)

    if not (revenues or cash_flows or multiples):
        return None

    return Benchmark(
        industry=industry,
        median_revenue=median(revenues) if revenues else None,
        median_cash_flow=median(cash_flows) if cash_flows else None,
        median_multiple=median(multiples) if multiples else None,
        margin_pct=(median(cash_flows) / median(revenues) * 100) if revenues and cash_flows else None,
        sample_size=max(len(revenues), len(cash_flows), len(multiples)),
        source="bizbuysell",
    )
