"""perchance info — show a generator's input sections without running."""

from __future__ import annotations

import click
from rich.console import Console
from rich.table import Table
from rich.text import Text

from perchance_toolkit.api.client import PerchanceClient
from perchance_toolkit.core.perchance_engine import _parse_model
from perchance_toolkit_cli.commands.run import _classify_sections

console = Console()


@click.command()
@click.argument("generator_id")
def info_cmd(generator_id: str) -> None:
    """Show input sections available for a generator.

    This is a read-only preview — sections are classified by type
    (text / int / dropdown / fileUpload) with their current defaults.
    """
    client = PerchanceClient()

    data = client._engine.fetch_data(generator_id)
    sections, _ = _parse_model(data.get("modelText", ""))
    fields = _classify_sections(sections)

    table = Table(
        title=f"Inputs for [bold cyan]{generator_id}[/bold cyan]",
        title_style="",
        border_style="blue",
        show_header=True,
        header_style="bold white",
        box=None,
    )
    table.add_column("Section", style="bold cyan", no_wrap=True)
    table.add_column("Type", width=12)
    table.add_column("Default")
    table.add_column("Choices", style="dim")

    for f in fields:
        type_tag = {
            "text": "[dim]text[/dim]",
            "int": "[yellow]int[/yellow]",
            "dropdown": "[green]dropdown[/green]",
            "fileUpload": "[magenta]file[/magenta]",
        }.get(f["type"], "[dim]text[/dim]")

        default = (f["default"][:60] if f["default"] else "—") or "—"
        choices = ""
        if f["type"] == "dropdown" and f["choices"]:
            n = len(f["choices"])
            choices = f"{n} option{'s' if n != 1 else ''}"

        table.add_row(
            Text(f["name"]),
            Text(type_tag),
            Text(default[:60], style="dim" if default else ""),
            Text(choices),
        )

    console.print()
    console.print(table)
    console.print()
    console.print("[dim]Run [bold]perchance run[/bold] to execute with custom inputs[/dim]")
