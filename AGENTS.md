# perchance — AGENTS.md

## State

Python project with working CLI toolkit. Evaluates perchance.org generators locally via curl_cffi (bypasses Cloudflare) and a pure-Python template engine. Interactive typed input form for generator sections.

Commit history:

| Commit | Date | What |
|--------|------|------|
| `4f8a2c5` | 2026-07-19 | Initial commit (GitHub) |
| `HEAD` | 2026-07-19 | refactor: rename src/perchance* -> src/perchance_toolkit* |
| | | docs: add README and ADRs for architecture decisions |
| | | ci: add GitHub Actions workflow for ruff, mypy, pytest |
| | | docs: add ADRs for HTTP client, Pydantic, CLI, package manager |

## Architecture

```
src/
├── perchance_toolkit/          # Core library (shared)
│   ├── api/                    # HTTP client (curl_cffi) + auth
│   ├── core/                   # Generator runner, perchance_engine (template eval)
│   ├── storage/                # SQLite (SQLAlchemy), YAML config
│   └── models/                 # Pydantic v2 models
├── perchance_toolkit_cli/      # CLI (click + rich)
│   └── commands/               # run, search, list, export, auth, config, info
├── perchance_toolkit_tui/      # TUI (textual)
├── perchance_toolkit_gui/      # GUI (PySide6)
└── tests/                      # pytest suite
```

Data flow: `User → CLI → core/engine (curl_cffi → perchance.org) → output`
Persistence: SQLite (~/.local/share/perchance/history.db), YAML config (~/.config/perchance/config.yaml), per-generator input config (~/.perchance/generators/<id>.config.yaml)

## Key Components

### `perchance_engine.py` (`src/perchance_toolkit/core/`) — Pure-Python template evaluator
- `PerchanceEngine`: fetches generator data via curl_cffi (`impersonate="chrome120"`), parses modelText, evaluates templates
- `_parse_model(text)`: parses perchance DSL into named `sections` dict + `root_assignments`
- `_parse_item(text)`: classifies each line as kind=`text`/`expr`/`import`/`assign`, with `^weight` suffix parsing
- `PerchanceEval`: evaluates `[method.chains]`, `{min-max}` ranges, `{a|b|c}` OR-expressions, `{import:name}` recursions
- `evaluate_raw(data, seed, prompt, section_overrides)`: main entry point for the CLI — injects `input` section and overrides before evaluating
- `_evaluate_with_scope(sections, root_assignments)`: processes root assignments, calls `evaluate("[output]")`
- `_weighted_choice(items, rng)`: weighted random selection

### `run.py` (`src/perchance_toolkit_cli/commands/`) — Interactive input form
- `_classify_sections(sections)`: infers field types from parsed sections — `text`, `int`, `dropdown`, `fileUpload`
- `_is_displayable_text(text)`: filters out template expressions (`[...]`) and brace ranges (`{1-6}`) from dropdown choices
- `_interactive_prompt(gen_id, sections)`: typed interactive form via rich.prompt, saves/loads `~/.perchance/generators/<id>.config.yaml`
- **Section override flow**: `run_cmd()` → `_interactive_prompt()` → `section_overrides` dict → `runner.run()` → `client.run_generator()` → `engine.evaluate_raw(section_overrides=...)` → merged into `sections` dict before evaluation

### `formatting.py` (`src/perchance_toolkit_cli/`) — Output rendering
- `_IS_KITTY`: detects Kitty terminal via `TERM=xterm-kitty`
- `_render_image(data_uri)`: decodes `data:image/...` base64, pipes through `kitty +kitten icat --stdin yes`; fallback prints metadata
- `print_generation(gen)`: auto-detects image output, renders text/markdown/json/html

## Conventions
- `perchance_toolkit/` must stay UI-agnostic (no click, textual, PySide imports — except under TYPE_CHECKING)
- `perchance_engine` module-level logger: `log = logging.getLogger(__name__)` with `DEBUG` level for trace
- CLI `--verbose`/`-v` flag enables trace logging via `logging.basicConfig`
- One logical change per commit
- Models use Pydantic v2, storage uses SQLAlchemy ORM, API uses curl_cffi
- Package management via `uv`; `uv.lock` committed
- Keep AGENTS.md up to date

## Commands

```bash
# setup (uv preferred)
uv pip install -e ".[dev]"
# or with pip
pip install -e ".[dev]"

# CLI
perchance --help
perchance -v run name-generator --interactive   # trace logging
perchance run name-generator                     # freeform prompt
printf '3\n' | perchance run name-generator -i   # pipe stdin
perchance info name-generator                    # list input sections
perchance search <query>
perchance list
perchance export <generation_id>
perchance auth login|logout|status
perchance config get|set <key> <value>

# quality
uv run pytest tests/ -v
uv run ruff check src/
uv run mypy src/
```

## Blocked
- `perchance run image "prompt"` fails `AuthenticationError: Failed to retrieve user key` — `verifyUser` behind Cloudflare
- `medieval-fantasy-generator` doesn't exist on perchance.org

## ADRs
Architecture Decision Records in `docs/decisions/`:
- ADR-001: Multi-UI architecture (separate packages)
- ADR-002: Pure-Python template engine
- ADR-003: SQLite + YAML storage
- ADR-004: curl_cffi HTTP client
- ADR-005: Pydantic v2 models
- ADR-006: Click + Rich CLI
- ADR-007: uv package manager
