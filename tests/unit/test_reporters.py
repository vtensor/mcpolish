"""Reporters produce the right shape."""

from __future__ import annotations

import io
import json

from mcpolish.report import get_reporter
from mcpolish.report.base import ReportPayload
from mcpolish.types import Category, Diagnostic, Severity


def _payload() -> ReportPayload:
    return ReportPayload(
        diagnostics=(
            Diagnostic(
                rule_id="MP010",
                rule_name="generic-tool-name",
                category=Category.NAMING,
                severity=Severity.WARNING,
                message="tool name `search` is too generic",
                file="server.py",
                line=42,
                col=5,
                tool_name="search",
                docs_url="https://mcpolish.dev/rules/MP010",
                hint="be more specific",
            ),
        ),
        score=78,
        server_name="memnex",
        files_scanned=1,
        tools_found=1,
    )


def test_tty_reporter_writes_score():
    buf = io.StringIO()
    get_reporter("tty").emit(_payload(), buf)
    out = buf.getvalue()
    assert "MP010" in out
    assert "78/100" in out


def test_json_reporter_is_valid_json():
    buf = io.StringIO()
    get_reporter("json").emit(_payload(), buf)
    doc = json.loads(buf.getvalue())
    assert doc["score"] == 78
    assert doc["diagnostics"][0]["rule_id"] == "MP010"


def test_sarif_reporter_has_required_keys():
    buf = io.StringIO()
    get_reporter("sarif").emit(_payload(), buf)
    doc = json.loads(buf.getvalue())
    assert doc["version"] == "2.1.0"
    assert doc["runs"][0]["tool"]["driver"]["name"] == "mcpolish"


def test_gitlab_reporter_emits_list():
    buf = io.StringIO()
    get_reporter("gitlab").emit(_payload(), buf)
    doc = json.loads(buf.getvalue())
    assert isinstance(doc, list)
    assert doc[0]["severity"] == "minor"


def test_pr_comment_reporter_contains_score():
    buf = io.StringIO()
    get_reporter("pr-comment").emit(_payload(), buf)
    out = buf.getvalue()
    assert "78/100" in out
    assert "MP010" in out
