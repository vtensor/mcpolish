"""Top-level public API. Library users call `lint()` and `score()`."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from mcpolish.config.loader import MCPolishConfig, load_config
from mcpolish.discover.ir import build_registry
from mcpolish.exceptions import RegistryError
from mcpolish.logging import get_logger
from mcpolish.registry.snapshot import Snapshot, load_bundled
from mcpolish.rules.base import RuleContext
from mcpolish.rules.registry import filter_rules, run_rules
from mcpolish.score.scorer import compute_score
from mcpolish.types import Diagnostic, Severity, ToolRegistry

log = get_logger(__name__)


@dataclass
class LintReport:
    diagnostics: tuple[Diagnostic, ...]
    registry: ToolRegistry
    score: int
    error_count: int
    warning_count: int
    note_count: int

    def has_errors(self) -> bool:
        return self.error_count > 0


def lint(
    target: str | Path,
    *,
    config: MCPolishConfig | None = None,
    select: list[str] | None = None,
    ignore: list[str] | None = None,
    llm: object | None = None,
    snapshot: Snapshot | None = None,
    use_bundled_snapshot: bool = True,
) -> LintReport:
    """Run discovery + rules. Returns a `LintReport` ready for any reporter."""
    target_path = Path(target)
    cfg = config or load_config(target_path)
    registry = build_registry(
        target_path,
        server_name=cfg.server_name,
        namespace=cfg.namespace,
    )

    if snapshot is None and use_bundled_snapshot and cfg.registry != "off":
        try:
            snapshot = load_bundled()
        except RegistryError as exc:
            log.warning("could not load bundled snapshot: %s", exc)
            snapshot = None

    ctx = RuleContext(config=cfg.rules, snapshot=snapshot, llm=llm)
    rules = filter_rules(
        select=select or cfg.select or None,
        ignore=ignore or cfg.ignore or None,
        llm_enabled=llm is not None,
    )
    diagnostics = run_rules(registry, ctx, rules)
    return _to_report(diagnostics, registry, weights=cfg.score_weights)


def score(target: str | Path, **kwargs: object) -> int:
    return lint(target, **kwargs).score  # type: ignore[arg-type]


def _to_report(
    diagnostics: list[Diagnostic],
    registry: ToolRegistry,
    *,
    weights,
) -> LintReport:
    err = sum(1 for d in diagnostics if d.severity == Severity.ERROR)
    warn = sum(1 for d in diagnostics if d.severity == Severity.WARNING)
    note = sum(1 for d in diagnostics if d.severity == Severity.NOTE)
    s = compute_score(diagnostics, tool_count=len(registry.tools), weights=weights)
    return LintReport(
        diagnostics=tuple(diagnostics),
        registry=registry,
        score=s,
        error_count=err,
        warning_count=warn,
        note_count=note,
    )
