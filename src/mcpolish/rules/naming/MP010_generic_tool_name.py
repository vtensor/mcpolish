"""MP010 - flag overly generic tool names.

Names like `search`, `get`, `run` collide trivially across servers and give
the agent no signal about *what kind of thing* the tool does. Wang et al.
(2026) call this the "low information name" smell; it is one of the four
naming-class smells in the paper's taxonomy.
"""

from __future__ import annotations

from typing import Iterable

from mcpolish.rules.base import RuleContext, docs_url
from mcpolish.rules.registry import register
from mcpolish.types import Category, Diagnostic, Severity, ToolRegistry

DEFAULT_GENERIC: frozenset[str] = frozenset(
    {
        "search",
        "query",
        "get",
        "list",
        "fetch",
        "run",
        "do",
        "call",
        "execute",
        "process",
        "handle",
        "request",
        "send",
        "load",
        "save",
        "update",
        "delete",
        "create",
        "read",
        "write",
        "go",
    }
)


@register(
    "MP010",
    name="generic-tool-name",
    category=Category.NAMING,
    severity=Severity.WARNING,
    summary="tool name is too generic to disambiguate from other servers' tools",
)
class GenericToolName:
    def check(self, registry: ToolRegistry, ctx: RuleContext) -> Iterable[Diagnostic]:
        cfg = ctx.rule_config("MP010")
        allow = set(cfg.get("allow", []))
        extra = set(cfg.get("extra", []))
        generic = (DEFAULT_GENERIC | extra) - allow
        for tool in registry.tools:
            if tool.name.lower() in generic:
                yield Diagnostic(
                    rule_id="MP010",
                    rule_name="generic-tool-name",
                    category=Category.NAMING,
                    severity=Severity.WARNING,
                    message=f"tool name `{tool.name}` is too generic",
                    file=tool.file,
                    line=tool.line,
                    col=tool.col,
                    tool_name=tool.name,
                    docs_url=docs_url("MP010"),
                    hint=(
                        f"consider a more specific name like `{tool.name}_<noun>` "
                        f"or `<verb>_<thing>`"
                    ),
                )
