"""Industry exchange formats for data and models (plan M3.4).

* Res2DInv general array (type 11) - ERT/IP data of a surface line;
* Surfer GRD, ASCII ``DSAA`` - a regular grid, blanks as Surfer's 1.70141e38;
* Geosoft XYZ - point columns by line, ``*`` for a dummy value;
* CSV - one row per cell of a :class:`~.protocol.ModelResultV2`, units in the header.

VTK export already exists (``visualization``). Every writer here has a reader
used by the round-trip tests; :func:`grid_section` puts a result's parameter
on the regular grid GRD needs, with the result's display mask applied.
"""

from __future__ import annotations

import csv
import re
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

import numpy as np

from PyHydroGeophysX.errors import DataValidationError

from .protocol import GridGeometry, LayeredGeometry, MeshGeometry, ModelResultV2

SURFER_BLANK = 1.70141e38
GEOSOFT_DUMMY = "*"
_HEADER_UNIT = re.compile(r"^(?P<name>.+?) \[(?P<unit>[^\]]+)\]$")


# -- Res2DInv ---------------------------------------------------------------------
def write_res2dinv_general(
    data: Any,
    path: str | Path,
    *,
    title: str = "PyHydroGeophysX export",
    measurement: str = "rhoa",
    ip_unit: str = "mV/V",
) -> Path:
    """Write a pyGIMLi ERT data container as a Res2DInv general-array file.

    ``measurement`` is "rhoa" (apparent resistivity) or "r" (transfer
    resistance). IP values are written when the container has nonzero ``ip``.
    Each row lists only the electrodes the array uses (a pole is left out), as
    the general-array layout does.
    """
    if measurement not in ("rhoa", "r"):
        raise DataValidationError("must be 'rhoa' or 'r'", field="measurement")
    if not data.haveData(measurement):
        raise DataValidationError(f"the data have no {measurement!r}", field="measurement")
    sensors = np.array([[p[0], p[1], p[2]] for p in data.sensors()], dtype=float)
    indices = np.column_stack([np.asarray(data[token]).astype(int) for token in ("a", "b", "m", "n")])
    values = np.asarray(data[measurement], dtype=float)
    ip = np.asarray(data["ip"], dtype=float) if data.haveData("ip") else np.zeros_like(values)
    has_ip = bool(np.any(ip != 0))
    x = sensors[:, 0]
    spacing = float(np.median(np.diff(np.unique(x)))) if len(np.unique(x)) > 1 else 1.0
    lines = [
        title,
        f"{spacing:g}",
        "11",
        "0",
        "Type of measurement (0=app. resistivity,1=resistance)",
        "0" if measurement == "rhoa" else "1",
        str(len(values)),
        "1",
        "1" if has_ip else "0",
    ]
    if has_ip:
        lines += ["Chargeability", ip_unit, "0.12 1.0"]
    for row, value, ip_value in zip(indices, values, ip, strict=True):
        used = [int(i) for i in row if i >= 0]
        coordinates = " ".join(f"{sensors[i, 0]:.6g} {sensors[i, 2]:.6g}" for i in used)
        line = f"{len(used)} {coordinates} {value:.10g}"
        lines.append(f"{line} {ip_value:.10g}" if has_ip else line)
    lines += ["0", "0", "0", "0", "0"]
    target = Path(path)
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return target


def read_res2dinv_general(path: str | Path) -> tuple[np.ndarray, Any]:
    """``(electrodes, table)`` of a Res2DInv general-array file (the package's reader)."""
    from PyHydroGeophysX.data_processing.ert_formats import parse_res2dinv_general

    return parse_res2dinv_general(path)


# -- Surfer GRD ---------------------------------------------------------------------
def write_surfer_grd(path: str | Path, x: Any, y: Any, z: Any) -> Path:
    """Write ``z[iy, ix]`` on node coordinates ``x`` and ``y`` as Surfer ASCII GRD; NaN is blank."""
    xs, ys = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
    grid = np.asarray(z, dtype=float)
    if grid.shape != (ys.size, xs.size):
        raise DataValidationError(f"z has shape {grid.shape}, expected {(ys.size, xs.size)}", field="z")
    if xs.size < 2 or ys.size < 2:
        raise DataValidationError("a GRD needs at least 2 x 2 nodes", field="z")
    if not (np.allclose(np.diff(xs), xs[1] - xs[0]) and np.allclose(np.diff(ys), ys[1] - ys[0])):
        raise DataValidationError("GRD nodes must be equally spaced", field="x/y")
    finite = grid[np.isfinite(grid)]
    lo, hi = (float(finite.min()), float(finite.max())) if finite.size else (0.0, 0.0)
    lines = [
        "DSAA",
        f"{xs.size} {ys.size}",
        f"{xs[0]:.10g} {xs[-1]:.10g}",
        f"{ys[0]:.10g} {ys[-1]:.10g}",
        f"{lo:.10g} {hi:.10g}",
    ]
    for row in grid:
        lines.append(" ".join(f"{SURFER_BLANK:.6g}" if not np.isfinite(v) else f"{v:.10g}" for v in row))
    target = Path(path)
    target.write_text("\n".join(lines) + "\n", encoding="ascii")
    return target


