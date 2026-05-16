# Glossary

> Who this page is for: anyone who hits a word in the docs they do not recognise.

Every short form and technical word that appears anywhere in the mcpolish docs has an entry below. Other pages link here on first use.

## A

### AST
Short for **Abstract Syntax Tree**. The tree a parser builds when it reads source code. The leaves are things like names, numbers, and strings. The branches are things like function definitions and if statements. mcpolish uses a richer cousin called [CST](#cst).

### autofix
A change mcpolish can make to your source code on your behalf. Some autofixes are [safe](#safe-fix). Some are [unsafe](#unsafe-fix). See [Autofix](../usage/autofix.md).

## B

### BaseModel
The base class in [Pydantic](#pydantic). When a tool takes a `BaseModel` as a parameter, the model defines the schema for that parameter.

### badge
A small image that shows a score. Like the green or red labels you see on GitHub README files. mcpolish can write one to a file with `mcpolish score --badge badge.svg`.

## C

### CI
Short for **Continuous Integration**. The automated checks that run when you push code to a service like GitHub or GitLab. If the checks fail, the build is marked red and you have to fix the problem before merging. mcpolish is designed to run as a CI check. See [GitHub Actions setup](../scenarios/ci-github.md) and [GitLab CI setup](../scenarios/ci-gitlab.md).

### CLI
Short for **Command Line Interface**. A program you run by typing commands into your terminal. `mcpolish lint server.py` is a CLI command. See the [CLI reference](../usage/cli-reference.md).

### CST
Short for **Concrete Syntax Tree**. Like an [AST](#ast) but keeps every space, comment, and newline. mcpolish uses CST through the [libcst](#libcst) library so that line numbers in diagnostics line up with the actual source.

## D

### decorator
A Python feature that wraps a function in something else. In MCP code you write `@mcp.tool()` above a function. That decorator registers the function as a tool. mcpolish recognises this pattern.

### diagnostic
One single complaint from mcpolish. A diagnostic includes the rule ID, the severity, the file and line, a message, and often a hint. mcpolish prints one diagnostic per problem.

## F

### FastMCP
A convenience class in the official `mcp` Python SDK that lets you write tools with decorators. `FastMCP("name")` creates a server. `@mcp.tool()` registers a tool. The other style is the lower-level `Server(...)` plus `Tool(...)` constructor.

### fixer
The code inside mcpolish that knows how to repair a specific diagnostic. Each rule may have a fixer. See [Autofix](../usage/autofix.md).

### fixture
A small example file used by the test suite to exercise one specific scenario. mcpolish ships about 50 fixtures under `tests/fixtures/scenarios/`.

## I

### IR
Short for **Intermediate Representation**. A simplified, in-memory view of your tools that all 23 rules read from. mcpolish parses your file once to build the IR, then every rule walks the IR. This is why mcpolish is fast even with many rules.

## J

### JSON
A common data format. Used by mcpolish for machine-readable output (`--format json`).

### JSON Schema
A standard way to describe the shape of a JSON value. MCP uses JSON Schema (draft 2020-12) for its `inputSchema` and `outputSchema` fields. mcpolish validates that your schema is well-formed.

## L

### libcst
A Python library, made by Instagram, that parses Python source into a [CST](#cst) you can walk and edit. mcpolish uses libcst for its Python discoverer.

### linter
A program that reads your code and flags problems without running it. ESLint, Pylint, and Ruff are linters for general code. mcpolish is a linter for MCP tool descriptions.

### LLM
Short for **Large Language Model**. The model your agent uses (Claude, GPT, Gemini, etc.). mcpolish has three optional rules that use an LLM as a judge. See [LLM rules](../usage/llm-rules.md).

## M

### MCP
Short for **Model Context Protocol**. An open protocol that lets AI agents call tools provided by separate small programs called MCP servers. Anthropic donated MCP to the Linux Foundation in December 2025. See [What is MCP](what-is-mcp.md).

### MCP server
A small program that exposes one or more tools to an MCP-aware agent. You write one when you want Claude or another agent to be able to call your code.

## N

### namespace
The name of the server, used by MCP hosts to disambiguate tools from different servers. If you write `FastMCP("memnex")`, your namespace is `memnex`. Agents see your tool as `memnex/your_tool_name`.

## P

### parser
A program that reads source code text and turns it into a tree. mcpolish uses [libcst](#libcst) as its Python parser.

### pre-commit
A tool that runs checks on your files just before you make a git commit. mcpolish ships a pre-commit hook so problems are caught locally before they reach a pull request. See [Pre-commit setup](../scenarios/pre-commit-setup.md).

### Pydantic
A popular Python library for data validation. MCP code often uses Pydantic [BaseModels](#basemodel) to define tool parameter shapes.

## R

### registry
1. The internal list of rules inside mcpolish.
2. A directory of public MCP servers, run by services like Smithery, Glama, or PulseMCP.
3. The [registry snapshot](#registry-snapshot) bundled inside mcpolish.

### registry snapshot
A small dataset bundled inside mcpolish that lists tool names used by popular public MCP servers. Used by rule MP013 to flag cross-server name collisions. Refreshed quarterly in the open-source build.

### rule
One single check that mcpolish performs. Each rule has a stable ID like `MP010` and a human-readable name like `generic-tool-name`. mcpolish has 23 rules in v1.

### rule ID
The stable identifier of a rule, like `MP001` or `MP041`. Stable means it never changes after a rule ships. You can put rule IDs in your config to silence or select specific rules.

## S

### safe fix
An autofix mcpolish can apply with no risk of changing the public behaviour of your tool. The MP001 fix that inserts a placeholder docstring is safe. Applied with `--fix`.

### SARIF
Short for **Static Analysis Results Interchange Format**. A JSON format that GitHub and GitLab understand for code-scanning results. mcpolish emits SARIF with `--format sarif`.

### score
A whole number from 0 to 100 that summarises the quality of your tool descriptions. 100 means no problems found. The score is computed from the diagnostics. See [How scoring works](how-scoring-works.md).

### severity
How serious mcpolish thinks a diagnostic is. Three levels: `error`, `warning`, and `note`. CI usually fails only on errors. See [How scoring works](how-scoring-works.md).

### smell
Borrowed from the "code smell" idea. A pattern in your tool description that is not technically wrong but is known to cause agents to pick the wrong tool. Many mcpolish rules detect description smells.

### source code
The text you wrote in a `.py` file. mcpolish reads source code; it does not run your server.

### stable ID
A rule ID that the project promises never to change. mcpolish stable IDs let you write `[tool.mcpolish] ignore = ["MP010"]` and trust that the line will keep working in future releases.

## T

### tool
A function in your MCP server that an agent can call. Each tool has a name, a description, and an input schema. mcpolish lints those three things plus a few others.

### tool description
The English text attached to a tool. The agent reads this text to decide whether to call the tool. Bad descriptions are the main reason agents pick the wrong tool. See [What mcpolish checks](what-mcpolish-checks.md).

## U

### unsafe fix
An autofix that may change the public API of your tool. The MP011 rename fix is unsafe because callers may reference the old name. Applied only with `--unsafe-fix`.
