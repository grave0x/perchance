"""Client wrapping eeemoon/perchance AI generators + custom user generators."""

from __future__ import annotations

import asyncio
from typing import Optional

from perchance import ImageGenerator, TextGenerator

from perchance_toolkit.core.perchance_engine import PerchanceEngine
from perchance_toolkit.models.generation import Generation
from perchance_toolkit.models.generator import Generator, GeneratorSummary


class PerchanceClient:
    """Access perchance.org generators — both AI and user-created.

    Two backends:
    - ``ai-text-generator`` / ``ai-image-generator`` → eeemoon/perchance
      (Playwright-based, hits internal API endpoints).
    - Any other ``generator_id`` → PerchanceEngine
      (pure-Python template evaluator, fetches data via curl_cffi).
    """

    def __init__(self) -> None:
        self._text = TextGenerator()
        self._image = ImageGenerator()
        self._engine = PerchanceEngine()

    # -- AI generators (eeemoon/perchance) ----------------------------------

    GENERATOR_MAP: dict[str, str] = {
        "ai-text-generator": "text",
        "text": "text",
        "ai-image-generator": "image",
        "image": "image",
    }

    # -- Public API ---------------------------------------------------------

    async def run_generator(
        self,
        generator_id: str,
        prompt: str,
        seed: Optional[int] = None,
        section_overrides: Optional[dict[str, str]] = None,
    ) -> Generation:
        """Run a generator by ID.

        For AI generators (text/image) the ``prompt`` is the input text.
        For user generators ``prompt`` is injected into the ``input``
        section, and ``section_overrides`` can override any section.
        """
        kind = self.GENERATOR_MAP.get(generator_id)

        if kind == "text":
            return await self._run_text(prompt)

        if kind == "image":
            return await self._run_image(prompt, seed)

        # User generator — use pure-Python evaluator
        return await self._run_user(generator_id, prompt, seed, section_overrides)

    async def search_generators(
        self, query: str, limit: int = 20
    ) -> list[GeneratorSummary]:
        """Stub — perchance.org has no public search API."""
        return []

    async def get_generator(self, generator_id: str) -> Generator:
        """Stub — returns minimal placeholder."""
        return Generator(id=generator_id, title=generator_id, author="perchance")

    async def close(self) -> None:
        await self._text.close()
        await self._image.close()

    # -- Internal: AI generators --------------------------------------------

    async def _run_text(self, prompt: str) -> Generation:
        output = await self._text.text(prompt, timeout=30.0)
        return Generation(
            id=_make_id(),
            generator_id="ai-text-generator",
            generator_title="AI Text Generator",
            prompt=prompt,
            output=output,
        )

    async def _run_image(self, prompt: str, seed: Optional[int]) -> Generation:
        result = await self._image.image(
            prompt, seed=seed or -1, shape="square"
        )
        import base64

        buf = await result.download()
        b64 = base64.b64encode(buf.read()).decode()
        return Generation(
            id=result.image_id,
            generator_id="ai-image-generator",
            generator_title="AI Image Generator",
            prompt=prompt,
            output=f"data:image/{result.file_extension};base64,{b64}",
            seed=result.seed if seed is not None else None,
        )

    # -- Internal: User generators ------------------------------------------

    async def _run_user(
        self,
        generator_id: str,
        prompt: str,
        seed: Optional[int],
        section_overrides: Optional[dict[str, str]] = None,
    ) -> Generation:
        # PerchanceEngine's evaluate is synchronous — run in executor
        import functools

        fn = functools.partial(
            self._engine.evaluate_raw,
            self._engine.fetch_data(generator_id),
            seed,
            prompt,
            section_overrides,
        )
        loop = asyncio.get_running_loop()
        output = await loop.run_in_executor(None, fn)

        return Generation(
            id=_make_id(),
            generator_id=generator_id,
            generator_title=generator_id,
            prompt=prompt,
            output=output,
            seed=seed,
        )


def _make_id() -> str:
    import uuid

    return uuid.uuid4().hex
