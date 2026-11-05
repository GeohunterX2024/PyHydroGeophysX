"""Pseudo-depth points of a resistivity or IP line: where each reading is drawn.

A pseudo-depth is a display convention, not a depth of investigation, so the
convention travels with the points and every view names it. Two are provided,
each reproducing the placement a PHGX page already draws:

- ``"pole_dipole_zond"`` - as the DCIP plugin (``phgx_dcip.figures.pseudo_coordinates``):
  pole-dipole rows at the midpoint of A and the nearer potential electrode, a
  depth of half that distance; rows with B on the line at the mean of the AB and
  MN midpoints, a depth of half the distance between them.
- ``"pygimli"`` - as the ERT page (``data_processing.ert_io.pseudosection_points``):
  the mean of the four electrodes, a depth of 0.19 times their spread (at least 1 cm).
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field

import numpy as np
from numpy.typing import ArrayLike

from PyHydroGeophysX.survey.layout import BoolArray, FloatArray, Key, TopographyProfile

#: Spread fraction of the ``"pygimli"`` convention (``ert_io.PSEUDO_DEPTH_FACTOR``).
PYGIMLI_DEPTH_FACTOR = 0.19
#: Conventions and the wording a legend uses for them (English source text).
CONVENTIONS = {
    "pole_dipole_zond": "Pseudo-depth: |AM|/2 (pole-dipole), |AB-MN midpoints|/2 (B on the line)",
    "pygimli": "Pseudo-depth: 0.19 x electrode spread (Edwards 1977)",
}


@dataclass(frozen=True)
class PseudoPoints:
    """Pseudo-depth points: position along the line, depth (positive down) and their keys."""

    along: FloatArray
    depth: FloatArray
    convention: str
    surface: FloatArray | None = None
    keys: tuple[Key, ...] = ()
    group: tuple[str, ...] = ()
    attrs: Mapping[str, FloatArray] = field(default_factory=dict)

    def __post_init__(self) -> None:
        along = np.asarray(self.along, dtype=np.float64).ravel()
        depth = np.asarray(self.depth, dtype=np.float64).ravel()
        if along.size != depth.size:
            raise ValueError("pseudo points need one depth per position")
        if self.convention not in CONVENTIONS:
            raise ValueError(f"unknown pseudo-depth convention {self.convention!r}")
        size = along.size
        surface = (
            np.zeros(size) if self.surface is None else np.asarray(self.surface, dtype=np.float64).ravel()
        )
        if surface.size != size:
            raise ValueError("pseudo points need one surface elevation per position")
        if self.keys and len(self.keys) != size:
            raise ValueError(f"keys has {len(self.keys)} entries for {size} points")
        group = tuple(str(g) for g in self.group) if self.group else ("",) * size
        if len(group) != size:
            raise ValueError(f"group has {len(group)} entries for {size} points")
        attrs = {name: np.asarray(v, dtype=np.float64).ravel() for name, v in self.attrs.items()}
        for name, values in attrs.items():
            if values.size != size:
                raise ValueError(f"attribute {name!r} has {values.size} values for {size} points")
        object.__setattr__(self, "along", along)
        object.__setattr__(self, "depth", depth)
        object.__setattr__(self, "surface", surface)
        object.__setattr__(self, "group", group)
        object.__setattr__(self, "attrs", attrs)

    @property
    def size(self) -> int:
        return int(self.along.size)

    @property
    def elevation(self) -> FloatArray:
        """Ground elevation minus the pseudo-depth: where a point is drawn on a terrain section."""
        assert self.surface is not None
        return np.asarray(self.surface - self.depth, dtype=np.float64)

    @property
    def legend(self) -> str:
        return CONVENTIONS[self.convention]

    def on_ground(self, topography: TopographyProfile | None) -> PseudoPoints:
        """The same points with their surface elevation taken from ``topography``."""
        surface = np.zeros(self.size) if topography is None else topography.at(self.along)
        return PseudoPoints(
            self.along, self.depth, self.convention, surface, self.keys, self.group, self.attrs
        )


def zond_coordinates(
    xa: ArrayLike, xm: ArrayLike, xn: ArrayLike, xb: ArrayLike | None = None
) -> tuple[FloatArray, FloatArray]:
    """``(x, depth)`` of the ``"pole_dipole_zond"`` convention (``xb`` NaN where B is remote)."""
    a, m, n = (np.asarray(v, dtype=np.float64) for v in (xa, xm, xn))
    near = np.where(np.abs(m - a) <= np.abs(n - a), m, n)
    px, pz = 0.5 * (a + near), 0.5 * np.abs(near - a)
    if xb is not None:
        b = np.asarray(xb, dtype=np.float64)
        rows = np.isfinite(b)
        if np.any(rows):
            px[rows] = 0.25 * (a[rows] + b[rows] + m[rows] + n[rows])
            pz[rows] = 0.25 * np.abs(a[rows] + b[rows] - m[rows] - n[rows])
    return np.asarray(px, dtype=np.float64), np.asarray(pz, dtype=np.float64)


def pygimli_coordinates(
    x: ArrayLike, a: ArrayLike, b: ArrayLike, m: ArrayLike, n: ArrayLike
) -> tuple[FloatArray, FloatArray, BoolArray]:
    """``(x, depth, inside)`` of the ``"pygimli"`` convention.

    ``a``, ``b``, ``m``, ``n`` are electrode indices into ``x`` (all-1-based
    indices are shifted down, as ``ert_io`` does); ``inside`` marks the readings
    whose electrodes all exist, the others being left out of ``x`` and ``depth``.
    """
    xs = np.asarray(x, dtype=np.float64)
    ia, ib, im, in_ = (np.asarray(v, dtype=np.int64).ravel() for v in (a, b, m, n))
    if ia.size:
        every = np.concatenate([ia, ib, im, in_])
        if every.min() >= 1 and every.max() >= xs.size:
            ia, ib, im, in_ = ia - 1, ib - 1, im - 1, in_ - 1
    ids = np.stack([ia, ib, im, in_], axis=1)
    inside = np.asarray(((ids >= 0) & (ids < xs.size)).all(axis=1), dtype=bool)
    if not inside.any():
        return np.zeros(0), np.zeros(0), inside
    positions = xs[ids[inside]]
    spread = positions.max(axis=1) - positions.min(axis=1)
    depth = np.maximum(spread * PYGIMLI_DEPTH_FACTOR, 0.01)
    return np.asarray(positions.mean(axis=1), dtype=np.float64), np.asarray(depth, dtype=np.float64), inside


__all__ = [
    "CONVENTIONS",
    "PYGIMLI_DEPTH_FACTOR",
    "PseudoPoints",
    "pygimli_coordinates",
    "zond_coordinates",
]
