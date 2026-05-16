# Huge monorepo

> Who this page is for: someone whose company has multiple MCP servers in one repo, or one server inside a much larger codebase.

## What you will learn

- How to point mcpolish at one subdirectory without linting the world.
- How to keep mcpolish fast on big trees.
- How to share config across multiple MCP servers.

## Background

A monorepo often holds many things mcpolish cannot lint. JavaScript, Go, generated code, vendored libraries. You want to point mcpolish only at the MCP server source it can understand.

mcpolish accepts any file or directory as `TARGET`. It walks down from there. It already skips `.git`, `.venv`, `node_modules`, `__pycache__`, `build`, `dist`, and `.tox`.

## Step by step

### 1. Lint one server inside the monorepo

```
mcpolish lint services/mcp-weather/
```

mcpolish walks only that subtree. The rest of the repo is invisible.

### 2. Lint multiple servers from a single command

mcpolish accepts one target per invocation. To lint several, run several:

```bash
for server in services/mcp-*/; do
    echo "== $server =="
    mcpolish lint "$server" --fail-on never
done
```

Or capture each result to JSON for aggregation later:

```bash
for server in services/mcp-*/; do
    name=$(basename "$server")
    mcpolish lint "$server" --format json --fail-on never > "reports/$name.json"
done
```

### 3. Share config across servers

Put the config at the monorepo root:

```toml
# /pyproject.toml
[tool.mcpolish]
ignore = ["MP025"]

[tool.mcpolish.MP010]
allow = ["search", "query"]
```

mcpolish walks up from `TARGET` until it finds the nearest `pyproject.toml`. If you put the shared config at the repo root, every server picks it up.

If a specific server needs different settings, give it its own `pyproject.toml`:

```
services/mcp-weather/pyproject.toml   # override per server
```

mcpolish stops at the nearest one going up the tree.

## Performance on big trees

mcpolish parses each `.py` file once with [libcst](../concepts/glossary.md#libcst) and runs every rule on the in-memory [IR](../concepts/glossary.md#ir). Measured numbers from this repo:

| Scope | Median time |
|---|---|
| 1 file, 3 tools | 3.7 ms |
| 1 file, 7 tools | 4.3 ms |
| 4 files, 4 tools (modular) | 6.4 ms |
| 40 files, 30 tools | 62.5 ms |

A 1,000-file monorepo scans in roughly 1 to 2 seconds. If you find that too slow, narrow the target.

### When to narrow

If your repo has dozens of unrelated Python files (tests, scripts, dev tools), point mcpolish only at the `tools/` directory or wherever your tool decorators live:

```
mcpolish lint services/mcp-weather/src/
```

If you keep tests next to the source, you can include or exclude them; tests typically have no `@mcp.tool()` decorators, so mcpolish walks past them quickly.

## CI pattern: one job per server

In GitHub Actions:

```yaml
strategy:
  matrix:
    server:
      - mcp-weather
      - mcp-notes
      - mcp-memory
steps:
  - uses: vtensor/mcpolish-action@v1
    with:
      path: services/${{ matrix.server }}
      fail-on: error
```

Each server lints in its own job. The matrix is faster than a single job and a failure on one server does not cancel the others.

## Common variations

### Mixed Python and TypeScript

mcpolish v1 lints Python only. The walker skips `node_modules` automatically, but it still tries to open `.py` files in TypeScript-heavy folders. To narrow:

```
mcpolish lint services/python-servers/
```

### Tracking score over time

Run mcpolish nightly. Store `mcpolish score path/ --json` output in a time series database. The score is a single integer; a chart of "score per server per day" is enough to catch regressions.

### Generated code

If a generator produces `.py` files with MCP tool registrations, mcpolish will lint them. To skip a generated subtree, exclude it from the path you pass:

```
mcpolish lint src/        # not src_generated/
```

## Troubleshooting

**Lint is slower than expected.** Pass `MCPOLISH_LOG=INFO` and look for files that take long to parse. Usually a file with thousands of decorators in a loop.

**One server's config affects another.** The nearest `pyproject.toml` wins. If the wrong file is being picked up, add an empty `pyproject.toml` inside the server's directory so the search stops there.

## See also

- [Multi-file server](multi-file-server.md)
- [Enterprise fleets](enterprise-fleet.md)
- [Configuration](../usage/configuration.md)
