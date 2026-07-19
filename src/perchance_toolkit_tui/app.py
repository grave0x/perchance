"""Textual-based TUI application."""

from __future__ import annotations

from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, Static, ListView, ListItem
from textual.containers import Vertical


class MainScreen(Screen):
    """Main screen with navigation to other screens."""

    def compose(self) -> ComposeResult:
        yield Header()
        yield Vertical(
            Static("perchance TUI", id="title"),
            ListView(
                ListItem(Static("Run Generator")),
                ListItem(Static("Search Generators")),
                ListItem(Static("Browse History")),
                ListItem(Static("Favorites")),
                ListItem(Static("Settings")),
                id="nav",
            ),
        )
        yield Footer()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        item_text = str(event.item.children[0])
        match item_text:
            case "Run Generator":
                self.app.push_screen("run")
            case "Search Generators":
                self.app.push_screen("search")
            case "Browse History":
                self.app.push_screen("history")
            case "Favorites":
                self.app.push_screen("history", {"favorites": True})  # type: ignore[call-overload]
            case "Settings":
                self.app.push_screen("settings")


class PerchanceTUI(App):
    """Main TUI application."""

    SCREENS = {"main": MainScreen}  # type: ignore[assignment]

    def on_mount(self) -> None:
        self.push_screen("main")


def main() -> None:
    app = PerchanceTUI()
    app.run()


if __name__ == "__main__":
    main()
