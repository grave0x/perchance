"""High-level generator orchestration."""

from __future__ import annotations

from typing import Optional

from perchance.api.client import PerchanceClient
from perchance.models.generation import Generation
from perchance.storage.db import Database, GenerationRow


class GeneratorRunner:
    """Orchestrates fetching generator metadata, executing, and saving results."""

    def __init__(self, client: PerchanceClient, db: Database) -> None:
        self._client = client
        self._db = db

    async def run(
        self,
        generator_id: str,
        prompt: str,
        seed: Optional[int] = None,
        save: bool = True,
    ) -> Generation:
        """Run a generator and optionally persist the result."""
        generation = await self._client.run_generator(generator_id, prompt, seed)
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
