"""mcpolish CLI entry. Exit codes follow §9.8 of the design doc."""

from __future__ import annotations

import click

from mcpolish._version import __version__
from mcpolish.cli.doctor import doctor_command
from mcpolish.cli.explain import explain_command
from mcpolish.cli.lint import lint_command
from mcpolish.cli.score import score_command


EXIT_OK = 0
EXIT_LINT_ERRORS = 1
EXIT_FILE_ERROR = 2
EXIT_USAGE = 64
EXIT_CONFIG = 65
EXIT_INTERNAL = 70


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(__version__, "-V", "--version")
def cli() -> None:
    """mcpolish - fast static linter for MCP servers."""


cli.add_command(lint_command, name="lint")
cli.add_command(score_command, name="score")
cli.add_command(explain_command, name="explain")
cli.add_command(doctor_command, name="doctor")


if __name__ == "__main__":  # pragma: no cover
    cli()
