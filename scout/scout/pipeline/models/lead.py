"""Canonical lead model for operator scanning flows."""

from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Any


@dataclass
class Lead:
    """Unified business lead row with persisted operator state."""

    lead_id: str
    source: str
    name: str
    address: str = ""
    phone: str = ""
    website: str = ""
    category: str = ""
    location: str = ""
    state: str = ""
    rating: float | None = None
    reviews: int | None = None
    is_saved: bool = False
    saved_at: str | None = None
    updated_at: str = ""

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "Lead":
        return cls(
            lead_id=str(payload.get("lead_id", "")),
            source=str(payload.get("source", "")),
            name=str(payload.get("name", "")),
            address=str(payload.get("address", "")),
            phone=str(payload.get("phone", "")),
            website=str(payload.get("website", "")),
            category=str(payload.get("category", "")),
            location=str(payload.get("location", "")),
            state=str(payload.get("state", "")),
            rating=_to_float(payload.get("rating")),
            reviews=_to_int(payload.get("reviews")),
            is_saved=bool(payload.get("is_saved", False)),
            saved_at=_to_optional_str(payload.get("saved_at")),
            updated_at=str(payload.get("updated_at", "")),
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


def _to_optional_str(value: Any) -> str | None:
    if value is None:
        return None
    return str(value)
