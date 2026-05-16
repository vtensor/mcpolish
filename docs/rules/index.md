# Rules index

> Who this page is for: anyone looking up what a specific rule does.

mcpolish ships 23 first-party rules. Each rule has a stable [rule ID](../concepts/glossary.md#rule-id) like `MP010` and a human name like `generic-tool-name`. The ID never changes. The name may be tweaked but the slug stays.

Rules are grouped into five [categories](../concepts/what-mcpolish-checks.md): schema, naming, description, consistency, security. Categories carry weight in the [score](../concepts/glossary.md#score).

## Schema (5 rules)

The tool is missing required pieces of metadata.

| ID | Name | Severity | Auto-fix |
|---|---|---|---|
| [MP001](MP001.md) | require-tool-description | error | safe |
| [MP002](MP002.md) | require-param-description | warning | - |
| [MP003](MP003.md) | require-return-schema | note | - |
| [MP004](MP004.md) | require-required-array | warning | - |
| [MP005](MP005.md) | valid-json-schema | error | - |

## Naming (5 rules)

Tool names confuse the agent.

| ID | Name | Severity | Auto-fix |
|---|---|---|---|
| [MP010](MP010.md) | generic-tool-name | warning | - |
| [MP011](MP011.md) | redundant-prefix | error | unsafe |
| [MP012](MP012.md) | inconsistent-verb-pattern | warning | - |
| [MP013](MP013.md) | name-collision-cross-server | warning | - |
| [MP014](MP014.md) | snake-vs-camel | note | - |

## Description (7 rules)

The English text agents read has problems.

| ID | Name | Severity | Auto-fix | LLM |
|---|---|---|---|---|
| [MP020](MP020.md) | description-too-short | warning | - | - |
| [MP021](MP021.md) | description-too-long | note | - | - |
| [MP022](MP022.md) | missing-example | note | - | - |
| [MP023](MP023.md) | no-trigger-condition | note | - | - |
| [MP024](MP024.md) | jargon-density | note | - | - |
| [MP025](MP025.md) | useless-qualifier | note | - | - |
| [MP026](MP026.md) | ambiguous-description | warning | - | yes |

## Consistency (4 rules)

Pieces of metadata disagree with each other.

| ID | Name | Severity | Auto-fix | LLM |
|---|---|---|---|---|
| [MP030](MP030.md) | param-type-mismatch | error | - | - |
| [MP031](MP031.md) | param-meaning-mismatch | warning | - | yes |
| [MP032](MP032.md) | undocumented-side-effect | error | - | yes |
| [MP033](MP033.md) | duplicate-tool-description | error | - | - |

## Security (2 rules)

The description contains a known attack pattern.

| ID | Name | Severity | Auto-fix |
|---|---|---|---|
| [MP040](MP040.md) | hidden-prompt-injection | error | - |
| [MP041](MP041.md) | instruction-in-description | error | - |

## See also

- [What mcpolish checks](../concepts/what-mcpolish-checks.md)
- [The rule system](../concepts/the-rule-system.md)
- [Methodology and citations](../methodology.md)
