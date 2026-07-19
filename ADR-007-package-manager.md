# ADR-007: uv for Package Management

**Status:** Accepted | **Date:** 2024-07-18

## Context
Need reproducible installs, fast CI resolution, lockfile for pinned transitive deps, simple dev workflow.

## Decision
**uv** (Astral). Rust-based, 10-100x faster than pip. Compatible with pyproject.toml (PEP 621). Generates uv.lock. Works with hatchling build backend.

## Alternatives Considered
- **pip + requirements.txt**: Slow, no lockfile
- **poetry**: Different build system
- **pdm**: Smaller ecosystem

## Consequences
- uv.lock committed for reproducible installs
- CI installs via `uv pip install -e ".[dev]"`
- hatchling remains the build backend
- pip users can still install without uv