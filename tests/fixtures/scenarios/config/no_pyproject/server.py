"""No pyproject in this directory. mcpolish must fall back to defaults."""

from mcp.server.fastmcp import FastMCP  # type: ignore[import-not-found]

mcp = FastMCP("cfg_none")


@mcp.tool()
def list_items() -> list:
    """Use this when the user wants every item. Returns a list of dicts."""
    return []
