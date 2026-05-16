"""MP031 - LLM-judged mismatch between param name/type and description.

Li et al. (2026, arXiv:2602.03580) found 3,449 servers where a parameter's
described meaning didn't match how it was used in the code. Catching that
end-to-end requires understanding *intent*, so this rule is LLM-gated.
"""

from __future__ import annotations

from typing import Iterable

from mcpolish.rules.base import RuleContext, docs_url
from mcpolish.rules.registry import register
from mcpolish.types import Category, Diagnostic, Severity, ToolRegistry

_PROMPT_TEMPLATE = """\
You are auditing an MCP tool parameter for consistency.

Tool: {tool_name}
Parameter name: {param_name}
Declared JSON-Schema type: {param_type}
Description: \"\"\"{param_desc}\"\"\"

Does the parameter NAME unambiguously describe what the agent should pass,
and is the DESCRIPTION consistent with both the name and the type?

Reply on one line: "OK" or "MISMATCH: <reason>".
"""


@register(
    "MP031",
    name="param-meaning-mismatch",
    category=Category.CONSISTENCY,
    severity=Severity.WARNING,
    summary="LLM judge: param name, type, and description disagree on meaning",
    llm_gated=True,
)
class ParamMeaningMismatch:
    def check(self, registry: ToolRegistry, ctx: RuleContext) -> Iterable[Diagnostic]:
        client = ctx.llm
        if client is None:
            return
        for tool in registry.tools:
            for p in tool.params:
                if not p.description:
                    continue
                verdict = client.judge(
                    rule_id="MP031",
                    prompt=_PROMPT_TEMPLATE.format(
                        tool_name=tool.name,
                        param_name=p.name,
                        param_type=p.type or "unknown",
                        param_desc=p.description,
                    ),
                )
                if verdict.startswith("MISMATCH"):
                    reason = verdict.split(":", 1)[-1].strip() or "mismatch"
                    yield Diagnostic(
                        rule_id="MP031",
                        rule_name="param-meaning-mismatch",
                        category=Category.CONSISTENCY,
                        severity=Severity.WARNING,
                        message=(
                            f"tool `{tool.name}` param `{p.name}` has a "
                            f"name/type/description mismatch: {reason}"
                        ),
                        file=tool.file,
                        line=tool.line,
                        col=tool.col,
                        tool_name=tool.name,
                        docs_url=docs_url("MP031"),
                    )
