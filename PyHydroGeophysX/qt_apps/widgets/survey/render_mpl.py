"""Matplotlib renderer of a :class:`~PyHydroGeophysX.survey.scene.Scene3D`: the simple 3-D view.

It draws the same layers as the PyVista renderer, without a graphics card:
terrain as a translucent surface, points by symbol, links, labels, and the
pseudo-depth points coloured by value with a colour bar. Matplotlib has no depth
buffer, so overlapping layers are drawn in layer order; picking is by nearest
point in the projection, and there is no measuring tool or VTK export.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import numpy as np

from PyHydroGeophysX.qt_apps.widgets.survey.render3d import RenderStyle, matplotlib_view
from PyHydroGeophysX.survey.scene import LabelLayer, LineLayer, PointLayer, Scene3D, SurfaceLayer

_logger = logging.getLogger(__name__)

_MARKERS = {
    "triangle": "^",
    "triangle_down": "v",
    "square": "s",
    "diamond": "D",
    "circle": "o",
    "sphere": "o",
}


class MatplotlibCanvas:
    """A Matplotlib 3-D canvas with the Studio's navigation toolbar."""

    name = "matplotlib"
    features = frozenset({"pick", "parallel", "labels"})

    def __init__(self, parent: Any) -> None:
        import matplotlib as mpl
        from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
        from matplotlib.figure import Figure
        from PySide6.QtWidgets import QVBoxLayout, QWidget

        from PyHydroGeophysX.qt_apps.widgets.readout import navigation_toolbar
        from PyHydroGeophysX.visualization.styles.publication import cjk_fonts

        fonts = [f for f in cjk_fonts() if f not in mpl.rcParams["font.sans-serif"]]
        if fonts:
            mpl.rcParams["font.sans-serif"] = [*fonts, *mpl.rcParams["font.sans-serif"]]
        mpl.rcParams["axes.unicode_minus"] = False
        self.figure = Figure(figsize=(6.0, 4.5), layout="constrained")
        self.canvas = FigureCanvasQTAgg(self.figure)
        toolbar, readout = navigation_toolbar(self.canvas, parent)
        self.widget = QWidget(parent)
        column = QVBoxLayout(self.widget)
        column.setContentsMargins(0, 0, 0, 0)
        column.addWidget(toolbar)
        column.addWidget(self.canvas, 1)
        readout.setVisible(False)
        self._scene: Scene3D | None = None
        self._style = RenderStyle()
        self._axes: Any = None
        self._artists: list[tuple[Any, str]] = []
        self._pick: Any = None
        self._parallel = False
        self._preset = "oblique"
        self.canvas.mpl_connect("pick_event", self._picked)

    def render(self, scene: Scene3D, style: RenderStyle, *, keep_camera: bool = True) -> None:
        view = (self._axes.elev, self._axes.azim) if keep_camera and self._axes is not None else None
        self.figure.clear()
        self.figure.set_facecolor(style.background)
        ax = self.figure.add_subplot(111, projection="3d")
        self._axes, self._scene, self._style = ax, scene, style
        self._artists = []
        mappable = None
        for layer in scene.layers:
            if isinstance(layer, SurfaceLayer):
                ax.plot_surface(
                    layer.x, layer.y, layer.z, color=layer.color, alpha=layer.opacity * 0.8, linewidth=0
                )
            elif isinstance(layer, LineLayer) and layer.segments.size:
                from mpl_toolkits.mplot3d.art3d import Line3DCollection

                colors = list(layer.colors) if layer.colors else layer.color
                ax.add_collection3d(
                    Line3DCollection(layer.segments, colors=colors, linewidths=layer.width * 0.7)
                )
            elif isinstance(layer, PointLayer) and layer.xyz.size:
                xyz = layer.xyz
                marker = _MARKERS.get(layer.symbol, "o")
                size = layer.size**2 * (0.5 if layer.symbol == "sphere" else 0.7)
                if layer.values is not None and np.isfinite(layer.values).any():
                    clim = style.value_range or scene.value_range
                    artist = ax.scatter(
                        xyz[:, 0],
                        xyz[:, 1],
                        xyz[:, 2],
                        c=layer.values,
                        cmap=style.colormap,
                        vmin=clim[0] if clim else None,
                        vmax=clim[1] if clim else None,
                        s=size,
                        marker=marker,
                        depthshade=False,
                        picker=True,
                    )
                    mappable = artist
                else:
                    artist = ax.scatter(
                        xyz[:, 0],
                        xyz[:, 1],
                        xyz[:, 2],
                        color=layer.color,
                        s=size,
                        marker=marker,
                        alpha=layer.opacity,
                        depthshade=False,
                        picker=True,
                        edgecolors="#1f2937",
                        linewidths=0.4,
                    )
                self._artists.append((artist, layer.name))
            elif isinstance(layer, LabelLayer):
                for (x, y, z), text in zip(layer.xyz, layer.texts, strict=True):
                    ax.text(x, y, z, text, fontsize=8, color=layer.color)
        if mappable is not None:
            bar = self.figure.colorbar(mappable, ax=ax, shrink=0.6, pad=0.08)
            bar.set_label(style.value_label or scene.value_name)
        x0, x1, y0, y1, z0, z1 = scene.bounds
        span = [max(x1 - x0, 1e-6), max(y1 - y0, 1e-6), max(z1 - z0, 1e-6)]
        ax.set_box_aspect(span)
        ax.set_xlabel(style.x_title, fontsize=8)  # i18n: as written
        ax.set_ylabel(style.y_title, fontsize=8)  # i18n: as written
        ax.set_zlabel(style.z_title, fontsize=8)
        ax.tick_params(labelsize=7)
        ax.set_proj_type("ortho" if self._parallel else "persp")
        if view is not None:
            ax.view_init(*view)
        else:
            ax.view_init(*matplotlib_view(self._preset, style.line_azimuth))
        self.canvas.draw_idle()

    def set_camera(self, preset: str) -> None:
        self._preset = preset
        if self._axes is not None:
            self._axes.view_init(*matplotlib_view(preset, self._style.line_azimuth))
            self.canvas.draw_idle()

    def set_parallel(self, on: bool) -> None:
        self._parallel = bool(on)
        if self._axes is not None:
            self._axes.set_proj_type("ortho" if on else "persp")
            self.canvas.draw_idle()

    def set_measuring(self, on: bool, report: Any = None) -> None:
        """Not available in the simple view."""

    def set_pick_callback(self, callback: Any) -> None:
        self._pick = callback

    def _picked(self, event: Any) -> None:
        if self._pick is None or not getattr(event, "ind", None):
            return
        for artist, name in self._artists:
            if artist is event.artist:
                self._pick(name, int(event.ind[0]))
                return

    def screenshot(self, path: str | Path, scale: int = 2) -> Path:
        target = Path(path)
        self.figure.savefig(target, dpi=110 * scale, facecolor=self._style.background)
        return target

    def export_vtk(self, path: str | Path) -> Path:
        raise RuntimeError("VTK export needs the PyVista 3D view")

    def refresh(self) -> None:
        self.canvas.draw_idle()

    def close(self) -> None:
        _logger.debug("MatplotlibCanvas.close: nothing to release")


__all__ = ["MatplotlibCanvas"]
