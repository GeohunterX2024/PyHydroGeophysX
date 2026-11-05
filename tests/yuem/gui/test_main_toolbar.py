"""The main toolbar: three zones of existing commands, and Quit at the right end."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

pytest.importorskip("PySide6")
pytestmark = pytest.mark.gui


@pytest.fixture
def window(qtbot: Any, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Any:
    from PyHydroGeophysX.qt_apps.main_window import PyHydroGeophysXStudio

    monkeypatch.setenv("PHGX_PROJECT_DIR", str(tmp_path / "project"))
    monkeypatch.setenv("PYHYDROGEOPHYSX_OUTPUT_DIR", str(tmp_path / "project"))
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(PyHydroGeophysXStudio, "_restore_window_settings", lambda self: False)
    monkeypatch.setattr(PyHydroGeophysXStudio, "_save_window_settings", lambda self: None)
    monkeypatch.setattr("PyHydroGeophysX.qt_apps.main_window.prepare_workflow_process", lambda: None)
    studio = PyHydroGeophysXStudio()
    qtbot.addWidget(studio)
    return studio


def test_every_toolbar_command_is_also_in_a_menu(window: Any) -> None:
    menu_actions = set()
    for top in window.menuBar().actions():
        if top.menu() is not None:
            menu_actions.update(top.menu().actions())
    project_menu = window._project_button.menu().actions()
    assert all(action in menu_actions for action in project_menu if not action.isSeparator())
    assert window._save_button.isEnabled() == window._save_action.isEnabled()
    assert window._exit_action in menu_actions
    assert window._main_toolbar.actions()[-1] is window._exit_action
    texts = {action.text() for action in window._main_toolbar.actions()}
    assert not {"Select", "Delete", "Dark", "Light"} & texts


def test_the_project_button_names_the_project(window: Any) -> None:
    assert window._project_button.text() == window.state.project_name


def test_quit_closes_the_window(qtbot: Any, window: Any, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(type(window), "_resolve_unsaved_runs", lambda self, *a, **k: True)
    window.show()
    qtbot.waitExposed(window)
    window._exit_action.trigger()
    qtbot.waitUntil(lambda: not window.isVisible())


def _settle(qtbot: Any, window: Any) -> None:
    qtbot.waitUntil(lambda: not window._page_tools_pending)


def test_run_repeats_the_one_run_button_on_screen(qtbot: Any, window: Any) -> None:
    window.show()
    window.show_module("ert")
    _settle(qtbot, window)
    page = window._pages["ert"]
    assert window._run_widget.isVisible()
    assert window._run_button.text() == page._invert_btn.text()
    assert window._run_button.isEnabled() == page._invert_btn.isEnabled()
    page._show_run_buttons(True)
    qtbot.waitUntil(lambda: window._run_button.text() == page._tl_btn.text())
    page._tl_btn.setVisible(False)
    page._invert_btn.setVisible(False)
    qtbot.waitUntil(lambda: not window._run_widget.isVisible())


def test_run_clicks_the_page_button(qtbot: Any, window: Any) -> None:
    window.show()
    window.show_module("gravmag")
    _settle(qtbot, window)
    button = window._pages["gravmag"]._inv_btn
    button.clicked.disconnect()
    clicks: list[bool] = []
    button.clicked.connect(lambda *_: clicks.append(True))
    button.setEnabled(True)
    qtbot.waitUntil(lambda: window._run_button.isEnabled())
    window._run_button.click()
    assert clicks == [True]


def test_plot_tools_follow_the_page(qtbot: Any, window: Any) -> None:
    window.show()
    window.show_module("home")
    _settle(qtbot, window)
    assert not any(action.isVisible() for action in window._view_tool_actions)
    window.show_module("gravmag")
    _settle(qtbot, window)
    tools = window._pages["gravmag"].toolbar_view_tools()
    for action, tool in zip(window._view_tool_actions, ("pan", "zoom", "pick"), strict=True):
        assert action.isVisible() == (tool in tools)


def test_a_busy_page_is_named_in_the_toolbar(qtbot: Any, window: Any) -> None:
    window.show()
    page = window._stack.currentWidget()
    page.set_activity("Inverting")
    try:
        assert window._activity_widget.isVisible()
        assert "Inverting" in window._activity_button.toolTip()
    finally:
        page.set_activity("")
    assert not window._activity_widget.isVisible()
