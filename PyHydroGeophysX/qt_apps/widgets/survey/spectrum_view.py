"""Power spectra of one group's channels over a window, with the line harmonics marked.

Harmonics that sampling folds below the Nyquist frequency are dashed. Under the
plot, one row per channel: the line-frequency peak over the broadband floor,
the floor itself, the noise RMS of the noise window and the signal-to-noise
ratio; the table sorts by any column, so the worst channel is one click away.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pyqtgraph as pg
from PySide6.QtCore import QCoreApplication, Qt, Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QHeaderView,
    QLabel,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from PyHydroGeophysX.qt_apps import i18n
from PyHydroGeophysX.qt_apps.widgets.flow_layout import FlowLayout, group
from PyHydroGeophysX.qt_apps.widgets.survey.common import Settings, ThinLogAxis
from PyHydroGeophysX.qt_apps.widgets.survey.trace_view import (
    COMPACT_LEGEND,
    DEFAULT_CURVE_LIMIT,
    REFERENCE_COLOUR,
)
from PyHydroGeophysX.survey.series import COLOURS, encode
from PyHydroGeophysX.survey.spectra import (
    NoiseMetrics,
    Spectrum,
    line_harmonics,
    noise_metrics,
    trace_spectrum,
)
from PyHydroGeophysX.survey.traces import TraceCollection, TraceSet

#: Power-line frequencies offered (Hz).
LINE_FREQUENCIES = (50.0, 60.0)
_HEADERS = ("Group", "Channel", "Line peak (dB)", "Floor", "Noise RMS", "SNR (dB)")


class _Number(QTableWidgetItem):
    """A table cell that sorts by its value, NaN last."""

    def __init__(self, value: float, text: str) -> None:
        super().__init__(text)
        self._value = value

    def __lt__(self, other: Any) -> bool:
        mine = self._value if np.isfinite(self._value) else np.inf
        theirs = getattr(other, "_value", np.inf)
        return bool(mine < (theirs if np.isfinite(theirs) else np.inf))


class SurveySpectrumView(QWidget):
    """The spectrum view; feed it with :meth:`set_traces` (one group or a collection)."""

    #: Noise measures of the channels shown, after each redraw.
    metricsComputed = Signal(object)
    #: A click on the table: the group's name and the channel's key.
    curvePicked = Signal(str, object)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._settings = Settings("spectrum")
        self._traces: TraceSet | None = None
        self._collection: TraceCollection | None = None
        self._spectrum: Spectrum | None = None
        self._metrics: tuple[NoiseMetrics, ...] = ()
        self._window = QComboBox()
        self._window.setToolTip(
            QCoreApplication.translate(
                "PHGX",
                "Window the spectrum is taken over; a steady part of the record avoids switching leakage",
            )
        )
        self._window.currentIndexChanged.connect(self._on_window)
        self._line = QComboBox()
        for value in LINE_FREQUENCIES:
            self._line.addItem(f"{value:g} Hz", value)  # i18n: as written
        self._line.setToolTip(
            QCoreApplication.translate("PHGX", "Power-line frequency whose harmonics are marked")
        )
        self._line.currentIndexChanged.connect(lambda _i: self.redraw())
        self._reference = QCheckBox(QCoreApplication.translate("PHGX", "Reference spectrum"))
        self._reference.setToolTip(
            QCoreApplication.translate(
                "PHGX", "Overlay the spectrum of the reference curve (such as the current)"
            )
        )
        self._reference.setChecked(self._settings.get("reference", False))
        self._reference.toggled.connect(self._on_reference)
        self._plot = pg.PlotWidget(axisItems={"left": ThinLogAxis("left")})
        self._plot.showGrid(x=True, y=True, alpha=0.2)
        self._plot.setMenuEnabled(False)
        self._plot.setLogMode(x=False, y=True)
        self._plot.getAxis("left").setStyle(hideOverlappingLabels=True)
        self._plot.getAxis("left").enableAutoSIPrefix(False)
        self._plot.setLabel("bottom", QCoreApplication.translate("PHGX", "Frequency (Hz)"))
        self._legend = self._plot.addLegend(offset=(8, 8))
        self._table = QTableWidget(0, len(_HEADERS))
        self._table.setHorizontalHeaderLabels([i18n.tr(h) for h in _HEADERS])
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self._table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._table.setSortingEnabled(True)
        self._table.itemClicked.connect(self._on_row)
        self._info = QLabel()
        self._info.setWordWrap(True)
        controls = FlowLayout(spacing=6)
        controls.addWidget(group(QCoreApplication.translate("PHGX", "Window"), self._window))
        controls.addWidget(group(QCoreApplication.translate("PHGX", "Line frequency"), self._line))
        controls.addWidget(self._reference)
        split = QSplitter(Qt.Orientation.Vertical)
        split.addWidget(self._plot)
        split.addWidget(self._table)
        split.setStretchFactor(0, 3)
        split.setStretchFactor(1, 1)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(controls)
        layout.addWidget(split, 1)
        layout.addWidget(self._info)

    def plot_widget(self) -> pg.PlotWidget:
        return self._plot

    def spectrum(self) -> Spectrum | None:
        return self._spectrum

    def metrics(self) -> tuple[NoiseMetrics, ...]:
        return self._metrics

    def line_frequency(self) -> float:
        return float(self._line.currentData() or 50.0)

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
        traces = self._traces
        if traces is not None and traces.line_frequency:
            index = self._line.findData(float(traces.line_frequency))
            if index >= 0:
                self._line.blockSignals(True)
                self._line.setCurrentIndex(index)
                self._line.blockSignals(False)
        wanted = self._window.currentData() or self._settings.get("window", "On-time (steady)")
        self._window.blockSignals(True)
        self._window.clear()
        for window in traces.windows if traces is not None else ():
            self._window.addItem(i18n.tr(window.name), window.name)
        index = self._window.findData(wanted)
        self._window.setCurrentIndex(max(index, 0))
        self._window.blockSignals(False)
        self.redraw()

    def redraw(self) -> None:
        plot = self._plot
        plot.clear()
        self._legend.clear()
        collection, traces = self._collection, self._traces
        self._table.setSortingEnabled(False)
        self._table.setRowCount(0)
        if collection is None or traces is None or collection.size == 0 or traces.sample_rate <= 0:
            self._spectrum, self._metrics = None, ()
            self._info.setText(
                QCoreApplication.translate("PHGX", "Choose a group and its channels to see their spectra.")
            )
            return
        name = str(self._window.currentData() or "")
        spectra = {
            item.group: trace_spectrum(item, item.window(name))
            for item in collection.sets
            if item.sample_rate > 0
        }
        spectrum = spectra.get(traces.group)
        self._spectrum = spectrum
        styles = encode(collection)
        limit = int(Settings("traces").get("limit", DEFAULT_CURVE_LIMIT))
        drawn = styles[: max(limit, 1)]
        compact = len(styles) > COMPACT_LEGEND
        floor = np.finfo(float).tiny
        dashes = (Qt.PenStyle.SolidLine, Qt.PenStyle.DashLine, Qt.PenStyle.DotLine, Qt.PenStyle.DashDotLine)
        seen: set[str] = set()
        for style in drawn:
            spectrum_of = spectra.get(style.group)
            owner = next((item for item in collection.sets if item.group == style.group), None)
            if spectrum_of is None or owner is None or style.channel not in owner.channels:
                continue
            row = owner.channels.index(style.channel)
            keep = spectrum_of.frequency > 0
            pen = pg.mkPen(
                COLOURS[style.colour % len(COLOURS)], width=1.0, style=dashes[style.dash % len(dashes)]
            )
            curve = plot.plot(
                spectrum_of.frequency[keep],
                np.maximum(spectrum_of.power[row, keep], floor),
                pen=pen,
                name=None if compact else style.label,
            )
            if compact and style.channel not in seen and len(seen) < 8:
                seen.add(style.channel)
                self._legend.addItem(curve, style.channel)  # i18n: as written
        if spectrum is not None and spectrum.reference is not None and self._reference.isChecked():
            keep = spectrum.frequency > 0
            pen = pg.mkPen(REFERENCE_COLOUR, width=1.0, style=Qt.PenStyle.DashLine)
            label = (
                i18n.tr(traces.reference_label)
                if traces.reference_label
                else QCoreApplication.translate("PHGX", "Reference")
            )
            plot.plot(
                spectrum.frequency[keep], np.maximum(spectrum.reference[keep], floor), pen=pen, name=label
            )
        f0 = self.line_frequency()
        if spectrum is not None:
            for harmonic in line_harmonics(spectrum.sample_rate, f0):
                style_pen = Qt.PenStyle.DashLine if harmonic.aliased else Qt.PenStyle.SolidLine
                line = pg.InfiniteLine(
                    harmonic.apparent, angle=90, pen=pg.mkPen("#dc2626", width=1, style=style_pen)
                )
                line.setToolTip(
                    QCoreApplication.translate("PHGX", "{0:g} Hz harmonic, seen at {1:g} Hz").format(
                        harmonic.frequency, harmonic.apparent
                    )
                )
                plot.addItem(line)
            plot.setXRange(0, spectrum.nyquist, padding=0.01)
        unit = f"{traces.unit}²/Hz" if traces.unit else "1/Hz"
        plot.setLabel("left", QCoreApplication.translate("PHGX", "PSD ({0})").format(unit))
        self._fill_table(collection, spectra, f0)
        rates = {round(item.sample_rate, 3) for item in collection.sets}
        note = QCoreApplication.translate(
            "PHGX", "Welch, Hann window · Nyquist {0:g} Hz · window: {1}"
        ).format(
            spectrum.nyquist if spectrum is not None else 0.0,
            i18n.tr(spectrum.window)
            if spectrum is not None and spectrum.window
            else QCoreApplication.translate("PHGX", "whole record"),
        )
        if len(rates) > 1:
            note += "    " + QCoreApplication.translate(
                "PHGX", "Sample rates differ; harmonics follow the focused group"
            )
        if len(drawn) < len(styles):
            note += "    " + QCoreApplication.translate("PHGX", "Showing {0} of {1}").format(
                len(drawn), len(styles)
            )
        self._info.setText(note)  # i18n: as written
        self.metricsComputed.emit(self._metrics)

    def _fill_table(
        self, collection: TraceCollection, spectra: dict[str, Spectrum], line_frequency: float
    ) -> None:
        table = self._table
        rows: list[tuple[str, object, NoiseMetrics]] = []
        focus_metrics: tuple[NoiseMetrics, ...] = ()
        for item in collection.sets:
            spectrum = spectra.get(item.group)
            if spectrum is None:
                continue
            metrics = noise_metrics(
                item,
                spectrum,
                line_frequency=line_frequency,
                signal_window=item.window("End of on-time"),
                noise_window=item.window("Late off-time") or item.window("Off-time"),
            )
            if item.group == collection.focus:
                focus_metrics = metrics
            for index, metric in enumerate(metrics):
                key = item.keys[index] if item.keys else ("trace", item.group, metric.channel)
                rows.append((item.group, key, metric))
        self._metrics = focus_metrics
        table.setRowCount(len(rows))
        for row, (group_name, key, metric) in enumerate(rows):
            group_item = QTableWidgetItem(group_name)
            group_item.setData(Qt.ItemDataRole.UserRole, (group_name, key))
            table.setItem(row, 0, group_item)
            table.setItem(row, 1, QTableWidgetItem(metric.channel))
            for column, value, text in (
                (2, metric.line_db, f"{metric.line_db:.1f}"),
                (3, metric.floor, f"{metric.floor:.3g}"),
                (4, metric.noise_rms, f"{metric.noise_rms:.3g}"),
                (5, metric.snr_db, f"{metric.snr_db:.1f}"),
            ):
                table.setItem(row, column, _Number(float(value), text if np.isfinite(value) else "-"))
        table.setSortingEnabled(True)

    def _on_row(self, item: QTableWidgetItem) -> None:
        stored = self._table.item(item.row(), 0).data(Qt.ItemDataRole.UserRole)
        if isinstance(stored, tuple) and len(stored) == 2:
            self.curvePicked.emit(str(stored[0]), stored[1])

    def _on_window(self, _index: int) -> None:
        self._settings.set("window", str(self._window.currentData() or ""))
        self.redraw()

    def _on_reference(self, on: bool) -> None:
        self._settings.set("reference", bool(on))
        self.redraw()


__all__ = ["LINE_FREQUENCIES", "SurveySpectrumView"]
