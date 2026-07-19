"""History and favorites screen."""

from __future__ import annotations

from textual.screen import Screen
from textual.app import ComposeResult
from textual.widgets import Header, Footer, ListView, Static
from textual.containers import Vertical


class HistoryScreen(Screen):
    """Display generation history."""

    def compose(self) -> ComposeResult:
        yield Header()
        yield Vertical(
            Static("Generation History", id="title"),
            ListView(id="history_list"),
        )
        yield Footer()
