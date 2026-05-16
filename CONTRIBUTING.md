# Contributing to mcpolish

Thank you for taking the time to contribute. This page explains how to get a development environment set up, the conventions the project follows, and how to propose changes.

## Ways to contribute

| If you have... | Open a |
|---|---|
| Found a bug | [Bug report issue](https://github.com/vtensor/mcpolish/issues/new?labels=bug) |
| Want a new rule | [Rule proposal issue](https://github.com/vtensor/mcpolish/issues/new?labels=rule-proposal) with a citation or operational evidence |
| Spotted a doc problem | Pull request that edits the file under `docs/` |
| Fixed a bug | Pull request linked to the issue |
| Want to discuss design | [Discussion](https://github.com/vtensor/mcpolish/discussions) |

Before opening a large pull request, please open an issue first so we can agree on the approach. Small fixes (typos, single-rule patches, doc edits) do not need an issue first.

## Development setup

mcpolish needs Python 3.11 or newer.

```bash
git clone https://github.com/vtensor/mcpolish.git
cd mcpolish
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev,llm]"
```

The `dev` extra adds pytest, mypy, and ruff. The `llm` extra adds the OpenAI and Anthropic SDKs needed for the three LLM-judged rules.

## Running the tests

```bash
pytest -q
```

The suite has 132 tests and runs in under one second. It must stay green for any pull request to be merged.

Useful subsets:

```bash
pytest -k MP010                 # tests for one rule
pytest tests/unit/test_scenarios.py -v
pytest --tb=short               # shorter failure traces
```

## Linting and type-checking

```bash
ruff check src tests
mypy src/mcpolish
mcpolish lint examples/clean_server.py
```

All three must pass before merge.

## Running mcpolish on itself

mcpolish lints MCP servers; the examples under `examples/` are real MCP servers. Use them as a smoke test:

```bash
mcpolish lint examples/clean_server.py       # must score 100
mcpolish lint examples/smelly_server.py --fail-on never
```

## Adding a new rule

This is the most common kind of contribution. The shape:

1. **Open a rule proposal issue.** Cite the paper, blog post, or operational evidence that supports the rule.
2. **Pick the next stable ID** in the appropriate category:
   - Schema: MP001-MP009
   - Naming: MP010-MP019
   - Description: MP020-MP029
   - Consistency: MP030-MP039
   - Security: MP040-MP049
3. **Add the rule file** under `src/mcpolish/rules/<category>/MPxxx_name.py`. Follow the shape of existing rules.
4. **Register it** with the `@register` decorator so the rule shows up at import time.
5. **Add a fixture** under `tests/fixtures/scenarios/rule_MPxxx.py` that triggers exactly your rule.
6. **Add tests** under `tests/unit/test_rules_<category>.py` plus the parametrised entry in `tests/unit/test_scenarios.py`.
7. **Write the docs** under `docs/rules/MPxxx.md`. Follow the template in [docs/rules/MP010.md](docs/rules/MP010.md).
8. **Update the indexes**: `docs/rules/index.md`, `docs/concepts/what-mcpolish-checks.md`, and `docs/methodology.md`.

Once shipped, a rule ID is stable forever. The default severity may change between releases. The ID and the human name never do.

## Style

- Plain English in docs and comments. Avoid em dashes and box-drawing characters; the project deliberately uses ASCII only.
- Sentences under 25 words where reasonable.
- Define every short form on first use, or link to the [glossary](docs/concepts/glossary.md).
- Code style follows `ruff` defaults. Run `ruff format` before committing.
- Type hints everywhere. `mypy` runs in strict mode for new code paths.

## Pull request checklist

Before opening a pull request:

- [ ] Tests pass: `pytest -q`
- [ ] Lint passes: `ruff check src tests`
- [ ] No forbidden characters: `grep -rPn "[\x{2014}\x{2013}\x{2500}-\x{257F}]" src tests docs README.md` returns nothing (Unicode em dash U+2014, en dash U+2013, and box-drawing block)
- [ ] Internal markdown links resolve (run the link-check script in `tests/` if present, or open the changed pages)
- [ ] New code paths covered by tests
- [ ] Docs updated where behaviour changed
- [ ] `VERIFICATION.md` updated if a verification scenario changed

## Commit messages

Use a short imperative subject line:

```
add MP015 require-tool-version
fix MP004 firing on auto-derived schemas
docs: expand MP010 examples
```

Long-form commit bodies are welcome for non-trivial changes.

## Release process (maintainers)

1. Bump `__version__` in `src/mcpolish/_version.py`.
2. Bump `version` in `pyproject.toml`.
3. Update `CHANGELOG.md`.
4. Tag the release: `git tag -a v0.x.y -m "v0.x.y"`.
5. Push: `git push --tags`.
6. CI publishes the wheel to PyPI.

## Code of Conduct

This project follows the [Contributor Covenant](CODE_OF_CONDUCT.md). Participation in this project means agreeing to abide by it.

## License

By contributing, you agree that your contributions will be licensed under the project's Apache 2.0 [LICENSE](LICENSE).
