"""Stable JSON report format. Schema: report.v1.json."""

from __future__ import annotations

import json
from typing import TextIO

from mcpolish.report.base import ReportPayload


class JsonReporter:
    name = "json"

    def emit(self, payload: ReportPayload, out: TextIO) -> None:
        document = {
            "schema": "https://mcpolish.dev/schemas/report.v1.json",
            "version": payload.version,
            "server": payload.server_name,
            "scanned_at": payload.scanned_at,
            "files_scanned": payload.files_scanned,
            "tools_found": payload.tools_found,
            "score": payload.score,
            "diagnostics": [
                {
                    "rule_id": d.rule_id,
                    "rule_name": d.rule_name,
                    "category": d.category.value,
                    "severity": d.severity.value,
                    "message": d.message,
                    "file": d.file,
                    "line": d.line,
                    "col": d.col,
                    "tool_name": d.tool_name,
                    "docs_url": d.docs_url,
                    "hint": d.hint,
                    "fix": (
                        {
                            "description": d.fix.description,
                            "safe": d.fix.safe,
                        }
                        if d.fix
                        else None
                    ),
                }
                for d in payload.diagnostics
            ],
        }
        json.dump(document, out, indent=2)
        out.write("\n")
