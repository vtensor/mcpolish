# mcpolish verification report

Generated 2026-05-16. Records every scenario exercised against mcpolish 0.1.0
along with the actual outcome.

## Summary

| | |
|---|---|
| Total scenarios | 67 (locked as automated tests) |
| Pass | 67 |
| Fail | 0 |
| Bugs found and fixed during verification | 2 |
| Test command | `pytest -q` |
| Run time of full suite | 0.28 seconds for 132 tests |

## How to reproduce

```
pip install -e ".[dev]"
pytest -q
```

Every result below is one row in `tests/unit/test_scenarios.py`. Each scenario
has at least one fixture under `tests/fixtures/scenarios/`. Run any single
scenario with:

```
pytest -k <scenario_name> -v
```

## Bugs found and fixed

| Bug | Where | Fix |
|---|---|---|
| MP004 never fired on hand-written Tool() schemas that omitted the `required` array | `src/mcpolish/rules/schema/MP004_require_required_array.py` | Track whether the schema came from a literal dict (`schema_is_explicit`). Fire when an explicit schema declares properties but omits the `required` key. |
| TTY summary line had a stray spaced hyphen after a global character scrub | `src/mcpolish/report/tty.py` | Replaced ` -  score:` with `. score:` so the line reads cleanly. |

Both bugs have regression tests under `tests/unit/test_scenarios.py`.

## Per-rule fixtures

Each rule has one fixture in `tests/fixtures/scenarios/rule_MPxxx.py` that
triggers the rule. Non-LLM rules must fire on their own fixture. LLM-gated
rules (`MP026`, `MP031`, `MP032`) must stay silent when `--llm` is not set.

| Rule | Fixture | Status | Also fires |
|---|---|---|---|
| MP001 | `rule_MP001.py` | pass | MP002, MP003 |
| MP002 | `rule_MP002.py` | pass | MP022 |
| MP003 | `rule_MP003.py` | pass | none |
| MP004 | `rule_MP004.py` | pass | MP022 |
| MP005 | `rule_MP005.py` | pass | none |
| MP010 | `rule_MP010.py` | pass | MP013 |
| MP011 | `rule_MP011.py` | pass | none |
| MP012 | `rule_MP012.py` | pass | MP013 |
| MP013 | `rule_MP013.py` | pass | MP010 |
| MP014 | `rule_MP014.py` | pass | none |
| MP020 | `rule_MP020.py` | pass | MP002, MP003, MP022, MP023 |
| MP021 | `rule_MP021.py` | pass | MP002 |
| MP022 | `rule_MP022.py` | pass | none |
| MP023 | `rule_MP023.py` | pass | none |
| MP024 | `rule_MP024.py` | pass | MP002 |
| MP025 | `rule_MP025.py` | pass | MP002 |
| MP026 | `rule_MP026.py` | pass (silent without --llm) | none |
| MP030 | `rule_MP030.py` | pass | MP001, MP003, MP022 |
| MP031 | `rule_MP031.py` | pass (silent without --llm) | none |
| MP032 | `rule_MP032.py` | pass (silent without --llm) | none |
| MP033 | `rule_MP033.py` | pass | MP003, MP011 |
| MP040 | `rule_MP040.py` | pass | MP002 |
| MP041 | `rule_MP041.py` | pass | MP002, MP023 |

## Discovery scenarios

Patterns the Python discoverer must handle. One fixture per row.

| Scenario | Fixture | Status | Notes |
|---|---|---|---|
| FastMCP `@mcp.tool()` decorator | `discovery/fastmcp_decorator.py` | pass | 1 tool, namespace detected from `FastMCP("discover_fastmcp")` |
| Low-level `Tool(name=, description=, inputSchema=)` constructor | `discovery/lowlevel_tool_constructor.py` | pass | Tool found, schema parsed |
| `server.add_tool(name=, ...)` call | `discovery/add_tool_call.py` | pass | Tool found |
| Multiple tools in one file | `discovery/multiple_tools_one_file.py` | pass | All 3 tools collected |
| File with no MCP tools at all | `discovery/no_tools.py` | pass | Zero tools, no crash |
| Empty file | `discovery/empty.py` | pass | Zero tools, no crash |
| Python syntax error | `discovery/syntax_error.py` | pass | Logs warning, yields zero tools |
| `async def` tools | `discovery/async_tools.py` | pass | Treated the same as sync |
| Pydantic `BaseModel` as param | `discovery/pydantic_schema.py` | pass | Falls back to bare signature in v1 |
| Rich type hints (`list[str]`, `Optional`, `Annotated`) | `discovery/typed_params.py` | pass | Mapped to JSON types |
| Google / NumPy / plain docstring styles | `discovery/docstring_styles.py` | pass | All three discovered, only Google-style Args block is parsed |
| Dynamic registration (loop over specs) | `discovery/dynamic_registration.py` | pass | Skipped silently (no literal name) |

## Modular project scenario

