"""Fixture for MP005 valid-json-schema.

Tool() inputSchema sets type to "string" instead of "object". JSON Schema
2020-12 allows it technically, but MCP requires type:object at the root.
"""

from mcp import Tool  # type: ignore[import-not-found]

TOOL = Tool(
    name="bad_schema",
    description=(
        "Use this when the user wants a thing. Returns the thing as a string."
    ),
    inputSchema={"type": "string"},
)
