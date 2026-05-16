"""MP033 - two tools in the same server share the same description.

If two tools have identical (or near-identical) descriptions the agent has
no signal to pick between them. Cheap normalised-text comparison.
"""

from __future__ import annotations

import re
from collections import defaultdict
from typing import Iterable

from mcpolish.rules.base import RuleContext, docs_url
from mcpolish.rules.registry import register
from mcpolish.types import Category, Diagnostic, Severity, ToolRegistry

_NORMALISE = re.compile(r"\s+")


@register(
    "MP033",
    name="duplicate-tool-description",
    category=Category.CONSISTENCY,
    severity=Severity.ERROR,
    summary="two tools share the same description verbatim",
)
class DuplicateToolDescription:
    def check(self, registry: ToolRegistry, ctx: RuleContext) -> Iterable[Diagnostic]:
        buckets: dict[str, list[int]] = defaultdict(list)
        for i, tool in enumerate(registry.tools):
            desc = (tool.description or "").strip()
            if len(desc) < 20:
                continue
            key = _NORMALISE.sub(" ", desc.lower())
            buckets[key].append(i)
        for indices in buckets.values():
            if len(indices) < 2:
                continue
            others = [registry.tools[i].name for i in indices]
            for i in indices:
                tool = registry.tools[i]
                duplicates = [n for n in others if n != tool.name]
                yield Diagnostic(
                    rule_id="MP033",
                    rule_name="duplicate-tool-description",
                    category=Category.CONSISTENCY,
                    severity=Severity.ERROR,
                    message=(
                        f"tool `{tool.name}` shares its description with: "
                        f"{', '.join(duplicates)}"
                    ),
                    file=tool.file,
                    line=tool.line,
                    col=tool.col,
                    tool_name=tool.name,
                    docs_url=docs_url("MP033"),
                    hint="differentiate what each tool does so agents can pick correctly",
                )
