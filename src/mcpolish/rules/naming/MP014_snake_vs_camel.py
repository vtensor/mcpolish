"""MP014 - mixed snake_case / camelCase inside one server.

Within a server, tool names should follow one casing convention. MCP spec
allows either, but mixing within a single server breaks predictability.
Default preferred form is snake_case (matches the Python SDK examples and
the official registry's published servers).
"""

from __future__ import annotations

import re
from typing import Iterable

from mcpolish.rules.base import RuleContext, docs_url
from mcpolish.rules.registry import register
from mcpolish.types import Category, Diagnostic, Severity, ToolRegistry

_CAMEL = re.compile(r"^[a-z]+(?:[A-Z][a-z0-9]*)+$")
_SNAKE = re.compile(r"^[a-z][a-z0-9]*(?:_[a-z0-9]+)*$")


@register(
    "MP014",
    name="snake-vs-camel",
    category=Category.NAMING,
    severity=Severity.NOTE,
    summary="tool naming convention is inconsistent within the server",
)
class SnakeVsCamel:
    def check(self, registry: ToolRegistry, ctx: RuleContext) -> Iterable[Diagnostic]:
        cfg = ctx.rule_config("MP014")
        preferred = cfg.get("style", "snake")  # "snake" | "camel" | "auto"
        styles = [_style(t.name) for t in registry.tools]
        if not styles:
            return
        if preferred == "auto":
            dominant = max(set(styles), key=styles.count)
        else:
            dominant = preferred
        for tool, style in zip(registry.tools, styles):
            if style != "unknown" and style != dominant:
                yield Diagnostic(
                    rule_id="MP014",
                    rule_name="snake-vs-camel",
                    category=Category.NAMING,
                    severity=Severity.NOTE,
                    message=(
                        f"tool `{tool.name}` uses {style}_case while the server "
                        f"prefers {dominant}_case"
                    ),
                    file=tool.file,
                    line=tool.line,
                    col=tool.col,
                    tool_name=tool.name,
                    docs_url=docs_url("MP014"),
                )


def _style(name: str) -> str:
    if _SNAKE.match(name):
        return "snake"
    if _CAMEL.match(name):
        return "camel"
    return "unknown"
