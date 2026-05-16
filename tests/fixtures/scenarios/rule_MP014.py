"""Fixture for MP014 snake-vs-camel.

Two tools use snake_case, one uses camelCase. The camelCase one should be
flagged as the outlier.
"""

from mcp.server.fastmcp import FastMCP  # type: ignore[import-not-found]

mcp = FastMCP("fix_mp014")


@mcp.tool()
def get_thing(name: str) -> dict:
    """Use this when the user wants a thing by name.

    Args:
        name: The thing's name. Example: "alpha".

    Returns: a thing dict.
    """
    return {"name": name}


@mcp.tool()
def get_other_thing(name: str) -> dict:
    """Use this when the user wants the other thing variant.

    Args:
        name: The thing's name. Example: "beta".

    Returns: a thing dict.
    """
    return {"name": name}


@mcp.tool()
def getThirdThing(name: str) -> dict:
    """Use this when the user wants the third variant of the thing.

    Args:
        name: The thing's name. Example: "gamma".

    Returns: a thing dict.
    """
    return {"name": name}
