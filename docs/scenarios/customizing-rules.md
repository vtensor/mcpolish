# Customising rules

> Who this page is for: anyone tuning mcpolish to a team's specific preferences.

## What you will learn

- How to enable, disable, or tune any rule.
- How to write per-rule overrides in `pyproject.toml`.
- How to raise or lower a rule's severity.

## Background

The defaults in mcpolish are sensible. Some teams will want different defaults. The three knobs are: which rules run, what their thresholds are, and how they affect the score. All three are set in `pyproject.toml`.

## Step by step

### 1. Turn a rule off

```toml
[tool.mcpolish]
ignore = ["MP025"]
```

That is it. The rule is silent globally.

You can ignore many rules:

```toml
[tool.mcpolish]
ignore = ["MP021", "MP022", "MP024", "MP025"]
```

### 2. Run only a subset of rules

```toml
[tool.mcpolish]
select = ["MP001-MP013", "MP040", "MP041"]
```

`select` accepts ranges and individual IDs. When `select` is set, every rule not in the list is dropped.

### 3. Tune a rule's threshold

Each rule may expose its own knobs under `[tool.mcpolish.MPxxx]`. The threshold for the minimum description length:

```toml
[tool.mcpolish.MP020]
min_chars = 80
```

The maximum length:

```toml
[tool.mcpolish.MP021]
max_chars = 2000
```

The full list of knobs for each rule lives on the rule's documentation page (linked from the [rules index](../rules/index.md)).

### 4. Whitelist a tool name MP010 flags

```toml
[tool.mcpolish.MP010]
allow = ["search"]
```

Now `def search(...)` is allowed. Other generic names (`get`, `list`, etc.) still fire.

### 5. Add custom words to the generic list

```toml
[tool.mcpolish.MP010]
extra = ["dispatch", "invoke"]
```

These tool names will now fire MP010 in addition to the built-in list.

### 6. Adjust score weights

If your team treats security findings as more serious than description quibbles:

```toml
[tool.mcpolish.score_weights]
schema = 0.10
naming = 0.20
description = 0.20
consistency = 0.20
security = 0.30
```

The total does not need to be 1.0; mcpolish normalises.

## Per-rule customisation examples

### MP013 cross-server collision

Disable the check entirely (useful for internal-only servers):

```toml
[tool.mcpolish]
ignore = ["MP013"]
```

Or raise the bar (require 5 collisions before firing):

```toml
[tool.mcpolish.MP013]
min_collisions = 5
```

Or use a different registry mode:

```toml
[tool.mcpolish]
registry = "off"
```

### MP014 snake vs camel

Force camelCase:

```toml
[tool.mcpolish.MP014]
style = "camel"
```

Force snake_case:

```toml
[tool.mcpolish.MP014]
style = "snake"
```

Auto-detect the dominant style in the project and flag outliers:

```toml
[tool.mcpolish.MP014]
style = "auto"
```

### MP022 missing example

Require two examples instead of one:

```toml
[tool.mcpolish.MP022]
required_examples = 2
```

### MP024 jargon density

Allow more all-caps tokens:

```toml
[tool.mcpolish.MP024]
max_ratio = 0.40
```

Add custom acronyms to the whitelist:

```toml
[tool.mcpolish.MP024]
allow = ["MCP", "K8S", "GCP", "AWS"]
```

## Putting it all together

A realistic team config:

```toml
[tool.mcpolish]
target-version = "2025-11"
ignore = ["MP025"]                   # we like marketing language
registry = "official"

[tool.mcpolish.MP010]
allow = ["search"]                    # one allowed exception

[tool.mcpolish.MP020]
min_chars = 80                        # stricter than default

[tool.mcpolish.MP024]
allow = ["MCP", "K8S", "AWS", "GCP"]  # team acronyms

[tool.mcpolish.score_weights]
security = 0.20                       # weight security more
schema = 0.20
naming = 0.30
description = 0.20
consistency = 0.10
```

## Common variations

### Per-project, not per-user

`pyproject.toml` is per-project. There is no per-user config. The team's settings live in the repo.

### Branch-specific config

If your release branch needs different rules than main, run with `--select`/`--ignore` overrides in that branch's CI. Or check in a different `pyproject.toml` per branch (rarely done in practice).

### Strictest possible

```toml
[tool.mcpolish]
target-version = "2025-11"
```

That is it. No overrides. Every rule fires at the default severity. This is the strictest configuration.

## Troubleshooting

**The override does not take effect.** Run `mcpolish doctor` to confirm mcpolish is reading the right file. The output shows the resolved config.

**`invalid [tool.mcpolish.MPxxx] section`.** A key is misspelled or has the wrong type. The error message names the field.

## See also

- [Configuration](../usage/configuration.md)
- [Silencing false positives](silencing-false-positives.md)
- [Rules index](../rules/index.md)
