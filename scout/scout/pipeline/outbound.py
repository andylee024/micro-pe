"""Outbound lead state management and SQLite-backed repository."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from scout.pipeline.models.business import Business
from scout.pipeline.models.lead import DEFAULT_NEXT_ACTION, DEFAULT_OUTBOUND_STATUS, Lead

OUTBOUND_STATUSES = (
    "new",
    "queued",
    "contacted",
    "waiting_reply",
    "responded",
    "archived",
)

NEXT_ACTIONS = (
    "research",
    "send_intro",
    "await_reply",
    "follow_up",
    "schedule_call",
    "close_out",
)

DEFAULT_NEXT_ACTION_BY_STATUS = {
    "new": "research",
    "queued": "send_intro",
    "contacted": "await_reply",
    "waiting_reply": "follow_up",
    "responded": "schedule_call",
    "archived": "close_out",
}

ALLOWED_NEXT_ACTIONS_BY_STATUS = {
    "new": {"research"},
    "queued": {"send_intro"},
    "contacted": {"await_reply"},
    "waiting_reply": {"await_reply", "follow_up"},
    "responded": {"schedule_call"},
    "archived": {"close_out"},
}

ALLOWED_STATUS_TRANSITIONS = {
    "new": {"queued", "archived"},
    "queued": {"contacted", "archived"},
    "contacted": {"waiting_reply", "responded", "archived"},
    "waiting_reply": {"contacted", "responded", "archived"},
    "responded": {"archived"},
    "archived": set(),
}


def canonical_outbound_status(value: str) -> str:
    normalized = _normalize_key(value)
    if normalized not in OUTBOUND_STATUSES:
        raise ValueError(
            f"Invalid outbound status '{value}'. Expected one of: {', '.join(OUTBOUND_STATUSES)}."
        )
    return normalized


def canonical_next_action(value: str) -> str:
    normalized = _normalize_key(value)
    if normalized not in NEXT_ACTIONS:
        raise ValueError(
            f"Invalid next action '{value}'. Expected one of: {', '.join(NEXT_ACTIONS)}."
        )
    return normalized


def resolve_next_action(status: str, next_action: str | None) -> str:
    if next_action is None:
        return DEFAULT_NEXT_ACTION_BY_STATUS[status]
    action = canonical_next_action(next_action)
    allowed_actions = ALLOWED_NEXT_ACTIONS_BY_STATUS[status]
    if action not in allowed_actions:
        raise ValueError(
            f"Invalid next action '{action}' for status '{status}'. "
            f"Allowed: {', '.join(sorted(allowed_actions))}."
        )
    return action


def validate_transition(current_status: str, next_status: str) -> None:
    if current_status == next_status:
        return
    allowed = ALLOWED_STATUS_TRANSITIONS[current_status]
    if next_status not in allowed:
        raise ValueError(
            f"Invalid outbound transition '{current_status}' -> '{next_status}'. "
            f"Allowed: {', '.join(sorted(allowed)) or '<none>'}."
        )


def format_queue_strip(queue: dict[str, int], *, location: str | None = None) -> str:
    location_suffix = f" location={location}" if location else ""
    return f"outbound_queue:{location_suffix} total={queue['total']} " + " ".join(
        f"{status}={queue[status]}" for status in OUTBOUND_STATUSES
    )


class LeadRepository:
    """SQLite-backed persistence for outbound lead state."""

    def __init__(self, db_path: str | Path = "outputs/pipeline/canonical.db") -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self._create_table()

    def _create_table(self) -> None:
        cursor = self.conn.cursor()
        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS lead_states (
                lead_id TEXT PRIMARY KEY,
                source TEXT NOT NULL,
                name TEXT NOT NULL,
                location TEXT,
                phone TEXT,
                website TEXT,
                outbound_status TEXT NOT NULL,
                next_action TEXT NOT NULL,
                last_contacted_at TEXT,
                updated_at TEXT NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_lead_states_status ON lead_states(outbound_status);
            CREATE INDEX IF NOT EXISTS idx_lead_states_location ON lead_states(location);
            """)
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()

    def sync_businesses(self, businesses: list[Business]) -> list[Lead]:
        if not businesses:
            return []

        now = _utc_now_iso()
        unique_leads: dict[str, Lead] = {}
        for business in businesses:
            if not business.name:
                continue
            lead = Lead.from_business(business)
            lead.updated_at = now
            unique_leads[lead.id] = lead

        rows = [
            (
                lead.id,
                lead.source,
                lead.name,
                lead.location,
                lead.phone,
                lead.website,
                DEFAULT_OUTBOUND_STATUS,
                DEFAULT_NEXT_ACTION,
                None,
                lead.updated_at,
            )
            for lead in unique_leads.values()
        ]
        if not rows:
            return []

        self.conn.executemany(
            """
            INSERT INTO lead_states (
                lead_id, source, name, location, phone, website,
                outbound_status, next_action, last_contacted_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(lead_id) DO UPDATE SET
                source=excluded.source,
                name=excluded.name,
                location=excluded.location,
                phone=excluded.phone,
                website=excluded.website,
                updated_at=excluded.updated_at
            """,
            rows,
        )
        self.conn.commit()

        return self.get_leads(list(unique_leads.keys()))

    def get_lead(self, lead_id: str) -> Lead | None:
        row = self.conn.execute(
            """
            SELECT
                lead_id, source, name, location, phone, website,
                outbound_status, next_action, last_contacted_at, updated_at
            FROM lead_states
            WHERE lead_id = ?
            """,
            (lead_id,),
        ).fetchone()
        if row is None:
            return None
        return _row_to_lead(row)

    def get_leads(self, lead_ids: list[str]) -> list[Lead]:
        if not lead_ids:
            return []
        placeholders = ", ".join("?" for _ in lead_ids)
        rows = self.conn.execute(
            f"""
            SELECT
                lead_id, source, name, location, phone, website,
                outbound_status, next_action, last_contacted_at, updated_at
            FROM lead_states
            WHERE lead_id IN ({placeholders})
            ORDER BY name ASC
            """,
            tuple(lead_ids),
        ).fetchall()
        return [_row_to_lead(row) for row in rows]

    def list_leads(
        self, *, status: str | None = None, location: str | None = None, limit: int = 25
    ) -> list[Lead]:
        clauses: list[str] = []
        params: list[object] = []
        if status:
            clauses.append("outbound_status = ?")
            params.append(canonical_outbound_status(status))
        if location:
            clauses.append("LOWER(location) = LOWER(?)")
            params.append(location.strip())

        where_sql = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        rows = self.conn.execute(
            f"""
            SELECT
                lead_id, source, name, location, phone, website,
                outbound_status, next_action, last_contacted_at, updated_at
            FROM lead_states
            {where_sql}
            ORDER BY name ASC
            LIMIT ?
            """,
            tuple(params + [limit]),
        ).fetchall()
        return [_row_to_lead(row) for row in rows]

    def transition_lead(
        self,
        *,
        lead_id: str,
        outbound_status: str,
        next_action: str | None = None,
    ) -> Lead:
        current = self.get_lead(lead_id)
        if current is None:
            raise KeyError(f"Lead '{lead_id}' not found.")

        current_status = canonical_outbound_status(current.outbound_status)
        next_status = canonical_outbound_status(outbound_status)
        validate_transition(current_status, next_status)
        resolved_action = resolve_next_action(next_status, next_action)
        now = _utc_now_iso()
        last_contacted = current.last_contacted_at
        if next_status == "contacted":
            last_contacted = now

        self.conn.execute(
            """
            UPDATE lead_states
            SET outbound_status = ?, next_action = ?, last_contacted_at = ?, updated_at = ?
            WHERE lead_id = ?
            """,
            (next_status, resolved_action, last_contacted, now, lead_id),
        )
        self.conn.commit()
        updated = self.get_lead(lead_id)
        if updated is None:
            raise KeyError(f"Lead '{lead_id}' not found after update.")
        return updated

    def queue_strip(self, *, location: str | None = None) -> dict[str, int]:
        params: tuple[object, ...] = ()
        where_sql = ""
        if location:
            where_sql = "WHERE LOWER(location) = LOWER(?)"
            params = (location.strip(),)

        rows = self.conn.execute(
            f"""
            SELECT outbound_status, COUNT(*) AS count
            FROM lead_states
            {where_sql}
            GROUP BY outbound_status
            """,
            params,
        ).fetchall()

        queue = {status: 0 for status in OUTBOUND_STATUSES}
        for row in rows:
            status = canonical_outbound_status(str(row["outbound_status"]))
            queue[status] = int(row["count"])
        queue["total"] = sum(queue.values())
        return queue


def _row_to_lead(row: sqlite3.Row) -> Lead:
    return Lead(
        id=str(row["lead_id"]),
        source=str(row["source"]),
        name=str(row["name"]),
        location=str(row["location"] or ""),
        phone=str(row["phone"] or ""),
        website=str(row["website"] or ""),
        outbound_status=canonical_outbound_status(str(row["outbound_status"])),
        next_action=canonical_next_action(str(row["next_action"])),
        last_contacted_at=str(row["last_contacted_at"]) if row["last_contacted_at"] else None,
        updated_at=str(row["updated_at"]),
    )


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalize_key(value: str) -> str:
    return "_".join(value.strip().lower().replace("-", "_").split())
