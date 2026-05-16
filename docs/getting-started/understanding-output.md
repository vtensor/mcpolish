# Understanding the output

> Who this page is for: someone who can run mcpolish but is not sure how to read the results.

## What you will learn

- The shape of each line in the default terminal output.
- What every column means.
- How the score is computed at a glance.
- How the exit code maps to the [CI](../concepts/glossary.md#ci) outcome.

## Background

When you run `mcpolish lint`, the default output goes to your terminal and is rendered with colour using the `rich` library. The same data is available as machine-readable [JSON](../concepts/glossary.md#json), [SARIF](../concepts/glossary.md#sarif), or GitLab Code Quality format. See [Output formats](../usage/output-formats.md).

This page covers only the default terminal format.

## Step by step

### 1. The header

The first two lines name the version and summarise what was scanned.

```
mcpolish 0.1.0
server: weather  (1 tool in 1 file)
```

- `mcpolish 0.1.0`: the version that ran.
- `server: weather`: the [namespace](../concepts/glossary.md#namespace) detected from `FastMCP("weather")`, or the path's basename if no namespace was found.
- `1 tool in 1 file`: how many tools mcpolish discovered and how many `.py` files contributed to that count.

### 2. The diagnostic body

Each problem is two or three lines:

```
weather_server.py:6:1: MP002 [W] tool `get` param `city` has no description
   -> document the param in the docstring's Args block or the JSON schema
   -> https://mcpolish.dev/rules/MP002
```

Anatomy of the first line:

| Part | Meaning |
|---|---|
| `weather_server.py` | The source file. |
| `6:1` | Line number and column number. 1-indexed. |
| `MP002` | The stable [rule ID](../concepts/glossary.md#rule-id). |
| `[W]` | The [severity](../concepts/glossary.md#severity): `[E]` for error, `[W]` for warning, `[N]` for note. |
| The rest | A short message naming the tool and the specific problem. |

The next lines start with `->` and contain:

- A hint that tells you what to change.
- A link to the detailed documentation for this rule.

### 3. The summary line

The last line of the output rolls up the counts and prints the [score](../concepts/glossary.md#score).

```
Found 6 issues (0 errors, 4 warnings, 2 notes). score: 88/100
```

If everything passed:

```
ok no issues found. score: 100/100
```

The score is a single number from 0 (worst) to 100 (best). See [How scoring works](../concepts/how-scoring-works.md).

### 4. The exit code

mcpolish returns an exit code that tells [CI](../concepts/glossary.md#ci) whether to pass or fail.

| Exit code | Meaning |
|---|---|
| 0 | No errors. Warnings and notes are allowed. |
| 1 | At least one error was found and `--fail-on` is set to `error` (the default) or stricter. |
| 2 | An input file could not be parsed at the project level. |
| 64 | You passed a bad CLI argument. |
| 65 | Your `pyproject.toml` config is malformed. |
| 70 | Internal error inside mcpolish. Open an issue. |

You can change which severities cause exit 1 with the `--fail-on` flag. See [CLI reference](../usage/cli-reference.md).

## Common variations

### JSON output

If you pass `--format json`, the output is one JSON document with the same information:

```json
{
  "schema": "https://mcpolish.dev/schemas/report.v1.json",
  "version": "0.1.0",
  "server": "weather",
  "score": 88,
  "diagnostics": [
    {
      "rule_id": "MP002",
      "severity": "warn",
      "message": "tool `get` param `city` has no description",
      "file": "weather_server.py",
      "line": 6,
      "col": 1,
      "tool_name": "get",
      "docs_url": "https://mcpolish.dev/rules/MP002"
    }
  ]
}
```

Useful for scripts and dashboards. See [Output formats](../usage/output-formats.md).

### No colour

If you pipe the output to a file, colour codes are dropped automatically. To force plain text, pipe to `cat`:

```
mcpolish lint . | cat
```

## Troubleshooting

**The output is truncated mid-line in my terminal.** Resize the terminal wider, or pipe to `less`:

```
mcpolish lint . | less -R
```

**The line numbers do not match what my editor shows.** mcpolish line numbers are 1-indexed, which matches most editors. If you are off by one consistently, the line in the diagnostic is the line of the `@tool` decorator, not the `def`. That is on purpose.

**I see a rule I have never heard of.** Look up the ID at [Rules index](../rules/index.md) or run `mcpolish explain MP010` to print the rule's documentation in your terminal.

## See also

- [How scoring works](../concepts/how-scoring-works.md): how the 0-100 number is computed.
- [Output formats](../usage/output-formats.md): JSON, SARIF, GitLab, PR comment.
- [Rules index](../rules/index.md): every rule by ID.
