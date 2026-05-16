"""Discovery: FastMCP @mcp.tool() decorator with docstring description."""

from mcp.server.fastmcp import FastMCP  # type: ignore[import-not-found]

mcp = FastMCP("discover_fastmcp")


@mcp.tool()
def hello(name: str = "world") -> str:
    """Use this when the user wants a friendly greeting.

    Args:
        name: Who to greet. Example: "Alice".

    Returns: a greeting string.
    """
    return f"hello {name}"
