"""Scout CLI (pipeline-only baseline)."""

from __future__ import annotations

import click

from scout.pipeline.outbound import LeadRepository, format_queue_strip
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

    for item in dataset.coverage:
        suffix = f" error={item.error}" if item.error else ""
        click.echo(
            f"source={item.source} status={item.status} records={item.records} "
            f"duration_ms={item.duration_ms}{suffix}"
        )

    lead_repo = LeadRepository()
    try:
        leads = lead_repo.sync_businesses(dataset.businesses)
        queue = lead_repo.queue_strip(location=dataset.query.location)
        click.echo(
            format_queue_strip(
                queue,
                location=dataset.query.location,
            )
            + f" in_scope={len(leads)}"
        )
    finally:
        lead_repo.close()


@cli.group("lead")
def lead_group() -> None:
    """Outbound lead state operations."""


@lead_group.command("list")
@click.option("--status", default=None, help="Filter by outbound status.")
@click.option("--location", default=None, help="Filter by location.")
@click.option("--limit", default=25, show_default=True, type=int)
def list_leads(status: str | None, location: str | None, limit: int) -> None:
    """List current leads and outbound state."""
    lead_repo = LeadRepository()
    try:
        leads = lead_repo.list_leads(status=status, location=location, limit=limit)
    except ValueError as exc:
        lead_repo.close()
        raise click.ClickException(str(exc)) from exc

    try:
        click.echo(f"leads: {len(leads)}")
        for lead in leads:
            click.echo(
                f"id={lead.id} name={lead.name} status={lead.outbound_status} "
                f"next_action={lead.next_action} location={lead.location}"
            )
    finally:
        lead_repo.close()


@lead_group.command("transition")
@click.argument("lead_id")
@click.option("--status", "status_value", required=True, help="Target outbound status.")
@click.option("--next-action", default=None, help="Optional target next action override.")
def transition_lead(lead_id: str, status_value: str, next_action: str | None) -> None:
    """Transition a lead to the next outbound state."""
    lead_repo = LeadRepository()
    try:
        lead = lead_repo.transition_lead(
            lead_id=lead_id,
            outbound_status=status_value,
            next_action=next_action,
        )
    except (ValueError, KeyError) as exc:
        lead_repo.close()
        raise click.ClickException(str(exc)) from exc

    try:
        click.echo(
            f"id={lead.id} status={lead.outbound_status} next_action={lead.next_action} "
            f"last_contacted_at={lead.last_contacted_at or '-'}"
        )
    finally:
        lead_repo.close()


@lead_group.command("queue")
@click.option("--location", default=None, help="Filter queue strip by location.")
def show_queue(location: str | None) -> None:
    """Show outbound queue-strip summary."""
    lead_repo = LeadRepository()
    try:
        queue = lead_repo.queue_strip(location=location)
        click.echo(format_queue_strip(queue, location=location))
    finally:
        lead_repo.close()


if __name__ == "__main__":
    cli()
