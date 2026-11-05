"""The Studio's main toolbar, as a part of the main window (plan D4).

Three zones: the Project on the left; the plot tools of the page on screen in
the middle; the page's run button for the step on screen, what is running,
the assistant's panel and Quit on the right. Every command on it is also in a
menu, or is the page's own button repeated. A page says what applies through
:meth:`BaseModule.toolbar_view_tools` and :attr:`BaseModule.toolbar_run_attrs`.
"""

from __future__ import annotations

import time

import pyqtgraph as pg
import shiboken6
from PySide6.QtCore import QCoreApplication, QTimer, Qt
from PySide6.QtWidgets import QDockWidget, QHBoxLayout, QLabel, QMenu, QSizePolicy, QToolBar, QToolButton, QWidget

from PyHydroGeophysX.agents import assistants as assistant_registry
from PyHydroGeophysX.qt_apps import i18n, theme
from PyHydroGeophysX.qt_apps.modules.base import GENERIC_ACTIVITY
from PyHydroGeophysX.qt_apps.widgets.array_viewer import ArrayViewer


#: Longest activity phrase the status bar shows; the label never wraps, and a
#: long one would push the output folder off the bar.
ACTIVITY_CHARS = 70


def page_activity(page) -> str:
    """What ``page`` is busy with ("" when idle), shortened for the status bar."""
    try:
        phrase = str(page.activity() or "") if hasattr(page, "activity") else ""
    except RuntimeError:                  # a page Qt has already destroyed
        return ""
    return phrase if len(phrase) <= ACTIVITY_CHARS else phrase[:ACTIVITY_CHARS - 1] + "…"


def elapsed_since(page, now: float) -> str:
    """How long ``page`` has been busy, in words: "45 s", "3 min 05 s", "1 h 02 min"."""
    since = page.busy_since() if hasattr(page, "busy_since") else None
    if since is None:
        return ""
    seconds = max(0, int(now - since))
    if seconds < 60:
        return f"{seconds} s"
    if seconds < 3600:
        return f"{seconds // 60} min {seconds % 60:02d} s"
    return f"{seconds // 3600} h {seconds % 3600 // 60:02d} min"


def dock_toggle_title(dock: QDockWidget) -> QWidget:
    """The dock caption as the button that shows and hides that dock.

    The same action is on the main toolbar. Closing the dock hides this
    title with it, and the toolbar button is what opens the dock again.
    """
    bar = QWidget(dock)
    bar.setObjectName("dockToggleTitle")
    bar.setAttribute(Qt.WA_StyledBackground, True)
    layout = QHBoxLayout(bar)
    layout.setContentsMargins(6, 2, 6, 2)
    layout.setSpacing(0)
    button = QToolButton(bar)
    button.setObjectName("dockToggleTitleButton")
    button.setDefaultAction(dock.toggleViewAction())
    button.setToolButtonStyle(Qt.ToolButtonTextOnly)
    button.setAutoRaise(True)
    button.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
    layout.addWidget(button, 0, Qt.AlignVCenter)
    layout.addStretch(1)
    return bar


