"""Scout CLI (pipeline-only baseline)."""

from __future__ import annotations

import click

from scout.pipeline.data_store.sqlite import SQLiteDataStore
from scout.pipeline.runner import Runner
from scout.pipeline.worker import WorkflowWorker
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

    for item in dataset.coverage:
        suffix = f" error={item.error}" if item.error else ""
        click.echo(
            f"source={item.source} status={item.status} records={item.records} "
            f"duration_ms={item.duration_ms}{suffix}"
        )


@cli.command("enqueue")
@click.argument("query")
@click.option("--max-results", default=100, show_default=True, type=int)
@click.option("--no-cache", is_flag=True, default=False)
@click.option("--max-attempts", default=3, show_default=True, type=int)
def enqueue_workflow(query: str, max_results: int, no_cache: bool, max_attempts: int) -> None:
    """Queue one workflow run instead of executing inline."""
    try:
        industry, location = parse_query(query)
    except Exception as exc:  # noqa: BLE001
        raise click.ClickException(str(exc)) from exc

    store = SQLiteDataStore()
    runner = Runner(data_store=store)
    queued = store.enqueue_workflow(
        query=runner.build_query(
            industry=industry,
            location=location,
            max_results=max_results,
            use_cache=not no_cache,
        ),
        max_attempts=max_attempts,
    )

    click.echo(f"queued run_id: {queued.run_id}")
    click.echo(f"status: {queued.status}")
    click.echo(f"max_attempts: {queued.max_attempts}")


@cli.group("worker")
def worker_group() -> None:
    """Workflow queue worker commands."""


@worker_group.command("run-once")
@click.option("--worker-id", default="local-worker", show_default=True)
@click.option("--retry-delay-seconds", default=30, show_default=True, type=int)
def worker_run_once(worker_id: str, retry_delay_seconds: int) -> None:
    """Claim and execute a single queued workflow record."""
    store = SQLiteDataStore()
    worker = WorkflowWorker(data_store=store)
    result = worker.run_once(worker_id=worker_id, retry_delay_seconds=retry_delay_seconds)

    if not result.claimed:
        click.echo("no queued workflows available")
        return

    assert result.run is not None
    click.echo(f"run_id: {result.run.run_id}")
    click.echo(f"status: {result.run.status}")
    click.echo(f"attempt: {result.run.attempt_count}/{result.run.max_attempts}")
    if result.run.error:
        click.echo(f"error_type: {result.run.error.error_type}")
        click.echo(f"error_message: {result.run.error.message}")


if __name__ == "__main__":
    cli()
