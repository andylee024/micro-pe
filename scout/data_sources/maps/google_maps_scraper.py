"""Google Maps Places API scraper"""

import time
from typing import Dict, List

import googlemaps


def search_google_maps(
    industry: str,
    city: str,
    api_key: str,
    max_results: int = 100,
) -> List[Dict]:
    """Search Google Maps for businesses by industry and city.

    Uses the Places Text Search API with pagination, then fetches
    phone and website via Places Details.

    Args:
        industry: Business type (e.g. "HVAC", "car wash")
        city: City/location string (e.g. "Houston, TX")
        api_key: Google Maps API key
        max_results: Maximum number of businesses to return

    Returns:
        List of business dicts with name, address, phone, website,
        rating, reviews, place_id, lat, lng, category fields.
    """
    gmaps = googlemaps.Client(key=api_key)
    businesses = []
    query = f"{industry} in {city}"

    response = gmaps.places(query=query)

    while response and len(businesses) < max_results:
        for place in response.get("results", []):
            if len(businesses) >= max_results:
                break

            place_id = place.get("place_id", "")
            geometry = place.get("geometry", {}).get("location", {})

            # Fetch details for phone + website (not in text search results)
            try:
                details = gmaps.place(
                    place_id=place_id,
                    fields=[
                        "name",
                        "formatted_address",
                        "formatted_phone_number",
                        "website",
                        "rating",
                        "user_ratings_total",
                    ],
                ).get("result", {})
            except Exception:
                details = {}

            businesses.append(
                {
                    "name": details.get("name") or place.get("name", ""),
                    "address": details.get("formatted_address")
                    or place.get("formatted_address", ""),
                    "phone": details.get("formatted_phone_number", ""),
                    "website": details.get("website", ""),
                    "rating": details.get("rating") or place.get("rating"),
                    "reviews": details.get("user_ratings_total")
                    or place.get("user_ratings_total", 0),
                    "place_id": place_id,
                    "lat": geometry.get("lat"),
                    "lng": geometry.get("lng"),
                    "category": industry,
                }
            )

        next_page_token = response.get("next_page_token")
        if not next_page_token or len(businesses) >= max_results:
            break

        # Google requires a short delay before next_page_token becomes valid
        time.sleep(2)
        response = gmaps.places(query=query, page_token=next_page_token)

    return businesses
