# GitHub Actions

> Who this page is for: someone wiring mcpolish into a GitHub repository.

## What you will learn

- The cleanest way to run mcpolish on every pull request.
- How to upload results to GitHub Code Scanning so they show inline on the PR.
- How to post a score comment to the PR.

## Background

mcpolish ships a GitHub Action defined in `action.yml`. The action installs mcpolish, runs the lint, and exposes the score as an output. From there you choose what to do: fail the build, upload [SARIF](../concepts/glossary.md#sarif), or post a comment.

## Step by step

### 1. The basic case

Create `.github/workflows/mcpolish.yml`:

```yaml
name: mcpolish
on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: vtensor/mcpolish-action@v1
        with:
          path: .
          fail-on: error
```

This runs mcpolish on every push and every pull request. If any rule fires at error severity, the build fails.

### 2. Upload SARIF to Code Scanning

GitHub's security tab can display SARIF results inline on the PR:

```yaml
name: mcpolish
on: [push, pull_request]

permissions:
  security-events: write   # required for SARIF upload
  contents: read

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: vtensor/mcpolish-action@v1
        with:
          path: .
          report: sarif
          output: mcpolish.sarif
          fail-on: never     # let SARIF be the gate
      - uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: mcpolish.sarif
```

Now mcpolish findings appear in the security tab and inline on each PR. Use `fail-on: never` here so the SARIF upload always runs.

### 3. Post a score comment to the PR

```yaml
name: mcpolish
on: pull_request

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - id: lint
        uses: vtensor/mcpolish-action@v1
        with:
          path: .
          report: pr-comment
          output: comment.md
          fail-on: never
      - uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const body = fs.readFileSync('comment.md', 'utf8');
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body,
            });
```

A markdown table of diagnostics now shows up as a PR comment.

### 4. Matrix over multiple servers

If you have several MCP servers in one repo:

```yaml
name: mcpolish
on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        server: [mcp-weather, mcp-notes, mcp-memory]
    steps:
      - uses: actions/checkout@v4
      - uses: vtensor/mcpolish-action@v1
        with:
          path: services/${{ matrix.server }}
          fail-on: error
```

Each server lints in parallel.

### 5. Lock the mcpolish version

Pin the action to a tag:

```yaml
- uses: vtensor/mcpolish-action@v1.0.0
```

This avoids surprises when mcpolish ships a new release.

## Action inputs

| Input | Default | Notes |
|---|---|---|
| `path` | `.` | File or directory to lint. |
| `fail-on` | `error` | One of `error`, `warn`, `note`, `never`. |
| `report` | `tty` | Output format. |
| `select` | empty | Comma-separated rule IDs to keep. |
| `ignore` | empty | Comma-separated rule IDs to drop. |
| `output` | empty | File to write the report to. Empty means stdout. |

## Action output

| Output | Notes |
|---|---|
| `score` | The mcpolish score for this run. |

You can use it in later steps:

```yaml
- id: lint
  uses: vtensor/mcpolish-action@v1
  ...
- run: echo "Score was ${{ steps.lint.outputs.score }}"
```

## Common variations

### Run mcpolish only when Python files change

```yaml
on:
  pull_request:
    paths:
      - '**/*.py'
      - 'pyproject.toml'
```

### Block merges below a score threshold

```yaml
- id: lint
  uses: vtensor/mcpolish-action@v1
  with:
    fail-on: never
- run: |
    score=${{ steps.lint.outputs.score }}
    if [ "$score" -lt 80 ]; then
      echo "score $score below gate"
      exit 1
    fi
```

### Combine SARIF upload with strict gate

Run mcpolish twice in the same job, once for SARIF and once for the gate:

```yaml
- uses: vtensor/mcpolish-action@v1
  with: { report: sarif, output: mcpolish.sarif, fail-on: never }
- uses: github/codeql-action/upload-sarif@v3
  with: { sarif_file: mcpolish.sarif }
- uses: vtensor/mcpolish-action@v1
  with: { fail-on: error }
```

The second run is the gate. The first run produces the SARIF.

## Troubleshooting

**SARIF upload fails with "Code scanning not enabled".** Enable Code Scanning in the repo's Settings -> Code security and analysis. Some plans require this be turned on.

**The PR comment job posts comments forever.** Use `actions/github-script` to delete the previous comment from the same workflow run before posting a new one. The pattern is well documented in the GitHub Actions docs.

**Action fails with "mcpolish: command not found".** The Action installs mcpolish from PyPI. Network issues during install reproduce intermittently. Rerun the job.

## See also

- [GitLab CI](ci-gitlab.md)
- [Pre-commit setup](pre-commit-setup.md)
- [Output formats](../usage/output-formats.md)
