"""CSS theme management for the GUI."""

from __future__ import annotations

from pathlib import Path


class ThemeManager:
    """Load and apply Qt stylesheets from theme files."""

    THEMES_DIR = Path(__file__).parent / "themes"

    def __init__(self, theme_name: str = "dark") -> None:
        self._theme_name = theme_name

    @property
    def stylesheet(self) -> str:
        path = self.THEMES_DIR / f"{self._theme_name}.qss"
        if path.exists():
            return path.read_text()
        return ""
