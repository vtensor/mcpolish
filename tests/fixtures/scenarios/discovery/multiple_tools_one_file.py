"""Discovery: three tools in the same file."""

from mcp.server.fastmcp import FastMCP  # type: ignore[import-not-found]

mcp = FastMCP("discover_multi")


@mcp.tool()
def get_a(key: str = "") -> str:
    """Use this when the user wants record a by key. Returns a string value."""
    return key


@mcp.tool()
def get_b(key: str = "") -> str:
    """Use this when the user wants record b by key. Returns a string value."""
    return key


@mcp.tool()
def get_c(key: str = "") -> str:
    """Use this when the user wants record c by key. Returns a string value."""
    return key
