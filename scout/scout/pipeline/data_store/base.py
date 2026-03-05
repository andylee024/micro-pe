"""DataStore contract."""

from __future__ import annotations

from abc import ABC, abstractmethod

from scout.pipeline.models.business import Business
from scout.pipeline.models.listing import Listing


class DataStore(ABC):
    """Persists raw payloads and canonical models."""

    @abstractmethod
    def persist_raw(self, run_id: str, source: str, payload: dict[str, object]) -> str:
        raise NotImplementedError

    @abstractmethod
    def upsert_businesses(self, businesses: list[Business]) -> int:
        raise NotImplementedError

    @abstractmethod
    def upsert_listings(self, listings: list[Listing]) -> int:
        raise NotImplementedError
