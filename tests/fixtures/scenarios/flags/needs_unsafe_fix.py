"""Fixture for --unsafe-fix. The tool name repeats the server namespace, so
MP011 fires with an unsafe rename fix."""

from mcp.server.fastmcp import FastMCP  # type: ignore[import-not-found]

memnex = FastMCP("memnex")


@memnex.tool()
def memnex_get_thing(key: str = "") -> str:
    """Use this when the user wants a thing by key. Returns the thing value.

    Args:
        key: thing key. Example: "alpha".
    """
    return key
