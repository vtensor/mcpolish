"""Discovery: a tool that takes a Pydantic BaseModel.

mcpolish does not introspect Pydantic models in v1. The discoverer falls back
to the bare signature. This fixture documents that behaviour. A future
version may follow Pydantic refs into the model fields.
"""

from mcp.server.fastmcp import FastMCP  # type: ignore[import-not-found]
from pydantic import BaseModel  # type: ignore[import-not-found]

mcp = FastMCP("discover_pydantic")


class Query(BaseModel):
    text: str
    limit: int = 10


@mcp.tool()
def run_query(q: Query) -> list:
    """Use this when the user wants to run a structured query.

    Args:
        q: The query object. Example: Query(text="hello", limit=5).

    Returns: a list of result rows.
    """
    return []
