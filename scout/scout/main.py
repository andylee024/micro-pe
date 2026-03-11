"""Scout CLI entrypoints for pipeline runs and terminal research mode."""

from __future__ import annotations

from typing import TYPE_CHECKING

import click

from scout.pipeline.runner import Runner
from scout.shared.query_parser import parse_query

if TYPE_CHECKING:
    from scout.app.terminal import ScoutTerminalApp


@click.group()
def cli() -> None:
    """Scout data pipeline CLI."""


@cli.command("run")
@click.argument("query")
@click.option("--max-results", default=100, show_default=True, type=int)
@click.option("--no-cache", is_flag=True, default=False)
def run_pipeline(query: str, max_results: int, no_cache: bool) -> None:
    """Run one ETL pipeline execution from a natural-language query.

    Example: scout run "HVAC businesses in Los Angeles"
    """
    try:
        industry, location = parse_query(query)
    except Exception as exc:  # noqa: BLE001
        raise click.ClickException(str(exc)) from exc
    runner = Runner()
    try:
        dataset = runner.run(
            industry=industry,
            location=location,
            max_results=max_results,
            use_cache=not no_cache,
        )
    except Exception as exc:  # noqa: BLE001
        raise click.ClickException(str(exc)) from exc

    click.echo(f"run_id: {dataset.query.run_id}")
    click.echo(f"industry: {dataset.query.industry}")
    click.echo(f"location: {dataset.query.location}")
    click.echo(f"businesses: {len(dataset.businesses)}")
    click.echo(f"listings: {len(dataset.listings)}")

    for item in dataset.coverage:
        suffix = f" error={item.error}" if item.error else ""
        click.echo(
            f"source={item.source} status={item.status} records={item.records} "
            f"duration_ms={item.duration_ms}{suffix}"
        )


def create_research_app(query: str, max_results: int, no_cache: bool) -> ScoutTerminalApp:
    """Build the Textual app from canonical service/state layers."""
    from scout.app.services import PipelineResearchService
    from scout.app.state import TerminalStateStore
    from scout.app.terminal import ScoutTerminalApp

    state_store = TerminalStateStore(service=PipelineResearchService())
    return ScoutTerminalApp(
        state_store=state_store,
        query_text=query,
        max_results=max_results,
        use_cache=not no_cache,
    )


@cli.command("research")
@click.argument("query")
@click.option("--max-results", default=100, show_default=True, type=int)
@click.option("--no-cache", is_flag=True, default=False)
def run_research(query: str, max_results: int, no_cache: bool) -> None:
    """Launch the Textual research shell for one market query."""
    app = create_research_app(query=query, max_results=max_results, no_cache=no_cache)
    app.run()


if __name__ == "__main__":
    cli()