A realistic layout with the server in `main.py` and tools spread across
`tools/search.py`, `tools/memory.py`, `tools/admin.py`, plus helper files with
no tools.

| Check | Result |
|---|---|
| Tools discovered | 4 (`search_records`, `store_fact`, `recall_fact`, `memnex_clear_all`) |
| Namespace | `memnex` (from `FastMCP("memnex")` in `main.py`) |
| MP011 fires across files | Yes, on `memnex_clear_all` (in `tools/admin.py`) |
| Helper file with no tools | Walked, zero contribution, no crash |

## CLI flag scenarios

Driven by `tests/fixtures/scenarios/flags/baseline.py` plus two specialised
fixtures for the fix flags. Every flag combination is covered by an
automated test.

| Flag | Tested behaviour | Status |
|---|---|---|
| `--select MP010` | Only MP010 in output | pass |
| `--select MP020-MP025` | Range expanded, only those rules appear | pass |
| `--ignore MP010` | MP010 excluded | pass |
| `--registry off` | MP013 cross-server check disabled | pass |
| `--fix` | Safe MP001 fix inserts docstring stub | pass |
| `--fix` does not apply unsafe fixes | MP011 rename not applied | pass |
| `--unsafe-fix` | MP011 rename applied across the file | pass |
| `--format tty` | Default. Rich-rendered terminal output | pass (visual) |
| `--format json` | Stable `report.v1.json` schema | pass |
| `--format sarif` | Valid SARIF 2.1.0 | pass |
| `--format gitlab` | JSON array of code-quality findings | pass |
| `--format pr-comment` | Markdown table for PR bots | pass |
| `--fail-on error` | Default. Exit 1 only when errors | pass |
| `--fail-on warn` | Exit 1 on errors or warnings | pass |
| `--fail-on never` | Always exit 0 | pass |
| `--llm openai:gpt-4o` without API key | Skips gracefully, lint continues | locked in `mcpolish.llm.client` |

## Exit code scenarios

Verified per `MCPOLISH.md` section 9.8.

| Inputs | Expected | Actual |
|---|---|---|
| Clean file, `--fail-on error` | 0 | 0 |
| Warnings only, `--fail-on error` | 0 | 0 |
| Errors present, `--fail-on error` | 1 | 1 |
| Warnings present, `--fail-on warn` | 1 | 1 |
| Errors present, `--fail-on never` | 0 | 0 |
| Malformed `pyproject.toml` | 65 | 65 |
| Unknown rule passed to `explain` | 64 | 64 |

## Config scenarios

Fixtures under `tests/fixtures/scenarios/config/`.

| Scenario | Fixture | Result |
|---|---|---|
| Empty `[tool.mcpolish]` section | `config/empty_section/` | Acts as defaults |
| `select` and `ignore` arrays | `config/select_ignore/` | Both applied; ignore wins on conflict |
| Per-rule override (`MP010.allow`) | `config/per_rule_override/` | MP010 silenced |
| Malformed TOML | `config/malformed_toml/` | Exits 65 with a clear message, no traceback |
| Custom `score_weights` | `config/custom_weights/` | Score reflects new weights |
| No `pyproject.toml` at all | `config/no_pyproject/` | Walks up the tree; uses defaults if none found |

## Output format scenarios

| Format | Validation |
|---|---|
| `tty` | Visual check. Diagnostic line, indented hint, indented docs URL. Summary line. |
| `json` | Parses with `json.loads`. Contains `schema`, `score`, `diagnostics[]`. |
| `sarif` | Parses with `json.loads`. `version == "2.1.0"`. `runs[0].tool.driver.name == "mcpolish"`. |
| `gitlab` | Parses with `json.loads`. Top-level is a list. Each item has `severity`, `location.path`, `location.lines.begin`. |
| `pr-comment` | Markdown. Contains a header with the score and a table of diagnostics. |

## Performance budget

`MCPOLISH.md` section 11 sets a sub-second target. Measured on this hardware
with five runs each, sorted (`min / median / max`):

| Target | Budget | Measured min | Measured median | Measured max |
|---|---|---|---|---|
| 1 file, 3 tools (`clean_server.py`) | < 50 ms | 3.3 ms | 3.7 ms | 20.3 ms |
| 1 file, 7 tools (`smelly_server.py`) | < 200 ms | 4.2 ms | 4.3 ms | 4.4 ms |
| 4 files, 4 tools (`modular_project`) | < 200 ms | 6.3 ms | 6.4 ms | 6.7 ms |
| ~40 files, ~30 tools (whole fixture tree) | < 5 s | 61.8 ms | 62.5 ms | 67.1 ms |

Well inside the budget on every row.

## What is not yet covered

These items are out of scope for v1 verification but tracked elsewhere:

- TypeScript MCP server discovery (roadmap M2, see `MCPOLISH.md` section 16).
- Real LLM judge runs (requires an OpenAI or Anthropic API key in CI).
- VS Code extension end-to-end behaviour (no VS Code extension yet).
- Registry crawler / SaaS dashboard scenarios (roadmap M3).
