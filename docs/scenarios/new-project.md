# Brand new project

> Who this page is for: someone starting an MCP server from scratch and wanting to set up mcpolish from day one.

## What you will learn

- The cleanest minimal layout for a new MCP server.
- How to wire mcpolish into your project before you have a single tool.
- How to keep the score at 100 as you add tools.

## Background

The cheapest time to fix description problems is before you have any descriptions. Set up mcpolish as part of project scaffolding and you never accumulate technical debt in your tool definitions.

## Step by step

### 1. Make the project

```
mkdir my-mcp-server
cd my-mcp-server
python -m venv .venv
source .venv/bin/activate
pip install mcp mcpolish
```

### 2. Add `pyproject.toml`

```toml
[project]
name = "my-mcp-server"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = ["mcp>=1.0"]

[tool.mcpolish]
target-version = "2025-11"
registry = "official"
```

mcpolish defaults are fine. You only need a `[tool.mcpolish]` section if you want to override something.

### 3. Add a tiny server

```python
# src/my_mcp_server/__init__.py
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("my_server")


@mcp.tool()
def ping() -> str:
    """Use this when the user wants to confirm the server is alive.

    Returns: the string "pong".
    """
    return "pong"
```

### 4. Run the lint

```
mcpolish lint src/
```

Expected: `score: 100/100`. From a 100 baseline you can detect any regression immediately.

### 5. Wire it into pre-commit

`.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/vtensor/mcpolish
    rev: v0.1.0
    hooks:
      - id: mcpolish
```

Run once:

```
pre-commit install
```

Now `git commit` runs mcpolish on the affected files. Bad descriptions get caught before they reach the repo.

### 6. Wire it into CI

`.github/workflows/lint.yml`:

```yaml
name: lint
on: [push, pull_request]

jobs:
  mcpolish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: vtensor/mcpolish-action@v1
        with:
          path: src
          fail-on: error
```

CI is now a quality gate. PRs that introduce a missing description, a generic name, or a duplicate are flagged on the build.

### 7. Habit: lint as part of "I am done"

When you finish a tool:

```
mcpolish lint src/
```

You will catch problems while the tool is fresh in your mind. Fix them in minutes.

## Common variations

### TypeScript MCP server

mcpolish v1 only lints Python. If you are starting in TypeScript, you can still adopt the rule taxonomy (the names and the meanings) without the tool itself; manual review against the [rules index](../rules/index.md) is a good practice.

### Internal-only servers

If your server is internal and you do not care about cross-server name collisions, turn MP013 off:

```toml
[tool.mcpolish]
ignore = ["MP013"]
```

You will save a small amount of scan time.

### Brand new and you do not know what tools to ship

Start with one tool, lint, score 100. Add a second, lint, score 100. The constraint forces you to write good descriptions from the start. This is much easier than retrofitting.

## Troubleshooting

**`mcpolish doctor` fails on a fresh install.** Confirm Python 3.11 or newer and that you installed inside the activated venv. Outside the venv, `mcpolish` may resolve to a different install.

**Lint passes locally but fails in CI.** The mcpolish version may differ. Pin it in `pyproject.toml` and `requirements.txt` or use the GitHub Action's `version` input to lock the same release.

## See also

- [Quickstart](../getting-started/quickstart.md)
- [Existing project](existing-project.md)
- [Pre-commit setup](pre-commit-setup.md)
