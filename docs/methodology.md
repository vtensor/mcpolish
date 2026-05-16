# Methodology

> Who this page is for: a skeptic who wants to know where each rule comes from.

## What you will learn

- The papers and operational sources behind every rule.
- The known limits of what mcpolish can prove.
- Why the rule IDs are stable forever.

## Background

Every mcpolish rule is grounded in either a published paper, a documented attack, or a clear operational pattern. This page lists each source so you can read the original work and judge for yourself whether the rule should apply to your project.

## Primary sources

| Source | Citation |
|---|---|
| Wang et al., "From Docs to Descriptions: Smell-Aware Evaluation of MCP Server Descriptions" | [arXiv:2602.18914](https://arxiv.org/abs/2602.18914), February 2026. Analysed 10,831 public MCP servers. Catalogued 18 description smells across 4 dimensions. Ran a controlled mutation experiment showing each smell causes wrong-tool selection regressions, p<0.001. |
| Li et al., "Don't believe everything you read: Understanding and Measuring MCP Behavior under Misleading Tool Descriptions" | [arXiv:2602.03580](https://arxiv.org/abs/2602.03580), February 2026. Static analysis of 10,240 MCP servers. Quantifies parameter mismatches and undocumented side effects. |
| Anthropic tool-use guidance | Internal evaluation. Cited in Wang 2026 section 6 discussion as the source for the "1 to 3 short paragraphs" description length recommendation. |
| Invariant Labs tool-poisoning advisories | May 2025. Documented zero-width character injection and operator-style instructions in tool descriptions in the wild. Snyk acquired Invariant Labs in June 2025. |
| MCP-Scan (Invariant Labs / Snyk) | [github.com/invariantlabs-ai/mcp-scan](https://github.com/invariantlabs-ai/mcp-scan). Attack catalogue for malicious tool descriptions. |

## Rule provenance table

| Rule | Source | Key finding |
|---|---|---|
| MP001 | Wang section 4.2 | An empty description is 52 percentage points worse in head-to-head selection. |
| MP002 | Wang section 4.4 | 1,285 of 10,831 servers had at least one undocumented parameter. |
| MP003 | Wang Table 4 | 3,093 of 10,831 servers shipped no return-value documentation. |
| MP004 | MCP spec | JSON Schema 2020-12 requires explicit `required` when any property is mandatory. |
| MP005 | MCP spec | The root of `inputSchema` must be a JSON Schema 2020-12 object. |
| MP010 | Wang section 4.3 | "Low-information name" smell increases wrong-tool selection by 8.8 percentage points. |
| MP011 | Operational | MCP hosts namespace tools by server name. Repeating the namespace inside the tool name wastes context tokens. |
| MP012 | Wang section 4.3 | Inconsistent verbs in the same server degrade in-server discrimination. |
| MP013 | Wang section 3.1 | 73 percent of analysed servers shared at least one tool name with another server. |
| MP014 | Operational | Mixing snake_case and camelCase within one server breaks predictability for the agent. |
| MP020 | Wang section 4.2 | Descriptions under 50 characters are 3.4 times more likely to cause wrong-tool selection. |
| MP021 | Anthropic guidance | Beyond about 1500 characters, descriptions burn context tokens without measurable accuracy gain. |
| MP022 | Wang section 4.4 | Missing example is a top-3 description smell by effect size. |
| MP023 | Wang section 4.5 | "Passive" descriptions without trigger language cause 6.8 percentage point regressions. |
| MP024 | Operational | Acronym-dense descriptions fail outside the team that wrote them. |
| MP025 | Wang section 4.5 | Marketing qualifiers ("simply", "powerful") add no signal. Cited as a description smell. |
| MP026 | Wang aggregate | An LLM judge variant of the above; catches cases the static heuristics miss. |
| MP030 | Li section 3 | 3,449 of 10,240 servers had a parameter type that disagreed with its description. |
| MP031 | Li section 3 | LLM-judged variant of MP030. Detects mismatches the keyword heuristic misses. |
| MP032 | Li section 4 | 1,326 servers performed undocumented mutating operations. |
| MP033 | Wang section 4.3 | Duplicate descriptions force the agent to disambiguate on names alone. |
| MP040 | Invariant Labs, May 2025 | Tool-poisoning via zero-width and bidi control characters in descriptions. |
| MP041 | MCP-Scan attack catalogue | Operator-style instructions ("ignore previous", chat-template tokens) embedded in tool descriptions. |

## Why this matters

Wang et al. ran a head-to-head selection experiment: agents picked between a clean tool and a smelly tool with the same name. Clean descriptions won 72 percent of the time. Smelly descriptions won 20 percent. The 52-percentage-point gap is the headline number that motivates the whole project.

Each rule in mcpolish targets at least one of the smells the paper isolated, or one of the attack patterns Invariant Labs catalogued.

## Limits

### What mcpolish does not check

- It does not run your function body. The behaviour of the code is invisible.
- It does not follow imports across packages. Tools registered by a third party are not visible.
- It does not validate semantic correctness of the description against your actual implementation. An MP032-style LLM judge approximates this for one specific case (read-vs-write mismatch).

### Heuristic vs. judge

Several rules are heuristic (regex or token-based). They have false positives. The three LLM-gated rules cost real money but catch cases the heuristics miss. mcpolish is honest about which is which on each rule's detail page.

### Cross-server snapshot freshness

The bundled snapshot is refreshed quarterly in OSS, more frequently in SaaS. A tool name that has just become a collision today will not be flagged until the next refresh. This is a known limit.

### Stable IDs

Once an `MPxxx` rule ID ships, it never changes. You can put `ignore = ["MP025"]` in your config and trust it to keep working. The default severity may change between versions, but the meaning of the ID does not.

## See also

- [What mcpolish checks](concepts/what-mcpolish-checks.md)
- [Rules index](rules/index.md)
- [The rule system](concepts/the-rule-system.md)
