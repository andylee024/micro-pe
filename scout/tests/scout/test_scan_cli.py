from pathlib import Path

from click.testing import CliRunner

from scout.main import cli
from scout.pipeline.data_store.sqlite import SQLiteDataStore
from scout.pipeline.models.business import Business
from scout.pipeline.models.market_dataset import MarketDataset
from scout.pipeline.models.query import Query


class _StubRunner:
    def run(
        self, industry: str, location: str, max_results: int = 100, use_cache: bool = True
    ) -> MarketDataset:
        return MarketDataset(
            query=Query(
                industry=industry, location=location, max_results=max_results, use_cache=use_cache
            ),
            businesses=[
                Business(
                    source="google_maps",
                    name="Alpha HVAC",
                    address="10 Main St",
                    phone="555-1000",
                    website="https://alpha.example.com",
                    category="hvac",
                    location="Austin TX",
                    state="TX",
                    rating=4.8,
                    reviews=300,
                ),
                Business(
                    source="google_maps",
                    name="Bravo HVAC",
                    address="20 Main St",
                    phone="555-2000",
                    website="https://bravo.example.com",
                    category="hvac",
                    location="Austin TX",
                    state="TX",
                    rating=4.6,
                    reviews=200,
                ),
            ],
        )


def test_scan_command_replays_keys_and_persists_saved_state(tmp_path: Path, monkeypatch):
    db_path = tmp_path / "canonical.db"
    raw_root = tmp_path / "raw"

    monkeypatch.setattr("scout.main.Runner", _StubRunner)
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "scan",
            "HVAC businesses in Austin TX",
            "--db-path",
            str(db_path),
            "--raw-root",
            str(raw_root),
            "--key",
            "j",
            "--key",
            "s",
            "--key",
            "enter",
        ],
    )

    assert result.exit_code == 0
    assert "universe:" in result.output
    assert "selected_business: Bravo HVAC" in result.output
    assert "phone: 555-2000" in result.output
    assert "website: https://bravo.example.com" in result.output
    assert "saved: yes" in result.output

    store = SQLiteDataStore(db_path=db_path, raw_root=raw_root)
    try:
        saved = store.list_leads(saved_only=True, limit=10)
    finally:
        store.close()

    assert len(saved) == 1
    assert saved[0].name == "Bravo HVAC"
