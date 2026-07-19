"""Rich output formatting for the CLI."""

from __future__ import annotations

import base64
import logging
import os
import subprocess

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from rich.markdown import Markdown

from perchance_toolkit.models.generation import Generation, ExportFormat
from perchance_toolkit.models.generator import Generator, GeneratorSummary
from perchance_toolkit.models.search_result import GeneratorSearchResult

log = logging.getLogger(__name__)

console = Console()
_IS_KITTY = os.environ.get("TERM") == "xterm-kitty"
log.debug("_IS_KITTY=%s (TERM=%s)", _IS_KITTY, os.environ.get("TERM"))


def _render_image(data_uri: str) -> None:
    """Decode a ``data:image/...`` URI and display via Kitty graphics protocol."""
    if not data_uri.startswith("data:image/"):
        log.debug("_render_image: not an image URI, printing raw text")
        console.print(data_uri)
        return

    fmt, _, b64data = data_uri.partition(";base64,")
    raw = base64.b64decode(b64data)
    log.debug("_render_image: fmt=%s, size=%d bytes", fmt, len(raw))

    if _IS_KITTY:
        ret = subprocess.run(
            ["kitty", "+kitten", "icat", "--stdin", "yes", "--transfer-mode", "stream"],
            input=raw,
            capture_output=True,
        )
        log.debug("icat exit code=%d", ret.returncode)
        if ret.returncode != 0:
            _print_image_info(fmt, len(raw))
    else:
        _print_image_info(fmt, len(raw))


def _print_image_info(fmt: str, size: int) -> None:
    """Print image metadata as fallback when terminal can't render."""
    ext = fmt.split("/")[-1]  # "png", "jpeg", etc.
    console.print(f"[dim]Image ({ext}, {size / 1024:.0f} KB)[/dim]")


def print_generation(gen: Generation, fmt: ExportFormat = ExportFormat.text) -> None:
    """Render a generation result to the console."""
    # Auto-detect image output
    if gen.output.startswith("data:image/"):
        if gen.prompt:
            console.print(f"[bold]{gen.generator_title}[/bold] — {gen.prompt}")
        elif gen.seed is not None:
            console.print(f"[bold]{gen.generator_title}[/bold] (seed {gen.seed})")
        _render_image(gen.output)
        return

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


def print_search_results(
    results: list[GeneratorSearchResult], query: str
) -> None:
    """Render search results as a table."""
    if not results:
        console.print(f"[yellow]No generators found for '{query}'[/yellow]")
        return

    table = Table(title=f"Search results for '{query}'")
    table.add_column("Name", style="cyan")
    table.add_column("Title")
    table.add_column("Views", justify="right", style="dim")
    table.add_column("Description")
    for r in results[:20]:
        desc = (r.description[:80] + "…") if len(r.description) > 80 else r.description
        table.add_row(r.name, r.title or "—", str(r.views), desc or "—")
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
