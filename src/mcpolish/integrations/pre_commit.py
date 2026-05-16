"""Adapter used by the pre-commit framework.

pre-commit passes one or more filenames; we expand them to a single batch
lint over the affected directories so repeated work is amortised.
"""

from __future__ import annotations

import sys
from pathlib import Path

from mcpolish.cli.lint import lint_command


def main(argv: list[str] | None = None) -> None:  # pragma: no cover - CLI shim
    args = list(argv or sys.argv[1:])
    if not args:
        args = ["."]
    paths = [Path(a) for a in args if not a.startswith("-")]
    flags = [a for a in args if a.startswith("-")]
    roots = sorted({str(p.parent if p.is_file() else p) for p in paths})
    target = roots[0] if len(roots) == 1 else "."
    lint_command.main(args=[*flags, target], standalone_mode=True)
