"""MP005 - the declared inputSchema must validate as JSON Schema 2020-12."""

from __future__ import annotations

from typing import Iterable

import jsonschema
from jsonschema import Draft202012Validator

from mcpolish.rules.base import RuleContext, docs_url
from mcpolish.rules.registry import register
from mcpolish.types import Category, Diagnostic, Severity, ToolRegistry


@register(
    "MP005",
    name="valid-json-schema",
    category=Category.SCHEMA,
    severity=Severity.ERROR,
    summary="inputSchema must be a valid JSON Schema 2020-12 object",
)
class ValidJsonSchema:
    def check(self, registry: ToolRegistry, ctx: RuleContext) -> Iterable[Diagnostic]:
        for tool in registry.tools:
            schema = tool.input_schema
            if not schema:
                continue
            try:
                Draft202012Validator.check_schema(schema)
            except jsonschema.SchemaError as exc:
                yield Diagnostic(
                    rule_id="MP005",
                    rule_name="valid-json-schema",
                    category=Category.SCHEMA,
                    severity=Severity.ERROR,
                    message=f"tool `{tool.name}` inputSchema is invalid: {exc.message}",
                    file=tool.file,
                    line=tool.line,
                    col=tool.col,
                    tool_name=tool.name,
                    docs_url=docs_url("MP005"),
                )
                continue
            if schema.get("type") not in (None, "object"):
                yield Diagnostic(
                    rule_id="MP005",
                    rule_name="valid-json-schema",
                    category=Category.SCHEMA,
                    severity=Severity.ERROR,
                    message=(
                        f"tool `{tool.name}` inputSchema.type must be 'object' "
                        f"(got {schema.get('type')!r})"
                    ),
                    file=tool.file,
                    line=tool.line,
                    col=tool.col,
                    tool_name=tool.name,
                    docs_url=docs_url("MP005"),
                )
