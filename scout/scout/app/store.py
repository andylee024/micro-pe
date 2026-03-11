"""SQLite app-layer store for persisted searches, runs, and curated leads."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from scout.app.models import LeadRecord, SearchRecord, SearchRunRecord
from scout.pipeline.models.business import Business


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalize_token(value: str) -> str:
    return " ".join(value.strip().lower().split())


def build_search_id(industry: str, location: str) -> str:
    return f"{_normalize_token(industry)}::{_normalize_token(location)}"


def _parse_lead_id(lead_id: str) -> tuple[str, str]:
    lead_id = lead_id.strip()
    prefix, sep, suffix = lead_id.partition(":")
    if sep != ":" or not suffix:
        raise ValueError("lead_id must use '<business|listing>:<id>' format")
    if prefix not in {"business", "listing"}:
        raise ValueError("lead_id prefix must be 'business' or 'listing'")
    return prefix, suffix


class AppStateStore:
    """App-level persistence for search/run state and curated lead actions."""

    def __init__(self, db_path: str | Path = "outputs/pipeline/canonical.db") -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self._create_tables()

    def close(self) -> None:
        self.conn.close()

    def _create_tables(self) -> None:
        self.conn.executescript("""
            PRAGMA foreign_keys = ON;

            CREATE TABLE IF NOT EXISTS searches (
                search_id TEXT PRIMARY KEY,
                query_text TEXT NOT NULL,
                industry TEXT NOT NULL,
                location TEXT NOT NULL,
                max_results INTEGER NOT NULL,
                use_cache INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS search_runs (
                run_id TEXT PRIMARY KEY,
                search_id TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                completed_at TEXT NOT NULL,
                business_count INTEGER NOT NULL DEFAULT 0,
                listing_count INTEGER NOT NULL DEFAULT 0,
                coverage_json TEXT NOT NULL DEFAULT '[]',
                FOREIGN KEY(search_id) REFERENCES searches(search_id)
            );
            CREATE INDEX IF NOT EXISTS idx_search_runs_search_created
                ON search_runs(search_id, created_at DESC);

            CREATE TABLE IF NOT EXISTS search_run_businesses (
                run_id TEXT NOT NULL,
                business_id INTEGER NOT NULL,
                PRIMARY KEY (run_id, business_id),
                FOREIGN KEY(run_id) REFERENCES search_runs(run_id),
                FOREIGN KEY(business_id) REFERENCES businesses(id)
            );
            CREATE INDEX IF NOT EXISTS idx_search_run_businesses_business
                ON search_run_businesses(business_id);

            CREATE TABLE IF NOT EXISTS search_run_listings (
                run_id TEXT NOT NULL,
                listing_id TEXT NOT NULL,
                PRIMARY KEY (run_id, listing_id),
                FOREIGN KEY(run_id) REFERENCES search_runs(run_id),
                FOREIGN KEY(listing_id) REFERENCES listings(id)
            );
            CREATE INDEX IF NOT EXISTS idx_search_run_listings_listing
                ON search_run_listings(listing_id);

            CREATE TABLE IF NOT EXISTS leads (
                lead_id TEXT PRIMARY KEY,
                lead_type TEXT NOT NULL,
                source TEXT NOT NULL,
                source_record_id TEXT NOT NULL,
                business_id INTEGER,
                listing_id TEXT,
                search_id TEXT NOT NULL,
                name TEXT NOT NULL,
                industry TEXT NOT NULL,
                location TEXT NOT NULL,
                state TEXT NOT NULL,
                phone TEXT NOT NULL,
                website TEXT NOT NULL,
                url TEXT NOT NULL,
                summary TEXT NOT NULL DEFAULT '',
                note TEXT NOT NULL DEFAULT '',
                saved_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(search_id) REFERENCES searches(search_id)
            );
            CREATE INDEX IF NOT EXISTS idx_leads_search_saved
                ON leads(search_id, saved_at DESC);
            """)
        self.conn.commit()

    def upsert_search(
        self,
        *,
        query_text: str,
        industry: str,
        location: str,
        max_results: int,
        use_cache: bool,
    ) -> SearchRecord:
        search_id = build_search_id(industry, location)
        now = _utc_now_iso()
        existing = self.get_search(search_id)
        if existing is None:
            created_at = now
            self.conn.execute(
                """
                INSERT INTO searches (
                    search_id, query_text, industry, location, max_results, use_cache, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    search_id,
                    query_text.strip(),
                    industry.strip(),
                    location.strip(),
                    int(max_results),
                    1 if use_cache else 0,
                    created_at,
                    now,
                ),
            )
        else:
            created_at = existing.created_at
            self.conn.execute(
                """
                UPDATE searches
                SET query_text = ?, industry = ?, location = ?, max_results = ?, use_cache = ?, updated_at = ?
                WHERE search_id = ?
                """,
                (
                    query_text.strip(),
                    industry.strip(),
                    location.strip(),
                    int(max_results),
                    1 if use_cache else 0,
                    now,
                    search_id,
                ),
            )
        self.conn.commit()
        updated = self.get_search(search_id)
        assert updated is not None
        return updated

    def get_search(self, search_id: str) -> SearchRecord | None:
        row = self.conn.execute(
            """
            SELECT search_id, query_text, industry, location, max_results, use_cache, created_at, updated_at
            FROM searches
            WHERE search_id = ?
            """,
            (search_id,),
        ).fetchone()
        if row is None:
            return None
        return SearchRecord(
            search_id=str(row["search_id"]),
            query_text=str(row["query_text"]),
            industry=str(row["industry"]),
            location=str(row["location"]),
            max_results=int(row["max_results"]),
            use_cache=bool(row["use_cache"]),
            created_at=str(row["created_at"]),
            updated_at=str(row["updated_at"]),
        )

    def get_latest_search_id(self) -> str | None:
        row = self.conn.execute(
            "SELECT search_id FROM searches ORDER BY updated_at DESC, search_id ASC LIMIT 1"
        ).fetchone()
        if row is None:
            return None
        return str(row["search_id"])

    def upsert_search_run(
        self,
        *,
        run_id: str,
        search_id: str,
        status: str,
        created_at: str,
        completed_at: str,
        business_count: int,
        listing_count: int,
        coverage_json: str,
    ) -> SearchRunRecord:
        self.conn.execute(
            """
            INSERT INTO search_runs (
                run_id, search_id, status, created_at, completed_at, business_count, listing_count, coverage_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(run_id) DO UPDATE SET
                search_id=excluded.search_id,
                status=excluded.status,
                created_at=excluded.created_at,
                completed_at=excluded.completed_at,
                business_count=excluded.business_count,
                listing_count=excluded.listing_count,
                coverage_json=excluded.coverage_json
            """,
            (
                run_id,
                search_id,
                status,
                created_at,
                completed_at,
                int(business_count),
                int(listing_count),
                coverage_json,
            ),
        )
        self.conn.commit()
        run = self.get_search_run(run_id)
        assert run is not None
        return run

    def get_search_run(self, run_id: str) -> SearchRunRecord | None:
        row = self.conn.execute(
            """
            SELECT run_id, search_id, status, created_at, completed_at, business_count, listing_count, coverage_json
            FROM search_runs
            WHERE run_id = ?
            """,
            (run_id,),
        ).fetchone()
        if row is None:
            return None
        return SearchRunRecord(
            run_id=str(row["run_id"]),
            search_id=str(row["search_id"]),
            status=str(row["status"]),
            created_at=str(row["created_at"]),
            completed_at=str(row["completed_at"]),
            business_count=int(row["business_count"]),
            listing_count=int(row["listing_count"]),
            coverage_json=str(row["coverage_json"]),
        )

    def get_latest_search_run_id(self, search_id: str) -> str | None:
        row = self.conn.execute(
            """
            SELECT run_id
            FROM search_runs
            WHERE search_id = ?
            ORDER BY created_at DESC, run_id DESC
            LIMIT 1
            """,
            (search_id,),
        ).fetchone()
        if row is None:
            return None
        return str(row["run_id"])

    def attach_run_businesses(self, run_id: str, business_ids: Iterable[int]) -> None:
        rows = {(run_id, int(business_id)) for business_id in business_ids}
        if not rows:
            return
        self.conn.executemany(
            """
            INSERT OR IGNORE INTO search_run_businesses (run_id, business_id)
            VALUES (?, ?)
            """,
            list(rows),
        )
        self.conn.commit()

    def attach_run_listings(self, run_id: str, listing_ids: Iterable[str]) -> None:
        rows = {(run_id, str(listing_id)) for listing_id in listing_ids if str(listing_id).strip()}
        if not rows:
            return
        self.conn.executemany(
            """
            INSERT OR IGNORE INTO search_run_listings (run_id, listing_id)
            VALUES (?, ?)
            """,
            list(rows),
        )
        self.conn.commit()

    def find_business_id(self, business: Business) -> int | None:
        row = self.conn.execute(
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

    def listing_exists(self, listing_id: str) -> bool:
        row = self.conn.execute(
            "SELECT 1 FROM listings WHERE id = ? LIMIT 1", (listing_id,)
        ).fetchone()
        return row is not None

    def list_leads(
        self,
        *,
        search_id: str,
        run_id: str | None = None,
        saved_only: bool = False,
        limit: int = 200,
    ) -> list[LeadRecord]:
        if limit < 1:
            raise ValueError("limit must be >= 1")

        selected_run_id = run_id or self.get_latest_search_run_id(search_id)
        if selected_run_id is None:
            return []

        business_rows = self.conn.execute(
            """
            SELECT
                ('business:' || b.id) AS lead_id,
                'business' AS lead_type,
                b.source AS source,
                CAST(b.id AS TEXT) AS source_record_id,
                b.name AS name,
                COALESCE(b.category, '') AS industry,
                COALESCE(b.location, '') AS location,
                COALESCE(b.state, '') AS state,
                COALESCE(b.phone, '') AS phone,
                COALESCE(b.website, '') AS website,
                '' AS url,
                COALESCE(l.summary, '') AS summary,
                COALESCE(l.note, '') AS note,
                ? AS search_id,
                COALESCE(l.saved_at, '') AS saved_at
            FROM search_run_businesses srb
            JOIN businesses b ON b.id = srb.business_id
            LEFT JOIN leads l ON l.lead_id = ('business:' || b.id)
            WHERE srb.run_id = ?
            ORDER BY b.name COLLATE NOCASE, b.id
            """,
            (search_id, selected_run_id),
        ).fetchall()

        listing_rows = self.conn.execute(
            """
            SELECT
                ('listing:' || ls.id) AS lead_id,
                'listing' AS lead_type,
                ls.source AS source,
                COALESCE(ls.source_id, '') AS source_record_id,
                ls.name AS name,
                COALESCE(ls.industry, '') AS industry,
                COALESCE(ls.location, '') AS location,
                COALESCE(ls.state, '') AS state,
                '' AS phone,
                '' AS website,
                COALESCE(ls.url, '') AS url,
                COALESCE(l.summary, '') AS summary,
                COALESCE(l.note, '') AS note,
                ? AS search_id,
                COALESCE(l.saved_at, '') AS saved_at
            FROM search_run_listings srl
            JOIN listings ls ON ls.id = srl.listing_id
            LEFT JOIN leads l ON l.lead_id = ('listing:' || ls.id)
            WHERE srl.run_id = ?
            ORDER BY ls.name COLLATE NOCASE, ls.id
            """,
            (search_id, selected_run_id),
        ).fetchall()

        combined = [self._row_to_lead(row) for row in business_rows] + [
            self._row_to_lead(row) for row in listing_rows
        ]
        combined.sort(key=lambda item: (item.name.lower(), item.lead_type, item.lead_id))
        if saved_only:
            combined = [item for item in combined if item.is_saved]
        return combined[:limit]

    def save_lead(
        self,
        *,
        lead_id: str,
        search_id: str,
        note: str = "",
        summary: str = "",
    ) -> LeadRecord:
        candidate = self._load_lead_candidate(lead_id=lead_id, search_id=search_id)
        existing = self.get_saved_lead(lead_id)
        final_note = note.strip() or (existing.note if existing is not None else candidate.note)
        final_summary = summary.strip() or (
            existing.summary if existing is not None else candidate.summary
        )
        now = _utc_now_iso()

        lead_type, suffix = _parse_lead_id(lead_id)
        business_id = int(suffix) if lead_type == "business" else None
        listing_id = suffix if lead_type == "listing" else None

        self.conn.execute(
            """
            INSERT INTO leads (
                lead_id, lead_type, source, source_record_id, business_id, listing_id, search_id, name,
                industry, location, state, phone, website, url, summary, note, saved_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(lead_id) DO UPDATE SET
                lead_type=excluded.lead_type,
                source=excluded.source,
                source_record_id=excluded.source_record_id,
                business_id=excluded.business_id,
                listing_id=excluded.listing_id,
                search_id=excluded.search_id,
                name=excluded.name,
                industry=excluded.industry,
                location=excluded.location,
                state=excluded.state,
                phone=excluded.phone,
                website=excluded.website,
                url=excluded.url,
                summary=excluded.summary,
                note=excluded.note,
                saved_at=excluded.saved_at,
                updated_at=excluded.updated_at
            """,
            (
                candidate.lead_id,
                candidate.lead_type,
                candidate.source,
                candidate.source_record_id,
                business_id,
                listing_id,
                search_id,
                candidate.name,
                candidate.industry,
                candidate.location,
                candidate.state,
                candidate.phone,
                candidate.website,
                candidate.url,
                final_summary,
                final_note,
                now,
                now,
            ),
        )
        self.conn.commit()
        saved = self.get_saved_lead(lead_id)
        assert saved is not None
        return saved

    def remove_lead(self, lead_id: str) -> bool:
        deleted = self.conn.execute("DELETE FROM leads WHERE lead_id = ?", (lead_id,)).rowcount
        self.conn.commit()
        return deleted > 0

    def get_saved_lead(self, lead_id: str) -> LeadRecord | None:
        row = self.conn.execute(
            """
            SELECT lead_id, lead_type, source, source_record_id, name, industry, location, state, phone,
                   website, url, summary, note, search_id, saved_at
            FROM leads
            WHERE lead_id = ?
            """,
            (lead_id,),
        ).fetchone()
        if row is None:
            return None
        return self._saved_row_to_lead(row)

    def list_saved_leads(
        self, *, search_id: str | None = None, limit: int = 200
    ) -> list[LeadRecord]:
        if limit < 1:
            raise ValueError("limit must be >= 1")

        params: list[object] = []
        where_sql = ""
        if search_id is not None:
            where_sql = "WHERE search_id = ?"
            params.append(search_id)

        rows = self.conn.execute(
            f"""
            SELECT lead_id, lead_type, source, source_record_id, name, industry, location, state, phone,
                   website, url, summary, note, search_id, saved_at
            FROM leads
            {where_sql}
            ORDER BY name COLLATE NOCASE, lead_id
            LIMIT ?
            """,
            tuple(params + [limit]),
        ).fetchall()
        return [self._saved_row_to_lead(row) for row in rows]

    def _load_lead_candidate(self, *, lead_id: str, search_id: str) -> LeadRecord:
        lead_type, suffix = _parse_lead_id(lead_id)
        if lead_type == "business":
            row = self.conn.execute(
                """
                SELECT id, source, name, category, location, state, phone, website
                FROM businesses
                WHERE id = ?
                """,
                (int(suffix),),
            ).fetchone()
            if row is None:
                raise KeyError(f"Unknown business lead id '{lead_id}'")
            return LeadRecord(
                lead_id=lead_id,
                lead_type="business",
                source=str(row["source"]),
                source_record_id=str(row["id"]),
                name=str(row["name"]),
                industry=str(row["category"] or ""),
                location=str(row["location"] or ""),
                state=str(row["state"] or ""),
                phone=str(row["phone"] or ""),
                website=str(row["website"] or ""),
                url="",
                summary="",
                note="",
                search_id=search_id,
                saved_at="",
                is_saved=False,
            )

        row = self.conn.execute(
            """
            SELECT id, source, source_id, name, industry, location, state, url
            FROM listings
            WHERE id = ?
            """,
            (suffix,),
        ).fetchone()
        if row is None:
            raise KeyError(f"Unknown listing lead id '{lead_id}'")
        return LeadRecord(
            lead_id=lead_id,
            lead_type="listing",
            source=str(row["source"]),
            source_record_id=str(row["source_id"] or ""),
            name=str(row["name"]),
            industry=str(row["industry"] or ""),
            location=str(row["location"] or ""),
            state=str(row["state"] or ""),
            phone="",
            website="",
            url=str(row["url"] or ""),
            summary="",
            note="",
            search_id=search_id,
            saved_at="",
            is_saved=False,
        )

    @staticmethod
    def _row_to_lead(row: sqlite3.Row) -> LeadRecord:
        saved_at = str(row["saved_at"] or "")
        return LeadRecord(
            lead_id=str(row["lead_id"]),
            lead_type=str(row["lead_type"]),
            source=str(row["source"]),
            source_record_id=str(row["source_record_id"]),
            name=str(row["name"]),
            industry=str(row["industry"] or ""),
            location=str(row["location"] or ""),
            state=str(row["state"] or ""),
            phone=str(row["phone"] or ""),
            website=str(row["website"] or ""),
            url=str(row["url"] or ""),
            summary=str(row["summary"] or ""),
            note=str(row["note"] or ""),
            search_id=str(row["search_id"]),
            saved_at=saved_at,
            is_saved=bool(saved_at),
        )

    @staticmethod
    def _saved_row_to_lead(row: sqlite3.Row) -> LeadRecord:
        return LeadRecord(
            lead_id=str(row["lead_id"]),
            lead_type=str(row["lead_type"]),
            source=str(row["source"]),
            source_record_id=str(row["source_record_id"]),
            name=str(row["name"]),
            industry=str(row["industry"] or ""),
            location=str(row["location"] or ""),
            state=str(row["state"] or ""),
            phone=str(row["phone"] or ""),
            website=str(row["website"] or ""),
            url=str(row["url"] or ""),
            summary=str(row["summary"] or ""),
            note=str(row["note"] or ""),
            search_id=str(row["search_id"]),
            saved_at=str(row["saved_at"]),
            is_saved=True,
        )
