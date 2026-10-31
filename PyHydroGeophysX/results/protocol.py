"""ModelResultV2: one shape for every inverted model, single- or multi-parameter (plan M3.2).

A result has

* a geometry - an unstructured mesh (:class:`MeshGeometry`), a rectilinear
  grid (:class:`GridGeometry`) or layered soundings (:class:`LayeredGeometry`);
* named parameters, each with a registered unit (:class:`Parameter`); the
  names of spectral IP and static corrections are reserved with their units
  (:data:`RESERVED_PARAMETERS`) so engines that add them agree;
* the data fit: observed and predicted data, errors, residuals, and chi²
  overall and per data group (:class:`DataFit`);
* what the data constrain: coverage, depth of investigation, resolution, and
  the boolean cell masks made from them;
* uncertainties (``Parameter.std``), iteration history, metadata, provenance.

:meth:`ModelResultV2.display_mask` combines the masks a viewer shows by
default and says on what basis, for the legend. Nothing here needs PyGIMLi
or Qt; live engine objects (a ``pg.Mesh``) may ride along in ``native`` and
are not saved.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np

from PyHydroGeophysX.errors import DataValidationError

from .units import UNITS, require_unit

SCHEMA = "phgx-model-result-v2"

#: Parameter names with a fixed meaning and unit quantity: Cole-Cole/Pelton IP
#: (rho0, m, tau, c), static-shift factors, and the common single parameters.
RESERVED_PARAMETERS: dict[str, str] = {
    "resistivity": "resistivity",
    "conductivity": "conductivity",
    "rho0": "resistivity",
    "m": "chargeability",
    "tau": "time",
    "c": "dimensionless",
    "phase": "angle",
    "static_shift": "dimensionless",
    "velocity": "velocity",
    "slowness": "slowness",
    "density_contrast": "density",
    "susceptibility": "susceptibility",
    "water_content": "volumetric content",
}

#: Coverage cut of the ERT section views, log10 cumulative sensitivity
#: (``MeshResultView``'s default "Hide below" threshold).
COVERAGE_LOG10_THRESHOLD = -2.0
#: Resolution (diagonal of the resolution matrix) under which a cell is
#: taken as unresolved.
RESOLUTION_THRESHOLD = 0.05


@dataclass
class Parameter:
    """A named model parameter: one value per cell (or per sounding and layer), with its unit."""

    name: str
    values: np.ndarray
    unit: str
    log_scale: bool = False
    #: One standard deviation, in the same unit, or of log10 of the value when ``std_log10``.
    std: np.ndarray | None = None
    std_log10: bool = False
    description: str = ""

    def __post_init__(self) -> None:
        self.values = np.asarray(self.values, dtype=float)
        if self.std is not None:
            self.std = np.asarray(self.std, dtype=float)


@dataclass
class MeshGeometry:
    """An unstructured 2-D or 3-D mesh: node coordinates and each cell's node indices."""

    nodes: np.ndarray
    cells: np.ndarray
    cell_centers: np.ndarray
    dim: int
    kind: str = "mesh"

    @property
    def n_cells(self) -> int:
        return int(self.cell_centers.shape[0])


@dataclass
class GridGeometry:
    """A rectilinear grid: node coordinates along each axis; values in Fortran order."""

    edges: tuple[np.ndarray, ...]
    axes: tuple[str, ...] = ("x", "y", "z")
    order: str = "F"
    kind: str = "grid"

    @property
    def shape(self) -> tuple[int, ...]:
        return tuple(len(e) - 1 for e in self.edges)

    @property
    def n_cells(self) -> int:
        return int(np.prod(self.shape))


@dataclass
class LayeredGeometry:
    """Layered models of one or more soundings.

    ``thickness`` is ``(n_layers - 1,)`` shared by every sounding, or
    ``(n_soundings, n_layers - 1)``; the last layer is a half-space. Parameter
    values are ``(n_soundings, n_layers)``. ``positions`` are distances along
    the line; ``x``, ``y`` and ``elevation`` optional coordinates per sounding.
    """

    thickness: np.ndarray
    n_soundings: int = 1
    positions: np.ndarray | None = None
    x: np.ndarray | None = None
    y: np.ndarray | None = None
    elevation: np.ndarray | None = None
    kind: str = "layered"

    @property
    def n_layers(self) -> int:
        return int(np.asarray(self.thickness).shape[-1]) + 1

    @property
    def n_cells(self) -> int:
        return self.n_soundings * self.n_layers

    def layer_tops(self) -> np.ndarray:
        """``(n_soundings, n_layers)`` depth of each layer's top."""
        thickness = np.broadcast_to(
            np.asarray(self.thickness, dtype=float), (self.n_soundings, self.n_layers - 1)
        )
        return np.hstack([np.zeros((self.n_soundings, 1)), np.cumsum(thickness, axis=1)])


