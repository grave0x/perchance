"""perchance search — find generators on perchance.org."""

from __future__ import annotations

import click

from perchance_toolkit.core.perchance_engine import PerchanceEngine
from perchance_toolkit.models.search_result import GeneratorSearchResult
from perchance_toolkit_cli.formatting import console, print_search_results


@click.command()
@click.argument("query")
@click.option("--limit", default=20, help="Maximum results")
@click.pass_context
def search_cmd(ctx: click.Context, query: str, limit: int) -> None:
    """Search for generators matching QUERY on perchance.org."""
    # Stateless search — create engine directly (no client overhead)
    engine = PerchanceEngine()
    try:
        raw_results = engine.search(query, limit=limit)
    except Exception as e:
        console.print(f"[red]Search failed: {e}[/red]")
        return

    results = [GeneratorSearchResult.from_api(r) for r in raw_results]
    print_search_results(results, query)
