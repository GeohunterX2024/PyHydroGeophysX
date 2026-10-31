"""Model Viewer renderers that need nothing of the page: arrays, curve files, tables, models.

Each returns the widget to show (and, for an array stack, the open file it
keeps reading from, which the page closes before the run can be deleted).
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from PySide6.QtWidgets import QHBoxLayout, QLabel, QSpinBox, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget

from PyHydroGeophysX.qt_apps.widgets.array_viewer import ArrayViewer
from PyHydroGeophysX.qt_apps.widgets.curve_viewer import CurveViewer


def close_array_resource(resource: Any) -> None:
    try:
        mmap = getattr(resource, "_mmap", None)
        if mmap is not None:
            mmap.close()
        elif hasattr(resource, "close"):
            resource.close()
    except (OSError, ValueError):
        pass


def numpy_view(
    path: Path,
    renderer: str,
    artifact: Dict[str, Any],
    title: str,
    value_label: str,
    log_scale: bool,
    colormaps: Optional[Dict[str, str]] = None,
) -> Tuple[QWidget, List[Any]]:
    """A curve, an image or a stepped image of an .npy/.npz artifact."""
    loaded = np.load(
        path,
        allow_pickle=False,
        mmap_mode="r" if path.suffix.lower() == ".npy" else None,
    )
    keep_open = False
    try:
        if isinstance(loaded, np.lib.npyio.NpzFile):
            names = [
                name for name in loaded.files
                if np.asarray(loaded[name]).dtype.kind in "fiu"
            ]
            if not names:
                raise ValueError("NPZ contains no numeric arrays.")
            metadata = artifact.get("metadata")
            metadata = dict(metadata) if isinstance(metadata, dict) else {}
            requested = str(metadata.get("array_key") or "")
            chosen = requested if requested in names else names[0]
            array = np.array(loaded[chosen], copy=True)
            loaded.close()
        else:
            array = loaded
        # Keep semantic dispatch from the artifact (notably a 2-D curve
        # table).  Shape only upgrades/downgrades the generic array modes.
        if renderer == "array" and array.ndim >= 3:
            renderer = "array_stack"
        elif renderer == "array_stack" and array.ndim < 3:
            renderer = "curve" if array.ndim == 1 else "array"
        if renderer == "curve" or array.ndim == 1:
            values = np.array(array, copy=True)
            view = CurveViewer()
            if values.ndim == 2 and min(values.shape) >= 2:
                # A compact 2 x N / 3 x N array normally stores x and one
                # or two series by row; a tall N x K array stores columns.
                if values.shape[0] <= 4 and values.shape[1] > 2 * values.shape[0]:
                    values = values.T
                x = values[:, 0]
                for column in range(1, values.shape[1]):
                    view.add_curve(x, values[:, column], f"{value_label} {column}")
            else:
                values = values.ravel()
                view.add_curve(np.arange(values.size), values, value_label)
            return view, []
        if array.ndim == 2:
            values = np.array(array, copy=True)
            view = ArrayViewer(colormaps=colormaps); view.set_array(
                values,
                log=log_scale,
                value_label=value_label,
                title=title,
            )
            return view, []
        if array.ndim >= 3:
            host = QWidget(); layout = QVBoxLayout(host)
            controls = QHBoxLayout(); step = QSpinBox()
            step.setRange(0, array.shape[0] - 1)
            controls.addWidget(QLabel("Step / slice:")); controls.addWidget(step); controls.addStretch(1)
            view = ArrayViewer(colormaps=colormaps)
            sample = np.asarray(array).ravel()[::max(1, array.size // 250_000)]
            if log_scale:
                with np.errstate(divide="ignore", invalid="ignore"):
                    sample = np.log10(np.where(sample > 0, sample, np.nan))
            finite = sample[np.isfinite(sample)]
            limits = None
            if finite.size:
                lo, hi = np.percentile(finite, [2, 98])
                if hi <= lo:
                    half_span = 0.5 if log_scale else max(abs(float(lo)) * 0.05, 0.5)
                    lo, hi = float(lo) - half_span, float(hi) + half_span
                limits = (float(lo), float(hi))
            def show_slice(value: int) -> None:
                # Copy only the visible slice: the widget never owns a view
                # of the file mapping, so Delete Run can close it first.
                view.set_array(
                    np.array(array[value], copy=True),
                    autoscale=limits is None,
                    log=log_scale,
                    value_label=value_label,
                    title=f"{title} — slice {value + 1}",
                )
                if limits is not None:
                    view.set_levels(*limits)
            step.valueChanged.connect(show_slice); show_slice(0)
            layout.addLayout(controls); layout.addWidget(view, stretch=1)
            keep_open = True
            return host, [loaded]
        raise ValueError(f"Unsupported array shape {array.shape}.")
    finally:
        if not keep_open:
            close_array_resource(loaded)



def curve_file_view(path: Path) -> QWidget:
    values = np.genfromtxt(path, delimiter="," if path.suffix.lower() == ".csv" else None,
                           names=True, dtype=float, encoding="utf-8")
    names = list(values.dtype.names or [])
    if len(names) < 2:
        raise ValueError("Curve table needs at least two numeric columns.")
    view = CurveViewer()
    for name in names[1:]:
        view.add_curve(np.asarray(values[names[0]]), np.asarray(values[name]), name)
    return view


def table_view(path: Path) -> QWidget:
    delimiter = "\t" if path.suffix.lower() == ".tsv" else ","
    with path.open("r", encoding="utf-8", errors="replace", newline="") as stream:
        rows = list(csv.reader(stream, delimiter=delimiter))[:5000]
    columns = max((len(row) for row in rows), default=0)
    table = QTableWidget(len(rows), columns)
    for row_index, row in enumerate(rows):
        for col, value in enumerate(row):
            table.setItem(row_index, col, QTableWidgetItem(value))
    return table


def model_result_view(path: Path) -> QWidget:
    """A saved ModelResultV2, masked by default (plan M3.5)."""
    from PyHydroGeophysX.qt_apps.widgets.model_result_view import ModelResultView
    from PyHydroGeophysX.results.protocol import ModelResultV2

    view = ModelResultView()
    view.set_result(ModelResultV2.load(path))
    return view


__all__ = ["close_array_resource", "curve_file_view", "model_result_view", "numpy_view", "table_view"]
