# CLI Reference

## Commands

| Command | Description |
|---------|-------------|
| `run <generator>` | Evaluate a generator (optionally with `-i` for interactive input) |
| `search <query>` | Search perchance.org for generators |
| `list` | List recent generators |
| `export <generation_id>` | Export a saved generation |
| `auth login\|logout\|status` | Manage perchance.org authentication |
| `config get\|set <key> <value>` | View/edit configuration |
| `info <generator>` | Show generator metadata and sections |

## Flags

| Flag | Description |
|------|-------------|
| `-v`, `--verbose` | Enable trace logging |
| `-i`, `--interactive` | Interactive input form for generator sections |

## Examples

```sh
# Run a generator non-interactively
perchance run name-generator

# Run with interactive input form
perchance run name-generator -i

# Pipe input
printf '3\n' | perchance run name-generator -i

# Search
perchance search "fantasy town"

# Get generator info
perchance info name-generator
```