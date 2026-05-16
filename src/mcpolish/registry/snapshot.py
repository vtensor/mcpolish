"""Loader for the bundled cross-server snapshot.

The OSS build ships a small JSON snapshot (`snapshot.v1.json`) with the
top-N most common tool names across public MCP servers. SaaS overrides this
with a weekly Parquet fetch - out of scope for OSS.

Schema:
  {
    "version": "v1",
    "generated_at": "2026-04-01T00:00:00Z",
    "source": "mcpolish-bundled",
    "tools": [
       {"tool_name": "search", "servers": ["context7", "exa", "..."], "count": 412},
       ...
    ]
  }
"""

from __future__ import annotations

import json
from collections import defaultdict
from importlib import resources
from pathlib import Path

from mcpolish.exceptions import RegistryError


class Snapshot:
    """Hash-set view over the registry snapshot. Cheap lookups."""

    def __init__(self, payload: dict) -> None:
        self.version: str = payload.get("version", "v1")
        self.generated_at: str = payload.get("generated_at", "")
        self.source: str = payload.get("source", "unknown")
        self._tool_to_servers: dict[str, tuple[str, ...]] = {}
        self._tool_counts: dict[str, int] = {}
        tools = payload.get("tools") or []
        if not isinstance(tools, list):
            raise RegistryError("snapshot.tools must be a list")
        seen: dict[str, set[str]] = defaultdict(set)
        counts: dict[str, int] = defaultdict(int)
        for row in tools:
            if not isinstance(row, dict):
                continue
            name = row.get("tool_name")
            if not name:
                continue
            servers = row.get("servers") or []
            if isinstance(servers, list):
                for s in servers:
                    seen[name].add(str(s))
            counts[name] = max(counts[name], int(row.get("count", len(servers))))
        for name, server_set in seen.items():
            self._tool_to_servers[name] = tuple(sorted(server_set))
        self._tool_counts.update(counts)

    def servers_for_tool(self, name: str) -> tuple[str, ...]:
        return self._tool_to_servers.get(name, ())

    def total_count(self, name: str) -> int:
        return self._tool_counts.get(name, 0)

    def __len__(self) -> int:
        return len(self._tool_to_servers)

    def __contains__(self, name: object) -> bool:
        return name in self._tool_to_servers


def load_snapshot(path: Path) -> Snapshot:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RegistryError(f"unable to load snapshot {path}: {exc}") from exc
    return Snapshot(payload)


def load_bundled() -> Snapshot:
    """Open the snapshot packaged inside the wheel."""
    try:
        data_files = resources.files("mcpolish.registry.data")
        with resources.as_file(data_files / "snapshot.v1.json") as f:
            return load_snapshot(Path(f))
    except (FileNotFoundError, ModuleNotFoundError) as exc:
        raise RegistryError(f"bundled snapshot missing: {exc}") from exc
