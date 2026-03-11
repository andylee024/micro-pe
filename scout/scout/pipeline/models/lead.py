"""Canonical lead model for outbound workflows."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any

from scout.pipeline.models.business import Business

DEFAULT_OUTBOUND_STATUS = "new"
DEFAULT_NEXT_ACTION = "research"


@dataclass
class Lead:
    id: str
    source: str
    name: str
    location: str = ""
    phone: str = ""
    website: str = ""
    outbound_status: str = DEFAULT_OUTBOUND_STATUS
    next_action: str = DEFAULT_NEXT_ACTION
    last_contacted_at: str | None = None
    updated_at: str = ""

    @classmethod
    def from_business(cls, business: Business) -> "Lead":
        return cls(
            id=lead_id_for_business(business),
            source=business.source,
            name=business.name,
            location=business.location,
            phone=business.phone,
            website=business.website,
        )

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "Lead":
        return cls(
            id=str(payload.get("id", "")),
            source=str(payload.get("source", "")),
            name=str(payload.get("name", "")),
            location=str(payload.get("location", "")),
            phone=str(payload.get("phone", "")),
            website=str(payload.get("website", "")),
            outbound_status=str(payload.get("outbound_status", DEFAULT_OUTBOUND_STATUS)),
            next_action=str(payload.get("next_action", DEFAULT_NEXT_ACTION)),
            last_contacted_at=_to_optional_str(payload.get("last_contacted_at")),
            updated_at=str(payload.get("updated_at", "")),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "source": self.source,
            "name": self.name,
            "location": self.location,
            "phone": self.phone,
            "website": self.website,
            "outbound_status": self.outbound_status,
            "next_action": self.next_action,
            "last_contacted_at": self.last_contacted_at,
            "updated_at": self.updated_at,
        }


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


def _to_optional_str(value: Any) -> str | None:
    if value is None:
        return None
    return str(value)
