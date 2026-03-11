"""Canonical lead model for operator-facing workflow actions."""

from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Any


@dataclass
class Lead:
    """Unified, workflow-friendly view over business and listing records."""

    lead_id: str
    lead_type: str
    source: str
    source_record_id: str
    name: str
    industry: str
    location: str
    state: str = ""
    address: str = ""
    phone: str = ""
    website: str = ""
    url: str = ""
    rating: float | None = None
    reviews: int | None = None
    asking_price: float | None = None
    annual_revenue: float | None = None
    cash_flow: float | None = None

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "Lead":
        return cls(
            lead_id=str(payload.get("lead_id", "")),
            lead_type=str(payload.get("lead_type", "")),
            source=str(payload.get("source", "")),
            source_record_id=str(payload.get("source_record_id", "")),
            name=str(payload.get("name", "")),
            industry=str(payload.get("industry", "")),
            location=str(payload.get("location", "")),
            state=str(payload.get("state", "")),
            address=str(payload.get("address", "")),
            phone=str(payload.get("phone", "")),
            website=str(payload.get("website", "")),
            url=str(payload.get("url", "")),
            rating=_to_float(payload.get("rating")),
            reviews=_to_int(payload.get("reviews")),
            asking_price=_to_float(payload.get("asking_price")),
            annual_revenue=_to_float(payload.get("annual_revenue")),
            cash_flow=_to_float(payload.get("cash_flow")),
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
