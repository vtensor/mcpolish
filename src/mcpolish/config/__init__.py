"""User configuration loaded from pyproject.toml [tool.mcpolish]."""

from mcpolish.config.loader import DEFAULT_CONFIG, MCPolishConfig, ScoreWeights, load_config

__all__ = ["MCPolishConfig", "ScoreWeights", "DEFAULT_CONFIG", "load_config"]
