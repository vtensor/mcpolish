# What is a linter?

> Who this page is for: someone who has not used a tool like ESLint, Pylint, or Ruff before.

## What you will learn

- What "linting" means.
- How a linter is different from a compiler or a test runner.
- Why linters exist.
- How mcpolish fits the same shape as other linters you may have seen.

## Background

A **linter** is a program that reads your source code and points out problems without running it. The word comes from a Unix tool from 1978 called `lint` that flagged suspicious C code.

The key feature of a linter is that it never executes your code. It only reads it. That means it is safe to run on code from the internet, on broken code, or on code in a partial state.

## How a linter differs from other tools

| Tool | What it does | Does it run your code? |
|---|---|---|
| Compiler | Translates source code to a binary or bytecode. | No, but the binary later does. |
| Test runner | Runs the tests in your code. | Yes. |
| Type checker | Checks that the types in your code agree. | No. |
| **Linter** | Checks your code against a set of style and correctness rules. | No. |

A linter sits between the type checker and the test runner. It catches problems that the type system cannot express but that are not yet bugs in production.

## Familiar examples

You may have used one of these:

| Linter | For | Famous for |
|---|---|---|
| ESLint | JavaScript and TypeScript | The reference design. Rules are configurable per project. |
| Pylint | Python | One of the first popular Python linters. |
| Ruff | Python | Same as Pylint, written in Rust for speed. |
| Hadolint | Dockerfile | Catches common Dockerfile mistakes. |
| Clippy | Rust | Ships with the standard Rust toolchain. |
| Stylelint | CSS | Catches style issues. |

Each one has a set of rules with stable IDs (`E501`, `react/no-unused-vars`, `DL3008`, `clippy::needless_return`). You enable, disable, or tune rules through a config file. You run the linter as a [CLI](glossary.md#cli) or as a step in [CI](glossary.md#ci).

mcpolish follows the same shape, but the rules are specific to MCP tool definitions.

## What rules look like

A rule is one specific check. For example, ESLint's `no-unused-vars` says: "If you declared a variable but never used it, that is probably a bug." It produces a [diagnostic](glossary.md#diagnostic) for every offence.

mcpolish has 23 rules. Each rule has:

- A stable ID, like `MP010`.
- A short human-readable name, like `generic-tool-name`.
- A default severity: error, warning, or note.
- A description of what triggers it.
- Sometimes an autofix.

Each rule looks at your code and either stays quiet or emits diagnostics. mcpolish runs all enabled rules and collects everything into one report.

## Why linters exist

Three reasons:

1. **Catch problems early.** A linter runs in milliseconds, before tests, before merging, before shipping. Catching a wrong-tool selection bug in mcpolish is faster than catching it from a user report.
2. **Encode lessons.** Each rule is a written-down piece of experience. "Do not use generic tool names." "Always document return values." Codifying these lessons means new contributors get the same standard.
3. **Decouple style from review.** Reviewers do not have to argue about consistency; the linter handles it. They can focus on the actual change.

## How mcpolish fits the same shape

| ESLint | mcpolish |
|---|---|
| `eslint .` | `mcpolish lint .` |
| `.eslintrc.json` | `pyproject.toml` `[tool.mcpolish]` |
| `no-unused-vars` | `generic-tool-name` |
| `error`, `warn`, `off` | `error`, `warn`, `note`, or excluded |
| `// eslint-disable-next-line` | (planned for v2; today use config) |
| ESLint plugin | (no plugin system in v1, by design) |

If you know any linter, you know mcpolish. The vocabulary is the same.

## Common variations

A linter is sometimes called a "static analyser" because it analyses code statically (without running it). The terms are interchangeable. mcpolish is a static analyser. So is mypy. So is Ruff.

## See also

- [What is MCP](what-is-mcp.md)
- [What mcpolish checks](what-mcpolish-checks.md)
- [The rule system](the-rule-system.md)
