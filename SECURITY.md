# Security policy

## Supported versions

Only the latest minor release of mcpolish receives security updates. Older releases may receive backports for critical issues at the maintainers' discretion.

| Version | Supported |
|---|---|
| 0.1.x | yes |

## Reporting a vulnerability

If you find a security issue in mcpolish, please report it privately first. Do not open a public GitHub issue.

Email: **security@mcpolish.dev**

Include:

- A description of the vulnerability.
- Steps to reproduce, ideally with a minimal `.py` fixture or a sample command.
- The version of mcpolish you tested against (`mcpolish --version`).
- Your Python version and OS.
- Whether the issue is exploitable in a default configuration.

We will acknowledge your report within 72 hours, give you an initial assessment within 7 days, and aim to have a patched release ready within 30 days for critical issues.

## What counts as a security issue

The mcpolish core engine is a static linter that runs offline on local files. The realistic threat model is narrow. The following do count:

- A crafted source file that, when linted, causes arbitrary code execution. mcpolish reads source with `libcst` and `jsonschema`; both are non-evaluating parsers, but bugs happen.
- A crafted source file that causes mcpolish to read or write files outside the target path.
- A vulnerability in the optional `--llm` code paths that leaks data the user did not intend to send. mcpolish sends only tool names and descriptions to the configured provider; sending anything else would be a security bug.
- A vulnerability in the GitHub Action wrapper (`action.yml`) that could allow log injection, secret leakage, or arbitrary command execution.

The following are not security issues:

- A false positive or false negative in any rule. Open a regular issue.
- A rule that flags a tool description you believe is fine. Open a regular issue or use the [silencing-false-positives](docs/scenarios/silencing-false-positives.md) page.
- Performance regressions. Open a regular issue.

## Out of scope

mcpolish is a linter, not a runtime sandbox or a security scanner for MCP servers in production. The rules MP040 and MP041 detect known prompt-injection patterns in tool descriptions, but mcpolish does not claim to catch every attack. For runtime security analysis of MCP traffic, see [mcp-scan](https://github.com/invariantlabs-ai/mcp-scan).

## Disclosure

Once a fix is ready, we will:

1. Publish a patched release on PyPI.
2. Open a public GitHub Security Advisory describing the issue and the fix.
3. Credit the reporter unless they prefer to remain anonymous.
4. Add a regression test to the suite so the same issue cannot recur silently.

Thank you for helping keep mcpolish and its users safe.
