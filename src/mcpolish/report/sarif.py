"""SARIF 2.1.0 output for GitHub / GitLab Code Scanning."""

from __future__ import annotations

import json
from typing import TextIO

from mcpolish.report.base import ReportPayload
from mcpolish.rules.registry import all_rules
from mcpolish.types import Severity

_SARIF_LEVEL: dict[Severity, str] = {
    Severity.ERROR: "error",
    Severity.WARNING: "warning",
    Severity.NOTE: "note",
}


class SarifReporter:
    name = "sarif"

    def emit(self, payload: ReportPayload, out: TextIO) -> None:
        rules = [
            {
                "id": r.id,
                "name": r.name,
                "shortDescription": {"text": r.summary},
                "helpUri": f"https://mcpolish.dev/rules/{r.id}",
                "defaultConfiguration": {
                    "level": _SARIF_LEVEL[r.severity_default]
                },
                "properties": {
                    "category": r.category.value,
                    "llm_gated": r.llm_gated,
                    "auto_fixable": r.auto_fixable,
                },
            }
            for r in all_rules()
        ]
        results = [
            {
                "ruleId": d.rule_id,
                "level": _SARIF_LEVEL[d.severity],
                "message": {"text": d.message},
                "locations": [
                    {
                        "physicalLocation": {
                            "artifactLocation": {"uri": d.file},
                            "region": {
                                "startLine": d.line,
                                "startColumn": d.col,
                            },
                        }
                    }
                ],
            }
            for d in payload.diagnostics
        ]
        document = {
            "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
            "version": "2.1.0",
            "runs": [
                {
                    "tool": {
                        "driver": {
                            "name": "mcpolish",
                            "version": payload.version,
                            "informationUri": "https://mcpolish.dev",
                            "rules": rules,
                        }
                    },
                    "results": results,
                }
            ],
        }
        json.dump(document, out, indent=2)
        out.write("\n")
