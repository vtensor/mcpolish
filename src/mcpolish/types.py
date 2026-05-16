"""Core typed IR. Everything that crosses a module boundary lives here."""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class Severity(str, Enum):
    ERROR = "error"
    WARNING = "warn"
    NOTE = "note"


class Category(str, Enum):
    SCHEMA = "schema"
    NAMING = "naming"
    DESCRIPTION = "description"
    CONSISTENCY = "consistency"
    SECURITY = "security"


class Position(BaseModel):
    """1-indexed source position."""

    model_config = ConfigDict(frozen=True)

    line: int = 1
    col: int = 1


class ParamDecl(BaseModel):
    """One named parameter inside a tool's input schema."""

    model_config = ConfigDict(frozen=True)

    name: str
    type: str | None = None
    description: str | None = None
    required: bool = False
    has_example: bool = False
    raw: dict[str, Any] = Field(default_factory=dict)


class ToolDecl(BaseModel):
    """One tool registration discovered in source."""

    model_config = ConfigDict(frozen=True)

    name: str
    description: str
    input_schema: dict[str, Any] = Field(default_factory=dict)
    output_schema: dict[str, Any] | None = None
    params: tuple[ParamDecl, ...] = ()
    file: str
    line: int = 1
    col: int = 1
    # Origin hint for fixers / reporters.
    decorator: str | None = None
    raw_source: str | None = None
    # True when the inputSchema came from an explicit dict literal in source
    # (Tool(inputSchema={...}) or @mcp.tool(inputSchema={...})), False when
    # the discoverer built it from the Python signature.
    schema_is_explicit: bool = False


class ToolRegistry(BaseModel):
    """The IR every rule visits."""

    model_config = ConfigDict(frozen=True)

    server_name: str = "unknown"
    namespace: str | None = None
    tools: tuple[ToolDecl, ...] = ()
    source_files: tuple[str, ...] = ()


class Fix(BaseModel):
    """A suggested edit. Safe = deterministic & semantics preserving."""

    model_config = ConfigDict(frozen=True)

    description: str
    safe: bool = True
    # Replacement text spans. file, (start_line, start_col, end_line, end_col), new_text
    edits: tuple[tuple[str, tuple[int, int, int, int], str], ...] = ()


class Diagnostic(BaseModel):
    """A single rule finding."""

    model_config = ConfigDict(frozen=True)

    rule_id: str
    rule_name: str
    category: Category
    severity: Severity
    message: str
    file: str
    line: int = 1
    col: int = 1
    tool_name: str | None = None
    docs_url: str = ""
    fix: Fix | None = None
    hint: str | None = None

    def location(self) -> str:
        return f"{self.file}:{self.line}:{self.col}"
