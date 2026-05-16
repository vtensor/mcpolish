# Installation

> Who this page is for: someone who has not yet installed mcpolish.

## What you will learn

- How to install mcpolish from PyPI.
- How to verify the install worked.
- How to install the optional [LLM](../concepts/glossary.md#llm) extras.
- How to install from source if you want to hack on mcpolish itself.

## Background

mcpolish is a Python package. It runs on Python 3.11 or newer. It has no system dependencies. It runs offline.

There is no separate daemon, server, or background process. mcpolish is a one-shot [CLI](../concepts/glossary.md#cli) that prints results and exits.

## Step by step

### 1. Confirm Python is available

```
python --version
```

You need 3.11 or newer. If you do not have it, install Python first.

### 2. Install mcpolish

```
pip install mcpolish
```

This pulls in mcpolish and its required libraries: `libcst`, `pydantic`, `click`, `rich`, and `jsonschema`.

### 3. Verify

```
mcpolish --version
```

You should see something like `mcpolish, version 0.1.0`.

### 4. Run the built-in self-check

```
mcpolish doctor
```

This validates your config, confirms the bundled cross-server [snapshot](../concepts/glossary.md#registry-snapshot) loaded, and prints the count of rules registered. Expected output:

```
config: ok (target-version=2025-11, registry=official)
snapshot: ok (51 tools, version=v1)
rules: 23 loaded
```

## Common variations

### Install the optional LLM extras

mcpolish ships three optional rules that ask an LLM to judge a description. They are off by default. To turn them on you need an LLM provider's Python SDK installed:

```
pip install "mcpolish[llm]"
```

This adds `openai` and `anthropic` to the install. You also need an API key in your environment. See [LLM rules](../usage/llm-rules.md) for details.

### Install from source

If you want to read the code or contribute:

```
git clone https://github.com/vtensor/mcpolish.git
cd mcpolish
pip install -e ".[dev]"
```

The `dev` extras add pytest, mypy, and ruff. After install you can run the test suite:

```
pytest -q
```

### Install with `uv` instead of `pip`

mcpolish works with [uv](https://github.com/astral-sh/uv):

```
uv pip install mcpolish
```

Or to add it to a `uv` project:

```
uv add mcpolish
```

## Troubleshooting

**`mcpolish: command not found`.** The package installed but the script is not on your `PATH`. If you installed into a virtual environment, activate the environment first. If you installed globally with `pip install --user`, add `python -m site --user-base`/bin to your `PATH`.

**`ModuleNotFoundError: No module named 'libcst'`.** The pip install did not complete. Re-run `pip install mcpolish` and read the output for the actual failure. Most common cause: an old Python (3.10 or older) that does not satisfy `requires-python`.

**`mcpolish doctor` reports `snapshot: missing`.** Reinstall mcpolish; the snapshot is shipped as a data file inside the wheel. If the install succeeded but the snapshot is still missing, file an issue with the output of `pip show -f mcpolish`.

## See also

- [Quickstart](quickstart.md): your first lint, in 30 seconds.
- [Your first lint](your-first-lint.md): a walkthrough on a real file.
