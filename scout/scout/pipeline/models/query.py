"""Run query model."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class Query:
    """One pipeline request."""

    industry: str
    location: str
    max_results: int = 100
    use_cache: bool = True
    run_id: str = field(default_factory=lambda: uuid4().hex[:12])
    created_at: str = field(default_factory=_utc_now_iso)

    def __post_init__(self) -> None:
        if not self.industry.strip():
            raise ValueError("query.industry must be non-empty")
        if not self.location.strip():
            raise ValueError("query.location must be non-empty")
        if self.max_results < 1:
            raise ValueError("query.max_results must be >= 1")
