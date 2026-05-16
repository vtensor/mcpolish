"""All 24 first-party MCPolish rules.

Each submodule self-registers via @register at import time. Power users can
import a specific rule class directly:

    from mcpolish.rules.naming.MP010_generic_tool_name import GenericToolName

Most callers just use `mcpolish.rules.registry.all_rules()`.
"""

from mcpolish.rules.base import Rule, RuleContext
from mcpolish.rules.registry import (
    all_rules,
    filter_rules,
    get_rule,
    load_all,
    register,
    run_rules,
)

__all__ = [
    "Rule",
    "RuleContext",
    "all_rules",
    "filter_rules",
    "get_rule",
    "load_all",
    "register",
    "run_rules",
]
