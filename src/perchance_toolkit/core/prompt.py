"""Prompt history and template management."""

from __future__ import annotations


from perchance_toolkit.storage.db import Database


class PromptManager:
    """Manages prompt history, templates, and autocomplete suggestions."""

    def __init__(self, db: Database) -> None:
        self._db = db

    def recent_prompts(self, limit: int = 20) -> list[str]:
        """Return the most recently used prompts, deduplicated."""
        history = self._db.get_history(limit=limit * 3)
        seen: set[str] = set()
        prompts: list[str] = []
        for row in history:
            if row.prompt not in seen:
                seen.add(row.prompt)  # type: ignore[arg-type]
                prompts.append(row.prompt)  # type: ignore[arg-type]
                if len(prompts) >= limit:
                    break
        return prompts
