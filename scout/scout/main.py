"""Scout CLI - Bloomberg Terminal for SMB Acquisition"""

import click
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scout.shared.query_parser import parse_query
from scout import config
from scout.shared.errors import (
    format_error_message,
    handle_api_error,
    validate_api_key,
    ConfigurationError,
    ValidationError
)


@click.group()
def cli():
    """Scout - Terminal-based tool for researching small businesses"""
    pass


@cli.command()
@click.argument('query', required=True)
@click.option('--no-cache', is_flag=True, help='Bypass cache and fetch fresh data')
@click.option('--max-results', default=config.MAX_RESULTS_DEFAULT, help='Maximum number of businesses to fetch')
@click.option('--no-ui', is_flag=True, help='Disable terminal UI and just print results')
@click.option('--mock-data', is_flag=True, help='Use bundled mock data for UI iteration')
@click.option('--mock-data-path', type=click.Path(exists=True, dir_okay=False, path_type=Path), help='Path to mock data JSON')
def research(
    query: str,
    no_cache: bool,
    max_results: int,
    no_ui: bool,
    mock_data: bool,
    mock_data_path: Path | None,
):
    """
    Research a market by searching for businesses.

    Example: scout research "HVAC in Los Angeles"
    """
    try:
        # Validate API key is configured (skip for mock data)
        if not mock_data and not mock_data_path:
            try:
                validate_api_key(config.GOOGLE_MAPS_API_KEY, "Google Maps")
            except ConfigurationError as e:
                click.echo(format_error_message(e), err=True)
                click.echo("\nPlease add GOOGLE_MAPS_API_KEY to your .env file", err=True)
                sys.exit(1)

        # Parse query into industry and location
        try:
            industry, location = parse_query(query)
        except ValidationError as e:
            click.echo(format_error_message(e), err=True)
            sys.exit(1)

        # Launch terminal UI (default) or simple CLI mode
        if not no_ui:
            # Launch Rich terminal UI
            from scout.ui.terminal import ScoutTerminal
            from scout.shared.mock_data import load_mock_result

            initial_result = None
            if mock_data or mock_data_path:
                initial_result = load_mock_result(mock_data_path)

            terminal = ScoutTerminal(
                industry=industry,
                location=location,
                use_cache=not no_cache,
                max_results=max_results,
                initial_result=initial_result,
            )
            terminal.run()

        else:
            # Simple CLI mode (no terminal UI)
            click.echo(f"\n📊 Scout Market Research")
            click.echo(f"{'=' * 50}")
            click.echo(f"Industry:  {industry}")
            click.echo(f"Location:  {location}")
            click.echo(f"Max Results: {max_results}")
            click.echo(f"Use Cache: {not no_cache}")
            click.echo(f"{'=' * 50}\n")

            # Import here to avoid circular imports
            from scout.application.research_market import ResearchMarket
            from scout.shared.mock_data import load_mock_result

            # Fetch business data
            click.echo(f"🔍 Searching data sources for {industry} in {location}...")
            try:
                if mock_data or mock_data_path:
                    results = load_mock_result(mock_data_path)
                else:
                    use_case = ResearchMarket()
                    results = use_case.run(
                        industry=industry,
                        location=location,
                        max_results=max_results,
                        use_cache=not no_cache,
                        include_benchmarks=True,
                    )
            except ConnectionError:
                click.echo("\n❌ Error: Network connection failed", err=True)
                click.echo("   Please check your internet connection and try again", err=True)
                sys.exit(1)
            except Exception as e:
                api_error = handle_api_error(e, "Google Maps")
                click.echo(format_error_message(api_error), err=True)
                sys.exit(1)

            # Display results
            businesses = results.businesses
            total_found = len(businesses)

            click.echo(f"\n✅ Found {total_found} businesses\n")

            # Show first 10 businesses
            if businesses:
                click.echo("Top businesses:")
                click.echo("-" * 80)
                for i, biz in enumerate(businesses[:10], 1):
                    name = biz.name or 'N/A'
                    rating = biz.rating or 0.0
                    reviews = biz.reviews or 0
                    phone = biz.phone or 'N/A'
                    click.echo(f"{i:2d}. {name:40s} {rating:.1f}⭐ ({reviews} reviews) {phone}")

                if total_found > 10:
                    click.echo(f"\n... and {total_found - 10} more businesses")

            click.echo(f"\n💾 Results cached for {config.CACHE_TTL_DAYS} days")
            click.echo(f"📂 Use terminal UI (remove --no-ui flag) to export to CSV")

    except ConfigurationError as e:
        click.echo(format_error_message(e), err=True)
        sys.exit(1)
    except ValidationError as e:
        click.echo(format_error_message(e), err=True)
        sys.exit(1)
    except KeyboardInterrupt:
        click.echo("\n\n👋 Exiting Scout...", err=True)
        sys.exit(0)
    except Exception as e:
        click.echo(f"\n❌ Unexpected error: {e}", err=True)
        click.echo("\nIf this persists, please report this issue with the error details above.", err=True)
        sys.exit(1)


if __name__ == '__main__':
    cli()
