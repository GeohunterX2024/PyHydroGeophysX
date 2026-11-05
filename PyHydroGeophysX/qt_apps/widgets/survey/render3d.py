"""What both 3-D renderers share: the style of a draw, camera presets, the backend choice.

:func:`choose_backend` decides between PyVista and the Matplotlib fallback once
per view: the fallback when ``PHGX_SURVEY_3D=simple`` is set, when "Use simple
3-D" is ticked in the Studio settings, under the offscreen Qt platform, or when
PyVista cannot be imported. A failure to create the PyVista window falls back
too (the view does that). Without a graphics driver VTK can end the process
outright, which Python cannot catch, hence the switch that needs no PyVista.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

import numpy as np

from PyHydroGeophysX.qt_apps.widgets.survey.common import Settings
from PyHydroGeophysX.survey.scene import Scene3D

#: Environment variable that forces the simple (Matplotlib) 3-D view.
SIMPLE_3D_ENV = "PHGX_SURVEY_3D"
#: Camera presets: key -> (elevation, azimuth offset from the line) in degrees.
CAMERA_PRESETS = {
    "top": (90.0, 0.0),
    "along": (12.0, 0.0),
    "across": (8.0, 90.0),
    "oblique": (30.0, 45.0),
}


@dataclass(frozen=True)
class RenderStyle:
    """How values are coloured and how the axes are named, for one draw."""

    colormap: str = "turbo"
    value_label: str = ""
    value_range: tuple[float, float] | None = None
    x_title: str = "East (m)"
    y_title: str = "North (m)"
    z_title: str = "Elevation (m)"
    background: str = "#ffffff"
    line_azimuth: float = 0.0


def simple_3d_setting() -> bool:
    return bool(Settings("3d").get("simple", False))


def set_simple_3d_setting(on: bool) -> None:
    Settings("3d").set("simple", bool(on))


def choose_backend() -> tuple[str, str]:
    """``("pyvista" | "matplotlib", reason)``; the reason is empty for PyVista."""
    if os.environ.get(SIMPLE_3D_ENV, "").strip().lower() in ("simple", "matplotlib", "mpl", "off", "0"):
        return "matplotlib", f"{SIMPLE_3D_ENV} asks for the simple 3D view"
    if simple_3d_setting():
        return "matplotlib", "the simple 3D view is chosen in the options"
    from PyHydroGeophysX.visualization.pyvista_compat import try_import_pyvista

    ok, _pv, _interactor, error = try_import_pyvista()
    if not ok:
        return "matplotlib", error or "PyVista is not available"
    return "pyvista", ""


def camera_vectors(
    preset: str, scene: Scene3D, line_azimuth: float, distance_factor: float = 2.2
) -> tuple[tuple[float, float, float], tuple[float, float, float], tuple[float, float, float]]:
    """``(position, focal point, view up)`` of ``preset`` for ``scene``."""
    x0, x1, y0, y1, z0, z1 = scene.bounds
    focal = ((x0 + x1) / 2.0, (y0 + y1) / 2.0, (z0 + z1) / 2.0)
    span = max(x1 - x0, y1 - y0, z1 - z0, 1.0)
    elevation, offset = CAMERA_PRESETS.get(preset, CAMERA_PRESETS["oblique"])
    if preset == "top":
        return (focal[0], focal[1], focal[2] + distance_factor * span), focal, (0.0, 1.0, 0.0)
    azimuth = np.radians(line_azimuth + offset)
    horizontal = np.cos(np.radians(elevation))
    direction = np.array(
        [-np.sin(azimuth) * horizontal, -np.cos(azimuth) * horizontal, np.sin(np.radians(elevation))]
    )
    position = np.asarray(focal) + direction * distance_factor * span
    return (float(position[0]), float(position[1]), float(position[2])), focal, (0.0, 0.0, 1.0)


def matplotlib_view(preset: str, line_azimuth: float) -> tuple[float, float]:
    """``(elev, azim)`` for ``Axes3D.view_init``: azimuth measured from +x, counter-clockwise."""
    elevation, offset = CAMERA_PRESETS.get(preset, CAMERA_PRESETS["oblique"])
    if preset == "top":
        return 90.0, -90.0
    compass = line_azimuth + offset + 180.0
    return elevation, float((90.0 - compass) % 360.0)


__all__ = [
    "CAMERA_PRESETS",
    "SIMPLE_3D_ENV",
    "RenderStyle",
    "camera_vectors",
    "choose_backend",
    "matplotlib_view",
    "set_simple_3d_setting",
    "simple_3d_setting",
]
