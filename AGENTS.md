# perchance — AGENTS.md

## State

Python project scaffold. Core library + CLI skeleton built. TUI/GUI stubs ready.

Commit history:

| Commit | Date | What |
|--------|------|------|
| `3d94a50` | 2026-07-18 | Init scaffold (contained `writing/weiter-llm/` plan) |
| `7f80490` | 2026-07-18 | Extracted weiter-llm to standalone repo; cleared all files |
| `129e51d` | 2026-07-18 | init: blank scaffold |
| `HEAD` | 2026-07-18 | feat: project skeleton — core lib, CLI, TUI, GUI |

## Architecture

```
src/
├── perchance/              # Core library (shared)
│   ├── api/                # HTTP client (httpx) + auth
│   ├── core/               # Generator runner, prompt mgmt, export
│   ├── storage/            # SQLite (SQLAlchemy), YAML config
│   └── models/             # Pydantic v2 models
├── perchance_cli/          # CLI (click + rich)
├── perchance_tui/          # TUI (textual)
└── perchance_gui/          # GUI (PySide6)
```

Data flow: `User → CLI/TUI/GUI → core → API client → perchance.org`
Persistence: SQLite (~/.local/share/perchance/history.db), YAML config (~/.config/perchance/config.yaml)

## Commands

```bash
# setup
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# CLI (all subcommands)
perchance --help
perchance run <generator_id> <prompt>
perchance search <query>
perchance list
perchance export <generation_id>
perchance auth login|logout|status
perchance config get|set <key> <value>

# TUI
python -m perchance_tui.app

# GUI
python -m perchance_gui.app

# quality
python -m pytest tests/ -v
ruff check src/
mypy src/
```

## Conventions

- Keep AGENTS.md up to date as repo gains substance.
- Core `perchance/` package must stay UI-agnostic (no click, textual, PySide imports).
- One logical change per commit.
- Models use Pydantic v2, storage uses SQLAlchemy ORM, API uses httpx.
