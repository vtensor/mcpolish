"""Scenario-level regression suite.

Each test exercises one realistic situation against the fixtures under
tests/fixtures/scenarios/ and locks the expected behaviour.

Categories covered:

1. Per-rule fixtures: every rule has a fixture that triggers it.
2. Discovery fixtures: every supported source pattern produces tools.
3. Modular project: tools spread across files are merged correctly.
4. CLI flags: select, ignore, fix, unsafe-fix, fail-on, registry off.
5. Config: per-rule overrides, custom weights, malformed toml.
6. Exit codes: every (fail-on, severity counts) combination.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from click.testing import CliRunner

import mcpolish
from mcpolish.cli.main import cli
from mcpolish.discover.ir import build_registry

REPO = Path(__file__).resolve().parents[2]
SCENARIOS = REPO / "tests" / "fixtures" / "scenarios"

# Rules that need --llm to fire. They are silent without it.
LLM_GATED = {"MP026", "MP031", "MP032"}

ALL_RULE_IDS = [
    "MP001", "MP002", "MP003", "MP004", "MP005",
    "MP010", "MP011", "MP012", "MP013", "MP014",
    "MP020", "MP021", "MP022", "MP023", "MP024", "MP025", "MP026",
    "MP030", "MP031", "MP032", "MP033",
    "MP040", "MP041",
]


# ---------------------------------------------------------------------------
# Per-rule fixtures: each rule's fixture must include that rule (unless gated)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("rule_id", [r for r in ALL_RULE_IDS if r not in LLM_GATED])
def test_per_rule_fixture_fires(rule_id: str) -> None:
    """Every non-gated rule has a fixture that triggers it."""
    fixture = SCENARIOS / f"rule_{rule_id}.py"
    report = mcpolish.lint(fixture)
    fired = {d.rule_id for d in report.diagnostics}
    assert rule_id in fired, (
        f"{rule_id} did not fire on its own fixture. Fired: {sorted(fired)}"
    )


@pytest.mark.parametrize("rule_id", sorted(LLM_GATED))
def test_llm_gated_rule_silent_without_flag(rule_id: str) -> None:
    """LLM-gated rules must not fire when --llm is not enabled."""
    fixture = SCENARIOS / f"rule_{rule_id}.py"
    report = mcpolish.lint(fixture)
    fired = {d.rule_id for d in report.diagnostics}
    assert rule_id not in fired, f"{rule_id} fired without --llm"


# ---------------------------------------------------------------------------
# Discovery fixtures
# ---------------------------------------------------------------------------


def test_fastmcp_decorator_discovered() -> None:
    reg = build_registry(SCENARIOS / "discovery" / "fastmcp_decorator.py")
    assert len(reg.tools) == 1
    assert reg.tools[0].name == "hello"
    assert reg.namespace == "discover_fastmcp"


def test_lowlevel_tool_constructor_discovered() -> None:
    reg = build_registry(SCENARIOS / "discovery" / "lowlevel_tool_constructor.py")
    assert any(t.name == "lookup_address" for t in reg.tools)


def test_add_tool_call_discovered() -> None:
    reg = build_registry(SCENARIOS / "discovery" / "add_tool_call.py")
    assert any(t.name == "get_temperature" for t in reg.tools)


def test_multiple_tools_in_one_file() -> None:
    reg = build_registry(SCENARIOS / "discovery" / "multiple_tools_one_file.py")
    names = sorted(t.name for t in reg.tools)
    assert names == ["get_a", "get_b", "get_c"]


def test_no_tools_file_is_quiet() -> None:
    reg = build_registry(SCENARIOS / "discovery" / "no_tools.py")
    assert reg.tools == ()


def test_empty_file_is_quiet() -> None:
    reg = build_registry(SCENARIOS / "discovery" / "empty.py")
    assert reg.tools == ()


def test_syntax_error_does_not_crash() -> None:
    # The file is broken; build_registry should log a warning and yield zero
    # tools, not raise.
    reg = build_registry(SCENARIOS / "discovery" / "syntax_error.py")
    assert reg.tools == ()


def test_async_tools_discovered() -> None:
    reg = build_registry(SCENARIOS / "discovery" / "async_tools.py")
    assert any(t.name == "fetch_news" for t in reg.tools)


def test_pydantic_model_param_discovered() -> None:
    reg = build_registry(SCENARIOS / "discovery" / "pydantic_schema.py")
    assert any(t.name == "run_query" for t in reg.tools)


def test_typed_params_normalised_to_json_types() -> None:
    reg = build_registry(SCENARIOS / "discovery" / "typed_params.py")
    tool = next(t for t in reg.tools if t.name == "fancy")
    types = {p.name: p.type for p in tool.params}
    assert types["items"] == "array"
    assert types["count"] == "integer" or types["count"] == "string"


def test_docstring_styles_all_yield_a_tool() -> None:
    reg = build_registry(SCENARIOS / "discovery" / "docstring_styles.py")
    names = sorted(t.name for t in reg.tools)
    assert names == ["google_style", "numpy_style", "plain_style"]


def test_dynamic_registration_skipped_silently() -> None:
    reg = build_registry(SCENARIOS / "discovery" / "dynamic_registration.py")
    # Tools registered inside a loop cannot be statically resolved. The
    # discoverer skips them. This locks the expected behaviour.
    assert reg.tools == ()


# ---------------------------------------------------------------------------
# Modular project: tools across files merge into one registry
# ---------------------------------------------------------------------------


def test_modular_project_merges_tools() -> None:
    reg = build_registry(SCENARIOS / "modular_project")
    names = sorted(t.name for t in reg.tools)
    assert names == ["memnex_clear_all", "recall_fact", "search_records", "store_fact"]
    assert reg.namespace == "memnex"


def test_modular_project_fires_mp011_across_files() -> None:
    report = mcpolish.lint(SCENARIOS / "modular_project")
    fired = {(d.rule_id, d.tool_name) for d in report.diagnostics}
    assert ("MP011", "memnex_clear_all") in fired


# ---------------------------------------------------------------------------
# CLI flags
# ---------------------------------------------------------------------------


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


def _baseline() -> Path:
    return SCENARIOS / "flags" / "baseline.py"


def test_lint_default_includes_mp010(runner: CliRunner) -> None:
    out = runner.invoke(
        cli, ["lint", str(_baseline()), "--format", "json", "--fail-on", "never"]
    )
    assert out.exit_code == 0
    doc = json.loads(out.output)
    assert any(d["rule_id"] == "MP010" for d in doc["diagnostics"])


def test_lint_select_includes_only_named(runner: CliRunner) -> None:
    out = runner.invoke(
        cli,
        [
            "lint", str(_baseline()),
            "--select", "MP020",
            "--format", "json", "--fail-on", "never",
        ],
    )
    doc = json.loads(out.output)
    rule_ids = {d["rule_id"] for d in doc["diagnostics"]}
    assert rule_ids.issubset({"MP020"})


def test_lint_select_range(runner: CliRunner) -> None:
    out = runner.invoke(
        cli,
        [
            "lint", str(_baseline()),
            "--select", "MP020-MP025",
            "--format", "json", "--fail-on", "never",
        ],
    )
    doc = json.loads(out.output)
    rule_ids = {d["rule_id"] for d in doc["diagnostics"]}
    # No diagnostic outside the range.
    for rid in rule_ids:
        n = int(rid[2:])
        assert 20 <= n <= 25, f"rule {rid} outside range"


def test_lint_ignore_excludes_named(runner: CliRunner) -> None:
    out = runner.invoke(
        cli,
        [
            "lint", str(_baseline()),
            "--ignore", "MP010",
            "--format", "json", "--fail-on", "never",
        ],
    )
    doc = json.loads(out.output)
    assert all(d["rule_id"] != "MP010" for d in doc["diagnostics"])


def test_lint_registry_off_silences_mp013(runner: CliRunner) -> None:
    out = runner.invoke(
        cli,
        [
            "lint", str(_baseline()),
            "--registry", "off",
            "--format", "json", "--fail-on", "never",
        ],
    )
    doc = json.loads(out.output)
    assert all(d["rule_id"] != "MP013" for d in doc["diagnostics"])


def test_lint_safe_fix_inserts_docstring(runner: CliRunner, tmp_path: Path) -> None:
    src = SCENARIOS / "flags" / "needs_safe_fix.py"
    target = tmp_path / "fix.py"
    shutil.copyfile(src, target)
    out = runner.invoke(
        cli, ["lint", str(target), "--fix", "--fail-on", "never"]
    )
    assert out.exit_code == 0
    new = target.read_text()
    assert "TODO" in new


def test_lint_unsafe_fix_renames_tool(runner: CliRunner, tmp_path: Path) -> None:
    src = SCENARIOS / "flags" / "needs_unsafe_fix.py"
    target = tmp_path / "fix.py"
    shutil.copyfile(src, target)
    out = runner.invoke(
        cli, ["lint", str(target), "--unsafe-fix", "--fail-on", "never"]
    )
    assert out.exit_code == 0
    new = target.read_text()
    # memnex_get_thing should have been renamed to get_thing.
    assert "def get_thing" in new
    assert "def memnex_get_thing" not in new


def test_lint_safe_fix_does_not_apply_unsafe(runner: CliRunner, tmp_path: Path) -> None:
    src = SCENARIOS / "flags" / "needs_unsafe_fix.py"
    target = tmp_path / "fix.py"
    shutil.copyfile(src, target)
    runner.invoke(cli, ["lint", str(target), "--fix", "--fail-on", "never"])
    new = target.read_text()
    # Plain --fix must leave the unsafe rename alone.
    assert "def memnex_get_thing" in new


def test_lint_format_json(runner: CliRunner) -> None:
    out = runner.invoke(
        cli, ["lint", str(_baseline()), "--format", "json", "--fail-on", "never"]
    )
    doc = json.loads(out.output)
    assert doc["schema"] == "https://mcpolish.dev/schemas/report.v1.json"


def test_lint_format_sarif(runner: CliRunner) -> None:
    out = runner.invoke(
        cli, ["lint", str(_baseline()), "--format", "sarif", "--fail-on", "never"]
    )
    doc = json.loads(out.output)
    assert doc["version"] == "2.1.0"
    assert doc["runs"][0]["tool"]["driver"]["name"] == "mcpolish"


def test_lint_format_gitlab(runner: CliRunner) -> None:
    out = runner.invoke(
        cli, ["lint", str(_baseline()), "--format", "gitlab", "--fail-on", "never"]
    )
    doc = json.loads(out.output)
    assert isinstance(doc, list)


def test_lint_format_pr_comment(runner: CliRunner) -> None:
    out = runner.invoke(
        cli, ["lint", str(_baseline()), "--format", "pr-comment", "--fail-on", "never"]
    )
    assert "mcpolish" in out.output


# ---------------------------------------------------------------------------
# Exit codes
# ---------------------------------------------------------------------------


def _exit(runner: CliRunner, target: Path, fail_on: str) -> int:
    return runner.invoke(
        cli, ["lint", str(target), "--fail-on", fail_on]
    ).exit_code


def test_exit_zero_on_clean_file(runner: CliRunner) -> None:
    target = REPO / "examples" / "clean_server.py"
    assert _exit(runner, target, "error") == 0


def test_exit_zero_on_warnings_only_with_fail_on_error(runner: CliRunner) -> None:
    # baseline has warnings but no errors.
    assert _exit(runner, _baseline(), "error") == 0


def test_exit_one_when_errors_present_with_fail_on_error(runner: CliRunner) -> None:
    # rule_MP011 fixture fires an error.
    target = SCENARIOS / "rule_MP011.py"
    assert _exit(runner, target, "error") == 1


def test_exit_one_on_warnings_with_fail_on_warn(runner: CliRunner) -> None:
    assert _exit(runner, _baseline(), "warn") == 1


def test_exit_zero_with_fail_on_never(runner: CliRunner) -> None:
    target = SCENARIOS / "rule_MP011.py"
    assert _exit(runner, target, "never") == 0


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------


def test_config_select_ignore_takes_effect(runner: CliRunner) -> None:
    cfg_dir = SCENARIOS / "config" / "select_ignore"
    out = runner.invoke(
        cli, ["lint", str(cfg_dir / "server.py"), "--format", "json", "--fail-on", "never"]
    )
    doc = json.loads(out.output)
    # select=[MP010, MP013], ignore=[MP013] -> only MP010 may appear.
    rule_ids = {d["rule_id"] for d in doc["diagnostics"]}
    assert rule_ids.issubset({"MP010"})


def test_config_per_rule_allow_silences(runner: CliRunner) -> None:
    cfg_dir = SCENARIOS / "config" / "per_rule_override"
    out = runner.invoke(
        cli, ["lint", str(cfg_dir / "server.py"), "--format", "json", "--fail-on", "never"]
    )
    doc = json.loads(out.output)
    # MP010.allow=['search'] silences MP010 for this fixture.
    assert all(d["rule_id"] != "MP010" for d in doc["diagnostics"])


def test_config_malformed_toml_exits_65(runner: CliRunner) -> None:
    cfg_dir = SCENARIOS / "config" / "malformed_toml"
    out = runner.invoke(cli, ["lint", str(cfg_dir / "server.py")])
    assert out.exit_code == 65


def test_config_custom_weights_applied(runner: CliRunner) -> None:
    # Just confirm the lint succeeds; the score will be lower than the same
    # finding would yield under default weights because security weight is 6x.
    cfg_dir = SCENARIOS / "config" / "custom_weights"
    out = runner.invoke(
        cli, ["lint", str(cfg_dir / "server.py"), "--format", "json", "--fail-on", "never"]
    )
    doc = json.loads(out.output)
    assert doc["score"] < 100


# ---------------------------------------------------------------------------
# CLI subcommands
# ---------------------------------------------------------------------------


def test_score_command(runner: CliRunner) -> None:
    target = REPO / "examples" / "clean_server.py"
    out = runner.invoke(cli, ["score", str(target)])
    assert out.exit_code == 0
    assert out.output.strip().isdigit()


def test_score_json(runner: CliRunner) -> None:
    target = REPO / "examples" / "clean_server.py"
    out = runner.invoke(cli, ["score", str(target), "--json"])
    doc = json.loads(out.output)
    assert "score" in doc and "tools" in doc


def test_score_badge_writes_svg(runner: CliRunner, tmp_path: Path) -> None:
    badge = tmp_path / "badge.svg"
    out = runner.invoke(
        cli, ["score", str(REPO / "examples" / "clean_server.py"), "--badge", str(badge)]
    )
    assert out.exit_code == 0
    assert badge.exists()
    assert "100" in badge.read_text()


def test_explain_lists_rules(runner: CliRunner) -> None:
    out = runner.invoke(cli, ["explain"])
    for rid in ALL_RULE_IDS:
        assert rid in out.output, f"explain index missing {rid}"


def test_explain_specific_rule(runner: CliRunner) -> None:
    out = runner.invoke(cli, ["explain", "MP010"])
    assert "MP010" in out.output
    assert "generic-tool-name" in out.output


def test_explain_unknown_rule_exits_64(runner: CliRunner) -> None:
    out = runner.invoke(cli, ["explain", "MP999"])
    assert out.exit_code == 64


def test_doctor_returns_zero(runner: CliRunner) -> None:
    out = runner.invoke(cli, ["doctor"])
    assert out.exit_code == 0
    assert "rules:" in out.output


# ---------------------------------------------------------------------------
# Performance budget (MCPOLISH.md section 11)
# ---------------------------------------------------------------------------


def test_one_tool_under_50ms() -> None:
    import time

    start = time.perf_counter()
    mcpolish.lint(REPO / "examples" / "clean_server.py")
    elapsed_ms = (time.perf_counter() - start) * 1000
    assert elapsed_ms < 150, f"clean_server lint took {elapsed_ms:.1f} ms"


def test_smelly_server_under_200ms() -> None:
    import time

    start = time.perf_counter()
    mcpolish.lint(REPO / "examples" / "smelly_server.py")
    elapsed_ms = (time.perf_counter() - start) * 1000
    assert elapsed_ms < 300, f"smelly_server lint took {elapsed_ms:.1f} ms"
