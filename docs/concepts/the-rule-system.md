# The rule system

> Who this page is for: someone who wants to understand how rules are organised, why their IDs are stable, and how to think about adding or disabling rules.

## What you will learn

- The anatomy of a rule.
- Why rule IDs never change once they ship.
- How rules are turned on, off, or tuned per project.
- Why mcpolish does not have a plugin system in v1.

## Background

A [rule](glossary.md#rule) is one specific check that mcpolish performs on your tool definitions. It is implemented as a Python class with a single method. Each rule lives in its own file under `src/mcpolish/rules/`.

mcpolish ships 23 rules in v1. Their IDs run `MP001` through `MP041`. The gaps are intentional: room to add more rules within a category without breaking sort order.

## Anatomy of a rule

Every rule has six pieces of metadata, plus the check method.

| Piece | Example | Stable? |
|---|---|---|
| `id` | `MP010` | Yes, forever. |
| `name` | `generic-tool-name` | Yes, forever. |
| `category` | `naming` | Yes. |
| `severity_default` | `warning` | May change between versions, but rarely. |
| `auto_fixable` | `False` | May change. |
| `llm_gated` | `False` | May change. |
| `summary` | "tool name is too generic..." | May be rephrased. |

The check method looks like this:

```python
def check(self, registry, ctx):
    for tool in registry.tools:
        if some_condition(tool):
            yield Diagnostic(rule_id="MP010", ...)
```

The runner calls `check()` once per scan, passes the IR plus per-rule config, and collects the diagnostics into the final report.

## Why rule IDs are stable

If you write a config like this:

```toml
[tool.mcpolish]
ignore = ["MP025"]
```

You need that line to keep working in future releases. If we renamed `MP025` to `MP025X` or to a different number, your config would silently stop working.

This is the same promise ESLint makes for rule names, Ruff makes for codes, and Hadolint makes for `DL...` numbers. Once a rule ships, its ID is fixed.

What can change about a rule:

- The default severity. We may downgrade a noisy rule to `note` or upgrade a critical one to `error`.
- The summary text. Phrasing improves over time.
- The internal algorithm. We may make the check more precise.

What never changes:

- The ID. `MP010` always means `generic-tool-name`.
- The name. The slug after the ID.
- The category. A naming rule stays a naming rule.

## Turning rules on and off

Three layers of control, in priority order from outermost to innermost:

1. **CLI flags**: `--select` and `--ignore` (highest priority).
2. **`pyproject.toml` settings**: `[tool.mcpolish] select` and `ignore` arrays.
3. **Defaults**: every non-LLM rule is on, LLM-gated rules are off without `--llm`.

Examples:

```
mcpolish lint . --ignore MP025
mcpolish lint . --select MP001 --select MP002
mcpolish lint . --select MP001-MP005
```

The range syntax `MP001-MP005` expands to `{MP001, MP002, MP003, MP004, MP005}`.

## Tuning rules

Each rule can expose its own config knobs. Common ones:

- `allow`: a list of names or tokens to whitelist for that rule.
- `min_chars` / `max_chars`: thresholds (for MP020, MP021).
- `extra`: additional values to add to a rule's built-in list.

Set them under `[tool.mcpolish.MPxxx]`:

```toml
[tool.mcpolish.MP010]
allow = ["search"]
extra = ["dispatch"]

[tool.mcpolish.MP020]
min_chars = 80
```

Per-rule pages under [Rules](../rules/index.md) document every knob.

## Why no plugin system in v1

Two reasons:

1. **Quality control.** A first-party rule set means every rule comes with citations, tests, and a doc page. A community plugin ecosystem fragments that. Ruff made the same call: ship one well-curated set.
2. **Stability.** A plugin system means every plugin needs a stable internal API. mcpolish is young; that API will change. Locking it in now would slow improvement.

If you have a rule you would like in mcpolish, open an issue with the case. Many of the existing rules came from user reports.

## How LLM-gated rules differ

Three rules use a Large Language Model as a judge: `MP026`, `MP031`, `MP032`. They follow the same shape as other rules but they need a real LLM call to make a decision. They are off by default. You opt in with:

```
mcpolish lint . --llm openai:gpt-4o
```

See [LLM rules](../usage/llm-rules.md) for details on providers, caching, and cost.

## Common variations

### Listing what is enabled

```
mcpolish explain
```

Prints every rule, including the LLM-gated ones (marked `[LLM]`). It does not show what is currently enabled in your config, just what mcpolish knows about.

### Disabling per file

mcpolish v1 does not support comment-based disables like `# noqa`. If you need to silence a rule for one file or one tool, use the `allow` table in `pyproject.toml`. Tracked for v2.

## See also

- [Rules index](../rules/index.md)
- [What mcpolish checks](what-mcpolish-checks.md)
- [Configuration](../usage/configuration.md)
