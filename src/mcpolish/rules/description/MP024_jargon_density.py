"""MP024 - descriptions densely packed with internal jargon.

Tools whose description leans heavily on internal acronyms or codenames
("RPCs to UFS via TKN headers") fail outside the team that wrote them.
Flag when the ratio of all-caps tokens to total tokens crosses a threshold.
"""

from __future__ import annotations

import re
from typing import Iterable

from mcpolish.rules.base import RuleContext, docs_url
from mcpolish.rules.registry import register
from mcpolish.types import Category, Diagnostic, Severity, ToolRegistry

_TOKEN_RE = re.compile(r"\b[A-Za-z][A-Za-z0-9_]+\b")
_ALLCAPS_RE = re.compile(r"^[A-Z][A-Z0-9_]{1,}$")  # 2+ chars all caps
_WHITELIST = frozenset({"API", "URL", "JSON", "XML", "HTTP", "HTTPS", "MCP", "SQL", "ID"})


@register(
    "MP024",
    name="jargon-density",
    category=Category.DESCRIPTION,
    severity=Severity.NOTE,
    summary="description is dense with all-caps jargon or internal acronyms",
)
class JargonDensity:
    def check(self, registry: ToolRegistry, ctx: RuleContext) -> Iterable[Diagnostic]:
        cfg = ctx.rule_config("MP024")
        max_ratio = float(cfg.get("max_ratio", 0.25))
        min_tokens = int(cfg.get("min_tokens", 8))
        whitelist = _WHITELIST | set(cfg.get("allow", []))
        for tool in registry.tools:
            tokens = _TOKEN_RE.findall(tool.description or "")
            if len(tokens) < min_tokens:
                continue
            allcaps = [
                t for t in tokens if _ALLCAPS_RE.match(t) and t not in whitelist
            ]
            ratio = len(allcaps) / len(tokens)
            if ratio > max_ratio:
                yield Diagnostic(
                    rule_id="MP024",
                    rule_name="jargon-density",
                    category=Category.DESCRIPTION,
                    severity=Severity.NOTE,
                    message=(
                        f"tool `{tool.name}` description is {ratio:.0%} all-caps "
                        f"tokens; offenders: {', '.join(sorted(set(allcaps))[:5])}"
                    ),
                    file=tool.file,
                    line=tool.line,
                    col=tool.col,
                    tool_name=tool.name,
                    docs_url=docs_url("MP024"),
                    hint="expand acronyms on first use; keep description portable",
                )
