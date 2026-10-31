"""Report figures of sections and pseudosections, saved as PDF or PNG (plan M4.3).

* :func:`section_figure` - any :class:`~PyHydroGeophysX.results.protocol.ModelResultV2`
  (mesh, grid slice, layered line or sounding), masked by default with the
  basis noted under the axes;
* :func:`pseudosection_figure` - ERT apparent resistivity at the pseudosection
  points the ERT page and workflows use (``ert_io.pseudosection_points``);
* :func:`save_publication` - vector PDF with embedded fonts, or 300 dpi PNG.
"""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any, Literal

import numpy as np

from PyHydroGeophysX.results.protocol import GridGeometry, LayeredGeometry, MeshGeometry, ModelResultV2

from .publication import (
    add_colorbar,
    add_scale_bar,
    add_title_block,
    cjk_fonts,
    labels,
    parameter_label,
    publication_style,
)

#: Figure attribute naming the language a figure was made in, for saving it in that style.
_LANGUAGE = "_phgx_language"


def _finish(fig: Any, language: str) -> Any:
    """Fix the fonts of the figure's texts now: Matplotlib resolves a font family when it
    draws, by which time the style may no longer be in force (a Qt canvas, a later save)."""
    from matplotlib.text import Text

    setattr(fig, _LANGUAGE, language)
    fonts = cjk_fonts() if language.lower().startswith("zh") else []
    if fonts:
        texts = list(fig.findobj(Text)) + [cell.get_text() for cell in _table_cells(fig)]
        for text in texts:
            text.set_fontfamily([*fonts, "DejaVu Sans"])
    return fig


def _table_cells(fig: Any) -> list[Any]:
    """The cells of the figure's tables (the title block), which ``findobj`` does not reach."""
    return [cell for ax in fig.axes for table in ax.tables for cell in table.get_celld().values()]


#: The mask notes of ``ModelResultV2.display_mask`` in Chinese.
_MASK_NOTES_ZH = (
    ("blank below the depth of investigation", "探测深度以下置空"),
    ("cells no ray passes are blank", "无射线穿过的单元置空"),
    ("blank where coverage < 10^", "覆盖度低于 10^"),
    (" (log10 cumulative sensitivity)", " 处置空（累计灵敏度取 log10）"),
    ("blank where resolution < ", "分辨率低于 "),
)


def mask_note(basis: str, language: str) -> str:
    """The legend's note on the mask, in the figure's language."""
    if not language.lower().startswith("zh"):
        return basis
    text = basis
    for english, chinese in _MASK_NOTES_ZH:
        text = text.replace(english, chinese)
    if "分辨率低于" in text and "处置空" not in text.split("分辨率低于")[-1]:
        text += " 处置空"
    return text.replace("; ", "；")


_CMAPS = {
    "resistivity": "Spectral_r",
    "conductivity": "Spectral",
    "velocity": "viridis",
    "density_contrast": "RdBu_r",
    "susceptibility": "magma",
    "m": "plasma",
    "rho0": "Spectral_r",
}


def section_figure(
    result: ModelResultV2,
    parameter: str | None = None,
    *,
    language: str = "zh",
    title: str = "",
    title_block: Mapping[str, str] | None = None,
    masked: bool = True,
    limits: tuple[float, float] | None = None,
    cmap: str | None = None,
    scale_bar: bool = True,
    size: tuple[float, float] = (7.5, 3.6),
) -> Any:
    """A report figure of one parameter of ``result``; returns the Matplotlib figure."""
    from matplotlib.figure import Figure

    name = parameter or next(iter(result.parameters))
    p = result.parameters[name]
    values = np.asarray(p.values, dtype=float).ravel().copy()
    mask, basis = result.display_mask()
    if masked and mask is not None:
        values[~mask] = np.nan
    shown = np.log10(np.where(values > 0, values, np.nan)) if p.log_scale else values
    words = labels(language)
    colours = cmap or _CMAPS.get(name.split("_step")[0], "viridis")
    with publication_style(language):
        fig = Figure(figsize=size)
        ax = fig.add_subplot(111)
        artist = _draw(ax, result, shown, colours, words)
        if artist is not None and limits is not None:
            lo, hi = limits
            artist.set_clim(*((np.log10(lo), np.log10(hi)) if p.log_scale else (lo, hi)))
        if artist is not None:
            add_colorbar(fig, ax, artist, parameter_label(name, p.unit, language), log_scale=p.log_scale)
        equal = isinstance(result.geometry, MeshGeometry) or (
            isinstance(result.geometry, GridGeometry) and len(result.geometry.edges) == 2
        )
        if equal:
            ax.set_aspect("equal", adjustable="box")
        if (
            scale_bar
            and artist is not None
            and not (isinstance(result.geometry, LayeredGeometry) and result.geometry.n_soundings == 1)
        ):
            add_scale_bar(ax)
        if title:
            ax.set_title(title)
        if masked and basis:
            note = f"{words['masked']}: {mask_note(basis, language)}"
            ax.text(0.0, -0.18, note, transform=ax.transAxes, fontsize=7, color="#444444", va="top")
        if title_block:
            add_title_block(fig, title_block, language=language)
    return _finish(fig, language)


