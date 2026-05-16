"""MP040 - description contains hidden / zero-width characters.

A common prompt-injection pattern in MCP tool poisoning attacks (Invariant
Labs, May 2025) hides instructions inside zero-width Unicode or unusual
homoglyphs. Static catchable.
"""

from __future__ import annotations

import re
from typing import Iterable

from mcpolish.rules.base import RuleContext, docs_url
from mcpolish.rules.registry import register
from mcpolish.types import Category, Diagnostic, Severity, ToolRegistry

# Zero-width, bidi controls, and other typically-malicious invisible runs.
_INVISIBLE_RE = re.compile(
    r"["
    r"​-‏"   # zero-width + bidi marks
    r"‪-‮"   # LRE, RLE, PDF, LRO, RLO
    r"⁦-⁩"   # isolate controls
    r"﻿"          # BOM
    r"]"
)


@register(
    "MP040",
    name="hidden-prompt-injection",
    category=Category.SECURITY,
    severity=Severity.ERROR,
    summary="description contains zero-width or bidi-control characters",
)
class HiddenPromptInjection:
    def check(self, registry: ToolRegistry, ctx: RuleContext) -> Iterable[Diagnostic]:
        for tool in registry.tools:
            desc = tool.description or ""
            matches = _INVISIBLE_RE.findall(desc)
            if not matches:
                continue
            uniq = sorted({f"U+{ord(c):04X}" for c in matches})
            yield Diagnostic(
                rule_id="MP040",
                rule_name="hidden-prompt-injection",
                category=Category.SECURITY,
                severity=Severity.ERROR,
                message=(
                    f"tool `{tool.name}` description contains invisible character"
                    f"{'s' if len(uniq) > 1 else ''} {', '.join(uniq)} - possible "
                    "prompt-injection vector"
                ),
                file=tool.file,
                line=tool.line,
                col=tool.col,
                tool_name=tool.name,
                docs_url=docs_url("MP040"),
                hint="strip zero-width / bidi control characters from descriptions",
            )
