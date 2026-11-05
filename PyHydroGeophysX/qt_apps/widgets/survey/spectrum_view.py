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

from PyHydroGeophysX.qt_apps import i18n, theme
from PyHydroGeophysX.qt_apps.widgets.flow_layout import FlowLayout, group
from PyHydroGeophysX.qt_apps.widgets.survey.common import Settings
from PyHydroGeophysX.qt_apps.widgets.survey.trace_view import REFERENCE_COLOUR
from PyHydroGeophysX.survey.spectra import (
    NoiseMetrics,
    Spectrum,
    line_harmonics,
    noise_metrics,
    trace_spectrum,
)
from PyHydroGeophysX.survey.traces import TraceSet

#: Power-line frequencies offered (Hz).
LINE_FREQUENCIES = (50.0, 60.0)
_HEADERS = ("Channel", "Line peak (dB)", "Floor", "Noise RMS", "SNR (dB)")


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
    """The spectrum view; feed it with :meth:`set_traces`."""

    #: Noise measures of the channels shown, after each redraw.
    metricsComputed = Signal(object)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._settings = Settings("spectrum")
        self._traces: TraceSet | None = None
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
        self._plot = pg.PlotWidget()
        self._plot.showGrid(x=True, y=True, alpha=0.2)
        self._plot.setMenuEnabled(False)
        self._plot.setLogMode(x=False, y=True)
        self._plot.getAxis("left").enableAutoSIPrefix(False)
        self._plot.setLabel("bottom", QCoreApplication.translate("PHGX", "Frequency (Hz)"))
        self._legend = self._plot.addLegend(offset=(8, 8))
        self._table = QTableWidget(0, len(_HEADERS))
        self._table.setHorizontalHeaderLabels([i18n.tr(h) for h in _HEADERS])
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self._table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._table.setSortingEnabled(True)
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

    def set_traces(self, traces: TraceSet | None) -> None:
        self._traces = traces
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
        traces = self._traces
        self._table.setSortingEnabled(False)
        self._table.setRowCount(0)
        if traces is None or traces.size == 0 or traces.sample_rate <= 0:
            self._spectrum, self._metrics = None, ()
            self._info.setText(
                QCoreApplication.translate("PHGX", "Choose a group and its channels to see their spectra.")
            )
            return
        window = traces.window(str(self._window.currentData() or ""))
        spectrum = trace_spectrum(traces, window)
        self._spectrum = spectrum
        keep = spectrum.frequency > 0
        colours = theme.SERIES_COLORS
        floor = np.finfo(float).tiny
        for row, label in enumerate(spectrum.labels):
            pen = pg.mkPen(colours[row % len(colours)], width=1.0)
            plot.plot(
                spectrum.frequency[keep], np.maximum(spectrum.power[row, keep], floor), pen=pen, name=label
            )
        if spectrum.reference is not None and self._reference.isChecked():
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
        for harmonic in line_harmonics(spectrum.sample_rate, f0):
            style = Qt.PenStyle.DashLine if harmonic.aliased else Qt.PenStyle.SolidLine
            line = pg.InfiniteLine(harmonic.apparent, angle=90, pen=pg.mkPen("#dc2626", width=1, style=style))
            line.setToolTip(
                QCoreApplication.translate("PHGX", "{0:g} Hz harmonic, seen at {1:g} Hz").format(
                    harmonic.frequency, harmonic.apparent
                )
            )
            plot.addItem(line)
        plot.setXRange(0, spectrum.nyquist, padding=0.01)
        unit = f"{traces.unit}²/Hz" if traces.unit else "1/Hz"
        plot.setLabel("left", QCoreApplication.translate("PHGX", "PSD ({0})").format(unit))
        signal_window = traces.window("End of on-time")
        noise_window = traces.window("Off-time") or traces.window("Late off-time")
        self._metrics = noise_metrics(
            traces, spectrum, line_frequency=f0, signal_window=signal_window, noise_window=noise_window
        )
        self._fill_table(traces)
        self._info.setText(
            QCoreApplication.translate("PHGX", "Welch, Hann window · Nyquist {0:g} Hz · window: {1}").format(
                spectrum.nyquist,
                i18n.tr(spectrum.window)
                if spectrum.window
                else QCoreApplication.translate("PHGX", "whole record"),
            )
        )
        self.metricsComputed.emit(self._metrics)

    def _fill_table(self, traces: TraceSet) -> None:
        table = self._table
        table.setRowCount(len(self._metrics))
        for row, metric in enumerate(self._metrics):
            label = traces.labels[row] if row < len(traces.labels) else metric.channel
            table.setItem(row, 0, QTableWidgetItem(label))
            for column, value, text in (
                (1, metric.line_db, f"{metric.line_db:.1f}"),
                (2, metric.floor, f"{metric.floor:.3g}"),
                (3, metric.noise_rms, f"{metric.noise_rms:.3g}"),
                (4, metric.snr_db, f"{metric.snr_db:.1f}"),
            ):
                table.setItem(row, column, _Number(float(value), text if np.isfinite(value) else "-"))
        table.setSortingEnabled(True)

    def _on_window(self, _index: int) -> None:
        self._settings.set("window", str(self._window.currentData() or ""))
        self.redraw()

    def _on_reference(self, on: bool) -> None:
        self._settings.set("reference", bool(on))
        self.redraw()


__all__ = ["LINE_FREQUENCIES", "SurveySpectrumView"]
