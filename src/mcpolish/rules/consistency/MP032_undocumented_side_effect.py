"""MP032 - LLM-judged undocumented side effect.

Li et al. flag 1,326 servers where a tool described as a *read* in fact
performed a write or delete. We give the judge model the description and a
short heuristic about the function body (decorators / function name pattern
suggesting mutation) and ask whether they agree.
"""

from __future__ import annotations

import re
from typing import Iterable

from mcpolish.rules.base import RuleContext, docs_url
from mcpolish.rules.registry import register
from mcpolish.types import Category, Diagnostic, Severity, ToolRegistry

_MUTATING_VERBS = re.compile(
    r"\b(create|write|delete|drop|insert|update|patch|put|post|"
    r"send|push|publish|kill|terminate|destroy|remove)\b",
    re.IGNORECASE,
)
_READ_DESCRIPTION = re.compile(
    r"\b(read|fetch|get|return|query|inspect|view|browse|search)\b",
    re.IGNORECASE,
)

_PROMPT_TEMPLATE = """\
You are auditing an MCP tool for undocumented side effects.

Tool: {tool_name}
Description: \"\"\"{description}\"\"\"

The tool's NAME suggests it may modify state (verb: {detected_verb}), but
the description reads as a read-only operation. Does the description
acknowledge the side effect (writes / deletes / external calls)?

Reply on one line: "OK" or "MISSING: <one-sentence summary of the missing
side effect>".
"""


@register(
    "MP032",
    name="undocumented-side-effect",
    category=Category.CONSISTENCY,
    severity=Severity.ERROR,
    summary="LLM judge: tool may have undocumented mutating side effects",
    llm_gated=True,
)
class UndocumentedSideEffect:
    def check(self, registry: ToolRegistry, ctx: RuleContext) -> Iterable[Diagnostic]:
        client = ctx.llm
        if client is None:
            return
        for tool in registry.tools:
            mutating = _MUTATING_VERBS.search(tool.name)
            if not mutating:
                continue
            desc = tool.description or ""
            if _MUTATING_VERBS.search(desc):
                continue  # already acknowledges it
            if not _READ_DESCRIPTION.search(desc):
                continue  # not specifically read-flavoured
            verdict = client.judge(
                rule_id="MP032",
                prompt=_PROMPT_TEMPLATE.format(
                    tool_name=tool.name,
                    description=desc,
                    detected_verb=mutating.group(0),
                ),
            )
            if verdict.startswith("MISSING"):
                summary = verdict.split(":", 1)[-1].strip() or "undocumented side effect"
                yield Diagnostic(
                    rule_id="MP032",
                    rule_name="undocumented-side-effect",
                    category=Category.CONSISTENCY,
                    severity=Severity.ERROR,
                    message=(
                        f"tool `{tool.name}` likely has an undocumented side "
                        f"effect: {summary}"
                    ),
                    file=tool.file,
                    line=tool.line,
                    col=tool.col,
                    tool_name=tool.name,
                    docs_url=docs_url("MP032"),
                )
