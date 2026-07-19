"""perchance CLI entry point."""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Optional

import click

from perchance import __version__
from perchance.storage.db import Database
from perchance.storage.config import ConfigManager
from perchance_cli.commands.run import run_cmd
from perchance_cli.commands.search import search_cmd
from perchance_cli.commands.list import list_cmd
from perchance_cli.commands.export import export_cmd
from perchance_cli.commands.auth import auth_cmd
from perchance_cli.commands.config import config_cmd


@click.group()
@click.version_option(version=__version__, prog_name="perchance")
@click.option("--db", "db_path", envvar="PERCHANCE_DB", help="Path to SQLite database")
@click.option("--config", "config_path", help="Path to config file")
@click.pass_context
def cli(ctx: click.Context, db_path: Optional[str], config_path: Optional[str]) -> None:
    """Interact with perchance.org from the command line."""
    ctx.ensure_object(dict)
    ctx.obj["config"] = ConfigManager(path=Path(config_path) if config_path else None)
    ctx.obj["db"] = Database(path=Path(db_path) if db_path else None)


# Register subcommands
cli.add_command(run_cmd, "run")
cli.add_command(search_cmd, "search")
cli.add_command(list_cmd, "list")
cli.add_command(export_cmd, "export")
cli.add_command(auth_cmd, "auth")
cli.add_command(config_cmd, "config")


def main() -> None:
    """Async wrapper for the CLI entry point."""
    asyncio.run(cli())  # type: ignore[arg-type]


if __name__ == "__main__":
    main()
