"""DataSource contract."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from scout.pipeline.models.business import Business
from scout.pipeline.models.listing import Listing
from scout.pipeline.models.query import Query


@dataclass
class NormalizedBatch:
    businesses: list[Business] = field(default_factory=list)
    listings: list[Listing] = field(default_factory=list)
    signals: dict[str, object] = field(default_factory=dict)


class DataSource(ABC):
    """Fetches source payloads and normalizes them into canonical models."""

    name: str

    @abstractmethod
    def fetch(self, query: Query) -> dict[str, object]:
        raise NotImplementedError

    @abstractmethod
    def normalize(self, raw: dict[str, object], query: Query) -> NormalizedBatch:
        raise NotImplementedError
