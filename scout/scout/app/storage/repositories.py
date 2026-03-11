"""Repository interfaces for canonical app storage."""

from __future__ import annotations

from abc import ABC, abstractmethod

from scout.app.storage.models import (
    ExternalRecordLink,
    Lead,
    Note,
    OutboundAttempt,
    Search,
    SearchRun,
    WorkflowArtifact,
    WorkflowRun,
)


class SearchRepository(ABC):
    @abstractmethod
    def create(self, search: Search) -> Search:
        raise NotImplementedError

    @abstractmethod
    def get(self, search_id: str) -> Search | None:
        raise NotImplementedError


class SearchRunRepository(ABC):
    @abstractmethod
    def create(self, search_run: SearchRun) -> SearchRun:
        raise NotImplementedError

    @abstractmethod
    def get(self, search_run_id: str) -> SearchRun | None:
        raise NotImplementedError

    @abstractmethod
    def list_for_search(self, search_id: str) -> list[SearchRun]:
        raise NotImplementedError


class LeadRepository(ABC):
    @abstractmethod
    def create(self, lead: Lead) -> Lead:
        raise NotImplementedError

    @abstractmethod
    def get(self, lead_id: str) -> Lead | None:
        raise NotImplementedError

    @abstractmethod
    def list_for_search(self, search_id: str) -> list[Lead]:
        raise NotImplementedError


class WorkflowRunRepository(ABC):
    @abstractmethod
    def create(self, workflow_run: WorkflowRun) -> WorkflowRun:
        raise NotImplementedError

    @abstractmethod
    def get(self, workflow_run_id: str) -> WorkflowRun | None:
        raise NotImplementedError


class WorkflowArtifactRepository(ABC):
    @abstractmethod
    def create(self, workflow_artifact: WorkflowArtifact) -> WorkflowArtifact:
        raise NotImplementedError

    @abstractmethod
    def list_for_workflow_run(self, workflow_run_id: str) -> list[WorkflowArtifact]:
        raise NotImplementedError


class OutboundAttemptRepository(ABC):
    @abstractmethod
    def create(self, outbound_attempt: OutboundAttempt) -> OutboundAttempt:
        raise NotImplementedError

    @abstractmethod
    def list_for_lead(self, lead_id: str) -> list[OutboundAttempt]:
        raise NotImplementedError


class ExternalRecordLinkRepository(ABC):
    @abstractmethod
    def create(self, external_record_link: ExternalRecordLink) -> ExternalRecordLink:
        raise NotImplementedError

    @abstractmethod
    def list_for_owner(self, owner_type: str, owner_id: str) -> list[ExternalRecordLink]:
        raise NotImplementedError


class NoteRepository(ABC):
    @abstractmethod
    def create(self, note: Note) -> Note:
        raise NotImplementedError

    @abstractmethod
    def list_for_owner(self, owner_type: str, owner_id: str) -> list[Note]:
        raise NotImplementedError

