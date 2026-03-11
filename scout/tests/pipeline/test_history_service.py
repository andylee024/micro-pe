from pathlib import Path

from scout.pipeline.data_store.sqlite import SQLiteDataStore
from scout.pipeline.history import HistoryService
from scout.pipeline.models.business import Business
from scout.pipeline.models.listing import Listing
from scout.pipeline.models.query import Query


def _listing(source_id: str, name: str) -> Listing:
    return Listing(
        source="bizbuysell",
        source_id=source_id,
        url=f"https://example.com/{source_id}",
        name=name,
        industry="hvac",
        location="Austin, TX",
    )


def test_history_service_reads_canonical_run_diff_state(tmp_path: Path):
    db_path = tmp_path / "canonical.db"
    store = SQLiteDataStore(db_path=db_path, raw_root=tmp_path / "raw")
    try:
        run1 = Query(
            industry="hvac",
            location="Austin, TX",
            run_id="run-one",
            created_at="2026-03-11T10:00:00+00:00",
        )
        run2 = Query(
            industry="hvac",
            location="Austin, TX",
            run_id="run-two",
            created_at="2026-03-11T10:05:00+00:00",
        )
        run1_summary = store.record_run(
            query=run1,
            businesses=[
                Business(name="Acme HVAC", source="google_maps", location="Austin, TX"),
                Business(name="Bravo HVAC", source="google_maps", location="Austin, TX"),
            ],
            listings=[_listing("1", "Acme Listing")],
        )
        run2_summary = store.record_run(
            query=run2,
            businesses=[
                Business(name="Acme HVAC", source="google_maps", location="Austin, TX"),
                Business(name="City HVAC", source="google_maps", location="Austin, TX"),
            ],
            listings=[_listing("1", "Acme Listing"), _listing("2", "City Listing")],
        )
    finally:
        store.close()

    assert run1_summary.previous_run_id is None
    assert run1_summary.added_businesses == 0
    assert run2_summary.previous_run_id == "run-one"
    assert run2_summary.added_businesses == 1
    assert run2_summary.removed_businesses == 1
    assert run2_summary.added_listings == 1
    assert run2_summary.removed_listings == 0

    service = HistoryService(db_path=db_path)
    try:
        history = service.list_runs(limit=5)
        assert [entry.run_id for entry in history] == ["run-two", "run-one"]
        assert history[0].added_businesses == 1
        assert history[0].removed_businesses == 1
        assert history[0].added_listings == 1
        assert history[0].removed_listings == 0
        assert history[0].previous_run_id == "run-one"

        diff = service.get_diff(run_id="run-two")
    finally:
        service.close()

    assert diff.previous_run_id == "run-one"
    added_businesses = [item.name for item in diff.items if item.item_type == "business" and item.change_type == "added"]
    removed_businesses = [item.name for item in diff.items if item.item_type == "business" and item.change_type == "removed"]
    added_listings = [item.name for item in diff.items if item.item_type == "listing" and item.change_type == "added"]
    assert added_businesses == ["City HVAC"]
    assert removed_businesses == ["Bravo HVAC"]
    assert added_listings == ["City Listing"]
