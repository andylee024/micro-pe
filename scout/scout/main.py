"""Scout CLI for pipeline execution and app-layer lead operations."""

from __future__ import annotations

from pathlib import Path

import click

from scout.app.service import ScoutAppService
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
    service = ScoutAppService()
    try:
        execution = service.run_search(
            query_text=query,
            industry=industry,
            location=location,
            max_results=max_results,
            use_cache=not no_cache,
        )
    except Exception as exc:  # noqa: BLE001
        raise click.ClickException(str(exc)) from exc
    finally:
        service.close()

    dataset = execution.dataset

    click.echo(f"search_id: {execution.search.search_id}")
    click.echo(f"search_run_id: {execution.search_run.run_id}")
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


@cli.group("lead")
def lead_group() -> None:
    """Lead persistence operations for the latest or selected search."""


@lead_group.command("list")
@click.option("--search-id", default=None, help="Search id. Defaults to latest search.")
@click.option("--saved-only", is_flag=True, default=False, help="Only return saved leads.")
@click.option("--limit", default=50, show_default=True, type=int)
def list_leads(search_id: str | None, saved_only: bool, limit: int) -> None:
    """List discovered leads for a persisted search run."""
    service = ScoutAppService()
    try:
        leads = service.list_leads(search_id=search_id, saved_only=saved_only, limit=limit)
    except Exception as exc:  # noqa: BLE001
        raise click.ClickException(str(exc)) from exc
    finally:
        service.close()

    click.echo(f"leads: {len(leads)}")
    for lead in leads:
        status = "saved" if lead.is_saved else "discovered"
        click.echo(
            f"id={lead.lead_id} status={status} name={lead.name} "
            f"source={lead.source} location={lead.location}"
        )


@lead_group.command("save")
@click.argument("lead_id")
@click.option("--search-id", default=None, help="Search id. Defaults to latest search.")
@click.option("--note", default="", help="Optional note for the saved lead.")
@click.option("--summary", default="", help="Optional summary for the saved lead.")
def save_lead(lead_id: str, search_id: str | None, note: str, summary: str) -> None:
    """Save one discovered lead into curated lead state."""
    service = ScoutAppService()
    try:
        lead = service.save_lead(lead_id=lead_id, search_id=search_id, note=note, summary=summary)
    except Exception as exc:  # noqa: BLE001
        raise click.ClickException(str(exc)) from exc
    finally:
        service.close()

    click.echo(f"saved lead_id={lead.lead_id} name={lead.name}")


@lead_group.command("remove")
@click.argument("lead_id")
def remove_lead(lead_id: str) -> None:
    """Remove one curated lead without rerunning pipeline ingestion."""
    service = ScoutAppService()
    try:
        removed = service.remove_lead(lead_id=lead_id)
    except Exception as exc:  # noqa: BLE001
        raise click.ClickException(str(exc)) from exc
    finally:
        service.close()

    if not removed:
        raise click.ClickException(f"lead_id '{lead_id}' is not saved")
    click.echo(f"removed lead_id={lead_id}")


@cli.command("export-leads")
@click.option("--search-id", default=None, help="Search id filter. Defaults to all saved leads.")
@click.option("--output", default="-", help="Output path or '-' for stdout.")
def export_leads(search_id: str | None, output: str) -> None:
    """Export curated leads from the app service boundary as CSV."""
    service = ScoutAppService()
    try:
        csv_text = service.export_saved_leads_csv(search_id=search_id)
    except Exception as exc:  # noqa: BLE001
        raise click.ClickException(str(exc)) from exc
    finally:
        service.close()

    if output == "-":
        click.echo(csv_text.rstrip("\n"))
        return

    destination = Path(output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(csv_text, encoding="utf-8")
    click.echo(f"wrote: {destination}")


if __name__ == "__main__":
    cli()
