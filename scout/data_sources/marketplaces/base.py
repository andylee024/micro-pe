"""MarketplaceProvider abstract base class and shared utilities."""

import re
import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from scout.domain.listing import Listing

logger = logging.getLogger(__name__)


@dataclass
class ListingQuery:
    """Query parameters for marketplace searches."""
    industry: str
    location: str = ""
    max_results: int = 50


class MarketplaceProvider(ABC):
    """Abstract base for marketplace data providers.

    Provides file-based caching and a template search method.
    Subclasses implement _fetch() with source-specific scraping logic.
    """

    SOURCE_ID: str = ""
    CACHE_TTL_DAYS: int = 7

    def __init__(self, cache_dir: Optional[Path] = None):
        self.cache_dir = cache_dir or Path("outputs/cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def _fetch(self, query: ListingQuery) -> List[Listing]:
        """Fetch listings from the source. Implemented by subclasses."""
        ...

    def search(self, query: ListingQuery, use_cache: bool = True) -> List[Listing]:
        """Template method: cache check -> fetch -> compute multiples -> cache save -> return."""
        cache_key = self._cache_key(query)

        if use_cache:
            cached = self._load_cache(cache_key)
            if cached is not None:
                self.logger.info(f"Cache hit: {cache_key}")
                return cached

        listings = self._fetch(query)
        now = datetime.now().isoformat()

        for listing in listings:
            if listing.asking_multiple is None and listing.asking_price and listing.cash_flow:
                if listing.cash_flow > 0:
                    listing.asking_multiple = round(listing.asking_price / listing.cash_flow, 2)
            if not listing.fetched_at:
                listing.fetched_at = now

        self._save_cache(cache_key, listings)
        return listings

    def _cache_key(self, query: ListingQuery) -> str:
        parts = [self.SOURCE_ID, query.industry, query.location, str(query.max_results)]
        return "_".join(p.lower().replace(" ", "-") for p in parts)

    def _load_cache(self, cache_key: str) -> Optional[List[Listing]]:
        cache_file = self.cache_dir / f"{cache_key}.json"
        if not cache_file.exists():
            return None
        try:
            with open(cache_file, "r") as f:
                data = json.load(f)
            cached_at = datetime.fromisoformat(data["cached_at"])
            if (datetime.now() - cached_at).days > self.CACHE_TTL_DAYS:
                return None
            return [Listing.from_dict(d) for d in data["listings"]]
        except Exception as e:
            self.logger.warning(f"Cache load failed for {cache_key}: {e}")
            return None

    def _save_cache(self, cache_key: str, listings: List[Listing]) -> None:
        cache_file = self.cache_dir / f"{cache_key}.json"
        try:
            data = {
                "cached_at": datetime.now().isoformat(),
                "listings": [l.to_dict() for l in listings],
            }
            with open(cache_file, "w") as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            self.logger.warning(f"Cache save failed for {cache_key}: {e}")

    @staticmethod
    def parse_money(text) -> Optional[float]:
        """Parse monetary strings into floats.

        Handles: $1.2M, $450K, $1,200,000, $1.5B, 1200000, $0
        Returns None for: None, "", "Not Disclosed", "N/A", "Undisclosed", non-numeric strings
        """
        if text is None:
            return None
        if not isinstance(text, str):
            try:
                return float(text)
            except (TypeError, ValueError):
                return None

        text = text.strip()
        if not text:
            return None

        # Check for non-numeric strings
        lower = text.lower()
        non_numeric = {"not disclosed", "n/a", "undisclosed", "na", "none", "call", "tbd"}
        if lower in non_numeric:
            return None

        # Remove dollar sign and whitespace
        cleaned = text.replace("$", "").replace(",", "").strip()
        if not cleaned:
            return None

        # Handle suffixes: M, K, B
        multiplier = 1.0
        upper = cleaned.upper()
        if upper.endswith("M"):
            multiplier = 1_000_000.0
            cleaned = cleaned[:-1]
        elif upper.endswith("K"):
            multiplier = 1_000.0
            cleaned = cleaned[:-1]
        elif upper.endswith("B"):
            multiplier = 1_000_000_000.0
            cleaned = cleaned[:-1]

        try:
            return float(cleaned) * multiplier
        except ValueError:
            return None
