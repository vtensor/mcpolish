"""Re-export config models for users referencing `mcpolish.config.schema`."""

from mcpolish.config.loader import MCPolishConfig, ScoreWeights

__all__ = ["MCPolishConfig", "ScoreWeights"]
