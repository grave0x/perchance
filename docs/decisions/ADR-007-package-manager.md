# ADR-007: uv for Package Management

## Status

Accepted

## Date

2024-07-18

## Context

The project needs a package management strategy that handles:
- Reproducible installs across environments
- Fast dependency resolution for CI
- Simple developer workflow (install, add/remove deps, run tests)
- Lockfile for pinned transitive dependencies

Initially used pip + requirements.txt, but dependency resolution was slow and requirements.txt didn't handle nested dependencies well.

## Decision

Use **uv** (Astral) for package management. uv:
- Rust-based, 10-100x faster than pip
- Compatible with pyproject.toml format (PEP 621)
- Generates `uv.lock` for reproducible installs
- Supports `uv sync`, `uv add`, `uv remove`, `uv run` workflow
- Works with existing pip/hatchling build systems

## Alternatives Considered

### pip + requirements.txt
- Pros: Standard, no new tool
- Cons: Slow resolution, no lockfile, manual dependency management
- Rejected: Too slow for CI, no reproducibility

### pip-tools (pip-compile + pip-sync)
- Pros: Lockfile support, standard pip underneath
- Cons: Slow resolution, two-step workflow
- Rejected: uv is faster and simpler

### poetry
- Pros: All-in-one build + dependency management
- Cons: Different build system (poetry-core), migration effort
- Rejected: Already using hatchling for builds, only need package management

### pdm
- Pros: PEP 582 compliant, fast
- Cons: Smaller ecosystem, less adoption
- Rejected: uv has wider adoption and better performance

## Consequences

- `uv.lock` committed to repo for reproducible installs
- CI installs via `uv sync --group dev` (fast, ~2s for resolution)
- Developers use `uv add` instead of `pip install`
- hatchling remains the build backend (uv only handles package management)
- pip users can still install via pip (uv.lock is optional for them)
