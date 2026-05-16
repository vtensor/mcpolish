"""Apply fixes by walking diagnostics that have an attached Fix.

Each strategy is responsible for one rule_id. The engine sorts diagnostics
by reverse-line so multiple edits in the same file don't shift offsets.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from mcpolish.fix.strategies import ALL_STRATEGIES
from mcpolish.types import Diagnostic


@dataclass
class FixResult:
    file: str
    diagnostic_id: str
    applied: bool
    safe: bool
    reason: str = ""


def apply_fixes(
    diagnostics: Iterable[Diagnostic], *, unsafe: bool = False, dry_run: bool = False
) -> list[FixResult]:
    out: list[FixResult] = []
    diag_list = sorted(diagnostics, key=lambda d: (d.file, -d.line))
    for diag in diag_list:
        if diag.fix is None:
            continue
        if not diag.fix.safe and not unsafe:
            out.append(
                FixResult(
                    file=diag.file,
                    diagnostic_id=diag.rule_id,
                    applied=False,
                    safe=False,
                    reason="unsafe fix; requires --unsafe-fix",
                )
            )
            continue
        strategy = next(
            (s for s in ALL_STRATEGIES if s.applies(diag)), None
        )
        if strategy is None:
            out.append(
                FixResult(
                    file=diag.file,
                    diagnostic_id=diag.rule_id,
                    applied=False,
                    safe=diag.fix.safe,
                    reason="no strategy registered",
                )
            )
            continue
        path = Path(diag.file)
        new_source = strategy.apply(path, diag)
        if new_source is None:
            out.append(
                FixResult(
                    file=diag.file,
                    diagnostic_id=diag.rule_id,
                    applied=False,
                    safe=diag.fix.safe,
                    reason="strategy could not derive a fix",
                )
            )
            continue
        if not dry_run:
            path.write_text(new_source, encoding="utf-8")
        out.append(
            FixResult(
                file=diag.file,
                diagnostic_id=diag.rule_id,
                applied=True,
                safe=diag.fix.safe,
            )
        )
    return out
