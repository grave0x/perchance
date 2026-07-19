"""perchance config — view and modify settings."""

from __future__ import annotations

from typing import Optional

import click
from rich.table import Table

from perchance_toolkit_cli.formatting import console


@click.group()
def config_cmd() -> None:
    """View or modify configuration."""


@config_cmd.command()
@click.argument("key", required=False)
def get(key: Optional[str] = None) -> None:
    """Show configuration value(s)."""
    from perchance_toolkit.storage.config import ConfigManager

    cfg = ConfigManager()
    if key:
        val = cfg.get(key)
        if val is None:
            console.print(f"[yellow]Key '{key}' not found[/yellow]")
        else:
            console.print(f"{key}: {val}")
    else:
        table = Table(title="Configuration")
        table.add_column("Key")
        table.add_column("Value")
        for k, v in _flatten(cfg.all):
            table.add_row(k, str(v))
        console.print(table)


@config_cmd.command()
@click.argument("key")
@click.argument("value")
def set(key: str, value: str) -> None:
    """Set a configuration value."""
    from perchance_toolkit.storage.config import ConfigManager

    cfg = ConfigManager()
    # Attempt type coercion
    coerced: object = value
    if value.lower() in ("true", "false"):
        coerced = value.lower() == "true"
    else:
        try:
            coerced = int(value)
        except ValueError:
            try:
                coerced = float(value)
            except ValueError:
                pass
    cfg.set(key, coerced)
    console.print(f"[green]Set {key} = {coerced}[/green]")


def _flatten(d: dict, prefix: str = "") -> list[tuple[str, str]]:
    items: list[tuple[str, str]] = []
    for k, v in d.items():
        key = f"{prefix}.{k}" if prefix else k
        if isinstance(v, dict):
            items.extend(_flatten(v, key))
        else:
            items.append((key, str(v)))
    return items
