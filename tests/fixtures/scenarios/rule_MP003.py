"""Fixture for MP003 require-return-schema.

Tool has no output_schema and the description never mentions what is returned.
"""

from mcp.server.fastmcp import FastMCP  # type: ignore[import-not-found]

mcp = FastMCP("fix_mp003")


@mcp.tool()
def ping_host(host: str) -> None:
    """Use this when the user wants to verify that a host is reachable.

    Args:
        host: Hostname or IP to check. Example: "example.com".
    """
    print(host)
