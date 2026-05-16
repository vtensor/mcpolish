"""MP011 fix - rename a redundantly prefixed tool.

UNSAFE: renaming a tool changes the public API. Only applied with
`--unsafe-fix`. Limits scope to the single source file; callers in other
files may still reference the old name.
"""

from __future__ import annotations

import re
from pathlib import Path

from mcpolish.types import Diagnostic


class RenameRedundantPrefix:
    rule_id = "MP011"
    safe = False

    def applies(self, diag: Diagnostic) -> bool:
        return diag.rule_id == "MP011" and diag.tool_name is not None

    def apply(self, source_path: Path, diag: Diagnostic) -> str | None:
        if not diag.hint:
            return None
        new_name_match = re.search(r"`([^`]+)`", diag.hint)
        if not new_name_match:
            return None
        new_name = new_name_match.group(1)
        old_name = diag.tool_name
        if not old_name:
            return None
        try:
            source = source_path.read_text(encoding="utf-8")
        except OSError:
            return None
        pattern = rf"\b{re.escape(old_name)}\b"
        new_source = re.sub(pattern, new_name, source)
        if new_source == source:
            return None
        return new_source
