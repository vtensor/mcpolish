"""MP021 - overly long descriptions burn context tokens for marginal value.

Anthropic's tool-use guidance: descriptions should be 1-3 short paragraphs.
Beyond ~1500 chars they pay-per-token without measurable accuracy lift
(internal Anthropic eval; cited in Wang 2026 §6 discussion).
"""

from __future__ import annotations

from typing import Iterable

from mcpolish.rules.base import RuleContext, docs_url
from mcpolish.rules.registry import register
from mcpolish.types import Category, Diagnostic, Severity, ToolRegistry


@register(
    "MP021",
    name="description-too-long",
    category=Category.DESCRIPTION,
    severity=Severity.NOTE,
    summary="tool description is longer than the configured maximum",
)
class TooLong:
    def check(self, registry: ToolRegistry, ctx: RuleContext) -> Iterable[Diagnostic]:
        cfg = ctx.rule_config("MP021")
        max_chars = int(cfg.get("max_chars", 1500))
        for tool in registry.tools:
            desc = (tool.description or "").strip()
            if len(desc) > max_chars:
                yield Diagnostic(
                    rule_id="MP021",
                    rule_name="description-too-long",
                    category=Category.DESCRIPTION,
                    severity=Severity.NOTE,
                    message=(
                        f"tool `{tool.name}` description is {len(desc)} chars "
                        f"(maximum {max_chars})"
                    ),
                    file=tool.file,
                    line=tool.line,
                    col=tool.col,
                    tool_name=tool.name,
                    docs_url=docs_url("MP021"),
                    hint=(
                        "move implementation details to docs and keep the "
                        "description focused on selection criteria"
                    ),
                )
