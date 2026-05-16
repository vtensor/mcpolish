"""`mcpolish doctor` - validate config + environment."""

from __future__ import annotations

import sys
from pathlib import Path

import click

from mcpolish.config.loader import load_config
from mcpolish.exceptions import ConfigError, RegistryError
from mcpolish.registry.snapshot import load_bundled


@click.command()
@click.argument(
    "target",
    type=click.Path(exists=True, file_okay=True, dir_okay=True, path_type=Path),
    required=False,
    default=Path("."),
)
def doctor_command(target: Path) -> None:
    """Check the local mcpolish configuration."""
    ok = True
    try:
        cfg = load_config(target)
        click.echo(f"config: ok (target-version={cfg.target_version}, registry={cfg.registry})")
    except ConfigError as exc:
        ok = False
        click.echo(f"config: error - {exc}", err=True)
    try:
        snapshot = load_bundled()
        click.echo(f"snapshot: ok ({len(snapshot)} tools, version={snapshot.version})")
    except RegistryError as exc:
        ok = False
        click.echo(f"snapshot: missing - {exc}", err=True)
    from mcpolish.rules.registry import all_rules

    click.echo(f"rules: {len(all_rules())} loaded")
    sys.exit(0 if ok else 65)
