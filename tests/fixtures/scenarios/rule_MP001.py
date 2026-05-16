"""Fixture for MP001 require-tool-description.

Tool has neither a docstring nor a description= kwarg, so the description is
empty. MP001 must fire.
"""

from mcp.server.fastmcp import FastMCP  # type: ignore[import-not-found]

mcp = FastMCP("fix_mp001")


@mcp.tool(description="")
def thing(x: int = 0) -> int:
    return x + 1
