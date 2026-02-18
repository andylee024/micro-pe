"""
Financial calculation utilities
"""

from typing import Dict, List, Optional


def calculate_multiple(price: float, cash_flow: float) -> Optional[float]:
    """
    Calculate EBITDA multiple

    Args:
        price: Asking or sale price
        cash_flow: Annual cash flow / EBITDA

    Returns:
        Multiple (price / cash_flow) or None if invalid
    """
    if not cash_flow or cash_flow <= 0:
        return None

    return round(price / cash_flow, 2)


def calculate_margin(cash_flow: float, revenue: float) -> Optional[float]:
    """
    Calculate profit margin

    Args:
        cash_flow: Annual cash flow / EBITDA
        revenue: Annual gross revenue

    Returns:
        Margin (cash_flow / revenue) or None if invalid
    """
    if not revenue or revenue <= 0:
        return None

    return round(cash_flow / revenue, 3)


def estimate_value(
    revenue: Optional[float] = None,
    cash_flow: Optional[float] = None,
    benchmark_multiple: Optional[float] = None,
    benchmark_margin: Optional[float] = None
) -> Dict:
    """
    Estimate business value using benchmarks

    Args:
        revenue: Estimated annual revenue
        cash_flow: Known or estimated cash flow
        benchmark_multiple: Industry median EBITDA multiple
        benchmark_margin: Industry median margin

    Returns:
        Dictionary with estimated values and confidence
    """
    result = {
        'estimated_revenue': revenue,
        'estimated_cash_flow': cash_flow,
        'estimated_value': None,
        'method': None,
        'confidence': None
    }

    # If we have cash flow and multiple, use that (most accurate)
    if cash_flow and benchmark_multiple:
        result['estimated_value'] = round(cash_flow * benchmark_multiple)
        result['method'] = 'cash_flow_x_multiple'
        result['confidence'] = 'high'
        return result

    # If we have revenue, estimate cash flow using margin, then apply multiple
    if revenue and benchmark_margin and benchmark_multiple:
        estimated_cf = revenue * benchmark_margin
        result['estimated_cash_flow'] = round(estimated_cf)
        result['estimated_value'] = round(estimated_cf * benchmark_multiple)
        result['method'] = 'revenue_x_margin_x_multiple'
        result['confidence'] = 'medium'
        return result

    # Not enough data
    result['confidence'] = 'insufficient_data'
    return result


def apply_benchmarks(businesses: List[Dict], benchmarks: Dict) -> List[Dict]:
    """
    Apply financial benchmarks to a list of businesses

    Args:
        businesses: List of business dictionaries (e.g., from Google Maps)
        benchmarks: Benchmark dictionary from BizBuySell

    Returns:
        List of businesses with estimated financials added
    """
    if not benchmarks or 'error' in benchmarks:
        # Can't apply benchmarks
        return businesses

    benchmark_multiple = benchmarks.get('multiple', {}).get('median')
    benchmark_margin = benchmarks.get('margin', {}).get('median')
    median_revenue = benchmarks.get('revenue', {}).get('median')

    enriched = []

    for business in businesses:
        # Estimate revenue based on review count (very rough proxy)
        # More reviews ≈ larger/more established business
        review_count = business.get('review_count', 0)

        if review_count and median_revenue:
            # Simple linear scaling: median reviews ≈ median revenue
            # This is a VERY rough estimate
            avg_reviews = 100  # Assume 100 reviews = median business
            scale_factor = review_count / avg_reviews
            estimated_revenue = median_revenue * scale_factor
        else:
            estimated_revenue = None

        # Apply benchmarks
        valuation = estimate_value(
            revenue=estimated_revenue,
            cash_flow=None,
            benchmark_multiple=benchmark_multiple,
            benchmark_margin=benchmark_margin
        )

        # Add to business data
        enriched_business = {
            **business,
            **valuation,
            'benchmarks_applied': True
        }

        enriched.append(enriched_business)

    return enriched


def rank_businesses(businesses: List[Dict], sort_by: str = 'estimated_value') -> List[Dict]:
    """
    Rank businesses by a given metric

    Args:
        businesses: List of business dictionaries
        sort_by: Field to sort by (default: 'estimated_value')

    Returns:
        Sorted list of businesses
    """
    # Filter to businesses with the sort field
    valid = [b for b in businesses if b.get(sort_by) is not None]

    # Sort descending
    sorted_businesses = sorted(valid, key=lambda x: x[sort_by], reverse=True)

    # Re-rank
    for i, business in enumerate(sorted_businesses, 1):
        business['rank'] = i

    return sorted_businesses
