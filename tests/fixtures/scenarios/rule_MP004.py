"""Fixture for MP004 require-required-array.

The Tool() constructor declares one required-looking property but the schema
has no required array. Triggers MP004.
"""

from mcp import Tool  # type: ignore[import-not-found]

TOOL = Tool(
    name="create_ticket",
    description=(
        "Use this when the user reports a new bug. Returns the new ticket id."
    ),
    inputSchema={
        "type": "object",
        "properties": {
            "title": {"type": "string", "description": "Short summary."},
        },
        # required array intentionally missing
    },
)
