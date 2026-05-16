# LLM-gated rules

> Who this page is for: someone deciding whether to enable the three optional rules that use an LLM judge.

## What you will learn

- Which three rules need an [LLM](../concepts/glossary.md#llm).
- How to enable them.
- How the cache keeps cost down.
- The privacy implications of sending descriptions to a provider.

## Background

mcpolish has 20 rules that are pure static analysis: deterministic, offline, sub-second. Three more rules need an LLM to judge whether a description is ambiguous, whether a parameter description matches its name and type, and whether a tool with a mutating verb is hiding side effects.

These three rules are **opt-in**. They never run unless you pass `--llm`.

## The three rules

| ID | Name | What it asks the LLM |
|---|---|---|
| MP026 | ambiguous-description | "Can a competent agent tell what this tool does from the description alone?" |
| MP031 | param-meaning-mismatch | "Do the parameter name, type, and description agree on what the agent should pass?" |
| MP032 | undocumented-side-effect | "The name suggests a mutation. Does the description acknowledge it?" |

The full prompts live in `src/mcpolish/rules/`. Read them before sending anything sensitive.

## Step by step

### 1. Install the LLM extras

```
pip install "mcpolish[llm]"
```

This adds `openai` and `anthropic` to the install.

### 2. Set your API key

For OpenAI:

```
export OPENAI_API_KEY=sk-...
```

For Anthropic:

```
export ANTHROPIC_API_KEY=sk-ant-...
```

For Ollama, no key is needed; run an Ollama daemon locally.

### 3. Run with `--llm`

```
mcpolish lint . --llm openai:gpt-4o
mcpolish lint . --llm anthropic:claude-opus-4-7
mcpolish lint . --llm ollama:llama3.1
```

The format is `provider:model`. The model must be one your provider exposes.

## How the cache works

LLM calls are slow and metered. mcpolish caches every verdict in `~/.cache/mcpolish/llm.db`, a small [SQLite](https://www.sqlite.org/) database.

The cache key is `sha256(rule_id, model_id, prompt)`. The same description with the same prompt and the same model is a cache hit the second time you run mcpolish on that tool. Cache entries expire after 30 days.

On a typical 8-tool server:

- First run with `--llm`: about 10 seconds (eight tools, three rules each, with retries).
- Second run with the same code: under a second (every call hits the cache).

You can ship the cache file in CI as an artifact. A team's CI run picks up the cache and skips repeat calls.

## What gets sent to the provider

For each LLM-gated rule, mcpolish sends:

- The rule prompt (a few hundred tokens).
- The tool name.
- The full description.
- The parameter name, type, and description (only for MP031).

What does **not** get sent:

- Your function body.
- Other tools' descriptions.
- Your file path.
- Your namespace or server name (unless it appears in the description text).

If your descriptions contain secrets or proprietary information, do not enable `--llm` unless you trust the provider.

## Provider behaviour on failure

If the LLM call fails (network, rate limit, bad key), the client logs a warning and returns `"OK"` for that rule. The lint continues. The result is that an LLM-gated rule may silently pass when the network is flaky.

If you need stricter behaviour, watch the log output:

```
MCPOLISH_LOG=WARNING mcpolish lint . --llm openai:gpt-4o
```

## Cost guidance

Single rule, single tool, gpt-4o, English description of about 100 tokens: under one cent. Mistakes are cheap.

A full repo scan with `--llm`:

- 50 tools, 3 LLM rules, cold cache: about 150 LLM calls.
- Each call: about 200 prompt tokens, 50 response tokens.
- Cost on gpt-4o: roughly 25 cents per full scan, then near zero on cache hits.

Adjust your provider and model to your cost target. Ollama is free if you can spare the local GPU time.

## Common variations

### Per-project default LLM

Set it in `pyproject.toml`:

```toml
[tool.mcpolish]
llm = "openai:gpt-4o"
```

A bare `--llm` flag (no value) reads this. An explicit `--llm provider:model` overrides it.

### Local-only judging with Ollama

```
ollama run llama3.1
mcpolish lint . --llm ollama:llama3.1
```

You need the Ollama daemon listening at `http://localhost:11434` (or override with `OLLAMA_HOST`).

### Disabling LLM rules for one run

Just omit `--llm`. The three rules are silent.

## Troubleshooting

**`OPENAI_API_KEY not set`.** The key has to be in the environment of the process running mcpolish. `export OPENAI_API_KEY=...` then re-run.

**Cache miss when I expected a hit.** Caches are keyed by the prompt text. If your description changed even by a single space, that is a new cache key. To force a cache rebuild, delete the file: `rm ~/.cache/mcpolish/llm.db`.

**LLM rule fires inconsistently.** LLM judges are stochastic. Use a low-temperature deterministic model like gpt-4o-mini. mcpolish sets temperature to 0 already, but providers may not honour it perfectly.

## See also

- [What mcpolish checks](../concepts/what-mcpolish-checks.md)
- [Configuration](configuration.md)
- [MP026](../rules/MP026.md), [MP031](../rules/MP031.md), [MP032](../rules/MP032.md)
