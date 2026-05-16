"""Safe + unsafe autofixes.

Safe = deterministic, semantics preserving. Applied by --fix.
Unsafe = renames or API changes. Applied only with --unsafe-fix.
"""

from mcpolish.fix.engine import FixResult, apply_fixes

__all__ = ["FixResult", "apply_fixes"]
