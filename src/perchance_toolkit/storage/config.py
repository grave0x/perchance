"""YAML-based configuration management."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

import yaml

DEFAULT_CONFIG: dict[str, Any] = {
    "theme": "dark",
    "default_export": "text",
    "max_history": 200,
    "api_timeout": 30,
    "tui": {"show_line_numbers": True, "vim_mode": False},
    "gui": {"window_width": 1200, "window_height": 800},
}


class ConfigManager:
    """Read/write user config at ~/.config/perchance/config.yaml."""

    def __init__(self, path: Optional[Path] = None) -> None:
        if path is None:
            path = Path.home() / ".config" / "perchance-toolkit" / "config.yaml"
        self._path = path
        self._data: dict[str, Any] = {}
        self._load()

    def _load(self) -> None:
        if self._path.exists():
            raw = self._path.read_text()
            self._data = yaml.safe_load(raw) or {}
        else:
            self._data = dict(DEFAULT_CONFIG)
            self._save()

    def _save(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(yaml.dump(self._data, default_flow_style=False))

    def get(self, key: str, default: Any = None) -> Any:
        """Get a config value by dot-separated key (e.g. 'tui.vim_mode')."""
        parts = key.split(".")
        val: Any = self._data
        for part in parts:
            if isinstance(val, dict):
                val = val.get(part)
            else:
                return default
            if val is None:
                return default
        return val

    def set(self, key: str, value: Any) -> None:
        """Set a config value by dot-separated key."""
        parts = key.split(".")
        target = self._data
        for part in parts[:-1]:
            if part not in target:
                target[part] = {}
            target = target[part]
        target[parts[-1]] = value
        self._save()

    @property
    def all(self) -> dict[str, Any]:
        return dict(self._data)
