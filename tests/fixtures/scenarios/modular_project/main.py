"""Modular project: the entry point. FastMCP("memnex") sets the namespace,
then the tools are imported from sibling modules. mcpolish should walk the
whole directory and merge the tools."""

from mcp.server.fastmcp import FastMCP  # type: ignore[import-not-found]

mcp = FastMCP("memnex")

# Tools register on import via decorators in the submodules.
from . import tools  # noqa: F401
