import csv
import io

from scout.app.service import ScoutAppService
from scout.app.store import build_search_id
from scout.pipeline.data_store.sqlite import SQLiteDataStore
from scout.pipeline.models.business import Business
from scout.pipeline.models.listing import Listing
from scout.pipeline.models.market_dataset import Coverage, MarketDataset
from scout.pipeline.models.query import Query
from scout.pipeline.runner import Runner


class StubWorkflow:
    def __init__(self, data_store: SQLiteDataStore) -> None:
        self.data_store = data_store
        self.run_calls = 0

    def run(self, query: Query) -> MarketDataset:
        self.run_calls += 1
        businesses = [
            Business(
                name="Atlas HVAC",
                source="google_maps",
                address="100 Main St",
                location=query.location,
                state="TX",
                phone="512-555-0100",
                website="https://atlashvac.example.com",
                category=query.industry,
            )
        ]
        listings = [
            Listing(
                source="bizbuysell",
                source_id="atlas-1",
                url="https://example.com/listings/atlas-1",
                name="Atlas HVAC for Sale",
                industry=query.industry,
                location=query.location,
                state="TX",
                asking_price=750000.0,
            )
        ]

        self.data_store.upsert_businesses(businesses)
        self.data_store.upsert_listings(listings)
        return MarketDataset(
            query=query,
            businesses=businesses,
            listings=listings,
            coverage=[
                Coverage(source="google_maps", status="success", records=1, duration_ms=1),
                Coverage(source="bizbuysell", status="success", records=1, duration_ms=1),
            ],
        )


def _make_service(tmp_path):
    db_path = tmp_path / "canonical.db"
    raw_root = tmp_path / "raw"
    data_store = SQLiteDataStore(db_path=db_path, raw_root=raw_root)
    workflow = StubWorkflow(data_store)
    runner = Runner(workflow=workflow, data_store=data_store)
    service = ScoutAppService(runner=runner, db_path=db_path)
    return service, workflow, data_store


def test_run_search_persists_search_and_search_run_state(tmp_path):
    service, workflow, data_store = _make_service(tmp_path)
    try:
        execution = service.run_search(
            query_text="HVAC businesses in Austin",
            industry="hvac",
            location="Austin, TX",
            max_results=25,
            use_cache=False,
        )

        assert execution.search.search_id == build_search_id("hvac", "Austin, TX")
        assert execution.search_run.run_id == execution.dataset.query.run_id
        assert execution.search_run.search_id == execution.search.search_id
        assert execution.search_run.business_count == 1
        assert execution.search_run.listing_count == 1

        leads = service.list_leads(search_id=execution.search.search_id)
        assert len(leads) == 2
        assert {lead.lead_type for lead in leads} == {"business", "listing"}
        assert any(lead.lead_id.startswith("business:") for lead in leads)
        assert any(lead.lead_id.startswith("listing:") for lead in leads)
        assert workflow.run_calls == 1
    finally:
        service.close()
        data_store.close()


def test_leads_can_be_saved_and_removed_without_rerunning_pipeline(tmp_path):
    service, workflow, data_store = _make_service(tmp_path)
    try:
        execution = service.run_search(
            query_text="HVAC businesses in Austin",
            industry="hvac",
            location="Austin, TX",
        )
        search_id = execution.search.search_id
        discovered = service.list_leads(search_id=search_id)
        business_lead = next(lead for lead in discovered if lead.lead_type == "business")

        saved = service.save_lead(
            lead_id=business_lead.lead_id,
            search_id=search_id,
            note="priority outreach",
        )
        assert saved.is_saved is True
        assert saved.note == "priority outreach"
        assert workflow.run_calls == 1

        saved_leads = service.list_saved_leads(search_id=search_id)
        assert [lead.lead_id for lead in saved_leads] == [business_lead.lead_id]

        removed = service.remove_lead(lead_id=business_lead.lead_id)
        assert removed is True
        assert workflow.run_calls == 1
        assert service.list_saved_leads(search_id=search_id) == []

        discovered_after_remove = service.list_leads(search_id=search_id)
        restored = next(
            lead for lead in discovered_after_remove if lead.lead_id == business_lead.lead_id
        )
        assert restored.is_saved is False
    finally:
        service.close()
        data_store.close()


def test_curated_lead_export_is_available_from_service_boundary(tmp_path):
    service, workflow, data_store = _make_service(tmp_path)
    try:
        execution = service.run_search(
            query_text="HVAC businesses in Austin",
            industry="hvac",
            location="Austin, TX",
        )
        search_id = execution.search.search_id
        discovered = service.list_leads(search_id=search_id)
        for lead in discovered:
            service.save_lead(
                lead_id=lead.lead_id,
                search_id=search_id,
                summary="curated for outreach",
            )

        csv_text = service.export_saved_leads_csv(search_id=search_id)
        rows = list(csv.DictReader(io.StringIO(csv_text)))
        assert len(rows) == 2
        assert [row["name"] for row in rows] == ["Atlas HVAC", "Atlas HVAC for Sale"]
        assert all(row["summary"] == "curated for outreach" for row in rows)
        assert workflow.run_calls == 1
    finally:
        service.close()
        data_store.close()
