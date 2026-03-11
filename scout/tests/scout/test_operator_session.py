from pathlib import Path

from scout.operator_session import OperatorSession
from scout.pipeline.data_store.sqlite import SQLiteDataStore
from scout.pipeline.models.business import Business
from scout.pipeline.models.lead import Lead


def _make_lead(idx: int) -> Lead:
    return Lead(
        lead_id=f"lead-{idx}",
        source="google_maps",
        name=f"HVAC Target {idx:02d}",
        address=f"{idx} Main St",
        phone=f"555-01{idx:02d}",
        website=f"https://target-{idx}.example.com",
        category="HVAC",
        location="Austin, TX",
        state="TX",
        rating=4.0 + (idx % 5) * 0.1,
        reviews=500 - idx,
        is_saved=False,
        saved_at=None,
        updated_at="2026-03-11T00:00:00+00:00",
    )


def test_dense_navigation_and_filter_preserves_selected_lead():
    session = OperatorSession(leads=[_make_lead(i) for i in range(30)], page_size=5)

    for _ in range(8):
        session.move_down()
    assert session.selected_index == 8
    assert session.scroll_offset == 4

    selected_before = session.selected_lead
    assert selected_before is not None
    session.apply_filter("target 08")
    assert session.total == 1
    assert session.selected_lead is not None
    assert session.selected_lead.lead_id == selected_before.lead_id

    session.clear_filter()
    assert session.total == 30
    assert session.selected_lead is not None
    assert session.selected_lead.lead_id == selected_before.lead_id


def test_selected_business_pane_returns_core_context():
    session = OperatorSession(leads=[_make_lead(1)], page_size=5)

    detail = session.selected_business_detail()
    assert detail is not None
    assert detail.name == "HVAC Target 01"
    assert detail.address == "1 Main St"
    assert detail.phone == "555-0101"
    assert detail.website == "https://target-1.example.com"
    assert detail.reviews == 499
    assert detail.is_saved is False

    rendered = session.render_selected_business_pane()
    assert "selected_business: HVAC Target 01" in rendered
    assert "address: 1 Main St" in rendered
    assert "phone: 555-0101" in rendered
    assert "website: https://target-1.example.com" in rendered


def test_save_and_remove_actions_persist_to_canonical_lead_state(tmp_path: Path):
    store = SQLiteDataStore(db_path=tmp_path / "canonical.db", raw_root=tmp_path / "raw")
    try:
        store.sync_business_leads(
            [
                Business(
                    source="google_maps",
                    name="Alpha HVAC",
                    address="10 Main St",
                    location="Austin, TX",
                    phone="555-1000",
                    website="https://alpha.example.com",
                    category="HVAC",
                    reviews=120,
                )
            ]
        )
        leads = store.list_leads(location="Austin", industry="HVAC", limit=10)
        session = OperatorSession(leads=leads, lead_store=store)

        session.handle_key("s")
        selected = session.selected_lead
        assert selected is not None
        assert selected.is_saved is True

        persisted = store.get_lead(selected.lead_id)
        assert persisted is not None
        assert persisted.is_saved is True
        assert persisted.saved_at is not None

        session.handle_key("x")
        selected = session.selected_lead
        assert selected is not None
        assert selected.is_saved is False

        persisted = store.get_lead(selected.lead_id)
        assert persisted is not None
        assert persisted.is_saved is False
        assert persisted.saved_at is None
    finally:
        store.close()


def test_keyboard_shortcuts_cover_dense_scanning_motion():
    session = OperatorSession(leads=[_make_lead(i) for i in range(40)], page_size=6)

    session.handle_key("j")
    session.handle_key("j")
    session.handle_key("page_down")
    assert session.selected_index == 8

    session.handle_key("G")
    assert session.selected_index == 39
    assert session.scroll_offset == 34

    session.handle_key("g")
    session.handle_key("g")
    assert session.selected_index == 0
    assert session.scroll_offset == 0

    assert session.open_selected_detail() is True
    assert session.detail_open is True
    assert session.handle_key("escape") is True
    assert session.detail_open is False
