"""Fixture for MP022 missing-example.

String params with no `example` in their docstring or schema trigger MP022.
"""

from mcp.server.fastmcp import FastMCP  # type: ignore[import-not-found]

mcp = FastMCP("fix_mp022")


@mcp.tool()
def search_records(query: str) -> list:
    """Use this when the user wants to find records by keyword.

    Args:
        query: Keywords describing what to look for.

    Returns: a list of matching record ids.
    """
    return [query]
