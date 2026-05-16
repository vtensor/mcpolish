"""Server that lints with the empty config section. Behaves as defaults."""

from mcp.server.fastmcp import FastMCP  # type: ignore[import-not-found]

mcp = FastMCP("cfg_empty")


@mcp.tool()
def hello(name: str = "world") -> str:
    """Use this when the user wants a friendly greeting. Returns a string.

    Args:
        name: who to greet. Example: "Alice".
    """
    return f"hi {name}"
