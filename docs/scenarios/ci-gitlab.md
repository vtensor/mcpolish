# GitLab CI

> Who this page is for: someone wiring mcpolish into a GitLab project.

## What you will learn

- How to add mcpolish to `.gitlab-ci.yml`.
- How to feed mcpolish's GitLab format into the merge request widget.
- How to set a score gate.

## Background

GitLab merge requests have two ways to show static analysis results:

1. **Code Quality**: shows findings inline on the diff and on the MR widget. mcpolish emits this format directly with `--format gitlab`.
2. **SARIF**: GitLab's security panel ingests it.

This page covers Code Quality, which is the cleaner integration.

## Step by step

### 1. Basic job

`.gitlab-ci.yml`:

```yaml
mcpolish:
  image: python:3.12-slim
  stage: test
  script:
    - pip install mcpolish
    - mcpolish lint .
```

If mcpolish finds errors, the job exits 1 and the pipeline fails.

### 2. Emit GitLab Code Quality format

```yaml
mcpolish:
  image: python:3.12-slim
  stage: test
  script:
    - pip install mcpolish
    - mcpolish lint . --format gitlab --fail-on never > codequality.json
    - mcpolish lint . --fail-on error
  artifacts:
    reports:
      codequality: codequality.json
    paths:
      - codequality.json
    when: always
```

Two lints: one emits the report, one is the gate. Both read the same source, so the second run is mostly cached file reads and is fast.

After this lands, MRs will show mcpolish findings inline on the diff:

```
[MP010] tool name `search` is too generic
```

### 3. Score gate

If you prefer to gate on the score rather than on errors:

```yaml
mcpolish:
  image: python:3.12-slim
  stage: test
  script:
    - pip install mcpolish
    - mcpolish lint . --format gitlab --fail-on never > codequality.json
    - |
      score=$(mcpolish score .)
      echo "score=$score"
      if [ "$score" -lt 80 ]; then
        echo "score below 80; failing"
        exit 1
      fi
  artifacts:
    reports:
      codequality: codequality.json
```

### 4. Pin the version

```yaml
script:
  - pip install "mcpolish==0.1.0"
```

Avoids surprises when mcpolish releases a new version.

### 5. Cache the install

GitLab caches pip downloads if you tell it to:

```yaml
mcpolish:
  cache:
    paths:
      - .cache/pip/
  variables:
    PIP_CACHE_DIR: $CI_PROJECT_DIR/.cache/pip
  ...
```

Speeds up repeat runs.

## What the Code Quality format looks like

GitLab expects an array of findings. mcpolish emits:

```json
[
  {
    "description": "[MP010] tool name `search` is too generic",
    "check_name": "MP010",
    "fingerprint": "9b1c5...",
    "severity": "minor",
    "location": {
      "path": "server.py",
      "lines": {"begin": 42}
    }
  }
]
```

| mcpolish severity | GitLab severity |
|---|---|
| error | major |
| warning | minor |
| note | info |

GitLab uses the `fingerprint` to track findings across commits, so it can mark a finding as "new in this MR" or "carried over from main".

## Common variations

### Run only when MCP files change

```yaml
mcpolish:
  rules:
    - changes:
        - '**/*.py'
        - 'pyproject.toml'
```

### Multiple servers in one repo

```yaml
.mcpolish_template: &mcpolish_template
  image: python:3.12-slim
  stage: test
  before_script:
    - pip install mcpolish
  artifacts:
    reports:
      codequality: codequality.json

mcpolish_weather:
  <<: *mcpolish_template
  script:
    - mcpolish lint services/mcp-weather --format gitlab --fail-on never > codequality.json
    - mcpolish lint services/mcp-weather --fail-on error

mcpolish_notes:
  <<: *mcpolish_template
  script:
    - mcpolish lint services/mcp-notes --format gitlab --fail-on never > codequality.json
    - mcpolish lint services/mcp-notes --fail-on error
```

### SARIF instead of Code Quality

```yaml
script:
  - pip install mcpolish
  - mcpolish lint . --format sarif --fail-on never > sarif.json
artifacts:
  reports:
    sast: sarif.json
```

GitLab ingests SARIF as SAST findings.

## Troubleshooting

**Code Quality widget shows no findings even though mcpolish output is present.** GitLab silently rejects bad JSON. Validate the file:

```
python -m json.tool codequality.json
```

If the file is empty, your lint exited non-zero before redirecting. Add `--fail-on never` to the report-emitting command.

**Pipeline succeeds when it should fail.** GitLab's `codequality` report does not affect job status by default. The gate must be a separate command:

```yaml
script:
  - mcpolish lint . --format gitlab --fail-on never > codequality.json
  - mcpolish lint . --fail-on error
```

The second line is the gate.

## See also

- [GitHub Actions](ci-github.md)
- [Pre-commit setup](pre-commit-setup.md)
- [Output formats](../usage/output-formats.md)
