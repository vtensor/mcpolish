"""Discovery: rich type hints. Discoverer maps each to a JSON Schema type."""

from typing import Annotated, Optional

from mcp.server.fastmcp import FastMCP  # type: ignore[import-not-found]

mcp = FastMCP("discover_typed")


@mcp.tool()
def fancy(
    items: list[str],
    count: Optional[int] = None,
    meta: dict[str, str] | None = None,
    label: Annotated[str, "tagged"] = "x",
) -> dict:
    """Use this when the user wants a fancy operation across rich types.

    Args:
        items: List of items. Example: ["a", "b"].
        count: Optional number. Example: 3.
        meta: Optional metadata mapping. Example: {"k": "v"}.
        label: Annotated string label. Example: "y".

    Returns: a dict of results.
    """
    return {"n": len(items)}
