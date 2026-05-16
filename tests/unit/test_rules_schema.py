"""Schema rules: MP001 - MP005."""

from __future__ import annotations

from mcpolish.rules.consistency.MP033_duplicate_tool_description import (
    DuplicateToolDescription,
)
from mcpolish.rules.schema.MP001_require_tool_description import RequireToolDescription
from mcpolish.rules.schema.MP002_require_param_description import RequireParamDescription
from mcpolish.rules.schema.MP003_require_return_schema import RequireReturnSchema
from mcpolish.rules.schema.MP004_require_required_array import RequireRequiredArray
from mcpolish.rules.schema.MP005_valid_json_schema import ValidJsonSchema
from mcpolish.types import ParamDecl


def test_mp001_empty_description(registry_factory, tool_factory, ctx):
    reg = registry_factory(tool_factory(description=""))
    diags = list(RequireToolDescription().check(reg, ctx))
    assert len(diags) == 1
    assert diags[0].rule_id == "MP001"


def test_mp001_ok_when_present(registry_factory, tool_factory, ctx):
    reg = registry_factory(tool_factory(description="Use this when looking up items by id."))
    assert list(RequireToolDescription().check(reg, ctx)) == []


def test_mp002_param_without_description(registry_factory, tool_factory, ctx):
    reg = registry_factory(
        tool_factory(
            params=(
                ParamDecl(name="x", type="string", description=None),
                ParamDecl(name="y", type="integer", description="ok"),
            )
        )
    )
    diags = list(RequireParamDescription().check(reg, ctx))
    assert [d.rule_id for d in diags] == ["MP002"]
    assert "x" in diags[0].message


def test_mp003_silent_when_returns_mentioned(registry_factory, tool_factory, ctx):
    reg = registry_factory(
        tool_factory(description="Use this when… Returns a list of objects.")
    )
    assert list(RequireReturnSchema().check(reg, ctx)) == []


def test_mp003_fires_when_silent_on_returns(registry_factory, tool_factory, ctx):
    reg = registry_factory(
        tool_factory(description="Use this when the user requests an item.")
    )
    assert [d.rule_id for d in RequireReturnSchema().check(reg, ctx)] == ["MP003"]


def test_mp004_missing_required_array(registry_factory, tool_factory, ctx):
    reg = registry_factory(
        tool_factory(
            params=(ParamDecl(name="x", type="string", required=True),),
            input_schema={"type": "object", "properties": {"x": {"type": "string"}}},
        )
    )
    diags = list(RequireRequiredArray().check(reg, ctx))
    assert [d.rule_id for d in diags] == ["MP004"]


def test_mp005_bad_schema(registry_factory, tool_factory, ctx):
    reg = registry_factory(
        tool_factory(input_schema={"type": "object", "properties": "not-a-dict"})
    )
    diags = list(ValidJsonSchema().check(reg, ctx))
    assert any(d.rule_id == "MP005" for d in diags)


def test_mp033_duplicate(registry_factory, tool_factory, ctx):
    a = tool_factory(name="a", description="Returns a list of all items in the workspace.")
    b = tool_factory(name="b", description="Returns a list of all items in the workspace.")
    reg = registry_factory(a, b)
    diags = list(DuplicateToolDescription().check(reg, ctx))
    assert {d.tool_name for d in diags} == {"a", "b"}
