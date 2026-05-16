"""Content-addressed SQLite cache for LLM verdicts.

Key = SHA-256(rule_id, model_id, prompt). Value = the literal one-line
response. TTL configurable, default 30 days.
"""

from __future__ import annotations

import hashlib
import sqlite3
import time
from pathlib import Path

_DDL = """
CREATE TABLE IF NOT EXISTS verdicts (
    key TEXT PRIMARY KEY,
    rule_id TEXT NOT NULL,
    model_id TEXT NOT NULL,
    response TEXT NOT NULL,
    created_at INTEGER NOT NULL
);
"""


class LLMCache:
    def __init__(self, path: Path, *, ttl_seconds: int = 30 * 24 * 3600) -> None:
        self.path = path
        self.ttl_seconds = ttl_seconds
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(self.path))
        self._conn.execute(_DDL)
        self._conn.commit()

    @staticmethod
    def key(rule_id: str, model_id: str, prompt: str) -> str:
        h = hashlib.sha256()
        h.update(rule_id.encode("utf-8"))
        h.update(b"|")
        h.update(model_id.encode("utf-8"))
        h.update(b"|")
        h.update(prompt.encode("utf-8"))
        return h.hexdigest()

    def get(self, key: str) -> str | None:
        row = self._conn.execute(
            "SELECT response, created_at FROM verdicts WHERE key = ?", (key,)
        ).fetchone()
        if not row:
            return None
        response, created_at = row
        if time.time() - created_at > self.ttl_seconds:
            return None
        return response

    def put(self, key: str, *, rule_id: str, model_id: str, response: str) -> None:
        self._conn.execute(
            "REPLACE INTO verdicts(key, rule_id, model_id, response, created_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (key, rule_id, model_id, response, int(time.time())),
        )
        self._conn.commit()

    def close(self) -> None:
        self._conn.close()
