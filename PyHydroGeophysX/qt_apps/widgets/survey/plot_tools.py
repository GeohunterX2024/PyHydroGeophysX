"""Mouse tools on a 2-D survey plot: a toolbar at its top left, guarded zooming and a cursor readout.

:class:`NavigationViewBox` has three left-button modes. *Zoom* (the default)
zooms into a box dragged to the right (top left to bottom right) and goes back
to the full view when the box is dragged to the left (bottom right to top
left); a drag shorter than a few pixels does nothing, so a stray click cannot
move the plot. *Pan* drags the plot, *Select* reports the box for selection.
The middle button pans in every mode, the right button does nothing, and the
wheel zooms only when switched on in the toolbar. Every zoom, pan and reset is
remembered, so the toolbar can step back and forward through the views.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from typing import Any

import pyqtgraph as pg
from PySide6.QtCore import QCoreApplication, QEvent, QObject, QPointF, QRectF, Qt, Signal
from PySide6.QtWidgets import QButtonGroup, QFrame, QHBoxLayout, QLabel, QToolButton

from PyHydroGeophysX.qt_apps import theme
from PyHydroGeophysX.qt_apps.widgets.survey.common import SelectViewBox
from PyHydroGeophysX.visualization import axis_units

#: Left-button modes.
MODES = ("zoom", "pan", "select")
#: A drag shorter than this (pixels, both ways) is taken for a click and changes nothing.
MIN_DRAG = 8
#: Views remembered for stepping back.
HISTORY = 50
#: Wheel steps closer together than this (seconds) are one view in the history.
_WHEEL_GAP = 0.6
#: Zoom of one press of the toolbar's zoom in / zoom out.
STEP = 1.25


class NavigationViewBox(SelectViewBox):
    """A view box with zoom, pan and select modes, guarded zooming and a view history."""

    #: The left-button mode changed (``zoom``, ``pan`` or ``select``).
    sigModeChanged = Signal(str)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._mode = "zoom"
        self._wheel = False
        self._back: list[QRectF] = []
        self._forward: list[QRectF] = []
        self._last_wheel = 0.0
        #: What "full view" means for the plot (fixed axis ranges, or fitting the data).
        self.home_action: Callable[[], None] | None = None
        pg.ViewBox.setMouseMode(self, pg.ViewBox.RectMode)

    # -- modes --------------------------------------------------------------
    def mode(self) -> str:
        return self._mode

    def set_mode(self, mode: str) -> None:
        if mode not in MODES:
            return
        self._mode = mode
        self.set_selecting(mode == "select")
        pg.ViewBox.setMouseMode(self, pg.ViewBox.PanMode if mode == "pan" else pg.ViewBox.RectMode)
        self.sigModeChanged.emit(mode)

    def setMouseMode(self, mode: Any) -> None:
        """The Studio toolbar's Pan and Zoom (they set every view box of the page)."""
        if not hasattr(self, "_back"):
            pg.ViewBox.setMouseMode(self, mode)
            return
        self.set_mode("pan" if mode == pg.ViewBox.PanMode else "zoom")

    def set_selecting(self, on: bool) -> None:
        super().set_selecting(on)
        if hasattr(self, "_mode") and on and self._mode != "select":
            self.set_mode("select")
        elif hasattr(self, "_mode") and not on and self._mode == "select":
            self.set_mode("zoom")

    def wheel_zoom(self) -> bool:
        return self._wheel

    def set_wheel_zoom(self, on: bool) -> None:
        self._wheel = bool(on)

    # -- views --------------------------------------------------------------
    def remember(self) -> None:
        """Keep the view on screen for :meth:`back` (before changing it)."""
        self._back.append(QRectF(self.viewRect()))
        del self._back[:-HISTORY]
        self._forward.clear()

    def can_go_back(self) -> bool:
        return bool(self._back)

    def can_go_forward(self) -> bool:
        return bool(self._forward)

    def back(self) -> None:
        if self._back:
            self._forward.append(QRectF(self.viewRect()))
            self.setRange(rect=self._back.pop(), padding=0.0)

    def forward(self) -> None:
        if self._forward:
            self._back.append(QRectF(self.viewRect()))
            self.setRange(rect=self._forward.pop(), padding=0.0)

    def home(self) -> None:
        """The full view: the plot's fixed ranges if it has them, else all of its data."""
        self.remember()
        if self.home_action is not None:
            self.home_action()
        else:
            self.autoRange()

    def zoom_by(self, factor: float) -> None:
        """Zoom about the centre of the view (``factor`` < 1 zooms in)."""
        self.remember()
        self.scaleBy((factor, factor))

    # -- mouse --------------------------------------------------------------
    def mouseDragEvent(self, ev: Any, axis: Any = None) -> None:
        button = ev.button()
        if button == Qt.MouseButton.RightButton:
            ev.ignore()
            return
        if button == Qt.MouseButton.MiddleButton or axis is not None or self._mode == "pan":
            if ev.isStart():
                self.remember()
            saved = self.state["mouseMode"]
            self.state["mouseMode"] = pg.ViewBox.PanMode
            try:
                pg.ViewBox.mouseDragEvent(self, ev, axis)
            finally:
                self.state["mouseMode"] = saved
            return
        if self._mode == "select":
            super().mouseDragEvent(ev, axis)
            return
        ev.accept()
        start, end = QPointF(ev.buttonDownPos()), QPointF(ev.pos())
        if not ev.isFinish():
            self.updateScaleBox(start, end)
            return
        self.rbScaleBox.hide()
        if abs(end.x() - start.x()) < MIN_DRAG and abs(end.y() - start.y()) < MIN_DRAG:
            return
        if end.x() < start.x():
            self.home()
            return
        box = self.childGroup.mapRectFromParent(QRectF(start, end).normalized())
        self.remember()
        self.showAxRect(box)

    def mouseClickEvent(self, ev: Any) -> None:
        if ev.button() == Qt.MouseButton.LeftButton and ev.double():
            ev.accept()
            self.home()
            return
        super().mouseClickEvent(ev)

    def wheelEvent(self, ev: Any, axis: Any = None) -> None:
        if not self._wheel:
            ev.ignore()
            return
        now = time.monotonic()
        if now - self._last_wheel > _WHEEL_GAP:
            self.remember()
        self._last_wheel = now
        super().wheelEvent(ev, axis)


