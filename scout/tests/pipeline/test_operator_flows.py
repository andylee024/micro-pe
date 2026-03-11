import csv
from pathlib import Path

from click.testing import CliRunner

from scout.main import cli
from scout.pipeline.data_store.sqlite import SQLiteDataStore, build_business_lead_id
from scout.pipeline.models.business import Business
from scout.pipeline.models.listing import Listing


def _seed_store(db_path: str | Path, raw_root: str | Path) -> None:
    store = SQLiteDataStore(db_path=db_path, raw_root=raw_root)
    try:
        store.upsert_businesses(
            [
                Business(
                    name="Alpha Air",
                    source="google_maps",
                    category="HVAC",
                    location="Austin, TX",
                    state="TX",
                    phone="555-0101",
                ),
                Business(
                    name="Delta Plumbing",
                    source="google_maps",
                    category="Plumbing",
                    location="Dallas, TX",
                    state="TX",
                ),
            ]
        )
        store.upsert_listings(
            [
                Listing(
                    source="bizbuysell",
                    source_id="hvac-1",
                    url="https://example.com/hvac-1",
                    name="Bravo HVAC Listing",
                    industry="HVAC",
                    location="Austin, TX",
                    state="TX",
                ),
                Listing(
                    source="bizbuysell",
                    source_id="plumbing-1",
                    url="https://example.com/plumbing-1",
                    name="Echo Plumbing Listing",
                    industry="Plumbing",
                    location="Dallas, TX",
                    state="TX",
                ),
            ]
        )
    finally:
        store.close()


def test_notes_persist_for_canonical_leads(tmp_path: Path):
    db_path = tmp_path / "canonical.db"
    raw_root = tmp_path / "raw"
    _seed_store(db_path, raw_root)

    store = SQLiteDataStore(db_path=db_path, raw_root=raw_root)
    try:
        leads = store.list_leads(industry="hvac", location="Austin", limit=10)
        assert len(leads) == 2
        business_lead_id = build_business_lead_id("google_maps", "Alpha Air", "")

        store.upsert_lead_note(business_lead_id, "Call owner next week")
    finally:
        store.close()

    reopened = SQLiteDataStore(db_path=db_path, raw_root=raw_root)
    try:
        leads = reopened.list_leads(industry="hvac", location="Austin", limit=10)
        by_id = {lead.lead_id: lead for lead in leads}

        assert business_lead_id in by_id
        assert by_id[business_lead_id].note == "Call owner next week"
        assert by_id[business_lead_id].note_updated_at is not None

        reopened.upsert_lead_note(business_lead_id, "Left voicemail")
        note, _ = reopened.get_lead_note(business_lead_id) or ("", "")
        assert note == "Left voicemail"
    finally:
        reopened.close()


def test_dump_list_shows_filtered_leads_and_notes():
    runner = CliRunner()
    with runner.isolated_filesystem():
        db_path = Path("canonical.db")
        raw_root = Path("raw")
        _seed_store(db_path, raw_root)

        store = SQLiteDataStore(db_path=db_path, raw_root=raw_root)
        try:
            business_lead_id = build_business_lead_id("google_maps", "Alpha Air", "")
            store.upsert_lead_note(business_lead_id, "priority lead")
        finally:
            store.close()

        result = runner.invoke(
            cli,
            [
                "dump-list",
                "--industry",
                "hvac",
                "--location",
                "Austin",
                "--db-path",
                str(db_path),
            ],
        )

        assert result.exit_code == 0
        assert "lead_id\tlead_type\tname\tlocation\tsource\tnote" in result.output
        assert business_lead_id in result.output
        assert "priority lead" in result.output
        assert "Echo Plumbing Listing" not in result.output


def test_export_writes_filtered_csv_with_note_fields():
    runner = CliRunner()
    with runner.isolated_filesystem():
        db_path = Path("canonical.db")
        raw_root = Path("raw")
        output_path = Path("exports") / "hvac.csv"
        _seed_store(db_path, raw_root)

        store = SQLiteDataStore(db_path=db_path, raw_root=raw_root)
        try:
            listing_lead_id = "bizbuysell:hvac-1"
            store.upsert_lead_note(listing_lead_id, "follow up with broker")
        finally:
            store.close()

        result = runner.invoke(
            cli,
            [
                "export",
                "--industry",
                "hvac",
                "--location",
                "Austin",
                "--format",
                "csv",
                "--output",
                str(output_path),
                "--db-path",
                str(db_path),
            ],
        )

        assert result.exit_code == 0
        assert output_path.exists()

        with output_path.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))

        assert len(rows) == 2
        by_id = {row["lead_id"]: row for row in rows}
        assert "bizbuysell:hvac-1" in by_id
        assert by_id["bizbuysell:hvac-1"]["note"] == "follow up with broker"
        assert "Echo Plumbing Listing" not in {row["name"] for row in rows}
