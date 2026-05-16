"""Memory tools for the memnex modular project."""

from ..main import mcp  # noqa: TID252


@mcp.tool()
def store_fact(key: str, value: str) -> dict:
    """Use this when the user wants to remember a fact for later recall.

    Args:
        key: A short label for the fact. Example: "favorite_color".
        value: The fact's value. Example: "blue".

    Returns: a dict echoing what was stored.
    """
    return {"key": key, "value": value}


@mcp.tool()
def recall_fact(key: str) -> str:
    """Use this when the user wants the value of a previously stored fact.

    Args:
        key: The fact's label. Example: "favorite_color".

    Returns: the stored value as a string.
    """
    return key
