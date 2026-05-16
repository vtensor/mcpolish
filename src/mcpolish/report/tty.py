"""Rich-rendered, ESLint-flavoured CLI output."""

from __future__ import annotations

from typing import TextIO

from rich.console import Console

from mcpolish.report.base import ReportPayload, diagnostics_for_file
from mcpolish.types import Severity

_SEVERITY_TAG: dict[Severity, str] = {
    Severity.ERROR: "[bold red][E][/bold red]",
    Severity.WARNING: "[yellow][W][/yellow]",
    Severity.NOTE: "[dim][N][/dim]",
}


class TTYReporter:
    name = "tty"

    def emit(self, payload: ReportPayload, out: TextIO) -> None:
        console = Console(file=out, force_terminal=out.isatty(), highlight=False)
        console.print(f"[bold]mcpolish[/bold] {payload.version}")
        console.print(
            f"server: [cyan]{payload.server_name}[/cyan]  "
            f"([magenta]{payload.tools_found}[/magenta] tools in "
            f"[magenta]{payload.files_scanned}[/magenta] file{'s' if payload.files_scanned != 1 else ''})"
        )
        console.print("")
        by_file = diagnostics_for_file(payload.diagnostics)
        errors = warns = notes = 0
        for fname, diags in by_file.items():
            for d in diags:
                tag = _SEVERITY_TAG.get(d.severity, "[ ]")
                console.print(
                    f"[white]{fname}[/white]:{d.line}:{d.col}: "
                    f"[bold]{d.rule_id}[/bold] {tag} {d.message}"
                )
                if d.hint:
                    console.print(f"   [dim]->[/dim] {d.hint}")
                console.print(f"   [dim]->[/dim] [link={d.docs_url}]{d.docs_url}[/link]")
                if d.severity == Severity.ERROR:
                    errors += 1
                elif d.severity == Severity.WARNING:
                    warns += 1
                else:
                    notes += 1
        if payload.diagnostics:
            console.print("")
        total = errors + warns + notes
        if total == 0:
            console.print(
                f"[green]ok no issues found[/green]. score: [bold]{payload.score}/100[/bold]"
            )
        else:
            console.print(
                f"Found [bold]{total}[/bold] issue{'s' if total != 1 else ''} "
                f"([red]{errors} error{'s' if errors != 1 else ''}[/red], "
                f"[yellow]{warns} warning{'s' if warns != 1 else ''}[/yellow], "
                f"[dim]{notes} note{'s' if notes != 1 else ''}[/dim]). "
                f"score: [bold]{payload.score}/100[/bold]"
            )
