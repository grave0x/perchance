# ADR-006: Click + Rich for CLI

## Status

Accepted

## Date

2024-07-18

## Context

The CLI is the primary interface for the toolkit. It needs:
- Subcommand routing (run, search, list, export, auth, config, info)
- Option parsing with help text
- Colored output, tables, progress indicators
- Pipe-friendly output for scripting (raw JSON)

## Decision

Use **click** for command routing and argument parsing, **rich** for terminal output.

- click: `@click.group()` / `@click.command()` for subcommands, `@click.option()` for flags
- rich: `Console()` for colored output, `Table()` for structured data, `Panel()` for formatted displays, `Prompt()` for interactive input
- JSON output via `-o json` flag bypasses rich formatting

## Alternatives Considered

### argparse (stdlib)
- Pros: No dependency
- Cons: More boilerplate, no nested subcommand support, manual help formatting
- Rejected: Subcommand complexity calls for a framework

### typer
- Pros: Built on click, type-annotated
- Cons: Less control over output formatting
- Rejected: Rich integration is more important than type-inferred CLI

### cement / cliff
- Pros: Full application framework
- Cons: Heavy, opinionated, overkill for this scale
- Rejected: Too much framework

## Consequences

- click + rich are two dependencies (~500KB combined)
- Output can switch between rich-formatted (terminal) and JSON (scripting) cleanly
- Interactive forms use rich's Prompt with typed validation
- Tables auto-adjust to terminal width via rich
