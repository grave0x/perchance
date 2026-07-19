from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class GeneratorSummary(BaseModel):
    """Lightweight reference returned from search/list endpoints."""

    id: str
    title: str
    author: str
    description: str = ""
    tags: list[str] = Field(default_factory=list)
    thumbnail_url: Optional[str] = None
    created: Optional[datetime] = None
    updated: Optional[datetime] = None


class Generator(GeneratorSummary):
    """Full generator including source and metadata."""

    source: str = ""
    version: int = 1
    power_ups: list[str] = Field(default_factory=list)
    plugin_deps: list[str] = Field(default_factory=list)
    is_remix: bool = False
    remix_of: Optional[str] = None
    stats: dict[str, int] = Field(default_factory=dict)
