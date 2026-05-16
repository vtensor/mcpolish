"""Discovery against representative MCP server snippets."""

from __future__ import annotations

import textwrap
from pathlib import Path

from mcpolish.discover.python_ast import PythonDiscoverer
from mcpolish.discover.ir import build_registry


def _write(tmp_path: Path, body: str) -> Path:
    p = tmp_path / "server.py"
    p.write_text(textwrap.dedent(body))
    return p


def test_fastmcp_decorator(tmp_path: Path) -> None:
    src = '''
        from mcp.server.fastmcp import FastMCP

        mcp = FastMCP("memnex")

        @mcp.tool()
        def search_memories(query: str, limit: int = 10) -> list:
            """Search across stored memories.

            Args:
                query: Keyword string. Example: "kubernetes".
                limit: max results.
            """
            return []
    '''
    p = _write(tmp_path, src)
    tools = PythonDiscoverer().extract(p)
    assert len(tools) == 1
    t = tools[0]
    assert t.name == "search_memories"
    assert "Search across stored memories" in t.description
    assert {p.name for p in t.params} == {"query", "limit"}
    assert {p.type for p in t.params} == {"string", "integer"}


def test_tool_constructor(tmp_path: Path) -> None:
    src = '''
        from mcp import Tool

        TOOLS = [
            Tool(
                name="create_entry",
                description="Add a new entry. Use this when…",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "amount": {"type": "integer", "description": "Cents"},
                    },
                    "required": ["amount"],
                },
            )
        ]
    '''
    p = _write(tmp_path, src)
    tools = PythonDiscoverer().extract(p)
    assert len(tools) == 1
    assert tools[0].name == "create_entry"
    assert tools[0].params[0].name == "amount"
    assert tools[0].params[0].required is True


def test_namespace_detection(tmp_path: Path) -> None:
    src = '''
        from mcp.server.fastmcp import FastMCP
        mcp = FastMCP("memnex")

        @mcp.tool()
        def foo():
            """Returns the answer to everything for the user."""
            return 42
    '''
    p = _write(tmp_path, src)
    registry = build_registry(p)
    assert registry.namespace == "memnex"
    assert registry.server_name == "memnex"


def test_syntax_error_is_recoverable(tmp_path: Path) -> None:
    p = tmp_path / "broken.py"
    p.write_text("@mcp.tool(\ndef oops(:")
    # Should not raise; ir.build_registry logs a warning and yields zero tools.
    registry = build_registry(p)
    assert len(registry.tools) == 0
