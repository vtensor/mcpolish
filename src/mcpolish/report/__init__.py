"""Diagnostic formatters."""

from mcpolish.report.base import Reporter, ReportPayload
from mcpolish.report.gitlab import GitLabReporter
from mcpolish.report.json_report import JsonReporter
from mcpolish.report.pr_comment import PRCommentReporter
from mcpolish.report.sarif import SarifReporter
from mcpolish.report.tty import TTYReporter

_REPORTERS: dict[str, type[Reporter]] = {
    "tty": TTYReporter,
    "json": JsonReporter,
    "sarif": SarifReporter,
    "gitlab": GitLabReporter,
    "pr-comment": PRCommentReporter,
}


def get_reporter(name: str) -> Reporter:
    cls = _REPORTERS.get(name)
    if cls is None:
        raise ValueError(f"unknown report format: {name!r}")
    return cls()


__all__ = [
    "Reporter",
    "ReportPayload",
    "TTYReporter",
    "JsonReporter",
    "SarifReporter",
    "GitLabReporter",
    "PRCommentReporter",
    "get_reporter",
]
