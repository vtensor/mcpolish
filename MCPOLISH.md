# MCPOLISH: Design Doc

| | |
|---|---|
| **Status** | Draft v1 |
| **Author** | Vikram Dev |
| **Date** | 2026-05-16 |
| **Reviewers** | TBD |
| **Repository** | `github.com/vtensor/mcpolish` (planned) |
| **Implementation target** | 20 May 2026 |

---

## 1. TL;DR

MCPolish is a fast static linter for MCP servers: like ESLint, but specialised for the Model Context Protocol's failure mode: **vague, colliding, or misleading tool descriptions that cause LLM agents to pick the wrong tool**.

Wang et al. (NTU/UCLA, Feb 2026, [arXiv:2602.18914](https://arxiv.org/abs/2602.18914)) analysed **10,831 MCP servers** and found 73% have repeated tool names, 3,093 have no return-value description, and bad descriptions degrade tool-selection accuracy by **52 percentage points** in head-to-head choice (72% → 20% [1]). MCPolish ships **24 named lint rules** mapped directly to that paper's smell taxonomy, plus naming-collision detection and schema-vs-description consistency checks.

OSS-free Python package runs sub-second on any local repo, ships as a pre-commit hook and GitHub Action. SaaS provides registry-wide scanning, cross-server collision data, and quality badges sold to MCP marketplaces (Smithery, Glama, PulseMCP) and enterprise teams running internal MCP fleets.

The one-line pitch: **the MCP ecosystem grew to 10,000+ servers with no quality gate. MCPolish is that gate.**

---

## 2. Problem

### 2.1 The state of the MCP ecosystem in 2026

- **23K servers on Glama**, ~20K on MCP.so, ~12K on PulseMCP, ~7K on Smithery, plus the official Anthropic registry [2][3][4].
- **97M monthly SDK downloads** combined across `@modelcontextprotocol/sdk` and Python `mcp` [5].
- **Adoption is universal across major hosts**: Anthropic (donor), OpenAI (announced full MCP support March 2025, "we are excited to add support across our products": Altman [6]), Google DeepMind, Cursor, Windsurf, Cline, Continue.dev, Zed, Replit, VS Code Copilot, Claude Code, Claude Desktop.

The ecosystem grew faster than its quality bar.

### 2.2 The empirical problem

Wang et al. (2026) catalogued **18 description smells across 4 dimensions** in 10,831 servers, then proved each one causes tool-selection regressions via a controlled mutation experiment [1]:

| Findings | Count / Effect |
|---|---|
| Servers with repeated tool names | 7,894 (73%) |
| Servers with wrong param meaning | 3,449 |
| Servers with no return-value description | 3,093 |
| Servers cluttered with irrelevant details | 2,904 |
| Servers with no parameter descriptions | 1,285 |
| Functionality-class smells effect | +11.6pp wrong-tool error rate (p<0.001) |
| Accuracy-class smells effect | +8.8pp wrong-tool error rate (p<0.001) |
| Clean vs smelly head-to-head selection | 72% vs 20% |

A companion paper (Zhihao Li et al. [arXiv:2602.03580](https://arxiv.org/abs/2602.03580)) extends with static analysis over 10,240 servers and finds ~13% have substantial mismatches between description and code behaviour, including undocumented privileged operations [7].

### 2.3 Why the existing tools don't solve it

| Tool | What it does | Why it doesn't solve description-quality linting |
|---|---|---|
| **MCP Inspector** (official) | Web UI for manual debugging | Manual only. Not CI. No quality rules. Had RCE CVE-2025-49596 [8]. |
| **mcp-scan** (Snyk-acquired) | Security: prompt injection, tool poisoning, rug pulls, tool shadowing | Detects *malicious* descriptions, not *bad* ones. |
| **MCPWatch** | OWASP MCP Top 10 + letter grade | Security grading, no DX/quality. Glama reports only 20.5% of 20,652 servers earn an A [3]. |
| **Smithery quality score** | 0-100 grade driving registry rank | Closed criteria. Registry-bound. Not a CLI. Not actionable per-rule. |
| **Glama quality score** | 70% tool-quality × 30% server-coherence | Registry-side only. Post-publish. Closed methodology. |
| **ToolRank** ("Lighthouse for MCP") | OSS scorer, 4 buckets, PR-comment Action | Closest competitor. Solo dev. 4 rules, no rule taxonomy. No commercial tier. Scores JSON only, not server source. |
| **Anthropic / Python MCP SDKs** | Runtime JSON-Schema validation | Validates types, not English. |

None of these check:
- Naming collisions **across servers** (the 73% problem).
- Redundant prefixes (`memnex_search_memory` where the server is already namespaced `memnex`).
- Schema-vs-description mismatches (the Zhihao Li paper's contribution).
- Description-quality smells with named, citable rule IDs the way ESLint does.

That is the wedge.

### 2.4 Why now

- The arXiv paper is **two months old**. Its 18-smell taxonomy is a defensible v1 ruleset and nobody has shipped a linter built on it.
- **Snyk acquired Invariant Labs (mcp-scan)** in June 2025 [9]. Agentic-AI security is a budget line. MCP tooling has real M&A.
- **MCP donated to Linux Foundation's Agentic AI Foundation (AAIF)** Dec 2025: OpenAI, AWS, Google, Microsoft, Cloudflare, Bloomberg are members [10]. The ecosystem now has institutional money behind it.

---

## 3. Goals and Non-Goals

### 3.1 Goals (v1)

1. **24 first-party lint rules** (full taxonomy below), every one mapped to a paper or known failure mode.
2. **Sub-second scan** on a typical MCP server (1-20 tools). Zero LLM calls for core engine.
3. **`--llm` flag for 4 semantic rules** (ambiguity, schema-vs-description drift, undocumented side effects, param-meaning mismatch). Optional, gated by API key.
4. **Cross-server collision check** via a pinned registry snapshot (refreshed weekly), so `mcpolish lint` flags `your_tool_name` colliding with the top-1000 MCP servers' tools.
5. **Five integration shapes**: PyPI library, CLI, pre-commit hook, GitHub Action, GitLab CI template.
6. **Stable rule IDs**: `MP001`-`MP041` and beyond. Once shipped, never renumbered. (Ruff and Hadolint enforce this; users rely on it.)
7. **Safe `--fix`** for ~8 rules where the fix is unambiguous (e.g. add missing description placeholder).
8. **SaaS dashboard** for registry-wide scoring (Smithery/Glama partnership shape) and white-label badges.

### 3.2 Non-goals (v1)

- We don't write MCP servers for you. (`mcp-server-generator` is a different product.)
- We don't run runtime checks. (mcp-scan does that for security; we're static.)
- We don't host servers. (Smithery / Cloudflare Workers do that.)
- We don't ship a host or client. (Anthropic, OpenAI, Cursor, etc. do that.)
- We don't grade *implementations* beyond what's visible in the registration code. Deep code review is out of scope.

### 3.3 Explicit anti-features

- **No plugin system in v1.** Ruff's call. 24 first-party rules in one binary. Plugins are a community-debt sink before product-market fit.
- **No LLM dependency in the core engine.** Determinism, speed, and offline-first are core promises. LLM checks are an explicit opt-in.
- **No frontend framework in OSS.** CLI + JSON output. Dashboards are the SaaS product.

---

## 4. Personas and ICP

| Persona | Pain | Lever MCPolish pulls | Buys? |
|---|---|---|---|
| **MCP server author** (open-source dev) | Server gets low Smithery score, no idea why | CLI + pre-commit + actionable rule IDs | OSS user. Top of funnel. |
| **MCP marketplace** (Smithery, Glama, PulseMCP, MCP.so) | Need quality bar, existing scores are opaque | White-label registry-wide scanning + badges + dashboards | **$30K-$150K/yr enterprise license** |
| **Enterprise platform team** running internal MCP fleet | Agents pick wrong tool; can't audit which descriptions are at fault | CI gate + SSO dashboards + private rules | **$15K-$40K/yr Team / Enterprise** |
| **AI safety / red-team vendor** | Need static-quality signal alongside security signal | API access for ingest into security suites | Channel partnerships |
| **Foundation lab / AAIF / official registry** | Need ecosystem-health metric | Licensed dataset + per-server grades | **$100K+/yr** strategic deal |

**Primary SaaS buyer**: the MCP marketplaces. They already run quality scores; they already have revenue tied to those scores; they need an explainable, defensible engine. White-labelling MCPolish is a faster path for them than maintaining their own.

**Pricing comparables**: Snyk Team $25/dev/mo + Enterprise $5K-$70K/yr [11]. Code Climate Quality $49/user/mo [12]. SonarQube Enterprise $20K+/yr. ESLint is free: but every commercial linter (Snyk Code, SonarQube, Code Climate) has demonstrated WTP for a CI-shaped quality SaaS.

---

## 5. Competitive Landscape

See the full table in §2.3. In one sentence: **ToolRank is the only adjacent competitor and it's a hobby project with 4 generic rules; everything else is either security-focused (mcp-scan, MCPWatch) or registry-side and closed (Smithery, Glama).**

### 5.1 The defensive moat

- **Citation defensibility.** Each rule cites the Wang/Li papers and the operational evidence behind it. That's hard to argue with.
- **Stable rule IDs.** Once `MP010 generic-tool-name` is in production code, switching to a competitor means rewriting `# mcpolish-disable MP010` comments. Sticky.
- **Cross-server collision dataset.** The pinned registry snapshot is a non-trivial dataset to maintain. Compounds with each weekly refresh.
- **Marketplace partnerships.** Once Smithery or Glama uses MCPolish as their quality engine, that's a referral channel for every MCP author.

---

## 6. Product Surface

### 6.1 CLI

```bash
# Lint a single server file or directory
mcpolish lint server.py
mcpolish lint .                     # auto-discovers MCP entry points

# Severity controls (Clippy-style)
mcpolish lint . --select MP010,MP012
mcpolish lint . --ignore MP020      # disable specific rules
mcpolish lint . --severity warn     # treat all-but-correctness as warnings

# LLM-gated rules
mcpolish lint . --llm openai:gpt-5  # enables MP026, MP031, MP032

# Cross-server collisions
mcpolish lint . --registry official # checks against the AAIF official registry
mcpolish lint . --registry off      # disable cross-server checks

# Auto-fix
mcpolish lint . --fix               # safe fixes only
mcpolish lint . --fix --unsafe-fix  # everything

# Machine output
mcpolish lint . --format json > report.json
mcpolish lint . --format sarif      # for GitHub Code Scanning
mcpolish lint . --format gitlab     # for GitLab merge requests

# Score (Lighthouse-style)
mcpolish score . --json             # 0-100 weighted score per the public rubric
```

### 6.2 Sample output

```
mcpolish 0.4.0
server: memnex/server.py  (8 tools)

memnex/server.py:42:5: MP010 [W] tool name `search` is too generic
  ──► consider a more specific name like `search_memory` or `query_memory_facts`
  ──► see https://mcpolish.dev/rules/MP010

memnex/server.py:42:5: MP011 [E] redundant prefix `memnex_` in tool `memnex_search_memory`
  ──► the server is already namespaced as `memnex`; rename to `search_memory`
  ──► see https://mcpolish.dev/rules/MP011

memnex/server.py:65:5: MP020 [W] description shorter than 50 characters (32 chars)
  ──► see https://mcpolish.dev/rules/MP020

memnex/server.py:80:5: MP030 [E] param `limit` is typed `string` but description says "number of results"
  ──► see https://mcpolish.dev/rules/MP030

Found 4 issues (2 errors, 2 warnings): score: 78/100
```

### 6.3 Pre-commit hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/vtensor/mcpolish
    rev: v0.4.0
    hooks:
      - id: mcpolish
```

### 6.4 GitHub Action

```yaml
- uses: vtensor/mcpolish-action@v1
  with:
    fail-on: error
    report: sarif         # uploads to GitHub Code Scanning UI
    comment-pr: true      # posts inline PR comments
```

### 6.5 Configuration (`pyproject.toml`)

```toml
[tool.mcpolish]
target-version = "2025-11"          # MCP spec version
select = ["MP001-MP040"]            # rule ranges
ignore = ["MP025"]
line-length = 100
registry = "official"

[tool.mcpolish.MP010]
allow = ["search", "query"]         # per-rule config: your server's exceptions

[tool.mcpolish.MP022]
required-examples = 1               # at least 1 example per param

[tool.mcpolish.score]
weights = { schema = 0.20, naming = 0.30, description = 0.30, consistency = 0.20 }
```

### 6.6 SaaS dashboard (paid)

- Per-org list of all MCP servers in scope.
- Time-series rule violations by category.
- Cross-server collision graph.
- Quality badges (Markdown/SVG embed).
- White-label registry integration (Smithery / Glama partner mode).
- Private rules (custom regex on description fields, custom collision allowlists).

---

## 7. Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                MCP Server source (Python / TS)               │
└──────────────┬───────────────────────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────────────────────┐
│                  mcpolish.discover                           │
│  Locates @mcp.tool() / Server.add_tool() registrations.      │
│  Extracts (name, description, inputSchema, outputSchema)     │
│  from Python AST or TypeScript ts-morph parse.               │
│  Produces ToolRegistry IR.                                   │
└──────────────┬───────────────────────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────────────────────┐
│                  mcpolish.rules                              │
│  24 visitors over ToolRegistry IR.                           │
│  Each emits zero or more Diagnostics.                        │
│  4 visitors are LLM-gated and skipped unless --llm is set.   │
└──────────────┬───────────────────────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────────────────────┐
│                  mcpolish.registry                           │
│  Pinned snapshot of the top-N public MCP tools.              │
│  Used by cross-server collision checks (MP013).              │
└──────────────┬───────────────────────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────────────────────┐
│           mcpolish.report (JSON / SARIF / GitLab / TTY)      │
└──────────────┬───────────────────────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────────────────────┐
│                  mcpolish.cli  +  exit code                  │
└──────────────────────────────────────────────────────────────┘
```

One parse, many rules: Ruff's pattern. The `ToolRegistry` IR is the choke point: every rule visits the same IR, so adding a rule is `O(1)` in parse cost.

---

## 8. Code Structure

Single PyPI package `mcpolish`. Single binary entrypoint. Google-style: shallow, intentional, nouns for modules, verbs/types for files.

```
mcpolish/
├── pyproject.toml
├── README.md
├── LICENSE                              # Apache-2.0 OSS core
├── docs/
│   ├── concepts.md
│   ├── rules/                           # one Markdown file per MP### rule
│   │   ├── MP010-generic-tool-name.md
│   │   ├── MP011-redundant-prefix.md
│   │   └── ...
│   ├── tutorials/
│   ├── reference/
│   └── methodology.md                   # cite Wang 2026, Li 2026
├── examples/
│   ├── clean_server.py                  # passes all rules
│   ├── smelly_server.py                 # fails every rule for testing
│   └── ts_server.ts                     # TypeScript example
├── tests/
│   ├── unit/
│   │   ├── test_discover_python.py
│   │   ├── test_discover_typescript.py
│   │   ├── test_rule_mp010.py
│   │   └── ...                          # one per rule
│   ├── fixtures/
│   │   └── servers/                     # known-good + known-bad MCP servers
│   ├── property/
│   │   └── test_idempotent_fix.py       # applying fix twice = identical output
│   ├── golden/
│   │   └── full_lint_outputs/           # frozen JSON outputs vs prior versions
│   └── e2e/
│       └── test_cli_lint.py
├── benches/
│   └── bench_lint_1000_servers.py       # perf budget
└── src/mcpolish/
    ├── __init__.py
    ├── _version.py
    ├── types.py                         # ToolRegistry, Diagnostic, Severity: Pydantic
    ├── exceptions.py
    ├── logging.py
    │
    ├── discover/                        # ──── parse + IR
    │   ├── __init__.py
    │   ├── base.py                      # Discoverer Protocol
    │   ├── python_ast.py                # libcst-based, handles @mcp.tool(), Server.add_tool()
    │   ├── typescript.py                # invokes ts-morph via Node subprocess (cached)
    │   ├── schema.py                    # validates inputSchema against JSON Schema 2020-12
    │   └── ir.py                        # ToolRegistry builder
    │
    ├── rules/                           # ──── all 24 lint rules
    │   ├── __init__.py
    │   ├── base.py                      # Rule Protocol, RuleContext
    │   ├── registry.py                  # registers rules by ID
    │   ├── schema/
    │   │   ├── MP001_require_tool_description.py
    │   │   ├── MP002_require_param_description.py
    │   │   ├── MP003_require_return_schema.py
    │   │   ├── MP004_require_required_array.py
    │   │   └── MP005_valid_json_schema.py
    │   ├── naming/
    │   │   ├── MP010_generic_tool_name.py
    │   │   ├── MP011_redundant_prefix.py
    │   │   ├── MP012_inconsistent_verb_pattern.py
    │   │   ├── MP013_name_collision_cross_server.py
    │   │   └── MP014_snake_vs_camel.py
    │   ├── description/
    │   │   ├── MP020_too_short.py
    │   │   ├── MP021_too_long.py
    │   │   ├── MP022_missing_example.py
    │   │   ├── MP023_no_trigger_condition.py
    │   │   ├── MP024_jargon_density.py
    │   │   ├── MP025_useless_qualifier.py
    │   │   └── MP026_ambiguous_description.py     # LLM-gated
    │   ├── consistency/
    │   │   ├── MP030_param_type_mismatch.py
    │   │   ├── MP031_param_meaning_mismatch.py    # LLM-gated
    │   │   ├── MP032_undocumented_side_effect.py  # LLM-gated
    │   │   └── MP033_duplicate_tool_description.py
    │   └── security/
    │       ├── MP040_hidden_prompt_injection.py
    │       └── MP041_instruction_in_description.py
    │
    ├── llm/                             # ──── only used by LLM-gated rules
    │   ├── __init__.py
    │   ├── client.py                    # openai/anthropic/ollama adapter
    │   ├── cache.py                     # SQLite-backed prompt cache, content-addressed
    │   └── prompts/
    │       ├── MP026_ambiguity.txt
    │       ├── MP031_meaning_mismatch.txt
    │       └── MP032_side_effect.txt
    │
    ├── registry/                        # ──── cross-server collision data
    │   ├── __init__.py
    │   ├── snapshot.py                  # loads pinned top-N tool registry
    │   ├── fetcher.py                   # weekly refresh (SaaS-only; OSS reads bundled snapshot)
    │   └── data/
    │       └── snapshot.v1.parquet      # ~10 MB; updated quarterly in OSS releases
    │
    ├── fix/                             # ──── safe and unsafe autofixes
    │   ├── __init__.py
    │   ├── base.py                      # Fix Protocol; safe vs unsafe
    │   └── strategies/
    │       ├── add_description_stub.py
    │       └── rename_redundant_prefix.py
    │
    ├── score/                           # ──── 0-100 scorer
    │   ├── __init__.py
    │   ├── scorer.py                    # weighted aggregation per pyproject config
    │   └── badge.py                     # SVG badge generation
    │
    ├── report/                          # ──── output formats
    │   ├── __init__.py
    │   ├── base.py                      # Reporter Protocol
    │   ├── tty.py                       # Rich-rendered CLI output
    │   ├── json_report.py
    │   ├── sarif.py
    │   ├── gitlab.py                    # Code Quality JSON format
    │   └── pr_comment.py                # Markdown for GitHub PR comments
    │
    ├── cli/
    │   ├── __init__.py
    │   ├── main.py                      # entry point (Click)
    │   ├── lint.py                      # `mcpolish lint`
    │   ├── score.py                     # `mcpolish score`
    │   ├── doctor.py                    # `mcpolish doctor`: config validation
    │   ├── explain.py                   # `mcpolish explain MP010`: opens docs
    │   └── update.py                    # `mcpolish update-registry` (SaaS-only)
    │
    ├── config/
    │   ├── __init__.py
    │   ├── loader.py                    # reads pyproject.toml [tool.mcpolish]
    │   └── schema.py                    # Pydantic model for config
    │
    └── integrations/
        ├── __init__.py
        ├── pre_commit.py
        ├── github_action.py
        └── pytest_plugin.py
```

### 8.1 Why this layout

- **One folder per noun.** `discover`, `rules`, `report`, `score`, `fix`, `registry`, `llm`, `cli`, `config`. No `utils.py`.
- **Each rule is its own file, named after its ID.** `MP010_generic_tool_name.py`. Grepping for a rule by ID lands in one file. This is the Ruff layout.
- **Rules are grouped by category folder.** Mirrors documentation structure. Mirrors Clippy's lint-group taxonomy.
- **The `llm/` module is isolated.** Any code that calls an LLM lives only here. The core engine never imports from `llm/`. Determinism guarantee is structural.
- **`registry/` has bundled data.** OSS ships a quarterly snapshot in-package. SaaS refreshes weekly via `fetcher.py`.
- **Dependency direction**: `cli → (lint, score) → rules → (discover, registry) → types`. Never up.

### 8.2 Public API

```python
from mcpolish import lint, score, Rule, Diagnostic
```

Library users get exactly that. Power users reach into `mcpolish.rules.MP010_generic_tool_name` directly.

---

## 9. Module Designs

### 9.1 `mcpolish.types`

```python
from pydantic import BaseModel
from enum import Enum
from typing import Optional, Sequence

class Severity(str, Enum):
    ERROR = "error"          # release-blocking by default
    WARNING = "warn"
    NOTE = "note"

class ToolDecl(BaseModel):
    """One tool registration."""
    name: str
    description: str
    input_schema: dict        # JSON Schema 2020-12
    output_schema: Optional[dict] = None
    file: str                 # source file
    line: int
    col: int

class ToolRegistry(BaseModel):
    """The IR every rule visits."""
    server_name: str          # from MCP server metadata
    tools: Sequence[ToolDecl]
    raw_source: dict          # AST nodes keyed by tool name, for fix application

class Diagnostic(BaseModel):
    rule_id: str              # "MP010"
    severity: Severity
    message: str
    file: str
    line: int
    col: int
    fix: Optional["Fix"] = None
    docs_url: str             # https://mcpolish.dev/rules/MP010
```

Immutable. JSON-Schema emitting. The only types that cross module boundaries.

### 9.2 `mcpolish.discover`

Discoverer Protocol:

```python
class Discoverer(Protocol):
    def supports(self, path: Path) -> bool: ...
    def extract(self, path: Path) -> ToolRegistry: ...
```

Two implementations in v1:

- `python_ast.PythonDiscoverer`: uses `libcst` (not `ast`) for round-trippable parse + position info. Detects `@mcp.tool()`, `@server.tool()`, `Server.add_tool(...)`, `FastMCP.tool(...)`. Resolves description from docstrings or explicit kwargs. Parses `inputSchema=...` literal or Pydantic-derived schema.
- `typescript.TSDiscoverer`: shells out to a vendored `ts-morph` Node helper (cached binary), extracts tool registrations from `server.tool({...})` calls.

Why libcst over ast: idempotent fix application requires position-preserving CST.

### 9.3 `mcpolish.rules`

Rule Protocol:

```python
class Rule(Protocol):
    id: str                            # "MP010"
    name: str                          # "generic-tool-name"
    category: Category                 # NAMING, DESCRIPTION, etc.
    severity_default: Severity
    llm_gated: bool = False
    auto_fixable: bool = False

    def check(self, registry: ToolRegistry, ctx: RuleContext) -> Iterable[Diagnostic]: ...
```

Registration via decorator:

```python
@register("MP010", category=Category.NAMING, severity=Severity.WARNING)
class GenericToolName(Rule):
    GENERIC = frozenset({"search", "query", "get", "list", "fetch", "run", "do"})

    def check(self, registry, ctx):
        allow = ctx.config.rule_config("MP010").get("allow", [])
        for tool in registry.tools:
            if tool.name in self.GENERIC and tool.name not in allow:
                yield Diagnostic(
                    rule_id="MP010",
                    severity=Severity.WARNING,
                    message=f"tool name `{tool.name}` is too generic",
                    file=tool.file, line=tool.line, col=tool.col,
                    docs_url=f"https://mcpolish.dev/rules/MP010",
                )
```

Every rule:
- Self-registers at import time. (`mcpolish.rules.__init__.py` imports all `MP*.py` modules.)
- Returns iterable of `Diagnostic`.
- Reads `ctx.config` for per-rule overrides.
- Is independently testable (pass it a `ToolRegistry`, assert diagnostics).

### 9.4 `mcpolish.rules.naming.MP013`: cross-server collision

The interesting one. Loads `registry/data/snapshot.v1.parquet`, builds an in-memory set of `(tool_name → [server_names])`, flags any tool whose name appears in the top-N (default 1000) of *other* servers in the snapshot.

In OSS, the snapshot is quarterly. In SaaS, it's weekly and includes private-org tool names.

### 9.5 `mcpolish.llm.cache`

SQLite at `~/.cache/mcpolish/llm.db`. Key: SHA-256 of `(rule_id, model_id, prompt, input)`. Value: response + timestamp. TTL: 30 days. This makes `--llm` checks fast on the second run and friendly to CI re-runs.

Cache is also serialisable, so a team can ship a `.mcpolish-cache.sqlite` in CI artifacts to skip LLM calls on unchanged tools.

### 9.6 `mcpolish.fix`

Two-level safety model (borrowed from Biome):

- **Safe fix**: deterministic, semantics-preserving. Example: `MP002` adds an empty `description=""` kwarg to a tool definition where it was missing. Applied by `--fix`.
- **Unsafe fix**: requires human review. Example: `MP011` renames `memnex_search_memory` → `search_memory`: that's an API change. Applied only with `--unsafe-fix`.

Fix application uses libcst's mutator API for Python so formatting is preserved.

### 9.7 `mcpolish.score`

Weighted aggregation:

```python
score = 100 - sum(
    weight[d.severity] * weight[rule.category] for d in diagnostics
)
```

Defaults: error = 5pt, warning = 2pt, note = 0.5pt. Category weights configurable in `pyproject.toml`. Capped at 0 floor.

Score is the SaaS hook: badges, dashboards, and registry-side scoring all consume it.

### 9.8 `mcpolish.cli`

Click + Rich. `mcpolish lint`, `mcpolish score`, `mcpolish explain MP010`, `mcpolish doctor` (validate config), `mcpolish update-registry` (SaaS-only).

Exit codes:
- `0`: no errors (warnings okay)
- `1`: at least one error
- `2`: file/parse failure
- `64`: usage error
- `65`: config error
- `70`: internal error

### 9.9 `mcpolish.report`

Multi-format. Each reporter is a Protocol implementation:

```python
class Reporter(Protocol):
    def emit(self, diagnostics: Iterable[Diagnostic], score: int, target: TextIO) -> None: ...
```

`tty` (Rich), `json_report`, `sarif` (GitHub Code Scanning), `gitlab` (merge request UI), `pr_comment` (markdown for PR bots). Open/Closed: adding a format is a new file + a registry entry. Zero edits to existing reporters.

---

## 10. Data Model

### 10.1 Registry snapshot schema

```
registry/data/snapshot.v1.parquet
─────────────────────────────────
server_id        string         dictionary
server_name      string
tool_name        string
description      string
input_schema     string (JSON)
namespace        string         (e.g. "memnex")
install_count    int64
last_updated     timestamp[us, UTC]
source           string         (smithery / glama / official / pulsemcp)
```

Bundled in OSS releases (~10 MB compressed for top 10,000 tools).

### 10.2 Diagnostic JSON output

```json
{
  "schema": "https://mcpolish.dev/schemas/report.v1.json",
  "version": "0.4.0",
  "server": "memnex",
  "scanned_at": "2026-05-16T10:30:00Z",
  "files_scanned": 12,
  "tools_found": 8,
  "score": 78,
  "diagnostics": [
    {
      "rule_id": "MP010",
      "severity": "warn",
      "message": "tool name `search` is too generic",
      "file": "memnex/server.py",
      "line": 42, "col": 5,
      "docs_url": "https://mcpolish.dev/rules/MP010",
      "fix": null
    }
  ]
}
```

Schema published at `https://mcpolish.dev/schemas/report.v1.json`. Stable v1; additions only.

---

## 11. Performance Budget

| Operation | Budget |
|---|---|
| Discover a 20-tool Python server | < 50ms |
| Run all 20 deterministic rules | < 100ms total |
| Cross-server collision check (10K snapshot) | < 30ms |
| `mcpolish lint .` end-to-end (single server) | < 200ms (sub-second promise) |
| `mcpolish lint .` with 4 LLM-gated rules, cold cache, 8 tools | < 30s |
| `mcpolish lint .` with 4 LLM-gated rules, warm cache | < 500ms |
| SaaS scan: 10K servers, deterministic rules only | < 5 min (parallelised) |

Optimisations:
- libcst parse once per file, all rules visit the same tree.
- Cross-server snapshot loaded once into a hash set.
- LLM cache is content-addressed; identical descriptions never re-call.

If sub-second slips on Python (libcst isn't as fast as Ruff's Rust parser), a Rust rewrite of `discover` is on the roadmap. Out of scope for v1: Python is enough for the perf budget above.

---

## 12. Scalability

### 12.1 OSS path (single server, single repo)

Always single-process, single-machine, sub-second. No scalability concern.

### 12.2 SaaS path

The hard problem is registry-wide scanning: scan all 10K+ MCP servers weekly, store time-series of scores and violations, serve dashboards.

- **Ingest**: nightly cron pulls server source from public registries (Smithery / Glama / PulseMCP have programmatic APIs). Clone to ephemeral storage.
- **Compute**: stateless workers run `mcpolish lint --format json` per server. RQ on Redis for queueing. 10K servers / 200ms each = ~30 min on 10 workers.
- **Storage**: S3 for raw report JSONs partitioned by week. DuckDB for analytic queries against the lake. Postgres for org/user/billing.
- **Time series**: per-server score and rule-violation counts in TimescaleDB hypertable. Cheap, no ad-hoc OLAP needed.
- **Dashboards**: Next.js + DuckDB-WASM for browser-side aggregation on the lighter queries. Server-side DuckDB for joins.

### 12.3 Capacity targets, year 1

- 5 marketplace partners (Smithery, Glama, PulseMCP, MCP.so, official)
- 200 paying enterprise teams
- 100K servers under weekly scan
- Comfortably 2 `t3.large` workers + Aurora Serverless v2 + 500 GB S3

### 12.4 Multitenancy

Same model as EVALSIG: Postgres RLS by `org_id`, S3 path prefix `org_id/`. Workers carry an org token.

---

## 13. Reliability and Failure Modes

| Failure | Detection | Mitigation |
|---|---|---|
| Server source has syntax errors | discover step | Surface as `MP000 parse-error`; continue with other files |
| Tool definition is dynamic (built at runtime, not statically declarable) | discover step | Emit a `MP000 dynamic-tools-detected` note; skip dynamic tools |
| LLM API down (`--llm` mode) | llm/client.py with retries (tenacity) | Fall back to skip-LLM-rules + warning; never block on LLM |
| Registry snapshot stale/missing | registry/snapshot.py | Use bundled in-package snapshot; warn that cross-server checks may be out of date |
| User config invalid | config/loader.py at startup | Exit 65 with detailed error; never silent-default |
| Rule throws unexpected exception | rules/registry.py wraps each rule call | Emit `MP000 internal-error` diagnostic; continue with remaining rules. Never abort entire scan. |

Every error is a typed subclass of `McpolishError`. No bare `except`. Rules are sandboxed: one buggy rule never aborts the lint.

---

## 14. Security and Privacy

- **OSS core has zero network egress.** Static analysis of local files only. Bundled snapshot ships in-package.
- **`--llm` flag is opt-in.** When on, descriptions and inputSchemas are sent to the configured provider (OpenAI / Anthropic / Ollama / etc.). Documented prominently.
- **`--registry` is opt-in for online refresh.** Default is bundled snapshot. `--registry online` fetches the latest from a CDN.
- **No `eval()`-style dynamic dispatch.** Rule registration is import-time, not config-time.
- **SaaS data plane**: TLS 1.3, AES-256 at rest, customer-managed KMS at Team tier and above.
- **No prompt content stored.** SaaS keeps `(rule_id, severity, file, line, col)` and aggregated metrics: never the description text from private servers. Aggregate-only collision detection.
- **SOC2 Type II** by month 9 of SaaS launch.

The security surface is *much smaller* than mcp-scan's because we're static: no runtime sandbox to escape, no remote-tool-execution attack surface.

---

## 15. Commercial Packaging

### 15.1 Tier matrix

| Tier | Price | Includes | ICP |
|---|---|---|---|
| **OSS** | Free, Apache-2.0 | Library, CLI, pre-commit, GitHub Action, quarterly snapshot | Individual MCP authors, OSS projects |
| **Pro** | $39 / dev / mo | OSS + private rules, custom collision allowlists, weekly snapshot, SARIF for GitHub Advanced Security | Solo / small teams |
| **Team** | $20 / dev / mo, 5-seat min | All Pro + SaaS dashboards (1 year history), SSO, audit log, badge generator | Mid-market enterprise platform teams |
| **Enterprise** | from $30K / yr | All Team + on-prem deployable, custom retention, SOC2 report, dedicated CSM | Banks, defence, regulated industries |
| **Registry / Marketplace** | from $50K / yr | API for ingesting third-party server source + white-label badges + private rules | Smithery, Glama, PulseMCP, MCP.so, official MCP Registry |

Anchored against Snyk Team ($25/dev/mo), Code Climate ($49/user/mo), SonarQube Enterprise ($20K+/yr).

### 15.2 GTM motion

1. **OSS first.** Ship the 24 rules + GitHub Action + a documentation site with one page per rule citing the Wang/Li papers. Submit to MCP Discord, /r/LocalLLaMA, the AAIF working group.
2. **Land one MCP marketplace as design partner.** Smithery is most likely: their public quality score is opaque and they have direct economic incentive to outsource the engine. Free / discounted in exchange for case study.
3. **Convert marketplace partnership into co-marketing.** Smithery-badge → "scored by MCPolish" links → top-of-funnel for MCPolish OSS.
4. **Enterprise wedge**: financial-services / defence teams running internal MCP fleets. Compliance + audit-trail story.
5. **Conference / blog presence.** AAIF working-group meetings, MCP Devs Day, Anthropic Builders summit. Publish "State of MCP Server Quality" annual report from the SaaS dataset. That report is itself a content asset.

### 15.3 The moat

- **Rule taxonomy is citation-backed.** Hard to dispute, hard to clone in a quarter.
- **Stable rule IDs.** Sticky in users' `noqa`-equivalent comments.
- **Cross-server collision dataset.** Compounds weekly.
- **Marketplace partnerships.** Once one major registry rebrands MCPolish as their engine, second is easier (network effect).
- **Time-series quality dataset.** "Servers that scored < 60 last year had 2.3× the GitHub-issue rate": that's a publishable claim.

---

## 16. Milestones

| Phase | Scope | Duration |
|---|---|---|
| **M0: Foundation** | Repo scaffold, `discover` (Python), `types`, MP001-MP005 (schema rules), MP010-MP012 (naming), `report.tty`, `report.json`, CLI `lint`. | 4 weeks |
| **M1: Full Ruleset** | All 24 rules including LLM-gated four, `--fix` for 8 safe rules, MP013 cross-server with bundled snapshot, GitHub Action, pre-commit hook. | 4 weeks |
| **M2: TypeScript Support** | `discover/typescript.py` (ts-morph subprocess), TS test fixtures, docs site go-live, `mcpolish explain` command. | 3 weeks |
| **M3: SaaS MVP** | Registry crawler, weekly scan, dashboards (Next.js), auth (Clerk), Stripe billing, first marketplace partner. | 8 weeks |
| **M4: Compliance + Marketplace GA** | SOC2 prep, white-label badge API, second marketplace partner, public launch. | 8 weeks |

Total to GA: ~27 weeks. Two-person team. Founder + one senior backend.

---

## 17. SOLID + Engineering Principles Applied

- **S: Single Responsibility.** `discover` parses, `rules` checks, `fix` mutates, `score` aggregates, `report` formats, `cli` presents. No module owns two of those.
- **O: Open/Closed.** Adding a new rule = one new file in `rules/{category}/`. Adding a new report format = one new file in `report/`. Adding a new language = one new `Discoverer`. Zero edits to existing code.
- **L: Liskov.** `Discoverer`, `Rule`, `Reporter`, `Fix` are all Protocols. Implementations are swappable.
- **I: Interface segregation.** No god-class `MCPolish`. The CLI imports `lint()` and `score()`. Library users import `Rule` and `Diagnostic`. No fat base classes.
- **D: Dependency inversion.** `cli → lint → rules → discover → types`. Never up.

Other practices:
- **Stable rule IDs forever.** Like Ruff, like ESLint. `MP010` means one thing for the life of the project.
- **Two-tier fix safety** (Biome's pattern). Safe by default, unsafe with explicit flag.
- **Pure-function rules.** No I/O in `check()`. Test by passing a `ToolRegistry`, asserting diagnostics. No fixtures-on-disk required.
- **Typed everywhere.** `mypy --strict`. Pydantic at boundaries.
- **Determinism is structural.** LLM code lives only in `llm/`. The core engine cannot call out by construction.

---

## 18. Open Questions

1. **First-class TypeScript support in v1?** Decision tree: most MCP servers are TypeScript, but Python tooling is faster to ship. Plan: Python in M0-M1, TypeScript in M2. Risk: if a TypeScript MCP marketplace partner lands first, accelerate.
2. **Plugin system?** Postpone past v1. Like Ruff, ship a strong first-party rule set; pluginise only after community pressure.
3. **Single binary vs Python?** Python for v1 (faster to ship). Reconsider Rust rewrite of `discover` + `rules` core if perf budget slips on large monorepos. Likely v2.
4. **MCP version targeting.** MCP spec versions (2024-11, 2025-03, 2025-11) have breaking changes. Need `target-version` config and per-version rule activation.
5. **Should the OSS package include the LLM-gated rules at all?** Pro: discoverability. Con: confusion ("I ran lint and got 20 diagnostics, why?"). Lean: include but require explicit `--llm` flag, never run silently.
6. **Pricing for marketplace partners.** $50K/yr is the anchor, but they may push for revenue-share on badge clicks. Negotiable past M3.

---

## 19. References

[1] Wang, Li, Sun, Liu, Liu, Tian, "From Docs to Descriptions: Smell-Aware Evaluation of MCP Server Descriptions," arXiv:2602.18914, Feb 2026. https://arxiv.org/abs/2602.18914
[2] Glama MCP server registry. https://glama.ai/mcp/servers
[3] MCPWatch on Glama (OWASP MCP Top 10 grading). https://glama.ai/mcp/servers/lazymac2x/mcpwatch
[4] Smithery quality score breakdown. https://medium.com/@francofuji/your-mcp-server-scores-60-100-on-smithery-what-it-means-and-how-to-hit-100-edd924758268
[5] "One Year of MCP," modelcontextprotocol.io blog, Nov 2025. https://blog.modelcontextprotocol.io/posts/2025-11-25-first-mcp-anniversary/
[6] InfoQ, "OpenAI Adds Full MCP Support to ChatGPT," Oct 2025. https://www.infoq.com/news/2025/10/chat-gpt-mcp/
[7] Li et al., "Don't believe everything you read: Understanding and Measuring MCP Behavior under Misleading Tool Descriptions," arXiv:2602.03580. https://arxiv.org/abs/2602.03580
[8] Oligo Security, "Critical RCE in Anthropic MCP Inspector (CVE-2025-49596)." https://www.oligo.security/blog/critical-rce-vulnerability-in-anthropic-mcp-inspector-cve-2025-49596
[9] Snyk Labs, "Acquisition of Invariant Labs," Jun 2025. https://labs.snyk.io/resources/snyk-labs-invariant-labs/
[10] The New Stack, "Why the Model Context Protocol Won." https://thenewstack.io/why-the-model-context-protocol-won/
[11] Konvu, "Snyk vs SonarQube pricing." https://konvu.com/compare/snyk-vs-sonarqube
[12] Vendr, "Code Climate pricing." https://www.vendr.com/marketplace/code-climate
[13] Huang et al., "MetaTool Benchmark," arXiv:2310.03128. https://arxiv.org/abs/2310.03128
[14] MCP-Scan (Invariant Labs / Snyk). https://github.com/invariantlabs-ai/mcp-scan
[15] MCP Inspector (Anthropic). https://github.com/modelcontextprotocol/inspector
[16] ESLint custom rules docs. https://eslint.org/docs/latest/extend/custom-rules
[17] Ruff (astral-sh/ruff). https://github.com/astral-sh/ruff
[18] Clippy lint categories. https://doc.rust-lang.org/stable/clippy/lints.html
[19] Biome linter docs. https://biomejs.dev/linter/
[20] Hadolint (Dockerfile linter). https://github.com/hadolint/hadolint
[21] ToolRank ("Lighthouse for MCP"). https://toolrank.dev
[22] Official MCP Registry. https://registry.modelcontextprotocol.io/
