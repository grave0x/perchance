"""perchance CLI entry point."""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import Optional

import click

from perchance_toolkit import __version__
from perchance_toolkit.storage.db import Database
from perchance_toolkit.storage.config import ConfigManager
from perchance_toolkit_cli.commands.run import run_cmd
from perchance_toolkit_cli.commands.search import search_cmd
from perchance_toolkit_cli.commands.list import list_cmd
from perchance_toolkit_cli.commands.export import export_cmd
from perchance_toolkit_cli.commands.auth import auth_cmd
from perchance_toolkit_cli.commands.config import config_cmd
from perchance_toolkit_cli.commands.info import info_cmd


@click.group()
@click.version_option(version=__version__, prog_name="perchance-toolkit")
@click.option("--db", "db_path", envvar="PERCHANCE_DB", help="Path to SQLite database")
@click.option("--config", "config_path", help="Path to config file")
@click.option("--verbose", "-v", is_flag=True, help="Enable debug/trace logging")
@click.pass_context
def cli(ctx: click.Context, db_path: Optional[str], config_path: Optional[str],
        verbose: bool) -> None:
    """Interact with perchance.org from the command line."""
    level = logging.DEBUG if verbose else logging.WARNING
    logging.basicConfig(
        level=level,
        format="%(levelname).1s %(name)s %(message)s",
    )
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
cli.add_command(info_cmd, "info")


def main() -> None:
    """Async wrapper for the CLI entry point."""
    asyncio.run(cli())  # type: ignore[arg-type]


if __name__ == "__main__":
    main()
