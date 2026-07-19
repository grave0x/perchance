from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class ExportFormat(str, Enum):
    text = "text"
    json = "json"
    html = "html"
    markdown = "markdown"


class Generation(BaseModel):
    """A single generation result from running a generator."""

    id: str
    generator_id: str
    generator_title: str
    prompt: str
    output: str
    created: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    power_ups_used: list[str] = Field(default_factory=list)
    seed: Optional[int] = None
    duration_ms: Optional[int] = None
    favorite: bool = False
    tags: list[str] = Field(default_factory=list)

    def to_export(self, fmt: ExportFormat) -> str:
        """Render generation in the requested export format."""
        match fmt:
            case ExportFormat.text:
                return self.output
            case ExportFormat.json:
                return self.model_dump_json(indent=2)
            case ExportFormat.markdown:
                return (
                    f"# {self.generator_title}\n\n"
                    f"**Prompt:** {self.prompt}\n\n"
                    f"{self.output}\n"
                )
            case ExportFormat.html:
                return f"<h1>{self.generator_title}</h1><p>{self.output}</p>"
