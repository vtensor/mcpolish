"""SVG badge for `score >= N` README pins."""

from __future__ import annotations


def render_badge(score: int, *, label: str = "mcpolish") -> str:
    """Return a shields.io-style SVG. Self-contained, no network."""
    color = _color_for(score)
    label_w = 6 + len(label) * 7
    value = f"{score}/100"
    value_w = 6 + len(value) * 7
    total = label_w + value_w
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{total}" height="20" role="img" '
        f'aria-label="{label}: {value}">'
        f'<linearGradient id="s" x2="0" y2="100%">'
        f'<stop offset="0" stop-color="#bbb" stop-opacity=".1"/>'
        f'<stop offset="1" stop-opacity=".1"/></linearGradient>'
        f'<rect width="{total}" height="20" rx="3" fill="#555"/>'
        f'<rect x="{label_w}" width="{value_w}" height="20" rx="3" fill="{color}"/>'
        f'<rect width="{total}" height="20" rx="3" fill="url(#s)"/>'
        f'<g fill="#fff" text-anchor="middle" '
        f'font-family="Verdana,Geneva,sans-serif" font-size="11">'
        f'<text x="{label_w / 2}" y="14">{label}</text>'
        f'<text x="{label_w + value_w / 2}" y="14">{value}</text>'
        f'</g></svg>'
    )


def _color_for(score: int) -> str:
    if score >= 90:
        return "#4c1"  # green
    if score >= 75:
        return "#97CA00"  # light green
    if score >= 60:
        return "#dfb317"  # yellow
    if score >= 40:
        return "#fe7d37"  # orange
    return "#e05d44"  # red
