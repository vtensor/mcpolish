# What is MCP?

> Who this page is for: someone who has heard the term "MCP server" but is not yet sure what it means.

## What you will learn

- What MCP stands for and why it exists.
- What an MCP server is, in concrete terms.
- Who uses MCP today.
- Why tool description quality matters for any MCP server.

## Background

MCP stands for [Model Context Protocol](glossary.md#mcp). It is an open protocol that lets AI agents call functions provided by separate small programs.

Anthropic announced MCP in November 2024. By the end of 2025, OpenAI, Google DeepMind, Cursor, Windsurf, Continue, Zed, Replit, Cline, VS Code Copilot, Claude Code, and Claude Desktop had all added MCP support. In December 2025, the Model Context Protocol was donated to the Linux Foundation under the Agentic AI Foundation.

By early 2026 there were over 23,000 public MCP servers on Glama, over 20,000 on MCP.so, and over 12,000 on Smithery.

## How an MCP setup looks in practice

There are three actors:

1. The **host**. The application the user talks to: Claude Desktop, Cursor, etc.
2. The **agent** inside the host. The LLM that decides what to do.
3. One or more **MCP servers**. Small programs that expose tools.

When the user types a question, the host shows the agent the list of available tools. Each tool has a name, a description, and an input schema. The agent picks a tool by reading those three things. The host calls the chosen tool through the MCP protocol. The result comes back to the agent. The agent assembles the final answer.

## What an MCP server is

An MCP server is a small program. You write it. It runs on the user's machine (or, less commonly, over the network). It exposes one or more tools.

A "tool" is just a function with three pieces of metadata attached:

- A name. Like `get_weather` or `search_memories`.
- A description. A short English paragraph that tells the agent when to call it.
- An input schema. A [JSON Schema](glossary.md#json-schema) describing what arguments the tool takes.

In Python, the most common way to write an MCP server is with FastMCP:

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("weather")


@mcp.tool()
def get_weather(city: str) -> dict:
    """Use this when the user asks for the current weather at a known city.

    Args:
        city: City name. Example: "Paris".

    Returns: a dict with `temp` (degrees Celsius) and `conditions` (string).
    """
    return {"temp": 19, "conditions": "cloudy"}
```

That whole file is the MCP server. Six lines of useful code. The agent will see exactly one tool, called `get_weather`, with the description and a single parameter named `city`.

## Why the description matters more than you might think

In tests across 10,831 public MCP servers published in February 2026 (Wang et al., arXiv:2602.18914), bad descriptions caused agents to pick the wrong tool **52 percentage points** more often. The same paper catalogued 18 specific patterns ("smells") that lead to wrong-tool selection.

The description is the agent's only source of truth at decision time. Your function body is invisible. Your parameter types are visible but limited. The English text you wrote is what the agent reads. If that text is vague, generic, or misleading, the agent gets it wrong.

This is what mcpolish exists to check.

## Common variations

### TypeScript MCP servers

You can also write an MCP server in TypeScript, Go, Rust, or any language. The protocol is language-neutral. mcpolish currently lints Python only. TypeScript support is on the roadmap.

### Lower-level Python API

Instead of FastMCP, you can use the lower-level `Server` plus `Tool(...)` constructor:

```python
from mcp import Server, Tool

server = Server("weather")

TOOLS = [
    Tool(
        name="get_weather",
        description="Use this when the user asks for...",
        inputSchema={
            "type": "object",
            "properties": {"city": {"type": "string"}},
            "required": ["city"],
        },
    ),
]
```

mcpolish recognises both styles.

## See also

- [What is a linter](what-is-a-linter.md)
- [What mcpolish checks](what-mcpolish-checks.md)
- [Glossary](glossary.md)
