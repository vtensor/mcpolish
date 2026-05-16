"""MP004 - JSON-Schema 2020-12 requires `required` when any param is mandatory.

Skipped if all params are optional. Catches the easy mistake of forgetting
the `required` array when registering tools by raw schema literal.
"""

from __future__ import annotations

from typing import Iterable

from mcpolish.rules.base import RuleContext, docs_url
from mcpolish.rules.registry import register
from mcpolish.types import Category, Diagnostic, Severity, ToolRegistry


@register(
    "MP004",
    name="require-required-array",
    category=Category.SCHEMA,
    severity=Severity.WARNING,
    summary="declare required:[] when any parameter is mandatory",
)
class RequireRequiredArray:
    def check(self, registry: ToolRegistry, ctx: RuleContext) -> Iterable[Diagnostic]:
        for tool in registry.tools:
            schema = tool.input_schema or {}
            props = schema.get("properties") or {}
            if not isinstance(props, dict) or not props:
                continue
            has_required_key = "required" in schema
            mandatory = [p.name for p in tool.params if p.required]
            if mandatory and not schema.get("required"):
                # Decorator path: the signature has mandatory params but the
                # schema lost the required list somehow.
                message = (
                    f"tool `{tool.name}` has mandatory params {mandatory} but the "
                    "inputSchema is missing a `required` array"
                )
            elif tool.schema_is_explicit and not has_required_key:
                # Hand-written Tool() constructor that forgot to spell out the
                # required array. Agents cannot tell which params are mandatory.
                names = list(props.keys())
                message = (
                    f"tool `{tool.name}` inputSchema declares properties "
                    f"{names} but no `required` array. Add `required: []` "
                    "even when empty so agents can tell which params are "
                    "mandatory."
                )
            else:
                continue
            yield Diagnostic(
                rule_id="MP004",
                rule_name="require-required-array",
                category=Category.SCHEMA,
                severity=Severity.WARNING,
                message=message,
                file=tool.file,
                line=tool.line,
                col=tool.col,
                tool_name=tool.name,
                docs_url=docs_url("MP004"),
            )
