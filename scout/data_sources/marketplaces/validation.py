"""Validation layer for marketplace listing results.

Checks that scraped listings actually match the queried industry,
and performs basic financial sanity checks.
"""

from dataclasses import dataclass, field
from typing import List, Optional

from scout.domain.listing import Listing

# Keywords used to determine if a listing is relevant to a given industry.
# Sub-category URLs already give precise results, so this is a secondary check.
INDUSTRY_KEYWORDS = {
    "hvac": [
        "hvac", "air conditioning", "heating", "cooling", "refrigeration",
        "furnace", "heat pump", "ac ", "a/c",
    ],
    "plumbing": [
        "plumbing", "plumber", "pipe", "drain", "sewer", "water heater",
    ],
    "electrical": [
        "electrical", "electrician", "wiring", "electric",
    ],
    "car wash": [
        "car wash", "carwash", "auto wash", "detailing", "car-wash",
    ],
    "landscaping": [
        "landscaping", "lawn", "tree service", "irrigation", "yard",
        "mowing", "landscape",
    ],
    "cleaning": [
        "cleaning", "janitorial", "maid", "housekeeping", "janitor",
    ],
    "pest control": [
        "pest", "exterminator", "termite", "pest control",
    ],
    "auto repair": [
        "auto repair", "mechanic", "automotive", "body shop", "auto service",
        "car repair", "oil change", "transmission",
    ],
    "restaurant": [
        "restaurant", "cafe", "diner", "food", "bar", "grill", "pizza",
        "bakery", "catering", "kitchen",
    ],
    "pool service": [
        "pool", "swimming pool", "spa", "hot tub",
    ],
}


@dataclass
class ValidationReport:
    """Summary of how well scraped listings matched the queried industry."""

    query_industry: str
    total: int
    relevant: int
    precision_pct: float
    irrelevant_names: List[str] = field(default_factory=list)


def is_relevant(listing: Listing, query_industry: str) -> bool:
    """Check if a listing appears relevant to the queried industry.

    Uses keyword matching against name + description.
    Returns True if no keywords are defined for the industry (permissive fallback).
    """
    key = query_industry.strip().lower()
    keywords = INDUSTRY_KEYWORDS.get(key)

    if not keywords:
        return True  # No keywords defined -> assume relevant

    text = f"{listing.name} {listing.description}".lower()
    return any(kw in text for kw in keywords)


def validate_batch(
    listings: List[Listing], query_industry: str
) -> ValidationReport:
    """Validate a batch of listings against the queried industry.

    Returns a ValidationReport with precision metrics.
    """
    if not listings:
        return ValidationReport(
            query_industry=query_industry,
            total=0,
            relevant=0,
            precision_pct=0.0,
        )

    relevant_count = 0
    irrelevant_names: List[str] = []

    for listing in listings:
        if is_relevant(listing, query_industry):
            relevant_count += 1
        else:
            irrelevant_names.append(listing.name)

    precision = (relevant_count / len(listings)) * 100.0 if listings else 0.0

    return ValidationReport(
        query_industry=query_industry,
        total=len(listings),
        relevant=relevant_count,
        precision_pct=round(precision, 1),
        irrelevant_names=irrelevant_names,
    )


def check_financial_sanity(listing: Listing) -> List[str]:
    """Run basic sanity checks on a listing's financial data.

    Returns a list of warning strings (empty = no issues).
    """
    warnings: List[str] = []

    if listing.asking_price is not None:
        if listing.asking_price < 0:
            warnings.append(f"Negative asking price: {listing.asking_price}")
        if listing.asking_price > 100_000_000:
            warnings.append(
                f"Unusually high asking price: ${listing.asking_price:,.0f}"
            )

    if listing.cash_flow is not None:
        if listing.cash_flow < -1_000_000:
            warnings.append(
                f"Very negative cash flow: ${listing.cash_flow:,.0f}"
            )

    if listing.asking_price and listing.cash_flow and listing.cash_flow > 0:
        multiple = listing.asking_price / listing.cash_flow
        if multiple > 20:
            warnings.append(
                f"Very high asking multiple: {multiple:.1f}x "
                f"(price={listing.asking_price:,.0f}, cf={listing.cash_flow:,.0f})"
            )

    return warnings
