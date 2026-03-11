from pathlib import Path

from click.testing import CliRunner

from scout.main import cli
from scout.pipeline.data_store.sqlite import SQLiteDataStore, build_business_lead_id
from scout.pipeline.models.business import Business


def _seed_business(db_path: Path, raw_root: Path) -> str:
    store = SQLiteDataStore(db_path=db_path, raw_root=raw_root)
    try:
        store.upsert_businesses(
            [
                Business(
                    name="Bravo Plumbing",
                    source="google_maps",
                    category="Plumbing",
                    location="Denver, CO",
                    state="CO",
                    address="500 Central Ave",
                    phone="555-2222",
                    website="https://bravo.example.com",
                )
            ]
        )
    finally:
        store.close()
    return build_business_lead_id("google_maps", "Bravo Plumbing", "500 Central Ave")


def test_workflow_cli_trigger_run_and_artifacts_flow():
    runner = CliRunner()
    with runner.isolated_filesystem():
        db_path = Path("canonical.db")
        raw_root = Path("raw")
        expected_lead_id = _seed_business(db_path, raw_root)

        list_result = runner.invoke(cli, ["lead", "list", "--db-path", str(db_path)])
        assert list_result.exit_code == 0
        assert expected_lead_id in list_result.output

        trigger_result = runner.invoke(
            cli,
            [
                "workflow",
                "trigger",
                expected_lead_id,
                "--action",
                "research",
                "--db-path",
                str(db_path),
            ],
        )
        assert trigger_result.exit_code == 0
        assert "queued run_id=" in trigger_result.output

        run_result = runner.invoke(
            cli,
            ["workflow", "run", "--max-jobs", "5", "--db-path", str(db_path)],
        )
        assert run_result.exit_code == 0
        assert "processed: 1" in run_result.output
        assert "action=research status=completed" in run_result.output

        artifacts_result = runner.invoke(
            cli,
            [
                "workflow",
                "artifacts",
                expected_lead_id,
                "--db-path",
                str(db_path),
            ],
        )
        assert artifacts_result.exit_code == 0
        assert "artifacts: 1" in artifacts_result.output
        assert "action=research" in artifacts_result.output
