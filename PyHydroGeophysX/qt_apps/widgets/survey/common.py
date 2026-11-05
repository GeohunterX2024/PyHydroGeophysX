"""Pieces the survey views share: a selecting view box, value colours, a colour bar, settings.

:class:`SelectViewBox` keeps pyqtgraph's own pan and zoom (the main toolbar's
Pan and Zoom set its mouse mode) and adds a box-select mode: a left drag draws
the rubber band and reports the rectangle instead of zooming into it.
"""

from __future__ import annotations

import logging
from collections.abc import Sequence
from typing import Any

import numpy as np
import pyqtgraph as pg
from PySide6.QtCore import QPointF, QRectF, QSettings, Qt, Signal

from PyHydroGeophysX.qt_apps.widgets import colormaps as cmaps

_logger = logging.getLogger(__name__)

#: Studio settings group the survey views keep their choices under.
SETTINGS_GROUP = "survey"
#: Colour of a value that has none (NaN).
MISSING = "#c7c9cc"
#: The shared value names of ``survey.attributes`` (English source text), for the translation catalog.
ATTRIBUTE_TEXTS = (
    "Apparent resistivity (ohm.m)",
    "Chargeability (%)",
    "Geometric factor (m)",
    "Rejected (1) or kept (0)",
    "Error (%)",
    "Line peak (dB)",
    "Noise RMS",
    "SNR (dB)",
    "Elevation (m)",
    "Current (A)",
    "Primary voltage Vp",
)


class SelectViewBox(pg.ViewBox):
    """A ViewBox with a box-select mode; :attr:`sigBoxSelected` carries the view rectangle."""

    sigBoxSelected = Signal(object)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._selecting = False

    def set_selecting(self, on: bool) -> None:
        self._selecting = bool(on)

    def selecting(self) -> bool:
        return self._selecting

    def mouseDragEvent(self, ev: Any, axis: Any = None) -> None:
        if not self._selecting or ev.button() != Qt.MouseButton.LeftButton:
            super().mouseDragEvent(ev, axis)
            return
        ev.accept()
        if ev.isFinish():
            self.rbScaleBox.hide()
            start = self.mapToView(ev.buttonDownPos())
            end = self.mapToView(ev.pos())
            self.sigBoxSelected.emit(QRectF(QPointF(start), QPointF(end)).normalized())
        else:
            self.updateScaleBox(ev.buttonDownPos(), ev.pos())


def inside(xy: np.ndarray, rect: QRectF) -> np.ndarray:
    """Indices of the ``(n, 2)`` points inside ``rect`` (view coordinates)."""
    if xy.size == 0:
        return np.zeros(0, int)
    x, y = xy[:, 0], xy[:, 1]
    keep = (x >= rect.left()) & (x <= rect.right()) & (y >= rect.top()) & (y <= rect.bottom())
    return np.flatnonzero(keep & np.isfinite(x) & np.isfinite(y))


def make_plot(parent: Any = None) -> tuple[pg.PlotWidget, SelectViewBox]:
    """A plot widget on a :class:`SelectViewBox`, with a light grid."""
    box = SelectViewBox()
    plot = pg.PlotWidget(parent=parent, viewBox=box)
    plot.showGrid(x=True, y=True, alpha=0.2)
    plot.setMenuEnabled(False)
    return plot, box


def value_range(values: np.ndarray | None, log: bool = False) -> tuple[float, float] | None:
    """The 2nd to 98th percentile of the finite values (log10 of the positive ones with ``log``)."""
    if values is None:
        return None
    data = np.asarray(values, dtype=float)
    if log:
        data = np.log10(data[data > 0])
    data = data[np.isfinite(data)]
    if data.size == 0:
        return None
    lo, hi = float(np.percentile(data, 2)), float(np.percentile(data, 98))
    if hi <= lo:
        hi = lo + (abs(lo) * 0.01 or 1.0)
    return lo, hi


def value_brushes(
    values: np.ndarray, colormap: str, limits: tuple[float, float], log: bool = False
) -> list[Any]:
    """One brush per value on ``colormap`` between ``limits`` (log10 values with ``log``)."""
    data = np.asarray(values, dtype=float)
    if log:
        with np.errstate(divide="ignore", invalid="ignore"):
            data = np.where(data > 0, np.log10(data), np.nan)
    lo, hi = limits
    fraction = np.clip((data - lo) / (hi - lo if hi > lo else 1.0), 0.0, 1.0)
    cmap = cmaps.to_pyqtgraph(colormap)
    missing = pg.mkBrush(MISSING)
    brushes: list[Any] = []
    for value, f in zip(data, fraction, strict=True):
        brushes.append(pg.mkBrush(cmap.map(float(f), mode="qcolor")) if np.isfinite(value) else missing)
    return brushes


class ColorBar:
    """A colour bar at the right of a plot item, shown only while the plot is colour-mapped."""

    def __init__(self, plot_item: Any) -> None:
        self._plot_item = plot_item
        self._bar: Any = None

    def show(self, colormap: str, limits: tuple[float, float], label: str) -> None:
        cmap = cmaps.to_pyqtgraph(colormap)
        if self._bar is None:
            self._bar = pg.ColorBarItem(values=limits, colorMap=cmap, interactive=False, width=14)
            self._plot_item.layout.addItem(self._bar, 2, 5)  # i18n: as written
        self._bar.setColorMap(cmap)
        self._bar.setLevels(limits)
        self._bar.setVisible(True)
        try:
            self._bar.axis.setLabel(label)
        except AttributeError:
            _logger.debug("ColorBar.show: this pyqtgraph has no colour-bar axis label", exc_info=True)

    def hide(self) -> None:
        if self._bar is not None:
            self._bar.setVisible(False)


class Settings:
    """A survey view's remembered choices, under ``survey/<view>/<name>`` in the Studio settings."""

    def __init__(self, view: str) -> None:
        self._prefix = f"{SETTINGS_GROUP}/{view}/"

    def get(self, name: str, default: Any) -> Any:
        value = QSettings("PyHydroGeophysX", "Studio").value(self._prefix + name, default)
        if isinstance(default, bool):
            return value in (True, "true", "1", 1)
        if isinstance(default, float):
            try:
                return float(value)
            except (TypeError, ValueError):
                return default
        if isinstance(default, int):
            try:
                return int(value)
            except (TypeError, ValueError):
                return default
        return value if value is not None else default

    def set(self, name: str, value: Any) -> None:
        QSettings("PyHydroGeophysX", "Studio").setValue(self._prefix + name, value)


def symbol_of(name: str) -> str:
    """pyqtgraph symbol for a :data:`PyHydroGeophysX.survey.scene.ROLE_STYLE` symbol name."""
    return {
        "triangle": "t1",
        "triangle_down": "t",
        "square": "s",
        "diamond": "d",
        "circle": "o",
        "sphere": "o",
    }.get(name, "o")


def keys_at(keys: Sequence[Any], indices: Sequence[int]) -> list[Any]:
    return [keys[i] for i in indices if 0 <= i < len(keys)] if keys else []


__all__ = [
    "ATTRIBUTE_TEXTS",
    "MISSING",
    "SETTINGS_GROUP",
    "ColorBar",
    "SelectViewBox",
    "Settings",
    "inside",
    "keys_at",
    "make_plot",
    "symbol_of",
    "value_brushes",
    "value_range",
]
