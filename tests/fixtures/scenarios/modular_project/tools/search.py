"""Search tools for the memnex modular project."""

from ..main import mcp  # noqa: TID252


@mcp.tool()
def search_records(query: str, limit: int = 10) -> list:
    """Use this when the user wants to find records by keyword.

    Args:
        query: Keywords. Example: "kubernetes".
        limit: How many results to return at most.

    Returns: a list of matching record dicts.
    """
    return [{"q": query, "n": limit}]
