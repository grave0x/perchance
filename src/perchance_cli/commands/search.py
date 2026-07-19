"""perchance search — find generators."""

from __future__ import annotations

import asyncio

import click

from perchance.api.client import PerchanceClient
from perchance_cli.formatting import console, print_generator_list


@click.command()
@click.argument("query")
@click.option("--limit", default=20, help="Maximum results")
@click.pass_context
def search_cmd(ctx: click.Context, query: str, limit: int) -> None:
    """Search for generators matching QUERY."""
    async def _search() -> None:
        client = PerchanceClient()
        results = await client.search_generators(query, limit=limit)
        if results:
            print_generator_list(results, title=f'Results for "{query}"')
        else:
            console.print(f"[yellow]No generators found for '{query}'[/yellow]")
        await client.close()

    asyncio.run(_search())
