<p align="center">
  <h1 align="center">mcpolish</h1>
</p>

<h3 align="center">
A static linter for Model Context Protocol servers
</h3>

<p align="center">
Catch vague, colliding, or misleading tool descriptions before agents pick the wrong tool.
</p>

<p align="center">
| <a href="https://github.com/vtensor/mcpolish/blob/main/docs/index.md"><b>Documentation</b></a> |
<a href="https://github.com/vtensor/mcpolish/blob/main/docs/getting-started/quickstart.md"><b>Quickstart</b></a> |
<a href="https://github.com/vtensor/mcpolish/blob/main/docs/rules/index.md"><b>Rules</b></a> |
<a href="https://github.com/vtensor/mcpolish/blob/main/docs/concepts/glossary.md"><b>Glossary</b></a> |
<a href="https://github.com/vtensor/mcpolish/blob/main/MCPOLISH.md"><b>Design doc</b></a> |
<a href="https://github.com/vtensor/mcpolish/blob/main/VERIFICATION.md"><b>Test report</b></a> |
</p>

<p align="center">
  <a href="https://pypi.org/project/mcpolish/"><img src="https://img.shields.io/badge/pypi-mcpolish-blue.svg" alt="pypi"></a>
  <a href="https://pypi.org/project/mcpolish/"><img src="https://img.shields.io/badge/python-3.11%2B-blue.svg" alt="python"></a>
  <a href="https://github.com/vtensor/mcpolish/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-Apache--2.0-lightgrey.svg" alt="license"></a>
  <a href="https://github.com/vtensor/mcpolish/blob/main/docs/rules/index.md"><img src="https://img.shields.io/badge/rules-23-brightgreen.svg" alt="rules"></a>
  <a href="https://github.com/vtensor/mcpolish/blob/main/VERIFICATION.md"><img src="https://img.shields.io/badge/tests-132%20passing-brightgreen.svg" alt="tests"></a>
</p>

---

## About

When you build an MCP server, every tool you expose carries an English description. The AI agent (Claude, GPT, Gemini, Cursor, and so on) reads that description to decide which tool to call. If the description is vague, generic, or misleading, the agent picks the wrong tool.

In tests across 10,831 public MCP servers (Wang et al., February 2026), bad descriptions caused agents to pick the wrong tool **52 percentage points** more often. That paper catalogued 18 specific problems. mcpolish detects 23 of them, before you ship.

mcpolish is to MCP server quality what ESLint is to JavaScript style: a fast static check with stable rule IDs that runs in your editor, your pre-commit hook, and your CI pipeline.

mcpolish is fast with:

- Sub-second scans on a typical MCP server. Verified 6 ms on a 3-tool file, 67 ms on a 40-file project.
- One parse, twenty-three checks. mcpolish reads each file once into an intermediate representation, then every rule runs against the same in-memory view.
- Zero external calls. The default engine runs offline.

mcpolish is flexible with:

- Five output formats: terminal, JSON, SARIF, GitLab Code Quality, GitHub PR-comment Markdown.
- Per-rule configuration in `pyproject.toml`. Whitelist names, raise thresholds, retune category weights.
- Two-tier auto-fix: safe fixes apply only deterministic edits; risky renames need `--unsafe-fix`.
- Three optional LLM-judged rules for the cases static heuristics miss. Off by default.

mcpolish covers:

- Schema problems (missing descriptions, broken JSON Schema, missing `required` arrays).
- Naming problems (generic names, redundant namespace prefixes, verb inconsistency, cross-server collisions, mixed casing).
- Description quality (too short, too long, no examples, no trigger conditions, jargon density, marketing qualifiers, ambiguity).
- Consistency between schema and description (param type mismatch, undocumented side effects, duplicate descriptions).
- Security smells (zero-width prompt injection, operator-style instructions baked into descriptions).

