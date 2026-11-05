"""Curves of one group: its channels over time, the reference curve on the right axis.

The time windows of the record (on-time, off-time, the end of on-time) are
offered in a list that zooms the time axis to them, and shaded faintly.
Long records are drawn decimated to their peaks and clipped to the view, so an
MT run of millions of samples pans as fast as a DC/IP shot.
"""

from __future__ import annotations

import numpy as np
import pyqtgraph as pg
from PySide6.QtCore import QCoreApplication, Signal
from PySide6.QtWidgets import QCheckBox, QComboBox, QLabel, QVBoxLayout, QWidget

from PyHydroGeophysX.qt_apps import i18n, theme
from PyHydroGeophysX.qt_apps.widgets.flow_layout import FlowLayout, group
from PyHydroGeophysX.qt_apps.widgets.survey.common import Settings
from PyHydroGeophysX.survey.traces import TraceSet, Window

#: Window names the adapters use (English source text, translated when shown).
WINDOW_NAMES = (
    "Whole record",
    "On-time (steady)",
    "End of on-time",
    "Off-time",
    "Late off-time",
    "Gates",
    "First minute",
    "Last minute",
)
#: Shading of each window kind.
_SHADES = {
    "on": (59, 130, 246, 22),
    "off": (16, 185, 129, 22),
    "signal": (245, 158, 11, 30),
    "gate": (139, 92, 246, 26),
}
REFERENCE_COLOUR = "#9a3412"


class SurveyTraceView(QWidget):
    """The curve view; feed it with :meth:`set_traces`."""

    windowChanged = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._settings = Settings("traces")
        self._traces: TraceSet | None = None
        self._window = QComboBox()
        self._window.setToolTip(
            QCoreApplication.translate("PHGX", "Zoom the time axis to a window of the record")
        )
        self._window.currentIndexChanged.connect(self._on_window)
        self._shade = QCheckBox(QCoreApplication.translate("PHGX", "Shade windows"))
        self._shade.setChecked(self._settings.get("shade", True))
        self._shade.toggled.connect(self._on_shade)
        self._reference = QCheckBox(QCoreApplication.translate("PHGX", "Reference curve"))
        self._reference.setToolTip(
            QCoreApplication.translate(
                "PHGX", "Draw the reference curve (such as the current) on the right axis"
            )
        )
        self._reference.setChecked(self._settings.get("reference", True))
        self._reference.toggled.connect(self._on_reference)
        self._plot = pg.PlotWidget()
        self._plot.showGrid(x=True, y=True, alpha=0.2)
        self._plot.setMenuEnabled(False)
        item = self._plot.getPlotItem()
        item.setDownsampling(auto=True, mode="peak")
        item.setClipToView(True)
        self._legend = item.addLegend(offset=(8, 8))
        self._right = pg.ViewBox()
        item.showAxis("right")
        item.scene().addItem(self._right)
        item.getAxis("right").linkToView(self._right)
        self._right.setXLink(item)
        item.vb.sigResized.connect(self._sync_right)
        self._info = QLabel()
        self._info.setWordWrap(True)
        controls = FlowLayout(spacing=6)
        controls.addWidget(group(QCoreApplication.translate("PHGX", "Window"), self._window))
        controls.addWidget(self._shade)
        controls.addWidget(self._reference)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(controls)
        layout.addWidget(self._plot, 1)
        layout.addWidget(self._info)
        self._plot.setLabel("bottom", QCoreApplication.translate("PHGX", "Time (s)"))

    def plot_widget(self) -> pg.PlotWidget:
        return self._plot

    def window(self) -> Window | None:
        traces = self._traces
        name = self._window.currentData()
        return traces.window(str(name)) if traces is not None and name else None

    def set_traces(self, traces: TraceSet | None) -> None:
        self._traces = traces
        wanted = self._window.currentData() or self._settings.get("window", "")
        self._window.blockSignals(True)
        self._window.clear()
        for window in traces.windows if traces is not None else ():
            self._window.addItem(i18n.tr(window.name), window.name)
        index = self._window.findData(wanted)
        self._window.setCurrentIndex(max(index, 0))
        self._window.blockSignals(False)
        self.redraw()

    def _sync_right(self) -> None:
        item = self._plot.getPlotItem()
        self._right.setGeometry(item.vb.sceneBoundingRect())
        self._right.linkedViewChanged(item.vb, self._right.XAxis)

    def redraw(self) -> None:
        item = self._plot.getPlotItem()
        item.clear()
        self._legend.clear()
        self._right.clear()
        traces = self._traces
        if traces is None or traces.size == 0:
            item.hideAxis("right")
            self._info.setText(
                QCoreApplication.translate("PHGX", "Choose a group and its channels to see their curves.")
            )
            return
        colours = theme.SERIES_COLORS
        for row, label in enumerate(traces.labels):
            pen = pg.mkPen(colours[row % len(colours)], width=1.1)
            item.plot(traces.t, traces.values[row], pen=pen, name=label)
        self._plot.setLabel("left", traces.unit or QCoreApplication.translate("PHGX", "Value"))
        if traces.reference is not None and self._reference.isChecked():
            item.showAxis("right")
            curve = pg.PlotCurveItem(
                traces.t,
                traces.reference,
                pen=pg.mkPen(REFERENCE_COLOUR, width=1.2, style=pg.QtCore.Qt.PenStyle.DashLine),
            )
            self._right.addItem(curve)
            label = (
                i18n.tr(traces.reference_label)
                if traces.reference_label
                else QCoreApplication.translate("PHGX", "Reference")
            )
            unit = f" ({traces.reference_unit})" if traces.reference_unit else ""
            item.getAxis("right").setLabel(label + unit, color=REFERENCE_COLOUR)
            self._right.enableAutoRange(axis=pg.ViewBox.YAxis)
        else:
            item.hideAxis("right")
        if self._shade.isChecked():
            for window in traces.windows:
                shade = _SHADES.get(window.kind)
                if shade is None:
                    continue
                region = pg.LinearRegionItem(
                    (window.start, window.end), movable=False, brush=pg.mkBrush(*shade), pen=None
                )
                region.setZValue(-10)
                item.addItem(region)
        self._apply_window()
        rate = traces.sample_rate
        self._info.setText(
            QCoreApplication.translate("PHGX", "{0} channels · {1} samples · {2:g} samples/s").format(
                traces.size, traces.t.size, rate
            )
            + (f"    {traces.title}" if traces.title else "")
        )
        self._sync_right()

    def _apply_window(self) -> None:
        traces = self._traces
        window = self.window()
        if traces is None:
            return
        if window is not None and window.kind != "record":
            self._plot.setXRange(window.start, window.end, padding=0.02)
            mask = traces.mask(window)
            if mask.any() and traces.size:
                values = traces.values[:, mask]
                finite = values[np.isfinite(values)]
                if finite.size:
                    lo, hi = float(finite.min()), float(finite.max())
                    pad = 0.05 * (hi - lo or abs(hi) or 1.0)
                    self._plot.setYRange(lo - pad, hi + pad, padding=0)
        else:
            self._plot.getPlotItem().enableAutoRange()

    def _on_window(self, _index: int) -> None:
        name = str(self._window.currentData() or "")
        self._settings.set("window", name)
        self._apply_window()
        self.windowChanged.emit(name)

    def _on_shade(self, on: bool) -> None:
        self._settings.set("shade", bool(on))
        self.redraw()

    def _on_reference(self, on: bool) -> None:
        self._settings.set("reference", bool(on))
        self.redraw()


__all__ = ["REFERENCE_COLOUR", "WINDOW_NAMES", "SurveyTraceView"]
