import json

from scout.pipeline.data_store.sqlite import SQLiteDataStore
from scout.pipeline.models.business import Business
from scout.pipeline.models.query import Query


def _query(run_id: str, created_at: str) -> Query:
    return Query(
        industry="HVAC",
        location="Austin, TX",
        run_id=run_id,
        created_at=created_at,
    )


def _business(name: str, *, address: str, phone: str, rating: float) -> Business:
    return Business(
        source="google_maps",
        name=name,
        address=address,
        phone=phone,
        category="HVAC Contractor",
        location="Austin, TX",
        state="TX",
        rating=rating,
        reviews=100,
    )


def test_record_business_history_tracks_seen_bounds_and_run_diffs(tmp_path):
    store = SQLiteDataStore(
        db_path=tmp_path / "canonical.db",
        raw_root=tmp_path / "raw",
    )

    first_run = _query("run-001", "2026-03-01T00:00:00+00:00")
    first_businesses = [
        _business(
            "Acme Mechanical",
            address="100 Main St, Austin, TX",
            phone="(512) 111-0001",
            rating=4.2,
        ),
        _business(
            "Bravo Cooling",
            address="200 Main St, Austin, TX",
            phone="(512) 111-0002",
            rating=4.1,
        ),
    ]
    store.upsert_businesses(first_businesses)
    store.record_business_history(first_run, first_businesses)

    second_run = _query("run-002", "2026-03-02T00:00:00+00:00")
    second_businesses = [
        _business(
            "Acme Mechanical",
            address="100 Main St, Austin, TX",
            phone="(512) 999-0001",
            rating=4.7,
        ),
        _business(
            "Charlie HVAC",
            address="300 Main St, Austin, TX",
            phone="(512) 111-0003",
            rating=4.0,
        ),
    ]
    store.upsert_businesses(second_businesses)
    store.record_business_history(second_run, second_businesses)

    rows = store.conn.execute("""
        SELECT name, first_seen_run_id, first_seen_at, last_seen_run_id, last_seen_at
        FROM businesses
        ORDER BY name
        """).fetchall()
    by_name = {row["name"]: row for row in rows}

    assert by_name["Acme Mechanical"]["first_seen_run_id"] == "run-001"
    assert by_name["Acme Mechanical"]["first_seen_at"] == "2026-03-01T00:00:00+00:00"
    assert by_name["Acme Mechanical"]["last_seen_run_id"] == "run-002"
    assert by_name["Acme Mechanical"]["last_seen_at"] == "2026-03-02T00:00:00+00:00"

    assert by_name["Bravo Cooling"]["first_seen_run_id"] == "run-001"
    assert by_name["Bravo Cooling"]["last_seen_run_id"] == "run-001"

    assert by_name["Charlie HVAC"]["first_seen_run_id"] == "run-002"
    assert by_name["Charlie HVAC"]["last_seen_run_id"] == "run-002"

    first_snapshot = store.conn.execute(
        "SELECT business_name FROM business_search_snapshots WHERE run_id = ? ORDER BY business_name",
        ("run-001",),
    ).fetchall()
    assert [row["business_name"] for row in first_snapshot] == [
        "Acme Mechanical",
        "Bravo Cooling",
    ]

    second_snapshot = store.conn.execute(
        "SELECT business_name FROM business_search_snapshots WHERE run_id = ? ORDER BY business_name",
        ("run-002",),
    ).fetchall()
    assert [row["business_name"] for row in second_snapshot] == [
        "Acme Mechanical",
        "Charlie HVAC",
    ]

    diff_rows = store.conn.execute(
        """
        SELECT business_name, change_type, changed_fields
        FROM search_business_diffs
        WHERE run_id = ?
        ORDER BY business_name
        """,
        ("run-002",),
    ).fetchall()
    assert [(row["business_name"], row["change_type"]) for row in diff_rows] == [
        ("Acme Mechanical", "changed"),
        ("Bravo Cooling", "removed"),
        ("Charlie HVAC", "new"),
    ]

    changed_fields = json.loads(diff_rows[0]["changed_fields"])
    assert "phone" in changed_fields
    assert "rating" in changed_fields
