"""Description rules: MP020 - MP026."""

from __future__ import annotations

from mcpolish.rules.description.MP020_too_short import TooShort
from mcpolish.rules.description.MP021_too_long import TooLong
from mcpolish.rules.description.MP022_missing_example import MissingExample
from mcpolish.rules.description.MP023_no_trigger_condition import NoTriggerCondition
from mcpolish.rules.description.MP024_jargon_density import JargonDensity
from mcpolish.rules.description.MP025_useless_qualifier import UselessQualifier
from mcpolish.types import ParamDecl


def test_mp020_short(registry_factory, tool_factory, ctx):
    reg = registry_factory(tool_factory(description="too short"))
    assert [d.rule_id for d in TooShort().check(reg, ctx)] == ["MP020"]


def test_mp020_silent_when_long_enough(registry_factory, tool_factory, ctx):
    reg = registry_factory(
        tool_factory(description="x" * 80)
    )
    assert list(TooShort().check(reg, ctx)) == []


def test_mp021_long(registry_factory, tool_factory, ctx):
    reg = registry_factory(tool_factory(description="x" * 5000))
    assert [d.rule_id for d in TooLong().check(reg, ctx)] == ["MP021"]


def test_mp022_freeform_needs_example(registry_factory, tool_factory, ctx):
    reg = registry_factory(
        tool_factory(
            params=(
                ParamDecl(name="query", type="string", description="search", has_example=False),
                ParamDecl(name="page", type="integer", description="page #"),
            )
        )
    )
    diags = list(MissingExample().check(reg, ctx))
    # Only string params should be flagged.
    assert [d.message for d in diags if "query" in d.message]
    assert not any("page" in d.message for d in diags)


def test_mp023_no_trigger(registry_factory, tool_factory, ctx):
    reg = registry_factory(tool_factory(description="Does the thing without saying why."))
    assert [d.rule_id for d in NoTriggerCondition().check(reg, ctx)] == ["MP023"]


def test_mp023_silent_when_trigger_present(registry_factory, tool_factory, ctx):
    reg = registry_factory(
        tool_factory(description="Use this when the user asks for the time. Returns ISO 8601.")
    )
    assert list(NoTriggerCondition().check(reg, ctx)) == []


def test_mp024_jargon(registry_factory, tool_factory, ctx):
    reg = registry_factory(
        tool_factory(description="Calls UFS via TKN RPC; emits XYZ ABC FOO BAR.")
    )
    assert [d.rule_id for d in JargonDensity().check(reg, ctx)] == ["MP024"]


def test_mp025_qualifier(registry_factory, tool_factory, ctx):
    reg = registry_factory(
        tool_factory(description="Simply does the powerful thing very easily.")
    )
    diags = list(UselessQualifier().check(reg, ctx))
    assert diags and diags[0].rule_id == "MP025"
