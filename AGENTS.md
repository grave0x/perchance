# perchance — AGENTS.md

## State

Empty scaffold. No code, no config, no dependencies. Two commits in history:

| Commit | Date | What |
|--------|------|------|
| `3d94a50` | 2026-07-18 | Init scaffold (contained `writing/weiter-llm/` plan) |
| `7f80490` | 2026-07-18 | Extracted weiter-llm to standalone repo; cleared all files |

The original plan proposed a `writer` binary — terminal CLI for local LLM text generation (llama.cpp subprocess), image generation (OpenAI-compatible API), worldbuilding entity management, LoRA training. That plan now lives elsewhere.

## What to know

- **Nothing is built yet.** Start by defining intent and scope before implementing.
- **Git log** has the original architecture decisions (module breakdown, tech stack, CLI commands) if they inform planning. View via `git show 3d94a50:writing/weiter-llm/INTENT.md`.
- **No .gitignore** currently committed (was part of extracted files). Re-create as needed.
- **Tech stack implied** by original plan: Python 3.11+, argparse, pyyaml, httpx, SQLite. This may change with actual scope.

## Commands

```bash
# current state
git log --oneline -10
```

## Conventions

- Keep AGENTS.md up to date as the repo gains substance.
- Prefer executable config over prose. Once build/test/lint commands exist, document them here.
