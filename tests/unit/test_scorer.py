"""Scorer + badge generator."""

from __future__ import annotations

from mcpolish.score.badge import render_badge
from mcpolish.score.scorer import compute_score
from mcpolish.types import Category, Diagnostic, Severity


def _diag(severity: Severity, category: Category = Category.NAMING) -> Diagnostic:
    return Diagnostic(
        rule_id="MP010",
        rule_name="x",
        category=category,
        severity=severity,
        message="x",
        file="t.py",
        docs_url="",
    )


def test_clean_is_100():
    assert compute_score([], tool_count=3) == 100


def test_floor_at_zero():
    diagnostics = [_diag(Severity.ERROR) for _ in range(50)]
    assert compute_score(diagnostics, tool_count=1) == 0


def test_warnings_count_less_than_errors():
    score_errors = compute_score([_diag(Severity.ERROR)] * 3, tool_count=3)
    score_warns = compute_score([_diag(Severity.WARNING)] * 3, tool_count=3)
    assert score_warns > score_errors


def test_badge_contains_score():
    svg = render_badge(82)
    assert "82/100" in svg
    assert "mcpolish" in svg
