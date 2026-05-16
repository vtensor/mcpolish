"""MP002 - every parameter needs a description.

Wang et al. (2026) found 1,285 servers with at least one undocumented
parameter. The companion mutation experiment shows this is a top-5 cause of
wrong-tool selection.
"""

from __future__ import annotations

from typing import Iterable

from mcpolish.rules.base import RuleContext, docs_url
from mcpolish.rules.registry import register
from mcpolish.types import Category, Diagnostic, Severity, ToolRegistry


@register(
    "MP002",
    name="require-param-description",
    category=Category.SCHEMA,
    severity=Severity.WARNING,
    summary="every tool parameter must have a description",
)
class RequireParamDescription:
    def check(self, registry: ToolRegistry, ctx: RuleContext) -> Iterable[Diagnostic]:
        for tool in registry.tools:
            for p in tool.params:
                if not p.description or not p.description.strip():
                    yield Diagnostic(
                        rule_id="MP002",
                        rule_name="require-param-description",
                        category=Category.SCHEMA,
                        severity=Severity.WARNING,
                        message=(
                            f"tool `{tool.name}` param `{p.name}` has no description"
                        ),
                        file=tool.file,
                        line=tool.line,
                        col=tool.col,
                        tool_name=tool.name,
                        docs_url=docs_url("MP002"),
                        hint="document the param in the docstring's Args block or the JSON schema",
                    )