Geometry = MeshGeometry | GridGeometry | LayeredGeometry


@dataclass
class DataFit:
    """Observed and predicted data with their errors; chi² overall and per group.

    ``groups`` maps a group name (a frequency band, a moment, a sounding, a
    survey) to a boolean mask or index array over the data.
    """

    observed: np.ndarray | None = None
    predicted: np.ndarray | None = None
    error: np.ndarray | None = None
    groups: dict[str, np.ndarray] = field(default_factory=dict)
    chi2: float | None = None

    def residual(self) -> np.ndarray | None:
        """Error-weighted residual ``(observed - predicted) / error``, where all three are known."""
        if self.observed is None or self.predicted is None or self.error is None:
            return None
        misfit = np.asarray(self.observed) - np.asarray(self.predicted)
        residual: np.ndarray = misfit / np.asarray(self.error)
        return residual

    def chi2_by_group(self) -> dict[str, float]:
        """Mean squared weighted residual of each group (and ``"all"``)."""
        residual = self.residual()
        if residual is None:
            return {} if self.chi2 is None else {"all": float(self.chi2)}
        finite = np.isfinite(residual)
        out = {"all": float(np.mean(residual[finite] ** 2)) if finite.any() else float("nan")}
        for name, selector in self.groups.items():
            chosen = np.zeros(residual.shape, dtype=bool)
            chosen[np.asarray(selector)] = True
            values = residual[chosen & finite]
            out[name] = float(np.mean(values**2)) if values.size else float("nan")
        return out


