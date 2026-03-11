"""Scout CLI."""

from __future__ import annotations

import click

from scout.pipeline.data_store.sqlite import SQLiteDataStore
from scout.pipeline.lead_workflow import LeadWorkflowService
from scout.pipeline.runner import Runner
from scout.pipeline.worker import WorkflowWorker
from scout.shared.query_parser import parse_query

DEFAULT_DB_PATH = "outputs/pipeline/canonical.db"
WORKFLOW_ACTION_CHOICES = ("research", "enrich", "prepare-call", "draft-email")


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


@cli.group("lead")
def lead_group() -> None:
    """Lead discovery and selection commands."""


@lead_group.command("list")
@click.option("--industry", default="", help="Case-insensitive industry/category filter.")
@click.option("--location", default="", help="Case-insensitive location filter.")
@click.option("--state", default="", help="State code filter (case-insensitive exact match).")
@click.option("--limit", default=50, show_default=True, type=int)
@click.option("--offset", default=0, show_default=True, type=int)
@click.option("--db-path", default=DEFAULT_DB_PATH, show_default=True, type=click.Path())
def list_leads(
    industry: str, location: str, state: str, limit: int, offset: int, db_path: str
) -> None:
    """List saved leads from canonical businesses + listings."""
    store = SQLiteDataStore(db_path=db_path)
    try:
        leads = store.list_leads(
            industry=industry,
            location=location,
            state=state,
            limit=limit,
            offset=offset,
        )
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc
    finally:
        store.close()

    click.echo(f"leads: {len(leads)}")
    for lead in leads:
        click.echo(
            f"lead_id={lead.lead_id} type={lead.lead_type} name={lead.name} "
            f"industry={lead.industry or '-'} location={lead.location or '-'} source={lead.source}"
        )


@cli.group("workflow")
def workflow_group() -> None:
    """Lead workflow queue + handler commands."""


@workflow_group.command("trigger")
@click.argument("lead_id")
@click.option(
    "--action",
    "action_name",
    required=True,
    type=click.Choice(WORKFLOW_ACTION_CHOICES, case_sensitive=False),
)
@click.option("--db-path", default=DEFAULT_DB_PATH, show_default=True, type=click.Path())
def trigger_workflow(lead_id: str, action_name: str, db_path: str) -> None:
    """Queue one workflow action for a lead."""
    service = LeadWorkflowService(db_path=db_path)
    try:
        run_id = service.trigger(lead_id=lead_id, action=action_name)
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc
    finally:
        service.close()
    click.echo(f"queued run_id={run_id} lead_id={lead_id} action={action_name}")


@workflow_group.command("run")
@click.option("--max-jobs", default=25, show_default=True, type=int)
@click.option("--db-path", default=DEFAULT_DB_PATH, show_default=True, type=click.Path())
def run_workflow(max_jobs: int, db_path: str) -> None:
    """Run queued workflow actions with the built-in worker."""
    service = LeadWorkflowService(db_path=db_path)
    try:
        try:
            results = service.run_batch(max_jobs=max_jobs)
        except ValueError as exc:
            raise click.ClickException(str(exc)) from exc
    finally:
        service.close()

    click.echo(f"processed: {len(results)}")
    for result in results:
        suffix = f" error={result.error}" if result.error else ""
        click.echo(
            f"run_id={result.run_id} lead_id={result.lead_id} action={result.action} "
            f"status={result.status}{suffix}"
        )


@workflow_group.command("queue")
@click.option("--lead-id", default=None, help="Optional lead_id filter.")
@click.option(
    "--status",
    "status_filter",
    default=None,
    type=click.Choice(["queued", "running", "completed", "failed"], case_sensitive=False),
)
@click.option("--limit", default=25, show_default=True, type=int)
@click.option("--db-path", default=DEFAULT_DB_PATH, show_default=True, type=click.Path())
def show_workflow_queue(
    lead_id: str | None,
    status_filter: str | None,
    limit: int,
    db_path: str,
) -> None:
    """Show canonical workflow run state."""
    service = LeadWorkflowService(db_path=db_path)
    try:
        runs = service.list_runs(lead_id=lead_id, status=status_filter, limit=limit)
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc
    finally:
        service.close()

    click.echo(f"workflow_runs: {len(runs)}")
    for row in runs:
        suffix = f" error={row['error']}" if row["error"] else ""
        click.echo(
            f"id={row['id']} lead_id={row['lead_id']} action={row['action']} "
            f"status={row['status']} artifact_id={row['artifact_id'] or '-'}{suffix}"
        )


@workflow_group.command("artifacts")
@click.argument("lead_id")
@click.option(
    "--action",
    "action_filter",
    default=None,
    type=click.Choice(WORKFLOW_ACTION_CHOICES, case_sensitive=False),
)
@click.option("--limit", default=20, show_default=True, type=int)
@click.option("--db-path", default=DEFAULT_DB_PATH, show_default=True, type=click.Path())
def show_workflow_artifacts(
    lead_id: str,
    action_filter: str | None,
    limit: int,
    db_path: str,
) -> None:
    """List stored workflow artifacts for a lead."""
    service = LeadWorkflowService(db_path=db_path)
    try:
        artifacts = service.list_artifacts(lead_id=lead_id, action=action_filter, limit=limit)
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc
    finally:
        service.close()

    click.echo(f"artifacts: {len(artifacts)}")
    for artifact in artifacts:
        click.echo(
            f"id={artifact['id']} lead_id={artifact['lead_id']} action={artifact['action']} "
            f"created_at={artifact['created_at']} summary={artifact['summary']}"
        )


if __name__ == "__main__":
    cli()
