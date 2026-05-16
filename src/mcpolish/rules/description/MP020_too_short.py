"""MP020 - descriptions shorter than the minimum threshold are uninformative.

Wang et al. report that descriptions under 50 chars are 3.4x as likely to
produce the wrong-tool error. The default threshold tracks that finding.
"""

from __future__ import annotations

from typing import Iterable

from mcpolish.rules.base import RuleContext, docs_url
from mcpolish.rules.registry import register
from mcpolish.types import Category, Diagnostic, Severity, ToolRegistry


@register(
    "MP020",
    name="description-too-short",
    category=Category.DESCRIPTION,
    severity=Severity.WARNING,
    summary="tool description is below the configured minimum length",
)
class TooShort:
    def check(self, registry: ToolRegistry, ctx: RuleContext) -> Iterable[Diagnostic]:
        cfg = ctx.rule_config("MP020")
        min_chars = int(cfg.get("min_chars", 50))
        for tool in registry.tools:
            desc = (tool.description or "").strip()
            if 0 < len(desc) < min_chars:
                yield Diagnostic(
                    rule_id="MP020",
                    rule_name="description-too-short",
                    category=Category.DESCRIPTION,
                    severity=Severity.WARNING,
                    message=(
                        f"tool `{tool.name}` description is {len(desc)} chars "
                        f"(minimum {min_chars})"
                    ),
                    file=tool.file,
                    line=tool.line,
                    col=tool.col,
                    tool_name=tool.name,
                    docs_url=docs_url("MP020"),
                    hint="state what the tool does and when an agent should pick it",
                )
