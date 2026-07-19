"""Generator detail view screen."""

from __future__ import annotations

from textual.screen import Screen
from textual.app import ComposeResult
from textual.widgets import Header, Footer, Static
from textual.containers import ScrollableContainer


class GeneratorDetailScreen(Screen):
    """View generator details and run it."""

    def compose(self) -> ComposeResult:
        yield Header()
        yield ScrollableContainer(Static(id="detail_content"))
        yield Footer()
