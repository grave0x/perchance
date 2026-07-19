"""perchance auth — login, logout, status."""

from __future__ import annotations

import asyncio

import click

from perchance.api.auth import AuthManager
from perchance_cli.formatting import console


@click.group()
def auth_cmd() -> None:
    """Manage perchance.org authentication."""


@auth_cmd.command()
@click.argument("username")
@click.password_option()
def login(username: str, password: str) -> None:
    """Log in to perchance.org."""
    async def _login() -> None:
        auth = AuthManager()
        user = await auth.login(username, password)
        console.print(f"[green]Logged in as {user.username}[/green]")

    asyncio.run(_login())


@auth_cmd.command()
def logout() -> None:
    """Log out and clear session."""
    async def _logout() -> None:
        auth = AuthManager()
        await auth.logout()
        console.print("[green]Logged out[/green]")

    asyncio.run(_logout())


@auth_cmd.command()
def status() -> None:
    """Show authentication status."""
    async def _status() -> None:
        auth = AuthManager()
        user = auth.current_user
        if auth.is_authenticated:
            console.print(f"[green]Authenticated as {user.username}[/green]")
        else:
            console.print("[yellow]Not logged in[/yellow]")

    asyncio.run(_status())