class MainToolbar:
    """Mixin of the main window: builds and keeps the main toolbar."""

    def _build_toolbar(self) -> None:
        from PySide6.QtCore import QSize

        # Three zones: the Project on the left, the plot tools of the page in
        # the middle, what is running and the window controls on the right.
        # Icons only, each named by its tooltip; every command here is also in
        # a menu.
        toolbar = QToolBar("Main")
        toolbar.setObjectName("main_toolbar")
        toolbar.setMovable(False)
        toolbar.setToolButtonStyle(Qt.ToolButtonIconOnly)
        toolbar.setIconSize(QSize(18, 18))
        self.addToolBar(toolbar)
        self._main_toolbar = toolbar

        # Left: the navigator toggle sits beside the panel it opens, then the
        # Project and the commands on it. The toggle is also the left dock's
        # title button.
        project_toggle = self._tree_dock.toggleViewAction()
        project_toggle.setIcon(theme.icon("mdi.page-layout-sidebar-left"))
        project_toggle.setToolTip(QCoreApplication.translate("PHGX", "Show or hide the project panel"))
        project_toggle.setStatusTip(QCoreApplication.translate("PHGX", "Show or hide the project panel"))
        toolbar.addAction(project_toggle)
        self._project_button = QToolButton()
        self._project_button.setObjectName("toolbarProject")
        self._project_button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self._project_button.setIcon(theme.icon("fa5s.folder-open"))
        self._project_button.setPopupMode(QToolButton.InstantPopup)
        project_menu = QMenu(self._project_button)  # i18n: as written
        project_menu.addActions([self._new_action, self._open_action, self._import_action])
        project_menu.addSeparator()
        project_menu.addActions([self._save_action, self._discard_action])
        project_menu.addSeparator()
        project_menu.addAction(self._export_action)
        self._project_button.setMenu(project_menu)
        toolbar.addWidget(self._project_button)
        # Runs are not recorded in the Project until saved, so how many are
        # waiting has to be visible without opening a menu.
        self._unsaved_label = QLabel()
        theme.set_tone(self._unsaved_label, "warn")
        toolbar.addWidget(self._unsaved_label)
        # "Save" adds the finished runs to the Project's history; the Streamlit
        # bridge commands stay in the File menu.
        self._save_button = self._add_action(
            toolbar, QCoreApplication.translate("PHGX", "Save Runs to Project"), self._save_runs,
            icon_name="fa5s.save")
        self._save_button.setToolTip(QCoreApplication.translate("PHGX", "Save Runs to Project (Ctrl+S)"))
        self._export_button = self._add_action(
            toolbar, QCoreApplication.translate("PHGX", "Export Results…"), self._export_results,
            icon_name="fa5s.file-export")
        self._export_button.setToolTip(QCoreApplication.translate("PHGX", "Export Results… (Ctrl+E)"))

        # Middle: the mouse tools of the page's plots. Pan is also what a
        # plain click-drag does, so there is no separate Select.
        toolbar.addWidget(self._toolbar_spacer())
        self._view_tool_separators = [toolbar.addSeparator()]
        pan = self._add_action(
            toolbar, QCoreApplication.translate("PHGX", "Pan"), lambda: self._set_mouse_mode(rect=False),
            icon_name="fa5s.arrows-alt")
        pan.setToolTip(QCoreApplication.translate("PHGX", "Pan: drag to move the plot"))
        zoom = self._add_action(
            toolbar, QCoreApplication.translate("PHGX", "Zoom"), lambda: self._set_mouse_mode(rect=True),
            icon_name="fa5s.search-plus")
        zoom.setToolTip(QCoreApplication.translate("PHGX", "Zoom: drag a box to zoom into it"))
        self._pick_action = self._add_action(
            toolbar, QCoreApplication.translate("PHGX", "Pick"), self._toggle_pick, checkable=True,
            icon_name="fa5s.crosshairs")
        self._pick_action.setToolTip(QCoreApplication.translate("PHGX", "Pick: click a section to place a marker"))
        self._view_tool_actions = [pan, zoom, self._pick_action]
        self._view_tool_separators.append(toolbar.addSeparator())
        toolbar.addWidget(self._toolbar_spacer())

        # Right: the page's run button for the step on screen, what is
        # running, the assistant's panel, and quitting.
        self._run_button = QToolButton()
        self._run_button.setObjectName("toolbarRun")
        self._run_button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self._run_button.setIcon(theme.icon("fa5s.play", color="#ffffff"))
        self._run_button.clicked.connect(self._click_page_run)
        self._run_widget = toolbar.addWidget(self._run_button)
        self._run_widget.setVisible(False)
        #: The page button the toolbar's Run repeats, or None.
        self._page_run_target = None
        self._watched_run_buttons: set = set()
        self._page_tools_pending = False
        self._activity_button = QToolButton()
        self._activity_button.setObjectName("toolbarActivity")
        self._activity_button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self._activity_button.setIcon(theme.icon("fa5s.circle-notch"))
        self._activity_button.clicked.connect(self._show_busy_page)
        self._activity_widget = toolbar.addWidget(self._activity_button)
        self._activity_widget.setVisible(False)
        assistant_toggle = self._properties_dock.toggleViewAction()
        assistant_toggle.setIcon(theme.icon("mdi.page-layout-sidebar-right"))
        assistant_toggle.setToolTip(QCoreApplication.translate("PHGX", "Show or hide the assistant panel"))
        assistant_toggle.setStatusTip(QCoreApplication.translate("PHGX", "Show or hide the assistant panel"))
        toolbar.addAction(assistant_toggle)
        toolbar.addSeparator()
        self._exit_action.setToolTip(QCoreApplication.translate("PHGX", "Quit the Studio (Ctrl+Q)"))
        toolbar.addAction(self._exit_action)
        self._sync_appearance_controls()
        theme.notifier().changed.connect(lambda _mode: self._sync_appearance_controls())

    @staticmethod
    def _toolbar_spacer() -> QWidget:
        spacer = QWidget()
        spacer.setObjectName("toolbarSpacer")
        spacer.setStyleSheet("#toolbarSpacer { background: transparent; }")
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        return spacer

    def _schedule_page_tools(self, *_args) -> None:
        """Refresh the page's toolbar tools once the event loop is free."""
        if not self._page_tools_pending:
            self._page_tools_pending = True
            QTimer.singleShot(0, self, self._refresh_page_tools)

    def _refresh_page_tools(self) -> None:
        """Show the plot tools and the Run button that apply to the page on screen."""
        self._page_tools_pending = False
        page = self._stack.currentWidget()
        focused = getattr(assistant_registry.active(), "focused_workspace", False)
        tools = frozenset()
        if not focused and hasattr(page, "toolbar_view_tools"):
            try:
                tools = page.toolbar_view_tools()
            except RuntimeError:  # a page Qt has already destroyed
                tools = frozenset()
        for action, tool in zip(self._view_tool_actions, ("pan", "zoom", "pick")):
            action.setVisible(tool in tools)
        for separator in self._view_tool_separators:
            separator.setVisible(bool(tools))
        if self._pick_action.isChecked() and "pick" not in tools:
            self._pick_action.setChecked(False)
            self._toggle_pick(False)

        buttons = tuple(page.toolbar_run_buttons()) if hasattr(page, "toolbar_run_buttons") else ()
        self._watched_run_buttons = {button for button in self._watched_run_buttons if shiboken6.isValid(button)}
        for button in buttons:
            if button not in self._watched_run_buttons:
                button.installEventFilter(self)
                self._watched_run_buttons.add(button)
        shown = [button for button in buttons if button.isVisible()]
        target = shown[0] if len(shown) == 1 else None
        self._page_run_target = target
        self._run_widget.setVisible(target is not None)
        if target is not None:
            self._run_button.setText(target.text())
            self._run_button.setEnabled(target.isEnabled())
            self._run_button.setToolTip(
                QCoreApplication.translate("PHGX", "{0} — the run button of the step on screen").format(target.text()))

    def _click_page_run(self) -> None:
        target = self._page_run_target
        if target is not None and target.isVisible() and target.isEnabled():
            target.click()

    def _busy_pages(self) -> list:
        """Pages with work in progress, the one on screen first."""
        current = self._stack.currentWidget()
        busy = [page for page in self._pages.values() if page_activity(page)]
        return sorted(busy, key=lambda page: page is not current)

    def _show_busy_page(self) -> None:
        """Go to the page whose run the toolbar names."""
        busy = self._busy_pages()
        if not busy:
            return
        key = next((key for key, page in self._pages.items() if page is busy[0]), None)
        if key is not None:
            self.show_module(key)

    def _refresh_activity_button(self) -> None:
        button = getattr(self, "_activity_button", None)
        if button is None:
            return
        busy = self._busy_pages()
        self._activity_widget.setVisible(bool(busy))
        if not busy:
            return
        page = busy[0]
        title = i18n.tr(getattr(page, "module_title", "") or "")
        elapsed = elapsed_since(page, time.monotonic())
        text = " · ".join(filter(None, [title, elapsed]))
        if len(busy) > 1:
            text += QCoreApplication.translate("PHGX", " (+{0})").format(len(busy) - 1)
        button.setText(text)  # i18n: as written
        doing = page_activity(page)
        button.setToolTip(
            (QCoreApplication.translate("PHGX", "Working…") if doing == GENERIC_ACTIVITY
             else QCoreApplication.translate("PHGX", "Working: {0}").format(i18n.tr(doing)))
            + "\n" + QCoreApplication.translate("PHGX", "Click to open the page."))

    # -- toolbar behavior ----------------------------------------------------
    def _array_viewers(self):
        page = self._current_page()
        return page.findChildren(ArrayViewer) if page is not None else []

    def _set_mouse_mode(self, rect: bool) -> None:
        page = self._current_page()
        if page is None:
            return
        mode = pg.ViewBox.RectMode if rect else pg.ViewBox.PanMode
        boxes = page.findChildren(pg.ViewBox)
        for vb in boxes:
            vb.setMouseMode(mode)
        if not boxes:
            self.log("No plot in the current module to change mouse mode.", "debug")

    def _toggle_pick(self, checked: bool) -> None:
        viewers = self._array_viewers()
        for av in viewers:
            av.set_pick_mode(checked)
        if not viewers:
            self.log("Pick mode is not applicable in this module.", "debug")
            self._pick_action.setChecked(False)


__all__ = ["ACTIVITY_CHARS", "MainToolbar", "dock_toggle_title", "elapsed_since", "page_activity"]
