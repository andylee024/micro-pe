from pathlib import Path

from scout.pipeline.data_store.sqlite import SQLiteDataStore, build_business_lead_id
from scout.pipeline.lead_workflow import LeadWorkflowService
from scout.pipeline.models.business import Business
from scout.pipeline.models.listing import Listing


def _seed_leads(db_path: Path, raw_root: Path) -> str:
    store = SQLiteDataStore(db_path=db_path, raw_root=raw_root)
    try:
        store.upsert_businesses(
            [
                Business(
                    name="Alpha Heating & Air",
                    source="google_maps",
                    category="HVAC",
                    location="Austin, TX",
                    state="TX",
                    address="101 Main St",
                    phone="555-0101",
                    website="https://alpha.example.com",
                    rating=4.7,
                    reviews=127,
                )
            ]
        )
        store.upsert_listings(
            [
                Listing(
                    source="bizbuysell",
                    source_id="hvac-1",
                    url="https://example.com/hvac-1",
                    name="Alpha HVAC Listing",
                    industry="HVAC",
                    location="Austin, TX",
                    state="TX",
                    asking_price=950000,
                    annual_revenue=1200000,
                    cash_flow=260000,
                )
            ]
        )
    finally:
        store.close()

    return build_business_lead_id("google_maps", "Alpha Heating & Air", "101 Main St")


def test_research_and_enrich_handlers_produce_stored_artifacts(tmp_path: Path):
    db_path = tmp_path / "canonical.db"
    raw_root = tmp_path / "raw"
    lead_id = _seed_leads(db_path, raw_root)

    service = LeadWorkflowService(db_path=str(db_path))
    try:
        service.trigger(lead_id=lead_id, action="research")
        service.trigger(lead_id=lead_id, action="enrich")

        results = service.run_batch(max_jobs=10)
        assert len(results) == 2
        assert all(result.status == "completed" for result in results)

        artifacts = service.list_artifacts(lead_id=lead_id, limit=10)
        by_action = {artifact["action"]: artifact for artifact in artifacts}

        assert "research" in by_action
        assert "enrich" in by_action
        assert "Alpha Heating & Air" in by_action["research"]["summary"]
        assert by_action["enrich"]["content"]["has_phone"] is True
        assert by_action["enrich"]["content"]["domain"] == "alpha.example.com"

        runs = service.list_runs(lead_id=lead_id, limit=10)
        status_by_action = {row["action"]: row["status"] for row in runs}
        assert status_by_action["research"] == "completed"
        assert status_by_action["enrich"] == "completed"
    finally:
        service.close()


def test_prepare_call_and_draft_email_are_triggerable_and_record_state(tmp_path: Path):
    db_path = tmp_path / "canonical.db"
    raw_root = tmp_path / "raw"
    lead_id = _seed_leads(db_path, raw_root)

    service = LeadWorkflowService(db_path=str(db_path))
    try:
        service.trigger(lead_id=lead_id, action="prepare-call")
        service.trigger(lead_id=lead_id, action="draft-email")

        processed = service.run_until_empty(max_jobs=10)
        assert processed == 2

        runs = service.list_runs(lead_id=lead_id, limit=10)
        status_by_action = {row["action"]: row["status"] for row in runs}
        assert status_by_action["prepare-call"] == "completed"
        assert status_by_action["draft-email"] == "completed"

        artifacts = service.list_artifacts(lead_id=lead_id, limit=10)
        by_action = {artifact["action"]: artifact for artifact in artifacts}
        assert "prepare-call" in by_action
        assert "draft-email" in by_action
        assert "subject" in by_action["draft-email"]["content"]
        assert "body" in by_action["draft-email"]["content"]
    finally:
        service.close()
