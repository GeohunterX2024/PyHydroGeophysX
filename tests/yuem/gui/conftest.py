"""Qt message guard for the GUI tier.

A QThread or QProcess destroyed while still running is a shutdown bug (a crash
on exit at best, an orphaned child at worst); any test during which Qt reports
one fails.
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest

FATAL_MARKERS = ("QThread: Destroyed while thread", "QProcess: Destroyed while process")


@pytest.fixture(autouse=True, scope="session")
def no_assistant_cli_download() -> Iterator[None]:
    """The assistant panel sets up its default CLI when it is built and downloads
    one that is missing (Codex, some 270 MB). A test run must not reach the
    network, and a download still running when the interpreter exits destroys
    a running QThread, which aborts the process (findings F-17). A configured
    path that does not exist makes the setup fail at once instead."""
    missing = str(Path(__file__).with_name("no-such-cli"))
    with pytest.MonkeyPatch.context() as patch:
        patch.setenv("PHGX_CODEX_CLI", missing)
        patch.setenv("PHGX_CLAUDE_CLI", missing)
        yield


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
