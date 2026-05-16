"""Fixture for MP031 param-meaning-mismatch.

LLM-gated. Param `since` looks like a date filter but is typed `integer`,
which an LLM judge would call out as ambiguous between epoch seconds and
days-ago. Without --llm this is silent.
"""

from mcp.server.fastmcp import FastMCP  # type: ignore[import-not-found]

mcp = FastMCP("fix_mp031")


@mcp.tool()
def list_events(since: int = 0) -> list:
    """Use this when the user wants recent events.

    Args:
        since: cutoff value. Example: 1700000000.

    Returns: a list of events.
    """
    return [since]
