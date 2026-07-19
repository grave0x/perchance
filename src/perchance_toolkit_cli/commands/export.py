"""perchance export — save generations to files."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import click

from perchance_toolkit.models.generation import ExportFormat, Generation
from perchance_toolkit_cli.formatting import console


@click.command()
@click.argument("generation_id")
@click.option(
    "--format",
    "fmt",
    type=click.Choice(["text", "json", "html", "markdown"]),
    default="markdown",
    help="Output format",
)
@click.option("--output", "-o", type=click.Path(path_type=Path), help="Output path")
@click.pass_context
def export_cmd(
    ctx: click.Context,
    generation_id: str,
    fmt: str,
    output: Optional[Path],
) -> None:
    """Export a generation to a file."""
    db = ctx.obj["db"]
    rows = db.get_history(limit=1000)
    match = [r for r in rows if r.id.startswith(generation_id)]

    if not match:
        console.print(f"[red]Generation '{generation_id}' not found.[/red]")
        return

    row = match[0]
    gen = _row_to_generation(row)
    export_fmt = ExportFormat(fmt)

    from perchance_toolkit.core.export import ExportService
    svc = ExportService()
    path = svc.export(gen, path=output, fmt=export_fmt)
    console.print(f"[green]Exported to {path}[/green]")


def _row_to_generation(row) -> Generation:
    from datetime import datetime, timezone
    return Generation(
        id=row.id,
        generator_id=row.generator_id,
        generator_title=row.generator_title,
        prompt=row.prompt,
        output=row.output,
        created=row.created or datetime.now(timezone.utc),
        favorite=row.favorite,
    )
