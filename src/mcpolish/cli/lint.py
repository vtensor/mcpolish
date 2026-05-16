"""`mcpolish lint` command."""

from __future__ import annotations

import sys
from pathlib import Path

import click

from mcpolish.api import lint
from mcpolish.config.loader import load_config
from mcpolish.exceptions import ConfigError, LLMError, McpolishError
from mcpolish.fix.engine import apply_fixes
from mcpolish.llm.client import build_client
from mcpolish.registry.snapshot import load_bundled
from mcpolish.report import get_reporter
from mcpolish.report.base import ReportPayload


@click.command()
@click.argument(
    "target",
    type=click.Path(exists=True, file_okay=True, dir_okay=True, path_type=Path),
    required=True,
)
@click.option("--select", "select", multiple=True, help="rule IDs to include (e.g. MP010 MP012)")
@click.option("--ignore", "ignore", multiple=True, help="rule IDs to exclude")
@click.option("--llm", "llm_spec", default=None, help="enable LLM-gated rules: provider:model")
@click.option(
    "--registry",
    "registry_mode",
    type=click.Choice(["official", "off"]),
    default=None,
    help="cross-server collision check source",
)
@click.option(
    "--format",
    "report_format",
    type=click.Choice(["tty", "json", "sarif", "gitlab", "pr-comment"]),
    default="tty",
)
@click.option("--fix", is_flag=True, help="apply safe autofixes in place")
@click.option("--unsafe-fix", is_flag=True, help="also apply unsafe autofixes")
@click.option(
    "--fail-on",
    type=click.Choice(["error", "warn", "note", "never"]),
    default="error",
    show_default=True,
)
def lint_command(
    target: Path,
    select: tuple[str, ...],
    ignore: tuple[str, ...],
    llm_spec: str | None,
    registry_mode: str | None,
    report_format: str,
    fix: bool,
    unsafe_fix: bool,
    fail_on: str,
) -> None:
    """Run mcpolish on TARGET (file or directory)."""
    try:
        cfg = load_config(target)
    except ConfigError as exc:
        click.echo(f"config error: {exc}", err=True)
        sys.exit(65)

    effective_registry = registry_mode or cfg.registry
    snapshot = None
    if effective_registry != "off":
        try:
            snapshot = load_bundled()
        except McpolishError as exc:
            click.echo(f"snapshot unavailable: {exc}", err=True)

    llm_client = None
    if llm_spec:
        try:
            llm_client = build_client(llm_spec)
        except LLMError as exc:
            click.echo(f"llm setup failed: {exc}", err=True)
            sys.exit(65)

    try:
        report = lint(
            target,
            config=cfg,
            select=list(select) or None,
            ignore=list(ignore) or None,
            llm=llm_client,
            snapshot=snapshot,
            use_bundled_snapshot=(snapshot is None and effective_registry != "off"),
        )
    except McpolishError as exc:
        click.echo(f"lint failed: {exc}", err=True)
        sys.exit(2)

    if fix or unsafe_fix:
        results = apply_fixes(report.diagnostics, unsafe=unsafe_fix)
        applied = sum(1 for r in results if r.applied)
        if applied:
            click.echo(f"applied {applied} fix(es); re-run to verify")

    payload = ReportPayload(
        diagnostics=report.diagnostics,
        score=report.score,
        server_name=report.registry.server_name,
        files_scanned=len(report.registry.source_files),
        tools_found=len(report.registry.tools),
    )
    reporter = get_reporter(report_format)
    reporter.emit(payload, sys.stdout)

    sys.exit(_exit_code(report, fail_on=fail_on))


def _exit_code(report, *, fail_on: str) -> int:
    from mcpolish.types import Severity

    counters = {
        Severity.ERROR: report.error_count,
        Severity.WARNING: report.warning_count,
        Severity.NOTE: report.note_count,
    }
    if fail_on == "never":
        return 0
    if fail_on == "error" and counters[Severity.ERROR] > 0:
        return 1
    if fail_on == "warn" and (
        counters[Severity.ERROR] > 0 or counters[Severity.WARNING] > 0
    ):
        return 1
    if fail_on == "note" and any(counters.values()):
        return 1
    return 0
