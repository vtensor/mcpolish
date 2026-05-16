"""Reporter Protocol + shared payload."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterable, Protocol, TextIO

from mcpolish._version import __version__
from mcpolish.types import Diagnostic


@dataclass
class ReportPayload:
    diagnostics: tuple[Diagnostic, ...]
    score: int
    server_name: str
    files_scanned: int
    tools_found: int
    version: str = __version__
    scanned_at: str = ""

    def __post_init__(self) -> None:
        if not self.scanned_at:
            self.scanned_at = (
                datetime.now(timezone.utc).isoformat(timespec="seconds")
            )


class Reporter(Protocol):
    name: str

    def emit(self, payload: ReportPayload, out: TextIO) -> None: ...


def diagnostics_for_file(
    diagnostics: Iterable[Diagnostic],
) -> dict[str, list[Diagnostic]]:
    grouped: dict[str, list[Diagnostic]] = {}
    for d in diagnostics:
        grouped.setdefault(d.file, []).append(d)
    return grouped
