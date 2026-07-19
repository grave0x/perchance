"""HTTP client for the perchance.org API."""

from __future__ import annotations

from typing import Optional

import httpx

from perchance.models.generator import Generator, GeneratorSummary
from perchance.models.generation import Generation


class PerchanceClient:
    """Thin wrapper around perchance.org HTTP API."""

    BASE_URL = "https://perchance.org/api"

    def __init__(self, session_token: Optional[str] = None) -> None:
        self._session_token = session_token
        self._client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            timeout=30.0,
            headers=self._build_headers(),
        )

    def _build_headers(self) -> dict[str, str]:
        headers = {
            "User-Agent": "perchance-client/0.1.0",
            "Accept": "application/json",
        }
        if self._session_token:
            headers["Authorization"] = f"Bearer {self._session_token}"
        return headers

    async def search_generators(
        self, query: str, limit: int = 20
    ) -> list[GeneratorSummary]:
        """Search for generators matching *query*."""
        params: dict[str, str | int] = {"q": query, "limit": limit}
        resp = await self._client.get("/generators", params=params)  # type: ignore[arg-type]
        resp.raise_for_status()
        data = resp.json()
        return [GeneratorSummary(**item) for item in data.get("results", [])]

    async def get_generator(self, generator_id: str) -> Generator:
        """Fetch full generator details by id."""
        resp = await self._client.get(f"/generators/{generator_id}")
        resp.raise_for_status()
        return Generator(**resp.json())

    async def run_generator(
        self, generator_id: str, prompt: str, seed: Optional[int] = None
    ) -> Generation:
        """Execute a generator with the given prompt."""
        payload: dict = {"prompt": prompt}
        if seed is not None:
            payload["seed"] = seed
        resp = await self._client.post(
            f"/generators/{generator_id}/run", json=payload
        )
        resp.raise_for_status()
        return Generation(**resp.json())

    async def close(self) -> None:
        await self._client.aclose()
