"""Rule selection / ignore expansion."""

from __future__ import annotations

from mcpolish.rules.registry import _expand_ids, filter_rules


def test_expand_single():
    assert _expand_ids(["MP010"]) == {"MP010"}


def test_expand_range():
    out = _expand_ids(["MP001-MP005"])
    assert "MP001" in out and "MP005" in out and "MP003" in out


def test_filter_ignore():
    rules = filter_rules(ignore=["MP010"])
    assert all(r.id != "MP010" for r in rules)


def test_filter_select():
    rules = filter_rules(select=["MP001"])
    assert {r.id for r in rules} == {"MP001"}


def test_llm_rules_hidden_by_default():
    rules = filter_rules()
    assert all(not r.llm_gated for r in rules)


def test_llm_rules_included_when_enabled():
    rules = filter_rules(llm_enabled=True)
    assert any(r.llm_gated for r in rules)
