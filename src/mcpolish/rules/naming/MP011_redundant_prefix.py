"""MP011 - server-name prefix inside the tool name is redundant.

MCP hosts already namespace tools by server. A tool called `memnex_search`
on server `memnex` shows up to the agent as `memnex/memnex_search`, which
wastes context tokens and adds noise.

The server namespace is derived from the registry's `server_name` /
`namespace` fields, with a fallback to the longest common prefix across
all tool names in the same registry.
"""

from __future__ import annotations

import re
from typing import Iterable

from mcpolish.rules.base import RuleContext, docs_url
from mcpolish.rules.registry import register
from mcpolish.types import Category, Diagnostic, Fix, Severity, ToolRegistry

_TOKEN_SPLIT = re.compile(r"[_\-]+")


@register(
    "MP011",
    name="redundant-prefix",
    category=Category.NAMING,
    severity=Severity.ERROR,
    summary="tool name redundantly repeats the server namespace",
    auto_fixable=True,
)
class RedundantPrefix:
    def check(self, registry: ToolRegistry, ctx: RuleContext) -> Iterable[Diagnostic]:
        cfg = ctx.rule_config("MP011")
        explicit = cfg.get("namespace") or registry.namespace or registry.server_name
        explicit = (explicit or "").lower().strip()
        candidates = {explicit} if explicit else set()
        # Also consider the longest shared token prefix across tools.
        common = _shared_prefix([t.name for t in registry.tools])
        if common:
            candidates.add(common.lower())
        candidates.discard("")
        for tool in registry.tools:
            tokens = _TOKEN_SPLIT.split(tool.name)
            if not tokens:
                continue
            first = tokens[0].lower()
            if first in candidates and len(tokens) > 1:
                stripped = "_".join(tokens[1:])
                yield Diagnostic(
                    rule_id="MP011",
                    rule_name="redundant-prefix",
                    category=Category.NAMING,
                    severity=Severity.ERROR,
                    message=(
                        f"tool `{tool.name}` redundantly starts with the server "
                        f"namespace `{first}` - agents see this as `{first}/{tool.name}`"
                    ),
                    file=tool.file,
                    line=tool.line,
                    col=tool.col,
                    tool_name=tool.name,
                    docs_url=docs_url("MP011"),
                    hint=f"rename to `{stripped}`",
                    fix=Fix(description=f"rename to {stripped}", safe=False),
                )


def _shared_prefix(names: list[str]) -> str:
    if len(names) < 2:
        return ""
    parts = [_TOKEN_SPLIT.split(n) for n in names]
    first_tokens = {p[0] for p in parts if p}
    if len(first_tokens) == 1:
        return next(iter(first_tokens))
    return ""
