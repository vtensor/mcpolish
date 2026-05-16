"""Fixture for MP025 useless-qualifier.

Description is heavy on empty marketing words.
"""

from mcp.server.fastmcp import FastMCP  # type: ignore[import-not-found]

mcp = FastMCP("fix_mp025")


@mcp.tool()
def helper(x: int = 0) -> int:
    """Use this when the user wants a simply powerful and very useful helper. Returns int."""
    return x
