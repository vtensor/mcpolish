"""Discovery: three docstring styles.

mcpolish reads Google-style Args blocks. NumPy and plain style do not have an
Args block, so the discoverer leaves per-param descriptions empty (which then
fires MP002 on those tools).
"""

from mcp.server.fastmcp import FastMCP  # type: ignore[import-not-found]

mcp = FastMCP("discover_docs")


@mcp.tool()
def google_style(query: str) -> list:
    """Use this when the user wants to search by keyword.

    Args:
        query: Search keywords. Example: "kubernetes".

    Returns: a list of matches.
    """
    return [query]


@mcp.tool()
def numpy_style(query: str) -> list:
    """Use this when the user wants to search by keyword.

    Parameters
    ----------
    query : str
        Search keywords. Example: "kubernetes".

    Returns
    -------
    list
        Matching items.
    """
    return [query]


@mcp.tool()
def plain_style(query: str) -> list:
    """Use this when the user wants to search by keyword. Takes a query
    string and returns a list of matching item ids.
    """
    return [query]
