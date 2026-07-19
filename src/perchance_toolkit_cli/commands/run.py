"""perchance run — execute a generator."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.prompt import IntPrompt, Prompt
from rich.table import Table
from rich.text import Text

from perchance_toolkit.api.client import PerchanceClient
from perchance_toolkit.core.generator import GeneratorRunner
from perchance_toolkit_cli.formatting import print_generation

log = logging.getLogger(__name__)
console = Console()
CONFIG_DIR = Path.home() / ".perchance" / "generators"


# -- Helpers -----------------------------------------------------------------


def _load_config(gen_id: str) -> dict | None:
    path = CONFIG_DIR / f"{gen_id}.config.yaml"
    if path.exists():
        import yaml

        with open(path) as f:
            return yaml.safe_load(f)
    return None


def _save_config(gen_id: str, data: dict) -> None:
    import yaml

    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    path = CONFIG_DIR / f"{gen_id}.config.yaml"
    with open(path, "w") as f:
        yaml.dump(data, f, default_flow_style=False)


# -- Input-type detection ----------------------------------------------------

InputField = dict[str, Any]
"""Keys: name, type, default, choices (for dropdown)."""


def _is_displayable_text(text: str) -> bool:
    """Check if a text value is user-facing (not template/expression code)."""
    t = text.strip()
    if not t:
        return False
    # Skip if it contains bracket expressions like [method.call] or [a][b]
    if "[" in t or "]" in t:
        return False
    # Skip bare brace expressions like {1-6}
    if t.startswith("{") and t.endswith("}"):
        return False
    return True


def _classify_sections(sections: dict) -> list[InputField]:
    """Infer input fields from parsed sections."""
    fields: list[InputField] = []
    for name, items in sections.items():
        if name in ("output", "$output"):
            log.debug("  skip %r: reserved name", name)
            continue
        if len(items) > 20:
            log.debug("  skip %r: %d items (large pool)", name, len(items))
            continue
        if all(it["kind"] in ("import", "expr") for it in items):
            log.debug("  skip %r: all import/expr items", name)
            continue

        # Only consider displayable text items as user-visible choices
        displayable = [it for it in items if it["kind"] == "text" and _is_displayable_text(it["text"])]
        if not displayable:
            log.debug("  skip %r: 0 displayable items (of %d)", name, len(items))
            continue

        field: InputField = {"name": name, "type": "text", "default": "", "choices": None}

        if len(displayable) == 1:
            val = displayable[0]["text"]
            # int detection
            if val.strip().lstrip("-").isdigit():
                field["type"] = "int"
                field["default"] = val.strip()
                log.debug("  field %r: int, default=%s", name, val)
            elif _looks_like_file(val):
                field["type"] = "fileUpload"
                field["default"] = val.strip()
                log.debug("  field %r: fileUpload, default=%s", name, val)
            else:
                field["default"] = val.strip()
                log.debug("  field %r: text, default=%s", name, val)
        else:
            # Multiple items → dropdown
            field["type"] = "dropdown"
            field["choices"] = [it["text"] for it in displayable]
            field["default"] = displayable[0]["text"] if displayable else ""
            log.debug("  field %r: dropdown, %d choices", name, len(field["choices"]))

        fields.append(field)
    log.debug("_classify_sections: %d fields from %d sections", len(fields), len(sections))
    return fields


def _looks_like_file(val: str) -> bool:
    ext = Path(val.strip()).suffix.lower()
    return ext in (
        ".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp",
        ".svg", ".ico", ".pdf", ".txt", ".json", ".yaml", ".csv",
    )


# -- Interactive input widget ------------------------------------------------


def _prompt_text(field: InputField) -> str:
    label = f"[bold]{field['name']}[/bold] [dim](text)[/dim]"
    default: str = field.get("default", "") or ""
    return str(Prompt.ask(label, default=default or None))


def _prompt_int(field: InputField) -> str:
    label = f"[bold]{field['name']}[/bold] [dim](int)[/dim]"
    default = int(field["default"]) if field.get("default") else None
    val = IntPrompt.ask(label, default=default)
    return str(val)


def _prompt_dropdown(field: InputField) -> str:
    name = field["name"]
    choices = field["choices"] or []
    console.print()
    console.print(f"[bold]{name}[/bold] [dim](dropdown — pick one)[/dim]")
    for i, opt in enumerate(choices, 1):
        marker = "▸" if opt == field["default"] else " "
        console.print(f"  {marker} [cyan]{i}[/cyan]) {opt}")
    console.print("  [dim]0) Type custom value[/dim]")
    while True:
        raw = str(Prompt.ask(f"  Choice [1-{len(choices)}]", default=""))
        if not raw:
            return str(field.get("default", ""))
        try:
            idx = int(raw)
        except ValueError:
            return raw  # treat as custom text
        if idx == 0:
            return str(Prompt.ask("  Custom value"))
        if 1 <= idx <= len(choices):
            return str(choices[idx - 1])
        console.print(f"  [red]Pick 1–{len(choices)}[/red]")


def _prompt_file(field: InputField) -> str:
    label = f"[bold]{field['name']}[/bold] [dim](file path)[/dim]"
    default: str = field.get("default", "") or ""
    return str(Prompt.ask(label, default=default or None))


# -- Main interactive loop ---------------------------------------------------


def _interactive_prompt(gen_id: str, sections: dict) -> dict[str, str]:
    """Show typed interactive form for all input sections.

    Returns ``{section_name: value}`` overrides.
    """
    cfg = _load_config(gen_id) or {}
    log.debug("_interactive_prompt: loaded config for '%s': %s", gen_id, cfg)
    fields = _classify_sections(sections)

    if not fields:
        # Fallback: just ask for a prompt
        log.debug("_interactive_prompt: no fields, falling back to freeform prompt")
        prompt = cfg.get("prompt", "")
        val = Prompt.ask(
            f"[bold]Prompt[/bold] for [cyan]{gen_id}[/cyan]",
            default=prompt or None,
        )
        _save_config(gen_id, {"prompt": str(val), "interactive": True})
        return {"input": str(val)}

    # Show header
    grid = Table.grid(padding=(0, 2))
    grid.add_column(style="bold cyan", no_wrap=True)
    grid.add_column(style="dim", width=12)
    grid.add_column()
    for f in fields:
        type_tag = {
            "text": "[dim]text[/dim]",
            "int": "[yellow]int[/yellow]",
            "dropdown": "[green]dropdown[/green]",
            "fileUpload": "[magenta]file[/magenta]",
        }.get(f["type"], "[dim]text[/dim]")
        default_display = f["default"] or "—"
        if f["type"] == "dropdown":
            default_display += f"  [dim]({len(f['choices'])} opts)[/dim]"
        row = [
            Text(f["name"]),
            Text(type_tag),
            Text(default_display, style="dim"),
        ]
        grid.add_row(*row)

    console.print()
    console.print(
        Panel(
            grid,
            title=f"[bold]Inputs[/bold] — [cyan]{gen_id}[/cyan]",
            border_style="blue",
        )
    )

    # Prompt for each field
    overrides: dict[str, str] = {}
    for f in fields:
        prompt_handlers = {
            "text": _prompt_text,
            "int": _prompt_int,
            "dropdown": _prompt_dropdown,
            "fileUpload": _prompt_file,
        }
        handler = prompt_handlers.get(f["type"], _prompt_text)
        val = handler(f)
        overrides[f["name"]] = val

    # Save to config
    _save_config(gen_id, {
        **overrides,
        "interactive": True,
        "last_run": datetime.now(timezone.utc).isoformat(),
    })

    return overrides


# -- CLI command --------------------------------------------------------------


def _fetch_sections(client: PerchanceClient, gen_id: str) -> dict:
    """Fetch generator data and parse sections."""
    from perchance_toolkit.core.perchance_engine import _parse_model

    log.debug("Fetching sections for '%s'", gen_id)
    data = client._engine.fetch_data(gen_id)
    model_len = len(data.get("modelText", ""))
    log.debug("Fetched %d chars of modelText for '%s'", model_len, gen_id)
    sections, _ = _parse_model(data.get("modelText", ""))
    log.debug("Parsed %d sections for '%s'", len(sections), gen_id)
    return sections


@click.command()
@click.argument("generator_id")
@click.argument("prompt", required=False, default=None)
@click.option("--seed", type=int, help="Random seed for reproducible output")
@click.option("--no-save", is_flag=True, help="Skip saving to history")
@click.option("--interactive", "-i", is_flag=True, help="Force interactive mode")
@click.pass_context
def run_cmd(
    ctx: click.Context,
    generator_id: str,
    prompt: str | None,
    seed: Optional[int],
    no_save: bool,
    interactive: bool,
) -> None:
    """Run a generator.

    If PROMPT is omitted (or --interactive is passed), you'll be prompted
    interactively for each input section.  Values are saved to
    ~/.perchance/generators/<id>.config.yaml for reuse.
    """
    prompt_text = prompt or ""

    async def _run() -> None:
        nonlocal prompt_text
        client = PerchanceClient()

        # Interactive mode: detect sections, prompt for each
        section_overrides: dict[str, str] | None = None
        if not prompt_text or interactive:
            sections = _fetch_sections(client, generator_id)
            section_overrides = _interactive_prompt(generator_id, sections)
            prompt_text = section_overrides.get("input", prompt_text or "")

        runner = GeneratorRunner(client, ctx.obj["db"])
        gen = await runner.run(
            generator_id,
            prompt_text,
            seed,
            save=not no_save,
            section_overrides=section_overrides,
        )
        print_generation(gen)
        await client.close()

    log.debug("run_cmd: generator=%r, prompt=%r, seed=%s, interactive=%s, no_save=%s",
              generator_id, prompt, seed, interactive, no_save)

    import asyncio

    asyncio.run(_run())
