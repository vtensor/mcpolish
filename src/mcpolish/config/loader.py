"""Load `[tool.mcpolish]` from pyproject.toml. Pydantic-validated."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from mcpolish.exceptions import ConfigError

if sys.version_info >= (3, 11):
    import tomllib
else:  # pragma: no cover
    import tomli as tomllib  # type: ignore[import-not-found]


class ScoreWeights(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_: float = Field(0.20, alias="schema")
    naming: float = 0.30
    description: float = 0.30
    consistency: float = 0.15
    security: float = 0.05


class MCPolishConfig(BaseModel):
    model_config = ConfigDict(extra="allow")

    target_version: str = "2025-11"
    select: list[str] = Field(default_factory=list)
    ignore: list[str] = Field(default_factory=list)
    line_length: int = 100
    registry: str = "official"  # "official" | "off" | "online"
    server_name: str | None = None
    namespace: str | None = None
    llm: str | None = None
    score_weights: ScoreWeights = Field(default_factory=ScoreWeights)
    rules: dict[str, dict[str, Any]] = Field(default_factory=dict)


DEFAULT_CONFIG = MCPolishConfig()


def load_config(start: Path) -> MCPolishConfig:
    """Walk up from `start` looking for the nearest pyproject.toml.

    A missing config is fine: we return DEFAULT_CONFIG. A malformed config is
    a fatal error with a precise message.
    """
    pyproject = _find_pyproject(start)
    if pyproject is None:
        return DEFAULT_CONFIG
    try:
        data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as exc:
        raise ConfigError(f"invalid pyproject.toml: {exc}") from exc
    section = data.get("tool", {}).get("mcpolish", {})
    rule_overrides = {k: v for k, v in section.items() if k.startswith("MP") and isinstance(v, dict)}
    flat = {k: v for k, v in section.items() if not (k.startswith("MP") and isinstance(v, dict))}
    score_block = flat.pop("score", None)
    if isinstance(score_block, dict):
        weights = score_block.get("weights", score_block)
        flat["score_weights"] = weights
    flat["rules"] = rule_overrides
    try:
        cfg = MCPolishConfig.model_validate(flat)
    except Exception as exc:  # pydantic.ValidationError; widen for safety
        raise ConfigError(f"invalid [tool.mcpolish] section: {exc}") from exc
    return cfg


def _find_pyproject(start: Path) -> Path | None:
    p = start.resolve()
    if p.is_file():
        p = p.parent
    for parent in [p, *p.parents]:
        candidate = parent / "pyproject.toml"
        if candidate.is_file():
            return candidate
    return None
