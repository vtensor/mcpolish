"""Fixture for MP013 name-collision-cross-server.

Tool name `search` collides with many entries in the bundled snapshot.
"""

from mcp.server.fastmcp import FastMCP  # type: ignore[import-not-found]

mcp = FastMCP("fix_mp013")


@mcp.tool()
def search(q: str) -> list:
    """Use this when the user wants to find an item.

    Args:
        q: Search terms. Example: "kubernetes".

    Returns: a list of matching items.
    """
    return [q]
