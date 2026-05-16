"""Fixture for MP011 redundant-prefix.

Server is named `memnex` and one tool name repeats that namespace.
"""

from mcp.server.fastmcp import FastMCP  # type: ignore[import-not-found]

memnex = FastMCP("memnex")


@memnex.tool()
def memnex_lookup(key: str) -> str:
    """Use this when the user wants to read a single memory cell.

    Args:
        key: Memory cell key. Example: "user:123:name".

    Returns: the stored value as a string.
    """
    return key
