# Tool() constructor server

> Who this page is for: someone using the lower-level Server plus Tool(...) style instead of FastMCP.

## What you will learn

- How mcpolish discovers tools registered through `Tool(name=, description=, inputSchema=)`.
- Why explicit input schemas are required to set in this style.
- How to lint a typical low-level server.

## Background

The official Python SDK ships two styles:

| Style | Class | Example |
|---|---|---|
| Decorator | [FastMCP](../concepts/glossary.md#fastmcp) | `@mcp.tool()` on a function. |
| Constructor | `Server` + `Tool(...)` | Hand-written list of `Tool` objects. |

mcpolish reads both. This page covers the constructor style.

## Step by step

### 1. Write a constructor-style server

```python
# ledger.py
from mcp import Server, Tool

server = Server("ledger")

TOOLS = [
    Tool(
        name="create_entry",
        description=(
            "Use this when the user reports a new transaction. "
            "Returns the new entry id."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "amount_cents": {
                    "type": "integer",
                    "description": "Amount in cents. Example: 1299.",
                    "example": 1299,
                },
                "currency": {
                    "type": "string",
                    "description": "ISO 4217 code. Example: 'USD'.",
                    "example": "USD",
                },
            },
            "required": ["amount_cents", "currency"],
        },
    ),
]
```

### 2. Lint it

```
mcpolish lint ledger.py
```

Expected:

```
mcpolish 0.1.0
server: ledger  (1 tool in 1 file)

ok no issues found. score: 100/100
```

### 3. Remove the `required` array on purpose

```python
inputSchema={
    "type": "object",
    "properties": {
        "amount_cents": {"type": "integer", "description": "Amount in cents."},
    },
}
```

Re-lint. MP004 fires:

```
ledger.py:5:9: MP004 [W] tool `create_entry` inputSchema declares properties
['amount_cents'] but no `required` array. Add `required: []` even when empty
so agents can tell which params are mandatory.
```

Add `"required": []` (or list the mandatory params) and MP004 stops firing.

## What constructor style requires

The constructor style is more verbose by design. mcpolish needs:

- `name` set to a string literal. `name=spec["name"]` is dynamic and skipped.
- `description` set to a string literal. mcpolish supports concatenated strings.
- `inputSchema` set to a dict literal.

If any of these is computed at runtime, mcpolish cannot see the tool. See the [dynamic registration scenario](https://github.com/vtensor/mcpolish/blob/main/tests/fixtures/scenarios/discovery/dynamic_registration.py).

## Schema authoring tips

The constructor style gives you full control over the input schema. mcpolish reads that schema directly, so:

- Adding an `example` field to a property silences MP022 for that param.
- Setting `"required": [...]` silences MP004.
- Setting `"type": "object"` at the root silences MP005.
- Using `"$ref"` or `"oneOf"` is supported but the linter does not deeply inspect referenced subschemas.

## Common variations

### Adding tools through `server.add_tool(...)`

mcpolish also recognises:

```python
server.add_tool(
    name="...",
    description="...",
    input_schema={...},
)
```

Either `inputSchema` or `input_schema` is accepted. Same rule applies: the kwargs must be literal.

### Multiple Tool() literals in one list

```python
TOOLS = [
    Tool(name="a", ...),
    Tool(name="b", ...),
]
```

mcpolish picks up every literal Tool object in the file.

## Troubleshooting

**MP005 fires "inputSchema.type must be 'object'".** The MCP spec requires the root of `inputSchema` to be an object. If you set `type: "string"` at the root, MP005 fires.

**My description is in a constant and mcpolish does not see it.** A constant reference (`description=MY_DESC`) is not a literal at the call site. mcpolish needs an inline string. Inline the description or use FastMCP plus a docstring.

## See also

- [Single-file server](single-file-server.md)
- [Multi-file server](multi-file-server.md)
- [What mcpolish checks](../concepts/what-mcpolish-checks.md)
