"""Base class for all data collection tools"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pathlib import Path
import json
from datetime import datetime


class Tool(ABC):
    """Base class for all data collection tools"""

    def __init__(self, cache_dir: Optional[Path] = None):
        self.cache_dir = cache_dir or Path("outputs/cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    @abstractmethod
    def search(self, **kwargs) -> Dict[str, Any]:
        """
        Execute search and return raw data.

        All search methods should return a dict with:
        - source: str (tool identifier)
        - search_date: datetime
        - results: List[dict] (raw data)
        """
        pass

    def save(self, data: Dict, filename: str) -> Path:
        """Save raw data to JSON file"""
        output_path = Path("outputs/raw_data") / filename
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)

        return output_path

    def load_cache(self, cache_key: str) -> Optional[Dict]:
        """Load cached data if available and not expired"""
        cache_file = self.cache_dir / f"{cache_key}.json"
        if not cache_file.exists():
            return None

        with open(cache_file, 'r') as f:
            cached = json.load(f)

        # Check if cache is expired
        if self._is_cache_expired(cached):
            return None

        return cached

    def save_cache(self, cache_key: str, data: Dict, ttl_days: int):
        """Save data to cache with expiration"""
        cache_file = self.cache_dir / f"{cache_key}.json"

        cached_data = {
            "cached_at": datetime.now().isoformat(),
            "ttl_days": ttl_days,
            "data": data
        }

        with open(cache_file, 'w') as f:
            json.dump(cached_data, f, indent=2, default=str)

    def _is_cache_expired(self, cached: Dict) -> bool:
        """Check if cached data is expired"""
        cached_at = datetime.fromisoformat(cached["cached_at"])
        ttl_days = cached["ttl_days"]
        age_days = (datetime.now() - cached_at).days
        return age_days > ttl_days
