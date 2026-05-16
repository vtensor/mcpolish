"""Single logger entry point. Other modules import `get_logger`."""

from __future__ import annotations

import logging
import os

_CONFIGURED = False


def get_logger(name: str = "mcpolish") -> logging.Logger:
    global _CONFIGURED
    if not _CONFIGURED:
        level = os.environ.get("MCPOLISH_LOG", "WARNING").upper()
        logging.basicConfig(
            level=level,
            format="%(asctime)s %(name)s %(levelname)s %(message)s",
        )
        _CONFIGURED = True
    return logging.getLogger(name)
