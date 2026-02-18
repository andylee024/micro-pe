"""
Utility functions for deal flow intelligence
"""

from .financials import (
    calculate_multiple,
    calculate_margin,
    estimate_value,
    apply_benchmarks
)

__all__ = [
    'calculate_multiple',
    'calculate_margin',
    'estimate_value',
    'apply_benchmarks'
]
