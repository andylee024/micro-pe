"""Enhanced base class for all data collection tools"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pathlib import Path
import json
import logging
from datetime import datetime

from data_sources.shared.config import ScraperConfig
from data_sources.shared.errors import CacheError


class Tool(ABC):
    """Enhanced base class for all data collection tools"""

    def __init__(self, cache_dir: Optional[Path] = None):
        """
        Initialize tool with caching and logging.

        Args:
            cache_dir: Optional cache directory (defaults to config)
        """
        self.cache_dir = cache_dir or Path(ScraperConfig.CACHE_DIR)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Setup logger for this specific tool
        self.logger = logging.getLogger(self.__class__.__name__)
        if not self.logger.handlers:
            self._setup_logging()

    def _setup_logging(self):
        """Setup logging for this tool"""
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            ScraperConfig.LOG_FORMAT,
            datefmt=ScraperConfig.LOG_DATE_FORMAT
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(getattr(logging, ScraperConfig.LOG_LEVEL))

    @abstractmethod
    def search(self, **kwargs) -> Dict[str, Any]:
        """
        Execute search and return standardized data.

        All search methods should return a dict with:
        - source: str (tool identifier)
        - search_date: str (ISO timestamp)
        - results: List[dict] (raw data)
        """
        pass

    # ==================== CACHING ====================

    def load_cache(self, cache_key: str) -> Optional[Dict]:
        """
        Load cached data if available and not expired.

        Args:
            cache_key: Unique cache identifier

        Returns:
            Cached data dict or None if not found/expired
        """
        cache_file = self.cache_dir / f"{cache_key}.json"

        if not cache_file.exists():
            self.logger.debug(f"Cache miss: {cache_key}")
            return None

        try:
            with open(cache_file, 'r') as f:
                cached = json.load(f)

            if self._is_cache_expired(cached):
                self.logger.debug(f"Cache expired: {cache_key}")
                return None

            self.logger.info(f"Cache hit: {cache_key} (age: {self._get_cache_age_days(cached)} days)")
            return cached

        except json.JSONDecodeError as e:
            self.logger.error(f"Cache corrupted: {cache_key} - {e}")
            return None
        except Exception as e:
            self.logger.error(f"Cache load error: {e}")
            return None

    def save_cache(self, cache_key: str, data: Dict, ttl_days: int):
        """
        Save data to cache with expiration.

        Args:
            cache_key: Unique cache identifier
            data: Data to cache
            ttl_days: Time-to-live in days
        """
        cache_file = self.cache_dir / f"{cache_key}.json"

        cached_data = {
            "cached_at": datetime.now().isoformat(),
            "ttl_days": ttl_days,
            "data": data
        }

        try:
            with open(cache_file, 'w') as f:
                json.dump(cached_data, f, indent=2, default=str)

            self.logger.info(f"Saved to cache: {cache_key} (TTL: {ttl_days} days)")

        except Exception as e:
            self.logger.error(f"Cache save error: {e}")
            # Don't raise - caching is optional

    def _is_cache_expired(self, cached: Dict) -> bool:
        """Check if cached data is expired"""
        try:
            cached_at = datetime.fromisoformat(cached["cached_at"])
            ttl_days = cached["ttl_days"]
            age_days = (datetime.now() - cached_at).days
            return age_days > ttl_days
        except (KeyError, ValueError):
            return True

    def _get_cache_age_days(self, cached: Dict) -> int:
        """Get age of cached data in days"""
        try:
            cached_at = datetime.fromisoformat(cached["cached_at"])
            return (datetime.now() - cached_at).days
        except (KeyError, ValueError):
            return 0

    # ==================== UTILITIES ====================

    def save(self, data: Dict, filename: str) -> Path:
        """
        Save raw data to JSON file.

        Args:
            data: Data to save
            filename: Output filename

        Returns:
            Path to saved file
        """
        output_path = Path(ScraperConfig.OUTPUT_DIR) / "raw_data" / filename
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)

        self.logger.info(f"Saved data: {output_path}")
        return output_path
