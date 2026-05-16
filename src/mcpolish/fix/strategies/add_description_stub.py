"""MP001 fix - add a docstring placeholder to a tool function.

Safe: inserts a TODO docstring; no behaviour change. The user still has to
write the real description, but the lint passes for placeholder rules
above it that depend on description being non-empty (so subsequent rules
can run against more representative shape).
"""

from __future__ import annotations

import re
from pathlib import Path

from mcpolish.types import Diagnostic

_PLACEHOLDER = '"""TODO: describe what this tool does and when an agent should call it."""'


class AddDescriptionStub:
    rule_id = "MP001"
    safe = True

    def applies(self, diag: Diagnostic) -> bool:
        return diag.rule_id == "MP001" and diag.tool_name is not None

    def apply(self, source_path: Path, diag: Diagnostic) -> str | None:
        try:
            source = source_path.read_text(encoding="utf-8")
        except OSError:
            return None
        lines = source.splitlines(keepends=True)
        target = diag.line - 1
        # Walk down from the decorator to find the `def` line.
        for i in range(target, min(target + 8, len(lines))):
            if re.match(r"\s*(?:async\s+)?def\s+\w+\s*\(", lines[i]):
                # Found the def. Insert a docstring after the next colon-ending line.
                end = _find_def_end(lines, i)
                if end is None:
                    return None
                indent = _detect_body_indent(lines, end)
                docstring = f"{indent}{_PLACEHOLDER}\n"
                if end + 1 < len(lines) and _is_docstring(lines[end + 1]):
                    return None  # already has docstring; nothing to do
                lines.insert(end + 1, docstring)
                return "".join(lines)
        return None


def _find_def_end(lines: list[str], start: int) -> int | None:
    """Return the line index where the def signature closes with ':'."""
    depth = 0
    for i in range(start, min(start + 20, len(lines))):
        for ch in lines[i]:
            if ch in "([{":
                depth += 1
            elif ch in ")]}":
                depth -= 1
        if depth == 0 and ":" in lines[i]:
            return i
    return None


def _detect_body_indent(lines: list[str], def_line_index: int) -> str:
    base_match = re.match(r"(\s*)", lines[def_line_index])
    base_indent = base_match.group(1) if base_match else ""
    return base_indent + "    "


_DOCSTRING_RE = re.compile(r'\s*([rRbBuU]*"""|[rRbBuU]*\'\'\')')


def _is_docstring(line: str) -> bool:
    return bool(_DOCSTRING_RE.match(line))
