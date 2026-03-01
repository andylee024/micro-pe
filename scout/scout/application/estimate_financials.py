"""Per-business financial estimation using benchmark signals."""

from typing import Optional
from scout.domain.models import Business, Benchmark


def estimate_business_financials(
    business: Business,
    benchmark: Optional[Benchmark],
) -> Business:
    """
    Estimate revenue, cash flow, and acquisition value for a business.

    Uses benchmark median as base, adjusted by review count and rating signals.
    Sets confidence based on data quality.
    """
    if benchmark is None or benchmark.median_revenue is None:
        return business

    base_revenue = benchmark.median_revenue

    # Review count multiplier
    reviews = business.reviews or 0
    if reviews > 200:
        review_mult = 1.3
    elif reviews >= 100:
        review_mult = 1.0
    elif reviews >= 30:
        review_mult = 0.8
    else:
        review_mult = 0.6

    # Rating multiplier
    rating = business.rating or 0
    if rating >= 4.5:
        rating_mult = 1.1
    elif rating >= 4.0:
        rating_mult = 1.0
    elif rating >= 3.5:
        rating_mult = 0.9
    else:
        rating_mult = 0.8

    est_revenue = base_revenue * review_mult * rating_mult

    # Cash flow from margin
    margin = benchmark.margin_pct / 100.0 if benchmark.margin_pct else 0.18
    est_cash_flow = est_revenue * margin

    # Acquisition value: SDE multiple (default 3.0x)
    multiple = benchmark.median_multiple or 3.0
    est_value = est_cash_flow * multiple

    # Confidence based on data quality
    if reviews > 200 and rating >= 4.0 and benchmark.sample_size >= 5:
        confidence = "high"
    elif reviews >= 50 or benchmark.sample_size >= 3:
        confidence = "medium"
    else:
        confidence = "low"

    # Only update if not already set (don't overwrite real data)
    if business.estimated_revenue is None:
        business.estimated_revenue = round(est_revenue)
    if business.estimated_cash_flow is None:
        business.estimated_cash_flow = round(est_cash_flow)
    if business.estimated_value is None:
        business.estimated_value = round(est_value)
    if business.confidence is None:
        business.confidence = confidence

    return business