@dataclass
class ModelResultV2:
    """An inverted model with its fit, what the data constrain, and where it came from."""

    method: str
    geometry: Geometry
    parameters: dict[str, Parameter]
    fit: DataFit | None = None
    #: Per cell: log10 cumulative sensitivity (``coverage_kind="log10_sensitivity"``)
    #: or ray coverage (``"rays"``, cells with none are unconstrained).
    coverage: np.ndarray | None = None
    coverage_kind: str = "log10_sensitivity"
    #: Depth of investigation per sounding (layered) or a per-cell DOI index.
    doi: np.ndarray | None = None
    resolution: np.ndarray | None = None
    masks: dict[str, np.ndarray] = field(default_factory=dict)
    history: list[dict[str, Any]] = field(default_factory=list)
    meta: dict[str, Any] = field(default_factory=dict)
    provenance: dict[str, Any] = field(default_factory=dict)
    #: Live engine objects (e.g. the ``pg.Mesh``); never saved.
    native: dict[str, Any] = field(default_factory=dict, repr=False, compare=False)

    # -- checks ------------------------------------------------------------------
    def validate(self) -> None:
        n_cells = self.geometry.n_cells
        if not self.parameters:
            raise DataValidationError("a result needs at least one parameter", field="parameters")
        for name, parameter in self.parameters.items():
            require_unit(f"parameters.{name}", parameter.unit)
            expected = RESERVED_PARAMETERS.get(name)
            if expected is not None and UNITS[parameter.unit].quantity != expected:
                raise DataValidationError(
                    f"{name} is reserved for {expected}, "
                    f"not {UNITS[parameter.unit].quantity} ({parameter.unit})",
                    field=f"parameters.{name}",
                )
            if parameter.values.size != n_cells:
                raise DataValidationError(
                    f"has {parameter.values.size} values for {n_cells} cells", field=f"parameters.{name}"
                )
            if parameter.std is not None and parameter.std.shape != parameter.values.shape:
                raise DataValidationError(
                    "std must have the shape of the values", field=f"parameters.{name}.std"
                )
        for name, mask in self.all_masks().items():
            if mask.dtype != np.bool_ or mask.size != n_cells:
                raise DataValidationError(f"must be {n_cells} booleans", field=f"masks.{name}")

    # -- masks ---------------------------------------------------------------------
    def all_masks(self) -> dict[str, np.ndarray]:
        """Stored masks plus those derived from coverage, DOI and resolution (True = shown)."""
        masks = {name: np.asarray(mask) for name, mask in self.masks.items()}
        if "coverage" not in masks and self.coverage is not None:
            coverage = np.asarray(self.coverage, dtype=float).ravel()
            if self.coverage_kind == "rays":
                masks["coverage"] = coverage > 0
            else:
                masks["coverage"] = np.nan_to_num(coverage, nan=-np.inf) >= COVERAGE_LOG10_THRESHOLD
        if "doi" not in masks and self.doi is not None and isinstance(self.geometry, LayeredGeometry):
            tops = self.geometry.layer_tops()
            doi = np.broadcast_to(np.asarray(self.doi, dtype=float).reshape(-1, 1), tops.shape)
            masks["doi"] = (tops < doi).ravel()
        if "resolution" not in masks and self.resolution is not None:
            masks["resolution"] = np.asarray(self.resolution, dtype=float).ravel() >= RESOLUTION_THRESHOLD
        return masks

    def display_mask(self) -> tuple[np.ndarray | None, str]:
        """The cells a viewer shows by default, and the legend's note on why the rest are blank.

        All available masks combined; ``(None, "")`` when there is nothing to
        mask by.
        """
        masks = self.all_masks()
        if not masks:
            return None, ""
        combined = np.ones(self.geometry.n_cells, dtype=bool)
        for mask in masks.values():
            combined &= np.asarray(mask, dtype=bool).ravel()
        notes = {
            "coverage": (
                "cells no ray passes are blank"
                if self.coverage_kind == "rays"
                else f"blank where coverage < 10^{COVERAGE_LOG10_THRESHOLD:g} (log10 cumulative sensitivity)"
            ),
            "doi": "blank below the depth of investigation",
            "resolution": f"blank where resolution < {RESOLUTION_THRESHOLD:g}",
        }
        basis = "; ".join(notes.get(name, f"mask {name!r}") for name in masks)
        return combined, basis

    # -- persistence -----------------------------------------------------------------
    def to_tree(self) -> dict[str, Any]:
        """Plain mapping of arrays and values (``native`` left out), for saving."""
        geometry = {key: value for key, value in vars(self.geometry).items()}
        if isinstance(self.geometry, GridGeometry):
            geometry["edges"] = list(self.geometry.edges)
            geometry["axes"] = list(self.geometry.axes)
        return {
            "schema": SCHEMA,
            "method": self.method,
            "geometry": geometry,
            "parameters": {name: dict(vars(p)) for name, p in self.parameters.items()},
            "fit": None if self.fit is None else dict(vars(self.fit)),
            "coverage": self.coverage,
            "coverage_kind": self.coverage_kind,
            "doi": self.doi,
            "resolution": self.resolution,
            "masks": dict(self.masks),
            "history": list(self.history),
            "meta": dict(self.meta),
            "provenance": dict(self.provenance),
        }

    @classmethod
    def from_tree(cls, tree: Mapping[str, Any]) -> ModelResultV2:
        if tree.get("schema") != SCHEMA:
            raise DataValidationError(f"not a {SCHEMA} result", field="schema")
        raw = dict(tree["geometry"])
        geometry: Geometry
        if raw["kind"] == "grid":
            geometry = GridGeometry(edges=tuple(raw["edges"]), axes=tuple(raw["axes"]), order=raw["order"])
        elif raw["kind"] == "layered":
            geometry = LayeredGeometry(**raw)
        else:
            geometry = MeshGeometry(**raw)
        fit = tree.get("fit")
        return cls(
            method=str(tree["method"]),
            geometry=geometry,
            parameters={name: Parameter(**values) for name, values in tree["parameters"].items()},
            fit=None if fit is None else DataFit(**fit),
            coverage=tree.get("coverage"),
            coverage_kind=str(tree.get("coverage_kind", "log10_sensitivity")),
            doi=tree.get("doi"),
            resolution=tree.get("resolution"),
            masks=dict(tree.get("masks") or {}),
            history=list(tree.get("history") or []),
            meta=dict(tree.get("meta") or {}),
            provenance=dict(tree.get("provenance") or {}),
        )

    def save(self, path: str | Path) -> Path:
        """Write the result to an HDF5 file (the dataset tree format)."""
        import h5py

        from PyHydroGeophysX.datastore.tree import write_tree

        self.validate()
        target = Path(path).resolve()
        target.parent.mkdir(parents=True, exist_ok=True)
        with h5py.File(target, "w") as handle:
            handle.attrs["schema"] = SCHEMA
            write_tree(
                handle.create_group("result"),
                self.to_tree(),
                path=("result",),
                file=target,
                base=None,
                origins={},
            )
        return target

    @classmethod
    def load(cls, path: str | Path) -> ModelResultV2:
        import h5py

        from PyHydroGeophysX.datastore.tree import read_tree

        source = Path(path).resolve()
        with h5py.File(source, "r") as handle:
            tree = read_tree(handle["result"], path=("result",), file=source, origins={})
        return cls.from_tree(tree)


__all__ = [
    "COVERAGE_LOG10_THRESHOLD",
    "RESERVED_PARAMETERS",
    "RESOLUTION_THRESHOLD",
    "SCHEMA",
    "DataFit",
    "Geometry",
    "GridGeometry",
    "LayeredGeometry",
    "MeshGeometry",
    "ModelResultV2",
    "Parameter",
]
