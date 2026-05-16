# Existing project

> Who this page is for: someone adopting mcpolish on a codebase that already has many MCP tools.

## What you will learn

- How to do the first run without breaking your team.
- How to triage the initial flood of diagnostics.
- How to introduce mcpolish to CI without forcing a fix-everything-at-once sprint.

## Background

If you have 50 tools spread across a real codebase, the first `mcpolish lint .` will almost certainly produce a lot of diagnostics. That is expected. mcpolish encodes 23 specific opinions; some of yours probably differ. The goal of adoption is not to chase every diagnostic. It is to get a baseline and stop the bleeding.

## Step by step

### 1. First run, no gating

```
pip install mcpolish
mcpolish lint . --fail-on never > first-run.txt
```

`--fail-on never` keeps the command from exiting non-zero. You want the data, not a build failure.

### 2. Read the summary

The last line tells you the score and the counts.

```
Found 87 issues (12 errors, 31 warnings, 44 notes). score: 64/100
```

Three numbers to write down: error count, warning count, total score.

### 3. Categorise the diagnostics

```
mcpolish lint . --format json --fail-on never | jq '.diagnostics[].rule_id' | sort | uniq -c | sort -rn
```

Output looks like:

```
  18 MP020
  12 MP023
  10 MP010
   7 MP013
   ...
```

Now you know which rules dominate.

### 4. Decide which rules to keep on

Look at your top three rules. Are they fair? Are they fixable in a week?

Common decisions:

- **MP013 (cross-server collision)**: if your servers are internal, the cross-server check may be noise. Consider `ignore = ["MP013"]`.
- **MP022 (missing example)**: useful long-term but may flood your initial report. Consider disabling for the first quarter.
- **MP024 (jargon density)**: useful if you have a lot of acronyms. Disable if your team's domain is genuinely acronym-heavy.

Edit your `pyproject.toml`:

```toml
[tool.mcpolish]
ignore = ["MP013", "MP022"]
```

Re-lint. The number drops.

### 5. Use `--fail-on warn` initially, raise the bar over time

For the first month, ignore notes:

```
mcpolish lint . --fail-on warn
```

For the second month, treat everything as fail-on:

```
mcpolish lint . --fail-on note
```

### 6. Add to CI as informational at first

In GitHub Actions:

```yaml
- uses: vtensor/mcpolish-action@v1
  continue-on-error: true   # do not block merges yet
  with:
    fail-on: error
```

You get a score badge on every PR without blocking anyone. Watch for two weeks. Then flip `continue-on-error: false` once the team is on board.

### 7. Bring the worst rule down to zero

Pick one rule. Get its count to zero. Then enable it in `--fail-on error` mode and add a CI gate so it never comes back. Move to the next rule.

This is the same approach big companies take with security debt: a budget for the past, a hard line going forward.

## What to expect numerically

For a typical 50-tool codebase that has never been linted:

- Initial score: somewhere between 40 and 80.
- After fixing MP001, MP002, MP003 (schema): score climbs 10 to 15 points.
- After fixing MP010, MP020, MP023 (description quality): another 10 to 20.
- Reaching 90+ usually takes a full quarter of part-time work.

The score does not have to be 100 to be useful. Pick a target that keeps shipping fast.

## Common variations

### Adopting mcpolish on a contractor codebase

Run mcpolish during code review for new tools only. Older tools are excluded by passing the path of only the new files:

```
mcpolish lint $(git diff --name-only main | grep "\.py$")
```

### Tracking the score over time

```
mcpolish score . >> score-history.txt
```

A simple file is enough to see whether the trend is up or down.

### Sharing the report with your team

Generate a PR comment Markdown body:

```
mcpolish lint . --format pr-comment > review.md
```

Paste it into the PR or open a doc.

## Troubleshooting

**The score jumps around between runs.** Three causes:

- LLM-gated rules (only with `--llm`): the model is not perfectly deterministic.
- A new release of mcpolish: rule severities can change. Pin the version.
- Cross-server snapshot refresh: a quarterly bundled update may add or remove collisions.

**MP033 keeps firing on tools that legitimately do similar things.** Slightly differentiate the descriptions. A tool that lists open tickets and a tool that lists closed tickets should mention "open" and "closed" in their descriptions.

## See also

- [New project](new-project.md)
- [Customising rules](customizing-rules.md)
- [Silencing false positives](silencing-false-positives.md)