def _draw(ax: Any, result: ModelResultV2, shown: np.ndarray, cmap: str, words: Mapping[str, str]) -> Any:
    geometry = result.geometry
    if isinstance(geometry, MeshGeometry):
        if geometry.dim != 2:
            raise ValueError("a 3-D mesh has no section figure; export it to VTK")
        from matplotlib.collections import PolyCollection

        polygons = [geometry.nodes[row[row >= 0]] for row in geometry.cells]
        collection = PolyCollection(
            polygons, array=np.ma.masked_invalid(shown), cmap=cmap, edgecolors="face", linewidths=0.05
        )
        ax.add_collection(collection)
        ax.autoscale_view()
        ax.set_xlabel(f"{words['distance']} (m)")
        ax.set_ylabel(f"{words['elevation']} (m)")
        return collection
    if isinstance(geometry, GridGeometry):
        order: Literal["C", "F"] = "F" if geometry.order == "F" else "C"
        grid_cells: np.ndarray = shown.reshape(geometry.shape, order=order)
        if len(geometry.edges) == 3:
            grid_cells = grid_cells[:, :, -1]
        ax.set_xlabel(f"{words.get(geometry.axes[0], geometry.axes[0])} (m)")
        ax.set_ylabel(f"{words.get(geometry.axes[1], geometry.axes[1])} (m)")
        return ax.pcolormesh(
            geometry.edges[0],
            geometry.edges[1],
            np.ma.masked_invalid(grid_cells.T),
            cmap=cmap,
            shading="flat",
        )
    assert isinstance(geometry, LayeredGeometry)
    tops = geometry.layer_tops()
    cells = shown.reshape(geometry.n_soundings, geometry.n_layers)
    bottom = float(tops[:, -1].max()) * 1.3 or 1.0
    if geometry.n_soundings == 1:
        ax.step(np.r_[cells[0], cells[0][-1]], np.r_[tops[0], bottom], where="post", color="black")
        ax.invert_yaxis()
        ax.set_ylabel(f"{words['depth']} (m)")
        return None
    positions = (
        np.arange(geometry.n_soundings, dtype=float) if geometry.positions is None else geometry.positions
    )
    half = 0.5 * (positions[1] - positions[0]) if positions.size > 1 else 0.5
    x_edges = np.r_[positions[0] - half, 0.5 * (positions[1:] + positions[:-1]), positions[-1] + half]
    depth_edges = np.linspace(0.0, bottom, 80)
    centers = 0.5 * (depth_edges[1:] + depth_edges[:-1])
    grid = np.full((centers.size, geometry.n_soundings), np.nan)
    for s in range(geometry.n_soundings):
        layer = np.clip(np.searchsorted(tops[s], centers, side="right") - 1, 0, geometry.n_layers - 1)
        grid[:, s] = cells[s, layer]
    mesh = ax.pcolormesh(x_edges, depth_edges, np.ma.masked_invalid(grid), cmap=cmap, shading="flat")
    ax.invert_yaxis()
    ax.set_xlabel(f"{words['distance']} (m)")
    ax.set_ylabel(f"{words['depth']} (m)")
    return mesh


def pseudosection_figure(
    points: Any,
    *,
    language: str = "zh",
    title: str = "",
    title_block: Mapping[str, str] | None = None,
    size: tuple[float, float] = (7.5, 3.2),
) -> Any:
    """Apparent resistivity at its pseudosection points.

    ``points`` is an ``(n, 3)`` array of (x, pseudo-depth, apparent
    resistivity) - what ``ert_io.pseudosection_points`` returns - or a
    pyGIMLi ERT data container, placed the same way.
    """
    from matplotlib.figure import Figure

    if hasattr(points, "dataMap"):
        from PyHydroGeophysX.data_processing import ert_io

        points = ert_io.container_pseudosection(points)
    table = np.asarray(points, dtype=float)
    keep = np.all(np.isfinite(table), axis=1) & (table[:, 2] > 0)
    x, depth, rhoa = table[keep, 0], np.abs(table[keep, 1]), table[keep, 2]
    words = labels(language)
    with publication_style(language):
        fig = Figure(figsize=size)
        ax = fig.add_subplot(111)
        scatter = ax.scatter(x, depth, c=np.log10(rhoa), cmap="Spectral_r", s=18, edgecolors="none")
        ax.invert_yaxis()
        ax.set_xlabel(f"{words['distance']} (m)")
        ax.set_ylabel(f"{words['pseudo_depth']} (m)")
        add_colorbar(fig, ax, scatter, f"{words['apparent_resistivity']} (ohm.m)", log_scale=True)
        if title:
            ax.set_title(title)
        if title_block:
            add_title_block(fig, title_block, language=language)
    return _finish(fig, language)


def save_publication(fig: Any, path: str | Path, *, dpi: int = 300) -> Path:
    """Save as PDF (vector, TrueType fonts embedded) or PNG at ``dpi``, by the suffix."""
    target = Path(path)
    if target.suffix.lower() not in (".pdf", ".png", ".svg"):
        raise ValueError(f"save as .pdf, .png or .svg, not {target.suffix!r}")
    target.parent.mkdir(parents=True, exist_ok=True)
    with publication_style(str(getattr(fig, _LANGUAGE, "en"))):
        fig.savefig(target, dpi=dpi, bbox_inches="tight", facecolor="white")
    return target


__all__ = ["pseudosection_figure", "save_publication", "section_figure"]
