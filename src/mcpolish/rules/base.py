"""Rule Protocol + RuleContext.

A rule is a pure function over the IR. No I/O in `check()`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable, Protocol, runtime_checkable

from mcpolish.types import Category, Diagnostic, Severity, ToolRegistry


DOCS_BASE = "https://mcpolish.dev/rules"


@dataclass
class RuleContext:
    """Per-scan context passed to every rule.

    Holds config overrides, the snapshot data, and the optional LLM client.
    Rules read from `ctx.rule_config(rule_id)` instead of touching globals.
    """

    config: dict[str, Any] = field(default_factory=dict)
    snapshot: Any = None  # type: registry.snapshot.Snapshot - late-bound
    llm: Any = None  # type: llm.client.LLMClient - late-bound

    def rule_config(self, rule_id: str) -> dict[str, Any]:
        per_rule = self.config.get(rule_id)
        if isinstance(per_rule, dict):
            return per_rule
        return {}


@runtime_checkable
class Rule(Protocol):
    id: str
    name: str
    category: Category
    severity_default: Severity
    llm_gated: bool
    auto_fixable: bool
    summary: str

    def check(
        self, registry: ToolRegistry, ctx: RuleContext
    ) -> Iterable[Diagnostic]: ...


def docs_url(rule_id: str) -> str:
    return f"{DOCS_BASE}/{rule_id}"
