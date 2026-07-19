# ADR-002: Pure-Python Template Engine

## Status

Accepted

## Date

2024-07-18

## Context

perchance.org generators use a custom template DSL with:
- Named sections with weighted random selection
- `[method.chains]` for dynamic evaluation
- `{min-max}` numeric ranges
- `{a|b|c}` OR-expressions
- `{import:name}` section recursion
- `^weight` suffixes on list items

The only existing evaluator is the JavaScript engine on perchance.org. We need offline evaluation.

## Decision

Build a pure-Python template evaluator (`perchance_engine.py`) that:
1. Fetches generator `modelText` via the perchance.org API (curl_cffi with browser impersonation)
2. Parses the DSL into an AST of named sections
3. Evaluates templates using Python with a seeded random number generator

The engine is designed to run the same DSL as the JS engine, producing equivalent output for the same seed and inputs.

## Alternatives Considered

### Reverse-engineer and run the JS engine via Node.js subprocess
- Pros: Exact compatibility
- Cons: Requires Node.js runtime, IPC overhead, harder to distribute
- Rejected: Adds runtime dependency

### Run the JS engine via PyMiniRacer or similar
- Pros: Same JS logic, no subprocess
- Cons: V8 embed dependency, version compatibility issues
- Rejected: Fragile, hard to debug

### Proxy evaluation through perchance.org API only
- Pros: No template engine needed
- Cons: Requires internet, rate limited, no offline mode
- Rejected: Offline use is a core requirement

## Consequences

- Must maintain parity with the JS engine as perchance.org evolves
- The engine is the most complex component (~700 lines)
- Works offline, no runtime dependencies beyond Python
- Some edge cases may produce different output than the JS engine
