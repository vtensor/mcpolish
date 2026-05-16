"""Fix Protocol."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol

from mcpolish.types import Diagnostic


class FixStrategy(Protocol):
    rule_id: str
    safe: bool

    def applies(self, diag: Diagnostic) -> bool: ...

    def apply(self, source_path: Path, diag: Diagnostic) -> str | None:
        """Return the new file contents, or None if no fix is possible."""
