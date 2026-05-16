# Output formats

> Who this page is for: anyone routing mcpolish output to a script, dashboard, or [CI](../concepts/glossary.md#ci) tool.

## What you will learn

- The five output formats mcpolish supports.
- The exact shape of each format.
- When to pick which one.

## Background

`mcpolish lint` produces the same data in five different shapes. You select the shape with `--format`. The data is identical; only the wire format differs.

| Format | Flag | When to use |
|---|---|---|
| Terminal (default) | `--format tty` | Reading the output yourself. |
| JSON | `--format json` | Scripts, dashboards, parsing in code. |
| SARIF 2.1.0 | `--format sarif` | GitHub Code Scanning, GitLab security panels. |
| GitLab Code Quality | `--format gitlab` | GitLab merge request widget. |
| PR comment Markdown | `--format pr-comment` | Posting as a comment on a pull request. |

## TTY (default)

What you saw in [Understanding output](../getting-started/understanding-output.md). Rich-rendered, coloured, with hint and docs lines per diagnostic. Pipes drop the colour codes automatically.

## JSON

A single JSON document. Stable schema, versioned, published at `https://mcpolish.dev/schemas/report.v1.json`.

```
mcpolish lint examples/clean_server.py --format json
```

Output shape:

```json
{
  "schema": "https://mcpolish.dev/schemas/report.v1.json",
  "version": "0.1.0",
  "server": "notes",
  "scanned_at": "2026-05-16T10:30:00+00:00",
  "files_scanned": 1,
  "tools_found": 3,
  "score": 100,
  "diagnostics": []
}
```

When there are diagnostics, each one has this shape:

```json
{
  "rule_id": "MP010",
  "rule_name": "generic-tool-name",
  "category": "naming",
  "severity": "warn",
  "message": "tool name `search` is too generic",
  "file": "server.py",
  "line": 42,
  "col": 5,
  "tool_name": "search",
  "docs_url": "https://mcpolish.dev/rules/MP010",
  "hint": "consider a more specific name",
  "fix": null
}
```

The `fix` field is `null` when no autofix is offered, or `{"description": "...", "safe": true}` when one is available.

## SARIF 2.1.0

Standard format for static analysis results. GitHub and GitLab can ingest it and show findings inline on pull requests.

```
mcpolish lint . --format sarif > sarif.json
```

Output is the standard SARIF schema. Each rule is listed in `runs[0].tool.driver.rules`. Each diagnostic is in `runs[0].results`. Severity is mapped:

| mcpolish severity | SARIF level |
|---|---|
| error | `error` |
| warning | `warning` |
| note | `note` |

To upload to GitHub Code Scanning, use the `github/codeql-action/upload-sarif` action. See [GitHub Actions setup](../scenarios/ci-github.md).

## GitLab Code Quality

GitLab's merge request widget displays Code Quality findings inline. mcpolish emits the format directly:

```
mcpolish lint . --format gitlab > codequality.json
```

Output is a JSON array. Each item has:

```json
{
  "description": "[MP010] tool name `search` is too generic",
  "check_name": "MP010",
  "fingerprint": "<sha1 of rule_id|file|line|tool>",
  "severity": "minor",
  "location": {
    "path": "server.py",
    "lines": {"begin": 42}
  }
}
```

Severity mapping:

| mcpolish severity | GitLab severity |
|---|---|
| error | `major` |
| warning | `minor` |
| note | `info` |

See [GitLab CI setup](../scenarios/ci-gitlab.md).

## PR comment Markdown

A Markdown body suitable for posting as a comment on a GitHub or GitLab pull request.

```
mcpolish lint . --format pr-comment
```

Sample output:

```markdown
### mcpolish: score **78/100**

Scanned **8** tools in **1** file.

<details><summary>Diagnostics</summary>

| Severity | Rule | File:Line | Message |
|---|---|---|---|
| warning | [MP010](https://mcpolish.dev/rules/MP010) | `server.py:42` | tool name `search` is too generic |
| error | [MP011](https://mcpolish.dev/rules/MP011) | `server.py:42` | tool `memnex_search_memory` redundantly starts with the server namespace `memnex` |
</details>
```

A bot like `actions/github-script` can take this output and post it to the PR. See [GitHub Actions setup](../scenarios/ci-github.md) for an example.

## Common variations

### Saving JSON to a file

```
mcpolish lint . --format json --fail-on never > report.json
```

Use `--fail-on never` to keep mcpolish from exiting 1 when you only want the data.

### Combining outputs

You can run mcpolish twice with different formats:

```
mcpolish lint . --format tty
mcpolish lint . --format json --fail-on never > report.json
```

Two parses, two prints, but the cost is small (well under a second for typical projects).

### Custom output formats

mcpolish v1 does not ship a plugin system, so you cannot register a new reporter from outside. The reporter set is fixed. If you need a different shape, parse `--format json` in your own script.

## Troubleshooting

**SARIF output is rejected by GitHub.** GitHub validates SARIF strictly. Confirm the file parses as JSON first (`python -m json.tool sarif.json`), then check that the path in `artifactLocation.uri` is relative to the repo root.

**Empty PR comment shows up.** mcpolish writes the comment to stdout. Your CI step needs to capture it and pass it to the GitHub comment API. See the example in [GitHub Actions setup](../scenarios/ci-github.md).

## See also

- [CLI reference](cli-reference.md)
- [GitHub Actions](../scenarios/ci-github.md)
- [GitLab CI](../scenarios/ci-gitlab.md)
