# Pre-commit setup

> Who this page is for: someone who wants mcpolish to run automatically before each git commit.

## What you will learn

- How to install the pre-commit framework.
- How to add the mcpolish hook.
- How to skip the hook for one commit when necessary.

## Background

[pre-commit](../concepts/glossary.md#pre-commit) is a popular framework that runs checks on staged files just before `git commit` creates the commit. If a check fails, the commit is blocked. Catching mcpolish problems at commit time is the cheapest possible feedback loop: you see the problem before you push, before [CI](../concepts/glossary.md#ci), before anyone else sees it.

mcpolish ships a `.pre-commit-hooks.yaml` definition in the repo, so adopting it is two lines of config.

## Step by step

### 1. Install pre-commit

```
pip install pre-commit
```

Or with brew on macOS:

```
brew install pre-commit
```

### 2. Add a `.pre-commit-config.yaml`

In the root of your project:

```yaml
repos:
  - repo: https://github.com/vtensor/mcpolish
    rev: v0.1.0
    hooks:
      - id: mcpolish
```

The `rev` line pins the mcpolish version. Use a real tag, not `main`.

### 3. Install the git hook

```
pre-commit install
```

This writes `.git/hooks/pre-commit` to invoke pre-commit on every commit.

### 4. Try a commit

Make a change to a Python file. Stage it. Commit:

```
git add .
git commit -m "test"
```

You should see something like:

```
mcpolish.....................................Passed
```

If mcpolish finds errors, the output prints them and the commit is aborted.

### 5. Run on all files (not just changed)

The first time you adopt a linter, you usually want to lint everything once:

```
pre-commit run --all-files
```

This runs mcpolish against every file in the repo, not only the staged ones.

## Skipping the hook

For one commit:

```
SKIP=mcpolish git commit -m "wip"
```

For one commit, everything:

```
git commit -m "wip" --no-verify
```

The `--no-verify` flag bypasses all hooks. Use sparingly.

## What gets linted

The pre-commit hook runs mcpolish against the files staged for commit. mcpolish handles individual file paths and a directory the same way: it walks each.

If you only changed a helper file with no MCP tools, mcpolish runs but finds nothing to complain about; the commit passes quickly.

## Common variations

### Pass custom arguments

```yaml
- repo: https://github.com/vtensor/mcpolish
  rev: v0.1.0
  hooks:
    - id: mcpolish
      args: ["--fail-on", "warn"]
```

This makes the hook strict.

### Run only on certain files

```yaml
- repo: https://github.com/vtensor/mcpolish
  rev: v0.1.0
  hooks:
    - id: mcpolish
      files: ^src/.*\.py$
```

This only runs the hook on Python files inside `src/`.

### Combine with other linters

mcpolish plays well with Ruff, Black, isort, and mypy:

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.4.0
    hooks:
      - id: ruff
      - id: ruff-format

  - repo: https://github.com/vtensor/mcpolish
    rev: v0.1.0
    hooks:
      - id: mcpolish
```

Order does not matter; pre-commit runs hooks independently.

## Troubleshooting

**Hook fails with `mcpolish: command not found`.** pre-commit runs hooks in an isolated environment. It manages the install itself. If you see this error, your pre-commit cache may be stale:

```
pre-commit clean
pre-commit run --all-files
```

**Hook is slow on big commits.** pre-commit re-runs on every commit. For a 1,000-file commit this can add seconds. Two options:

- Use `--all-files` only for the first run; let normal commits lint only staged files.
- Move mcpolish to a [GitHub Action](ci-github.md) and skip the pre-commit hook entirely.

**Hook conflicts with a different mcpolish version installed globally.** The pre-commit version is the one that wins. Pin the same tag in both places to keep them in sync.

## See also

- [GitHub Actions](ci-github.md)
- [GitLab CI](ci-gitlab.md)
- [CLI reference](../usage/cli-reference.md)
