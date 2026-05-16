"""Auto-fix strategies, one per fixable rule."""

from mcpolish.fix.strategies.add_description_stub import AddDescriptionStub
from mcpolish.fix.strategies.rename_redundant_prefix import RenameRedundantPrefix

ALL_STRATEGIES = (AddDescriptionStub(), RenameRedundantPrefix())

__all__ = ["AddDescriptionStub", "RenameRedundantPrefix", "ALL_STRATEGIES"]
