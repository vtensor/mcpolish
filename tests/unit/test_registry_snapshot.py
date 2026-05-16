"""Bundled cross-server snapshot."""

from __future__ import annotations

from mcpolish.registry.snapshot import Snapshot, load_bundled


def test_bundled_loads_with_entries():
    snap = load_bundled()
    assert len(snap) > 0
    assert "search" in snap


def test_servers_for_known_tool():
    snap = load_bundled()
    servers = snap.servers_for_tool("search")
    assert len(servers) >= 2


def test_empty_snapshot():
    s = Snapshot({"tools": []})
    assert len(s) == 0
    assert s.servers_for_tool("anything") == ()
