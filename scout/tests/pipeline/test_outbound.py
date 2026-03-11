from scout.pipeline.models.business import Business
from scout.pipeline.outbound import LeadRepository


def test_sync_businesses_creates_default_outbound_state(tmp_path):
    repo = LeadRepository(db_path=tmp_path / "canonical.db")
    try:
        leads = repo.sync_businesses(
            [
                Business(
                    name="Acme HVAC",
                    source="google_maps",
                    address="101 Main St",
                    location="Austin, TX",
                    phone="555-0100",
                )
            ]
        )
    finally:
        repo.close()

    assert len(leads) == 1
    assert leads[0].outbound_status == "new"
    assert leads[0].next_action == "research"


def test_sync_preserves_existing_outbound_state(tmp_path):
    repo = LeadRepository(db_path=tmp_path / "canonical.db")
    try:
        first = repo.sync_businesses(
            [Business(name="Acme HVAC", source="google_maps", location="Austin, TX")]
        )
        lead = repo.transition_lead(lead_id=first[0].id, outbound_status="queued")
        assert lead.outbound_status == "queued"
        assert lead.next_action == "send_intro"

        repo.sync_businesses(
            [
                Business(
                    name="Acme HVAC",
                    source="google_maps",
                    location="Austin, TX",
                    phone="555-0199",
                )
            ]
        )
        refreshed = repo.get_lead(first[0].id)
    finally:
        repo.close()

    assert refreshed is not None
    assert refreshed.outbound_status == "queued"
    assert refreshed.next_action == "send_intro"
    assert refreshed.phone == "555-0199"


def test_transition_rejects_invalid_status_path(tmp_path):
    repo = LeadRepository(db_path=tmp_path / "canonical.db")
    try:
        leads = repo.sync_businesses([Business(name="Acme HVAC", source="google_maps")])
        lead_id = leads[0].id
        try:
            repo.transition_lead(lead_id=lead_id, outbound_status="responded")
            assert False, "Expected transition to fail"
        except ValueError as exc:
            assert "Invalid outbound transition" in str(exc)
    finally:
        repo.close()


def test_queue_strip_counts_by_status(tmp_path):
    repo = LeadRepository(db_path=tmp_path / "canonical.db")
    try:
        leads = repo.sync_businesses(
            [
                Business(name="Acme HVAC", source="google_maps", location="Austin, TX"),
                Business(name="Blue Plumbing", source="google_maps", location="Austin, TX"),
                Business(name="City Electric", source="google_maps", location="Austin, TX"),
            ]
        )

        repo.transition_lead(lead_id=leads[0].id, outbound_status="queued")
        repo.transition_lead(lead_id=leads[0].id, outbound_status="contacted")
        repo.transition_lead(lead_id=leads[1].id, outbound_status="queued")
        queue = repo.queue_strip(location="Austin, TX")
    finally:
        repo.close()

    assert queue["total"] == 3
    assert queue["contacted"] == 1
    assert queue["queued"] == 1
    assert queue["new"] == 1
