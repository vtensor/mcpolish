"""When the sibling pyproject.toml is broken, mcpolish exits 65 with a clear
config error rather than crashing."""

from mcp.server.fastmcp import FastMCP  # type: ignore[import-not-found]

mcp = FastMCP("cfg_broken")


@mcp.tool()
def hello() -> str:
    """Use this when the user wants a greeting. Returns a string."""
    return "hi"
