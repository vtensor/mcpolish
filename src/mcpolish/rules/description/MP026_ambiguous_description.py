"""MP026 - LLM-judged ambiguity in the description.

Skipped unless --llm enables LLM-gated rules. Asks the configured judge
model: "given only this description, can you tell what this tool does and
when to call it?". A NO response yields a diagnostic.
"""

from __future__ import annotations

from typing import Iterable

from mcpolish.rules.base import RuleContext, docs_url
from mcpolish.rules.registry import register
from mcpolish.types import Category, Diagnostic, Severity, ToolRegistry

_PROMPT_TEMPLATE = """\
You are evaluating an MCP tool description for agent comprehension.

Tool name: {name}
Description:
\"\"\"
{description}
\"\"\"

Answer YES if a competent LLM agent could reliably tell (a) what this tool
does and (b) when to call it, given ONLY the description above. Otherwise
answer NO and give a one-sentence reason.

Reply on one line: "YES" or "NO: <reason>".
"""


@register(
    "MP026",
    name="ambiguous-description",
    category=Category.DESCRIPTION,
    severity=Severity.WARNING,
    summary="LLM judge: description is ambiguous about what the tool does or when to call it",
    llm_gated=True,
)
class AmbiguousDescription:
    def check(self, registry: ToolRegistry, ctx: RuleContext) -> Iterable[Diagnostic]:
        client = ctx.llm
        if client is None:
            return
        for tool in registry.tools:
            desc = (tool.description or "").strip()
            if not desc:
                continue
            verdict = client.judge(
                rule_id="MP026",
                prompt=_PROMPT_TEMPLATE.format(name=tool.name, description=desc),
            )
            if verdict.startswith("NO"):
                reason = verdict[3:].lstrip(": ").strip() or "ambiguous"
                yield Diagnostic(
                    rule_id="MP026",
                    rule_name="ambiguous-description",
                    category=Category.DESCRIPTION,
                    severity=Severity.WARNING,
                    message=f"tool `{tool.name}` description is ambiguous: {reason}",
                    file=tool.file,
                    line=tool.line,
                    col=tool.col,
                    tool_name=tool.name,
                    docs_url=docs_url("MP026"),
                )
