"""End-to-end CLI tests via Click's CliRunner."""

from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner

from mcpolish.cli.main import cli

EXAMPLES = Path(__file__).resolve().parents[2] / "examples"


def test_lint_clean_server_scores_high():
    runner = CliRunner()
    result = runner.invoke(cli, ["lint", str(EXAMPLES / "clean_server.py"), "--fail-on", "never"])
    assert result.exit_code == 0
    assert "100/100" in result.output or "/100" in result.output


def test_lint_smelly_server_flags_issues():
    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["lint", str(EXAMPLES / "smelly_server.py"), "--fail-on", "never"],
    )
    assert result.exit_code == 0
    assert "MP041" in result.output  # tool poisoning fired
    assert "MP033" in result.output  # duplicate description fired


def test_lint_json_output_parses():
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "lint",
            str(EXAMPLES / "smelly_server.py"),
            "--format",
            "json",
            "--fail-on",
            "never",
        ],
    )
    doc = json.loads(result.output)
    assert doc["score"] < 100
    assert {d["rule_id"] for d in doc["diagnostics"]} & {"MP033", "MP041"}


def test_score_command_prints_number():
    runner = CliRunner()
    result = runner.invoke(cli, ["score", str(EXAMPLES / "clean_server.py")])
    assert result.exit_code == 0
    assert result.output.strip().isdigit()


def test_explain_lists_rules_when_no_id():
    runner = CliRunner()
    result = runner.invoke(cli, ["explain"])
    assert "MP010" in result.output
    assert "MP041" in result.output


def test_explain_unknown_rule_fails():
    runner = CliRunner()
    result = runner.invoke(cli, ["explain", "MP999"])
    assert result.exit_code == 64


def test_doctor_returns_ok():
    runner = CliRunner()
    result = runner.invoke(cli, ["doctor"])
    assert result.exit_code == 0
    assert "rules:" in result.output
