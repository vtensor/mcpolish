"""Fixture for MP033 duplicate-tool-description.

Two tools share the exact same description.
"""

from mcp.server.fastmcp import FastMCP  # type: ignore[import-not-found]

mcp = FastMCP("fix_mp033")


@mcp.tool()
def list_items_a() -> list:
    """Use this when the user wants the complete list of items owned by them."""
    return []


@mcp.tool()
def list_items_b() -> list:
    """Use this when the user wants the complete list of items owned by them."""
    return []
