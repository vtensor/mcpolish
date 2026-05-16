"""Discovery: low-level Tool(name=, description=, inputSchema=) constructor."""

from mcp import Tool  # type: ignore[import-not-found]

TOOLS = [
    Tool(
        name="lookup_address",
        description=(
            "Use this when the user wants the postal address for a known person id. "
            "Returns a dict with street, city, and zip."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "person_id": {
                    "type": "string",
                    "description": "The person id. Example: 'p_42'.",
                    "example": "p_42",
                },
            },
            "required": ["person_id"],
        },
    ),
]
