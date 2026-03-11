"""Tests for app schema bootstrap and SQLite repositories."""

from __future__ import annotations

import sqlite3

from scout.app.storage.models import Lead, Search, SearchRun
from scout.app.storage.sqlite import SQLiteAppStorage, bootstrap_app_schema
from scout.pipeline.data_store.sqlite import SQLiteDataStore
from scout.pipeline.models.business import Business
from scout.pipeline.models.listing import Listing


def test_bootstrap_is_idempotent_and_preserves_pipeline_tables(tmp_path):
    db_path = tmp_path / "canonical.db"
    raw_root = tmp_path / "raw"

    data_store = SQLiteDataStore(db_path=db_path, raw_root=raw_root)
    data_store.upsert_businesses([Business(name="Acme HVAC", source="google_maps")])
    data_store.upsert_listings(
        [
            Listing(
                source="bizbuysell",
                source_id="listing-1",
                url="https://example.com/listing-1",
                name="Acme HVAC Listing",
                industry="HVAC",
                location="Austin, TX",
            )
        ]
    )
    data_store.conn.close()

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    bootstrap_app_schema(conn)
    bootstrap_app_schema(conn)

    table_names = {
        row["name"]
        for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        )
    }
    expected_tables = {
        "businesses",
        "listings",
        "searches",
        "search_runs",
        "leads",
        "workflow_runs",
        "workflow_artifacts",
        "outbound_attempts",
        "external_record_links",
        "notes",
    }
    assert expected_tables.issubset(table_names)

    business_count = conn.execute("SELECT COUNT(*) FROM businesses").fetchone()[0]
    listing_count = conn.execute("SELECT COUNT(*) FROM listings").fetchone()[0]
    assert business_count == 1
    assert listing_count == 1

    conn.close()


def test_search_and_search_run_round_trip(tmp_path):
    storage = SQLiteAppStorage(db_path=tmp_path / "app.db")

    search = Search(
        query_text="HVAC businesses in Austin, TX",
        industry="HVAC",
        location="Austin, TX",
    )
    storage.searches.create(search)

    search_run = SearchRun(
        search_id=search.id,
        pipeline_run_id="run_123",
        status="completed",
        summary="Collected canonical records",
    )
    storage.search_runs.create(search_run)

    assert storage.searches.get(search.id) == search
    assert storage.search_runs.get(search_run.id) == search_run
    assert storage.search_runs.list_for_search(search.id) == [search_run]

    storage.close()


def test_lead_round_trip(tmp_path):
    storage = SQLiteAppStorage(db_path=tmp_path / "app.db")

    search = Search(
        query_text="Plumbing businesses in Denver, CO",
        industry="Plumbing",
        location="Denver, CO",
    )
    storage.searches.create(search)

    search_run = SearchRun(
        search_id=search.id,
        pipeline_run_id="run_456",
        status="completed",
    )
    storage.search_runs.create(search_run)

    lead = Lead(
        search_id=search.id,
        search_run_id=search_run.id,
        source="google_maps",
        source_record_id="gm_001",
        name="Mile High Plumbing",
        score=0.91,
    )
    storage.leads.create(lead)

    assert storage.leads.get(lead.id) == lead
    assert storage.leads.list_for_search(search.id) == [lead]

    storage.close()

