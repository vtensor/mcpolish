"""Fixture for MP002 require-param-description.

Param `query` has no description in the docstring's Args block.
"""

from mcp.server.fastmcp import FastMCP  # type: ignore[import-not-found]

mcp = FastMCP("fix_mp002")


@mcp.tool()
def lookup_records(query: str) -> list:
    """Use this when the user wants to find archived records by keyword.

    Returns a list of matching record ids.
    """
    return [query]
