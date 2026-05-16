"""MP030 - declared type in inputSchema disagrees with the description.

A param typed `string` whose description says "number of results" misleads
the agent into sending a stringified number, or a string when the function
will reject it. Cheap static check, no LLM required.
"""

from __future__ import annotations

import re
from typing import Iterable

from mcpolish.rules.base import RuleContext, docs_url
from mcpolish.rules.registry import register
from mcpolish.types import Category, Diagnostic, Severity, ToolRegistry

# Keyword → expected JSON-Schema type. If the description has a keyword from
# the left column and the schema type isn't in the right set, that's a hit.
_NUMERIC_HINTS = re.compile(
    r"\b(number|count|amount|quantity|integer|float|size|limit|"
    r"page|offset|index|ratio|percent|percentage)\b",
    re.IGNORECASE,
)
_BOOL_HINTS = re.compile(
    r"\b(true/false|yes/no|toggle|enable|disable|whether)\b",
    re.IGNORECASE,
)
_ARRAY_HINTS = re.compile(
    r"\b(list of|array of|sequence of|set of|each item)\b",
    re.IGNORECASE,
)


@register(
    "MP030",
    name="param-type-mismatch",
    category=Category.CONSISTENCY,
    severity=Severity.ERROR,
    summary="parameter type disagrees with its description",
)
class ParamTypeMismatch:
    def check(self, registry: ToolRegistry, ctx: RuleContext) -> Iterable[Diagnostic]:
        for tool in registry.tools:
            for p in tool.params:
                desc = p.description or ""
                if not desc:
                    continue
                expected = _expected_types(desc)
                if not expected:
                    continue
                actual = p.type or ""
                if actual and actual not in expected:
                    yield Diagnostic(
                        rule_id="MP030",
                        rule_name="param-type-mismatch",
                        category=Category.CONSISTENCY,
                        severity=Severity.ERROR,
                        message=(
                            f"tool `{tool.name}` param `{p.name}` is typed "
                            f"`{actual}` but described as something requiring "
                            f"{'/'.join(sorted(expected))}"
                        ),
                        file=tool.file,
                        line=tool.line,
                        col=tool.col,
                        tool_name=tool.name,
                        docs_url=docs_url("MP030"),
                        hint=(
                            "either rewrite the description to match the type "
                            "or update the schema to the expected type"
                        ),
                    )


def _expected_types(description: str) -> set[str]:
    expected: set[str] = set()
    if _NUMERIC_HINTS.search(description):
        expected.update({"integer", "number"})
    if _BOOL_HINTS.search(description):
        expected.add("boolean")
    if _ARRAY_HINTS.search(description):
        expected.add("array")
    return expected
