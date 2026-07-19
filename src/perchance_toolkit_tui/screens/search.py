"""Generator search screen."""

from __future__ import annotations

from textual.screen import Screen
from textual.app import ComposeResult
from textual.widgets import Header, Footer, Input, ListView
from textual.containers import Vertical


class SearchScreen(Screen):
    """Search for generators."""

    def compose(self) -> ComposeResult:
        yield Header()
        yield Vertical(
            Input(placeholder="Search generators...", id="search_input"),
            ListView(id="results"),
        )
        yield Footer()
