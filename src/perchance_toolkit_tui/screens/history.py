"""History and favorites screen."""

from __future__ import annotations

from textual.screen import Screen
from textual.app import ComposeResult
from textual.widgets import Header, Footer, ListView, Static
from textual.containers import Vertical


class HistoryScreen(Screen):
    """Display generation history or favorites."""

    def compose(self) -> ComposeResult:
        is_favorites = self.name == "favorites"
        title = "Favorites" if is_favorites else "Generation History"
        yield Header()
        yield Vertical(
            Static(title, id="title"),
            ListView(id="history_list"),
        )
        yield Footer()

    def on_mount(self) -> None:
        """Load history or favorites from DB."""
        from perchance_toolkit.storage.db import Database
        from textual.widgets import ListItem, Label

        is_favorites = self.name == "favorites"
        db = Database()
        rows = db.get_favorites() if is_favorites else db.get_history(limit=50)

        list_view = self.query_one("#history_list", ListView)
        list_view.clear()
        for r in rows:
            label = f"{r.generator_title}: {r.prompt[:60]}"
            list_view.append(ListItem(Label(label)))
