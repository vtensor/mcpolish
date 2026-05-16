"""MP001 - every tool must have a description.

Wang et al. (2026) §4.2: tools with empty descriptions are ~52pp worse in
head-to-head selection. This is the highest-signal rule in the taxonomy.
"""

from __future__ import annotations

from typing import Iterable

from mcpolish.rules.base import Rule, RuleContext, docs_url
from mcpolish.rules.registry import register
from mcpolish.types import Category, Diagnostic, Fix, Severity, ToolRegistry


@register(
    "MP001",
    name="require-tool-description",
    category=Category.SCHEMA,
    severity=Severity.ERROR,
    summary="every tool must declare a non-empty description",
    auto_fixable=True,
)
class RequireToolDescription:
    def check(self, registry: ToolRegistry, ctx: RuleContext) -> Iterable[Diagnostic]:
        for tool in registry.tools:
            if not tool.description or not tool.description.strip():
                yield Diagnostic(
                    rule_id="MP001",
                    rule_name="require-tool-description",
                    category=Category.SCHEMA,
                    severity=Severity.ERROR,
                    message=f"tool `{tool.name}` has no description",
                    file=tool.file,
                    line=tool.line,
                    col=tool.col,
                    tool_name=tool.name,
                    docs_url=docs_url("MP001"),
                    hint="add a docstring or `description=...` kwarg explaining what the tool does",
                    fix=Fix(description="insert a description= placeholder", safe=True),
                )
