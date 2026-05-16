"""Example using the low-level Server API with Tool() literals.

Demonstrates that mcpolish discovers tools from raw Tool() constructors as
well as decorators.
"""

from mcp import Server, Tool  # type: ignore[import-not-found]


server = Server("ledger")


TOOLS = [
    Tool(
        name="create_entry",
        description=(
            "Add a new ledger entry. Use this when the user reports a new "
            "transaction. Returns the entry id."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "amount_cents": {
                    "type": "integer",
                    "description": "Amount in cents. Example: 1299.",
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
