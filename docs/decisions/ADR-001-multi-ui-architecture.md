# ADR-001: Multi-UI Architecture with Separate Packages

## Status

Accepted

## Date

2024-07-18

## Context

The perchance toolkit needs to support three interaction modes:
- **CLI** — quick one-shot evaluations, scripting, pipe-friendly
- **TUI** — interactive terminal UI for browsing and editing
- **GUI** — rich desktop application with canvas and visual tools

Each mode has different dependencies and users. A single monolithic package would force all users to install dependencies they don't need (e.g., GUI users don't need textual, CLI users don't need PySide6).

## Decision

Structure the project as one core library with three separate frontend packages:

- `perchance_toolkit/` — Core library, UI-agnostic, no GUI/TUI/CLI framework imports
- `perchance_toolkit_cli/` — CLI using click + rich
- `perchance_toolkit_tui/` — TUI using textual
- `perchance_toolkit_gui/` — GUI using PySide6

The core library enforces strict separation: it must not import click, textual, or PySide6 except under `TYPE_CHECKING`.

## Alternatives Considered

### Single package with optional extras
- Pros: Simpler project structure
- Cons: All code in one namespace, harder to enforce UI-agnostic rules
- Rejected: Weaker separation of concerns

### Monorepo with multiple pyproject.toml files
- Pros: Cleanest dependency isolation
- Cons: More complex build tooling, premature for current scale
- Rejected: Over-engineering for v0.1

## Consequences

- Users only install what they need (`pip install perchance-toolkit[cli]`)
- Core library stays clean and testable without UI frameworks
- Adding a new UI (e.g., web interface) doesn't affect existing packages
- Some code duplication across frontends (input validation, formatting)
