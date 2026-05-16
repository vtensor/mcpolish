# Single-file server

> Who this page is for: someone whose entire MCP server lives in one Python file.

## What you will learn

- How to run mcpolish on a single file.
- A complete clean example.
- A complete smelly example and how to clean it.

## Background

A single-file MCP server is the most common shape for getting started. One Python file, one [FastMCP](../concepts/glossary.md#fastmcp) instance, a handful of `@mcp.tool()` functions. mcpolish handles this case in milliseconds.

## Step by step

### 1. Write the server

```python
# notes.py
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("notes")


@mcp.tool()
def create_note(title: str, body: str) -> dict:
    """Use this when the user wants to save a new note for later reference.

    Args:
        title: Short label. Example: "Q3 plan".
        body: Markdown contents. Example: "# Q3 plan\\n- ...".

    Returns: a dict with the new note's id and timestamp.
    """
    return {"id": "n_1", "created_at": "2026-05-16T10:00:00Z"}
```

### 2. Lint it

```
mcpolish lint notes.py
```

Expected:

```
mcpolish 0.1.0
server: notes  (1 tool in 1 file)

ok no issues found. score: 100/100
```

### 3. Add a smelly tool to see what happens

Append:

```python
@mcp.tool()
def search(q):
    """Search."""
    return []
```

Re-lint:

```
mcpolish lint notes.py --fail-on never
```

You will see MP002 (param has no description), MP010 (generic name), MP013 (cross-server collision), MP020 (description too short), MP023 (no trigger condition).

### 4. Fix the smelly tool

Replace it with:

```python
@mcp.tool()
def search_notes(query: str) -> list:
    """Use this when the user wants to find a previous note by keyword.

    Args:
        query: Search terms. Example: "kubernetes".

    Returns: a list of {id, title, snippet} dicts.
    """
    return []
```

Re-lint:

```
mcpolish lint notes.py
```

Back to 100/100.

## Common variations

### Multiple tools in one file

mcpolish handles this fine. Every `@mcp.tool()` function in the file is discovered.

### Tools with no parameters

`def show_help() -> str: ...` is supported. mcpolish does not require parameters; it only complains about parameters that exist without descriptions.

### A tool using a Pydantic model

```python
from pydantic import BaseModel

class Query(BaseModel):
    text: str
    limit: int = 10


@mcp.tool()
def run_query(q: Query) -> list:
    ...
```

mcpolish discovers the tool. It does not follow into the Pydantic model in v1. If you need the model's fields to be visible as parameters to the linter, expose them inline:

```python
@mcp.tool()
def run_query(text: str, limit: int = 10) -> list:
    ...
```

## Troubleshooting

**`0 tools in 0 files`.** Check that you imported `FastMCP` and decorated your function. mcpolish only finds tools registered with one of the supported patterns; see [What mcpolish checks](../concepts/what-mcpolish-checks.md).

**MP013 fires on a name that feels unique.** Cross-server collision uses a bundled [snapshot](../concepts/glossary.md#registry-snapshot) of the top public tool names. If your tool name happens to coincide, MP013 fires. Whitelist with `[tool.mcpolish.MP013]` or use a more specific name.

## See also

- [Multi-file server](multi-file-server.md)
- [Quickstart](../getting-started/quickstart.md)
- [Your first lint](../getting-started/your-first-lint.md)
