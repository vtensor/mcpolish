"""Discovery: async def tools should be found just like sync ones."""

from mcp.server.fastmcp import FastMCP  # type: ignore[import-not-found]

mcp = FastMCP("discover_async")


@mcp.tool()
async def fetch_news(topic: str) -> list:
    """Use this when the user wants recent news on a topic.

    Args:
        topic: The topic to query. Example: "ai safety".

    Returns: a list of headline strings.
    """
    return [topic]
