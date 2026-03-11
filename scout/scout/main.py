"""Scout CLI (pipeline-only baseline)."""

from __future__ import annotations

from pathlib import Path

import click

from scout.pipeline.history import HistoryService
from scout.pipeline.runner import Runner
from scout.shared.query_parser import parse_query


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
    if dataset.run_diff is not None:
        if dataset.run_diff.previous_run_id:
            click.echo(
                "diff: "
                f"previous_run_id={dataset.run_diff.previous_run_id} "
                f"businesses +{dataset.run_diff.added_businesses}/-{dataset.run_diff.removed_businesses} "
                f"listings +{dataset.run_diff.added_listings}/-{dataset.run_diff.removed_listings}"
            )
        else:
            click.echo("diff: previous_run_id=<none> (first run for this market)")

    for item in dataset.coverage:
        suffix = f" error={item.error}" if item.error else ""
        click.echo(
            f"source={item.source} status={item.status} records={item.records} "
            f"duration_ms={item.duration_ms}{suffix}"
        )


@cli.command("history")
@click.option("--db-path", default="outputs/pipeline/canonical.db", show_default=True, type=click.Path())
@click.option("--limit", default=10, show_default=True, type=int)
@click.option("--industry", default=None)
@click.option("--location", default=None)
def history_command(db_path: str, limit: int, industry: str | None, location: str | None) -> None:
    """Show recent search runs with canonical diff summaries."""
    if limit < 1:
        raise click.ClickException("--limit must be >= 1")
    service = HistoryService(db_path=db_path)
    try:
        entries = service.list_runs(limit=limit, industry=industry, location=location)
    finally:
        service.close()
    if not entries:
        click.echo("No search history found.")
        return

    for entry in entries:
        previous = entry.previous_run_id or "<none>"
        click.echo(
            f"run_id={entry.run_id} created_at={entry.created_at} "
            f"industry={entry.industry} location={entry.location} "
            f"businesses={entry.business_count} listings={entry.listing_count} "
            f"previous_run_id={previous} "
            f"diff_businesses=+{entry.added_businesses}/-{entry.removed_businesses} "
            f"diff_listings=+{entry.added_listings}/-{entry.removed_listings}"
        )


@cli.command("diff")
@click.argument("run_id")
@click.option("--db-path", default="outputs/pipeline/canonical.db", show_default=True, type=click.Path())
@click.option("--limit-items", default=100, show_default=True, type=int)
def diff_command(run_id: str, db_path: str, limit_items: int) -> None:
    """Show canonical diff details for one run."""
    if limit_items < 1:
        raise click.ClickException("--limit-items must be >= 1")
    service = HistoryService(db_path=db_path)
    try:
        try:
            view = service.get_diff(run_id=run_id)
        except ValueError as exc:
            raise click.ClickException(str(exc)) from exc
    finally:
        service.close()

    click.echo(f"run_id: {view.run_id}")
    click.echo(f"created_at: {view.created_at}")
    click.echo(f"industry: {view.industry}")
    click.echo(f"location: {view.location}")
    click.echo(f"previous_run_id: {view.previous_run_id or '<none>'}")
    click.echo(f"diff_businesses: +{view.added_businesses}/-{view.removed_businesses}")
    click.echo(f"diff_listings: +{view.added_listings}/-{view.removed_listings}")

    if not view.items:
        click.echo("diff_items: none")
        return

    click.echo("diff_items:")
    for item in view.items[:limit_items]:
        click.echo(
            f"- item_type={item.item_type} change={item.change_type} "
            f"name={item.name} source={item.source} location={item.location} state={item.state}"
        )
    if len(view.items) > limit_items:
        click.echo(f"... truncated {len(view.items) - limit_items} item(s)")


@cli.command("export-diff")
@click.argument("run_id")
@click.option("--output", required=True, type=click.Path())
@click.option("--format", "fmt", default="csv", show_default=True, type=click.Choice(["csv", "json"]))
@click.option("--db-path", default="outputs/pipeline/canonical.db", show_default=True, type=click.Path())
def export_diff_command(run_id: str, output: str, fmt: str, db_path: str) -> None:
    """Export canonical diff items for one run."""
    service = HistoryService(db_path=db_path)
    try:
        try:
            output_path = service.export_diff(run_id=run_id, output_path=Path(output), fmt=fmt)
        except ValueError as exc:
            raise click.ClickException(str(exc)) from exc
    finally:
        service.close()
    click.echo(f"diff export written: {output_path}")


if __name__ == "__main__":
    cli()
