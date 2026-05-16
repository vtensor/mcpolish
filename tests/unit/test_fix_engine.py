"""Autofix engine + strategies."""

from __future__ import annotations

import textwrap
from pathlib import Path

from mcpolish.fix.engine import apply_fixes
from mcpolish.fix.strategies.add_description_stub import AddDescriptionStub
from mcpolish.types import Category, Diagnostic, Fix, Severity


def test_add_description_stub_inserts_docstring(tmp_path: Path) -> None:
    src = textwrap.dedent('''\
        from mcp.server.fastmcp import FastMCP
        mcp = FastMCP("x")

        @mcp.tool()
        def foo(x: int) -> int:
            return x + 1
    ''')
    p = tmp_path / "server.py"
    p.write_text(src)

    diag = Diagnostic(
        rule_id="MP001",
        rule_name="require-tool-description",
        category=Category.SCHEMA,
        severity=Severity.ERROR,
        message="missing",
        file=str(p),
        line=4,
        col=1,
        tool_name="foo",
        docs_url="",
        fix=Fix(description="add stub"),
    )
    assert AddDescriptionStub().applies(diag)
    new = AddDescriptionStub().apply(p, diag)
    assert new is not None
    assert "TODO" in new


def test_apply_fixes_skips_unsafe_without_flag(tmp_path: Path) -> None:
    p = tmp_path / "server.py"
    p.write_text("# nothing\n")
    diag = Diagnostic(
        rule_id="MP011",
        rule_name="redundant-prefix",
        category=Category.NAMING,
        severity=Severity.ERROR,
        message="rename",
        file=str(p),
        line=1,
        col=1,
        tool_name="memnex_search",
        docs_url="",
        fix=Fix(description="rename", safe=False),
        hint="rename to `search`",
    )
    results = apply_fixes([diag], unsafe=False)
    assert results and results[0].applied is False
    assert "unsafe" in results[0].reason
