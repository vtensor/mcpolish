"""MP023 - description never says when to call the tool.

A useful description includes a *trigger condition*: "use this when …",
"call this if …", "best for …". Wang et al. call descriptions without
trigger language "passive descriptions" and find they cause +6.8pp wrong
tool selection.

Heuristic: look for any phrase from a trigger lexicon. This is an opt-in
rule (NOTE severity) because false positives are easy.
"""

from __future__ import annotations

import re
from typing import Iterable

from mcpolish.rules.base import RuleContext, docs_url
from mcpolish.rules.registry import register
from mcpolish.types import Category, Diagnostic, Severity, ToolRegistry

_TRIGGER_RE = re.compile(
    r"\b("
    r"use (?:this|it) when|"
    r"call (?:this|it) (?:when|if)|"
    r"invoke (?:this|it) (?:when|if)|"
    r"useful (?:when|for)|"
    r"appropriate (?:when|for)|"
    r"best for|"
    r"only (?:when|if)|"
    r"prefer (?:this|it) when|"
    r"when the user"
    r")\b",
    re.IGNORECASE,
)


@register(
    "MP023",
    name="no-trigger-condition",
    category=Category.DESCRIPTION,
    severity=Severity.NOTE,
    summary="description has no trigger condition telling the agent when to pick the tool",
)
class NoTriggerCondition:
    def check(self, registry: ToolRegistry, ctx: RuleContext) -> Iterable[Diagnostic]:
        for tool in registry.tools:
            desc = (tool.description or "").strip()
            if not desc:
                continue
            if _TRIGGER_RE.search(desc):
                continue
            yield Diagnostic(
                rule_id="MP023",
                rule_name="no-trigger-condition",
                category=Category.DESCRIPTION,
                severity=Severity.NOTE,
                message=(
                    f"tool `{tool.name}` description has no trigger condition "
                    "(`use this when…`, `best for…`)"
                ),
                file=tool.file,
                line=tool.line,
                col=tool.col,
                tool_name=tool.name,
                docs_url=docs_url("MP023"),
                hint=(
                    "add a sentence describing the conditions under which an "
                    "agent should pick this tool over alternatives"
                ),
            )
