"""GitLab Code Quality JSON format."""

from __future__ import annotations

import hashlib
import json
from typing import TextIO

from mcpolish.report.base import ReportPayload
from mcpolish.types import Severity

_SEVERITY_MAP: dict[Severity, str] = {
    Severity.ERROR: "major",
    Severity.WARNING: "minor",
    Severity.NOTE: "info",
}


class GitLabReporter:
    name = "gitlab"

    def emit(self, payload: ReportPayload, out: TextIO) -> None:
        out_list = []
        for d in payload.diagnostics:
            fingerprint = hashlib.sha1(
                f"{d.rule_id}|{d.file}|{d.line}|{d.tool_name}".encode("utf-8")
            ).hexdigest()
            out_list.append(
                {
                    "description": f"[{d.rule_id}] {d.message}",
                    "check_name": d.rule_id,
                    "fingerprint": fingerprint,
                    "severity": _SEVERITY_MAP.get(d.severity, "minor"),
                    "location": {
                        "path": d.file,
                        "lines": {"begin": d.line},
                    },
                }
            )
        json.dump(out_list, out, indent=2)
        out.write("\n")
