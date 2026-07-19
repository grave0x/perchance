# ADR-003: SQLite + YAML Config Storage

## Status

Accepted

## Date

2024-07-18

## Context

The toolkit needs to persist:
- **Generation history** — structured records with timestamps, seeds, outputs
- **User config** — API keys, preferences, default settings
- **Per-generator input config** — saved form values for repeat runs

Each has different access patterns and structure requirements.

## Decision

Use three storage backends, each matched to its use case:

| Data | Backend | Location | Why |
|------|---------|----------|-----|
| Generation history | SQLite via SQLAlchemy ORM | `~/.local/share/perchance/history.db` | Relational queries, efficient filtering |
| User config | YAML | `~/.config/perchance/config.yaml` | Human-editable, easy to backup |
| Generator input config | YAML | `~/.perchance/generators/<id>.config.yaml` | Per-generator, easy to share/reuse |

## Alternatives Considered

### SQLite for everything
- Pros: Single backend
- Cons: Config files aren't human-editable, harder to debug
- Rejected: Config needs to be hand-editable

### JSON for config files
- Pros: Native Python support
- Cons: No comments, less readable for humans
- Rejected: YAML is more user-friendly for config

### TOML for config files
- Pros: Standard for Python projects (pyproject.toml)
- Cons: Less flexible for nested structures
- Rejected: YAML handles the config complexity better

## Consequences

- Three backends to maintain, but each is well-suited to its data
- SQLAlchemy ORM provides migration support as schema evolves
- YAML configs are easy for users to inspect and modify
- Config paths follow XDG conventions for cross-platform compatibility
