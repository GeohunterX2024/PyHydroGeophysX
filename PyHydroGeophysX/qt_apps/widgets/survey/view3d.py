"""The 3-D survey view: PyVista when the machine can, Matplotlib when it cannot.

Both renderers draw the same :class:`~PyHydroGeophysX.survey.scene.Scene3D`;
what one of them lacks (the measuring tool, VTK export) is greyed out in the
options with the reason. The options panel folds away; every choice is kept
per view in the Studio settings.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from PySide6.QtCore import QCoreApplication
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFileDialog,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from PyHydroGeophysX.qt_apps import i18n
from PyHydroGeophysX.qt_apps.widgets import colormaps as cmaps
from PyHydroGeophysX.qt_apps.widgets import length_units
from PyHydroGeophysX.qt_apps.widgets.survey.common import Settings
from PyHydroGeophysX.qt_apps.widgets.survey.options import CollapsiblePanel
from PyHydroGeophysX.qt_apps.widgets.survey.render3d import (
    RenderStyle,
    choose_backend,
    set_simple_3d_setting,
    simple_3d_setting,
)
from PyHydroGeophysX.qt_apps.widgets.survey.selection import SurveySelection
from PyHydroGeophysX.survey.layout import Key, LineFrame, SurveyLayout
from PyHydroGeophysX.survey.pseudo import PseudoPoints
from PyHydroGeophysX.survey.scene import PointLayer, Scene3D, SceneOptions, build_scene

_logger = logging.getLogger(__name__)
#: What a renderer raises when its window or a draw fails (VTK reports GL failures as RuntimeError).
_CANVAS_ERRORS = (RuntimeError, OSError, ValueError, TypeError, AttributeError, IndexError, ImportError)

#: Camera preset names (English source text, translated when shown).
CAMERA_NAMES = dict(
    (("top", "Top"), ("along", "Along the line"), ("across", "Across the line"), ("oblique", "Oblique"))
)
#: Layer switches: option field -> (label, default) (English source text).
LAYER_SWITCHES = {
    "show_terrain": ("Terrain", True),
    "show_other_groups": ("Other shots", True),
    "show_links": ("Current and potential pairs", True),
    "show_pseudo": ("Pseudo-depth points", True),
    "show_labels": ("Labels", False),
    "include_remote": ("Include remote B", False),
}


class Survey3DView(QWidget):
    """The 3-D view; feed it with :meth:`set_data`."""

    def __init__(
        self,
        selection: SurveySelection,
        parent: QWidget | None = None,
        *,
        colormaps: Any = None,
        settings_key: str = "3d",
    ) -> None:
        super().__init__(parent)
        self._selection = selection
        self._settings = Settings(settings_key)
        self._layout: SurveyLayout | None = None
        self._pseudo: PseudoPoints | None = None
        self._scene: Scene3D | None = None
        self._pending = False
        self._first = True
        self._canvas: Any = None
        self.backend = ""
        self.reason = ""
        self._key_groups: dict[Key, str] = {}

        self._holder = QVBoxLayout()
        self._holder.setContentsMargins(0, 0, 0, 0)
        self._status = QLabel()
        self._status.setWordWrap(True)
        self._panel = CollapsiblePanel(QCoreApplication.translate("PHGX", "3D options"), settings_key)
        self._build_options(colormaps)
        canvas_column = QVBoxLayout()
        canvas_column.setContentsMargins(0, 0, 0, 0)
        canvas_column.addLayout(self._holder, 1)
        canvas_column.addWidget(self._status)
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.addLayout(canvas_column, 1)
        root.addWidget(self._panel)
        self._make_canvas()
        selection.groupChanged.connect(lambda _g: self._request())
        selection.keysChanged.connect(lambda _k: self._request())
        length_units.notifier().changed.connect(lambda _u: self._request())

    # -- options ------------------------------------------------------------
    def _build_options(self, colormaps: Any) -> None:
        body = self._panel.body_layout
        layers = QGroupBox(QCoreApplication.translate("PHGX", "Layers"))
        column = QVBoxLayout(layers)
        self._switches: dict[str, QCheckBox] = {}
        for field, (label, default) in LAYER_SWITCHES.items():
            box = QCheckBox(i18n.tr(label))
            box.setChecked(self._settings.get(field, default))
            box.toggled.connect(lambda on, f=field: self._on_option(f, on))
            column.addWidget(box)
            self._switches[field] = box
        body.addWidget(layers)

        look = QGroupBox(QCoreApplication.translate("PHGX", "Appearance"))
        grid = QGridLayout(look)
        self._colour = QComboBox()
        self._colour.currentIndexChanged.connect(
            lambda _i: self._on_option("colour_by", self._colour.currentData())
        )
        self._colormap = cmaps.ColormapChooser(cmaps.SURVEY, "Spectral_r", shared=colormaps, parent=self)
        self._colormap.colormapChanged.connect(lambda _n: self._request())
        self._exaggeration = QDoubleSpinBox()
        self._exaggeration.setRange(0.5, 50.0)
        self._exaggeration.setSingleStep(0.5)
        self._exaggeration.setSuffix(" \u00d7")
        self._exaggeration.setValue(self._settings.get("exaggeration", 1.0))
        self._exaggeration.setToolTip(
            QCoreApplication.translate("PHGX", "Vertical exaggeration of elevations and depths")
        )
        self._exaggeration.valueChanged.connect(lambda v: self._on_option("exaggeration", v))
        self._size = QDoubleSpinBox()
        self._size.setRange(0.3, 4.0)
        self._size.setSingleStep(0.1)
        self._size.setValue(self._settings.get("point_scale", 1.0))
        self._size.valueChanged.connect(lambda v: self._on_option("point_scale", v))
        self._depth = QDoubleSpinBox()
        self._depth.setRange(0.0, 1.0e5)
        self._depth.setDecimals(1)
        self._depth.setSpecialValueText(QCoreApplication.translate("PHGX", "All"))
        self._depth.setSuffix(" m")
        self._depth.setValue(self._settings.get("max_depth", 0.0))
        self._depth.setToolTip(
            QCoreApplication.translate(
                "PHGX", "Show pseudo-depth points down to this depth (All: every point)"
            )
        )
        self._depth.valueChanged.connect(lambda v: self._on_option("max_depth", v))
        rows = (
            (QCoreApplication.translate("PHGX", "Colour by"), self._colour),
            (QCoreApplication.translate("PHGX", "Colour map"), self._colormap),
            (QCoreApplication.translate("PHGX", "Exaggeration"), self._exaggeration),
            (QCoreApplication.translate("PHGX", "Point size"), self._size),
            (QCoreApplication.translate("PHGX", "Max pseudo-depth"), self._depth),
        )
        for row, (text, widget) in enumerate(rows):
            grid.addWidget(QLabel(text), row, 0)  # i18n: as written
            grid.addWidget(widget, row, 1)
        body.addWidget(look)

        view = QGroupBox(QCoreApplication.translate("PHGX", "View"))
        grid = QGridLayout(view)
        for index, (key, text) in enumerate(CAMERA_NAMES.items()):
            button = QPushButton(i18n.tr(text))
            button.clicked.connect(lambda _c=False, k=key: self.set_camera(k))
            grid.addWidget(button, index // 2, index % 2)
        self._parallel = QCheckBox(QCoreApplication.translate("PHGX", "Parallel projection"))
        self._parallel.setChecked(self._settings.get("parallel", False))
        self._parallel.toggled.connect(self._on_parallel)
        grid.addWidget(self._parallel, 2, 0, 1, 2)
        body.addWidget(view)

        tools = QGroupBox(QCoreApplication.translate("PHGX", "Tools"))
        column = QVBoxLayout(tools)
        self._measure = QCheckBox(QCoreApplication.translate("PHGX", "Measure distance"))
        self._measure.toggled.connect(self._on_measure)
        self._shot = QPushButton(QCoreApplication.translate("PHGX", "Screenshot…"))
        self._shot.clicked.connect(lambda: self.save_screenshot())
        self._vtk = QPushButton(QCoreApplication.translate("PHGX", "Export VTK…"))
        self._vtk.clicked.connect(lambda: self.export_vtk())
        self._simple = QCheckBox(QCoreApplication.translate("PHGX", "Use simple 3D (no graphics card)"))
        self._simple.setToolTip(
            QCoreApplication.translate(
                "PHGX",
                "Draw with Matplotlib, not PyVista: slower, but works without a graphics driver",
            )
        )
        self._simple.setChecked(simple_3d_setting())
        self._simple.toggled.connect(self._on_simple)
        self._hint = QLabel()
        self._hint.setWordWrap(True)
        for widget in (self._measure, self._shot, self._vtk, self._simple, self._hint):
            column.addWidget(widget)
        body.addWidget(tools)
        body.addStretch(1)

    def options(self) -> SceneOptions:
        depth = float(self._depth.value())
        return SceneOptions(
            exaggeration=float(self._exaggeration.value()),
            include_remote=self._switches["include_remote"].isChecked(),
            show_terrain=self._switches["show_terrain"].isChecked(),
            show_other_groups=self._switches["show_other_groups"].isChecked(),
            show_links=self._switches["show_links"].isChecked(),
            show_pseudo=self._switches["show_pseudo"].isChecked(),
            show_labels=self._switches["show_labels"].isChecked(),
            colour_by=str(self._colour.currentData() or ""),
            point_scale=float(self._size.value()),
            group=self._selection.group(),
            depth_range=(0.0, depth) if depth > 0 else None,
        )

    # -- the canvas ---------------------------------------------------------
    def _make_canvas(self) -> None:
        if self._canvas is not None:
            self._holder.removeWidget(self._canvas.widget)
            self._canvas.close()
            self._canvas.widget.setParent(None)
            self._canvas.widget.deleteLater()
            self._canvas = None
        backend, reason = choose_backend()
        canvas: Any = None
        if backend == "pyvista":
            try:
                from PyHydroGeophysX.qt_apps.widgets.survey.render_pyvista import PyVistaCanvas

                canvas = PyVistaCanvas(self)
            except _CANVAS_ERRORS as exc:
                _logger.warning("Survey3DView: PyVista window failed (%s); using the simple 3D view", exc)
                backend, reason = "matplotlib", str(exc)
        if canvas is None:
            from PyHydroGeophysX.qt_apps.widgets.survey.render_mpl import MatplotlibCanvas

            canvas = MatplotlibCanvas(self)
        self._canvas = canvas
        self.backend, self.reason = backend, reason
        canvas.set_pick_callback(self._picked)
        canvas.set_parallel(self._parallel.isChecked())
        self._holder.addWidget(canvas.widget, 1)
        has = canvas.features
        self._measure.setEnabled("measure" in has)
        self._vtk.setEnabled("vtk" in has)
        why = QCoreApplication.translate("PHGX", "Needs the PyVista 3D view")
        self._measure.setToolTip("" if "measure" in has else why)  # i18n: as written
        self._vtk.setToolTip("" if "vtk" in has else why)  # i18n: as written
        if backend == "pyvista":
            self._hint.setText(
                QCoreApplication.translate(
                    "PHGX", "Drag to rotate, scroll to zoom; right-click a point to select it."
                )
            )
            self._status.setText("")
        else:
            self._hint.setText(
                QCoreApplication.translate("PHGX", "Drag to rotate; click a point to select it.")
            )
            self._status.setText(
                QCoreApplication.translate("PHGX", "Simple 3D view: {0}").format(i18n.tr(reason))
            )
        self._status.setVisible(bool(self._status.text()))
        self._first = True
        self._request()

    # -- data ---------------------------------------------------------------
    def set_data(self, layout: SurveyLayout | None, pseudo: PseudoPoints | None) -> None:
        from PyHydroGeophysX.qt_apps.widgets.survey.plan_view import has_grouped_sources

        self._layout, self._pseudo = layout, pseudo
        self._switches["show_other_groups"].setVisible(has_grouped_sources(layout))
        self._switches["show_pseudo"].setVisible(pseudo is not None)
        self._depth.setEnabled(pseudo is not None)
        self._key_groups = {}
        if layout is not None and layout.points.keys:
            self._key_groups.update(
                {k: g for k, g in zip(layout.points.keys, layout.points.group, strict=True) if g}
            )
        if pseudo is not None and pseudo.keys:
            self._key_groups.update({k: g for k, g in zip(pseudo.keys, pseudo.group, strict=True) if g})
        names = sorted(set(pseudo.attrs) if pseudo is not None else set())
        names += sorted(set(layout.points.attrs) - set(names)) if layout is not None else []
        wanted = self._colour.currentData() or self._settings.get("colour_by", "")
        self._colour.blockSignals(True)
        self._colour.clear()
        self._colour.addItem(QCoreApplication.translate("PHGX", "None"), "")
        for name in names:
            self._colour.addItem(i18n.tr(name), name)
        self._colour.setCurrentIndex(max(self._colour.findData(wanted), 0))
        self._colour.blockSignals(False)
        self._first = True
        self._request()

    def scene(self) -> Scene3D | None:
        return self._scene

    def _request(self) -> None:
        if self.isVisible():
            self.redraw()
        else:
            self._pending = True

    def showEvent(self, event: Any) -> None:
        super().showEvent(event)
        if self._pending:
            self.redraw()

    def redraw(self) -> None:
        self._pending = False
        layout = self._layout
        if layout is None or self._canvas is None:
            self._scene = None
            return
        options = self.options()
        scene = build_scene(layout, self._pseudo, options)
        self._scene = scene
        frame = layout.frame or LineFrame.fit(layout.points.xyz[layout.line_points()])
        unit = length_units.current()
        exaggerated = f" \u00d7{options.exaggeration:g}" if options.exaggeration != 1 else ""
        style = RenderStyle(
            colormap=self._colormap.colormap(),
            value_label=i18n.tr(options.colour_by),
            x_title=QCoreApplication.translate("PHGX", "East ({0})").format(unit),
            y_title=QCoreApplication.translate("PHGX", "North ({0})").format(unit),
            z_title=QCoreApplication.translate("PHGX", "Elevation ({0})").format(unit) + exaggerated,
            line_azimuth=frame.azimuth,
        )
        try:
            self._canvas.render(scene, style, keep_camera=not self._first)
        except _CANVAS_ERRORS as exc:
            _logger.warning("Survey3DView.redraw: %s", exc)
            self._status.setText(
                QCoreApplication.translate("PHGX", "The 3D view could not draw: {0}").format(exc)
            )
            self._status.setVisible(True)
            return
        self._first = False
        notes = [i18n.tr(n) for n in scene.notes]
        for role, label, distance in scene.remote:
            name = role if label in ("", role) else f"{role} {label}"
            notes.append(
                QCoreApplication.translate("PHGX", "{0}: {1:.2f} km from the line centre").format(
                    name, distance / 1000.0
                )
            )
        if self.backend == "matplotlib":
            notes.insert(
                0, QCoreApplication.translate("PHGX", "Simple 3D view: {0}").format(i18n.tr(self.reason))
            )
        self._status.setText("    ".join(notes))  # i18n: as written
        self._status.setVisible(bool(notes))

    # -- actions ------------------------------------------------------------
    def set_camera(self, preset: str) -> None:
        if self._canvas is not None:
            self._canvas.set_camera(preset)

    def save_screenshot(self, path: str | Path | None = None) -> Path | None:
        if self._canvas is None or self._scene is None:
            return None
        if path is None:
            chosen, _ = QFileDialog.getSaveFileName(
                self, QCoreApplication.translate("PHGX", "Save screenshot"), "survey_3d.png", "PNG (*.png)"
            )
            if not chosen:
                return None
            path = chosen
        return Path(self._canvas.screenshot(path))

    def export_vtk(self, path: str | Path | None = None) -> Path | None:
        if self._canvas is None or self._scene is None or "vtk" not in self._canvas.features:
            return None
        if path is None:
            chosen, _ = QFileDialog.getSaveFileName(
                self,
                QCoreApplication.translate("PHGX", "Export VTK"),
                "survey_3d.vtm",
                "VTK MultiBlock (*.vtm)",
            )
            if not chosen:
                return None
            path = chosen
        return Path(self._canvas.export_vtk(path))

    def _picked(self, layer_name: str, index: int) -> None:
        scene = self._scene
        layer = scene.layer(layer_name) if scene is not None else None
        if not isinstance(layer, PointLayer) or not layer.keys or index >= len(layer.keys):
            return
        key = layer.keys[index]
        group = self._key_groups.get(key, "")
        if group:
            self._selection.set_group(group)
        self._selection.set_keys([key])

    def _on_option(self, field: str, value: Any) -> None:
        self._settings.set(field, value)
        self._request()

    def _on_parallel(self, on: bool) -> None:
        self._settings.set("parallel", bool(on))
        if self._canvas is not None:
            self._canvas.set_parallel(on)

    def _on_measure(self, on: bool) -> None:
        if self._canvas is None:
            return
        self._canvas.set_measuring(on, self._measured)

    def _measured(self, a: Any, b: Any, distance: float) -> None:
        self._status.setText(
            QCoreApplication.translate("PHGX", "Distance: {0:.2f} m").format(float(distance))
        )
        self._status.setVisible(True)

    def _on_simple(self, on: bool) -> None:
        set_simple_3d_setting(on)
        self._make_canvas()

    def closeEvent(self, event: Any) -> None:
        if self._canvas is not None:
            self._canvas.close()
        super().closeEvent(event)


__all__ = ["CAMERA_NAMES", "LAYER_SWITCHES", "Survey3DView"]
