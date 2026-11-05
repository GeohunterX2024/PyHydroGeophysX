"""PyVista renderer of a :class:`~PyHydroGeophysX.survey.scene.Scene3D`.

Electrodes and sources are glyphs (cones pointing down for electrodes and
current electrodes, cubes for sites), sized from the line length so they read
at any scale; pseudo-depth points are spheres coloured by their value with a
scalar bar; the terrain is a translucent surface. Rendering happens on demand
(``auto_update=False``), when the scene, the camera or the window changes.

:func:`scene_datasets` turns a scene into PyVista datasets without a window,
which is what the tests and the VTK export use.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import numpy as np

from PyHydroGeophysX.qt_apps.widgets.survey.render3d import RenderStyle, camera_vectors
from PyHydroGeophysX.survey.scene import LabelLayer, LineLayer, PointLayer, Scene3D, SurfaceLayer

_logger = logging.getLogger(__name__)

#: Glyph shape of each point symbol.
_GLYPHS = {
    "triangle": "cone_down",
    "triangle_down": "cone_down",
    "square": "cube",
    "diamond": "cube",
    "circle": "sphere",
}


_FONT_FILE: list[str | None] = []
#: ``vtkTextProperty`` family that reads a font file (``VTK_FONT_FILE``).
_VTK_FONT_FILE = 4


def cjk_font_file() -> str | None:
    """Path of the first CJK font Matplotlib finds (VTK's own fonts have no Chinese), or None."""
    if not _FONT_FILE:
        found = None
        try:
            from matplotlib import font_manager

            from PyHydroGeophysX.visualization.styles.publication import cjk_fonts

            for family in cjk_fonts():
                try:
                    found = font_manager.findfont(
                        font_manager.FontProperties(family=family), fallback_to_default=False
                    )
                    break
                except ValueError:
                    continue
        except ImportError:
            _logger.debug("cjk_font_file: Matplotlib is not available", exc_info=True)
        _FONT_FILE.append(found)
    return _FONT_FILE[0]


def use_font(text_property: Any) -> None:
    """Draw ``text_property`` with the CJK font file, when there is one."""
    path = cjk_font_file()
    if path is not None and text_property is not None:
        text_property.SetFontFamily(_VTK_FONT_FILE)
        text_property.SetFontFile(path)


def label_format(limits: tuple[float, float] | None) -> str:
    """A printf format with enough significant digits to tell the colour bar's labels apart."""
    if limits is None:
        return "%.3g"
    low, high = limits
    span = abs(high - low)
    size = max(abs(low), abs(high), 1e-300)
    if span <= 0:
        return "%.3g"
    digits = int(np.clip(np.ceil(np.log10(size / span)) + 2, 3, 8))
    return f"%.{digits}g"


def _glyph(pv: Any, kind: str, size: float) -> Any:
    if kind == "cube":
        return pv.Cube(x_length=size, y_length=size, z_length=size)
    if kind == "sphere":
        return pv.Sphere(radius=size / 2.0)
    return pv.Cone(direction=(0.0, 0.0, -1.0), height=size, radius=size * 0.45, resolution=16)


def _lines(pv: Any, segments: np.ndarray) -> Any:
    points = segments.reshape(-1, 3)
    n = segments.shape[0]
    cells = np.column_stack([np.full(n, 2), np.arange(0, 2 * n, 2), np.arange(1, 2 * n, 2)]).ravel()
    return pv.PolyData(points, lines=cells)


def scene_datasets(pv: Any, scene: Scene3D) -> dict[str, Any]:
    """The scene's layers as PyVista datasets, by layer name (labels left out)."""
    datasets: dict[str, Any] = {}
    for layer in scene.layers:
        if isinstance(layer, SurfaceLayer):
            datasets[layer.name] = pv.StructuredGrid(layer.x, layer.y, layer.z)
        elif isinstance(layer, PointLayer) and layer.xyz.size:
            cloud = pv.PolyData(np.asarray(layer.xyz, dtype=float))
            if layer.values is not None:
                cloud.point_data["value"] = np.asarray(layer.values, dtype=float)
            datasets[layer.name] = cloud
        elif isinstance(layer, LineLayer) and layer.segments.size:
            datasets[layer.name] = _lines(pv, layer.segments)
    return datasets


class PyVistaCanvas:
    """A ``QtInteractor`` drawing scenes; raises when the window cannot be created."""

    name = "pyvista"
    features = frozenset({"pick", "measure", "vtk", "parallel", "labels"})

    def __init__(self, parent: Any) -> None:
        from PyHydroGeophysX.visualization.pyvista_compat import try_import_pyvista

        ok, pv, interactor, error = try_import_pyvista()
        if not ok:
            raise RuntimeError(error or "PyVista is not available")
        self._pv = pv
        self.plotter = interactor(parent, auto_update=False)
        self.widget = self.plotter.interactor
        self._scene: Scene3D | None = None
        self._style = RenderStyle()
        self._datasets: dict[str, Any] = {}
        self._pick: Any = None
        self._measuring = False

    # -- drawing ------------------------------------------------------------
    def glyph_size(self, scene: Scene3D) -> float:
        x0, x1, y0, y1, _, _ = scene.bounds
        return max(float(np.hypot(x1 - x0, y1 - y0)) * 0.012, 0.2)

    def render(self, scene: Scene3D, style: RenderStyle, *, keep_camera: bool = True) -> None:
        pv, plotter = self._pv, self.plotter
        camera = plotter.camera_position if keep_camera and self._scene is not None else None
        plotter.clear()
        plotter.set_background(style.background)
        self._scene, self._style = scene, style
        size = self.glyph_size(scene)
        self._datasets = scene_datasets(pv, scene)
        scalar_shown = False
        for layer in scene.layers:
            data = self._datasets.get(layer.name)
            if isinstance(layer, SurfaceLayer) and data is not None:
                plotter.add_mesh(
                    data, color=layer.color, opacity=layer.opacity, smooth_shading=True, name=layer.name
                )
            elif isinstance(layer, LineLayer) and data is not None:
                colours = layer.colors or (layer.color,) * layer.segments.shape[0]
                for colour in dict.fromkeys(colours):
                    rows = [i for i, c in enumerate(colours) if c == colour]
                    plotter.add_mesh(
                        _lines(pv, layer.segments[rows]),
                        color=colour,
                        line_width=layer.width * 1.6,
                        render_lines_as_tubes=True,
                        name=f"{layer.name}:{colour}",
                    )
            elif isinstance(layer, PointLayer) and data is not None:
                scale = layer.size / 10.0
                if layer.symbol == "sphere":
                    kwargs: dict[str, Any] = {
                        "render_points_as_spheres": True,
                        "point_size": max(layer.size * 2.2, 8.0),
                        "name": layer.name,
                        "opacity": layer.opacity,
                    }
                    if layer.values is not None and np.isfinite(layer.values).any():
                        plotter.add_mesh(
                            data,
                            scalars="value",
                            cmap=style.colormap,
                            clim=style.value_range or scene.value_range,
                            nan_color="#c7c9cc",
                            show_scalar_bar=not scalar_shown,
                            scalar_bar_args={
                                "title": style.value_label or scene.value_name,
                                "vertical": False,
                                "position_x": 0.3,
                                "position_y": 0.03,
                                "width": 0.4,
                                "height": 0.06,
                                "title_font_size": 13,
                                "label_font_size": 11,
                                "n_labels": 3,
                                "fmt": label_format(style.value_range or scene.value_range),
                                "color": "#1f2937",
                            },
                            **kwargs,
                        )
                        scalar_shown = True
                        for bar in plotter.scalar_bars.values():
                            use_font(bar.GetTitleTextProperty())
                            use_font(bar.GetLabelTextProperty())
                    else:
                        plotter.add_mesh(data, color=layer.color, **kwargs)
                else:
                    glyph = _glyph(pv, _GLYPHS.get(layer.symbol, "sphere"), size * scale)
                    shapes = data.glyph(geom=glyph, scale=False, orient=False)
                    plotter.add_mesh(shapes, color=layer.color, opacity=layer.opacity, name=layer.name)
            elif isinstance(layer, LabelLayer) and layer.xyz.size:
                plotter.add_point_labels(
                    layer.xyz,
                    list(layer.texts),
                    font_size=13,
                    text_color=layer.color,
                    shape_color="#ffffff",
                    shape_opacity=0.7,
                    always_visible=True,
                    show_points=False,
                    name=layer.name,
                )
        axes = plotter.show_bounds(
            grid="back",
            location="outer",
            ticks="outside",
            xtitle=style.x_title,
            ytitle=style.y_title,
            ztitle=style.z_title,
            font_size=12,
            fmt="%.0f",
            color="#374151",
        )
        for axis in range(3):
            try:
                use_font(axes.GetTitleTextProperty(axis))
                use_font(axes.GetLabelTextProperty(axis))
            except (AttributeError, TypeError):
                _logger.debug("PyVistaCanvas.render: these axes have no per-axis text", exc_info=True)
        plotter.add_axes(xlabel="E", ylabel="N", zlabel="Z", line_width=2)
        if camera is not None:
            plotter.camera_position = camera
        else:
            self.set_camera("oblique")
        self._repaint()

    def _repaint(self) -> None:
        try:
            self.widget.update()
            self.plotter.render()
        except (RuntimeError, AttributeError):
            _logger.debug("PyVistaCanvas._repaint: the window is gone", exc_info=True)

    # -- view ---------------------------------------------------------------
    def set_camera(self, preset: str) -> None:
        if self._scene is None:
            return
        position, focal, up = camera_vectors(preset, self._scene, self._style.line_azimuth)
        self.plotter.camera_position = [position, focal, up]
        self.plotter.reset_camera()
        self.plotter.reset_camera_clipping_range()
        self._repaint()

    def set_parallel(self, on: bool) -> None:
        if on:
            self.plotter.enable_parallel_projection()
        else:
            self.plotter.disable_parallel_projection()
        self._repaint()

    def set_measuring(self, on: bool, report: Any = None) -> None:
        if on and not self._measuring:
            self.plotter.add_measurement_widget(callback=report)
        elif not on and self._measuring:
            self.plotter.clear_measure_widgets()
        self._measuring = bool(on)
        self._repaint()

    def set_pick_callback(self, callback: Any) -> None:
        """``callback(layer name, point index)`` on a right click on a point."""
        self._pick = callback
        try:
            self.plotter.enable_point_picking(
                callback=self._picked,
                show_message=False,
                show_point=False,
                use_picker=True,
                left_clicking=False,
            )
        except (TypeError, RuntimeError):
            _logger.debug("PyVistaCanvas.set_pick_callback: point picking unavailable", exc_info=True)

    def _picked(self, point: Any, *_args: Any) -> None:
        if self._pick is None or point is None or self._scene is None:
            return
        target = np.asarray(point, dtype=float)
        best: tuple[float, str, int] | None = None
        for layer in self._scene.layers:
            if isinstance(layer, PointLayer) and layer.xyz.size and layer.keys:
                distance = np.linalg.norm(layer.xyz - target, axis=1)
                index = int(np.argmin(distance))
                if best is None or distance[index] < best[0]:
                    best = (float(distance[index]), layer.name, index)
        if best is not None:
            self._pick(best[1], best[2])

    def screenshot(self, path: str | Path, scale: int = 2) -> Path:
        target = Path(path)
        self.plotter.screenshot(str(target), scale=scale)
        return target

    def export_vtk(self, path: str | Path) -> Path:
        target = Path(path).with_suffix(".vtm")
        blocks = self._pv.MultiBlock()
        for name, data in self._datasets.items():
            blocks[name] = data
        blocks.save(str(target))
        return target

    def refresh(self) -> None:
        self._repaint()

    def close(self) -> None:
        try:
            self.plotter.close()
        except (RuntimeError, AttributeError):
            _logger.debug("PyVistaCanvas.close: already closed", exc_info=True)


__all__ = ["PyVistaCanvas", "scene_datasets"]
