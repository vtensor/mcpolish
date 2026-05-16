# Quickstart

> Who this page is for: someone who wants to see mcpolish do something useful in under a minute.

## What you will learn

- How to install mcpolish.
- How to run your first lint.
- How to read the score.

## Background

mcpolish is a [CLI](../concepts/glossary.md#cli) that reads your [MCP server](../concepts/glossary.md#mcp-server) source code and reports problems with your tool definitions. You point it at a file or a folder and it prints diagnostics.

## Step by step

### 1. Install

```
pip install mcpolish
```

### 2. Lint a known-good example shipped with mcpolish

Clone the repo so you have the example files:

```
git clone https://github.com/vtensor/mcpolish.git
cd mcpolish
mcpolish lint examples/clean_server.py
```

Expected output:

```
mcpolish 0.1.0
server: notes  (3 tools in 1 file)

ok no issues found. score: 100/100
```

A score of `100/100` means every [rule](../concepts/glossary.md#rule) passed.

### 3. Lint a deliberately-broken example

```
mcpolish lint examples/smelly_server.py --fail-on never
```

This file is hand-crafted to fail every rule. The output is long. Look at the end:

```
Found 26 issues (5 errors, 7 warnings, 14 notes). score: 72/100
```

The `--fail-on never` flag tells mcpolish to always exit 0, even when there are errors. Without it, the command would exit with code 1, which is what you want in [CI](../concepts/glossary.md#ci).

### 4. Lint your own server

Replace the path with your file or folder:

```
mcpolish lint path/to/your_server.py
mcpolish lint path/to/your_project/
```

mcpolish accepts a single file or a folder. If you give it a folder, it walks every `.py` file inside and finds tools wherever they live.

### 5. Get just the score

```
mcpolish score path/to/your_server.py
```

Prints a single number. Useful for shell scripts and badges.

## Common variations

If you have a TypeScript MCP server, mcpolish does not lint TypeScript yet (this is on the roadmap). It only reads Python.

If your project uses a config file already, mcpolish reads `[tool.mcpolish]` from `pyproject.toml` automatically. You do not need any flags.

## Troubleshooting

**`mcpolish: command not found`.** See the [installation troubleshooting section](installation.md#troubleshooting).

**`server: unknown  (0 tools in 0 files)`.** mcpolish found no tools in the path you gave it. Check that the file actually uses `@mcp.tool()`, `Tool(...)`, or `server.add_tool(...)`. mcpolish only finds tools registered via those three patterns.

**You see no diagnostics but you know your code has issues.** mcpolish only flags things it knows how to recognise. If the issue is in code behaviour rather than the tool description, mcpolish will not see it.

## See also

- [Your first lint](your-first-lint.md): a longer walkthrough on a real example.
- [Understanding the output](understanding-output.md): what every line of the output means.
- [Rules index](../rules/index.md): every rule mcpolish knows about.
