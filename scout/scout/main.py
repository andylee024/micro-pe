"""Scout CLI."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import click

from scout.pipeline.data_store.sqlite import SQLiteDataStore
from scout.pipeline.models.lead import Lead
from scout.pipeline.outbound import LeadRepository, format_queue_strip
from scout.pipeline.runner import Runner
from scout.shared.query_parser import parse_query

DEFAULT_DB_PATH = "outputs/pipeline/canonical.db"
EXPORT_FIELDS = [
    "lead_id",
    "lead_type",
    "source",
    "source_record_id",
    "name",
    "industry",
    "location",
    "state",
    "address",
    "phone",
    "website",
    "url",
    "rating",
    "reviews",
    "asking_price",
    "annual_revenue",
    "cash_flow",
    "note",
    "note_updated_at",
]


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


@cli.command("dump-list")
@click.option("--industry", default="", help="Case-insensitive industry/category filter.")
@click.option("--location", default="", help="Case-insensitive location filter.")
@click.option("--state", default="", help="State code filter (exact, case-insensitive).")
@click.option("--limit", default=50, show_default=True, type=int)
@click.option("--offset", default=0, show_default=True, type=int)
@click.option("--db-path", default=DEFAULT_DB_PATH, show_default=True)
def dump_list(industry: str, location: str, state: str, limit: int, offset: int, db_path: str) -> None:
    """Dump a filtered lead set for operator review."""
    leads = _list_leads(
        industry=industry,
        location=location,
        state=state,
        limit=limit,
        offset=offset,
        db_path=db_path,
    )
    if not leads:
        click.echo("No leads found for current filters.")
        return

    click.echo("lead_id\tlead_type\tname\tlocation\tsource\tnote")
    for lead in leads:
        click.echo(
            f"{lead.lead_id}\t{lead.lead_type}\t{lead.name}\t{lead.location}\t{lead.source}\t"
            f"{_note_preview(lead.note)}"
        )


@cli.command("note")
@click.argument("lead_id")
@click.argument("note")
@click.option("--db-path", default=DEFAULT_DB_PATH, show_default=True)
def save_note(lead_id: str, note: str, db_path: str) -> None:
    """Attach or update an operator note for a lead_id."""
    store = SQLiteDataStore(db_path=db_path)
    try:
        store.upsert_lead_note(lead_id=lead_id, note=note)
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc
    finally:
        store.close()
    click.echo(f"saved note: {lead_id}")


@cli.command("review")
@click.option("--industry", default="", help="Case-insensitive industry/category filter.")
@click.option("--location", default="", help="Case-insensitive location filter.")
@click.option("--state", default="", help="State code filter (exact, case-insensitive).")
@click.option("--limit", default=50, show_default=True, type=int)
@click.option("--offset", default=0, show_default=True, type=int)
@click.option("--db-path", default=DEFAULT_DB_PATH, show_default=True)
def review(industry: str, location: str, state: str, limit: int, offset: int, db_path: str) -> None:
    """Show lightweight review context for a filtered lead set."""
    leads = _list_leads(
        industry=industry,
        location=location,
        state=state,
        limit=limit,
        offset=offset,
        db_path=db_path,
    )
    with_notes = sum(1 for lead in leads if lead.note.strip())
    business_count = sum(1 for lead in leads if lead.lead_type == "business")
    listing_count = sum(1 for lead in leads if lead.lead_type == "listing")

    click.echo(f"total_leads: {len(leads)}")
    click.echo(f"with_notes: {with_notes}")
    click.echo(f"without_notes: {len(leads) - with_notes}")
    click.echo(f"businesses: {business_count}")
    click.echo(f"listings: {listing_count}")

    if not leads:
        return

    click.echo("review_queue:")
    for lead in leads[:10]:
        status = "noted" if lead.note.strip() else "todo"
        click.echo(f"{lead.lead_id}\t{status}\t{lead.name}\t{lead.location}")


@cli.command("export")
@click.option("--industry", default="", help="Case-insensitive industry/category filter.")
@click.option("--location", default="", help="Case-insensitive location filter.")
@click.option("--state", default="", help="State code filter (exact, case-insensitive).")
@click.option("--limit", default=500, show_default=True, type=int)
@click.option("--offset", default=0, show_default=True, type=int)
@click.option(
    "--format",
    "export_format",
    default="csv",
    show_default=True,
    type=click.Choice(["csv", "json"], case_sensitive=False),
)
@click.option("--output", "output_path", required=True, type=click.Path(path_type=Path, dir_okay=False))
@click.option("--db-path", default=DEFAULT_DB_PATH, show_default=True)
def export(
    industry: str,
    location: str,
    state: str,
    limit: int,
    offset: int,
    export_format: str,
    output_path: Path,
    db_path: str,
) -> None:
    """Batch-export the filtered lead set to CSV or JSON."""
    leads = _list_leads(
        industry=industry,
        location=location,
        state=state,
        limit=limit,
        offset=offset,
        db_path=db_path,
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if export_format.lower() == "csv":
        _write_csv(output_path, leads)
    else:
        _write_json(output_path, leads)
    click.echo(f"exported {len(leads)} leads -> {output_path}")


def _list_leads(
    *, industry: str, location: str, state: str, limit: int, offset: int, db_path: str
) -> list[Lead]:
    store = SQLiteDataStore(db_path=db_path)
    try:
        return store.list_leads(
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


def _write_csv(path: Path, leads: list[Lead]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=EXPORT_FIELDS)
        writer.writeheader()
        for lead in leads:
            writer.writerow(_export_row(lead))


def _write_json(path: Path, leads: list[Lead]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        json.dump([_export_row(lead) for lead in leads], handle, indent=2, sort_keys=True)


def _export_row(lead: Lead) -> dict[str, object]:
    payload = lead.to_dict()
    return {field: payload.get(field) for field in EXPORT_FIELDS}


def _note_preview(note: str, max_chars: int = 48) -> str:
    compact = " ".join(note.split())
    if len(compact) <= max_chars:
        return compact
    return f"{compact[: max_chars - 3]}..."


if __name__ == "__main__":
    cli()
