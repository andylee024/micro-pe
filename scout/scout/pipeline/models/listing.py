"""Canonical listing model."""

from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Any


@dataclass
class Listing:
    source: str
    source_id: str
    url: str
    name: str
    industry: str
    location: str
    state: str = ""
    description: str = ""
    asking_price: float | None = None
    annual_revenue: float | None = None
    cash_flow: float | None = None
    asking_multiple: float | None = None
    days_on_market: int | None = None
    broker: str = ""
    listed_at: str | None = None
    fetched_at: str = ""

    @property
    def id(self) -> str:
        return f"{self.source}:{self.source_id}"

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "Listing":
        return cls(
            source=str(payload.get("source", "")),
            source_id=str(payload.get("source_id", "")),
            url=str(payload.get("url", "")),
            name=str(payload.get("name", "")),
            industry=str(payload.get("industry", "")),
            location=str(payload.get("location", "")),
            state=str(payload.get("state", "")),
            description=str(payload.get("description", "")),
            asking_price=_to_float(payload.get("asking_price")),
            annual_revenue=_to_float(payload.get("annual_revenue")),
            cash_flow=_to_float(payload.get("cash_flow")),
            asking_multiple=_to_float(payload.get("asking_multiple")),
            days_on_market=_to_int(payload.get("days_on_market")),
            broker=str(payload.get("broker", "")),
            listed_at=payload.get("listed_at"),
            fetched_at=str(payload.get("fetched_at", "")),
        )

    def to_dict(self) -> dict[str, Any]:
        return {field.name: getattr(self, field.name) for field in fields(self)}


def _to_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _to_int(value: Any) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None
