"""SQLite DataStore implementation."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

from scout.pipeline.data_store.base import DataStore
from scout.pipeline.data_store.raw_snapshot import persist_snapshot
from scout.pipeline.models.business import Business
from scout.pipeline.models.listing import Listing
from scout.pipeline.models.query import Query
from scout.pipeline.models.workflow_run import (
    WORKFLOW_STATUS_COMPLETED,
    WORKFLOW_STATUS_FAILED,
    WORKFLOW_STATUS_QUEUED,
    WORKFLOW_STATUS_RUNNING,
    WorkflowError,
    WorkflowRun,
)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _to_iso(ts: datetime | None = None) -> str:
    return (ts or _utc_now()).isoformat()


def _to_datetime(value: datetime | str | None) -> datetime:
    if value is None:
        return _utc_now()
    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed


class SQLiteDataStore(DataStore):
    def __init__(
        self,
        db_path: str | Path = "outputs/pipeline/canonical.db",
        raw_root: str | Path = "outputs/pipeline/raw",
    ) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.raw_root = Path(raw_root)
        self.raw_root.mkdir(parents=True, exist_ok=True)

        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self) -> None:
        cursor = self.conn.cursor()
        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS businesses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT NOT NULL,
                name TEXT NOT NULL,
                address TEXT,
                phone TEXT,
                website TEXT,
                category TEXT,
                location TEXT,
                state TEXT,
                rating REAL,
                reviews INTEGER,
                UNIQUE(source, name, address)
            );

            CREATE TABLE IF NOT EXISTS listings (
                id TEXT PRIMARY KEY,
                source TEXT NOT NULL,
                source_id TEXT NOT NULL,
                url TEXT,
                name TEXT NOT NULL,
                industry TEXT,
                location TEXT,
                state TEXT,
                description TEXT,
                asking_price REAL,
                annual_revenue REAL,
                cash_flow REAL,
                asking_multiple REAL,
                days_on_market INTEGER,
                broker TEXT,
                listed_at TEXT,
                fetched_at TEXT
            );

            CREATE TABLE IF NOT EXISTS workflow_runs (
                run_id TEXT PRIMARY KEY,
                industry TEXT NOT NULL,
                location TEXT NOT NULL,
                max_results INTEGER NOT NULL,
                use_cache INTEGER NOT NULL,
                status TEXT NOT NULL,
                attempt_count INTEGER NOT NULL DEFAULT 0,
                max_attempts INTEGER NOT NULL,
                available_at TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                worker_id TEXT,
                claimed_at TEXT,
                started_at TEXT,
                finished_at TEXT,
                error_type TEXT,
                error_message TEXT,
                error_details TEXT
            );
            CREATE INDEX IF NOT EXISTS idx_workflow_runs_claim
                ON workflow_runs(status, available_at, created_at);
            """)
        self.conn.commit()

    def persist_raw(self, run_id: str, source: str, payload: dict[str, object]) -> str:
        return persist_snapshot(self.raw_root, run_id, source, payload)

    def upsert_businesses(self, businesses: list[Business]) -> int:
        if not businesses:
            return 0

        rows = [
            (
                business.source,
                business.name,
                business.address,
                business.phone,
                business.website,
                business.category,
                business.location,
                business.state,
                business.rating,
                business.reviews,
            )
            for business in businesses
            if business.name
        ]

        self.conn.executemany(
            """
            INSERT INTO businesses (
                source, name, address, phone, website, category, location, state, rating, reviews
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(source, name, address) DO UPDATE SET
                phone=excluded.phone,
                website=excluded.website,
                category=excluded.category,
                location=excluded.location,
                state=excluded.state,
                rating=excluded.rating,
                reviews=excluded.reviews
            """,
            rows,
        )
        self.conn.commit()
        return len(rows)

    def upsert_listings(self, listings: list[Listing]) -> int:
        if not listings:
            return 0

        rows = [
            (
                listing.id,
                listing.source,
                listing.source_id,
                listing.url,
                listing.name,
                listing.industry,
                listing.location,
                listing.state,
                listing.description,
                listing.asking_price,
                listing.annual_revenue,
                listing.cash_flow,
                listing.asking_multiple,
                listing.days_on_market,
                listing.broker,
                listing.listed_at,
                listing.fetched_at,
            )
            for listing in listings
            if listing.name
        ]

        self.conn.executemany(
            """
            INSERT INTO listings (
                id, source, source_id, url, name, industry, location, state, description,
                asking_price, annual_revenue, cash_flow, asking_multiple, days_on_market,
                broker, listed_at, fetched_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                url=excluded.url,
                name=excluded.name,
                industry=excluded.industry,
                location=excluded.location,
                state=excluded.state,
                description=excluded.description,
                asking_price=excluded.asking_price,
                annual_revenue=excluded.annual_revenue,
                cash_flow=excluded.cash_flow,
                asking_multiple=excluded.asking_multiple,
                days_on_market=excluded.days_on_market,
                broker=excluded.broker,
                listed_at=excluded.listed_at,
                fetched_at=excluded.fetched_at
            """,
            rows,
        )
        self.conn.commit()
        return len(rows)

    def enqueue_workflow(
        self,
        query: Query,
        max_attempts: int = 3,
        available_at: datetime | str | None = None,
    ) -> WorkflowRun:
        if max_attempts < 1:
            raise ValueError("max_attempts must be >= 1")

        available_at_dt = (
            _to_datetime(available_at)
            if available_at is not None
            else _to_datetime(query.created_at)
        )
        now_iso = _to_iso()
        available_at_iso = _to_iso(available_at_dt)
        use_cache = 1 if query.use_cache else 0

        self.conn.execute(
            """
            INSERT INTO workflow_runs (
                run_id, industry, location, max_results, use_cache, status,
                attempt_count, max_attempts, available_at, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, 0, ?, ?, ?, ?)
            """,
            (
                query.run_id,
                query.industry,
                query.location,
                query.max_results,
                use_cache,
                WORKFLOW_STATUS_QUEUED,
                max_attempts,
                available_at_iso,
                query.created_at,
                now_iso,
            ),
        )
        self.conn.commit()
        run = self.get_workflow_run(query.run_id)
        assert run is not None
        return run

    def claim_next_workflow(
        self,
        worker_id: str,
        now: datetime | str | None = None,
    ) -> WorkflowRun | None:
        if not worker_id.strip():
            raise ValueError("worker_id must be non-empty")

        now_iso = _to_iso(_to_datetime(now))
        cursor = self.conn.cursor()
        cursor.execute("BEGIN IMMEDIATE")
        cursor.execute(
            """
            SELECT run_id
            FROM workflow_runs
            WHERE status = ? AND available_at <= ?
            ORDER BY available_at ASC, created_at ASC
            LIMIT 1
            """,
            (WORKFLOW_STATUS_QUEUED, now_iso),
        )
        row = cursor.fetchone()
        if row is None:
            self.conn.commit()
            return None

        run_id = row["run_id"]
        cursor.execute(
            """
            UPDATE workflow_runs
            SET status = ?,
                attempt_count = attempt_count + 1,
                worker_id = ?,
                claimed_at = ?,
                started_at = ?,
                updated_at = ?,
                finished_at = NULL
            WHERE run_id = ? AND status = ?
            """,
            (
                WORKFLOW_STATUS_RUNNING,
                worker_id,
                now_iso,
                now_iso,
                now_iso,
                run_id,
                WORKFLOW_STATUS_QUEUED,
            ),
        )
        if cursor.rowcount != 1:
            self.conn.commit()
            return None
        self.conn.commit()
        run = self.get_workflow_run(run_id)
        assert run is not None
        return run

    def complete_workflow(self, run_id: str, now: datetime | str | None = None) -> WorkflowRun:
        now_iso = _to_iso(_to_datetime(now))
        cursor = self.conn.execute(
            """
            UPDATE workflow_runs
            SET status = ?,
                finished_at = ?,
                updated_at = ?
            WHERE run_id = ? AND status = ?
            """,
            (
                WORKFLOW_STATUS_COMPLETED,
                now_iso,
                now_iso,
                run_id,
                WORKFLOW_STATUS_RUNNING,
            ),
        )
        self.conn.commit()
        if cursor.rowcount != 1:
            raise ValueError(f"run_id={run_id} is not in running state")
        run = self.get_workflow_run(run_id)
        assert run is not None
        return run

    def fail_workflow(
        self,
        run_id: str,
        error_type: str,
        error_message: str,
        error_details: dict[str, object] | None = None,
        retry_delay_seconds: int = 0,
        now: datetime | str | None = None,
    ) -> WorkflowRun:
        if retry_delay_seconds < 0:
            raise ValueError("retry_delay_seconds must be >= 0")

        now_dt = _to_datetime(now)
        now_iso = _to_iso(now_dt)
        run = self.get_workflow_run(run_id)
        if run is None:
            raise ValueError(f"unknown run_id={run_id}")
        if run.status != WORKFLOW_STATUS_RUNNING:
            raise ValueError(f"run_id={run_id} is not in running state")

        should_retry = run.attempt_count < run.max_attempts
        next_status = WORKFLOW_STATUS_QUEUED if should_retry else WORKFLOW_STATUS_FAILED
        available_at_iso = (
            _to_iso(now_dt + timedelta(seconds=retry_delay_seconds))
            if should_retry
            else run.available_at
        )
        finished_at_iso = None if should_retry else now_iso
        details_json = json.dumps(error_details or {}, sort_keys=True)

        self.conn.execute(
            """
            UPDATE workflow_runs
            SET status = ?,
                available_at = ?,
                finished_at = ?,
                updated_at = ?,
                error_type = ?,
                error_message = ?,
                error_details = ?
            WHERE run_id = ? AND status = ?
            """,
            (
                next_status,
                available_at_iso,
                finished_at_iso,
                now_iso,
                error_type,
                error_message,
                details_json,
                run_id,
                WORKFLOW_STATUS_RUNNING,
            ),
        )
        self.conn.commit()
        updated = self.get_workflow_run(run_id)
        assert updated is not None
        return updated

    def get_workflow_run(self, run_id: str) -> WorkflowRun | None:
        row = self.conn.execute(
            "SELECT * FROM workflow_runs WHERE run_id = ?", (run_id,)
        ).fetchone()
        if row is None:
            return None
        return self._row_to_workflow_run(row)

    @staticmethod
    def _row_to_workflow_run(row: sqlite3.Row) -> WorkflowRun:
        details = {}
        if row["error_details"]:
            details = json.loads(row["error_details"])

        error = None
        if row["error_type"] or row["error_message"]:
            error = WorkflowError(
                error_type=row["error_type"] or "",
                message=row["error_message"] or "",
                details=details,
            )

        return WorkflowRun(
            run_id=row["run_id"],
            industry=row["industry"],
            location=row["location"],
            max_results=row["max_results"],
            use_cache=bool(row["use_cache"]),
            status=row["status"],
            attempt_count=row["attempt_count"],
            max_attempts=row["max_attempts"],
            available_at=row["available_at"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            worker_id=row["worker_id"],
            claimed_at=row["claimed_at"],
            started_at=row["started_at"],
            finished_at=row["finished_at"],
            error=error,
        )
