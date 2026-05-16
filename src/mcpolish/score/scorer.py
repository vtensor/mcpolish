"""Compute the 0-100 weighted score from a list of diagnostics."""

from __future__ import annotations

from typing import Iterable

from mcpolish.config.loader import ScoreWeights
from mcpolish.types import Category, Diagnostic, Severity

_SEVERITY_POINTS: dict[Severity, float] = {
    Severity.ERROR: 5.0,
    Severity.WARNING: 2.0,
    Severity.NOTE: 0.5,
}

_DEFAULT_CATEGORY_WEIGHTS: dict[Category, float] = {
    Category.SCHEMA: 0.20,
    Category.NAMING: 0.30,
    Category.DESCRIPTION: 0.30,
    Category.CONSISTENCY: 0.15,
    Category.SECURITY: 0.05,
}


def compute_score(
    diagnostics: Iterable[Diagnostic],
    *,
    tool_count: int,
    weights: ScoreWeights | None = None,
) -> int:
    """0-100. Higher is better. Calibration: a 5-tool server with one error
    per tool lands around 50. Zero diagnostics ⇒ 100."""
    cat_weights = _resolve_weights(weights)
    # Normalise category weights to a constant total so the scale doesn't
    # silently shift when a user reweights them.
    total = sum(cat_weights.values()) or 1.0
    norm = {k: v / total for k, v in cat_weights.items()}
    penalty = 0.0
    for d in diagnostics:
        sev = _SEVERITY_POINTS.get(d.severity, 0.0)
        cat = norm.get(d.category, 0.1)
        penalty += sev * cat
    # Per-tool amortisation keeps large servers fair, but the multiplier
    # ensures a handful of issues moves the needle.
    denom = max(1.0, float(tool_count) ** 0.5)
    score = 100.0 - (penalty / denom) * 8.0
    return max(0, min(100, int(round(score))))


def _resolve_weights(weights: ScoreWeights | None) -> dict[Category, float]:
    if weights is None:
        return _DEFAULT_CATEGORY_WEIGHTS
    return {
        Category.SCHEMA: weights.schema_,
        Category.NAMING: weights.naming,
        Category.DESCRIPTION: weights.description,
        Category.CONSISTENCY: weights.consistency,
        Category.SECURITY: weights.security,
    }
