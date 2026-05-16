"""Fixture for MP024 jargon-density.

Description is loaded with all-caps acronyms beyond the threshold.
"""

from mcp.server.fastmcp import FastMCP  # type: ignore[import-not-found]

mcp = FastMCP("fix_mp024")


@mcp.tool()
def relay(x: int = 0) -> int:
    """Use this when the user wants to dispatch via TKN over UFS using XYZ ABC FOO BAR PDQ NPC encoding. Returns int."""
    return x
