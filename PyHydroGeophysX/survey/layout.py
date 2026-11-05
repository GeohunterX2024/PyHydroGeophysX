"""Where a survey's electrodes, sources, receivers and sites are, and the ground under them.

A :class:`SurveyLayout` is points with a role (``A``, ``B``, ``M``, ``N``,
``tx``, ``rx``, ``site``, ``electrode``), the links between them (the AB
current pair, an MN dipole, a transmitter loop), the terrain, and the
coordinate reference. Coordinates are metres: ``x`` east, ``y`` north and
``z`` elevation. A point far off the line (the remote B of a pole-dipole
survey) is flagged ``remote``, so a view can keep the line readable.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any

import numpy as np
from numpy.typing import ArrayLike, NDArray

FloatArray = NDArray[np.float64]
BoolArray = NDArray[np.bool_]
IntArray = NDArray[np.int64]
#: A selection key, shaped like a QC log key: ``("shot", id)``, ``("trace", id, serial, code)``.
Key = tuple[str | int, ...]

#: Roles a point can have.
ROLES = ("A", "B", "M", "N", "tx", "rx", "site", "electrode")
#: Mean Earth radius of the local equirectangular projection (as ``mt.station_distances``).
EARTH_RADIUS_M = 6371000.0


def _floats(values: ArrayLike, name: str, shape_tail: tuple[int, ...] = ()) -> FloatArray:
    array = np.asarray(values, dtype=np.float64)
    if shape_tail and (array.ndim != 1 + len(shape_tail) or array.shape[1:] != shape_tail):
        raise ValueError(f"{name} must have shape (n, {', '.join(map(str, shape_tail))}), got {array.shape}")
    return array


def _texts(values: Sequence[Any], size: int, name: str, default: str = "") -> tuple[str, ...]:
    texts = tuple(str(v) for v in values) if len(values) else (default,) * size
    if len(texts) != size:
        raise ValueError(f"{name} has {len(texts)} entries for {size} points")
    return texts


@dataclass(frozen=True)
class SurveyPoints:
    """Points of a survey, all arrays aligned by index.

    ``keys`` are the selection keys of the points (empty when the points are
    not selectable); ``attrs`` hold values a view can colour the points by.
    """

    ids: tuple[str, ...]
    role: tuple[str, ...]
    xyz: FloatArray
    group: tuple[str, ...] = ()
    label: tuple[str, ...] = ()
    keys: tuple[Key, ...] = ()
    attrs: Mapping[str, FloatArray] = field(default_factory=dict)
    along: FloatArray | None = None
    remote: BoolArray | None = None

    def __post_init__(self) -> None:
        xyz = _floats(self.xyz, "xyz", (3,)) if np.size(self.xyz) else np.zeros((0, 3))
        size = xyz.shape[0]
        object.__setattr__(self, "xyz", xyz)
        object.__setattr__(self, "ids", _texts(self.ids, size, "ids"))
        object.__setattr__(self, "role", _texts(self.role, size, "role", "electrode"))
        object.__setattr__(self, "group", _texts(self.group, size, "group"))
        object.__setattr__(self, "label", _texts(self.label, size, "label") if self.label else self.ids)
        unknown = sorted(set(self.role) - set(ROLES))
        if unknown:
            raise ValueError(f"unknown point roles {unknown}; expected one of {ROLES}")
        if self.keys and len(self.keys) != size:
            raise ValueError(f"keys has {len(self.keys)} entries for {size} points")
        attrs = {name: np.asarray(v, dtype=np.float64).ravel() for name, v in self.attrs.items()}
        for name, values in attrs.items():
            if values.size != size:
                raise ValueError(f"attribute {name!r} has {values.size} values for {size} points")
        object.__setattr__(self, "attrs", attrs)
        if self.along is not None:
            along = np.asarray(self.along, dtype=np.float64).ravel()
            if along.size != size:
                raise ValueError(f"along has {along.size} values for {size} points")
            object.__setattr__(self, "along", along)
        remote = np.zeros(size, bool) if self.remote is None else np.asarray(self.remote, bool).ravel()
        if remote.size != size:
            raise ValueError(f"remote has {remote.size} values for {size} points")
        object.__setattr__(self, "remote", remote)

    @property
    def size(self) -> int:
        return int(self.xyz.shape[0])

    def is_remote(self) -> BoolArray:
        """The far-off points (never None after construction)."""
        assert self.remote is not None
        return self.remote

    def where(self, role: str | Sequence[str] | None = None, group: str | None = None) -> BoolArray:
        """Mask of the points with ``role`` (one or several) and in ``group``."""
        mask = np.ones(self.size, bool)
        if role is not None:
            roles = {role} if isinstance(role, str) else set(role)
            mask &= np.array([r in roles for r in self.role], bool)
        if group is not None:
            mask &= np.array([g == group for g in self.group], bool)
        return mask


@dataclass(frozen=True)
class SurveyLinks:
    """Segments between points (indices into :class:`SurveyPoints`)."""

    start: IntArray
    end: IntArray
    kind: tuple[str, ...] = ()
    group: tuple[str, ...] = ()
    keys: tuple[Key, ...] = ()

    def __post_init__(self) -> None:
        start = np.asarray(self.start, dtype=np.int64).ravel()
        end = np.asarray(self.end, dtype=np.int64).ravel()
        if start.size != end.size:
            raise ValueError("links need as many ends as starts")
        object.__setattr__(self, "start", start)
        object.__setattr__(self, "end", end)
        object.__setattr__(self, "kind", _texts(self.kind, start.size, "kind", "link"))
        object.__setattr__(self, "group", _texts(self.group, start.size, "group"))
        if self.keys and len(self.keys) != start.size:
            raise ValueError(f"keys has {len(self.keys)} entries for {start.size} links")

    @property
    def size(self) -> int:
        return int(self.start.size)

    @classmethod
    def none(cls) -> SurveyLinks:
        return cls(np.zeros(0, np.int64), np.zeros(0, np.int64))


@dataclass(frozen=True)
class TopographyProfile:
    """Ground elevation along the line: ``distance`` (m along the line) and ``elevation`` (m)."""

    distance: FloatArray
    elevation: FloatArray

    def __post_init__(self) -> None:
        distance = np.asarray(self.distance, dtype=np.float64).ravel()
        elevation = np.asarray(self.elevation, dtype=np.float64).ravel()
        if distance.size != elevation.size:
            raise ValueError("topography needs one elevation per distance")
        order = np.argsort(distance, kind="stable")
        object.__setattr__(self, "distance", distance[order])
        object.__setattr__(self, "elevation", elevation[order])

    def at(self, distance: ArrayLike) -> FloatArray:
        """Elevation at ``distance``; the end values hold beyond the profile."""
        values = np.asarray(distance, dtype=np.float64)
        if self.distance.size == 0:
            return np.zeros_like(values)
        return np.interp(values, self.distance, self.elevation)


@dataclass(frozen=True)
class TopographyGrid:
    """Ground elevation on a regular grid: ``x`` (nx), ``y`` (ny), ``z`` (ny, nx)."""

    x: FloatArray
    y: FloatArray
    z: FloatArray

    def __post_init__(self) -> None:
        x = np.asarray(self.x, dtype=np.float64).ravel()
        y = np.asarray(self.y, dtype=np.float64).ravel()
        z = np.asarray(self.z, dtype=np.float64)
        if z.shape != (y.size, x.size):
            raise ValueError(f"z must have shape ({y.size}, {x.size}), got {z.shape}")
        object.__setattr__(self, "x", x)
        object.__setattr__(self, "y", y)
        object.__setattr__(self, "z", z)


@dataclass(frozen=True)
class LineFrame:
    """A straight survey line: distance along it is ``(xy - origin) @ direction``."""

    origin: FloatArray
    direction: FloatArray

    def along(self, xy: ArrayLike) -> FloatArray:
        points = np.atleast_2d(np.asarray(xy, dtype=np.float64))[:, :2]
        return np.asarray((points - self.origin) @ self.direction, dtype=np.float64)

    def point(self, distance: ArrayLike) -> FloatArray:
        """``(n, 2)`` positions at ``distance`` along the line."""
        d = np.asarray(distance, dtype=np.float64).ravel()
        return np.asarray(self.origin[None, :] + d[:, None] * self.direction[None, :], dtype=np.float64)

    @property
    def azimuth(self) -> float:
        """Degrees clockwise from north."""
        return float(np.degrees(np.arctan2(self.direction[0], self.direction[1])) % 360.0)

    @classmethod
    def fit(cls, xy: ArrayLike) -> LineFrame:
        """The principal direction of ``xy``, pointing from the first point to the last, origin at the start.

        Distances agree with ``mt.station_distances`` for the same points.
        """
        points = np.atleast_2d(np.asarray(xy, dtype=np.float64))[:, :2]
        if points.shape[0] < 2:
            origin = points[0] if points.shape[0] else np.zeros(2)
            return cls(np.asarray(origin, dtype=np.float64), np.array([0.0, 1.0]))
        centre = points.mean(axis=0)
        _, _, vt = np.linalg.svd(points - centre, full_matrices=False)
        direction = np.asarray(vt[0], dtype=np.float64)
        along = points @ direction
        if along[-1] < along[0]:
            direction, along = -direction, -along
        start = int(np.argmin(along))
        origin = centre + (along[start] - float(centre @ direction)) * direction
        return cls(np.asarray(origin, dtype=np.float64), direction)


def local_projection(
    longitude: ArrayLike, latitude: ArrayLike, origin: tuple[float, float] | None = None
) -> tuple[FloatArray, FloatArray]:
    """Geographic degrees to local metres ``(east, north)``, equirectangular about ``origin``.

    ``origin`` is ``(longitude, latitude)``; by default the mean of the points,
    as ``mt.station_distances`` projects MT sites.
    """
    lon = np.asarray(longitude, dtype=np.float64)
    lat = np.asarray(latitude, dtype=np.float64)
    lon0, lat0 = (float(np.mean(lon)), float(np.mean(lat))) if origin is None else origin
    north = np.radians(lat - lat0) * EARTH_RADIUS_M
    east = np.radians(lon - lon0) * EARTH_RADIUS_M * np.cos(np.radians(lat0))
    return np.asarray(east, dtype=np.float64), np.asarray(north, dtype=np.float64)


@dataclass(frozen=True)
class SurveyLayout:
    """A survey's points, links, terrain and coordinate reference."""

    points: SurveyPoints
    links: SurveyLinks = field(default_factory=SurveyLinks.none)
    topography: TopographyProfile | None = None
    grid: TopographyGrid | None = None
    frame: LineFrame | None = None
    crs: Mapping[str, Any] | None = None
    title: str = ""

    def __post_init__(self) -> None:
        if self.links.size and (
            int(np.max(self.links.start, initial=-1)) >= self.points.size
            or int(np.max(self.links.end, initial=-1)) >= self.points.size
        ):
            raise ValueError("a link names a point that is not in the layout")

    def groups(self) -> tuple[str, ...]:
        """The groups of the points (shots, injections, sites), in first-seen order."""
        return tuple(dict.fromkeys(g for g in self.points.group if g))

    def along(self) -> FloatArray:
        """Each point's distance along the line: given, from the frame, or fitted."""
        if self.points.along is not None:
            return self.points.along
        frame = self.frame or LineFrame.fit(self.points.xyz[~self.points.is_remote()])
        return frame.along(self.points.xyz)

    def line_points(self) -> BoolArray:
        """The points on the line (all but the remote ones)."""
        return np.asarray(~self.points.is_remote(), dtype=bool)

    def extent(self, include_remote: bool = False) -> tuple[float, float, float, float, float, float]:
        """``(xmin, xmax, ymin, ymax, zmin, zmax)`` of the points."""
        mask = np.ones(self.points.size, bool) if include_remote else self.line_points()
        xyz = self.points.xyz[mask] if mask.any() else self.points.xyz
        if xyz.size == 0:
            return (0.0, 1.0, 0.0, 1.0, 0.0, 1.0)
        lo, hi = np.nanmin(xyz, axis=0), np.nanmax(xyz, axis=0)
        return (float(lo[0]), float(hi[0]), float(lo[1]), float(hi[1]), float(lo[2]), float(hi[2]))

    def line_length(self) -> float:
        """Length of the line along its direction (at least 1 m)."""
        along = self.along()[self.line_points()]
        return max(float(np.ptp(along)) if along.size else 0.0, 1.0)

    def position_at(self, distance: ArrayLike) -> FloatArray:
        """``(n, 2)`` east/north at ``distance`` along the line, following the line's points."""
        d = np.asarray(distance, dtype=np.float64).ravel()
        on_line = self.line_points()
        along = self.along()[on_line]
        xy = self.points.xyz[on_line, :2]
        if along.size < 2:
            frame = self.frame or LineFrame(np.zeros(2), np.array([0.0, 1.0]))
            return frame.point(d)
        order = np.argsort(along, kind="stable")
        along, xy = along[order], xy[order]
        along, first = np.unique(along, return_index=True)
        xy = xy[first]
        if along.size < 2:
            return np.repeat(xy[:1], d.size, axis=0)
        return np.column_stack([np.interp(d, along, xy[:, 0]), np.interp(d, along, xy[:, 1])])


__all__ = [
    "EARTH_RADIUS_M",
    "ROLES",
    "Key",
    "LineFrame",
    "SurveyLayout",
    "SurveyLinks",
    "SurveyPoints",
    "TopographyGrid",
    "TopographyProfile",
    "local_projection",
]
