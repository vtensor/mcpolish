"""MP003 - encourage return-value description / outputSchema.

3,093 servers (Wang 2026 Table 4) ship without any documentation of what a
tool returns. Agents that can't predict the shape of the return value resort
to defensive shotgunning across tools.
"""

from __future__ import annotations

import re
from typing import Iterable

from mcpolish.rules.base import RuleContext, docs_url
from mcpolish.rules.registry import register
from mcpolish.types import Category, Diagnostic, Severity, ToolRegistry

_RETURN_HINT_RE = re.compile(
    r"\b(returns?|yields?|response|output)\b", re.IGNORECASE
)


@register(
    "MP003",
    name="require-return-schema",
    category=Category.SCHEMA,
    severity=Severity.NOTE,
    summary="prefer declaring outputSchema or describing what the tool returns",
)
class RequireReturnSchema:
    def check(self, registry: ToolRegistry, ctx: RuleContext) -> Iterable[Diagnostic]:
        for tool in registry.tools:
            if tool.output_schema:
                continue
            if _RETURN_HINT_RE.search(tool.description or ""):
                continue
            yield Diagnostic(
                rule_id="MP003",
                rule_name="require-return-schema",
                category=Category.SCHEMA,
                severity=Severity.NOTE,
                message=(
                    f"tool `{tool.name}` does not declare an outputSchema and the "
                    "description never mentions what it returns"
                ),
                file=tool.file,
                line=tool.line,
                col=tool.col,
                tool_name=tool.name,
                docs_url=docs_url("MP003"),
                hint="add an outputSchema or a 'Returns: …' line to the docstring",
            )
