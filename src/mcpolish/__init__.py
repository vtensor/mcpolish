"""MCPolish - fast static linter for MCP servers."""

from mcpolish._version import __version__
from mcpolish.api import lint, score
from mcpolish.types import (
    Category,
    Diagnostic,
    Severity,
    ToolDecl,
    ToolRegistry,
)

__all__ = [
    "__version__",
    "lint",
    "score",
    "Category",
    "Diagnostic",
    "Severity",
    "ToolDecl",
    "ToolRegistry",
]
