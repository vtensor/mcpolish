"""Fixture for MP040 hidden-prompt-injection.

The description contains a zero-width space character that an attacker could
use to smuggle hidden instructions.
"""

from mcp.server.fastmcp import FastMCP  # type: ignore[import-not-found]

mcp = FastMCP("fix_mp040")


@mcp.tool()
def safe_looking_tool(x: int = 0) -> int:
    """Use this when you want a number returned.​ Returns the int."""
    return x
