"""Fixture for MP032 undocumented-side-effect.

LLM-gated. Tool name `delete_record` suggests mutation but the description
reads as read-only. An LLM judge should flag the missing side-effect note.
Without --llm this is silent.
"""

from mcp.server.fastmcp import FastMCP  # type: ignore[import-not-found]

mcp = FastMCP("fix_mp032")


@mcp.tool()
def delete_record(rid: str) -> dict:
    """Use this when the user wants to read a record by id.

    Args:
        rid: Record id. Example: "r_1".

    Returns: the record's contents as a dict.
    """
    return {"id": rid}
