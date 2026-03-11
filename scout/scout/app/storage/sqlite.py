"""SQLite app storage bootstrap and repository implementations."""

from __future__ import annotations

import sqlite3
from dataclasses import asdict
from pathlib import Path
from typing import Callable, TypeVar

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
from scout.app.storage.repositories import (
    ExternalRecordLinkRepository,
    LeadRepository,
    NoteRepository,
    OutboundAttemptRepository,
    SearchRepository,
    SearchRunRepository,
    WorkflowArtifactRepository,
    WorkflowRunRepository,
)

T = TypeVar("T")


def bootstrap_app_schema(conn: sqlite3.Connection) -> None:
    """Create canonical app-level tables and indexes."""
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS searches (
            id TEXT PRIMARY KEY,
            query_text TEXT NOT NULL,
            industry TEXT NOT NULL,
            location TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS search_runs (
            id TEXT PRIMARY KEY,
            search_id TEXT NOT NULL,
            pipeline_run_id TEXT NOT NULL,
            status TEXT NOT NULL,
            summary TEXT NOT NULL,
            started_at TEXT NOT NULL,
            finished_at TEXT,
            FOREIGN KEY(search_id) REFERENCES searches(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS leads (
            id TEXT PRIMARY KEY,
            search_id TEXT NOT NULL,
            search_run_id TEXT,
            source TEXT NOT NULL,
            source_record_id TEXT NOT NULL,
            name TEXT NOT NULL,
            score REAL,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY(search_id) REFERENCES searches(id) ON DELETE CASCADE,
            FOREIGN KEY(search_run_id) REFERENCES search_runs(id) ON DELETE SET NULL,
            UNIQUE(search_id, source, source_record_id)
        );

        CREATE TABLE IF NOT EXISTS workflow_runs (
            id TEXT PRIMARY KEY,
            search_run_id TEXT NOT NULL,
            workflow_name TEXT NOT NULL,
            status TEXT NOT NULL,
            metadata_json TEXT NOT NULL,
            started_at TEXT NOT NULL,
            finished_at TEXT,
            FOREIGN KEY(search_run_id) REFERENCES search_runs(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS workflow_artifacts (
            id TEXT PRIMARY KEY,
            workflow_run_id TEXT NOT NULL,
            artifact_type TEXT NOT NULL,
            uri TEXT NOT NULL,
            metadata_json TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(workflow_run_id) REFERENCES workflow_runs(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS outbound_attempts (
            id TEXT PRIMARY KEY,
            lead_id TEXT NOT NULL,
            channel TEXT NOT NULL,
            target TEXT NOT NULL,
            status TEXT NOT NULL,
            template_key TEXT NOT NULL,
            response_json TEXT NOT NULL,
            attempted_at TEXT NOT NULL,
            FOREIGN KEY(lead_id) REFERENCES leads(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS external_record_links (
            id TEXT PRIMARY KEY,
            owner_type TEXT NOT NULL,
            owner_id TEXT NOT NULL,
            provider TEXT NOT NULL,
            external_id TEXT NOT NULL,
            url TEXT NOT NULL,
            created_at TEXT NOT NULL,
            UNIQUE(owner_type, owner_id, provider, external_id)
        );

        CREATE TABLE IF NOT EXISTS notes (
            id TEXT PRIMARY KEY,
            owner_type TEXT NOT NULL,
            owner_id TEXT NOT NULL,
            body TEXT NOT NULL,
            author TEXT NOT NULL,
            created_at TEXT NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_search_runs_search_id ON search_runs(search_id);
        CREATE INDEX IF NOT EXISTS idx_search_runs_pipeline_run_id ON search_runs(pipeline_run_id);
        CREATE INDEX IF NOT EXISTS idx_leads_search_id ON leads(search_id);
        CREATE INDEX IF NOT EXISTS idx_leads_search_run_id ON leads(search_run_id);
        CREATE INDEX IF NOT EXISTS idx_workflow_runs_search_run_id ON workflow_runs(search_run_id);
        CREATE INDEX IF NOT EXISTS idx_workflow_artifacts_run_id ON workflow_artifacts(workflow_run_id);
        CREATE INDEX IF NOT EXISTS idx_outbound_attempts_lead_id ON outbound_attempts(lead_id);
        CREATE INDEX IF NOT EXISTS idx_external_record_links_owner
            ON external_record_links(owner_type, owner_id);
        CREATE INDEX IF NOT EXISTS idx_notes_owner ON notes(owner_type, owner_id);
        """
    )
    conn.commit()


def _row_to_model(row: sqlite3.Row | None, constructor: Callable[..., T]) -> T | None:
    if row is None:
        return None
    return constructor(**dict(row))


class SQLiteSearchRepository(SearchRepository):
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def create(self, search: Search) -> Search:
        payload = asdict(search)
        self.conn.execute(
            """
            INSERT INTO searches (
                id, query_text, industry, location, status, created_at, updated_at
            ) VALUES (
                :id, :query_text, :industry, :location, :status, :created_at, :updated_at
            )
            """,
            payload,
        )
        self.conn.commit()
        return search

    def get(self, search_id: str) -> Search | None:
        row = self.conn.execute("SELECT * FROM searches WHERE id = ?", (search_id,)).fetchone()
        return _row_to_model(row, Search)


class SQLiteSearchRunRepository(SearchRunRepository):
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def create(self, search_run: SearchRun) -> SearchRun:
        payload = asdict(search_run)
        self.conn.execute(
            """
            INSERT INTO search_runs (
                id, search_id, pipeline_run_id, status, summary, started_at, finished_at
            ) VALUES (
                :id, :search_id, :pipeline_run_id, :status, :summary, :started_at, :finished_at
            )
            """,
            payload,
        )
        self.conn.commit()
        return search_run

    def get(self, search_run_id: str) -> SearchRun | None:
        row = self.conn.execute("SELECT * FROM search_runs WHERE id = ?", (search_run_id,)).fetchone()
        return _row_to_model(row, SearchRun)

    def list_for_search(self, search_id: str) -> list[SearchRun]:
        rows = self.conn.execute(
            "SELECT * FROM search_runs WHERE search_id = ? ORDER BY started_at ASC, id ASC",
            (search_id,),
        ).fetchall()
        return [SearchRun(**dict(row)) for row in rows]


class SQLiteLeadRepository(LeadRepository):
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def create(self, lead: Lead) -> Lead:
        payload = asdict(lead)
        self.conn.execute(
            """
            INSERT INTO leads (
                id, search_id, search_run_id, source, source_record_id, name, score, status,
                created_at, updated_at
            ) VALUES (
                :id, :search_id, :search_run_id, :source, :source_record_id, :name, :score, :status,
                :created_at, :updated_at
            )
            """,
            payload,
        )
        self.conn.commit()
        return lead

    def get(self, lead_id: str) -> Lead | None:
        row = self.conn.execute("SELECT * FROM leads WHERE id = ?", (lead_id,)).fetchone()
        return _row_to_model(row, Lead)

    def list_for_search(self, search_id: str) -> list[Lead]:
        rows = self.conn.execute(
            "SELECT * FROM leads WHERE search_id = ? ORDER BY created_at ASC, id ASC",
            (search_id,),
        ).fetchall()
        return [Lead(**dict(row)) for row in rows]


class SQLiteWorkflowRunRepository(WorkflowRunRepository):
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def create(self, workflow_run: WorkflowRun) -> WorkflowRun:
        payload = asdict(workflow_run)
        self.conn.execute(
            """
            INSERT INTO workflow_runs (
                id, search_run_id, workflow_name, status, metadata_json, started_at, finished_at
            ) VALUES (
                :id, :search_run_id, :workflow_name, :status, :metadata_json, :started_at, :finished_at
            )
            """,
            payload,
        )
        self.conn.commit()
        return workflow_run

    def get(self, workflow_run_id: str) -> WorkflowRun | None:
        row = self.conn.execute("SELECT * FROM workflow_runs WHERE id = ?", (workflow_run_id,)).fetchone()
        return _row_to_model(row, WorkflowRun)


class SQLiteWorkflowArtifactRepository(WorkflowArtifactRepository):
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def create(self, workflow_artifact: WorkflowArtifact) -> WorkflowArtifact:
        payload = asdict(workflow_artifact)
        self.conn.execute(
            """
            INSERT INTO workflow_artifacts (
                id, workflow_run_id, artifact_type, uri, metadata_json, created_at
            ) VALUES (
                :id, :workflow_run_id, :artifact_type, :uri, :metadata_json, :created_at
            )
            """,
            payload,
        )
        self.conn.commit()
        return workflow_artifact

    def list_for_workflow_run(self, workflow_run_id: str) -> list[WorkflowArtifact]:
        rows = self.conn.execute(
            "SELECT * FROM workflow_artifacts WHERE workflow_run_id = ? ORDER BY created_at ASC, id ASC",
            (workflow_run_id,),
        ).fetchall()
        return [WorkflowArtifact(**dict(row)) for row in rows]


class SQLiteOutboundAttemptRepository(OutboundAttemptRepository):
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def create(self, outbound_attempt: OutboundAttempt) -> OutboundAttempt:
        payload = asdict(outbound_attempt)
        self.conn.execute(
            """
            INSERT INTO outbound_attempts (
                id, lead_id, channel, target, status, template_key, response_json, attempted_at
            ) VALUES (
                :id, :lead_id, :channel, :target, :status, :template_key, :response_json, :attempted_at
            )
            """,
            payload,
        )
        self.conn.commit()
        return outbound_attempt

    def list_for_lead(self, lead_id: str) -> list[OutboundAttempt]:
        rows = self.conn.execute(
            "SELECT * FROM outbound_attempts WHERE lead_id = ? ORDER BY attempted_at ASC, id ASC",
            (lead_id,),
        ).fetchall()
        return [OutboundAttempt(**dict(row)) for row in rows]


class SQLiteExternalRecordLinkRepository(ExternalRecordLinkRepository):
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def create(self, external_record_link: ExternalRecordLink) -> ExternalRecordLink:
        payload = asdict(external_record_link)
        self.conn.execute(
            """
            INSERT INTO external_record_links (
                id, owner_type, owner_id, provider, external_id, url, created_at
            ) VALUES (
                :id, :owner_type, :owner_id, :provider, :external_id, :url, :created_at
            )
            """,
            payload,
        )
        self.conn.commit()
        return external_record_link

    def list_for_owner(self, owner_type: str, owner_id: str) -> list[ExternalRecordLink]:
        rows = self.conn.execute(
            """
            SELECT * FROM external_record_links
            WHERE owner_type = ? AND owner_id = ?
            ORDER BY created_at ASC, id ASC
            """,
            (owner_type, owner_id),
        ).fetchall()
        return [ExternalRecordLink(**dict(row)) for row in rows]


class SQLiteNoteRepository(NoteRepository):
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def create(self, note: Note) -> Note:
        payload = asdict(note)
        self.conn.execute(
            """
            INSERT INTO notes (
                id, owner_type, owner_id, body, author, created_at
            ) VALUES (
                :id, :owner_type, :owner_id, :body, :author, :created_at
            )
            """,
            payload,
        )
        self.conn.commit()
        return note

    def list_for_owner(self, owner_type: str, owner_id: str) -> list[Note]:
        rows = self.conn.execute(
            """
            SELECT * FROM notes
            WHERE owner_type = ? AND owner_id = ?
            ORDER BY created_at ASC, id ASC
            """,
            (owner_type, owner_id),
        ).fetchall()
        return [Note(**dict(row)) for row in rows]


class SQLiteAppStorage:
    """SQLite-backed app storage with canonical repositories."""

    def __init__(self, db_path: str | Path = "outputs/pipeline/canonical.db") -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        bootstrap_app_schema(self.conn)

        self.searches = SQLiteSearchRepository(self.conn)
        self.search_runs = SQLiteSearchRunRepository(self.conn)
        self.leads = SQLiteLeadRepository(self.conn)
        self.workflow_runs = SQLiteWorkflowRunRepository(self.conn)
        self.workflow_artifacts = SQLiteWorkflowArtifactRepository(self.conn)
        self.outbound_attempts = SQLiteOutboundAttemptRepository(self.conn)
        self.external_record_links = SQLiteExternalRecordLinkRepository(self.conn)
        self.notes = SQLiteNoteRepository(self.conn)

    def close(self) -> None:
        self.conn.close()

