# Python API

> Who this page is for: someone who wants to call mcpolish from Python code rather than the command line.

## What you will learn

- How to import mcpolish and call its public functions.
- The shape of the report objects you get back.
- How to iterate over diagnostics in code.
- How to use mcpolish inside your own tooling or CI scripts.

## Background

mcpolish ships as a normal Python package. The same engine that powers the [CLI](../concepts/glossary.md#cli) is available as a library. There are two top-level functions:

- `mcpolish.lint(path)` returns a full report.
- `mcpolish.score(path)` returns just the score.

Both accept a string path or a `pathlib.Path`.

## The public surface

```python
import mcpolish

mcpolish.__version__
mcpolish.lint(path)
mcpolish.score(path)
mcpolish.Category
mcpolish.Severity
mcpolish.Diagnostic
mcpolish.ToolDecl
mcpolish.ToolRegistry
```

That is the whole public API. Power users can also reach into specific rule classes:

```python
from mcpolish.rules.naming.MP010_generic_tool_name import GenericToolName
```

But the rules module is treated as semi-public; small changes between releases are possible.

## Step by step

### 1. Install

```
pip install mcpolish
```

### 2. Call lint

```python
import mcpolish

report = mcpolish.lint("examples/smelly_server.py")

print(report.score)           # 72
print(report.error_count)     # 5
print(report.warning_count)   # 7
print(report.note_count)      # 14
```

The `report` is a `LintReport` dataclass with five fields:

| Field | Type | What |
|---|---|---|
| `diagnostics` | `tuple[Diagnostic, ...]` | Every finding, sorted by file then line. |
| `registry` | `ToolRegistry` | The IR mcpolish built. Has `server_name`, `namespace`, `tools`. |
| `score` | `int` | 0-100, same as `mcpolish.score()`. |
| `error_count` | `int` | Number of diagnostics with severity `error`. |
| `warning_count` | `int` | Number of diagnostics with severity `warning`. |
| `note_count` | `int` | Number of diagnostics with severity `note`. |

There is also a helper:

```python
report.has_errors()  # True if error_count > 0
```

### 3. Walk diagnostics

```python
for d in report.diagnostics:
    print(d.rule_id, d.severity.value, d.location(), d.message)
```

`Diagnostic` is a frozen Pydantic model. Useful fields:

| Field | Type | Notes |
|---|---|---|
| `rule_id` | `str` | `MP010` etc. |
| `rule_name` | `str` | `generic-tool-name`. |
| `category` | `Category` | Enum value. |
| `severity` | `Severity` | Enum value. |
| `message` | `str` | One-line summary. |
| `file` | `str` | Absolute path. |
| `line` | `int` | 1-indexed. |
| `col` | `int` | 1-indexed. |
| `tool_name` | `str | None` | Which tool. |
| `docs_url` | `str` | Link to the rule's page. |
| `hint` | `str | None` | Plain-language fix hint. |
| `fix` | `Fix | None` | Present when an [autofix](../concepts/glossary.md#autofix) is available. |

`d.location()` returns the file:line:col string.

### 4. Filter diagnostics in code

```python
errors = [d for d in report.diagnostics if d.severity == mcpolish.Severity.ERROR]
naming = [d for d in report.diagnostics if d.category == mcpolish.Category.NAMING]
```

### 5. Just the score

```python
score = mcpolish.score("path/to/server.py")
print(score)
```

Same number you would get from `mcpolish score path/to/server.py`.

## Common variations

### Build the registry yourself

If you want the IR without running any rules:

```python
from mcpolish.discover.ir import build_registry

reg = build_registry("path/to/server.py")
for tool in reg.tools:
    print(tool.name, tool.description[:50])
```

This is useful for writing your own checks on top of the discovery layer.

### Pass a config in code

```python
import mcpolish
from mcpolish.config.loader import MCPolishConfig

cfg = MCPolishConfig(ignore=["MP025"])
report = mcpolish.lint("path/", config=cfg)
```

### Enable LLM rules programmatically

```python
from mcpolish.llm.client import build_client

client = build_client("openai:gpt-4o")
report = mcpolish.lint("path/", llm=client)
```

You still need the right API key in your environment.

## Use case: a custom CI gate

```python
import sys
import mcpolish

report = mcpolish.lint(".")

if report.has_errors():
    print(f"mcpolish: {report.error_count} errors, exiting", file=sys.stderr)
    sys.exit(1)

if report.score < 80:
    print(f"mcpolish: score {report.score} below gate of 80", file=sys.stderr)
    sys.exit(1)

print(f"mcpolish: score {report.score}, build green")
```

This is more flexible than `mcpolish lint --fail-on error` because you can combine error counts and the score in one rule.

## Troubleshooting

**`AttributeError: module 'mcpolish' has no attribute 'lint'`.** Older builds may not have wired the public API yet. Run `pip install -U mcpolish`. Confirm with `mcpolish --version`.

**`pydantic.ValidationError` when constructing a `Diagnostic`.** The library treats `Diagnostic` as immutable. Build the `Diagnostic` once with the fields you have. Do not mutate it.

## See also

- [CLI reference](cli-reference.md)
- [Output formats](output-formats.md)
- [Configuration](configuration.md)
