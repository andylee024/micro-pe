"""
Google Maps Places API scraper for building business universe
"""

import googlemaps
from typing import List, Dict, Optional


def search_google_maps(industry: str, city: str, api_key: str, max_results: int = 60) -> List[Dict]:
    """
    Search Google Maps for businesses and return structured data

    Args:
        industry: Business type (e.g., "HVAC contractor", "backflow testing")
        city: Location (e.g., "Arcadia, CA", "Houston, TX")
        api_key: Google Maps API key
        max_results: Maximum number of results to return (default 60)

    Returns:
        List of business dictionaries with keys:
        - rank, place_id, name, address, city, state, zip
        - phone, website, rating, review_count, lat, lng

    Raises:
        ValueError: If API key is invalid
        Exception: For other API errors
    """

    # Initialize client
    client = googlemaps.Client(key=api_key)

    # Text search
    query = f'{industry} in {city}'
    search_results = client.places(query=query)

    places = search_results.get('results', [])

    if not places:
        return []

    businesses = []

    # Get details for each place (limit to max_results)
    for i, place in enumerate(places[:max_results], 1):
        place_id = place['place_id']

        try:
            # Get detailed info
            details = client.place(
                place_id=place_id,
                fields=[
                    'name',
                    'formatted_address',
                    'formatted_phone_number',
                    'website',
                    'rating',
                    'user_ratings_total',
                    'geometry'
                ]
            )

            result = details['result']

            # Parse address into components
            address = result.get('formatted_address', '')
            address_parts = address.split(',')

            business = {
                'rank': i,
                'place_id': place_id,
                'name': result.get('name', ''),
                'address': address,
                'city': address_parts[-3].strip() if len(address_parts) >= 3 else '',
                'state': address_parts[-2].strip().split()[0] if len(address_parts) >= 2 else '',
                'zip': address_parts[-2].strip().split()[1] if len(address_parts) >= 2 and len(address_parts[-2].strip().split()) > 1 else '',
                'phone': result.get('formatted_phone_number'),
                'website': result.get('website'),
                'rating': result.get('rating'),
                'review_count': result.get('user_ratings_total'),
                'lat': result.get('geometry', {}).get('location', {}).get('lat'),
                'lng': result.get('geometry', {}).get('location', {}).get('lng'),
            }

            businesses.append(business)

        except Exception as e:
            # Skip businesses that fail to fetch
            print(f"Warning: Error fetching details for {place.get('name')}: {e}")
            continue

    return businesses


def estimate_api_cost(num_businesses: int) -> float:
    """
    Estimate Google Maps API cost for a search

    Args:
        num_businesses: Number of businesses fetched

    Returns:
        Estimated cost in USD
    """
    # Text search: $0.032 per search
    # Place details: $0.017 per business
    text_search_cost = 0.032
    details_cost = num_businesses * 0.017

    return text_search_cost + details_cost


def get_summary_stats(businesses: List[Dict]) -> Dict:
    """
    Calculate summary statistics for a list of businesses

    Args:
        businesses: List of business dictionaries

    Returns:
        Dictionary with summary statistics
    """
    if not businesses:
        return {
            'total': 0,
            'with_phone': 0,
            'with_website': 0,
            'avg_rating': 0
        }

    return {
        'total': len(businesses),
        'with_phone': sum(1 for b in businesses if b.get('phone')),
        'with_website': sum(1 for b in businesses if b.get('website')),
        'avg_rating': sum(b.get('rating') or 0 for b in businesses) / len(businesses) if businesses else 0
    }
