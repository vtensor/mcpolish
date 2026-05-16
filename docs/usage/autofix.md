# Autofix

> Who this page is for: someone considering whether to let mcpolish rewrite their source code.

## What you will learn

- How mcpolish autofixes work.
- The difference between [safe](../concepts/glossary.md#safe-fix) and [unsafe](../concepts/glossary.md#unsafe-fix) fixes.
- Which rules ship with a fix in v1.
- How to apply, preview, and revert fixes.

## Background

Some mcpolish diagnostics come with an attached fix. A fix is a deterministic edit to your source code that resolves the diagnostic. You opt in with `--fix` (safe fixes only) or `--unsafe-fix` (safe plus unsafe).

mcpolish never applies a fix unless you ask. Without a flag, `--fix` and `--unsafe-fix` are both off.

## Safe versus unsafe

| Kind | Flag | Property |
|---|---|---|
| Safe fix | `--fix` | Cannot change the tool's public name or schema. Pure additions. |
| Unsafe fix | `--unsafe-fix` | May rename a tool or change its schema. Callers of the tool may need updates. |

This split is the same model Biome uses for JavaScript.

## Fixes in v1

| Rule | Fix kind | What it does |
|---|---|---|
| MP001 | safe | Inserts a TODO placeholder docstring so the description rules can run cleanly. |
| MP011 | unsafe | Renames the tool to drop the redundant prefix (`memnex_search` -> `search`). |

More fixes will land in future releases. The protocol is stable, so a fix added later is opt-in just like these.

## Step by step

### 1. See what is fixable

```
mcpolish lint . --fail-on never
```

Any diagnostic with `[fixable]` in `mcpolish explain` is a candidate. JSON output shows `"fix": {"safe": true}` or `"fix": {"safe": false}` per diagnostic.

### 2. Preview the changes

mcpolish does not have a `--dry-run` flag yet. The easiest preview is a git diff after `--fix`:

```
mcpolish lint . --fix
git diff
```

Discard with `git restore .` if you do not like the result.

### 3. Apply safe fixes

```
mcpolish lint . --fix
```

You will see lines like:

```
applied 2 fix(es); re-run to verify
```

Re-run the lint to confirm the diagnostics are gone:

```
mcpolish lint .
```

### 4. Apply unsafe fixes

```
mcpolish lint . --unsafe-fix
```

Unsafe fixes may rename a tool. If other parts of your codebase reference the old tool name, they will not be updated. Search-and-replace yourself or restore from git.

## Example: MP001 safe fix

Before:

```python
@mcp.tool()
def thing(x: int) -> int:
    return x + 1
```

After `--fix`:

```python
@mcp.tool()
def thing(x: int) -> int:
    """TODO: describe what this tool does and when an agent should call it."""
    return x + 1
```

The autofix gives the next round of description rules something to work with. You still need to replace the TODO with real prose.

## Example: MP011 unsafe fix

Before (server is named `memnex`):

```python
@memnex.tool()
def memnex_search_memory(q: str):
    ...
```

After `--unsafe-fix`:

```python
@memnex.tool()
def search_memory(q: str):
    ...
```

If any other file calls `memnex_search_memory`, that call is now broken. The fix is intentionally local. Search the rest of your project for the old name after applying:

```
grep -rn memnex_search_memory src/
```

## Common variations

### Dry-run via stash

```
git stash
mcpolish lint . --fix
git diff --stat
git restore .
git stash pop
```

### Combining with format=json

You can still use `--fix` and `--format json` together. The JSON output reflects the state after the fixes were applied.

### Fix only one rule

mcpolish does not have a per-rule fix flag. Use `--select` to narrow scope:

```
mcpolish lint . --select MP001 --fix
```

This only runs MP001 and only applies its fix.

## Troubleshooting

**`applied 0 fix(es)` but I have fixable diagnostics.** Some fixers cannot derive a clean edit and back out. The diagnostic is still reported. You will need to fix it by hand. The CLI prints `"strategy could not derive a fix"` in the JSON output's reason field.

**The fix produced syntactically broken Python.** Open an issue with the input file and the diff. Mcpolish runs `libcst` to keep edits structured but edge cases exist.

**An unsafe rename broke callers in other files.** Expected. Run a project-wide grep for the old name and update.

## See also

- [Rules index](../rules/index.md)
- [CLI reference](cli-reference.md)
- [Configuration](configuration.md)
