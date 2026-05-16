"""Fixture for MP023 no-trigger-condition.

Description states what the tool does but never says when an agent should
pick it. MP023 fires.
"""

from mcp.server.fastmcp import FastMCP  # type: ignore[import-not-found]

mcp = FastMCP("fix_mp023")


@mcp.tool()
def list_open_tickets() -> list:
    """Returns a JSON array of open ticket records pulled from the database."""
    return []