See the [rules index](https://github.com/vtensor/mcpolish/blob/main/docs/rules/index.md) for the full table.

## Quickstart

```bash
pip install mcpolish

mcpolish lint .
mcpolish score . --json
mcpolish explain MP010
```

Sample run on a real server file:

```bash
$ mcpolish lint weather_server.py
mcpolish 0.1.0
server: weather  (1 tool in 1 file)

weather_server.py:6:1: MP010 [W] tool name `get` is too generic
   -> consider a more specific name like `get_<noun>` or `<verb>_<thing>`
   -> https://mcpolish.dev/rules/MP010
weather_server.py:6:1: MP020 [W] tool `get` description is 12 chars (minimum 50)
   -> state what the tool does and when an agent should pick it
   -> https://mcpolish.dev/rules/MP020

Found 2 issues (0 errors, 2 warnings, 0 notes). score: 86/100
```

## Documentation

The full documentation lives under [docs/](https://github.com/vtensor/mcpolish/blob/main/docs/index.md). Common entry points:

| If you want to... | Go here |
|---|---|
| Run mcpolish for the first time | [Quickstart](https://github.com/vtensor/mcpolish/blob/main/docs/getting-started/quickstart.md) |
| Understand the diagnostic lines | [Understanding the output](https://github.com/vtensor/mcpolish/blob/main/docs/getting-started/understanding-output.md) |
| Wire mcpolish into CI | [GitHub Actions](https://github.com/vtensor/mcpolish/blob/main/docs/scenarios/ci-github.md), [GitLab CI](https://github.com/vtensor/mcpolish/blob/main/docs/scenarios/ci-gitlab.md), [pre-commit](https://github.com/vtensor/mcpolish/blob/main/docs/scenarios/pre-commit-setup.md) |
| Lint a multi-file project | [Multi-file server](https://github.com/vtensor/mcpolish/blob/main/docs/scenarios/multi-file-server.md) |
| Customise which rules run | [Customising rules](https://github.com/vtensor/mcpolish/blob/main/docs/scenarios/customizing-rules.md) |
| Look up one specific rule | [Rules index](https://github.com/vtensor/mcpolish/blob/main/docs/rules/index.md) |
| Find what a technical word means | [Glossary](https://github.com/vtensor/mcpolish/blob/main/docs/concepts/glossary.md) |
| Use the Python API | [Python API](https://github.com/vtensor/mcpolish/blob/main/docs/usage/python-api.md) |

## The 23 rules

Each rule has a stable identifier like `MP010` and a documentation page.

| Category | Rules |
|---|---|
| Schema | MP001, MP002, MP003, MP004, MP005 |
| Naming | MP010, MP011, MP012, MP013, MP014 |
| Description | MP020, MP021, MP022, MP023, MP024, MP025, MP026 (LLM) |
| Consistency | MP030, MP031 (LLM), MP032 (LLM), MP033 |
| Security | MP040, MP041 |

Print the full list in your terminal:

```bash
mcpolish explain          # one line per rule
mcpolish explain MP010    # details for one rule
```

See the [rules index](https://github.com/vtensor/mcpolish/blob/main/docs/rules/index.md) for the categorised table and links to every rule's detail page.

## Configuration

Settings go in `pyproject.toml`:

```toml
[tool.mcpolish]
target-version = "2025-11"
select = ["MP001-MP041"]
ignore = ["MP025"]
registry = "official"

[tool.mcpolish.MP010]
allow = ["search"]

[tool.mcpolish.MP020]
min_chars = 80
```

See [Configuration](https://github.com/vtensor/mcpolish/blob/main/docs/usage/configuration.md) for every knob.

## Integrations

### GitHub Actions

```yaml
- uses: vtensor/mcpolish-action@v1
  with:
    fail-on: error
    report: sarif
```

### GitLab CI

```yaml
mcpolish:
  image: python:3.12
  script:
    - pip install mcpolish
    - mcpolish lint . --format gitlab > codequality.json
  artifacts:
    reports:
      codequality: codequality.json
```

### Pre-commit hook

```yaml
repos:
  - repo: https://github.com/vtensor/mcpolish
    rev: v0.1.0
    hooks:
      - id: mcpolish
```

## CLI cheat sheet

```
mcpolish lint .                  # lint everything reachable
  --select MP010                 # keep only specific rules (range syntax: MP001-MP005)
  --ignore MP020                 # drop specific rules
  --llm openai:gpt-4o            # enable the 3 LLM-judged rules
  --registry official            # cross-server collision check (default)
  --registry off                 # local rules only
  --fix                          # apply safe autofixes
  --unsafe-fix                   # apply risky autofixes (renames)
  --format tty|json|sarif|gitlab|pr-comment
  --fail-on error|warn|note|never

mcpolish score . --json --badge badge.svg
mcpolish explain MP010
mcpolish doctor
```

Full reference: [CLI reference](https://github.com/vtensor/mcpolish/blob/main/docs/usage/cli-reference.md).

## Python API

```python
import mcpolish

report = mcpolish.lint("server.py")
print(report.score)              # 0 to 100

for d in report.diagnostics:
    print(d.rule_id, d.location(), d.message)
```

See [Python API](https://github.com/vtensor/mcpolish/blob/main/docs/usage/python-api.md).

## Why this exists

- Wang et al., [arXiv:2602.18914](https://arxiv.org/abs/2602.18914), February 2026: 10,831 public MCP servers analysed, 18 description smells catalogued, controlled mutation experiment proving each smell causes wrong-tool selection (p < 0.001).
- Li et al., [arXiv:2602.03580](https://arxiv.org/abs/2602.03580), February 2026: static analysis of 10,240 servers; 3,449 with parameter type mismatches, 1,326 with undocumented side effects.
- Snyk acquired Invariant Labs (mcp-scan) in June 2025. Agentic-AI security is now a real budget line.
- MCP was donated to the Linux Foundation's Agentic AI Foundation in December 2025. OpenAI, AWS, Google, Microsoft, Cloudflare, and Bloomberg are members.

The ecosystem grew to over 23,000 servers on Glama, 20,000 on MCP.so, and 12,000 on Smithery with no quality gate. mcpolish is that gate.

## Project status

| | |
|---|---|
| Version | 0.1.0 |
| Python | 3.11 and newer |
| Rules shipped | 23 |
| Tests | 132 passing |
| Performance | 6 to 67 ms on real fixtures |
| License | Apache 2.0 |
| Status | Beta. The 23 rule IDs are stable forever. |

See [MCPOLISH.md](https://github.com/vtensor/mcpolish/blob/main/MCPOLISH.md) for the full design document and [VERIFICATION.md](https://github.com/vtensor/mcpolish/blob/main/VERIFICATION.md) for the end-to-end verification report.

## Contributing

Contributions are welcome. Bug reports, rule proposals, and documentation improvements are equally valued.

See [CONTRIBUTING.md](https://github.com/vtensor/mcpolish/blob/main/CONTRIBUTING.md) for the developer setup and the workflow. See [CODE_OF_CONDUCT.md](https://github.com/vtensor/mcpolish/blob/main/CODE_OF_CONDUCT.md) for community expectations. See [SECURITY.md](https://github.com/vtensor/mcpolish/blob/main/SECURITY.md) to report a security issue privately.

## License

Apache 2.0. See [LICENSE](https://github.com/vtensor/mcpolish/blob/main/LICENSE).
