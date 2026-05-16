"""Markdown body suitable for posting as a GitHub PR comment."""

from __future__ import annotations

from typing import TextIO

from mcpolish.report.base import ReportPayload, diagnostics_for_file
from mcpolish.types import Severity

_BADGE_EMOJI: dict[Severity, str] = {
    Severity.ERROR: "🔴",
    Severity.WARNING: "🟡",
    Severity.NOTE: "🔵",
}


class PRCommentReporter:
    name = "pr-comment"

    def emit(self, payload: ReportPayload, out: TextIO) -> None:
        out.write(f"### 🧹 mcpolish - score **{payload.score}/100**\n\n")
        out.write(
            f"Scanned **{payload.tools_found}** tools in "
            f"**{payload.files_scanned}** file"
            f"{'s' if payload.files_scanned != 1 else ''}.\n\n"
        )
        if not payload.diagnostics:
            out.write("No issues found.\n")
            return
        out.write("<details><summary>Diagnostics</summary>\n\n")
        out.write("| Severity | Rule | File:Line | Message |\n")
        out.write("|---|---|---|---|\n")
        for d in payload.diagnostics:
            badge = _BADGE_EMOJI.get(d.severity, "•")
            out.write(
                f"| {badge} {d.severity.value} | "
                f"[{d.rule_id}]({d.docs_url}) | "
                f"`{d.file}:{d.line}` | {d.message} |\n"
            )
        out.write("\n</details>\n")
        by_file = diagnostics_for_file(payload.diagnostics)
        if any(d.hint for ds in by_file.values() for d in ds):
            out.write("\n#### Hints\n\n")
            for ds in by_file.values():
                for d in ds:
                    if d.hint:
                        out.write(f"- **{d.rule_id}** `{d.tool_name or ''}`: {d.hint}\n")
