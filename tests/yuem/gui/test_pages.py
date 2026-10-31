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


@pytest.mark.parametrize("key", sorted(MODULE_SPECS))
def test_page_builds_in_chinese(qtbot: Any, state: StudioState, key: str) -> None:
    """Translated templates are formatted as each page builds; a broken one raises here."""
    from PySide6.QtWidgets import QApplication

    from PyHydroGeophysX.qt_apps import i18n

    app = QApplication.instance()
    i18n.install_translator(app, "zh_CN")
    try:
        errors: list[str] = []
        page = build_module(
            key, state, lambda message, level="info": errors.append(message) if level == "error" else None
        )
        qtbot.addWidget(page)
        assert not isinstance(page, PlaceholderModule), errors
        page.stop_workers(wait_ms=5000)
    finally:
        i18n.install_translator(app, "en")


def test_the_studio_starts_without_font_warnings(tmp_path: Path) -> None:
    import os
    import subprocess
    import sys

    env = {
        **os.environ,
        "QT_QPA_PLATFORM": "offscreen",
        "PHGX_PROJECT_DIR": str(tmp_path / "project"),
        "PHGX_LOG_DIR": str(tmp_path / "logs"),
    }
    done = subprocess.run(
        [sys.executable, "-m", "PyHydroGeophysX.qt_apps.launcher", "--self-test"],
        capture_output=True,
        text=True,
        env=env,
        timeout=120,
        check=False,
    )
    assert done.returncode == 0, done.stderr[-2000:]
    assert "missing font family" not in done.stderr


def test_parameters_name_their_standard(qtbot: Any, state: StudioState) -> None:
    from PyHydroGeophysX.qt_apps.standards import ANNOTATIONS, STANDARDS

    for key, controls in ANNOTATIONS.items():
        page = build_module(key, state, lambda *_args: None)
        qtbot.addWidget(page)
        for attribute, (codes, _zh, _en) in controls.items():
            assert all(code in STANDARDS for code in codes)
            widget = getattr(page, attribute)
            assert f"Standard: {codes[0]}" in widget.toolTip(), (key, attribute)
        page.stop_workers(wait_ms=5000)
