"""perchance list — browse history and favorites."""

from __future__ import annotations

import click
from rich.table import Table

from perchance_cli.formatting import console


@click.command()
@click.option("--favorites", is_flag=True, help="Show favorites only")
@click.option("--limit", default=20, help="Number of entries")
@click.pass_context
def list_cmd(ctx: click.Context, favorites: bool, limit: int) -> None:
    """List recent generations or favorites."""
    db = ctx.obj["db"]

    if favorites:
        rows = db.get_favorites()
    else:
        rows = db.get_history(limit=limit)

    if not rows:
        console.print("[yellow]No generations yet. Run 'perchance run' first.[/yellow]")
        return

    table = Table(title="Favorites" if favorites else "Recent Generations")
    table.add_column("ID", style="dim")
    table.add_column("Generator")
    table.add_column("Prompt", width=40)
    table.add_column("Created")
    table.add_column("Fav")

    for r in rows:
        created = r.created.strftime("%Y-%m-%d %H:%M") if r.created else "—"
        fav = "★" if r.favorite else " "
        table.add_row(r.id[:8], r.generator_title, r.prompt[:40], created, fav)

    console.print(table)
