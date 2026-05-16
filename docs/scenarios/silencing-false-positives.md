# Silencing false positives

> Who this page is for: someone hitting a diagnostic they believe is wrong for their case.

## What you will learn

- How to decide whether the diagnostic is wrong, or you are.
- How to silence one rule for one tool.
- How to silence one rule project-wide.
- When to file an issue against mcpolish instead.

## Background

Static analysis is a balance: catch real problems, miss true issues, avoid false alarms. mcpolish picks reasonable defaults, but every project is different. When a rule fires on a tool that is fine, you have three options:

1. Whitelist the specific name or pattern.
2. Disable the rule project-wide.
3. Convince the maintainers the rule is genuinely wrong (open an issue).

This page walks through the first two.

## Is it really a false positive?

Before silencing, check the rule's docs. Run:

```
mcpolish explain MP010
```

The rule's page says exactly what triggers it and why. Often a name that feels fine on first read is one of the patterns the paper [Wang et al., 2026](https://arxiv.org/abs/2602.18914) shows causes wrong-tool selection in real agent use.

If after reading the rule's rationale you still think the diagnostic is wrong, proceed.

## Silence one rule for one tool

mcpolish v1 does not support inline disable comments like `# noqa`. The two ways to narrow are:

### Whitelist the specific value

Most rules expose an `allow` list. Example: MP010 considers `search` too generic. If your tool is `search` and you want to keep that name:

```toml
[tool.mcpolish.MP010]
allow = ["search"]
```

Now `search` is allowed; `get`, `list`, etc. still fire.

### Whitelist a token MP024 flags

MP024 fires on jargon density. To whitelist team-specific acronyms:

```toml
[tool.mcpolish.MP024]
allow = ["MCP", "GCP", "K8S"]
```

### Raise a threshold

If MP020 says your description is too short and you genuinely cannot say more, drop the bar:

```toml
[tool.mcpolish.MP020]
min_chars = 25
```

(Better: write a longer description. But the knob exists.)

## Silence one rule project-wide

```toml
[tool.mcpolish]
ignore = ["MP025"]
```

Add a comment explaining why so future you can remember:

```toml
[tool.mcpolish]
# MP025 disabled because our domain copy uses words like "powerful" intentionally.
ignore = ["MP025"]
```

## Silence with a CLI flag for one run

```
mcpolish lint . --ignore MP025
```

Useful for one-off scans where you do not want to change the config file.

## When you cannot whitelist what you need

If a rule's `allow` list is too coarse and the rule should not be disabled entirely, that is a sign the rule needs a new knob. Open an issue with:

- The rule ID.
- A minimal example of the false positive.
- What knob would resolve it.

Many mcpolish knobs came from issues like this.

## Rules that commonly produce false positives

| Rule | When it falsely fires | How to silence |
|---|---|---|
| MP013 cross-server collision | Internal-only servers where collisions do not matter | `registry = "off"` or `ignore = ["MP013"]` |
| MP024 jargon density | Genuinely domain-heavy descriptions | `allow = ["YOUR_ACRONYM"]` per rule |
| MP025 useless qualifier | Marketing copy that needs to be vivid | `ignore = ["MP025"]` |
| MP022 missing example | When the parameter has only one valid value | Add a single `example` anyway; cheap and improves agent accuracy |

## When NOT to silence

Resist the urge to disable these rules even if they feel noisy:

| Rule | Why to keep it on |
|---|---|
| MP001 require-tool-description | Every tool needs a description. There is no good reason to skip it. |
| MP005 valid-json-schema | A broken schema breaks the agent. Always an error. |
| MP030 param-type-mismatch | A type-vs-description mismatch is the kind of bug that produces wrong-arg failures at runtime. |
| MP040 hidden-prompt-injection | Zero-width characters in a description are almost always an attack. |
| MP041 instruction-in-description | Operator-style instructions are tool-poisoning. |

If one of these fires on what you believe is benign code, dig in. Almost always there is a real problem.

## Common variations

### Silencing for a single CI run

Use the CLI flag in your job config:

```yaml
- run: mcpolish lint . --ignore MP025
```

### Silencing across multiple servers in a monorepo

Put the `ignore` at the monorepo root in `/pyproject.toml`. Every server below it inherits.

## Troubleshooting

**Whitelist did not silence the rule.** Read the rule's allow knob spelling on its detail page. Most are `allow`, but a few use a different key.

**The rule still fires when I include it in `ignore`.** Check that the `ignore` array contains the rule ID exactly as printed in the diagnostic (`MP025`, not `mp025`). The match is case-insensitive in practice, but a typo is the usual cause.

## See also

- [Customising rules](customizing-rules.md)
- [Configuration](../usage/configuration.md)
- [Rules index](../rules/index.md)
