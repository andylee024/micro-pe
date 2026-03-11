"""SQLite DataStore implementation."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from scout.pipeline.data_store.base import DataStore
from scout.pipeline.data_store.raw_snapshot import persist_snapshot
from scout.pipeline.models.business import Business
from scout.pipeline.models.lead import Lead
from scout.pipeline.models.listing import Listing


def _normalize_token(value: str) -> str:
    return " ".join(value.strip().lower().split())


def build_business_lead_id(source: str, name: str, address: str) -> str:
    """Build a deterministic lead id for one business row."""
    normalized_source = _normalize_token(source)
    normalized_name = _normalize_token(name)
    normalized_address = _normalize_token(address)
    return f"business:{normalized_source}:{normalized_name}:{normalized_address}"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


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

            CREATE TABLE IF NOT EXISTS lead_states (
                lead_id TEXT PRIMARY KEY,
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
                is_saved INTEGER NOT NULL DEFAULT 0,
                saved_at TEXT,
                updated_at TEXT NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_lead_states_saved ON lead_states(is_saved);
            CREATE INDEX IF NOT EXISTS idx_lead_states_location ON lead_states(location);
            CREATE INDEX IF NOT EXISTS idx_lead_states_category ON lead_states(category);
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
        self.sync_business_leads(businesses)
        return len(rows)

    def sync_business_leads(self, businesses: list[Business]) -> int:
        """Ensure canonical lead states exist for the provided businesses."""
        if not businesses:
            return 0

        now = _utc_now_iso()
        unique_rows: dict[str, tuple[object, ...]] = {}
        for business in businesses:
            if not business.name:
                continue
            lead_id = build_business_lead_id(
                source=business.source,
                name=business.name,
                address=business.address,
            )
            unique_rows[lead_id] = (
                lead_id,
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
                now,
            )

        if not unique_rows:
            return 0

        self.conn.executemany(
            """
            INSERT INTO lead_states (
                lead_id, source, name, address, phone, website, category, location,
                state, rating, reviews, is_saved, saved_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, NULL, ?)
            ON CONFLICT(lead_id) DO UPDATE SET
                source=excluded.source,
                name=excluded.name,
                address=excluded.address,
                phone=excluded.phone,
                website=excluded.website,
                category=excluded.category,
                location=excluded.location,
                state=excluded.state,
                rating=excluded.rating,
                reviews=excluded.reviews,
                updated_at=excluded.updated_at
            """,
            list(unique_rows.values()),
        )
        self.conn.commit()
        return len(unique_rows)

    def list_leads(
        self,
        *,
        industry: str = "",
        location: str = "",
        state: str = "",
        saved_only: bool = False,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Lead]:
        """Return filtered leads ordered for dense operator scanning."""
        if limit < 1:
            raise ValueError("limit must be >= 1")
        if offset < 0:
            raise ValueError("offset must be >= 0")

        clauses = ["1=1"]
        params: list[object] = []
        if industry.strip():
            clauses.append("LOWER(category) LIKE LOWER(?)")
            params.append(f"%{industry.strip()}%")
        if location.strip():
            clauses.append("LOWER(location) LIKE LOWER(?)")
            params.append(f"%{location.strip()}%")
        if state.strip():
            clauses.append("UPPER(state) = UPPER(?)")
            params.append(state.strip())
        if saved_only:
            clauses.append("is_saved = 1")

        sql = f"""
            SELECT
                lead_id, source, name, address, phone, website, category, location, state,
                rating, reviews, is_saved, saved_at, updated_at
            FROM lead_states
            WHERE {' AND '.join(clauses)}
            ORDER BY COALESCE(reviews, 0) DESC, LOWER(name), lead_id
            LIMIT ? OFFSET ?
        """
        rows = self.conn.execute(sql, tuple(params + [limit, offset])).fetchall()
        return [_row_to_lead(row) for row in rows]

    def get_lead(self, lead_id: str) -> Lead | None:
        row = self.conn.execute(
            """
            SELECT
                lead_id, source, name, address, phone, website, category, location, state,
                rating, reviews, is_saved, saved_at, updated_at
            FROM lead_states
            WHERE lead_id = ?
            """,
            (lead_id.strip(),),
        ).fetchone()
        if row is None:
            return None
        return _row_to_lead(row)

    def set_lead_saved(self, lead_id: str, is_saved: bool) -> Lead:
        normalized_id = lead_id.strip()
        if not normalized_id:
            raise ValueError("lead_id must be non-empty")
        if self.get_lead(normalized_id) is None:
            raise KeyError(f"Lead '{normalized_id}' not found.")

        now = _utc_now_iso()
        saved_at = now if is_saved else None
        self.conn.execute(
            """
            UPDATE lead_states
            SET is_saved = ?, saved_at = ?, updated_at = ?
            WHERE lead_id = ?
            """,
            (1 if is_saved else 0, saved_at, now, normalized_id),
        )
        self.conn.commit()
        lead = self.get_lead(normalized_id)
        if lead is None:
            raise KeyError(f"Lead '{normalized_id}' not found after update.")
        return lead

    def close(self) -> None:
        self.conn.close()

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


def _row_to_lead(row: sqlite3.Row) -> Lead:
    return Lead(
        lead_id=str(row["lead_id"]),
        source=str(row["source"]),
        name=str(row["name"]),
        address=str(row["address"] or ""),
        phone=str(row["phone"] or ""),
        website=str(row["website"] or ""),
        category=str(row["category"] or ""),
        location=str(row["location"] or ""),
        state=str(row["state"] or ""),
        rating=row["rating"],
        reviews=row["reviews"],
        is_saved=bool(row["is_saved"]),
        saved_at=str(row["saved_at"]) if row["saved_at"] else None,
        updated_at=str(row["updated_at"]),
    )
