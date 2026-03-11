"""SQLite DataStore implementation."""

from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path
from typing import Any

from scout.pipeline.data_store.base import DataStore
from scout.pipeline.data_store.raw_snapshot import persist_snapshot
from scout.pipeline.models.business import Business
from scout.pipeline.models.listing import Listing
from scout.pipeline.models.market_dataset import RunDiffSummary
from scout.pipeline.models.query import Query


def _clean(value: str | None) -> str:
    return (value or "").strip().lower()


def _business_item_key(business: Business) -> str:
    raw = "||".join(
        [
            _clean(business.source),
            _clean(business.name),
            _clean(business.address),
            _clean(business.location),
            _clean(business.phone),
        ]
    )
    return f"business:{hashlib.sha1(raw.encode('utf-8')).hexdigest()[:20]}"


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
        self.conn.execute("PRAGMA foreign_keys = ON")
        self._create_tables()

    def _create_tables(self) -> None:
        cursor = self.conn.cursor()
        cursor.executescript(
            """
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

            CREATE TABLE IF NOT EXISTS search_runs (
                seq INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT NOT NULL UNIQUE,
                industry TEXT NOT NULL,
                location TEXT NOT NULL,
                max_results INTEGER NOT NULL,
                use_cache INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                business_count INTEGER NOT NULL,
                listing_count INTEGER NOT NULL
            );

            CREATE TABLE IF NOT EXISTS run_entities (
                run_id TEXT NOT NULL,
                item_type TEXT NOT NULL,
                item_key TEXT NOT NULL,
                source TEXT NOT NULL,
                name TEXT NOT NULL,
                location TEXT,
                state TEXT,
                payload_json TEXT NOT NULL,
                PRIMARY KEY (run_id, item_type, item_key),
                FOREIGN KEY (run_id) REFERENCES search_runs(run_id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS run_diffs (
                run_id TEXT PRIMARY KEY,
                previous_run_id TEXT,
                compared_at TEXT NOT NULL,
                added_businesses INTEGER NOT NULL,
                removed_businesses INTEGER NOT NULL,
                added_listings INTEGER NOT NULL,
                removed_listings INTEGER NOT NULL,
                FOREIGN KEY (run_id) REFERENCES search_runs(run_id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS run_diff_items (
                run_id TEXT NOT NULL,
                item_type TEXT NOT NULL,
                change_type TEXT NOT NULL,
                item_key TEXT NOT NULL,
                source TEXT NOT NULL,
                name TEXT NOT NULL,
                location TEXT,
                state TEXT,
                payload_json TEXT NOT NULL,
                PRIMARY KEY (run_id, item_type, change_type, item_key),
                FOREIGN KEY (run_id) REFERENCES run_diffs(run_id) ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_search_runs_industry_location
            ON search_runs(industry, location, seq DESC);

            CREATE INDEX IF NOT EXISTS idx_run_entities_lookup
            ON run_entities(run_id, item_type, item_key);

            CREATE INDEX IF NOT EXISTS idx_run_diff_items_run
            ON run_diff_items(run_id, item_type, change_type);
            """
        )
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

    def record_run(
        self,
        *,
        query: Query,
        businesses: list[Business],
        listings: list[Listing],
    ) -> RunDiffSummary:
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO search_runs (
                run_id, industry, location, max_results, use_cache, created_at, business_count, listing_count
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(run_id) DO UPDATE SET
                industry=excluded.industry,
                location=excluded.location,
                max_results=excluded.max_results,
                use_cache=excluded.use_cache,
                created_at=excluded.created_at,
                business_count=excluded.business_count,
                listing_count=excluded.listing_count
            """,
            (
                query.run_id,
                query.industry,
                query.location,
                query.max_results,
                1 if query.use_cache else 0,
                query.created_at,
                len(businesses),
                len(listings),
            ),
        )

        cursor.execute("DELETE FROM run_entities WHERE run_id = ?", (query.run_id,))
        entity_rows = self._build_entity_rows(query.run_id, businesses, listings)
        if entity_rows:
            cursor.executemany(
                """
                INSERT INTO run_entities (
                    run_id, item_type, item_key, source, name, location, state, payload_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                entity_rows,
            )

        previous_run_id = self._previous_run_id(
            cursor=cursor,
            run_id=query.run_id,
            industry=query.industry,
            location=query.location,
        )
        summary = self._persist_diff(
            cursor=cursor,
            run_id=query.run_id,
            compared_at=query.created_at,
            previous_run_id=previous_run_id,
            current_rows=entity_rows,
        )
        self.conn.commit()
        return summary

    def list_search_runs(
        self,
        *,
        limit: int = 10,
        industry: str | None = None,
        location: str | None = None,
    ) -> list[sqlite3.Row]:
        query = """
            SELECT
                r.run_id,
                r.industry,
                r.location,
                r.max_results,
                r.use_cache,
                r.created_at,
                r.business_count,
                r.listing_count,
                d.previous_run_id,
                d.added_businesses,
                d.removed_businesses,
                d.added_listings,
                d.removed_listings
            FROM search_runs r
            LEFT JOIN run_diffs d ON d.run_id = r.run_id
        """
        where_clauses: list[str] = []
        params: list[Any] = []
        if industry:
            where_clauses.append("r.industry = ?")
            params.append(industry)
        if location:
            where_clauses.append("r.location = ?")
            params.append(location)
        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)
        query += " ORDER BY r.seq DESC LIMIT ?"
        params.append(limit)
        return list(self.conn.execute(query, params))

    def get_run_diff(self, run_id: str) -> sqlite3.Row | None:
        row = self.conn.execute(
            """
            SELECT
                r.run_id,
                r.industry,
                r.location,
                r.created_at,
                r.business_count,
                r.listing_count,
                d.previous_run_id,
                COALESCE(d.added_businesses, 0) AS added_businesses,
                COALESCE(d.removed_businesses, 0) AS removed_businesses,
                COALESCE(d.added_listings, 0) AS added_listings,
                COALESCE(d.removed_listings, 0) AS removed_listings
            FROM search_runs r
            LEFT JOIN run_diffs d ON d.run_id = r.run_id
            WHERE r.run_id = ?
            """,
            (run_id,),
        ).fetchone()
        return row

    def get_run_diff_items(self, run_id: str) -> list[sqlite3.Row]:
        return list(
            self.conn.execute(
                """
                SELECT
                    run_id,
                    item_type,
                    change_type,
                    item_key,
                    source,
                    name,
                    location,
                    state,
                    payload_json
                FROM run_diff_items
                WHERE run_id = ?
                ORDER BY item_type, change_type, name, item_key
                """,
                (run_id,),
            )
        )

    def close(self) -> None:
        self.conn.close()

    def _build_entity_rows(
        self,
        run_id: str,
        businesses: list[Business],
        listings: list[Listing],
    ) -> list[tuple[str, str, str, str, str, str, str, str]]:
        rows: list[tuple[str, str, str, str, str, str, str, str]] = []
        for business in businesses:
            if not business.name:
                continue
            rows.append(
                (
                    run_id,
                    "business",
                    _business_item_key(business),
                    business.source,
                    business.name,
                    business.location,
                    business.state,
                    json.dumps(business.to_dict(), sort_keys=True),
                )
            )
        for listing in listings:
            if not listing.name:
                continue
            rows.append(
                (
                    run_id,
                    "listing",
                    listing.id,
                    listing.source,
                    listing.name,
                    listing.location,
                    listing.state,
                    json.dumps(listing.to_dict(), sort_keys=True),
                )
            )
        return rows

    def _previous_run_id(
        self,
        *,
        cursor: sqlite3.Cursor,
        run_id: str,
        industry: str,
        location: str,
    ) -> str | None:
        row = cursor.execute(
            """
            SELECT run_id
            FROM search_runs
            WHERE industry = ?
              AND location = ?
              AND seq < (SELECT seq FROM search_runs WHERE run_id = ?)
            ORDER BY seq DESC
            LIMIT 1
            """,
            (industry, location, run_id),
        ).fetchone()
        if row is None:
            return None
        value = row["run_id"]
        return value if isinstance(value, str) else None

    def _persist_diff(
        self,
        *,
        cursor: sqlite3.Cursor,
        run_id: str,
        compared_at: str,
        previous_run_id: str | None,
        current_rows: list[tuple[str, str, str, str, str, str, str, str]],
    ) -> RunDiffSummary:
        cursor.execute("DELETE FROM run_diff_items WHERE run_id = ?", (run_id,))

        if previous_run_id is None:
            summary = RunDiffSummary(run_id=run_id, previous_run_id=None)
            cursor.execute(
                """
                INSERT INTO run_diffs (
                    run_id, previous_run_id, compared_at,
                    added_businesses, removed_businesses, added_listings, removed_listings
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(run_id) DO UPDATE SET
                    previous_run_id=excluded.previous_run_id,
                    compared_at=excluded.compared_at,
                    added_businesses=excluded.added_businesses,
                    removed_businesses=excluded.removed_businesses,
                    added_listings=excluded.added_listings,
                    removed_listings=excluded.removed_listings
                """,
                (
                    run_id,
                    None,
                    compared_at,
                    summary.added_businesses,
                    summary.removed_businesses,
                    summary.added_listings,
                    summary.removed_listings,
                ),
            )
            return summary

        current = self._row_map(current_rows)
        previous_rows = list(
            cursor.execute(
                """
                SELECT run_id, item_type, item_key, source, name, location, state, payload_json
                FROM run_entities
                WHERE run_id = ?
                """,
                (previous_run_id,),
            )
        )
        previous = self._row_map(
            [
                (
                    row["run_id"],
                    row["item_type"],
                    row["item_key"],
                    row["source"],
                    row["name"],
                    row["location"] or "",
                    row["state"] or "",
                    row["payload_json"],
                )
                for row in previous_rows
            ]
        )

        diff_item_rows: list[tuple[str, str, str, str, str, str, str, str, str]] = []
        added_businesses = 0
        removed_businesses = 0
        added_listings = 0
        removed_listings = 0

        for item_type in ("business", "listing"):
            current_keys = set(current[item_type].keys())
            previous_keys = set(previous[item_type].keys())

            for item_key in sorted(current_keys - previous_keys):
                row = current[item_type][item_key]
                diff_item_rows.append(
                    (
                        run_id,
                        item_type,
                        "added",
                        row[2],
                        row[3],
                        row[4],
                        row[5],
                        row[6],
                        row[7],
                    )
                )
            for item_key in sorted(previous_keys - current_keys):
                row = previous[item_type][item_key]
                diff_item_rows.append(
                    (
                        run_id,
                        item_type,
                        "removed",
                        row[2],
                        row[3],
                        row[4],
                        row[5],
                        row[6],
                        row[7],
                    )
                )

            if item_type == "business":
                added_businesses = len(current_keys - previous_keys)
                removed_businesses = len(previous_keys - current_keys)
            else:
                added_listings = len(current_keys - previous_keys)
                removed_listings = len(previous_keys - current_keys)

        summary = RunDiffSummary(
            run_id=run_id,
            previous_run_id=previous_run_id,
            added_businesses=added_businesses,
            removed_businesses=removed_businesses,
            added_listings=added_listings,
            removed_listings=removed_listings,
        )
        cursor.execute(
            """
            INSERT INTO run_diffs (
                run_id, previous_run_id, compared_at,
                added_businesses, removed_businesses, added_listings, removed_listings
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(run_id) DO UPDATE SET
                previous_run_id=excluded.previous_run_id,
                compared_at=excluded.compared_at,
                added_businesses=excluded.added_businesses,
                removed_businesses=excluded.removed_businesses,
                added_listings=excluded.added_listings,
                removed_listings=excluded.removed_listings
            """,
            (
                run_id,
                previous_run_id,
                compared_at,
                summary.added_businesses,
                summary.removed_businesses,
                summary.added_listings,
                summary.removed_listings,
            ),
        )
        if diff_item_rows:
            cursor.executemany(
                """
                INSERT INTO run_diff_items (
                    run_id, item_type, change_type, item_key, source, name, location, state, payload_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                diff_item_rows,
            )
        return summary

    @staticmethod
    def _row_map(
        rows: list[tuple[str, str, str, str, str, str, str, str]],
    ) -> dict[str, dict[str, tuple[str, str, str, str, str, str, str, str]]]:
        mapping: dict[str, dict[str, tuple[str, str, str, str, str, str, str, str]]] = {
            "business": {},
            "listing": {},
        }
        for row in rows:
            mapping[row[1]][row[2]] = row
        return mapping

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
