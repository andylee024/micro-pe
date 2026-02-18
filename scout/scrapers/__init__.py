"""
Scrapers for deal flow intelligence

Available scrapers:
- google_maps: Find businesses via Google Maps Places API
- bizbuysell: Get financial benchmarks from business-for-sale listings
"""

from .google_maps import search_google_maps
from .bizbuysell import scrape_bizbuysell

__all__ = ['search_google_maps', 'scrape_bizbuysell']
