"""High-level generator orchestration.

Wraps eeemoon/perchance generator calls and persists results to local DB.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from perchance_toolkit.models.generation import Generation
from perchance_toolkit.storage.db import Database, GenerationRow

if TYPE_CHECKING:
    from perchance_toolkit.api.client import PerchanceClient


class GeneratorRunner:
    """Orchestrates running a generator and saving results."""

    def __init__(self, client: PerchanceClient, db: Database) -> None:
        self._client = client
        self._db = db

    async def run(
        self,
        generator_id: str,
        prompt: str,
        seed: Optional[int] = None,
        save: bool = True,
        section_overrides: Optional[dict[str, str]] = None,
    ) -> Generation:
        """Run a generator and optionally persist the result.

        Supported generator IDs: ``ai-text-generator``, ``ai-image-generator``
        (or shorthand ``text`` / ``image``).
        """
        generation = await self._client.run_generator(
            generator_id, prompt, seed, section_overrides
        )
        if save:
            row = GenerationRow(
                id=generation.id,
                generator_id=generation.generator_id,
                generator_title=generation.generator_title,
                prompt=generation.prompt,
                output=generation.output,
                duration_ms=generation.duration_ms,
            )
            self._db.save_generation(row)
        return generation
