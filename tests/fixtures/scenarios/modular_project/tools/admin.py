"""Admin tools. Includes one tool that fires MP011 redundant-prefix because
its name starts with the server namespace `memnex_`."""

from ..main import mcp  # noqa: TID252


@mcp.tool()
def memnex_clear_all() -> dict:
    """Use this when the operator confirms wiping every stored record.

    Returns: a dict reporting how many records were removed.
    """
    return {"removed": 0}
