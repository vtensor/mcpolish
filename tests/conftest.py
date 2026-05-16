"""Pytest fixtures used across the suite."""

from __future__ import annotations

from pathlib import Path

import pytest

from mcpolish.rules.base import RuleContext
from mcpolish.types import ParamDecl, ToolDecl, ToolRegistry


@pytest.fixture
def registry_factory():
    def _make(*tools: ToolDecl, server_name: str = "test", namespace: str | None = None) -> ToolRegistry:
        return ToolRegistry(
            server_name=server_name,
            namespace=namespace,
            tools=tools,
            source_files=("test.py",),
        )

    return _make


@pytest.fixture
def tool_factory():
    def _make(
        name: str = "search_items",
        description: str = (
            "Use this when the user wants to find items by keyword. "
            "Returns a list of matching items with their identifiers."
        ),
        params: tuple[ParamDecl, ...] = (),
        input_schema: dict | None = None,
        output_schema: dict | None = None,
        file: str = "test.py",
        line: int = 1,
        col: int = 1,
    ) -> ToolDecl:
        return ToolDecl(
            name=name,
            description=description,
            input_schema=input_schema or {"type": "object", "properties": {}},
            output_schema=output_schema,
            params=params,
            file=file,
            line=line,
            col=col,
        )

    return _make


@pytest.fixture
def ctx() -> RuleContext:
    return RuleContext()


@pytest.fixture
def fixtures_dir() -> Path:
    return Path(__file__).parent / "fixtures"
