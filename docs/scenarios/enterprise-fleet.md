# Enterprise fleets

> Who this page is for: someone running mcpolish across many internal MCP servers at a company.

## What you will learn

- How to share rules and config across teams.
- How to roll mcpolish out gradually.
- How to aggregate scores across servers.

## Background

A platform team in a company often hosts an internal MCP server registry: 10 to 50 servers, written by different teams, all running inside the company's network. Quality varies; descriptions written by different teams drift apart. mcpolish gives a uniform standard.

This page covers the operational side: rollout, aggregation, and governance. The technical side is the same as a single project.

## Step by step

### 1. Pick a baseline config

Start with the mcpolish defaults plus one override:

```toml
[tool.mcpolish]
# Internal-only: skip cross-server collision checks. Our agents never share
# sessions with public servers.
ignore = ["MP013"]
```

This is a sensible starting point for internal-only fleets.

### 2. Distribute the config

Three ways:

| Method | When |
|---|---|
| Copy and paste into each repo | Smallest cost. Easy to drift. |
| Cookiecutter / template | One-time copy at server creation. Drift is on the team to manage. |
| Internal Python package that emits the config | Highest investment. Teams `pip install mcpolish-rules-company` and a script writes the section. |

For a fleet of 10 servers, copy and paste is fine. For 100, invest in the template or the internal package.

### 3. Adopt server by server

Pick the team most enthusiastic about quality. Run mcpolish on their server. Walk them through fixing the diagnostics. Get them to 90+.

Add their server to your "lit up" list. Use them as the example for the next team. Do not try to onboard everyone at once; the social dynamic matters as much as the tooling.

### 4. Aggregate scores across servers

Each server runs `mcpolish lint . --format json` in CI. Write the JSON to a central S3 bucket or a database. A simple cron pulls the latest, computes averages, and posts a dashboard.

You only need three numbers per server per day:

- The score.
- The error count.
- The rule that fires most.

A spreadsheet does this. So does a small Streamlit app.

### 5. Track the trend

The interesting question is not "what is the score today" but "is the score going up or down over time". Plot:

- Score per server per week.
- Error count per server per week.
- New diagnostics introduced this week.

A regression on any line is a conversation with the team that owns that server.

## Governance patterns

### Tier the gate

| Tier | Gate | Who |
|---|---|---|
| Strict | `--fail-on error` | Production servers, customer-facing agents. |
| Warn | `--fail-on warn` | Internal tools, finance, ops. |
| Inform | `--fail-on never` | Experimental, alpha. |

Each server chooses a tier in its `pyproject.toml`:

```toml
[tool.mcpolish]
# strict tier
```

Document the tiers in your internal playbook.

### Allow per-team overrides

A central config is rarely a perfect fit for every team. Allow each repo to add its own overrides on top of the company defaults:

```toml
# inherited defaults: ignore = ["MP013"]
# local override:
[tool.mcpolish]
ignore = ["MP013", "MP025"]   # team-specific
```

mcpolish has no native `extends` mechanism in v1, so this is copy-paste.

### Publish a private registry snapshot

The bundled cross-server snapshot ships in mcpolish. To check against your internal servers' tool names instead, you can:

1. Scrape your internal MCP registry.
2. Build a JSON file in the same shape as `src/mcpolish/registry/data/snapshot.v1.json`.
3. Replace the bundled file (vendored install) or wait for the SaaS fetcher (planned).

Internal collision checking is a high-value upgrade once you have 10+ servers.

## How fast is mcpolish on a fleet

For 50 servers averaging 8 tools each, running 50 parallel CI jobs takes seconds. The bottleneck is git checkout, not mcpolish itself.

If you batch into one job (`for server in ...; do mcpolish lint $server; done`), expect 30 to 90 seconds total for a 50-server fleet.

## Common variations

### Self-hosted runners

The mcpolish GitHub Action runs unchanged on self-hosted runners. The only requirement is Python 3.11+ available in the runner's PATH.

### Air-gapped network

mcpolish is offline by default. The only network calls are optional `--llm` rules. If your fleet is air-gapped:

1. Install mcpolish in a private PyPI mirror.
2. Pin a release tag.
3. Do not pass `--llm`.

### Compliance reporting

Some teams need to report linter coverage to compliance. Run mcpolish in CI and store the JSON output as an artifact. The artifact is the audit trail.

## Troubleshooting

**Scores swing between releases of mcpolish.** Pin the version across the fleet. A single team upgrading first to a release with new rules will see a sudden score drop that is not really a regression. Coordinate version bumps.

**One team's MP010 allowlist starts shrinking everyone else's.** Each `pyproject.toml` is per-project. A team's allowlist only affects their server. If you see drift, you may have a shared config file that should not be shared.

## See also

- [Huge monorepo](huge-monorepo.md)
- [Customising rules](customizing-rules.md)
- [Configuration](../usage/configuration.md)
