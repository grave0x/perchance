# perchance toolkit

CLI, TUI, and GUI toolkit for evaluating [perchance.org](https://perchance.org) generators locally.

## Features

- **Run generators locally** — evaluate perchance templates without a browser
- **Interactive input forms** — typed fields for generator sections (text, int, dropdown)
- **Search** — find generators on perchance.org
- **Export** — save generations as JSON or Markdown
- **Auth** — login/logout/status for perchance.org accounts
- **Config** — manage settings via YAML config
- **Three interfaces** — CLI (click+rich), TUI (textual), GUI (PySide6)

## Quick Start

```sh
# Install
python3 -m venv .venv
source .venv/bin/activate
pip install -e .

# Use
perchance run name-generator
perchance search "fantasy names"
perchance info name-generator
```

## Commands

| Command | Description |
|---------|-------------|
| `run <generator>` | Evaluate a generator (use `-i` for interactive input) |
| `search <query>` | Search perchance.org |
| `list` | List recent generators |
| `export <generation_id>` | Export a saved generation |
| `auth login\|logout\|status` | Manage authentication |
| `config get\|set <key> <value>` | View/edit configuration |
| `info <generator>` | Show generator metadata and sections |

## Architecture

```
src/
├── perchance_toolkit/          # Core library (UI-agnostic)
│   ├── api/                    # HTTP client (curl_cffi) + auth
│   ├── core/                   # Generator runner, template engine
│   ├── storage/                # SQLite (SQLAlchemy), YAML config
│   └── models/                 # Pydantic v2 models
├── perchance_toolkit_cli/      # CLI (click + rich)
├── perchance_toolkit_tui/      # TUI (textual)
└── perchance_toolkit_gui/      # GUI (PySide6)
```

Data flow: `User → CLI → core/engine (curl_cffi → perchance.org) → output`

## Development

```sh
pip install -e ".[dev]"
python -m pytest tests/ -v
ruff check src/
mypy src/
```

See [docs/decisions/](docs/decisions/) for architectural decisions.

## Blocked

- `perchance run image "prompt"` fails with `AuthenticationError` — `verifyUser` behind Cloudflare
- `medieval-fantasy-generator` doesn't exist on perchance.org
