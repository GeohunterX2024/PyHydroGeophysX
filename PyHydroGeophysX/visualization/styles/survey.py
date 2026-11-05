"""Report figures of a survey's layout, its curves and their spectra.

The Studio's survey views are interactive (pyqtgraph, PyVista); these are the
same contents drawn for a report: equal-aspect plan with a scale bar and a north
arrow, terrain section with the pseudo-depth points and their convention, a
record with its reference curve on a second axis, and a power spectrum with the
power-line harmonics marked. Save them with :func:`save_publication`.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import numpy as np

from PyHydroGeophysX.survey.layout import SurveyLayout
from PyHydroGeophysX.survey.pseudo import PseudoPoints
from PyHydroGeophysX.survey.scene import LINK_COLOURS, ROLE_STYLE
from PyHydroGeophysX.survey.spectra import Spectrum, line_harmonics
from PyHydroGeophysX.survey.traces import TraceSet

from .figures import _finish
from .publication import (
    add_colorbar,
    add_north_arrow,
    add_scale_bar,
    add_title_block,
    labels,
    publication_style,
)

_WORDS = {
    "zh": {
        "east": "东",
        "north": "北",
        "time": "时间",
        "frequency": "频率",
        "psd": "功率谱密度",
        "remote": "远端",
        "harmonic": "工频谐波",
        "aliased": "折叠",
        "convention": "拟深度约定",
    },
    "en": {
        "east": "East",
        "north": "North",
        "time": "Time",
        "frequency": "Frequency",
        "psd": "PSD",
        "remote": "Remote",
        "harmonic": "Line harmonics",
        "aliased": "aliased",
        "convention": "Pseudo-depth convention",
    },
}
_MARKERS = {"triangle": "^", "triangle_down": "v", "square": "s", "diamond": "D", "circle": "o"}


def _words(language: str) -> dict[str, str]:
    return _WORDS["zh" if language.lower().startswith("zh") else "en"]


def survey_plan_figure(
    layout: SurveyLayout,
    *,
    group: str = "",
    language: str = "zh",
    title: str = "",
    title_block: Mapping[str, str] | None = None,
    size: tuple[float, float] = (7.0, 6.0),
) -> Any:
    """Plan of the points (remote ones noted, not drawn) with the current group's links."""
    from matplotlib.figure import Figure

    extra = _words(language)
    points = layout.points
    on_line = layout.line_points()
    with publication_style(language):
        fig = Figure(figsize=size)
        ax = fig.add_subplot(111)
        for role in dict.fromkeys(points.role):
            mask = points.where(role) & on_line
            if group:
                mask &= np.array([g in ("", group) for g in points.group], bool)
            if not mask.any():
                continue
            colour, symbol, marker_size = ROLE_STYLE[role]
            ax.scatter(
                points.xyz[mask, 0],
                points.xyz[mask, 1],
                s=marker_size**2 * 0.6,
                marker=_MARKERS.get(symbol, "o"),
                color=colour,
                label=role,
                zorder=3,
            )
        links = layout.links
        for start, end, kind, link_group in zip(links.start, links.end, links.kind, links.group, strict=True):
            if group and link_group not in ("", group):
                continue
            if not (on_line[start] and on_line[end]):
                continue
            ax.plot(
                points.xyz[[start, end], 0],
                points.xyz[[start, end], 1],
                color=LINK_COLOURS.get(kind, "#374151"),
                lw=1.2,
                zorder=2,
            )
        remote = np.flatnonzero(points.is_remote())
        if remote.size:
            notes = [
                f"{extra['remote']} {points.role[i]} ({points.xyz[i, 0]:.0f}, {points.xyz[i, 1]:.0f})"
                for i in remote
            ]
            ax.text(0.01, 0.01, "; ".join(notes), transform=ax.transAxes, fontsize=7, va="bottom")
        ax.set_aspect("equal", adjustable="datalim")
        ax.set_xlabel(f"{extra['east']} (m)")
        ax.set_ylabel(f"{extra['north']} (m)")
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=7, loc="upper left")
        add_scale_bar(ax)
        add_north_arrow(ax, language=language)
        if title:
            ax.set_title(title)
        if title_block:
            add_title_block(fig, title_block, language=language)
    return _finish(fig, language)


