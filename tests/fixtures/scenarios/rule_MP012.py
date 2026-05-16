"""Fixture for MP012 inconsistent-verb-pattern.

Three tools: two use the canonical verb `get`, one uses the synonym `fetch`.
MP012 must fire on the `fetch` outlier.
"""

from mcp.server.fastmcp import FastMCP  # type: ignore[import-not-found]

mcp = FastMCP("fix_mp012")


@mcp.tool()
def get_user(uid: str) -> dict:
    """Use this when the user wants the profile for one user id.

    Args:
        uid: User id. Example: "u_42".

    Returns: a user dict.
    """
    return {"uid": uid}


@mcp.tool()
def get_post(pid: str) -> dict:
    """Use this when the user wants one post by id.

    Args:
        pid: Post id. Example: "p_99".

    Returns: a post dict.
    """
    return {"pid": pid}


@mcp.tool()
def fetch_comment(cid: str) -> dict:
    """Use this when the user wants a single comment record.

    Args:
        cid: Comment id. Example: "c_1".

    Returns: a comment dict.
    """
    return {"cid": cid}
