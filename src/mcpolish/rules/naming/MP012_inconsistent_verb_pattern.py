"""MP012 - verbs across tools in the same server should be consistent.

Mixing `fetch_user`, `get_post`, `retrieve_comment` confuses agents that
rely on verb regularity to predict the right tool. Flag any tool whose
leading verb is a synonym of the modal verb used by the rest of the server.
"""

from __future__ import annotations

import re
from collections import Counter
from typing import Iterable

from mcpolish.rules.base import RuleContext, docs_url
from mcpolish.rules.registry import register
from mcpolish.types import Category, Diagnostic, Severity, ToolRegistry

_TOKEN = re.compile(r"[_\-]+")

# Verbs that mean roughly the same thing. The modal in each cluster is the
# canonical form we recommend.
_VERB_SYNONYMS: dict[str, str] = {
    "fetch": "get",
    "retrieve": "get",
    "read": "get",
    "obtain": "get",
    "find": "get",
    "lookup": "get",
    "remove": "delete",
    "destroy": "delete",
    "drop": "delete",
    "make": "create",
    "new": "create",
    "add": "create",
    "modify": "update",
    "change": "update",
    "edit": "update",
    "set": "update",
    "list": "list",
    "enumerate": "list",
}


@register(
    "MP012",
    name="inconsistent-verb-pattern",
    category=Category.NAMING,
    severity=Severity.WARNING,
    summary="leading verb is a synonym of the modal verb used elsewhere in this server",
)
class InconsistentVerbPattern:
    def check(self, registry: ToolRegistry, ctx: RuleContext) -> Iterable[Diagnostic]:
        if len(registry.tools) < 2:
            return
        canonical_counts: Counter[str] = Counter()
        for tool in registry.tools:
            verb = _leading_verb(tool.name)
            if verb is None:
                continue
            canonical_counts[_VERB_SYNONYMS.get(verb, verb)] += 1
        if not canonical_counts:
            return
        # Find clusters where multiple words map to the same canonical verb.
        for tool in registry.tools:
            verb = _leading_verb(tool.name)
            if verb is None:
                continue
            canonical = _VERB_SYNONYMS.get(verb, verb)
            if canonical == verb:
                continue
            # Only flag when the canonical form is also used elsewhere in
            # the server - otherwise we have no evidence of inconsistency.
            if canonical_counts[canonical] >= 1 and any(
                _leading_verb(t.name) == canonical for t in registry.tools
            ):
                yield Diagnostic(
                    rule_id="MP012",
                    rule_name="inconsistent-verb-pattern",
                    category=Category.NAMING,
                    severity=Severity.WARNING,
                    message=(
                        f"tool `{tool.name}` uses verb `{verb}` while sibling tools "
                        f"use `{canonical}`"
                    ),
                    file=tool.file,
                    line=tool.line,
                    col=tool.col,
                    tool_name=tool.name,
                    docs_url=docs_url("MP012"),
                    hint=f"rename to `{canonical}_{'_'.join(_TOKEN.split(tool.name)[1:])}`",
                )


def _leading_verb(name: str) -> str | None:
    tokens = _TOKEN.split(name)
    if not tokens:
        return None
    return tokens[0].lower() or None
