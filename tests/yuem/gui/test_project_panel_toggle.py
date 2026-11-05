"""The project navigator shows and hides from a button, as the assistant does."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

pytest.importorskip("PySide6")
pytestmark = pytest.mark.gui

from PySide6.QtCore import Qt  # noqa: E402
from PySide6.QtWidgets import QToolButton  # noqa: E402

from PyHydroGeophysX.qt_apps.state import StudioState  # noqa: E402


@pytest.fixture
def state(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> StudioState:
    # Results go to a throwaway project, never the user's ~/.pyhydrogeophysx.
    monkeypatch.setenv("PHGX_PROJECT_DIR", str(tmp_path / "project"))
    monkeypatch.setenv("PYHYDROGEOPHYSX_OUTPUT_DIR", str(tmp_path / "project"))
    monkeypatch.chdir(tmp_path)
    return StudioState.from_context(None)


def test_the_project_button_shows_and_hides_the_left_panel(
    qtbot: Any, state: StudioState, monkeypatch: pytest.MonkeyPatch
) -> None:
    from PySide6.QtWidgets import QApplication

    from PyHydroGeophysX.qt_apps import i18n
    from PyHydroGeophysX.qt_apps.main_window import PyHydroGeophysXStudio

    del state
    monkeypatch.setattr(PyHydroGeophysXStudio, "_restore_window_settings", lambda self: False)
    monkeypatch.setattr(PyHydroGeophysXStudio, "_save_window_settings", lambda self: None)
    monkeypatch.setattr("PyHydroGeophysX.qt_apps.main_window.prepare_workflow_process", lambda: None)
    app = QApplication.instance()
    assert app is not None
    i18n.install_translator(app, "zh_CN")
    try:
        window = PyHydroGeophysXStudio()
        qtbot.addWidget(window)
        toggle = window._tree_dock.toggleViewAction()
        assert toggle.text() == "工程"
        assert toggle.toolTip() == "显示或隐藏左侧工程区"
        actions = window._main_toolbar.actions()
        assert actions[0] is toggle
        assistant = window._properties_dock.toggleViewAction()
        assert assistant.text() == "助手"
        # The assistant toggle sits at the right end, just before Quit.
        assert actions.index(assistant) > actions.index(window._pick_action)
        assert actions[-1] is window._exit_action
        title = window._tree_dock.titleBarWidget()
        assert title is not None
        button = title.findChild(QToolButton)
        assert button is not None
        assert button.defaultAction() is toggle

        window.resize(1280, 800)
        window.show()
        qtbot.waitExposed(window)
        qtbot.waitUntil(lambda: window._tree_dock.isVisible() and toggle.isChecked())
        before = window.centralWidget().width()
        qtbot.mouseClick(button, Qt.LeftButton)
        qtbot.waitUntil(lambda: not window._tree_dock.isVisible())
        assert not toggle.isChecked()
        qtbot.waitUntil(lambda: window.centralWidget().width() > before + 80)
        hidden_width = window.centralWidget().width()
        toggle.trigger()
        qtbot.waitUntil(lambda: window._tree_dock.isVisible() and toggle.isChecked())
        assert window.centralWidget().width() < hidden_width
    finally:
        i18n.install_translator(app, "en")
