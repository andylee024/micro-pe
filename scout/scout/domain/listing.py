"""Listing domain model for businesses-for-sale."""

from dataclasses import dataclass, fields
from typing import Optional, Dict, Any


def _to_float(v: Any) -> Optional[float]:
    """Safely convert a value to float, returning None on failure."""
    if v is None:
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _to_int(v: Any) -> Optional[int]:
    """Safely convert a value to int, returning None on failure."""
    if v is None:
        return None
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


@dataclass
class Listing:
    """A business-for-sale listing from a marketplace source."""

    source: str
    source_id: str
    url: str
    name: str
    industry: str
    location: str
    state: str = ""
    description: str = ""
    asking_price: Optional[float] = None
    annual_revenue: Optional[float] = None
    cash_flow: Optional[float] = None
    asking_multiple: Optional[float] = None
    days_on_market: Optional[int] = None
    broker: str = ""
    listed_at: Optional[str] = None
    fetched_at: str = ""

    @property
    def id(self) -> str:
        return f"{self.source}:{self.source_id}"

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Listing":
        """Create a Listing from a dict with safe type coercion."""
        return cls(
            source=str(d.get("source", "")),
            source_id=str(d.get("source_id", "")),
            url=str(d.get("url", "")),
            name=str(d.get("name", "")),
            industry=str(d.get("industry", "")),
            location=str(d.get("location", "")),
            state=str(d.get("state", "")),
            description=str(d.get("description", "")),
            asking_price=_to_float(d.get("asking_price")),
            annual_revenue=_to_float(d.get("annual_revenue")),
            cash_flow=_to_float(d.get("cash_flow")),
            asking_multiple=_to_float(d.get("asking_multiple")),
            days_on_market=_to_int(d.get("days_on_market")),
            broker=str(d.get("broker", "")),
            listed_at=d.get("listed_at"),
            fetched_at=str(d.get("fetched_at", "")),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serialize all fields to a dict."""
        return {f.name: getattr(self, f.name) for f in fields(self)}
