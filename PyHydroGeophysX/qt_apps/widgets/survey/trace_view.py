"""Curves of one group: its channels over time, the reference curve on the right axis.

The time windows of the record (on-time, off-time, the end of on-time) are
offered in a list that zooms the time axis to them, and shaded faintly.
Long records are drawn decimated to their peaks and clipped to the view, so an
MT run of millions of samples pans as fast as a DC/IP shot.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pyqtgraph as pg
from PySide6.QtCore import QCoreApplication, Qt, Signal
from PySide6.QtWidgets import QCheckBox, QComboBox, QLabel, QSpinBox, QVBoxLayout, QWidget

from PyHydroGeophysX.qt_apps import i18n
from PyHydroGeophysX.qt_apps.widgets.flow_layout import FlowLayout, group
from PyHydroGeophysX.qt_apps.widgets.survey.common import Settings
from PyHydroGeophysX.survey.series import COLOURS, encode, normalized, percentile_band, window_mask
from PyHydroGeophysX.survey.traces import TraceCollection, TraceSet, Window

#: Curves drawn per plot; the spin box stays inside this.
CURVE_LIMITS = (32, 400)
DEFAULT_CURVE_LIMIT = 96
#: A legend listing every curve stops being readable past this many.
COMPACT_LEGEND = 12

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
    """The curve view; feed it with :meth:`set_traces` (one group or a collection)."""

    windowChanged = Signal(str)
    #: A click on a curve: its group and its key. The page decides what that selects.
    curvePicked = Signal(str, object)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._settings = Settings("traces")
        self._traces: TraceSet | None = None
        self._collection: TraceCollection | None = None
        self._picked: object = None
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
        self._time_mode = QComboBox()
        self._time_mode.addItem(QCoreApplication.translate("PHGX", "Record time"), "record")
        self._time_mode.addItem(QCoreApplication.translate("PHGX", "Relative to time origin"), "relative")
        self._time_mode.setToolTip(
            QCoreApplication.translate("PHGX", "Align every group on its time origin (a shot's switch-off)")
        )
        self._time_mode.setVisible(False)
        self._time_mode.currentIndexChanged.connect(self._on_time_mode)
        self._normalize = QCheckBox(QCoreApplication.translate("PHGX", "Normalise by window mean"))
        self._normalize.setToolTip(
            QCoreApplication.translate(
                "PHGX", "Divide each curve by its mean inside the window chosen beside it, keeping the sign"
            )
        )
        self._normalize.toggled.connect(self._on_normalize)
        self._norm_window = QComboBox()
        self._norm_window.setToolTip(
            QCoreApplication.translate(
                "PHGX", "Window the mean is taken over; the steady on-time gives V/Vp for a DC/IP shot"
            )
        )
        self._norm_window.setEnabled(False)
        self._norm_window.currentIndexChanged.connect(self._on_norm_window)
        self._draw = QComboBox()
        self._draw.addItem(QCoreApplication.translate("PHGX", "Each curve"), "curves")
        self._draw.addItem(QCoreApplication.translate("PHGX", "Median and 10-90% band"), "band")
        self._draw.setToolTip(
            QCoreApplication.translate(
                "PHGX", "The band needs curves aligned on their time origin and normalised"
            )
        )
        self._draw.currentIndexChanged.connect(lambda _i: self.redraw())
        self._limit = QSpinBox()
        self._limit.setRange(*CURVE_LIMITS)
        self._limit.setValue(int(self._settings.get("limit", DEFAULT_CURVE_LIMIT)))
        self._limit.setToolTip(
            QCoreApplication.translate("PHGX", "Curves drawn at once; the rest stay listed")
        )
        self._limit.valueChanged.connect(self._on_limit)
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
        controls.addWidget(group(QCoreApplication.translate("PHGX", "Time axis"), self._time_mode))
        controls.addWidget(self._normalize)
        controls.addWidget(self._norm_window)
        controls.addWidget(group(QCoreApplication.translate("PHGX", "Curves drawn"), self._draw))
        controls.addWidget(group(QCoreApplication.translate("PHGX", "Up to"), self._limit))
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

    def curve_limit(self) -> int:
        return int(self._limit.value())

    def set_traces(self, traces: TraceSet | TraceCollection | None) -> None:
        if isinstance(traces, TraceCollection):
            self._collection = traces
            self._traces = traces.focus_set()
        elif traces is not None:
            self._collection = TraceCollection.single(traces)
            self._traces = self._collection.focus_set()
        else:
            self._collection = None
            self._traces = None
        focus = self._traces
        has_origin = self._collection is not None and any(
            item.origin is not None for item in self._collection.sets
        )
        self._time_mode.setVisible(has_origin)
        wanted = self._window.currentData() or self._settings.get("window", "")
        self._window.blockSignals(True)
        self._window.clear()
        for window in focus.windows if focus is not None else ():
            self._window.addItem(i18n.tr(window.name), window.name)
        index = self._window.findData(wanted)
        self._window.setCurrentIndex(max(index, 0))
        self._window.blockSignals(False)
        windows = focus.windows if focus is not None else ()
        steady = next((window.name for window in windows if window.kind == "on"), "")
        wanted = self._norm_window.currentData() or self._settings.get("norm_window", "") or steady
        self._norm_window.blockSignals(True)
        self._norm_window.clear()
        for window in windows:
            self._norm_window.addItem(i18n.tr(window.name), window.name)
        index = self._norm_window.findData(wanted)
        if index < 0:
            index = self._norm_window.findData(steady)
        self._norm_window.setCurrentIndex(max(index, 0))
        self._norm_window.blockSignals(False)
        self._sync_band()
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
        collection, focus = self._collection, self._traces
        if collection is None or focus is None or collection.size == 0:
            item.hideAxis("right")
            self._info.setText(
                QCoreApplication.translate("PHGX", "Choose a group and its channels to see their curves.")
            )
            return
        styles = encode(collection)
        drawn = styles[: self.curve_limit()]
        compact = len(styles) > COMPACT_LEGEND
        band = self._draw.currentData() == "band" and self._draw.isEnabled()
        if band:
            drawn = styles
            self._draw_band(collection, styles)
        else:
            self._draw_curves(drawn, compact)
        if self._normalize.isChecked():
            self._plot.setLabel(
                "left",
                QCoreApplication.translate("PHGX", "Ratio to the mean over {0}").format(
                    i18n.tr(str(self._norm_window.currentData() or ""))
                ),
            )
        else:
            self._plot.setLabel("left", focus.unit or QCoreApplication.translate("PHGX", "Value"))
        self._draw_reference(focus)
        if self._shade.isChecked():
            shift = self._shift()
            for window in focus.windows:
                shade = _SHADES.get(window.kind)
                if shade is None:
                    continue
                region = pg.LinearRegionItem(
                    (window.start - shift, window.end - shift),
                    movable=False,
                    brush=pg.mkBrush(*shade),
                    pen=None,
                )
                region.setZValue(-10)
                item.addItem(region)
        self._apply_window()
        text = QCoreApplication.translate("PHGX", "{0} channels · {1} samples · {2:g} samples/s").format(
            focus.size, focus.t.size, focus.sample_rate
        )
        if len(drawn) < len(styles):
            text += "    " + QCoreApplication.translate("PHGX", "Showing {0} of {1}").format(
                len(drawn), len(styles)
            )
        if focus.title:
            text += f"    {focus.title}"
        picked = next((style for style in drawn if style.key == self._picked), None)
        if picked is not None:
            text = (
                QCoreApplication.translate("PHGX", "{0} · {1}").format(picked.group, picked.channel)
                + "    "
                + text
            )
        self._info.setText(text)  # i18n: as written
        self._sync_right()

    def _draw_curves(self, styles: tuple[Any, ...], compact: bool) -> None:
        item = self._plot.getPlotItem()
        dashes = (Qt.PenStyle.SolidLine, Qt.PenStyle.DashLine, Qt.PenStyle.DotLine, Qt.PenStyle.DashDotLine)
        seen: set[str] = set()
        for style in styles:
            owner = self._set(style.group)
            if owner is None:
                continue
            row = owner.channels.index(style.channel)
            pen = pg.mkPen(
                COLOURS[style.colour % len(COLOURS)],
                width=2.2 if style.key == self._picked else 1.1,
                style=dashes[style.dash % len(dashes)],
            )
            curve = item.plot(
                self._times(owner),
                self._values(owner)[row],
                pen=pen,
                name=None if compact else style.label,
                clickable=True,
            )
            curve.sigClicked.connect(lambda _curve, _points, picked=style: self._on_curve(picked))
            if compact and style.channel not in seen and len(seen) < 8:
                seen.add(style.channel)
                self._legend.addItem(curve, style.channel)  # i18n: as written
        if compact:
            blank = pg.PlotDataItem()
            count = QCoreApplication.translate("PHGX", "{0} curves").format(
                self._collection.size if self._collection else 0
            )
            self._legend.addItem(blank, count)  # i18n: as written

    def _draw_band(self, collection: TraceCollection, styles: tuple[Any, ...]) -> None:
        focus = self._traces
        if focus is None or not styles:
            return
        curves = []
        for style in styles:
            owner = self._set(style.group)
            if owner is None:
                continue
            row = owner.channels.index(style.channel)
            curves.append((self._times(owner), self._values(owner)[row]))
        median, low, high = percentile_band(curves, self._times(focus))
        item = self._plot.getPlotItem()
        bottom = item.plot(self._times(focus), low, pen=pg.mkPen(COLOURS[0], width=0.6))
        top = item.plot(self._times(focus), high, pen=pg.mkPen(COLOURS[0], width=0.6))
        item.addItem(pg.FillBetweenItem(bottom, top, brush=pg.mkBrush(0, 122, 255, 50)))
        item.plot(
            self._times(focus), median, pen=pg.mkPen(COLOURS[0], width=1.8), name=style_count(len(curves))
        )

    def _draw_reference(self, focus: TraceSet) -> None:
        item = self._plot.getPlotItem()
        if focus.reference is None or not self._reference.isChecked():
            item.hideAxis("right")
            return
        item.showAxis("right")
        curve = pg.PlotCurveItem(
            self._times(focus),
            focus.reference,
            pen=pg.mkPen(REFERENCE_COLOUR, width=1.2, style=Qt.PenStyle.DashLine),
        )
        self._right.addItem(curve)
        label = (
            i18n.tr(focus.reference_label)
            if focus.reference_label
            else QCoreApplication.translate("PHGX", "Reference")
        )
        unit = f" ({focus.reference_unit})" if focus.reference_unit else ""
        item.getAxis("right").setLabel(label + unit, color=REFERENCE_COLOUR)
        self._right.enableAutoRange(axis=pg.ViewBox.YAxis)

    def _set(self, group: str) -> TraceSet | None:
        collection = self._collection
        return next((item for item in collection.sets if item.group == group), None) if collection else None

    def _relative(self) -> bool:
        return self._time_mode.isVisible() and self._time_mode.currentData() == "relative"

    def _shift(self) -> float:
        focus = self._traces
        if not self._relative() or focus is None or focus.origin is None:
            return 0.0
        return float(focus.origin)

    def _times(self, traces: TraceSet) -> np.ndarray:
        origin = float(traces.origin or 0.0) if self._relative() else 0.0
        return traces.t - origin

    def _values(self, traces: TraceSet) -> np.ndarray:
        if not self._normalize.isChecked():
            return traces.values
        window = traces.window(str(self._norm_window.currentData() or ""))
        return normalized(traces.values, window_mask(traces.t, window))

    def _sync_band(self) -> None:
        allowed = self._relative() and self._normalize.isChecked()
        self._draw.setEnabled(allowed)
        if not allowed and self._draw.currentData() == "band":
            self._draw.blockSignals(True)
            self._draw.setCurrentIndex(0)
            self._draw.blockSignals(False)

    def _on_curve(self, style: Any) -> None:
        self._picked = style.key
        self.curvePicked.emit(style.group, style.key)
        self.redraw()

    def _apply_window(self) -> None:
        traces = self._traces
        window = self.window()
        if traces is None:
            return
        shift = self._shift()
        if window is not None and window.kind != "record":
            start, end = window.start - shift, window.end - shift
            self._plot.setXRange(start, end, padding=0.02)
            sets = self._collection.sets if self._collection is not None else (traces,)
            parts = []
            for item in sets:
                times = self._times(item)
                inside = (times >= start) & (times <= end)
                if inside.any() and item.size:
                    values = self._values(item)[:, inside]
                    parts.append(values[np.isfinite(values)])
            finite = np.concatenate(parts) if parts else np.zeros(0)
            if finite.size:
                lo, hi = float(finite.min()), float(finite.max())
                pad = 0.05 * (hi - lo or abs(hi) or 1.0)
                self._plot.setYRange(lo - pad, hi + pad, padding=0)
        else:
            self._plot.getPlotItem().enableAutoRange()

    def _on_window(self, _index: int) -> None:
        name = str(self._window.currentData() or "")
        self._settings.set("window", name)
        self.redraw()
        self.windowChanged.emit(name)

    def _on_shade(self, on: bool) -> None:
        self._settings.set("shade", bool(on))
        self.redraw()

    def _on_reference(self, on: bool) -> None:
        self._settings.set("reference", bool(on))
        self.redraw()

    def _on_time_mode(self, _index: int) -> None:
        self._sync_band()
        self.redraw()

    def _on_normalize(self, on: bool) -> None:
        self._norm_window.setEnabled(bool(on))
        self._sync_band()
        self.redraw()

    def _on_norm_window(self, _index: int) -> None:
        self._settings.set("norm_window", str(self._norm_window.currentData() or ""))
        if self._normalize.isChecked():
            self.redraw()

    def _on_limit(self, value: int) -> None:
        self._settings.set("limit", int(value))
        self.redraw()


def style_count(count: int) -> str:
    return QCoreApplication.translate("PHGX", "{0} curves").format(count)


__all__ = [
    "COMPACT_LEGEND",
    "CURVE_LIMITS",
    "DEFAULT_CURVE_LIMIT",
    "REFERENCE_COLOUR",
    "WINDOW_NAMES",
    "SurveyTraceView",
]
