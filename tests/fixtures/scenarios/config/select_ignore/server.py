"""With select=[MP010,MP013] and ignore=[MP013], only MP010 should fire."""

from mcp.server.fastmcp import FastMCP  # type: ignore[import-not-found]

mcp = FastMCP("cfg_select")


@mcp.tool()
def search(q: str) -> list:
    """Use this when the user wants a keyword lookup. Returns a list of ids.

    Args:
        q: query string. Example: "kubernetes".
    """
    return [q]
