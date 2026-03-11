from pathlib import Path

from click.testing import CliRunner

from scout.main import cli
from scout.pipeline.data_store.sqlite import SQLiteDataStore
from scout.pipeline.models.business import Business
from scout.pipeline.models.listing import Listing
from scout.pipeline.models.market_dataset import Coverage, MarketDataset, RunDiffSummary
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


def _seed_history(db_path: Path, raw_root: Path) -> None:
    store = SQLiteDataStore(db_path=db_path, raw_root=raw_root)
    try:
        store.record_run(
            query=Query(
                industry="hvac",
                location="Austin, TX",
                run_id="run-one",
                created_at="2026-03-11T10:00:00+00:00",
            ),
            businesses=[
                Business(name="Acme HVAC", source="google_maps", location="Austin, TX"),
                Business(name="Bravo HVAC", source="google_maps", location="Austin, TX"),
            ],
            listings=[_listing("1", "Acme Listing")],
        )
        store.record_run(
            query=Query(
                industry="hvac",
                location="Austin, TX",
                run_id="run-two",
                created_at="2026-03-11T10:05:00+00:00",
            ),
            businesses=[
                Business(name="Acme HVAC", source="google_maps", location="Austin, TX"),
                Business(name="City HVAC", source="google_maps", location="Austin, TX"),
            ],
            listings=[_listing("1", "Acme Listing"), _listing("2", "City Listing")],
        )
    finally:
        store.close()


def test_history_command_surfaces_diff_summary(tmp_path: Path):
    db_path = tmp_path / "canonical.db"
    _seed_history(db_path, tmp_path / "raw")

    runner = CliRunner()
    result = runner.invoke(cli, ["history", "--db-path", str(db_path), "--limit", "5"])

    assert result.exit_code == 0
    assert "run_id=run-two" in result.output
    assert "previous_run_id=run-one" in result.output
    assert "diff_businesses=+1/-1" in result.output
    assert "diff_listings=+1/-0" in result.output


def test_run_command_shows_diff_summary(monkeypatch):
    class StubRunner:
        def run(self, **_: object) -> MarketDataset:
            query = Query(
                industry="hvac",
                location="Austin, TX",
                run_id="run-live",
                created_at="2026-03-11T11:00:00+00:00",
            )
            return MarketDataset(
                query=query,
                businesses=[Business(name="Acme HVAC", source="google_maps", location="Austin, TX")],
                listings=[],
                coverage=[Coverage(source="google_maps", status="success", records=1, duration_ms=12)],
                run_diff=RunDiffSummary(
                    run_id="run-live",
                    previous_run_id="run-prev",
                    added_businesses=1,
                    removed_businesses=0,
                    added_listings=0,
                    removed_listings=0,
                ),
            )

    monkeypatch.setattr("scout.main.Runner", StubRunner)
    monkeypatch.setattr("scout.main.parse_query", lambda _query: ("hvac", "Austin, TX"))

    runner = CliRunner()
    result = runner.invoke(cli, ["run", "HVAC in Austin"])

    assert result.exit_code == 0
    assert "run_id: run-live" in result.output
    assert "diff: previous_run_id=run-prev businesses +1/-0 listings +0/-0" in result.output


def test_diff_command_shows_diff_items(tmp_path: Path):
    db_path = tmp_path / "canonical.db"
    _seed_history(db_path, tmp_path / "raw")

    runner = CliRunner()
    result = runner.invoke(cli, ["diff", "run-two", "--db-path", str(db_path)])

    assert result.exit_code == 0
    assert "run_id: run-two" in result.output
    assert "previous_run_id: run-one" in result.output
    assert "diff_businesses: +1/-1" in result.output
    assert "name=City HVAC" in result.output
    assert "name=Bravo HVAC" in result.output


def test_export_diff_command_writes_csv(tmp_path: Path):
    db_path = tmp_path / "canonical.db"
    _seed_history(db_path, tmp_path / "raw")

    output = tmp_path / "diff.csv"
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "export-diff",
            "run-two",
            "--db-path",
            str(db_path),
            "--format",
            "csv",
            "--output",
            str(output),
        ],
    )

    assert result.exit_code == 0
    assert output.exists()
    exported = output.read_text(encoding="utf-8")
    assert "run_id,previous_run_id,item_type,change_type,item_key,source,name,location,state" in exported
    assert "run-two,run-one,business,added" in exported
