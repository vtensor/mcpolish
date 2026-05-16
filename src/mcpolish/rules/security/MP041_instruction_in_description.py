"""MP041 - description tries to give the agent operator-level instructions.

Tool-poisoning attacks (mcp-scan) plant instructions in descriptions like
"ignore previous instructions" or "you must always". These belong in the
host's system prompt, never in a tool description.
"""

from __future__ import annotations

import re
from typing import Iterable

from mcpolish.rules.base import RuleContext, docs_url
from mcpolish.rules.registry import register
from mcpolish.types import Category, Diagnostic, Severity, ToolRegistry

_INJECTION_PATTERNS = re.compile(
    r"\b("
    r"ignore (?:all )?previous(?: instructions)?|"
    r"disregard (?:the )?(?:above|previous)|"
    r"you must always|"
    r"you must never|"
    r"override (?:the )?system|"
    r"system prompt|"
    r"<\|.*?\|>|"
    r"</?(?:s|im_start|im_end)>"
    r")",
    re.IGNORECASE,
)


@register(
    "MP041",
    name="instruction-in-description",
    category=Category.SECURITY,
    severity=Severity.ERROR,
    summary="description contains operator-style instructions or chat-template tokens",
)
class InstructionInDescription:
    def check(self, registry: ToolRegistry, ctx: RuleContext) -> Iterable[Diagnostic]:
        for tool in registry.tools:
            desc = tool.description or ""
            match = _INJECTION_PATTERNS.search(desc)
            if not match:
                continue
            yield Diagnostic(
                rule_id="MP041",
                rule_name="instruction-in-description",
                category=Category.SECURITY,
                severity=Severity.ERROR,
                message=(
                    f"tool `{tool.name}` description contains operator-style "
                    f"instruction `{match.group(0)}` - likely tool poisoning"
                ),
                file=tool.file,
                line=tool.line,
                col=tool.col,
                tool_name=tool.name,
                docs_url=docs_url("MP041"),
                hint=(
                    "tool descriptions describe behaviour, not commands to the "
                    "agent - remove the instruction"
                ),
            )
