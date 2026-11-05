"""Plan of a survey: the points at their real coordinates, the current group's links.

The current group (shot, injection, site) is drawn in full and the other
groups' sources faded; a remote point is an arrow at the edge with its distance
unless "Include remote B" scales the plan to it. A click picks the group of the
point and its key; a box (with "Box select") picks the keys inside it.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pyqtgraph as pg
from PySide6.QtCore import QCoreApplication, QRectF, Signal
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
    symbol_of,
    value_brushes,
    value_range,
)
from PyHydroGeophysX.qt_apps.widgets.survey.selection import SurveySelection
from PyHydroGeophysX.survey.layout import SurveyLayout
from PyHydroGeophysX.survey.scene import ALWAYS_SHOWN, FADED, LINK_COLOURS, ROLE_STYLE

#: Role names as a legend shows them (English source text, translated when shown).
ROLE_NAMES = dict(
    (
        ("A", "Current electrode A"),
        ("B", "Current electrode B"),
        ("M", "Potential electrode M"),
        ("N", "Potential electrode N"),
        ("electrode", "Electrode"),
        ("site", "Site"),
        ("tx", "Transmitter"),
        ("rx", "Receiver"),
    )
)


def has_grouped_sources(layout: SurveyLayout | None) -> bool:
    """Whether ``layout`` has sources that belong to groups (the shots of a DC/IP line)."""
    if layout is None:
        return False
    points = layout.points
    return bool((points.where(("A", "B", "tx")) & np.array([bool(g) for g in points.group], bool)).any())


class SurveyPlanView(QWidget):
    """The plan view; feed it with :meth:`set_layout` and a shared :class:`SurveySelection`."""

    #: The user picked a point: its key (a tuple) and its group.
    pointPicked = Signal(object, str)

    def __init__(
        self, selection: SurveySelection, parent: QWidget | None = None, *, colormaps: Any = None
    ) -> None:
        super().__init__(parent)
        self._selection = selection
        self._settings = Settings("plan")
        self._layout: SurveyLayout | None = None
        self._spots: list[tuple[np.ndarray, list[Any], list[str]]] = []
        self._colour = QComboBox()
        self._colour.setToolTip(
            QCoreApplication.translate("PHGX", "Colour the points by one of their values")
        )
        self._colour.currentIndexChanged.connect(self.redraw)
        self._colormap = cmaps.ColormapChooser(cmaps.SURVEY, "turbo", shared=colormaps, parent=self)
        self._colormap.colormapChanged.connect(lambda _name: self.redraw())
        self._range = ColorRange(self, what="the points' colours")
        self._range.changed.connect(self.redraw)
        self._remote = QCheckBox(QCoreApplication.translate("PHGX", "Include remote B"))
        self._remote.setToolTip(
            QCoreApplication.translate(
                "PHGX",
                "Show a remote electrode where it is (rescales the plan); otherwise an arrow points to it.",
            )
        )
        self._remote.setChecked(self._settings.get("include_remote", False))
        self._remote.toggled.connect(self._on_remote)
        self._others = QCheckBox(QCoreApplication.translate("PHGX", "Other shots"))
        self._others.setToolTip(
            QCoreApplication.translate("PHGX", "Show the sources of the other groups, faded")
        )
        self._others.setChecked(self._settings.get("others", True))
        self._others.toggled.connect(self._on_others)
        self._box = QCheckBox(QCoreApplication.translate("PHGX", "Box select"))
        self._box.setToolTip(QCoreApplication.translate("PHGX", "Drag a box to select the points inside it"))
        self._plot, self._view = make_plot(self)
        self._plot.setAspectLocked(True)
        self._view.sigBoxSelected.connect(self._on_box)
        self._box.toggled.connect(self._view.set_selecting)
        self._bar = ColorBar(self._plot.getPlotItem())
        self._legend = self._plot.addLegend(offset=(8, 8))
        self._note = QLabel()
        self._note.setWordWrap(True)

        controls = FlowLayout(spacing=6)
        controls.addWidget(group(QCoreApplication.translate("PHGX", "Colour by"), self._colour))
        controls.addWidget(self._colormap)
        controls.addWidget(self._range)
        for widget in (self._others, self._remote, self._box):
            controls.addWidget(widget)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(controls)
        layout.addWidget(self._plot, 1)
        layout.addWidget(self._note)
        selection.groupChanged.connect(lambda _g: self.redraw())
        selection.keysChanged.connect(lambda _k: self._mark_selected())
        length_units.notifier().changed.connect(lambda _u: self._label_axes())
        self._selected = pg.ScatterPlotItem(size=16, pen=pg.mkPen("#f59e0b", width=2), brush=None)
        self._label_axes()

    # -- data ---------------------------------------------------------------
    def set_layout(self, layout: SurveyLayout | None) -> None:
        self._layout = layout
        self._others.setVisible(has_grouped_sources(layout))
        names = sorted(layout.points.attrs) if layout is not None else []
        current = self._colour.currentData()
        self._colour.blockSignals(True)
        self._colour.clear()
        self._colour.addItem(QCoreApplication.translate("PHGX", "Role"), "")
        for name in names:
            self._colour.addItem(i18n.tr(name), name)
        index = self._colour.findData(current)
        self._colour.setCurrentIndex(max(index, 0))
        self._colour.blockSignals(False)
        self.redraw()

    def plot_widget(self) -> pg.PlotWidget:
        return self._plot

    # -- drawing ------------------------------------------------------------
    def _label_axes(self) -> None:
        length_units.pyqtgraph_axis(self._plot, "bottom", QCoreApplication.translate("PHGX", "East"))
        length_units.pyqtgraph_axis(self._plot, "left", QCoreApplication.translate("PHGX", "North"))

    def redraw(self) -> None:
        plot = self._plot
        plot.clear()
        self._legend.clear()
        self._spots = []
        self._bar.hide()
        layout = self._layout
        if layout is None or layout.points.size == 0:
            self._note.setText(QCoreApplication.translate("PHGX", "No survey layout to show."))
            return
        points = layout.points
        include_remote = self._remote.isChecked()
        current_group = self._selection.group()
        in_group = np.array([g in ("", current_group) or not current_group for g in points.group], bool)
        in_group |= points.where(ALWAYS_SHOWN)
        remote = points.is_remote()
        attribute = str(self._colour.currentData() or "")
        values = points.attrs.get(attribute) if attribute else None
        limits = None
        if values is not None:
            auto = value_range(values)
            limits = self._range.limits(*auto) if auto is not None else None
        for role in dict.fromkeys(points.role):
            mask = points.where(role) & in_group & (~remote | include_remote)
            if not mask.any():
                continue
            colour, symbol, size = ROLE_STYLE[role]
            brushes: Any = pg.mkBrush(colour)
            if values is not None and limits is not None:
                brushes = value_brushes(values[mask], self._colormap.colormap(), limits)
            self._add_points(mask, symbol_of(symbol), size, brushes, i18n.tr(ROLE_NAMES.get(role, role)))
        if self._others.isChecked() and current_group:
            other = ~in_group & points.where(("A", "B", "tx")) & ~remote
            if other.any():
                self._add_points(
                    other, "t1", 7.0, pg.mkBrush(FADED), QCoreApplication.translate("PHGX", "Other shots")
                )
        self._draw_links(layout, in_group, include_remote)
        notes = self._draw_remote(layout, include_remote, in_group)
        if values is not None and limits is not None:
            self._bar.show(self._colormap.colormap(), limits, i18n.tr(attribute))
        here = points.where(ALWAYS_SHOWN, current_group) if current_group else np.zeros(points.size, bool)
        if here.any():
            ring = pg.ScatterPlotItem(
                points.xyz[here, 0],
                points.xyz[here, 1],
                symbol="o",
                size=22,
                brush=None,
                pen=pg.mkPen("#f59e0b", width=2.5),
            )
            plot.addItem(ring)
        plot.addItem(self._selected)
        self._mark_selected()
        if layout.crs:
            notes.append(QCoreApplication.translate("PHGX", "CRS: {0}").format(layout.crs.get("name", "")))
        self._note.setText("    ".join(notes))  # i18n: as written
        self._note.setVisible(bool(notes))

    def _add_points(self, mask: np.ndarray, symbol: str, size: float, brushes: Any, name: str) -> None:
        points = self._layout.points if self._layout is not None else None
        if points is None:
            return
        index = np.flatnonzero(mask)
        item = pg.ScatterPlotItem(
            points.xyz[index, 0],
            points.xyz[index, 1],
            symbol=symbol,
            size=size,
            brush=brushes,
            pen=pg.mkPen("#1f2937", width=0.6),
            data=index,
            name=name,
        )
        item.sigClicked.connect(self._on_clicked)
        self._plot.addItem(item)

    def _draw_links(self, layout: SurveyLayout, in_group: np.ndarray, include_remote: bool) -> None:
        links = layout.links
        if not links.size:
            return
        remote = layout.points.is_remote()
        current_group = self._selection.group()
        xyz = layout.points.xyz
        by_kind: dict[str, list[int]] = {}
        for i in range(links.size):
            if current_group and links.group[i] not in ("", current_group):
                continue
            if not current_group and links.size > 400:
                continue
            a, b = int(links.start[i]), int(links.end[i])
            if not include_remote and (remote[a] or remote[b]):
                continue
            by_kind.setdefault(links.kind[i], []).append(i)
        for kind, rows in by_kind.items():
            x = np.empty(2 * len(rows))
            y = np.empty(2 * len(rows))
            x[0::2], x[1::2] = xyz[links.start[rows], 0], xyz[links.end[rows], 0]
            y[0::2], y[1::2] = xyz[links.start[rows], 1], xyz[links.end[rows], 1]
            pen = pg.mkPen(LINK_COLOURS.get(kind, "#374151"), width=2)
            self._plot.plot(x, y, pen=pen, connect="pairs")

    def _draw_remote(self, layout: SurveyLayout, include_remote: bool, in_group: np.ndarray) -> list[str]:
        points = layout.points
        remote = np.flatnonzero(points.is_remote() & in_group)
        notes: list[str] = []
        if remote.size == 0:
            return notes
        line = layout.line_points()
        centre = points.xyz[line, :2].mean(axis=0) if line.any() else np.zeros(2)
        xmin, xmax, ymin, ymax, _, _ = layout.extent()
        half = 0.5 * max(xmax - xmin, ymax - ymin, layout.line_length())
        for index in remote:
            offset = points.xyz[index, :2] - centre
            distance = float(np.hypot(*offset))
            notes.append(
                QCoreApplication.translate("PHGX", "{0} {1}: {2:.2f} km away ({3:.0f}, {4:.0f})").format(
                    points.role[index], points.label[index], distance / 1000.0, *points.xyz[index, :2]
                )
            )
            if include_remote or distance == 0:
                continue
            direction = offset / distance
            tip = centre + direction * half * 1.1
            # ArrowItem angles are in screen pixels (y down), with 0 pointing left.
            angle = 180.0 - float(np.degrees(np.arctan2(direction[1], direction[0])))
            arrow = pg.ArrowItem(pos=(tip[0], tip[1]), angle=angle, headLen=16, brush=ROLE_STYLE["B"][0])
            self._plot.addItem(arrow)
            label = pg.TextItem(f"{points.role[index]} {distance / 1000.0:.2f} km", color=ROLE_STYLE["B"][0])
            label.setPos(tip[0], tip[1])
            self._plot.addItem(label)
        return notes

    def _mark_selected(self) -> None:
        layout = self._layout
        if layout is None:
            self._selected.setData([], [])
            return
        chosen = set(self._selection.keys())
        index = [i for i, key in enumerate(layout.points.keys) if key in chosen] if chosen else []
        xy = layout.points.xyz[index, :2] if index else np.zeros((0, 2))
        self._selected.setData(xy[:, 0], xy[:, 1], symbol="o")

    # -- picking ---------------------------------------------------------------
    def _on_clicked(self, _item: Any, spots: Any) -> None:
        layout = self._layout
        if layout is None or not len(spots):
            return
        index = int(spots[0].data())
        key = layout.points.keys[index] if layout.points.keys else ("point", layout.points.ids[index])
        group_name = layout.points.group[index]
        if group_name:
            self._selection.set_group(group_name)
        self._selection.set_keys([key])
        self.pointPicked.emit(key, group_name)

    def _on_box(self, rect: QRectF) -> None:
        layout = self._layout
        if layout is None:
            return
        found = inside(layout.points.xyz[:, :2], rect)
        self._selection.set_keys(keys_at(layout.points.keys, list(found)))

    def _on_remote(self, on: bool) -> None:
        self._settings.set("include_remote", bool(on))
        self.redraw()
        self._plot.autoRange()

    def _on_others(self, on: bool) -> None:
        self._settings.set("others", bool(on))
        self.redraw()


__all__ = ["ROLE_NAMES", "SurveyPlanView", "has_grouped_sources"]
