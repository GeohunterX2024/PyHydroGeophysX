"""Qt message guard for the GUI tier.

A QThread or QProcess destroyed while still running is a shutdown bug (a crash
on exit at best, an orphaned child at worst); any test during which Qt reports
one fails.
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import pytest

FATAL_MARKERS = ("QThread: Destroyed while thread", "QProcess: Destroyed while process")


@pytest.fixture(autouse=True)
def qt_lifecycle_guard() -> Iterator[None]:
    from PySide6.QtCore import qInstallMessageHandler

    seen: list[str] = []

    def handler(mode: Any, context: Any, message: str) -> None:
        if any(marker in message for marker in FATAL_MARKERS):
            seen.append(message)

    previous = qInstallMessageHandler(handler)
    try:
        yield
    finally:
        qInstallMessageHandler(previous)
    assert not seen, seen
