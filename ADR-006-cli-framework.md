# ADR-006: Click + Rich for CLI

**Status:** Accepted | **Date:** 2024-07-18

## Context
Primary interface needs subcommand routing, option parsing, colored output, tables, pipe-friendly JSON output.

## Decision
**click** for command routing and argument parsing. **rich** for terminal output (Console, Table, Panel, Prompt). JSON bypasses rich when `-o json` flag is set.

## Alternatives Considered
- **argparse**: More boilerplate, no nested subcommands
- **typer**: Less control over output formatting

## Consequences
- ~500KB combined dependency
- Clean switch between rich-formatted terminal output and JSON scripting
- Interactive forms use rich's Prompt with typed validation