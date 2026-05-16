"""Fixture for MP030 param-type-mismatch.

Param typed `string` but description has the word "number".
"""

from mcp import Tool  # type: ignore[import-not-found]

TOOL = Tool(
    name="paginate",
    description=(
        "Use this when the user wants a page of records. Returns up to limit "
        "rows from the underlying store."
    ),
    inputSchema={
        "type": "object",
        "properties": {
            "limit": {
                "type": "string",
                "description": "number of results to return",
            },
        },
        "required": ["limit"],
    },
)
