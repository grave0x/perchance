"""perchance run — execute a generator."""

from __future__ import annotations

from typing import Optional

import click

from perchance.api.client import PerchanceClient
from perchance.core.generator import GeneratorRunner
from perchance_cli.formatting import print_generation


@click.command()
@click.argument("generator_id")
@click.argument("prompt")
@click.option("--seed", type=int, help="Random seed for reproducible output")
@click.option("--no-save", is_flag=True, help="Skip saving to history")
@click.pass_context
def run_cmd(
    ctx: click.Context,
    generator_id: str,
    prompt: str,
    seed: Optional[int],
    no_save: bool,
) -> None:
    """Run a generator with PROMPT text."""
    async def _run() -> None:
        client = PerchanceClient()
        runner = GeneratorRunner(client, ctx.obj["db"])
        gen = await runner.run(generator_id, prompt, seed, save=not no_save)
        print_generation(gen)
        await client.close()

    import asyncio
    asyncio.run(_run())
