"""`mcpolish score` - print 0-100 score, optionally as JSON or SVG badge."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import click

from mcpolish.api import lint
from mcpolish.score.badge import render_badge


@click.command()
@click.argument(
    "target",
    type=click.Path(exists=True, file_okay=True, dir_okay=True, path_type=Path),
    required=True,
)
@click.option("--json", "as_json", is_flag=True, help="emit JSON instead of plain number")
@click.option("--badge", "badge_path", type=click.Path(path_type=Path), help="write SVG badge here")
def score_command(target: Path, as_json: bool, badge_path: Path | None) -> None:
    """Print the mcpolish quality score for TARGET."""
    report = lint(target)
    if as_json:
        click.echo(
            json.dumps(
                {
                    "score": report.score,
                    "server": report.registry.server_name,
                    "tools": len(report.registry.tools),
                    "errors": report.error_count,
                    "warnings": report.warning_count,
                    "notes": report.note_count,
                }
            )
        )
    else:
        click.echo(report.score)
    if badge_path is not None:
        badge_path.write_text(render_badge(report.score), encoding="utf-8")
        click.echo(f"badge written to {badge_path}", err=True)
    sys.exit(0)
