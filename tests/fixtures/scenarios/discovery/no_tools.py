"""Discovery: a file that has no MCP tool registrations at all."""


def helper(x: int) -> int:
    """Plain utility function. Not registered with any MCP server."""
    return x + 1


class Service:
    def do_thing(self) -> str:
        return "ok"
