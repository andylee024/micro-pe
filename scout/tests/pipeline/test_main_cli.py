from click.testing import CliRunner

from scout.main import cli
from scout.pipeline.models.business import Business
from scout.pipeline.models.market_dataset import MarketDataset
from scout.pipeline.models.query import Query
from scout.pipeline.outbound import LeadRepository


class StubRunner:
    def run(
        self, industry: str, location: str, max_results: int = 100, use_cache: bool = True
    ) -> MarketDataset:
        _ = max_results
        _ = use_cache
        return MarketDataset(
            query=Query(industry=industry, location=location),
            businesses=[
                Business(name="Acme HVAC", source="google_maps", location=location),
                Business(name="Blue Plumbing", source="google_maps", location=location),
            ],
        )


def test_run_shows_outbound_queue_strip(monkeypatch, tmp_path):
    db_path = tmp_path / "canonical.db"
    monkeypatch.setattr("scout.main.Runner", lambda: StubRunner())
    monkeypatch.setattr("scout.main.LeadRepository", lambda: LeadRepository(db_path=db_path))

    runner = CliRunner()
    result = runner.invoke(cli, ["run", "HVAC in Austin, TX"])

    assert result.exit_code == 0
    assert "outbound_queue:" in result.output
    assert "new=2" in result.output
    assert "total=2" in result.output


def test_lead_transition_command_updates_state(monkeypatch, tmp_path):
    db_path = tmp_path / "canonical.db"
    seed_repo = LeadRepository(db_path=db_path)
    try:
        seed = seed_repo.sync_businesses([Business(name="Acme HVAC", source="google_maps")])
        lead_id = seed[0].id
    finally:
        seed_repo.close()

    monkeypatch.setattr("scout.main.LeadRepository", lambda: LeadRepository(db_path=db_path))
    runner = CliRunner()

    result = runner.invoke(cli, ["lead", "transition", lead_id, "--status", "queued"])
    assert result.exit_code == 0
    assert "status=queued" in result.output
    assert "next_action=send_intro" in result.output

    queue_result = runner.invoke(cli, ["lead", "queue"])
    assert queue_result.exit_code == 0
    assert "queued=1" in queue_result.output