def read_surfer_grd(path: str | Path) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """``(x, y, z)`` of a Surfer ASCII GRD, blanks as NaN."""
    tokens = Path(path).read_text(encoding="ascii").split()
    if not tokens or tokens[0] != "DSAA":
        raise DataValidationError("not a Surfer ASCII grid (DSAA)", file=path)
    nx, ny = int(tokens[1]), int(tokens[2])
    x0, x1, y0, y1 = (float(t) for t in tokens[3:7])
    values = np.array([float(t) for t in tokens[9 : 9 + nx * ny]]).reshape(ny, nx)
    values[values >= SURFER_BLANK * 0.999] = np.nan
    return np.linspace(x0, x1, nx), np.linspace(y0, y1, ny), values


def grid_section(
    result: ModelResultV2,
    parameter: str,
    *,
    nx: int = 200,
    ny: int = 100,
    masked: bool = True,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """A 2-D result's parameter on a regular ``ny x nx`` node grid, for GRD.

    Meshes are interpolated linearly between cell centres (nothing outside
    their hull); grids are sampled at cell centres; layered lines become a
    distance-depth section (depth positive down, as a negative elevation).
    With ``masked`` the result's display mask blanks what the data do not
    constrain.
    """
    values = np.asarray(result.parameters[parameter].values, dtype=float).ravel().copy()
    if masked:
        mask = result.display_mask()[0]
        if mask is not None:
            values[~mask] = np.nan
    geometry = result.geometry
    if isinstance(geometry, MeshGeometry):
        if geometry.dim != 2:
            raise DataValidationError("only 2-D meshes make a GRD section", field="geometry")
        from scipy.interpolate import griddata

        centers = geometry.cell_centers
        xs = np.linspace(centers[:, 0].min(), centers[:, 0].max(), nx)
        ys = np.linspace(centers[:, 1].min(), centers[:, 1].max(), ny)
        gx, gy = np.meshgrid(xs, ys)
        keep = np.isfinite(values)
        grid = griddata(centers[keep], values[keep], (gx, gy), method="linear")
        # Blank where the nearest cell is masked, so interpolation does not bridge a cut.
        nearest = griddata(centers, np.isfinite(values).astype(float), (gx, gy), method="nearest")
        grid[nearest < 0.5] = np.nan
        return xs, ys, np.asarray(grid, dtype=float)
    if isinstance(geometry, GridGeometry):
        if len(geometry.edges) != 2:
            raise DataValidationError("only 2-D grids make a GRD section", field="geometry")
        ex, ey = (np.asarray(e, dtype=float) for e in geometry.edges)
        cx, cy = 0.5 * (ex[1:] + ex[:-1]), 0.5 * (ey[1:] + ey[:-1])
        cells = values.reshape(geometry.shape, order=geometry.order)  # (nx_cells, ny_cells)
        xs, ys = np.linspace(cx[0], cx[-1], nx), np.linspace(cy[0], cy[-1], ny)
        ix = np.clip(np.searchsorted(ex, xs, side="right") - 1, 0, cx.size - 1)
        iy = np.clip(np.searchsorted(ey, ys, side="right") - 1, 0, cy.size - 1)
        return xs, ys, cells[np.ix_(ix, iy)].T
    if isinstance(geometry, LayeredGeometry):
        positions = (
            np.arange(geometry.n_soundings, dtype=float) if geometry.positions is None else geometry.positions
        )
        tops = geometry.layer_tops()
        cells = values.reshape(geometry.n_soundings, geometry.n_layers)
        bottom = float(tops[:, -1].max()) * 1.25 or 1.0
        xs = np.linspace(float(np.min(positions)), float(np.max(positions)), nx)
        depths = np.linspace(0.0, bottom, ny)
        nearest_sounding = np.abs(xs[:, None] - np.asarray(positions)[None, :]).argmin(axis=1)
        grid = np.empty((ny, nx))
        for column, sounding in enumerate(nearest_sounding):
            layer = np.clip(
                np.searchsorted(tops[sounding], depths, side="right") - 1, 0, geometry.n_layers - 1
            )
            grid[:, column] = cells[sounding, layer]
        return xs, -depths[::-1], grid[::-1]
    raise DataValidationError(f"unknown geometry {type(geometry).__name__}", field="geometry")


# -- Geosoft XYZ -------------------------------------------------------------------------
def write_geosoft_xyz(
    path: str | Path,
    columns: Mapping[str, Any],
    *,
    lines: Sequence[Any] | None = None,
    title: str = "PyHydroGeophysX export",
) -> Path:
    """Write point columns as Geosoft XYZ; ``lines`` (one per row) splits them into ``Line`` blocks."""
    names = list(columns)
    table = np.column_stack([np.asarray(columns[name], dtype=float) for name in names])
    labels = np.asarray(lines) if lines is not None else np.zeros(table.shape[0], dtype=int)
    out = [f"/ {title}", "/ " + " ".join(names)]
    current: Any = None
    for label, row in zip(labels, table, strict=True):
        if label != current:
            out.append(f"Line {label}")
            current = label
        out.append(" ".join(GEOSOFT_DUMMY if not np.isfinite(v) else f"{v:.10g}" for v in row))
    target = Path(path)
    target.write_text("\n".join(out) + "\n", encoding="utf-8")
    return target


def read_geosoft_xyz(path: str | Path) -> tuple[dict[str, np.ndarray], np.ndarray]:
    """``(columns, line of each row)`` of a Geosoft XYZ file, dummies as NaN."""
    names: list[str] = []
    last_comment: list[str] = []
    rows: list[list[float]] = []
    labels: list[str] = []
    line = ""
    for raw in Path(path).read_text(encoding="utf-8").splitlines():
        text = raw.strip()
        if not text:
            continue
        if text.startswith("/"):
            if not rows:
                # The column names are the comment line just above the data.
                last_comment = text[1:].split()
            continue
        if not names:
            names = last_comment
        if text.lower().startswith(("line", "tie")):
            line = text.split(None, 1)[1] if " " in text else ""
            continue
        rows.append([float("nan") if t == GEOSOFT_DUMMY else float(t) for t in text.split()])
        labels.append(line)
    table = np.asarray(rows, dtype=float)
    if len(names) != table.shape[1]:
        names = [f"col{i}" for i in range(table.shape[1])]
    return {name: table[:, i] for i, name in enumerate(names)}, np.asarray(labels)


# -- CSV ------------------------------------------------------------------------------------
def write_cells_csv(path: str | Path, result: ModelResultV2) -> Path:
    """One row per cell: index, centre coordinates, every parameter with its unit, and the display mask."""
    geometry = result.geometry
    if isinstance(geometry, MeshGeometry):
        centers = geometry.cell_centers
        axes = ["x", "y", "z"] if geometry.dim == 3 else ["x", "z"]
    elif isinstance(geometry, GridGeometry):
        mids = [0.5 * (np.asarray(e)[1:] + np.asarray(e)[:-1]) for e in geometry.edges]
        mesh = np.meshgrid(*mids, indexing="ij")
        centers = np.column_stack([m.ravel(order=geometry.order) for m in mesh])
        axes = list(geometry.axes[: len(mids)])
    else:
        tops = geometry.layer_tops()
        thickness = np.diff(tops, axis=1)
        mid = np.hstack(
            [tops[:, :-1] + 0.5 * thickness, tops[:, -1:] + 0.5 * np.maximum(thickness[:, -1:], 1.0)]
        )
        positions = (
            np.arange(geometry.n_soundings, dtype=float) if geometry.positions is None else geometry.positions
        )
        centers = np.column_stack([np.repeat(positions, geometry.n_layers), mid.ravel()])
        axes = ["distance", "depth"]
    mask = result.display_mask()[0]
    header = ["cell", *[f"{a} [m]" for a in axes]]
    header += [f"{name} [{p.unit}]" for name, p in result.parameters.items()]
    header.append("shown")
    target = Path(path)
    with target.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(header)
        for index in range(geometry.n_cells):
            row: list[Any] = [index, *(f"{v:.10g}" for v in centers[index])]
            row += [f"{float(np.ravel(p.values)[index]):.10g}" for p in result.parameters.values()]
            row.append(1 if mask is None or mask[index] else 0)
            writer.writerow(row)
    return target


def read_cells_csv(path: str | Path) -> tuple[dict[str, np.ndarray], dict[str, str]]:
    """``(columns, units)`` of a :func:`write_cells_csv` file; column names without their unit."""
    with Path(path).open(newline="", encoding="utf-8") as stream:
        reader = csv.reader(stream)
        header = next(reader)
        rows = [[float(v) for v in row] for row in reader]
    table = np.asarray(rows, dtype=float)
    columns: dict[str, np.ndarray] = {}
    units: dict[str, str] = {}
    for i, label in enumerate(header):
        match = _HEADER_UNIT.match(label)
        name = match.group("name") if match else label
        if match:
            units[name] = match.group("unit")
        columns[name] = table[:, i]
    return columns, units


__all__ = [
    "GEOSOFT_DUMMY",
    "SURFER_BLANK",
    "grid_section",
    "read_cells_csv",
    "read_geosoft_xyz",
    "read_res2dinv_general",
    "read_surfer_grd",
    "write_cells_csv",
    "write_geosoft_xyz",
    "write_res2dinv_general",
    "write_surfer_grd",
]