def survey_section_figure(
    layout: SurveyLayout,
    pseudo: PseudoPoints | None = None,
    *,
    colour_by: str = "",
    log_scale: bool = False,
    unit: str = "",
    language: str = "zh",
    title: str = "",
    title_block: Mapping[str, str] | None = None,
    size: tuple[float, float] = (7.5, 3.6),
) -> Any:
    """Terrain and electrodes along the line, with the pseudo-depth points below the ground."""
    from matplotlib.figure import Figure

    words = labels(language)
    along = layout.along()
    on_line = layout.line_points()
    with publication_style(language):
        fig = Figure(figsize=size)
        ax = fig.add_subplot(111)
        if layout.topography is not None and layout.topography.distance.size:
            ax.plot(layout.topography.distance, layout.topography.elevation, color="#4d7c0f", lw=1.0)
        ax.scatter(along[on_line], layout.points.xyz[on_line, 2], marker="v", s=14, color="#1f2937", zorder=3)
        if pseudo is not None and pseudo.size:
            values = pseudo.attrs.get(colour_by) if colour_by else None
            if values is not None:
                shown = np.log10(np.where(values > 0, values, np.nan)) if log_scale else values
                scatter = ax.scatter(
                    pseudo.along, pseudo.elevation, c=shown, s=14, cmap="Spectral_r", zorder=2
                )
                add_colorbar(
                    fig, ax, scatter, f"{colour_by} ({unit})" if unit else colour_by, log_scale=log_scale
                )
            else:
                ax.scatter(pseudo.along, pseudo.elevation, s=8, color="#6b7280", zorder=2)
            ax.text(0.01, 0.01, pseudo.legend, transform=ax.transAxes, fontsize=7, va="bottom")
        ax.set_xlabel(f"{words['distance']} (m)")
        ax.set_ylabel(f"{words['elevation']} (m)")
        ax.grid(True, alpha=0.3)
        if title:
            ax.set_title(title)
        if title_block:
            add_title_block(fig, title_block, language=language)
    return _finish(fig, language)


def trace_figure(
    traces: TraceSet,
    *,
    window: str = "",
    language: str = "zh",
    title: str = "",
    size: tuple[float, float] = (7.5, 3.4),
) -> Any:
    """The channels over time; the reference curve on the right axis."""
    from matplotlib.figure import Figure

    extra = _words(language)
    chosen = traces.window(window) if window else None
    with publication_style(language):
        fig = Figure(figsize=size)
        ax = fig.add_subplot(111)
        for row, label in enumerate(traces.labels):
            ax.plot(traces.t, traces.values[row], lw=0.8, label=label)
        if traces.reference is not None:
            twin = ax.twinx()
            twin.plot(traces.t, traces.reference, color="#9a3412", lw=1.0, ls="--")
            twin.set_ylabel(
                f"{traces.reference_label} ({traces.reference_unit})"
                if traces.reference_unit
                else traces.reference_label,
                color="#9a3412",
            )
            ax.set_zorder(twin.get_zorder() + 1)
            ax.patch.set_visible(False)
        if chosen is not None:
            ax.set_xlim(chosen.start, chosen.end)
        ax.set_xlabel(f"{extra['time']} (s)")
        ax.set_ylabel(traces.unit)
        ax.grid(True, alpha=0.3)
        if traces.size:
            ax.legend(fontsize=7, ncol=4)
        ax.set_title(title or traces.title)
    return _finish(fig, language)


def spectrum_figure(
    spectrum: Spectrum,
    *,
    line_frequency: float = 50.0,
    language: str = "zh",
    title: str = "",
    size: tuple[float, float] = (7.5, 3.4),
) -> Any:
    """Power spectral density on a log axis, the line harmonics marked (dashed where folded)."""
    from matplotlib.figure import Figure

    extra = _words(language)
    with publication_style(language):
        fig = Figure(figsize=size)
        ax = fig.add_subplot(111)
        keep = spectrum.frequency > 0
        for row, label in enumerate(spectrum.labels):
            ax.semilogy(spectrum.frequency[keep], spectrum.power[row, keep], lw=0.8, label=label)
        for harmonic in line_harmonics(spectrum.sample_rate, line_frequency):
            ax.axvline(
                harmonic.apparent, color="#dc2626", lw=0.7, ls="--" if harmonic.aliased else "-", alpha=0.7
            )
        ax.set_xlim(0, spectrum.nyquist)
        ax.set_xlabel(f"{extra['frequency']} (Hz)")
        ax.set_ylabel(f"{extra['psd']} ({spectrum.unit}²/Hz)" if spectrum.unit else extra["psd"])
        ax.grid(True, which="both", alpha=0.25)
        if spectrum.labels:
            ax.legend(fontsize=7, ncol=4)
        ax.set_title(title)
    return _finish(fig, language)


__all__ = ["spectrum_figure", "survey_plan_figure", "survey_section_figure", "trace_figure"]
