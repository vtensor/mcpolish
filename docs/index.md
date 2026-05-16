# mcpolish documentation

> Who this page is for: anyone who just landed on the docs and is looking for the right entry point.

mcpolish is a static checker for [MCP](concepts/glossary.md#mcp) server source code. It reads the tool definitions in your `.py` files and reports problems that would cause an AI agent to pick the wrong tool, fail silently, or be tricked by a malicious tool description.

If you have never used a [linter](concepts/glossary.md#linter), think of it as a spellchecker for your tool descriptions.

## Choose your starting point

| You are... | Start here |
|---|---|
| Brand new to mcpolish | [Quickstart](getting-started/quickstart.md) (30 seconds) |
| Brand new to MCP itself | [What is MCP](concepts/what-is-mcp.md) |
| Setting up your first project | [Your first lint](getting-started/your-first-lint.md) |
| Trying to understand the output | [Understanding output](getting-started/understanding-output.md) |
| Looking for a specific command or flag | [CLI reference](usage/cli-reference.md) |
| Wiring mcpolish into [CI](concepts/glossary.md#ci) | [GitHub setup](scenarios/ci-github.md) or [GitLab setup](scenarios/ci-gitlab.md) |
| Hitting a diagnostic and want to understand it | [Rules index](rules/index.md) |

## What problem does this solve?

When you build an MCP server, you give each tool a name and a description in English. An AI agent (Claude, GPT, Gemini) reads those descriptions to decide which tool to call. If your descriptions are vague, generic, or misleading, the agent picks the wrong tool.

In research published in 2026, vague descriptions caused **52 percentage points** more wrong-tool selections in head-to-head tests. mcpolish detects 23 specific problems that lead to this failure, before you ship.

See [What mcpolish checks](concepts/what-mcpolish-checks.md) for the five problem categories.

## 30-second tour

```
pip install mcpolish
mcpolish lint your_server.py
```

That is it. mcpolish prints any problems it finds, gives each one a stable rule ID, and exits non-zero if there are errors. Wire that into your [CI](concepts/glossary.md#ci) and you have a quality gate.

## Documentation map

### Getting started
- [Installation](getting-started/installation.md)
- [Quickstart](getting-started/quickstart.md)
- [Your first lint](getting-started/your-first-lint.md)
- [Understanding the output](getting-started/understanding-output.md)

### Concepts
- [What is MCP](concepts/what-is-mcp.md)
- [What is a linter](concepts/what-is-a-linter.md)
- [What mcpolish checks](concepts/what-mcpolish-checks.md)
- [How scoring works](concepts/how-scoring-works.md)
- [The rule system](concepts/the-rule-system.md)
- [Glossary](concepts/glossary.md)

### Usage
- [CLI reference](usage/cli-reference.md)
- [Python API](usage/python-api.md)
- [Configuration](usage/configuration.md)
- [Output formats](usage/output-formats.md)
- [Autofix](usage/autofix.md)
- [LLM-gated rules](usage/llm-rules.md)

### Scenarios
- [Single-file server](scenarios/single-file-server.md)
- [Multi-file server](scenarios/multi-file-server.md)
- [Tool() constructor style](scenarios/tool-constructor-server.md)
- [Huge monorepo](scenarios/huge-monorepo.md)
- [Brand new project](scenarios/new-project.md)
- [Existing project](scenarios/existing-project.md)
- [Customising rules](scenarios/customizing-rules.md)
- [Silencing false positives](scenarios/silencing-false-positives.md)
- [GitHub Actions](scenarios/ci-github.md)
- [GitLab CI](scenarios/ci-gitlab.md)
- [Pre-commit hook](scenarios/pre-commit-setup.md)
- [Enterprise fleets](scenarios/enterprise-fleet.md)

### Rules
- [Rules index (all 23)](rules/index.md)

### Other
- [Methodology and citations](methodology.md)
