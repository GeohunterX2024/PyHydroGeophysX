"""Section along the line: terrain, electrodes and the pseudo-depth points under the ground.

The points sit at the ground elevation minus their pseudo-depth, coloured by a
value of theirs; the current group's points are ringed. The legend names the
pseudo-depth convention, which is a display convention, not a depth of
investigation. A box (with "Box select") selects the keys of the points inside it.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pyqtgraph as pg
from PySide6.QtCore import QCoreApplication, QRectF
from PySide6.QtWidgets import QCheckBox, QComboBox, QLabel, QVBoxLayout, QWidget

from PyHydroGeophysX.qt_apps import i18n
from PyHydroGeophysX.qt_apps.widgets import colormaps as cmaps
from PyHydroGeophysX.qt_apps.widgets import length_units
from PyHydroGeophysX.qt_apps.widgets.color_range import ColorRange
from PyHydroGeophysX.qt_apps.widgets.flow_layout import FlowLayout, group
from PyHydroGeophysX.qt_apps.widgets.survey.common import (
    ColorBar,
    Settings,
    inside,
    keys_at,
    make_plot,
    value_brushes,
    value_range,
)
from PyHydroGeophysX.qt_apps.widgets.survey.selection import SurveySelection
from PyHydroGeophysX.survey import attributes
from PyHydroGeophysX.survey.layout import SurveyLayout
from PyHydroGeophysX.survey.pseudo import PseudoPoints

#: Legends of the pseudo-depth conventions (English source text; see survey.pseudo.CONVENTIONS).
CONVENTION_TEXTS = (
    "Pseudo-depth: |AM|/2 (pole-dipole), |AB-MN midpoints|/2 (B on the line)",
    "Pseudo-depth: 0.19 x electrode spread (Edwards 1977)",
)
#: Attributes usually drawn on a log scale.
LOG_ATTRIBUTES = attributes.LOG_SCALE | {"rho_a", "rhoa", "k"}


class SurveySectionView(QWidget):
    """The section view; feed it with :meth:`set_data`."""

    def __init__(
        self, selection: SurveySelection, parent: QWidget | None = None, *, colormaps: Any = None
    ) -> None:
        super().__init__(parent)
        self._selection = selection
        self._settings = Settings("section")
        self._layout: SurveyLayout | None = None
        self._pseudo: PseudoPoints | None = None
        self._colour = QComboBox()
        self._colour.setToolTip(
            QCoreApplication.translate("PHGX", "Colour the pseudo-depth points by one of their values")
        )
        self._colour.currentIndexChanged.connect(self._on_attribute)
        self._log = QCheckBox(QCoreApplication.translate("PHGX", "Log scale"))
        self._log.toggled.connect(self.redraw)
        self._colormap = cmaps.ColormapChooser(cmaps.SURVEY, "Spectral_r", shared=colormaps, parent=self)
        self._colormap.colormapChanged.connect(lambda _name: self.redraw())
        self._range = ColorRange(self, what="the pseudo-depth points' colours")
        self._range.changed.connect(self.redraw)
        self._terrain = QCheckBox(QCoreApplication.translate("PHGX", "Terrain"))
        self._terrain.setChecked(self._settings.get("terrain", True))
        self._terrain.toggled.connect(self._on_terrain)
        self._box = QCheckBox(QCoreApplication.translate("PHGX", "Box select"))
        self._box.setToolTip(
            QCoreApplication.translate("PHGX", "Drag a box to select the readings inside it")
        )
        self._plot, self._view = make_plot(self)
        self._view.sigBoxSelected.connect(self._on_box)
        self._box.toggled.connect(self._view.set_selecting)
        self._bar = ColorBar(self._plot.getPlotItem())
        self._legend = QLabel()
        self._legend.setWordWrap(True)
        controls = FlowLayout(spacing=6)
        controls.addWidget(group(QCoreApplication.translate("PHGX", "Colour by"), self._colour))
        controls.addWidget(self._log)
        controls.addWidget(self._colormap)
        controls.addWidget(self._range)
        controls.addWidget(self._terrain)
        controls.addWidget(self._box)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(controls)
        layout.addWidget(self._plot, 1)
        layout.addWidget(self._legend)
        self._selected = pg.ScatterPlotItem(
            size=11, pen=pg.mkPen("#111827", width=1.6), brush=None, symbol="o"
        )
        self._current = pg.ScatterPlotItem(size=9, pen=pg.mkPen("#f59e0b", width=1.6), brush=None, symbol="o")
        selection.groupChanged.connect(lambda _g: self._mark())
        selection.keysChanged.connect(lambda _k: self._mark())
        length_units.notifier().changed.connect(lambda _u: self._label_axes())
        self._label_axes()

    def set_data(self, layout: SurveyLayout | None, pseudo: PseudoPoints | None) -> None:
        self._layout = layout
        self._pseudo = pseudo
        names = sorted(pseudo.attrs) if pseudo is not None else []
        current = self._colour.currentData()
        self._colour.blockSignals(True)
        self._colour.clear()
        self._colour.addItem(QCoreApplication.translate("PHGX", "None"), "")
        for name in names:
            self._colour.addItem(i18n.tr(name), name)
        index = self._colour.findData(current if current is not None else self._settings.get("attribute", ""))
        self._colour.setCurrentIndex(max(index, 0))
        self._colour.blockSignals(False)
        self._log.setChecked(str(self._colour.currentData() or "") in LOG_ATTRIBUTES)
        self.redraw()

    def plot_widget(self) -> pg.PlotWidget:
        return self._plot

    def attribute(self) -> str:
        """The value the pseudo-depth points are coloured by ("" for none)."""
        return str(self._colour.currentData() or "")

    def log_scale(self) -> bool:
        return self._log.isChecked()

    def _label_axes(self) -> None:
        length_units.pyqtgraph_axis(
            self._plot, "bottom", QCoreApplication.translate("PHGX", "Distance along the line")
        )
        length_units.pyqtgraph_axis(self._plot, "left", QCoreApplication.translate("PHGX", "Elevation"))

    def redraw(self) -> None:
        plot = self._plot
        plot.clear()
        self._bar.hide()
        layout, pseudo = self._layout, self._pseudo
        if layout is None:
            self._legend.setText(QCoreApplication.translate("PHGX", "No survey layout to show."))
            return
        if self._terrain.isChecked() and layout.topography is not None and layout.topography.distance.size:
            plot.plot(
                layout.topography.distance, layout.topography.elevation, pen=pg.mkPen("#4d7c0f", width=1.6)
            )
        along = layout.along()
        line = layout.line_points()
        plot.addItem(
            pg.ScatterPlotItem(
                along[line],
                layout.points.xyz[line, 2],
                symbol="t",
                size=7,
                brush=pg.mkBrush("#1f2937"),
                pen=None,
            )
        )
        legend = ""
        if pseudo is not None and pseudo.size:
            attribute = str(self._colour.currentData() or "")
            values = pseudo.attrs.get(attribute) if attribute else None
            log = self._log.isChecked()
            brushes: Any = pg.mkBrush("#6b7280")
            auto = value_range(values, log)
            if values is not None and auto is not None:
                limits = self._range.limits(*auto)
                brushes = value_brushes(values, self._colormap.colormap(), limits, log)
                label = i18n.tr(attribute) + (" [log10]" if log else "")
                self._bar.show(self._colormap.colormap(), limits, label)
            plot.addItem(pg.ScatterPlotItem(pseudo.along, pseudo.elevation, size=7, brush=brushes, pen=None))
            legend = i18n.tr(pseudo.legend)
        plot.addItem(self._current)
        plot.addItem(self._selected)
        self._mark()
        self._legend.setText(legend)  # i18n: as written
        self._legend.setVisible(bool(legend))

    def _mark(self) -> None:
        pseudo = self._pseudo
        if pseudo is None or not pseudo.size:
            self._current.setData([], [])
            self._selected.setData([], [])
            return
        current_group = self._selection.group()
        mine = (
            np.array([g == current_group for g in pseudo.group], bool)
            if current_group
            else np.zeros(pseudo.size, bool)
        )
        self._current.setData(pseudo.along[mine], pseudo.elevation[mine])
        chosen = set(self._selection.keys())
        picked = (
            np.array([k in chosen for k in pseudo.keys], bool)
            if chosen and pseudo.keys
            else np.zeros(pseudo.size, bool)
        )
        self._selected.setData(pseudo.along[picked], pseudo.elevation[picked])

    def _on_box(self, rect: QRectF) -> None:
        pseudo = self._pseudo
        if pseudo is None:
            return
        found = inside(np.column_stack([pseudo.along, pseudo.elevation]), rect)
        self._selection.set_keys(keys_at(pseudo.keys, list(found)))

    def _on_attribute(self, _index: int) -> None:
        attribute = str(self._colour.currentData() or "")
        self._settings.set("attribute", attribute)
        self._log.blockSignals(True)
        self._log.setChecked(attribute in LOG_ATTRIBUTES)
        self._log.blockSignals(False)
        self._range.unlock()
        self.redraw()

    def _on_terrain(self, on: bool) -> None:
        self._settings.set("terrain", bool(on))
        self.redraw()


__all__ = ["CONVENTION_TEXTS", "LOG_ATTRIBUTES", "SurveySectionView"]