def make_navigable_plot(parent: Any = None) -> tuple[pg.PlotWidget, NavigationViewBox]:
    """A plot widget on a :class:`NavigationViewBox`, with a light grid and no context menu."""
    box = NavigationViewBox()
    plot = pg.PlotWidget(parent=parent, viewBox=box)
    plot.showGrid(x=True, y=True, alpha=0.2)
    plot.setMenuEnabled(False)
    return plot, box


#: Toolbar buttons: key, icon, tooltip (English source text). Modes first.
_MODE_BUTTONS = (
    (
        "zoom",
        "mdi.magnify-scan",
        "Zoom: drag a box right (top left to bottom right) to zoom in, "
        "left (bottom right to top left) to show everything",
    ),
    ("pan", "fa5s.arrows-alt", "Pan: drag to move the plot (the middle button pans in every mode)"),
    ("select", "mdi.selection-drag", "Select: drag a box to select the points inside it"),
)


class PlotToolbar(QFrame):
    """The mouse tools of one plot, floating at the top left of its plotting area."""

    #: The plot asks to fill the space of the views beside it (True) or to share it again.
    maximizeToggled = Signal(bool)

    def __init__(
        self,
        plot: pg.PlotWidget,
        view: NavigationViewBox,
        *,
        axis_names: tuple[str, str] = ("x", "y"),
        can_select: bool = True,
    ) -> None:
        super().__init__(plot)
        self.setObjectName("surveyPlotTools")
        self.setStyleSheet(
            "QFrame#surveyPlotTools { background: rgba(241, 245, 249, 225);"
            " border: 1px solid rgba(100, 116, 139, 110); border-radius: 5px; }"
            "QFrame#surveyPlotTools QToolButton { border: none; border-radius: 3px; padding: 2px;"
            " background: transparent; }"
            "QFrame#surveyPlotTools QToolButton:hover { background: rgba(37, 99, 235, 40); }"
            "QFrame#surveyPlotTools QToolButton:checked { background: rgba(37, 99, 235, 80); }"
            "QFrame#surveyPlotToolsRule { background: rgba(100, 116, 139, 110); }"
        )
        self._plot = plot
        self._view = view
        self._axis_names = axis_names
        row = QHBoxLayout(self)
        row.setContentsMargins(3, 2, 3, 2)
        row.setSpacing(1)
        self._modes = QButtonGroup(self)
        self._modes.setExclusive(True)
        self.buttons: dict[str, QToolButton] = {}
        for key, icon, tip in _MODE_BUTTONS:
            if key == "select" and not can_select:
                continue
            button = self._tool(key, icon, QCoreApplication.translate("PHGX", tip), checkable=True)
            self._modes.addButton(button)
            button.toggled.connect(lambda on, k=key: on and self._view.set_mode(k))
            row.addWidget(button)
        row.addWidget(self._rule())
        for key, icon, tip, action in (
            ("zoom_in", "fa5s.search-plus", "Zoom in", lambda: self._view.zoom_by(1.0 / STEP)),
            ("zoom_out", "fa5s.search-minus", "Zoom out", lambda: self._view.zoom_by(STEP)),
            (
                "home",
                "fa5s.home",
                "Full view (also: double-click, or drag a box to the left)",
                self._view.home,
            ),
            ("back", "fa5s.arrow-left", "Previous view", self._view.back),
            ("forward", "fa5s.arrow-right", "Next view", self._view.forward),
        ):
            button = self._tool(key, icon, QCoreApplication.translate("PHGX", tip))
            button.clicked.connect(action)
            button.clicked.connect(self._sync_history)
            row.addWidget(button)
        row.addWidget(self._rule())
        crosshair = self._tool(
            "crosshair",
            "fa5s.crosshairs",
            QCoreApplication.translate("PHGX", "Crosshair: lines through the cursor"),
            checkable=True,
        )
        crosshair.toggled.connect(self._on_crosshair)
        wheel = self._tool(
            "wheel",
            "fa5s.mouse",
            QCoreApplication.translate(
                "PHGX", "Wheel zoom: the mouse wheel zooms (off: the wheel does nothing)"
            ),
            checkable=True,
        )
        wheel.toggled.connect(self._view.set_wheel_zoom)
        maximize = self._tool(
            "maximize",
            "fa5s.expand-arrows-alt",
            QCoreApplication.translate("PHGX", "Fill the space of both plots, or share it again"),
            checkable=True,
        )
        maximize.toggled.connect(self._on_maximize)
        for button in (crosshair, wheel, maximize):
            row.addWidget(button)
        self._readout = QLabel(plot)  # i18n: as written
        self._readout.setObjectName("surveyCursorReadout")
        self._readout.setStyleSheet(
            "QLabel#surveyCursorReadout { background: rgba(241, 245, 249, 225);"
            " border: 1px solid rgba(100, 116, 139, 110); border-radius: 3px;"
            " padding: 1px 4px; color: #1f2937; }"
        )
        self._readout.hide()
        self._lines = (
            pg.InfiniteLine(
                angle=90, movable=False, pen=pg.mkPen("#64748b", width=1, style=Qt.PenStyle.DashLine)
            ),
            pg.InfiniteLine(
                angle=0, movable=False, pen=pg.mkPen("#64748b", width=1, style=Qt.PenStyle.DashLine)
            ),
        )
        for line in self._lines:
            line.setVisible(False)
            line.setZValue(1000)
            view.addItem(line, ignoreBounds=True)
        view.sigModeChanged.connect(self._sync_mode)
        view.sigRangeChanged.connect(lambda *_a: self._sync_history())
        view.sigResized.connect(lambda *_a: self.place())
        plot.scene().sigMouseMoved.connect(self._on_moved)
        plot.viewport().installEventFilter(self)
        plot.installEventFilter(self)
        self._sync_mode(view.mode())
        self._sync_history()
        self.adjustSize()
        self.place()

    def _tool(self, key: str, icon: str, tip: str, *, checkable: bool = False) -> QToolButton:
        button = QToolButton(self)
        button.setIcon(theme.icon(icon))
        button.setToolTip(tip)  # i18n: as written
        button.setCheckable(checkable)
        button.setAutoRaise(True)
        button.setFixedSize(24, 24)
        self.buttons[key] = button
        return button

    def _rule(self) -> QFrame:
        rule = QFrame(self)
        rule.setObjectName("surveyPlotToolsRule")
        rule.setFixedSize(1, 18)
        return rule

    # -- state --------------------------------------------------------------
    def set_maximized(self, on: bool) -> None:
        button = self.buttons["maximize"]
        button.blockSignals(True)
        button.setChecked(on)
        button.blockSignals(False)
        button.setIcon(theme.icon("fa5s.compress-arrows-alt" if on else "fa5s.expand-arrows-alt"))

    def set_axis_names(self, x_name: str, y_name: str) -> None:
        self._axis_names = (x_name, y_name)

    def _sync_mode(self, mode: str) -> None:
        button = self.buttons.get(mode)
        if button is not None and not button.isChecked():
            button.blockSignals(True)
            button.setChecked(True)
            button.blockSignals(False)

    def _sync_history(self) -> None:
        self.buttons["back"].setEnabled(self._view.can_go_back())
        self.buttons["forward"].setEnabled(self._view.can_go_forward())

    def _on_maximize(self, on: bool) -> None:
        self.set_maximized(on)
        self.maximizeToggled.emit(on)

    def _on_crosshair(self, on: bool) -> None:
        if not on:
            for line in self._lines:
                line.setVisible(False)

    # -- placing and the cursor ---------------------------------------------
    def place(self) -> None:
        """Keep the toolbar at the top left of the plotting area and the readout at its bottom left."""
        area = self._view.sceneBoundingRect()
        top_left = self._plot.mapFromScene(area.topLeft())
        bottom_left = self._plot.mapFromScene(area.bottomLeft())
        self.move(top_left.x() + 6, top_left.y() + 6)
        self.raise_()
        self._readout.adjustSize()
        self._readout.move(bottom_left.x() + 6, bottom_left.y() - self._readout.height() - 6)
        self._readout.raise_()

    def _on_moved(self, position: Any) -> None:
        view = self._view
        if not view.sceneBoundingRect().contains(position):
            self._readout.hide()
            for line in self._lines:
                line.setVisible(False)
            return
        point = view.mapSceneToView(position)
        crosshair = self.buttons["crosshair"].isChecked()
        self._lines[0].setPos(point.x())
        self._lines[1].setPos(point.y())
        for line in self._lines:
            line.setVisible(crosshair)
        factor = axis_units.length_factor()
        unit = axis_units.get_length_unit()
        self._readout.setText(
            QCoreApplication.translate("PHGX", "{0} {1:.2f}   {2} {3:.2f}  ({4})").format(
                self._axis_names[0], point.x() * factor, self._axis_names[1], point.y() * factor, unit
            )
        )
        self._readout.show()
        self.place()

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        kind = event.type()
        if kind == QEvent.Type.Resize:
            self.place()
        elif kind == QEvent.Type.Leave:
            self._readout.hide()
            for line in self._lines:
                line.setVisible(False)
        return False


def attach_toolbar(plot: pg.PlotWidget, view: NavigationViewBox, **kwargs: Any) -> PlotToolbar:
    """A :class:`PlotToolbar` on ``plot``, shown above it."""
    toolbar = PlotToolbar(plot, view, **kwargs)
    toolbar.show()
    return toolbar


__all__ = [
    "HISTORY",
    "MIN_DRAG",
    "MODES",
    "STEP",
    "NavigationViewBox",
    "PlotToolbar",
    "attach_toolbar",
    "make_navigable_plot",
]
