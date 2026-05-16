"""Walk a path on disk and build a ToolRegistry."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from mcpolish.discover.base import Discoverer
from mcpolish.discover.python_ast import PythonDiscoverer
from mcpolish.exceptions import DiscoveryError
from mcpolish.logging import get_logger
from mcpolish.types import ToolDecl, ToolRegistry

log = get_logger(__name__)

_DEFAULT_DISCOVERERS: tuple[Discoverer, ...] = (PythonDiscoverer(),)

_EXCLUDE_DIRS = frozenset(
    {".git", ".venv", "venv", "__pycache__", "node_modules", "dist", "build", ".tox"}
)


def discover_path(
    target: Path, *, discoverers: Iterable[Discoverer] = _DEFAULT_DISCOVERERS
) -> list[ToolDecl]:
    """Find and extract every tool reachable from `target`."""
    tools, _ = _discover_internal(target, discoverers)
    return tools


def build_registry(
    target: Path,
    *,
    server_name: str | None = None,
    namespace: str | None = None,
    discoverers: Iterable[Discoverer] = _DEFAULT_DISCOVERERS,
) -> ToolRegistry:
    target = target.resolve()
    tools, detected_ns = _discover_internal(target, discoverers)
    files = sorted({t.file for t in tools})
    resolved_ns = namespace or detected_ns
    return ToolRegistry(
        server_name=server_name or resolved_ns or target.name,
        namespace=resolved_ns,
        tools=tuple(tools),
        source_files=tuple(files),
    )


def _discover_internal(
    target: Path, discoverers: Iterable[Discoverer]
) -> tuple[list[ToolDecl], str | None]:
    target = target.resolve()
    discoverer_list = list(discoverers)
    files = list(_walk(target))
    tools: list[ToolDecl] = []
    namespace: str | None = None
    for path in files:
        for d in discoverer_list:
            if not d.supports(path):
                continue
            try:
                if hasattr(d, "extract_with_namespace"):
                    file_tools, file_ns = d.extract_with_namespace(path)  # type: ignore[attr-defined]
                else:
                    file_tools = d.extract(path)
                    file_ns = None
            except DiscoveryError as exc:
                log.warning("discover skipped %s: %s", path, exc)
                break
            tools.extend(file_tools)
            if namespace is None and file_ns:
                namespace = file_ns
            break
    return tools, namespace


def _walk(target: Path) -> Iterable[Path]:
    if target.is_file():
        yield target
        return
    for p in target.rglob("*"):
        if p.is_dir():
            continue
        if any(part in _EXCLUDE_DIRS for part in p.parts):
            continue
        yield p
