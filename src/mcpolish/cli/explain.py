"""`mcpolish explain MP010` - print the rule documentation."""

from __future__ import annotations

import sys

import click

from mcpolish.rules.registry import all_rules, get_rule


@click.command()
@click.argument("rule_id", required=False)
def explain_command(rule_id: str | None) -> None:
    """Explain a rule, or list all rules when no ID is given."""
    if rule_id is None:
        for rule in all_rules():
            llm = " [LLM]" if rule.llm_gated else ""
            fix = " [fixable]" if rule.auto_fixable else ""
            click.echo(
                f"{rule.id:<6} {rule.category.value:<13} "
                f"{rule.severity_default.value:<5} {rule.name}{llm}{fix}"
            )
            click.echo(f"       {rule.summary}")
        return
    rule = get_rule(rule_id.upper())
    if rule is None:
        click.echo(f"unknown rule {rule_id}", err=True)
        sys.exit(64)
    click.echo(f"{rule.id} - {rule.name}")
    click.echo(f"category: {rule.category.value}")
    click.echo(f"severity (default): {rule.severity_default.value}")
    click.echo(f"llm-gated: {rule.llm_gated}")
    click.echo(f"auto-fixable: {rule.auto_fixable}")
    click.echo("")
    click.echo(rule.summary)
    click.echo("")
    click.echo(f"docs: https://mcpolish.dev/rules/{rule.id}")
    if rule.__doc__:
        click.echo("")
        click.echo(rule.__doc__.strip())
