"""Fixture for MP021 description-too-long.

The docstring is well over 1500 characters.
"""

from mcp.server.fastmcp import FastMCP  # type: ignore[import-not-found]

mcp = FastMCP("fix_mp021")


@mcp.tool()
def overdocumented(x: int = 0) -> int:
    """Use this when the user wants a long-winded operation that we will now describe at length.
    This tool returns an integer. It does not raise. It does not call out to the network.
    It does not write to disk. It does not read environment variables. It does not consult
    the registry. It does not modify global state. It does not invoke any subprocess.
    It does not run any sandbox. It does not produce side effects of any kind. It is the
    simplest possible identity function dressed up in a long description so that the
    description-too-long rule fires for testing purposes. We will repeat that one more
    time because the threshold is fifteen hundred characters and we still have some
    distance to go before that limit is comfortably exceeded. The function does not
    raise. The function does not call out to the network. The function does not write to
    disk. The function does not read environment variables. The function does not
    consult the registry. The function does not modify global state. The function does
    not invoke any subprocess. The function does not run any sandbox. The function does
    not produce side effects of any kind. The function is the simplest possible identity
    function dressed up in a long description so that the description-too-long rule
    fires for testing purposes. Returns the parameter unchanged. Adding still more
    sentences here to comfortably exceed the configured threshold so that this rule
    has a stable trigger fixture for the regression suite over many future releases.
    """
    return x
