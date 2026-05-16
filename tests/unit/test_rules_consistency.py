"""Consistency rules: MP030 - MP033."""

from __future__ import annotations

from mcpolish.rules.consistency.MP030_param_type_mismatch import ParamTypeMismatch
from mcpolish.rules.consistency.MP033_duplicate_tool_description import (
    DuplicateToolDescription,
)
from mcpolish.types import ParamDecl


def test_mp030_string_typed_count(registry_factory, tool_factory, ctx):
    reg = registry_factory(
        tool_factory(
            params=(
                ParamDecl(
                    name="limit",
                    type="string",
                    description="number of results to return",
                ),
            )
        )
    )
    diags = list(ParamTypeMismatch().check(reg, ctx))
    assert [d.rule_id for d in diags] == ["MP030"]


def test_mp030_silent_for_matching(registry_factory, tool_factory, ctx):
    reg = registry_factory(
        tool_factory(
            params=(
                ParamDecl(
                    name="limit",
                    type="integer",
                    description="number of results to return",
                ),
            )
        )
    )
    assert list(ParamTypeMismatch().check(reg, ctx)) == []


def test_mp033_duplicate(registry_factory, tool_factory, ctx):
    a = tool_factory(name="alpha", description="Returns the same long-enough description.")
    b = tool_factory(name="beta", description="Returns the same long-enough description.")
    reg = registry_factory(a, b)
    diags = list(DuplicateToolDescription().check(reg, ctx))
    names = {d.tool_name for d in diags}
    assert names == {"alpha", "beta"}
