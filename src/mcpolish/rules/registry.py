"""Rule registry. Rules self-register at import via @register."""

from __future__ import annotations

import importlib
import pkgutil
from typing import Iterable, Type

from mcpolish.exceptions import RuleError
from mcpolish.logging import get_logger
from mcpolish.rules.base import Rule, RuleContext, docs_url
from mcpolish.types import Category, Diagnostic, Severity, ToolRegistry

log = get_logger(__name__)

_RULES: dict[str, Type[Rule]] = {}
_LOADED = False


def register(
    rule_id: str,
    *,
    name: str,
    category: Category,
    severity: Severity,
    summary: str,
    llm_gated: bool = False,
    auto_fixable: bool = False,
):
    """Decorator. Attach the rule metadata and add the class to the registry."""

    def decorator(cls: Type[Rule]) -> Type[Rule]:
        cls.id = rule_id  # type: ignore[attr-defined]
        cls.name = name  # type: ignore[attr-defined]
        cls.category = category  # type: ignore[attr-defined]
        cls.severity_default = severity  # type: ignore[attr-defined]
        cls.summary = summary  # type: ignore[attr-defined]
        cls.llm_gated = llm_gated  # type: ignore[attr-defined]
        cls.auto_fixable = auto_fixable  # type: ignore[attr-defined]
        if rule_id in _RULES:
            raise RuleError(f"duplicate rule id {rule_id}")
        _RULES[rule_id] = cls
        return cls

    return decorator


def load_all() -> None:
    """Import every submodule of mcpolish.rules.* so @register fires."""
    global _LOADED
    if _LOADED:
        return
    import mcpolish.rules as pkg  # noqa: WPS433 - late import on purpose

    for finder, mod_name, ispkg in pkgutil.walk_packages(pkg.__path__, prefix="mcpolish.rules."):
        if mod_name.endswith(".base") or mod_name.endswith(".registry"):
            continue
        importlib.import_module(mod_name)
    _LOADED = True


def all_rules() -> list[Type[Rule]]:
    load_all()
    return sorted(_RULES.values(), key=lambda r: r.id)


def get_rule(rule_id: str) -> Type[Rule] | None:
    load_all()
    return _RULES.get(rule_id)


def filter_rules(
    *,
    select: Iterable[str] | None = None,
    ignore: Iterable[str] | None = None,
    llm_enabled: bool = False,
) -> list[Type[Rule]]:
    """Apply --select / --ignore / --llm gates."""
    rules = all_rules()
    select_set = _expand_ids(select) if select else None
    ignore_set = _expand_ids(ignore) if ignore else set()
    out: list[Type[Rule]] = []
    for rule in rules:
        if rule.id in ignore_set:
            continue
        if select_set is not None and rule.id not in select_set:
            continue
        if rule.llm_gated and not llm_enabled:
            continue
        out.append(rule)
    return out


def _expand_ids(ids: Iterable[str]) -> set[str]:
    """Accept exact IDs ("MP010") and dash ranges ("MP001-MP005")."""
    out: set[str] = set()
    for raw in ids:
        token = raw.strip().upper()
        if "-" in token and token.startswith("MP"):
            head, _, tail = token.partition("-")
            if not tail.startswith("MP"):
                tail = f"MP{tail}"
            try:
                start = int(head[2:])
                end = int(tail[2:])
            except ValueError:
                out.add(token)
                continue
            for n in range(start, end + 1):
                out.add(f"MP{n:03d}")
        else:
            out.add(token)
    return out


def run_rules(
    registry: ToolRegistry,
    ctx: RuleContext,
    rules: Iterable[Type[Rule]],
) -> list[Diagnostic]:
    """Execute every rule. A throwing rule emits MP000 and is skipped."""
    diagnostics: list[Diagnostic] = []
    for rule_cls in rules:
        try:
            instance = rule_cls()  # type: ignore[call-arg]
            for diag in instance.check(registry, ctx):
                diagnostics.append(diag)
        except Exception as exc:  # noqa: BLE001 - sandbox each rule
            log.exception("rule %s threw", getattr(rule_cls, "id", "?"))
            diagnostics.append(
                Diagnostic(
                    rule_id="MP000",
                    rule_name="internal-error",
                    category=Category.SCHEMA,
                    severity=Severity.NOTE,
                    message=f"rule {getattr(rule_cls, 'id', '?')} raised: {exc}",
                    file=registry.source_files[0] if registry.source_files else "",
                    docs_url=docs_url("MP000"),
                )
            )
    diagnostics.sort(key=lambda d: (d.file, d.line, d.col, d.rule_id))
    return diagnostics
