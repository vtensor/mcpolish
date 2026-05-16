# CLI reference

> Who this page is for: anyone who needs the exact spelling of a command, flag, or exit code.

## What you will learn

- Every mcpolish subcommand.
- Every flag on every subcommand.
- Every exit code and when it fires.

## Background

mcpolish is a single binary called `mcpolish`. It uses subcommands: `lint`, `score`, `explain`, `doctor`. Each subcommand has its own flags. Global flags are `--help` and `--version`.

## Global

```
mcpolish --version
mcpolish --help
mcpolish <subcommand> --help
```

## mcpolish lint

The main check.

```
mcpolish lint TARGET [OPTIONS]
```

`TARGET` is required. It can be:

- A path to a single `.py` file.
- A path to a directory. mcpolish walks every `.py` file inside (skipping `.git`, `.venv`, `venv`, `__pycache__`, `node_modules`, `dist`, `build`, `.tox`).

### Options

| Flag | Type | Default | What it does |
|---|---|---|---|
| `--select RULE` | string, repeatable | none | Only run the named rules. Accepts a range like `MP001-MP005`. |
| `--ignore RULE` | string, repeatable | none | Drop the named rules. Takes priority over `--select`. |
| `--llm SPEC` | string | none | Enable [LLM](../concepts/glossary.md#llm)-gated rules. `SPEC` is `provider:model`, e.g. `openai:gpt-4o`. |
| `--registry MODE` | choice | `official` | `official` enables MP013 cross-server check using the bundled snapshot. `off` disables it. |
| `--format FORMAT` | choice | `tty` | Output format. One of `tty`, `json`, `sarif`, `gitlab`, `pr-comment`. |
| `--fix` | flag | off | Apply [safe](../concepts/glossary.md#safe-fix) autofixes in place. |
| `--unsafe-fix` | flag | off | Apply both safe and [unsafe](../concepts/glossary.md#unsafe-fix) autofixes. Implies `--fix`. |
| `--fail-on LEVEL` | choice | `error` | Which severity should cause exit code 1. One of `error`, `warn`, `note`, `never`. |

### Examples

```
# Default: run every non-LLM rule, exit 1 on errors.
mcpolish lint .

# Run only naming rules.
mcpolish lint . --select MP010-MP014

# Run everything except MP025.
mcpolish lint . --ignore MP025

# Strict mode: any warning fails the build.
mcpolish lint . --fail-on warn

# Emit SARIF for GitHub Code Scanning.
mcpolish lint . --format sarif > sarif.json

# Apply safe fixes in place.
mcpolish lint . --fix
```

## mcpolish score

Print the score without the diagnostics.

```
mcpolish score TARGET [OPTIONS]
```

### Options

| Flag | Type | Default | What it does |
|---|---|---|---|
| `--json` | flag | off | Print a JSON document with `score`, `server`, `tools`, `errors`, `warnings`, `notes`. |
| `--badge FILE` | path | none | Write an SVG badge to `FILE`. Designed for README pins. |

### Examples

```
mcpolish score examples/clean_server.py
# 100

mcpolish score . --json
# {"score": 78, "server": "memnex", "tools": 8, ...}

mcpolish score . --badge badge.svg
# badge written to badge.svg
```

## mcpolish explain

Print rule documentation in the terminal.

```
mcpolish explain [RULE_ID]
```

If `RULE_ID` is omitted, prints a one-line summary of every rule. If provided, prints the rule's category, severity, hints, and docs URL.

### Examples

```
mcpolish explain
mcpolish explain MP010
```

## mcpolish doctor

Validate the local config and confirm the install works.

```
mcpolish doctor [TARGET]
```

`TARGET` defaults to the current directory. Output looks like:

```
config: ok (target-version=2025-11, registry=official)
snapshot: ok (51 tools, version=v1)
rules: 23 loaded
```

Returns 0 if everything is healthy, 65 if the config is malformed.

## Exit codes

| Code | Meaning |
|---|---|
| 0 | Success. No errors, or `--fail-on` did not trip. |
| 1 | At least one diagnostic at the configured `--fail-on` level. |
| 2 | A file in the target could not be parsed at the project level. |
| 64 | Bad CLI usage. Wrong flag, unknown rule, etc. |
| 65 | The `pyproject.toml` config is malformed. |
| 70 | Internal error inside mcpolish. Open an issue with the trace. |

## Common variations

### Reading config from a specific directory

mcpolish walks up from `TARGET` looking for the nearest `pyproject.toml`. To force a different starting point, cd into that directory first:

```
cd /path/to/project && mcpolish lint .
```

### Piping output

The `tty` format detects whether stdout is a real terminal. When piped, colour is dropped automatically. To force plain text in a real terminal, pipe to `cat`:

```
mcpolish lint . | cat
```

For machine parsing always use `--format json`.

## See also

- [Configuration](configuration.md)
- [Output formats](output-formats.md)
- [Autofix](autofix.md)
