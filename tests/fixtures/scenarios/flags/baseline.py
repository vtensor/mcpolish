"""Baseline single-tool fixture used by every CLI flag scenario.

This tool fires several rules so flag tests can observe what gets included
or excluded: MP010 (generic name `search`), MP013 (cross-server collision),
MP023 (no trigger condition).
"""

from mcp.server.fastmcp import FastMCP  # type: ignore[import-not-found]

mcp = FastMCP("flag_baseline")


@mcp.tool()
def search(q: str) -> list:
    """Returns matching records from the underlying store.

    Args:
        q: query string. Example: "kubernetes".
    """
    return [q]
