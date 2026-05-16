"""Helpers with no MCP tools. mcpolish should walk past this file and find
nothing to lint here. It exists to confirm that non-tool files do not raise."""


def slugify(text: str) -> str:
    return text.strip().lower().replace(" ", "-")


def format_size(n: int) -> str:
    if n >= 1024:
        return f"{n / 1024:.1f} KB"
    return f"{n} B"
