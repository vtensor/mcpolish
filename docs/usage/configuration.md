# Configuration

> Who this page is for: anyone customising mcpolish for a project.

## What you will learn

- Where mcpolish reads its config from.
- Every top-level setting.
- Every per-rule setting.
- How to set custom score weights.

## Background

mcpolish reads `[tool.mcpolish]` from the nearest `pyproject.toml` file. Settings in that section apply to every run from that project. CLI flags override the file when both are set.

If there is no `pyproject.toml`, mcpolish uses defaults. Defaults are sensible; you do not need to configure mcpolish to start using it.

## Where mcpolish looks

When you run `mcpolish lint TARGET`, mcpolish:

1. Resolves `TARGET` to an absolute path.
2. Walks up the directory tree from `TARGET` looking for the nearest `pyproject.toml`.
3. Reads `[tool.mcpolish]` from that file.

If no `pyproject.toml` is found anywhere up to the filesystem root, defaults apply.

## Top-level settings

```toml
[tool.mcpolish]
target-version = "2025-11"           # MCP protocol version to target
select = ["MP001-MP041"]              # only run these rules
ignore = ["MP025"]                    # never run these rules
line-length = 100                     # used in some message formatting
registry = "official"                 # "official" or "off"
server-name = "my_server"             # override autodetection
namespace = "my_server"               # override autodetection
llm = "openai:gpt-4o"                 # default provider when --llm is bare
```

| Key | Type | Default | Notes |
|---|---|---|---|
| `target-version` | string | `"2025-11"` | The MCP spec version. Future-proof for breaking spec changes. |
| `select` | list of strings | `[]` (means "all") | Rule IDs or ranges to keep. Empty means every rule. |
| `ignore` | list of strings | `[]` | Rule IDs to drop. Overrides `select`. |
| `line-length` | int | `100` | Used by formatters and a few rules. |
| `registry` | choice | `"official"` | `"off"` disables cross-server checks (MP013). |
| `server-name` | string | autodetect | Override the detected server name. |
| `namespace` | string | autodetect | Override the detected namespace. |
| `llm` | string | none | `provider:model` default for `--llm`. |

## Per-rule settings

Each rule may expose its own knobs under `[tool.mcpolish.MPxxx]`. The common ones:

```toml
[tool.mcpolish.MP010]
allow = ["search", "query"]            # whitelist generic names you defend
extra = ["dispatch"]                    # add more words to the generic list

[tool.mcpolish.MP011]
namespace = "memnex"                    # override server namespace for MP011

[tool.mcpolish.MP013]
min_collisions = 3                      # raise the bar for "collision"

[tool.mcpolish.MP014]
style = "snake"                         # "snake", "camel", or "auto"

[tool.mcpolish.MP020]
min_chars = 80                          # raise the minimum description length

[tool.mcpolish.MP021]
max_chars = 2000                        # raise the maximum description length

[tool.mcpolish.MP022]
required_examples = 1                   # how many examples per param

[tool.mcpolish.MP024]
max_ratio = 0.30                        # all-caps tokens as a fraction
min_tokens = 8                          # only fire when description is long enough
allow = ["MCP", "JSON"]                 # extra whitelisted acronyms
```

Each rule's documentation page lists its full set of knobs.

## Score weights

The score is computed by category. Adjust the weights:

```toml
[tool.mcpolish.score_weights]
schema = 0.10
naming = 0.30
description = 0.30
consistency = 0.20
security = 0.10
```

The values are normalised so they do not need to sum to 1. See [How scoring works](../concepts/how-scoring-works.md).

## Full example

```toml
[project]
name = "my_mcp_server"
version = "0.3.0"

[tool.mcpolish]
target-version = "2025-11"
select = ["MP001-MP041"]
ignore = ["MP025"]
registry = "official"

[tool.mcpolish.MP010]
allow = ["search"]

[tool.mcpolish.MP020]
min_chars = 80

[tool.mcpolish.score_weights]
security = 0.20
schema = 0.20
naming = 0.30
description = 0.20
consistency = 0.10
```

## How CLI flags interact with the file

The CLI does not merge with the file; it replaces. If you pass `--select MP010`, the file's `select` is ignored for that run. If you pass `--ignore MP025`, the file's `ignore` is ignored.

`--llm` works the other way: if you pass `--llm provider:model`, you override the file. If you pass `--llm` with no spec, the file's `llm` setting is read.

## Common variations

### Different config per environment

Keep the production config in `pyproject.toml`. Add an environment-specific override using a wrapper shell script:

```bash
# strict-lint.sh
mcpolish lint . --select MP001-MP010 --fail-on warn
```

mcpolish itself does not read multiple config files.

### Sharing config across projects

The standard answer is a private Python package that emits a `pyproject.toml` fragment. mcpolish does not have an `extends` mechanism in v1.

## Troubleshooting

**`config error: invalid pyproject.toml`.** Run `python -c "import tomllib; tomllib.loads(open('pyproject.toml').read())"` to see the exact parse error.

**`invalid [tool.mcpolish] section`.** A field has the wrong type. For example, `select = "MP010"` instead of `select = ["MP010"]`. The error message names the field.

**My setting did not take effect.** Check that `mcpolish` is reading the right file:

```
mcpolish doctor
```

Doctor prints the resolved config.

## See also

- [CLI reference](cli-reference.md)
- [How scoring works](../concepts/how-scoring-works.md)
- [Rules index](../rules/index.md)
