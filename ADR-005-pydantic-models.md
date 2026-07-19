# ADR-005: Pydantic v2 for Data Models

**Status:** Accepted | **Date:** 2024-07-18

## Context
Data passes between API, core engine, storage, and presentation layers. Needs runtime validation, serialization, field documentation.

## Decision
Pydantic v2 with Rust-based pydantic-core. Automatic validation, model_dump()/model_validate(), JSON Schema generation.

## Alternatives Considered
- **dataclasses**: No built-in validation
- **attrs + cattrs**: Smaller ecosystem

## Consequences
- ~10MB dependency (pydantic-core)
- Models serve as validation + documentation
- Separate SQLAlchemy ORM models with conversion functions