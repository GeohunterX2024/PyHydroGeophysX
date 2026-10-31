"""Every Studio page builds offscreen and shuts down cleanly (plan M1.2)."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

import pytest

pytest.importorskip("PySide6")
pytestmark = pytest.mark.gui

from PyHydroGeophysX.qt_apps.modules import MODULE_SPECS, PlaceholderModule, build_module  # noqa: E402
from PyHydroGeophysX.qt_apps.state import StudioState  # noqa: E402


@pytest.fixture
def state(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> StudioState:
    # Results go to a throwaway project, never the user's ~/.pyhydrogeophysx.
    monkeypatch.setenv("PHGX_PROJECT_DIR", str(tmp_path / "project"))
    monkeypatch.chdir(tmp_path)
    return StudioState.from_context(None)


@pytest.mark.parametrize("key", sorted(MODULE_SPECS))
def test_page_builds_and_stops(qtbot: Any, state: StudioState, key: str) -> None:
    messages: list[tuple[str, str]] = []

    def log(message: str, level: str = "info") -> None:
        messages.append((level, str(message)))

    page = build_module(key, state, log)
    qtbot.addWidget(page)
    errors = [text for level, text in messages if level == "error"]
    assert not isinstance(page, PlaceholderModule), errors
    description = page.agent_describe()
    assert isinstance(description, dict)
    started = time.monotonic()
    page.stop_workers(wait_ms=5000)
    assert time.monotonic() - started < 5.5


def test_main_window_offers_the_environment_check(qtbot: Any, state: StudioState) -> None:
    from PyHydroGeophysX.qt_apps.main_window import PyHydroGeophysXStudio

    window = PyHydroGeophysXStudio()
    qtbot.addWidget(window)
    help_menu = next(
        action.menu() for action in window.menuBar().actions() if action.text().replace("&", "") == "Help"
    )
    labels = [action.text() for action in help_menu.actions()]
    assert "Environment Check…" in labels
