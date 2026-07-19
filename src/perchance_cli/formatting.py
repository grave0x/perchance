"""Rich output formatting for the CLI."""

from __future__ import annotations

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from rich.markdown import Markdown

from perchance.models.generation import Generation, ExportFormat
from perchance.models.generator import Generator, GeneratorSummary

console = Console()


def print_generation(gen: Generation, fmt: ExportFormat = ExportFormat.text) -> None:
    """Render a generation result to the console."""
    match fmt:
        case ExportFormat.text:
            console.print(Panel(gen.output, title=gen.generator_title))
        case ExportFormat.markdown:
            console.print(Markdown(gen.to_export(ExportFormat.markdown)))
        case ExportFormat.json:
            console.print(Syntax(gen.to_export(ExportFormat.json), "json"))
        case ExportFormat.html:
            console.print(gen.to_export(ExportFormat.html))


def print_generator_list(
    generators: list[GeneratorSummary], title: str = "Generators"
) -> None:
    """Render a list of generators as a table."""
    table = Table(title=title)
    table.add_column("ID", style="dim")
    table.add_column("Title")
    table.add_column("Author")
    table.add_column("Tags")
    for g in generators:
        table.add_row(g.id, g.title, g.author, ", ".join(g.tags[:3]))
    console.print(table)


def print_generator_detail(gen: Generator) -> None:
    """Render full generator details."""
    console.print(f"[bold]{gen.title}[/bold] by {gen.author}")
    console.print(f"ID: {gen.id}")
    console.print(f"Version: {gen.version}")
    if gen.tags:
        console.print(f"Tags: {', '.join(gen.tags)}")
    if gen.description:
        console.print(Panel(gen.description, title="Description"))
    if gen.source:
        console.print(Panel(Syntax(gen.source, "javascript"), title="Source"))
