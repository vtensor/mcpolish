"""Fixture for --fix. Tool has no description, so MP001 fires with a safe
autofix that inserts a docstring stub."""

from mcp.server.fastmcp import FastMCP  # type: ignore[import-not-found]

mcp = FastMCP("needs_safe_fix")


@mcp.tool()
def needs_docstring(x: int = 0) -> int:
    return x + 1
