# Development

## Setup

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Commands

| Command | Description |
|---------|-------------|
| `perchance --help` | CLI help |
| `python -m pytest tests/ -v` | Run tests |
| `ruff check src/` | Lint |
| `mypy src/` | Type check |

## Project conventions

- Core library (`perchance_toolkit/`) must stay UI-agnostic — no click, textual, PySide imports (except under TYPE_CHECKING)
- Models use Pydantic v2
- Storage uses SQLAlchemy ORM
- API uses httpx (async)
- One logical change per commit

## Architecture notes

### Template engine

The `perchance_engine.py` module is a pure-Python evaluator for perchance's DSL:
- Parses `modelText` into named sections
- Evaluates `[method.chains]`, `{min-max}` ranges, `{a\|b\|c}` OR-expressions, `{import:name}` recursions
- Supports weighted choices via `^weight` suffix

### Interactive input

The `run.py` command infers field types from parsed sections:
- `text` — for display text without input
- `int` — for numeric inputs
- `dropdown` — for choice-based inputs
- `fileUpload` — for file uploads