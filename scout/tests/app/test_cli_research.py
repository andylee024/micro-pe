from __future__ import annotations

from click.testing import CliRunner

from scout.main import cli


def test_research_command_builds_and_runs_textual_app(monkeypatch):
    observed: dict[str, object] = {}

    class StubApp:
        def run(self) -> None:
            observed["ran"] = True

    def fake_create_research_app(query: str, max_results: int, no_cache: bool) -> StubApp:
        observed["query"] = query
        observed["max_results"] = max_results
        observed["no_cache"] = no_cache
        return StubApp()

    monkeypatch.setattr("scout.main.create_research_app", fake_create_research_app)

    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "research",
            "HVAC businesses in Los Angeles",
            "--max-results",
            "40",
            "--no-cache",
        ],
    )

    assert result.exit_code == 0
    assert observed == {
        "query": "HVAC businesses in Los Angeles",
        "max_results": 40,
        "no_cache": True,
        "ran": True,
    }
