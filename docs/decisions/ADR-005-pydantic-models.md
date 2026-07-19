# ADR-005: Pydantic v2 for Data Models

## Status

Accepted

## Date

2024-07-18

## Context

The toolkit passes data between layers: API responses → core engine → storage → presentation. Models need:
- Runtime type validation (catch API changes early)
- Serialization to/from JSON (storage, export)
- Clear documentation of field types and constraints
- Integration with SQLAlchemy for persistence

## Decision

Use Pydantic v2 for all data models. Pydantic v2 uses Rust-based validation (pydantic-core) and provides:
- Automatic type coercion and validation
- `model_dump()` / `model_validate()` for serialization
- JSON Schema generation for documentation
- `Field()` with descriptions, defaults, constraints

## Alternatives Considered

### Python dataclasses
- Pros: Standard library, lightweight
- Cons: No built-in validation, manual serialization
- Rejected: Too much boilerplate for validation

### attrs + cattrs
- Pros: Flexible, composable
- Cons: Smaller ecosystem, less familiar to contributors
- Rejected: Pydantic is more widely adopted

### msgspec
- Pros: Fastest serialization
- Cons: Smaller ecosystem, fewer integration options
- Rejected: SQLAlchemy integration is more important than raw speed

### TypedDict (static typing only)
- Pros: Minimal, no runtime dependency
- Cons: No runtime validation at all
- Rejected: Need runtime safety for API responses

## Consequences

- Pydantic v2 is a significant dependency (pydantic-core is ~10MB)
- Models serve as both validation layer and documentation
- SQLAlchemy uses separate ORM models — duplication is managed via conversion functions
- JSON Schema can be exported for API documentation
