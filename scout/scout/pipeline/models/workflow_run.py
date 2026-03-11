"""Workflow run queue models."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


WORKFLOW_STATUS_QUEUED = "queued"
WORKFLOW_STATUS_RUNNING = "running"
WORKFLOW_STATUS_COMPLETED = "completed"
WORKFLOW_STATUS_FAILED = "failed"

WORKFLOW_STATUSES = {
    WORKFLOW_STATUS_QUEUED,
    WORKFLOW_STATUS_RUNNING,
    WORKFLOW_STATUS_COMPLETED,
    WORKFLOW_STATUS_FAILED,
}


@dataclass(frozen=True)
class WorkflowError:
    """Structured failure state for one workflow attempt."""

    error_type: str
    message: str
    details: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class WorkflowRun:
    """Durable queue record for one workflow execution."""

    run_id: str
    industry: str
    location: str
    max_results: int
    use_cache: bool
    status: str = WORKFLOW_STATUS_QUEUED
    attempt_count: int = 0
    max_attempts: int = 3
    available_at: str = field(default_factory=_utc_now_iso)
    created_at: str = field(default_factory=_utc_now_iso)
    updated_at: str = field(default_factory=_utc_now_iso)
    worker_id: str | None = None
    claimed_at: str | None = None
    started_at: str | None = None
    finished_at: str | None = None
    error: WorkflowError | None = None
