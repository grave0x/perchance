"""Settings screen."""

from __future__ import annotations

from textual.screen import Screen
from textual.app import ComposeResult
from textual.widgets import Header, Footer, Static
from textual.containers import Vertical


class SettingsScreen(Screen):
    """Application settings."""

    def compose(self) -> ComposeResult:
        yield Header()
        yield Vertical(Static("Settings", id="title"))
        yield Footer()
