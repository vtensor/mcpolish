"""Fixture for MP010 generic-tool-name.

Tool name `search` is on the generic list.
"""

from mcp.server.fastmcp import FastMCP  # type: ignore[import-not-found]

mcp = FastMCP("fix_mp010")


@mcp.tool()
def search(q: str) -> list:
    """Use this when the user wants to find an item by keyword.

    Args:
        q: Search keywords. Example: "kubernetes".

    Returns: a list of matching item ids.
    """
    return [q]
