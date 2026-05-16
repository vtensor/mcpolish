# Multi-file server

> Who this page is for: someone whose MCP server is split across several Python files.

## What you will learn

- How mcpolish walks a directory.
- How tools spread across files get merged into one report.
- Which folders mcpolish skips automatically.
- How to point mcpolish at the project root.

## Background

Most real MCP servers grow beyond a single file. A `main.py` creates the [FastMCP](../concepts/glossary.md#fastmcp) instance, and tools live under `tools/`. mcpolish handles this layout directly: pass the directory and it walks every `.py` file.

## Step by step

### 1. Lay out the project

```
my_mcp_server/
  pyproject.toml
  src/
    my_mcp_server/
      __init__.py
      main.py              FastMCP("my_server") lives here
      tools/
        __init__.py
        search.py          @mcp.tool() definitions
        memory.py          @mcp.tool() definitions
        admin.py           @mcp.tool() definitions
      helpers/
        util.py            no tools, just helpers
  tests/
```

### 2. main.py

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("my_server")

from . import tools  # noqa: F401   trigger the decorators
```

### 3. tools/__init__.py

```python
from . import admin, memory, search  # noqa: F401
```

### 4. tools/search.py

```python
from ..main import mcp


@mcp.tool()
def search_records(query: str, limit: int = 10) -> list:
    """Use this when the user wants to find records by keyword.

    Args:
        query: Search terms. Example: "kubernetes".
        limit: Max number of results.

    Returns: a list of matching records.
    """
    return []
```

### 5. Lint the whole project

```
cd my_mcp_server
mcpolish lint .
```

mcpolish walks every `.py` file in the directory. It finds:

- The `FastMCP("my_server")` constructor in `main.py`, setting the namespace.
- One tool in `tools/search.py`.
- Two tools in `tools/memory.py`.
- One tool in `tools/admin.py`.
- Zero tools in `helpers/util.py` (walked but contributes nothing).

The report names every diagnostic with its original file and line number. A diagnostic from `tools/admin.py` is reported there, not in `main.py`.

## What gets skipped

mcpolish skips these directory names anywhere in the path:

```
.git, .venv, venv, __pycache__, node_modules, dist, build, .tox
```

So your virtualenv and build artifacts do not get linted.

## Cross-file rules

Three rules look at the merged set of tools, not one file at a time:

- **MP011 redundant-prefix**: uses the server namespace detected anywhere in the project.
- **MP012 inconsistent-verb-pattern**: compares verbs across every tool in every file.
- **MP033 duplicate-tool-description**: catches two tools that share a description even if they live in different files.

Example: `tools/search.py` has `get_record`, `tools/memory.py` has `fetch_note`. MP012 fires because the canonical verb across the project is `get`, and `fetch` is an outlier.

## Common variations

### Linting only one subfolder

```
mcpolish lint src/my_mcp_server/tools/
```

mcpolish builds the registry from that subfolder only. Cross-file rules still work but only across files within the subfolder. The namespace defaults to the basename of the path if no `FastMCP("name")` call is visible.

### Setting the namespace manually

If you split your project in unusual ways and mcpolish does not detect the namespace, set it in `pyproject.toml`:

```toml
[tool.mcpolish]
namespace = "my_server"
```

This applies to every run.

### Running from a parent directory

```
mcpolish lint my_mcp_server/
```

Works the same as `cd my_mcp_server && mcpolish lint .`. The reported file paths are relative to where you ran the command.

## Troubleshooting

**Discovered fewer tools than expected.** Some patterns are skipped:

- Dynamic registration in a loop (no static name literal). See [dynamic_registration.py fixture](https://github.com/vtensor/mcpolish/blob/main/tests/fixtures/scenarios/discovery/dynamic_registration.py).
- Tools registered behind a conditional import.
- Tools defined inside a function body.

mcpolish reads source statically. If a tool is not visible from the AST, it is invisible to mcpolish.

**MP011 does not fire even though the namespace is clear.** Check that `FastMCP("name")` (or `Server("name")`) is in one of the scanned files. If your namespace lives in a config file or environment variable, set it manually in `pyproject.toml`.

## See also

- [Single-file server](single-file-server.md)
- [Tool() constructor server](tool-constructor-server.md)
- [Huge monorepo](huge-monorepo.md)
