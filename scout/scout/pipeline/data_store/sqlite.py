"""SQLite DataStore implementation."""

from __future__ import annotations

import hashlib
import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from scout.pipeline.data_store.base import DataStore
from scout.pipeline.data_store.raw_snapshot import persist_snapshot
from scout.pipeline.models.business import Business
from scout.pipeline.models.listing import Listing
from scout.pipeline.models.query import Query


def _normalize_token(value: str) -> str:
    return " ".join((value or "").strip().lower().split())


def _search_key(industry: str, location: str) -> str:
    return f"{_normalize_token(industry)}::{_normalize_token(location)}"


def _business_key(source: str, name: str, address: str) -> str:
    return "|".join(
        [
            _normalize_token(source),
            _normalize_token(name),
            _normalize_token(address),
        ]
    )


def _payload_hash(payload: dict[str, Any]) -> str:
    serialized = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def _changed_fields(previous: dict[str, Any], current: dict[str, Any]) -> list[str]:
    keys = sorted(set(previous) | set(current))
    return [key for key in keys if previous.get(key) != current.get(key)]


@dataclass(frozen=True)
class _CurrentBusinessSnapshot:
    business: Business
    payload: dict[str, Any]
    payload_json: str
    payload_hash: str


@dataclass(frozen=True)
class _StoredBusinessSnapshot:
    payload: dict[str, Any]
    payload_hash: str
    business_name: str
    business_address: str


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
                first_seen_run_id TEXT,
                first_seen_at TEXT,
                last_seen_run_id TEXT,
                last_seen_at TEXT,
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

            CREATE TABLE IF NOT EXISTS search_runs (
                run_id TEXT PRIMARY KEY,
                search_key TEXT NOT NULL,
                industry TEXT NOT NULL,
                location TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_search_runs_key_created_at
                ON search_runs(search_key, created_at);

            CREATE TABLE IF NOT EXISTS business_search_snapshots (
                run_id TEXT NOT NULL,
                search_key TEXT NOT NULL,
                business_key TEXT NOT NULL,
                business_id INTEGER,
                business_name TEXT NOT NULL,
                business_address TEXT NOT NULL,
                payload TEXT NOT NULL,
                payload_hash TEXT NOT NULL,
                PRIMARY KEY (run_id, business_key),
                FOREIGN KEY (run_id) REFERENCES search_runs(run_id)
            );
            CREATE INDEX IF NOT EXISTS idx_business_snapshots_search_run
                ON business_search_snapshots(search_key, run_id);

            CREATE TABLE IF NOT EXISTS search_business_diffs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                search_key TEXT NOT NULL,
                run_id TEXT NOT NULL,
                previous_run_id TEXT,
                business_key TEXT NOT NULL,
                business_name TEXT NOT NULL,
                business_address TEXT NOT NULL,
                change_type TEXT NOT NULL,
                changed_fields TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (run_id) REFERENCES search_runs(run_id)
            );
            CREATE INDEX IF NOT EXISTS idx_search_business_diffs_search_run
                ON search_business_diffs(search_key, run_id);
            """)
        self._ensure_column("businesses", "first_seen_run_id", "TEXT")
        self._ensure_column("businesses", "first_seen_at", "TEXT")
        self._ensure_column("businesses", "last_seen_run_id", "TEXT")
        self._ensure_column("businesses", "last_seen_at", "TEXT")
        self.conn.commit()

    def _ensure_column(self, table_name: str, column_name: str, column_sql: str) -> None:
        rows = self.conn.execute(f"PRAGMA table_info({table_name})").fetchall()
        existing_columns = {row["name"] for row in rows}
        if column_name in existing_columns:
            return
        self.conn.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_sql}")

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

    def record_business_history(self, query: Query, businesses: list[Business]) -> None:
        search_key = _search_key(query.industry, query.location)
        run_id = query.run_id
        run_created_at = query.created_at

        current_snapshot: dict[str, _CurrentBusinessSnapshot] = {}
        for business in businesses:
            if not business.name:
                continue
            payload = business.to_dict()
            payload_json = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
            key = _business_key(business.source, business.name, business.address)
            current_snapshot[key] = _CurrentBusinessSnapshot(
                business=business,
                payload=payload,
                payload_json=payload_json,
                payload_hash=_payload_hash(payload),
            )

        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO search_runs (run_id, search_key, industry, location, created_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(run_id) DO UPDATE SET
                search_key=excluded.search_key,
                industry=excluded.industry,
                location=excluded.location,
                created_at=excluded.created_at
            """,
            (run_id, search_key, query.industry, query.location, run_created_at),
        )

        previous_run_id = self._latest_previous_run_id(cursor, search_key, run_id)
        previous_snapshot = self._load_snapshot(cursor, previous_run_id)

        cursor.execute("DELETE FROM business_search_snapshots WHERE run_id = ?", (run_id,))
        for key, snapshot in current_snapshot.items():
            business_id = self._lookup_business_id(cursor, snapshot.business)
            cursor.execute(
                """
                INSERT INTO business_search_snapshots (
                    run_id,
                    search_key,
                    business_key,
                    business_id,
                    business_name,
                    business_address,
                    payload,
                    payload_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run_id,
                    search_key,
                    key,
                    business_id,
                    snapshot.business.name,
                    snapshot.business.address,
                    snapshot.payload_json,
                    snapshot.payload_hash,
                ),
            )
            if business_id is not None:
                cursor.execute(
                    """
                    UPDATE businesses
                    SET first_seen_run_id = COALESCE(first_seen_run_id, ?),
                        first_seen_at = COALESCE(first_seen_at, ?),
                        last_seen_run_id = ?,
                        last_seen_at = ?
                    WHERE id = ?
                    """,
                    (run_id, run_created_at, run_id, run_created_at, business_id),
                )

        cursor.execute("DELETE FROM search_business_diffs WHERE run_id = ?", (run_id,))
        if previous_run_id:
            current_keys = set(current_snapshot)
            previous_keys = set(previous_snapshot)

            for key in sorted(current_keys - previous_keys):
                snapshot = current_snapshot[key]
                self._insert_diff_row(
                    cursor=cursor,
                    search_key=search_key,
                    run_id=run_id,
                    previous_run_id=previous_run_id,
                    business_key=key,
                    business_name=snapshot.business.name,
                    business_address=snapshot.business.address,
                    change_type="new",
                    changed_fields=[],
                    created_at=run_created_at,
                )

            for key in sorted(previous_keys - current_keys):
                snapshot = previous_snapshot[key]
                self._insert_diff_row(
                    cursor=cursor,
                    search_key=search_key,
                    run_id=run_id,
                    previous_run_id=previous_run_id,
                    business_key=key,
                    business_name=snapshot.business_name,
                    business_address=snapshot.business_address,
                    change_type="removed",
                    changed_fields=[],
                    created_at=run_created_at,
                )

            for key in sorted(current_keys & previous_keys):
                current = current_snapshot[key]
                previous = previous_snapshot[key]
                if current.payload_hash == previous.payload_hash:
                    continue
                self._insert_diff_row(
                    cursor=cursor,
                    search_key=search_key,
                    run_id=run_id,
                    previous_run_id=previous_run_id,
                    business_key=key,
                    business_name=current.business.name,
                    business_address=current.business.address,
                    change_type="changed",
                    changed_fields=_changed_fields(previous.payload, current.payload),
                    created_at=run_created_at,
                )

        self.conn.commit()

    def _latest_previous_run_id(
        self,
        cursor: sqlite3.Cursor,
        search_key: str,
        current_run_id: str,
    ) -> str | None:
        row = cursor.execute(
            """
            SELECT run_id
            FROM search_runs
            WHERE search_key = ? AND run_id != ?
            ORDER BY created_at DESC, run_id DESC
            LIMIT 1
            """,
            (search_key, current_run_id),
        ).fetchone()
        if row is None:
            return None
        return str(row["run_id"])

    def _load_snapshot(
        self,
        cursor: sqlite3.Cursor,
        run_id: str | None,
    ) -> dict[str, _StoredBusinessSnapshot]:
        if run_id is None:
            return {}

        rows = cursor.execute(
            """
            SELECT business_key, business_name, business_address, payload, payload_hash
            FROM business_search_snapshots
            WHERE run_id = ?
            """,
            (run_id,),
        ).fetchall()

        result: dict[str, _StoredBusinessSnapshot] = {}
        for row in rows:
            payload_text = row["payload"] if isinstance(row["payload"], str) else "{}"
            try:
                payload_obj = json.loads(payload_text)
            except json.JSONDecodeError:
                payload_obj = {}
            if not isinstance(payload_obj, dict):
                payload_obj = {}
            result[str(row["business_key"])] = _StoredBusinessSnapshot(
                payload=payload_obj,
                payload_hash=str(row["payload_hash"]),
                business_name=str(row["business_name"]),
                business_address=str(row["business_address"]),
            )
        return result

    def _lookup_business_id(self, cursor: sqlite3.Cursor, business: Business) -> int | None:
        row = cursor.execute(
            """
            SELECT id
            FROM businesses
            WHERE source = ? AND name = ? AND COALESCE(address, '') = COALESCE(?, '')
            ORDER BY id DESC
            LIMIT 1
            """,
            (business.source, business.name, business.address),
        ).fetchone()
        if row is None:
            return None
        return int(row["id"])

    def _insert_diff_row(
        self,
        *,
        cursor: sqlite3.Cursor,
        search_key: str,
        run_id: str,
        previous_run_id: str,
        business_key: str,
        business_name: str,
        business_address: str,
        change_type: str,
        changed_fields: list[str],
        created_at: str,
    ) -> None:
        cursor.execute(
            """
            INSERT INTO search_business_diffs (
                search_key,
                run_id,
                previous_run_id,
                business_key,
                business_name,
                business_address,
                change_type,
                changed_fields,
                created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                search_key,
                run_id,
                previous_run_id,
                business_key,
                business_name,
                business_address,
                change_type,
                json.dumps(changed_fields, sort_keys=True),
                created_at,
            ),
        )
