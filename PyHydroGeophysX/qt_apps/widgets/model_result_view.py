"""Draw any ModelResultV2: mesh, grid or layered, one parameter at a time (plan M3.5).

What the data do not constrain - by coverage, depth of investigation or
resolution - is blank by default, and the caption under the plot says on what
basis; "Mask" shows everything when unticked. Meshes are drawn from the
result's own node and cell arrays, so no PyGIMLi is needed to view a saved
result.
"""

from __future__ import annotations

import logging
from PySide6.QtCore import QCoreApplication
from typing import Any

import numpy as np
from PySide6.QtWidgets import QCheckBox, QComboBox, QHBoxLayout, QLabel, QSpinBox, QVBoxLayout, QWidget

from PyHydroGeophysX.results.protocol import GridGeometry, LayeredGeometry, MeshGeometry, ModelResultV2
from PyHydroGeophysX.qt_apps import i18n

_logger = logging.getLogger(__name__)

#: Colour map by parameter name; others use the default.
_CMAPS = {"resistivity": "turbo", "conductivity": "turbo_r", "velocity": "viridis", "density_contrast": "RdBu_r",
          "susceptibility": "magma", "m": "plasma", "rho0": "turbo"}


class ModelResultView(QWidget):
    """A ModelResultV2 with a parameter chooser, a mask switch and the mask's basis as caption."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
        from matplotlib.figure import Figure

        self._result: ModelResultV2 | None = None
        self._parameter = QComboBox()
        self._parameter.currentIndexChanged.connect(self._redraw)
        self._mask = QCheckBox(QCoreApplication.translate("PHGX", "Mask"))
        self._mask.setChecked(True)
        self._mask.setToolTip(QCoreApplication.translate("PHGX", "Blank what the data do not constrain; the caption says by what."))
        self._mask.toggled.connect(self._redraw)
        self._slice = QSpinBox()
        self._slice.setPrefix(QCoreApplication.translate("PHGX", "z slice "))
        self._slice.valueChanged.connect(self._redraw)
        self._slice.setVisible(False)
        self._figure = Figure(figsize=(7, 4), layout="constrained")
        self._canvas = FigureCanvasQTAgg(self._figure)
        self._caption = QLabel()
        self._caption.setWordWrap(True)
        bar = QHBoxLayout()
        bar.addWidget(QLabel(QCoreApplication.translate("PHGX", "Parameter")))
        bar.addWidget(self._parameter)
        bar.addWidget(self._mask)
        bar.addWidget(self._slice)
        bar.addStretch(1)
        layout = QVBoxLayout(self)
        layout.addLayout(bar)
        layout.addWidget(self._canvas, stretch=1)
        layout.addWidget(self._caption)

    def set_result(self, result: ModelResultV2) -> None:
        self._result = result
        self._parameter.blockSignals(True)
        self._parameter.clear()
        for name, parameter in result.parameters.items():
            label = f"{name} [{parameter.unit}]" + (f" - {parameter.description}" if parameter.description else "")
            self._parameter.addItem(i18n.tr(label), name)
        self._parameter.blockSignals(False)
        geometry = result.geometry
        three_d_grid = isinstance(geometry, GridGeometry) and len(geometry.edges) == 3
        self._slice.setVisible(three_d_grid)
        if isinstance(geometry, GridGeometry) and three_d_grid:
            self._slice.setRange(0, geometry.shape[2] - 1)
            self._slice.setValue(geometry.shape[2] - 1)
        self._mask.setEnabled(result.display_mask()[0] is not None)
        self._redraw()

    def caption(self) -> str:
        return self._caption.text()

    def _values(self) -> tuple[np.ndarray, Any] | None:
        if self._result is None or self._parameter.currentData() is None:
            return None
        parameter = self._result.parameters[str(self._parameter.currentData())]
        values = np.asarray(parameter.values, dtype=float).ravel().copy()
        mask, basis = self._result.display_mask()
        if mask is not None and self._mask.isChecked():
            values[~mask] = np.nan
            self._caption.setText(QCoreApplication.translate("PHGX", "Masked: {0}.").format(basis))
        elif mask is not None:
            self._caption.setText(QCoreApplication.translate("PHGX", "Unmasked; the default mask would apply: {0}.").format(basis))
        else:
            self._caption.setText(QCoreApplication.translate("PHGX", "No coverage, DOI or resolution with this result: every cell is shown."))
        return values, parameter

    def _redraw(self, *_args: Any) -> None:
        self._figure.clear()
        prepared = self._values()
        if prepared is None or self._result is None:
            self._canvas.draw_idle()
            return
        values, parameter = prepared
        axes = self._figure.add_subplot(111)
        shown = np.log10(np.where(values > 0, values, np.nan)) if parameter.log_scale else values
        cmap = _CMAPS.get(parameter.name.split("_step")[0], "viridis")
        geometry = self._result.geometry
        artist = None
        try:
            if isinstance(geometry, MeshGeometry):
                artist = self._draw_mesh(axes, geometry, shown, cmap)
            elif isinstance(geometry, GridGeometry):
                artist = self._draw_grid(axes, geometry, shown, cmap)
            elif isinstance(geometry, LayeredGeometry):
                artist = self._draw_layered(axes, geometry, shown, cmap, parameter.log_scale)
        except (ValueError, IndexError) as exc:
            _logger.warning("cannot draw the result: %s", exc, exc_info=True)
            axes.text(0.5, 0.5, f"Cannot draw this result: {exc}", ha="center", transform=axes.transAxes)
        if artist is not None:
            label = f"{'log10 ' if parameter.log_scale else ''}{parameter.name} [{parameter.unit}]"
            self._figure.colorbar(artist, ax=axes, label=label)
        axes.set_title(f"{self._result.method} - {parameter.name}")
        self._canvas.draw_idle()

    @staticmethod
    def _draw_mesh(axes: Any, geometry: MeshGeometry, values: np.ndarray, cmap: str) -> Any:
        if geometry.dim != 2:
            axes.text(0.5, 0.5, "3-D mesh: open the VTK export for a volume view.", ha="center",
                      transform=axes.transAxes)
            return None
        from matplotlib.collections import PolyCollection

        polygons = [geometry.nodes[row[row >= 0]] for row in geometry.cells]
        collection = PolyCollection(polygons, array=np.ma.masked_invalid(values), cmap=cmap, edgecolors="none")
        axes.add_collection(collection)
        axes.autoscale_view()
        axes.set_aspect("equal")
        axes.set_xlabel("x [m]")
        axes.set_ylabel("z [m]")
        return collection

    def _draw_grid(self, axes: Any, geometry: GridGeometry, values: np.ndarray, cmap: str) -> Any:
        cells = values.reshape(geometry.shape, order=geometry.order)
        if len(geometry.edges) == 3:
            k = int(self._slice.value())
            cells = cells[:, :, k]
            axes.set_ylabel("y [m]")
            axes.set_aspect("equal")
            axes.set_title(QCoreApplication.translate("PHGX", "slice {0} of {1}").format(k + 1, geometry.shape[2]), loc="right", fontsize=8)
        else:
            axes.set_ylabel(f"{geometry.axes[1]} [m]")
        axes.set_xlabel(f"{geometry.axes[0]} [m]")
        return axes.pcolormesh(geometry.edges[0], geometry.edges[1], np.ma.masked_invalid(cells.T), cmap=cmap)

    @staticmethod
    def _draw_layered(axes: Any, geometry: LayeredGeometry, values: np.ndarray, cmap: str, log_scale: bool) -> Any:
        cells = values.reshape(geometry.n_soundings, geometry.n_layers)
        tops = geometry.layer_tops()
        bottom = float(tops[:, -1].max()) * 1.3 or 1.0
        if geometry.n_soundings == 1:
            edges = np.r_[tops[0], bottom]
            axes.step(np.r_[cells[0], cells[0][-1]], edges, where="post")
            axes.invert_yaxis()
            axes.set_ylabel(QCoreApplication.translate("PHGX", "depth [m]"))
            axes.set_xlabel(QCoreApplication.translate("PHGX", "log10 value") if log_scale else QCoreApplication.translate("PHGX", "value"))
            return None
        positions = (
            np.arange(geometry.n_soundings, dtype=float) if geometry.positions is None else geometry.positions
        )
        mids = 0.5 * (positions[1:] + positions[:-1])
        half = 0.5 * (positions[1] - positions[0]) if positions.size > 1 else 0.5
        x_edges = np.r_[positions[0] - half, mids, positions[-1] + half]
        depth_edges = np.r_[tops[0], bottom] if np.allclose(tops, tops[0]) else np.linspace(0.0, bottom, 60)
        grid = np.full((depth_edges.size - 1, geometry.n_soundings), np.nan)
        centers = 0.5 * (depth_edges[1:] + depth_edges[:-1])
        for s in range(geometry.n_soundings):
            layer = np.clip(np.searchsorted(tops[s], centers, side="right") - 1, 0, geometry.n_layers - 1)
            grid[:, s] = cells[s, layer]
        mesh = axes.pcolormesh(x_edges, depth_edges, np.ma.masked_invalid(grid), cmap=cmap)
        axes.invert_yaxis()
        axes.set_xlabel(QCoreApplication.translate("PHGX", "distance [m]"))
        axes.set_ylabel(QCoreApplication.translate("PHGX", "depth [m]"))
        return mesh


__all__ = ["ModelResultView"]
