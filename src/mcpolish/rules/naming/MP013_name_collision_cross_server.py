"""MP013 - cross-server name collisions.

Wang et al. (2026): 73% of analysed servers share at least one tool name
with another server. When two `search` tools are mounted in the same host
session, the model has to guess from descriptions alone - exactly the
failure mode the rest of MCPolish exists to prevent.

The snapshot is bundled in OSS (quarterly) and refreshed weekly in SaaS.
"""

from __future__ import annotations

from typing import Iterable

from mcpolish.rules.base import RuleContext, docs_url
from mcpolish.rules.registry import register
from mcpolish.types import Category, Diagnostic, Severity, ToolRegistry


@register(
    "MP013",
    name="name-collision-cross-server",
    category=Category.NAMING,
    severity=Severity.WARNING,
    summary="tool name collides with a tool exported by other public MCP servers",
)
class NameCollisionCrossServer:
    def check(self, registry: ToolRegistry, ctx: RuleContext) -> Iterable[Diagnostic]:
        snapshot = ctx.snapshot
        if snapshot is None:
            return
        cfg = ctx.rule_config("MP013")
        threshold = int(cfg.get("min_collisions", 2))
        own_namespace = (registry.namespace or registry.server_name or "").lower()
        for tool in registry.tools:
            collisions = snapshot.servers_for_tool(tool.name)
            # Exclude ourselves from the collision set.
            external = [s for s in collisions if s.lower() != own_namespace]
            if len(external) >= threshold:
                sample = ", ".join(external[:3])
                more = f" (+{len(external) - 3} more)" if len(external) > 3 else ""
                yield Diagnostic(
                    rule_id="MP013",
                    rule_name="name-collision-cross-server",
                    category=Category.NAMING,
                    severity=Severity.WARNING,
                    message=(
                        f"tool `{tool.name}` collides with {len(external)} public "
                        f"server(s): {sample}{more}"
                    ),
                    file=tool.file,
                    line=tool.line,
                    col=tool.col,
                    tool_name=tool.name,
                    docs_url=docs_url("MP013"),
                    hint=(
                        "pick a more specific name - agents in multi-server sessions "
                        "must disambiguate on description alone when names collide"
                    ),
                )
