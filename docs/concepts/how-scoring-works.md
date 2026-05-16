# How scoring works

> Who this page is for: anyone trying to understand or tune the 0-100 score.

## What you will learn

- The formula mcpolish uses to compute the score.
- How severity and category weights interact.
- How to tune the weights for your team.
- How to interpret the number.

## Background

The mcpolish score is a single integer from 0 (worst) to 100 (best). It is what `mcpolish score path/` prints and what the summary line of `mcpolish lint` ends with.

The score is a useful proxy in [CI](glossary.md#ci) gates, in dashboards, and as a [badge](glossary.md#badge) in your README. It is **not** a measure of correctness. It measures the quality of the descriptions and metadata mcpolish can see.

## The formula

mcpolish computes a per-diagnostic penalty and subtracts the total from 100.

```
for each diagnostic d:
    points = severity_points[d.severity]
    weight = normalised_category_weight[d.category]
    penalty += points * weight

score = 100 - (penalty / sqrt(tool_count)) * 8
```

Then it clamps the result between 0 and 100 and rounds to an integer.

### Severity points

| Severity | Points |
|---|---|
| error | 5.0 |
| warning | 2.0 |
| note | 0.5 |

### Category weights

The default weights:

| Category | Weight |
|---|---|
| schema | 0.20 |
| naming | 0.30 |
| description | 0.30 |
| consistency | 0.15 |
| security | 0.05 |

The weights are normalised so the total is 1.0 before they multiply the points. That means changing one weight changes the relative importance, not the absolute scale.

### Why divide by `sqrt(tool_count)`

A server with 50 tools has more surface area for findings than a server with 5 tools. Dividing by the square root of the tool count keeps big servers from being unfairly punished while still rewarding diligence on small servers. Square root is a middle ground between "divide by 1" (penalise both equally) and "divide by N" (a single bad tool barely shows).

## Examples

### Clean server

Zero diagnostics. Penalty is 0. Score is 100.

### A 5-tool server with one MP010 warning

```
diagnostic: MP010 [warn] in NAMING
points = 2.0
weight = 0.30 / 1.00 = 0.30 (normalised)
penalty = 2.0 * 0.30 = 0.60

score = 100 - (0.60 / sqrt(5)) * 8
      = 100 - (0.60 / 2.236) * 8
      = 100 - 2.147
      = 97.85 ~ 98
```

### A 7-tool server with 5 errors, 7 warnings, 14 notes (the smelly example)

Penalty is roughly 8.5 after weighting. Divided by sqrt(7) and multiplied by 8 gives about 25.7. Score 72.

## How to read the number

| Range | Reading |
|---|---|
| 90-100 | Ship it. Your descriptions are in good shape. |
| 75-89 | A few rough edges. Worth fixing for high-traffic servers. |
| 60-74 | Likely causes wrong-tool selections in production. |
| 0-59 | Many problems. Either descriptions are missing or the wrong rules are firing. Investigate. |

These ranges are guidance, not law.

## Tuning the weights

Open `pyproject.toml` and set the `score_weights` table:

```toml
[tool.mcpolish.score_weights]
schema = 0.10
naming = 0.20
description = 0.30
consistency = 0.20
security = 0.20
```

The weights do not need to sum to 1; mcpolish normalises them. The example above doubles the weight of security findings, which makes any MP040 or MP041 finding drop the score harder.

You can verify the change is applied:

```
mcpolish score path/ --json
```

## Score versus exit code

The score is informational. The CI gate is the exit code. By default mcpolish exits 1 on any error and 0 otherwise, regardless of the score. If you want the gate to depend on the score, do it in your CI script:

```
score=$(mcpolish score path/)
if [ "$score" -lt 80 ]; then
    echo "score $score below the gate of 80"
    exit 1
fi
```

See [CLI reference](../usage/cli-reference.md).

## Common variations

### Per-tool average

If you want the average penalty per tool rather than the absolute score, read the JSON output and divide:

```
mcpolish lint path/ --format json | jq '.score / .tools_found'
```

### Score over time

Run mcpolish on every commit and store the score in a time series. The bundled SVG badge is good for the latest score. For history, use the JSON output.

## See also

- [What mcpolish checks](what-mcpolish-checks.md)
- [Configuration](../usage/configuration.md)
- [Python API](../usage/python-api.md)
