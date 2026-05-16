"""MP022 - parameter is missing an example value.

Examples in property schemas dramatically improve agent accuracy when the
parameter is a free-form string or a structured payload. Wang et al. find
"missing example" as a top-3 description smell.
"""

from __future__ import annotations

from typing import Iterable

from mcpolish.rules.base import RuleContext, docs_url
from mcpolish.rules.registry import register
from mcpolish.types import Category, Diagnostic, Severity, ToolRegistry

_FREEFORM_TYPES = {"string", "object", "array"}


@register(
    "MP022",
    name="missing-example",
    category=Category.DESCRIPTION,
    severity=Severity.NOTE,
    summary="parameter is free-form but has no example",
)
class MissingExample:
    def check(self, registry: ToolRegistry, ctx: RuleContext) -> Iterable[Diagnostic]:
        cfg = ctx.rule_config("MP022")
        required_examples = int(cfg.get("required_examples", 1))
        for tool in registry.tools:
            for p in tool.params:
                if p.type not in _FREEFORM_TYPES:
                    continue
                if p.has_example:
                    continue
                yield Diagnostic(
                    rule_id="MP022",
                    rule_name="missing-example",
                    category=Category.DESCRIPTION,
                    severity=Severity.NOTE,
                    message=(
                        f"tool `{tool.name}` param `{p.name}` ({p.type}) has no "
                        f"`example` (>= {required_examples} expected)"
                    ),
                    file=tool.file,
                    line=tool.line,
                    col=tool.col,
                    tool_name=tool.name,
                    docs_url=docs_url("MP022"),
                    hint="add `example: ...` to the schema entry to anchor the model",
                )
