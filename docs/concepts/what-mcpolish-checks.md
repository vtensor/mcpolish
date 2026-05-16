# What mcpolish checks

> Who this page is for: someone who wants the full picture of the 23 rules, grouped by intent.

## What you will learn

- The five rule categories.
- One sentence per rule, explaining what it looks for.
- Which rules are LLM-gated.
- Which rules can apply [autofixes](glossary.md#autofix).

## Background

mcpolish ships 23 [rules](glossary.md#rule). Each rule has a stable ID like `MP001`. Rules are grouped by category. Categories carry weight in the [score](glossary.md#score).

| Category | Default weight | What it covers |
|---|---|---|
| schema | 0.20 | Tools are missing required pieces of metadata. |
| naming | 0.30 | Tool names confuse agents. |
| description | 0.30 | The English text is too short, too long, too vague, or too jargon-heavy. |
| consistency | 0.15 | The schema and the description disagree. |
| security | 0.05 | The description contains a known attack pattern. |

The weights are configurable (see [Configuration](../usage/configuration.md)). They determine how much each finding moves the score. The descriptions of every rule live on [their detail pages](../rules/index.md).

## Schema rules (5)

These rules check that the tool has the required pieces of metadata.

| ID | Name | What triggers it | Default severity |
|---|---|---|---|
| MP001 | require-tool-description | Tool has no description at all. | error (auto-fixable) |
| MP002 | require-param-description | A parameter has no description. | warning |
| MP003 | require-return-schema | Description never says what the tool returns and there is no `outputSchema`. | note |
| MP004 | require-required-array | Hand-written `inputSchema` declares properties but no `required` list. | warning |
| MP005 | valid-json-schema | `inputSchema` is not a valid JSON Schema 2020-12 object. | error |

## Naming rules (5)

These rules check that the tool name will not confuse an agent.

| ID | Name | What triggers it | Default severity |
|---|---|---|---|
| MP010 | generic-tool-name | Name is on a list of low-information words like `search`, `get`, `run`. | warning |
| MP011 | redundant-prefix | Name starts with the server's [namespace](glossary.md#namespace), so the agent sees `memnex/memnex_search`. | error (auto-fixable, unsafe) |
| MP012 | inconsistent-verb-pattern | A tool uses a synonym of the verb other tools use (`fetch_post` next to `get_user`). | warning |
| MP013 | name-collision-cross-server | Name collides with at least two other public servers' tools (from the bundled [snapshot](glossary.md#registry-snapshot)). | warning |
| MP014 | snake-vs-camel | One tool uses a casing convention different from the rest of the server. | note |

## Description rules (7)

These rules check the English text agents read.

| ID | Name | What triggers it | Default severity |
|---|---|---|---|
| MP020 | description-too-short | Description is below the minimum character count (default 50). | warning |
| MP021 | description-too-long | Description is above the maximum (default 1500). | note |
| MP022 | missing-example | A free-form parameter (string, object, array) has no example value. | note |
| MP023 | no-trigger-condition | Description never says when an agent should pick this tool. | note |
| MP024 | jargon-density | Description has too many all-caps acronyms relative to its length. | note |
| MP025 | useless-qualifier | Description contains marketing words like "simply", "just", "powerful". | note |
| MP026 | ambiguous-description | An [LLM](glossary.md#llm) judge says the description does not tell the agent what to do. | warning (LLM-gated) |

## Consistency rules (4)

These rules check that pieces of metadata agree with each other.

| ID | Name | What triggers it | Default severity |
|---|---|---|---|
| MP030 | param-type-mismatch | Param typed `string` but description has numeric words like "count" or "limit". | error |
| MP031 | param-meaning-mismatch | LLM judge says the param name, type, and description disagree. | warning (LLM-gated) |
| MP032 | undocumented-side-effect | Tool name implies mutation (e.g. `delete_user`) but description reads as read-only. | error (LLM-gated) |
| MP033 | duplicate-tool-description | Two tools in the same server share the exact description. | error |

## Security rules (2)

These rules look for known tool-poisoning patterns.

| ID | Name | What triggers it | Default severity |
|---|---|---|---|
| MP040 | hidden-prompt-injection | Description contains zero-width or bidi control characters. | error |
| MP041 | instruction-in-description | Description contains operator-style instructions ("ignore previous", chat-template tokens). | error |

## How to see the same information in the terminal

```
mcpolish explain
```

Prints every rule with its category, severity, and one-line summary. Use it as a quick reference.

```
mcpolish explain MP010
```

Prints the detail of one rule.

## Common variations

The default severities are sensible starting points. You can change any of them in `pyproject.toml`. See [Configuration](../usage/configuration.md).

Three rules are [LLM-gated](glossary.md#llm). They never run without `--llm provider:model`. See [LLM rules](../usage/llm-rules.md).

## See also

- [Rules index](../rules/index.md)
- [How scoring works](how-scoring-works.md)
- [The rule system](the-rule-system.md)
