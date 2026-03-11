"""Canonical lead model shared across outbound and operator-facing workflows."""

from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass
from typing import Any

from scout.pipeline.models.business import Business

DEFAULT_OUTBOUND_STATUS = "new"
DEFAULT_NEXT_ACTION = "research"


@dataclass
class Lead:
    lead_id: str
    lead_type: str = "business"
    source: str = ""
    source_record_id: str = ""
    name: str = ""
    industry: str = ""
    location: str = ""
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
    note: str = ""
    note_updated_at: str | None = None
    outbound_status: str = DEFAULT_OUTBOUND_STATUS
    next_action: str = DEFAULT_NEXT_ACTION
    last_contacted_at: str | None = None
    updated_at: str = ""

    @property
    def id(self) -> str:
        return self.lead_id

    @id.setter
    def id(self, value: str) -> None:
        self.lead_id = value

    @classmethod
    def from_business(cls, business: Business) -> "Lead":
        return cls(
            lead_id=lead_id_for_business(business),
            lead_type="business",
            source=business.source,
            name=business.name,
            industry=business.category,
            location=business.location,
            state=business.state,
            address=business.address,
            phone=business.phone,
            website=business.website,
            rating=business.rating,
            reviews=business.reviews,
        )

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "Lead":
        lead_id = str(payload.get("lead_id") or payload.get("id") or "")
        lead_type = str(payload.get("lead_type") or ("business" if lead_id else ""))
        return cls(
            lead_id=lead_id,
            lead_type=lead_type,
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
            note=str(payload.get("note", "")),
            note_updated_at=_to_optional_str(payload.get("note_updated_at")),
            outbound_status=str(payload.get("outbound_status", DEFAULT_OUTBOUND_STATUS)),
            next_action=str(payload.get("next_action", DEFAULT_NEXT_ACTION)),
            last_contacted_at=_to_optional_str(payload.get("last_contacted_at")),
            updated_at=str(payload.get("updated_at", "")),
        )

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["id"] = self.lead_id
        return payload


def lead_id_for_business(business: Business) -> str:
    """Build a deterministic lead id from stable business identity fields."""
    payload = "|".join(
        [
            business.source.strip().lower(),
            business.name.strip().lower(),
            business.address.strip().lower(),
            business.location.strip().lower(),
        ]
    )
    digest = hashlib.sha1(payload.encode("utf-8")).hexdigest()[:16]
    source = business.source.strip().lower() or "unknown"
    return f"{source}:{digest}"


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
