"""Discoverer Protocol - one parser per language."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol

from mcpolish.types import ToolDecl


class Discoverer(Protocol):
    """Parses source files into ToolDecls.

    Implementations: PythonDiscoverer (libcst). A TypeScript discoverer is
    planned for M2 and would shell out to ts-morph.
    """

    name: str

    def supports(self, path: Path) -> bool: ...

    def extract(self, path: Path) -> list[ToolDecl]: ...
