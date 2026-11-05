"""The layers of a 3-D survey view, built once from a layout and its pseudo-depth points.

Both 3-D renderers (PyVista and the Matplotlib fallback) draw a :class:`Scene3D`,
so they show the same things; a renderer only decides how. Vertical
exaggeration, the placement of remote points and the split between the current
group and the others are decided here, once.

Layer names are stable, so a view can toggle them: ``terrain``, ``points:<role>``,
``points:other`` (A and B of the other groups, faded), ``links``, ``remote``,
``pseudo``, ``pseudo:current``, ``labels`` and the reserved ``curtain``.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field

import numpy as np

from PyHydroGeophysX.survey.layout import BoolArray, FloatArray, Key, SurveyLayout
from PyHydroGeophysX.survey.pseudo import PseudoPoints

#: Colour, symbol and size (points) of each role.
ROLE_STYLE: dict[str, tuple[str, str, float]] = {
    "A": ("#dc2626", "triangle", 11.0),
    "B": ("#7c3aed", "triangle", 11.0),
    "M": ("#2563eb", "triangle_down", 7.0),
    "N": ("#0891b2", "triangle_down", 7.0),
    "electrode": ("#334155", "triangle_down", 7.0),
    "site": ("#0f766e", "square", 10.0),
    "tx": ("#ea580c", "diamond", 10.0),
    "rx": ("#2563eb", "circle", 7.0),
}
FADED = "#9ca3af"
TERRAIN = "#a3b18a"
LINK_COLOURS = {
    "AB": "#dc2626",
    "MN": "#2563eb",
    "dipole_ex": "#2563eb",
    "dipole_ey": "#0891b2",
    "tx_loop": "#ea580c",
}
#: Roles drawn whatever the current group (it selects the sources and dipoles of one group).
ALWAYS_SHOWN = ("site", "rx")
#: Links drawn for "all groups" before the view keeps to the current group only.
_ALL_LINKS_LIMIT = 400


@dataclass(frozen=True)
class SceneOptions:
    """What a 3-D view shows; every field has an option in the view."""

    exaggeration: float = 1.0
    include_remote: bool = False
    show_terrain: bool = True
    show_points: bool = True
    show_other_groups: bool = True
    show_links: bool = True
    show_pseudo: bool = True
    show_labels: bool = False
    colour_by: str = ""
    point_scale: float = 1.0
    ribbon_width: float = 0.0
    group: str = ""
    depth_range: tuple[float, float] | None = None


@dataclass(frozen=True)
class PointLayer:
    name: str
    xyz: FloatArray
    color: str
    size: float
    symbol: str = "circle"
    values: FloatArray | None = None
    labels: tuple[str, ...] = ()
    keys: tuple[Key, ...] = ()
    opacity: float = 1.0


@dataclass(frozen=True)
class LineLayer:
    name: str
    segments: FloatArray
    color: str
    width: float = 2.0
    dashed: bool = False
    colors: tuple[str, ...] = ()


@dataclass(frozen=True)
class SurfaceLayer:
    name: str
    x: FloatArray
    y: FloatArray
    z: FloatArray
    color: str = TERRAIN
    opacity: float = 0.55


@dataclass(frozen=True)
class LabelLayer:
    name: str
    xyz: FloatArray
    texts: tuple[str, ...]
    color: str = "#111827"


@dataclass(frozen=True)
class CurtainLayer:
    """Reserved: an inverted section hung under the line (``values`` (nz, n-1) between ``path`` nodes)."""

    name: str
    path: FloatArray
    top: FloatArray
    depth_edges: FloatArray
    values: FloatArray
    colormap: str = "turbo"


Layer = PointLayer | LineLayer | SurfaceLayer | LabelLayer | CurtainLayer


@dataclass(frozen=True)
class Scene3D:
    """Layers in display coordinates (elevations already exaggerated about ``z_reference``)."""

    layers: tuple[Layer, ...]
    bounds: tuple[float, float, float, float, float, float]
    z_reference: float
    exaggeration: float
    value_name: str = ""
    value_range: tuple[float, float] | None = None
    notes: tuple[str, ...] = field(default_factory=tuple)
    #: Remote points: ``(role, label, distance from the line centre in m)``.
    remote: tuple[tuple[str, str, float], ...] = field(default_factory=tuple)

    def names(self) -> tuple[str, ...]:
        return tuple(layer.name for layer in self.layers)

    def layer(self, name: str) -> Layer | None:
        return next((layer for layer in self.layers if layer.name == name), None)


def _lift(xyz: FloatArray, z_reference: float, exaggeration: float) -> FloatArray:
    out = np.array(xyz, dtype=np.float64, copy=True)
    if out.size:
        out[:, 2] = z_reference + (out[:, 2] - z_reference) * exaggeration
    return out


def _remote_positions(
    layout: SurveyLayout, include_remote: bool
) -> tuple[FloatArray, tuple[tuple[str, str, float], ...]]:
    """Display positions of all points; remote ones moved to the edge unless ``include_remote``."""
    points = layout.points
    xyz = np.array(points.xyz, dtype=np.float64, copy=True)
    notes: list[tuple[str, str, float]] = []
    remote = points.is_remote()
    if not remote.any():
        return xyz, ()
    line = ~remote
    centre = xyz[line, :2].mean(axis=0) if line.any() else np.zeros(2)
    surface = float(np.median(xyz[line, 2])) if line.any() else 0.0
    xmin, xmax, ymin, ymax, _, _ = layout.extent()
    radius = 0.5 * float(np.hypot(xmax - xmin, ymax - ymin)) or layout.line_length()
    for index in np.flatnonzero(remote):
        offset = xyz[index, :2] - centre
        distance = float(np.hypot(*offset))
        notes.append((points.role[index], points.label[index], distance))
        if include_remote or distance == 0:
            continue
        xyz[index, :2] = centre + offset / distance * radius * 1.25
        xyz[index, 2] = surface
    return xyz, tuple(notes)


def _ribbon(
    layout: SurveyLayout, distance: FloatArray, elevation: FloatArray, width: float
) -> tuple[FloatArray, FloatArray, FloatArray] | None:
    if distance.size < 2:
        return None
    centre = layout.position_at(distance)
    tangent = np.gradient(centre, distance, axis=0)
    norm = np.hypot(tangent[:, 0], tangent[:, 1])
    norm[norm == 0] = 1.0
    normal = np.column_stack([-tangent[:, 1] / norm, tangent[:, 0] / norm])
    half = 0.5 * width
    x = np.vstack([centre[:, 0] - half * normal[:, 0], centre[:, 0] + half * normal[:, 0]])
    y = np.vstack([centre[:, 1] - half * normal[:, 1], centre[:, 1] + half * normal[:, 1]])
    z = np.vstack([elevation, elevation])
    return x, y, z


def _terrain(layout: SurveyLayout, options: SceneOptions) -> tuple[FloatArray, FloatArray, FloatArray] | None:
    if layout.grid is not None:
        gx, gy = np.meshgrid(layout.grid.x, layout.grid.y)
        return gx, gy, layout.grid.z
    width = options.ribbon_width or 0.04 * layout.line_length()
    along = layout.along()[layout.line_points()]
    if layout.topography is not None and layout.topography.distance.size >= 2:
        lo, hi = (float(np.min(along)), float(np.max(along))) if along.size else (0.0, 1.0)
        margin = 0.05 * (hi - lo)
        keep = (layout.topography.distance >= lo - margin) & (layout.topography.distance <= hi + margin)
        distance = layout.topography.distance[keep]
        if distance.size >= 2:
            return _ribbon(layout, distance, layout.topography.elevation[keep], width)
    if along.size < 2:
        return None
    order = np.argsort(along, kind="stable")
    distance, first = np.unique(along[order], return_index=True)
    z = layout.points.xyz[layout.line_points()][order][first, 2]
    return _ribbon(layout, distance, z, width)


def _values(attrs: dict[str, FloatArray] | object, name: str) -> FloatArray | None:
    if not name or not isinstance(attrs, dict) or name not in attrs:
        return None
    return np.asarray(attrs[name], dtype=np.float64)


def _range(values: FloatArray | None) -> tuple[float, float] | None:
    if values is None:
        return None
    finite = values[np.isfinite(values)]
    if finite.size == 0:
        return None
    return float(np.percentile(finite, 2)), float(np.percentile(finite, 98))


def _subset_keys(keys: Sequence[Key], mask: BoolArray) -> tuple[Key, ...]:
    return tuple(k for k, keep in zip(keys, mask, strict=True) if keep) if keys else ()


def build_scene(
    layout: SurveyLayout, pseudo: PseudoPoints | None = None, options: SceneOptions | None = None
) -> Scene3D:
    """The layers of ``layout`` (and ``pseudo``) as ``options`` asks for them."""
    options = options or SceneOptions()
    points = layout.points
    xyz, remote_info = _remote_positions(layout, options.include_remote)
    line = layout.line_points()
    z_reference = float(np.median(points.xyz[line, 2])) if line.any() else 0.0
    ex = max(float(options.exaggeration), 0.01)
    layers: list[Layer] = []

    if options.show_terrain:
        terrain = _terrain(layout, options)
        if terrain is not None:
            tx, ty, tz = terrain
            tz = z_reference + (tz - z_reference) * ex
            layers.append(SurfaceLayer("terrain", tx, ty, tz))

    # Sites and receivers are always drawn: a group (a shot) selects sources and dipoles only.
    always = points.where(ALWAYS_SHOWN)
    current = np.array([g == options.group or not g for g in points.group], bool) | always
    grouped = np.array([bool(g) for g in points.group], bool) & ~always
    if not options.group:
        current = np.ones(points.size, bool)
    if options.show_points:
        point_values = _values(points.attrs, options.colour_by)
        for role in dict.fromkeys(points.role):
            mask = points.where(role) & current & ~points.is_remote()
            if not mask.any():
                continue
            color, symbol, size = ROLE_STYLE[role]
            layers.append(
                PointLayer(
                    f"points:{role}",
                    _lift(xyz[mask], z_reference, ex),
                    color,
                    size * options.point_scale,
                    symbol,
                    None if point_values is None else point_values[mask],
                    tuple(np.asarray(points.label)[mask]),
                    _subset_keys(points.keys, mask),
                )
            )
        other = grouped & ~current & points.where(("A", "B", "tx")) & ~points.is_remote()
        if options.show_other_groups and other.any():
            layers.append(
                PointLayer(
                    "points:other",
                    _lift(xyz[other], z_reference, ex),
                    FADED,
                    6.0 * options.point_scale,
                    "triangle",
                    labels=tuple(np.asarray(points.label)[other]),
                    keys=_subset_keys(points.keys, other),
                    opacity=0.6,
                )
            )
        remote = points.is_remote() & (current | ~grouped)
        if remote.any():
            lifted = _lift(xyz[remote], z_reference, ex)
            layers.append(
                PointLayer(
                    "remote",
                    lifted,
                    ROLE_STYLE["B"][0],
                    12.0 * options.point_scale,
                    "triangle",
                    labels=tuple(np.asarray(points.label)[remote]),
                    keys=_subset_keys(points.keys, remote),
                )
            )
            if not options.include_remote:
                texts = tuple(f"{role} {distance / 1000.0:.2f} km" for role, _label, distance in remote_info)
                layers.append(
                    LabelLayer("remote-label", lifted, texts[: lifted.shape[0]], ROLE_STYLE["B"][0])
                )

    links = layout.links
    if options.show_links and links.size:
        in_group = np.array([g == options.group or not g for g in links.group], bool)
        chosen = in_group if options.group else np.full(links.size, links.size <= _ALL_LINKS_LIMIT)
        if chosen.any():
            starts = _lift(xyz[links.start[chosen]], z_reference, ex)
            ends = _lift(xyz[links.end[chosen]], z_reference, ex)
            kinds = tuple(np.asarray(links.kind)[chosen])
            layers.append(
                LineLayer(
                    "links",
                    np.stack([starts, ends], axis=1),
                    LINK_COLOURS.get(kinds[0], "#374151"),
                    2.5,
                    colors=tuple(LINK_COLOURS.get(k, "#374151") for k in kinds),
                )
            )

    value_range = None
    if pseudo is not None and options.show_pseudo and pseudo.size:
        keep = np.ones(pseudo.size, bool)
        if options.depth_range is not None:
            low, high = options.depth_range
            keep &= (pseudo.depth >= low) & (pseudo.depth <= high)
        if keep.any():
            xy = layout.position_at(pseudo.along[keep])
            pxyz = np.column_stack([xy, pseudo.elevation[keep]])
            values = _values(dict(pseudo.attrs), options.colour_by)
            shown = None if values is None else values[keep]
            value_range = _range(shown)
            layers.append(
                PointLayer(
                    "pseudo",
                    _lift(pxyz, z_reference, ex),
                    "#1f2937",
                    5.0 * options.point_scale,
                    "sphere",
                    shown,
                    keys=_subset_keys(pseudo.keys, keep),
                )
            )
            if options.group:
                mine = np.array([g == options.group for g in pseudo.group], bool)[keep]
                if mine.any():
                    layers.append(
                        PointLayer(
                            "pseudo:current",
                            _lift(pxyz[mine], z_reference, ex),
                            "#f59e0b",
                            8.0 * options.point_scale,
                            "sphere",
                            keys=_subset_keys(_subset_keys(pseudo.keys, keep), mine),
                        )
                    )

    if options.show_labels:
        mask = current & points.where(("A", "B", "site", "tx"))
        if mask.any():
            layers.append(
                LabelLayer("labels", _lift(xyz[mask], z_reference, ex), tuple(np.asarray(points.label)[mask]))
            )

    bounds = _bounds(layers, z_reference)
    return Scene3D(tuple(layers), bounds, z_reference, ex, options.colour_by, value_range, (), remote_info)


def _bounds(layers: Sequence[Layer], z_reference: float) -> tuple[float, float, float, float, float, float]:
    chunks: list[FloatArray] = []
    for layer in layers:
        if isinstance(layer, (PointLayer, LabelLayer)):
            chunks.append(layer.xyz)
        elif isinstance(layer, LineLayer):
            chunks.append(layer.segments.reshape(-1, 3))
        elif isinstance(layer, SurfaceLayer):
            chunks.append(np.column_stack([layer.x.ravel(), layer.y.ravel(), layer.z.ravel()]))
    if not chunks:
        return (0.0, 1.0, 0.0, 1.0, z_reference - 1.0, z_reference + 1.0)
    every = np.vstack(chunks)
    lo, hi = np.nanmin(every, axis=0), np.nanmax(every, axis=0)
    return (float(lo[0]), float(hi[0]), float(lo[1]), float(hi[1]), float(lo[2]), float(hi[2]))


__all__ = [
    "ALWAYS_SHOWN",
    "FADED",
    "LINK_COLOURS",
    "ROLE_STYLE",
    "CurtainLayer",
    "LabelLayer",
    "Layer",
    "LineLayer",
    "PointLayer",
    "Scene3D",
    "SceneOptions",
    "SurfaceLayer",
    "build_scene",
]
