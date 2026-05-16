# Your first lint

> Who this page is for: someone who has installed mcpolish and wants a guided tour on a realistic file.

## What you will learn

- How to write a small MCP server that mcpolish can lint.
- How to read each diagnostic line.
- How to fix one problem and re-run.
- How to confirm the score went up.

## Background

mcpolish reads your source code, parses it with [libcst](../concepts/glossary.md#libcst), and runs 23 rules against the tools it finds. Each [rule](../concepts/glossary.md#rule) produces zero or more [diagnostics](../concepts/glossary.md#diagnostic). Each diagnostic is one specific complaint with a file, line, severity, and message.

## Step by step

### 1. Make a starter server

Create a file called `weather_server.py`:

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("weather")


@mcp.tool()
def get(city):
    """Get weather."""
    return {"temp": 72}
```

This is a tiny MCP server with one tool. It is also a tour of common problems.

### 2. Run the lint

```
mcpolish lint weather_server.py --fail-on never
```

Expected output (line numbers may shift slightly):

```
mcpolish 0.1.0
server: weather  (1 tool in 1 file)

weather_server.py:6:1: MP002 [W] tool `get` param `city` has no description
   -> document the param in the docstring's Args block or the JSON schema
   -> https://mcpolish.dev/rules/MP002
weather_server.py:6:1: MP003 [N] tool `get` does not declare an outputSchema and the description never mentions what it returns
   -> add an outputSchema or a 'Returns: ...' line to the docstring
   -> https://mcpolish.dev/rules/MP003
weather_server.py:6:1: MP010 [W] tool name `get` is too generic
   -> consider a more specific name like `get_<noun>` or `<verb>_<thing>`
   -> https://mcpolish.dev/rules/MP010
weather_server.py:6:1: MP013 [W] tool `get` collides with 5 public server(s): http-get, config-get, redis, secrets-manager, vault
   -> pick a more specific name - agents in multi-server sessions must disambiguate on description alone when names collide
   -> https://mcpolish.dev/rules/MP013
weather_server.py:6:1: MP020 [W] tool `get` description is 12 chars (minimum 50)
   -> state what the tool does and when an agent should pick it
   -> https://mcpolish.dev/rules/MP020
weather_server.py:6:1: MP023 [N] tool `get` description has no trigger condition (`use this when...`, `best for...`)
   -> add a sentence describing the conditions under which an agent should pick this tool over alternatives
   -> https://mcpolish.dev/rules/MP023

Found 6 issues (0 errors, 4 warnings, 2 notes). score: 88/100
```

### 3. Read one diagnostic in detail

Take the first line:

```
weather_server.py:6:1: MP002 [W] tool `get` param `city` has no description
```

Breaking it down:

- `weather_server.py:6:1` is the file, line, and column.
- `MP002` is the stable [rule ID](../concepts/glossary.md#rule-id). The detailed page is at [MP002](../rules/MP002.md).
- `[W]` is the [severity](../concepts/glossary.md#severity): warning.
- The rest is the message. It names the tool and the parameter.

Below the diagnostic, the `->` lines give a hint and a link to the rule's documentation.

### 4. Fix one problem

Improve the file. We will fix the name (MP010), the missing description content (MP020, MP023, MP003), and the missing parameter description (MP002) all at once:

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("weather")


@mcp.tool()
def get_weather(city: str) -> dict:
    """Use this when the user wants the current weather for a known city.

    Args:
        city: City name. Example: "Paris".

    Returns: a dict with `temp` (degrees) and `conditions` (string).
    """
    return {"temp": 72, "conditions": "sunny"}
```

### 5. Re-run

```
mcpolish lint weather_server.py
```

Expected output:

```
mcpolish 0.1.0
server: weather  (1 tool in 1 file)

ok no issues found. score: 100/100
```

The score moved from 88 to 100. The default exit code on a clean run is 0, so you can drop `--fail-on never`.

## Common variations

If your tool needs to refer to a name that is genuinely correct but happens to be on the generic list, you can whitelist it. Add to your `pyproject.toml`:

```toml
[tool.mcpolish.MP010]
allow = ["search"]
```

See [Customising rules](../scenarios/customizing-rules.md) for more.

If your tool returns nothing, MP003 will still want you to say so in the description. Phrasing like `Returns nothing on success.` satisfies the rule.

## Troubleshooting

**MP013 fires on a name that does not feel generic.** mcpolish ships a quarterly [snapshot](../concepts/glossary.md#registry-snapshot) of common public tool names. If your tool happens to share a name with several public servers, MP013 fires. You can disable cross-server checks with `--registry off` or move on if the collision is genuine and intentional.

**Adding a docstring did not silence MP020.** Check that the docstring is at least 50 characters after stripping whitespace. The threshold is configurable; see [MP020](../rules/MP020.md).

## See also

- [Understanding the output](understanding-output.md): every part of every line.
- [Rules index](../rules/index.md): all 23 rules with one-line descriptions.
- [Configuration](../usage/configuration.md): how to tune mcpolish to your taste.
