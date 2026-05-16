"""MP025 - descriptions full of empty qualifiers ("simply", "just", "very").

Wang et al. find a small but consistent regression from descriptions that
read as marketing copy rather than functional spec.
"""

from __future__ import annotations

import re
from typing import Iterable

from mcpolish.rules.base import RuleContext, docs_url
from mcpolish.rules.registry import register
from mcpolish.types import Category, Diagnostic, Severity, ToolRegistry

_USELESS_RE = re.compile(
    r"\b("
    r"simply|"
    r"just|"
    r"very|"
    r"really|"
    r"basically|"
    r"essentially|"
    r"obviously|"
    r"actually|"
    r"powerful|"
    r"easy|"
    r"simple|"
    r"convenient|"
    r"useful|"
    r"helpful|"
    r"great|"
    r"awesome|"
    r"perfect"
    r")\b",
    re.IGNORECASE,
)


@register(
    "MP025",
    name="useless-qualifier",
    category=Category.DESCRIPTION,
    severity=Severity.NOTE,
    summary="description contains empty qualifiers that add no signal",
)
class UselessQualifier:
    def check(self, registry: ToolRegistry, ctx: RuleContext) -> Iterable[Diagnostic]:
        for tool in registry.tools:
            matches = _USELESS_RE.findall(tool.description or "")
            if not matches:
                continue
            uniq = sorted({m.lower() for m in matches})
            yield Diagnostic(
                rule_id="MP025",
                rule_name="useless-qualifier",
                category=Category.DESCRIPTION,
                severity=Severity.NOTE,
                message=(
                    f"tool `{tool.name}` description uses empty qualifier"
                    f"{'s' if len(uniq) > 1 else ''}: {', '.join(uniq)}"
                ),
                file=tool.file,
                line=tool.line,
                col=tool.col,
                tool_name=tool.name,
                docs_url=docs_url("MP025"),
                hint=(
                    "replace with concrete capability statements; agents weight "
                    "functional content not adjectives"
                ),
            )
