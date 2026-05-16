"""Discovery: tools registered through a runtime call where name and
description come from variables, not string literals. The Tool() constructor
branch in the discoverer needs a literal `name=` argument to register a tool
in the IR. Because every value here is a subscript expression rather than a
literal, the discoverer reports zero tools for this file.

A future MP000 dynamic-tools-detected diagnostic could surface this case so
the user knows their tools were skipped.
"""

from mcp import Tool  # type: ignore[import-not-found]

SPECS = [
    {"name": "alpha", "description": "Use this for alpha. Returns int."},
    {"name": "beta", "description": "Use this for beta. Returns int."},
]


TOOLS = [Tool(name=spec["name"], description=spec["description"]) for spec in SPECS]
