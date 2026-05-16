"""Fixture for MP020 description-too-short.

The description is well under 50 characters.
"""

from mcp.server.fastmcp import FastMCP  # type: ignore[import-not-found]

mcp = FastMCP("fix_mp020")


@mcp.tool()
def get_value(key: str) -> str:
    """Reads the value."""
    return key
