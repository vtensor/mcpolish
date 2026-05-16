"""Naming rules: MP010 - MP014."""

from __future__ import annotations

from mcpolish.registry.snapshot import Snapshot
from mcpolish.rules.base import RuleContext
from mcpolish.rules.naming.MP010_generic_tool_name import GenericToolName
from mcpolish.rules.naming.MP011_redundant_prefix import RedundantPrefix
from mcpolish.rules.naming.MP012_inconsistent_verb_pattern import (
    InconsistentVerbPattern,
)
from mcpolish.rules.naming.MP013_name_collision_cross_server import (
    NameCollisionCrossServer,
)
from mcpolish.rules.naming.MP014_snake_vs_camel import SnakeVsCamel


def test_mp010_generic_name(registry_factory, tool_factory, ctx):
    reg = registry_factory(tool_factory(name="search"))
    diags = list(GenericToolName().check(reg, ctx))
    assert [d.rule_id for d in diags] == ["MP010"]


def test_mp010_allow_list_silences(registry_factory, tool_factory):
    reg = registry_factory(tool_factory(name="search"))
    ctx = RuleContext(config={"MP010": {"allow": ["search"]}})
    assert list(GenericToolName().check(reg, ctx)) == []


def test_mp011_namespace_prefix(registry_factory, tool_factory, ctx):
    reg = registry_factory(
        tool_factory(name="memnex_search_memory"),
        namespace="memnex",
        server_name="memnex",
    )
    diags = list(RedundantPrefix().check(reg, ctx))
    assert diags
    assert "memnex" in diags[0].message


def test_mp011_silent_for_clean(registry_factory, tool_factory, ctx):
    reg = registry_factory(
        tool_factory(name="search_memory"),
        namespace="memnex",
    )
    assert list(RedundantPrefix().check(reg, ctx)) == []


def test_mp012_inconsistent_verbs(registry_factory, tool_factory, ctx):
    reg = registry_factory(
        tool_factory(name="get_user"),
        tool_factory(name="fetch_post"),
        tool_factory(name="retrieve_comment"),
    )
    diags = list(InconsistentVerbPattern().check(reg, ctx))
    flagged = {d.tool_name for d in diags}
    assert {"fetch_post", "retrieve_comment"}.issubset(flagged)


def test_mp013_cross_server_collision(registry_factory, tool_factory):
    snapshot = Snapshot(
        {
            "tools": [
                {"tool_name": "search", "servers": ["alice", "bob", "carol"]},
            ]
        }
    )
    ctx = RuleContext(snapshot=snapshot)
    reg = registry_factory(tool_factory(name="search"))
    diags = list(NameCollisionCrossServer().check(reg, ctx))
    assert diags


def test_mp013_ignores_own_namespace(registry_factory, tool_factory):
    snapshot = Snapshot(
        {"tools": [{"tool_name": "search", "servers": ["memnex"]}]}
    )
    ctx = RuleContext(snapshot=snapshot)
    reg = registry_factory(tool_factory(name="search"), namespace="memnex")
    assert list(NameCollisionCrossServer().check(reg, ctx)) == []


def test_mp014_mixed_casing(registry_factory, tool_factory, ctx):
    reg = registry_factory(
        tool_factory(name="search_items"),
        tool_factory(name="search_items"),
        tool_factory(name="getThings"),
    )
    diags = list(SnakeVsCamel().check(reg, ctx))
    assert any(d.tool_name == "getThings" for d in diags)
