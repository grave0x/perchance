from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field


class GeneratorSearchResult(BaseModel):
    """Result from the perchance.org generator search API."""

    name: str
    title: str = ""
    description: str = ""
    views: int = 0
    last_edit: Optional[datetime] = None
    tags: list[str] = Field(default_factory=list)
    image_url: Optional[str] = None

    @classmethod
    def from_api(cls, raw: dict) -> GeneratorSearchResult:
        """Build from the API JSON blob."""
        meta: dict = raw.get("metaData") or {}
        edit_ts = raw.get("lastEditTime")
        dt = None
        if edit_ts:
            dt = datetime.fromtimestamp(edit_ts / 1000, tz=timezone.utc)

        return cls(
            name=raw.get("name", ""),
            title=meta.get("title", "") or "",
            description=meta.get("description", "") or "",
            views=raw.get("views", 0),
            last_edit=dt,
            tags=meta.get("tags", []),
            image_url=meta.get("image") or None,
        )
