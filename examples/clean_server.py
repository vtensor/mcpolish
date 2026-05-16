"""Example MCP server that passes every mcpolish rule.

Run `mcpolish lint examples/clean_server.py` - expect score 100.
"""

from mcp.server.fastmcp import FastMCP  # type: ignore[import-not-found]

mcp = FastMCP("notes")


@mcp.tool()
def create_note(title: str, body: str) -> dict:
    """Create a new note and return its id.

    Use this when the user wants to save a new piece of information. Best for
    short reference material; for long-form drafts prefer `upsert_document`.

    Args:
        title: Short human-readable label, 1-80 chars. Example: "Q3 plan".
        body: Markdown contents of the note. Example: "# Q3 plan\\n- ...".

    Returns:
        A JSON object: {"id": str, "created_at": iso8601 string}.
    """
    return {"id": "n_1", "created_at": "2026-05-16T10:00:00Z"}


@mcp.tool()
def search_notes(query: str, limit: int = 10) -> list:
    """Full-text search across all notes owned by the current user.

    Use this when the user asks "find my notes about ..." or wants to
    locate an existing note. Best for keyword retrieval - for semantic
    similarity prefer `search_notes_semantic`.

    Args:
        query: Keywords to match. Example: "kubernetes networking".
        limit: Maximum number of results to return.

    Returns:
        A list of {"id": str, "title": str, "snippet": str} objects.
    """
    return []


@mcp.tool()
def delete_note(note_id: str) -> dict:
    """Permanently delete a note. This mutation cannot be undone.

    Use this when the user explicitly confirms removal. Only call after the
    user has acknowledged the destructive nature.

    Args:
        note_id: The note id returned by `create_note`. Example: "n_1".

    Returns:
        {"deleted": true} on success.
    """
    return {"deleted": True}
