"""Google Maps adapter that returns domain Business models."""

from typing import List
from data_sources.maps.google_maps import GoogleMapsTool
from scout.domain.models import Business


class GoogleMapsAdapter:
    def __init__(self):
        self.tool = GoogleMapsTool()

    def search(self, industry: str, location: str, max_results: int, use_cache: bool = True) -> List[Business]:
        result = self.tool.search(
            industry=industry,
            location=location,
            max_results=max_results,
            use_cache=use_cache,
        )
        businesses = []
        for b in result.get("results", []):
            businesses.append(
                Business(
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
                )
            )
        return businesses
