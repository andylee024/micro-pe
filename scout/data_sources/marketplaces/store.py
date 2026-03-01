"""SQLite-backed listing store for marketplace data."""

import sqlite3
from datetime import datetime, timedelta
from typing import List, Optional

from scout.domain.listing import Listing


class ListingStore:
    """Persistent store for business-for-sale listings backed by SQLite."""

    def __init__(self, db_path: str = "outputs/listings.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self) -> None:
        cur = self.conn.cursor()
        cur.executescript("""
            CREATE TABLE IF NOT EXISTS listings (
                id TEXT PRIMARY KEY,
                source TEXT NOT NULL,
                source_id TEXT NOT NULL,
                name TEXT NOT NULL,
                industry TEXT,
                location TEXT,
                state TEXT,
                asking_price REAL,
                annual_revenue REAL,
                cash_flow REAL,
                asking_multiple REAL,
                days_on_market INTEGER,
                broker TEXT,
                url TEXT,
                description TEXT,
                listed_at TEXT,
                fetched_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_industry_state ON listings(industry, state);
            CREATE INDEX IF NOT EXISTS idx_asking_price ON listings(asking_price);
            CREATE INDEX IF NOT EXISTS idx_cash_flow ON listings(cash_flow);
            CREATE INDEX IF NOT EXISTS idx_fetched_at ON listings(fetched_at);

            CREATE TABLE IF NOT EXISTS scrape_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT NOT NULL,
                industry TEXT NOT NULL,
                location TEXT NOT NULL,
                scraped_at TEXT NOT NULL,
                listing_count INTEGER,
                status TEXT,
                precision_pct REAL,
                error_msg TEXT
            );
        """)
        self.conn.commit()

    def upsert(self, listings: List[Listing]) -> int:
        """Insert or replace listings. Returns count of rows written."""
        if not listings:
            return 0
        cur = self.conn.cursor()
        count = 0
        for listing in listings:
            cur.execute(
                """INSERT OR REPLACE INTO listings
                   (id, source, source_id, name, industry, location, state,
                    asking_price, annual_revenue, cash_flow, asking_multiple,
                    days_on_market, broker, url, description, listed_at, fetched_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    listing.id,
                    listing.source,
                    listing.source_id,
                    listing.name,
                    listing.industry,
                    listing.location,
                    listing.state,
                    listing.asking_price,
                    listing.annual_revenue,
                    listing.cash_flow,
                    listing.asking_multiple,
                    listing.days_on_market,
                    listing.broker,
                    listing.url,
                    listing.description,
                    listing.listed_at,
                    listing.fetched_at,
                ),
            )
            count += 1
        self.conn.commit()
        return count

    def search(
        self,
        industry: str = "",
        location: str = "",
        state: str = "",
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        min_revenue: Optional[float] = None,
        min_cash_flow: Optional[float] = None,
        max_multiple: Optional[float] = None,
        source: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Listing]:
        """Search listings with optional filters."""
        clauses: list = []
        params: list = []

        if industry:
            clauses.append("LOWER(industry) LIKE LOWER('%' || ? || '%')")
            params.append(industry)

        if state:
            clauses.append("state = ?")
            params.append(state)
        elif location:
            clauses.append("LOWER(location) LIKE LOWER('%' || ? || '%')")
            params.append(location)

        if min_price is not None:
            clauses.append("asking_price IS NOT NULL AND asking_price >= ?")
            params.append(min_price)

        if max_price is not None:
            clauses.append("asking_price IS NOT NULL AND asking_price <= ?")
            params.append(max_price)

        if min_revenue is not None:
            clauses.append("annual_revenue IS NOT NULL AND annual_revenue >= ?")
            params.append(min_revenue)

        if min_cash_flow is not None:
            clauses.append("cash_flow IS NOT NULL AND cash_flow >= ?")
            params.append(min_cash_flow)

        if max_multiple is not None:
            clauses.append("asking_multiple IS NOT NULL AND asking_multiple <= ?")
            params.append(max_multiple)

        if source is not None:
            clauses.append("source = ?")
            params.append(source)

        where = " AND ".join(clauses) if clauses else "1=1"
        sql = f"SELECT * FROM listings WHERE {where} LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        cur = self.conn.execute(sql, params)
        rows = cur.fetchall()
        return [Listing.from_dict(dict(row)) for row in rows]

    def log_scrape(
        self,
        source: str,
        industry: str,
        location: str,
        count: int,
        status: str,
        precision_pct: Optional[float] = None,
        error_msg: Optional[str] = None,
    ) -> None:
        """Record a scrape event."""
        self.conn.execute(
            """INSERT INTO scrape_log (source, industry, location, scraped_at, listing_count, status, precision_pct, error_msg)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (source, industry, location, datetime.now().isoformat(), count, status, precision_pct, error_msg),
        )
        self.conn.commit()

    def last_scraped(self, source: str, industry: str, location: str) -> Optional[str]:
        """Return ISO timestamp of most recent successful scrape, or None."""
        cur = self.conn.execute(
            """SELECT scraped_at FROM scrape_log
               WHERE source = ? AND industry = ? AND location = ? AND status = 'success'
               ORDER BY scraped_at DESC LIMIT 1""",
            (source, industry, location),
        )
        row = cur.fetchone()
        return row["scraped_at"] if row else None

    def is_stale(self, source: str, industry: str, location: str, max_age_hours: int = 24) -> bool:
        """Return True if data was never scraped or is older than max_age_hours."""
        ts = self.last_scraped(source, industry, location)
        if ts is None:
            return True
        last = datetime.fromisoformat(ts)
        return (datetime.now() - last) > timedelta(hours=max_age_hours)

    def count(self, industry: str = "", location: str = "") -> int:
        """Count matching listings."""
        clauses: list = []
        params: list = []
        if industry:
            clauses.append("LOWER(industry) LIKE LOWER('%' || ? || '%')")
            params.append(industry)
        if location:
            clauses.append("LOWER(location) LIKE LOWER('%' || ? || '%')")
            params.append(location)
        where = " AND ".join(clauses) if clauses else "1=1"
        cur = self.conn.execute(f"SELECT COUNT(*) as cnt FROM listings WHERE {where}", params)
        return cur.fetchone()["cnt"]
