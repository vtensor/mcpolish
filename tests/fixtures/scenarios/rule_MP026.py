"""Fixture for MP026 ambiguous-description.

LLM-gated. This fixture is intentionally vague. With --llm enabled and a
backend wired up, MP026 should classify it as ambiguous. Without --llm,
MP026 is silent and other description rules fire instead.
"""

from mcp.server.fastmcp import FastMCP  # type: ignore[import-not-found]

mcp = FastMCP("fix_mp026")


@mcp.tool()
def handle_thing(x: str = "") -> str:
    """Use this when the input thing needs to be transformed somehow.

    Args:
        x: The thing to handle. Example: "abc".

    Returns: the resulting thing as a string.
    """
    return x
