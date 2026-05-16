"""With MP010.allow=['search'], MP010 should be silent on this tool."""

from mcp.server.fastmcp import FastMCP  # type: ignore[import-not-found]

mcp = FastMCP("cfg_override")


@mcp.tool()
def search(q: str) -> list:
    """Use this when the user wants a keyword lookup. Returns matching ids.

    Args:
        q: query string. Example: "kubernetes".
    """
    return [q]
