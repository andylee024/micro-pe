"""Canonical app-state models for search and workflow orchestration."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex}"


@dataclass(frozen=True)
class Search:
    query_text: str
    industry: str
    location: str
    status: str = "active"
    id: str = field(default_factory=lambda: new_id("search"))
    created_at: str = field(default_factory=utc_now_iso)
    updated_at: str = field(default_factory=utc_now_iso)


@dataclass(frozen=True)
class SearchRun:
    search_id: str
    pipeline_run_id: str
    status: str = "running"
    summary: str = ""
    started_at: str = field(default_factory=utc_now_iso)
    finished_at: str | None = None
    id: str = field(default_factory=lambda: new_id("search_run"))


@dataclass(frozen=True)
class Lead:
    search_id: str
    source: str
    source_record_id: str
    name: str
    search_run_id: str | None = None
    score: float | None = None
    status: str = "new"
    created_at: str = field(default_factory=utc_now_iso)
    updated_at: str = field(default_factory=utc_now_iso)
    id: str = field(default_factory=lambda: new_id("lead"))


@dataclass(frozen=True)
class WorkflowRun:
    search_run_id: str
    workflow_name: str
    status: str = "running"
    metadata_json: str = ""
    started_at: str = field(default_factory=utc_now_iso)
    finished_at: str | None = None
    id: str = field(default_factory=lambda: new_id("workflow_run"))


@dataclass(frozen=True)
class WorkflowArtifact:
    workflow_run_id: str
    artifact_type: str
    uri: str
    metadata_json: str = ""
    created_at: str = field(default_factory=utc_now_iso)
    id: str = field(default_factory=lambda: new_id("workflow_artifact"))


@dataclass(frozen=True)
class OutboundAttempt:
    lead_id: str
    channel: str
    target: str
    status: str = "pending"
    template_key: str = ""
    response_json: str = ""
    attempted_at: str = field(default_factory=utc_now_iso)
    id: str = field(default_factory=lambda: new_id("outbound_attempt"))


@dataclass(frozen=True)
class ExternalRecordLink:
    owner_type: str
    owner_id: str
    provider: str
    external_id: str
    url: str = ""
    created_at: str = field(default_factory=utc_now_iso)
    id: str = field(default_factory=lambda: new_id("external_record_link"))


@dataclass(frozen=True)
class Note:
    owner_type: str
    owner_id: str
    body: str
    author: str = "system"
    created_at: str = field(default_factory=utc_now_iso)
    id: str = field(default_factory=lambda: new_id("note"))

