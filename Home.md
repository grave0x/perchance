# perchance toolkit

Python CLI toolkit for evaluating [perchance.org](https://perchance.org) generators locally.

## Features

- **Run generators** — evaluate perchance templates locally without a browser
- **Interactive input** — typed form for generator sections (text, int, dropdown)
- **Search** — search perchance.org for generators
- **Export** — save generations as JSON/Markdown
- **Auth** — login/logout/status for perchance.org accounts
- **Config** — manage settings via YAML config
- **CLI + TUI + GUI** — three interfaces for different workflows

## Quick Start

```sh
pip install -e .
perchance --help
perchance run name-generator
perchance search "fantasy names"
```

## Architecture

```
src/
├── perchance_toolkit/          # Core library (UI-agnostic)
│   ├── api/                    # HTTP client, auth
│   ├── core/                   # Generator runner, template engine
│   ├── storage/                # SQLite, YAML config
│   └── models/                 # Pydantic v2 models
├── perchance_toolkit_cli/      # CLI (click + rich)
├── perchance_toolkit_gui/      # GUI (PySide6)
└── perchance_toolkit_tui/      # TUI (textual)
```

## Project Links

- [GitHub](https://github.com/grave0x/perchance)
- [Issues](https://github.com/grave0x/perchance/issues)