"""MT sites and recordings as survey-view descriptions.

* The layout: every site (a transfer function or a recording) at its latitude
  and longitude, projected to local metres as ``mt.station_distances`` does,
  with its elevation; a recording's electric dipoles drawn from the channel
  azimuths and lengths, centred on the site. The profile direction is the
  sites' principal direction, so distances along it are the 2-D inversion's.
* The curves of a site: the recording chosen for it, each channel in the
  logger's units (or in field units, mV/km and nT, when ``calibrated``),
  seconds from the start of the run.

A site is a *group*; its recordings are listed by the page, which picks the one
shown with :meth:`MTSurvey.choose_run`.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import numpy as np

from PyHydroGeophysX.survey.layout import (
    LineFrame,
    SurveyLayout,
    SurveyLinks,
    SurveyPoints,
    local_projection,
)
from PyHydroGeophysX.survey.pseudo import PseudoPoints
from PyHydroGeophysX.survey.traces import TraceSet, Window

#: Channels in the order a curve view lists them.
COMPONENTS = ("ex", "ey", "hx", "hy", "hz")


def site_name(item: Any, fallback: str) -> str:
    """A site's name: its station, or ``fallback`` when it has none."""
    name = str(getattr(item, "station", "") or "").strip()
    return name or fallback


class MTSurvey:
    """The survey provider of an MT page: its transfer functions and its recordings."""

    def __init__(
        self, sites: Sequence[Any] = (), runs: Sequence[Any] = (), *, calibrated: bool = False
    ) -> None:
        self.sites = list(sites)
        self.runs = list(runs)
        self.calibrated = bool(calibrated)
        self._chosen: dict[str, int] = {}
        self._layout: SurveyLayout | None = None
        self._line: dict[int, float | None] = {}

    # -- the page's choices ---------------------------------------------------------------------
    def runs_of(self, site: str) -> list[int]:
        """Indices into :attr:`runs` of the recordings of ``site``."""
        return [i for i, run in enumerate(self.runs) if site_name(run, f"run {i + 1}") == site]

    def choose_run(self, site: str, index: int) -> None:
        """Show recording ``index`` for ``site``; its dipoles are drawn on the next layout."""
        self._chosen[site] = int(index)
        self._layout = None

    def chosen_run(self, site: str) -> int | None:
        runs = self.runs_of(site)
        if not runs:
            return None
        chosen = self._chosen.get(site)
        return chosen if chosen in runs else runs[0]

    # -- SurveyProvider -------------------------------------------------------------------------
    def survey_capabilities(self) -> frozenset[str]:
        found = set()
        if self.sites or self.runs:
            found.add("layout")
        if self.runs:
            found.update(("traces", "spectrum"))
        return frozenset(found)

    def survey_layout(self) -> SurveyLayout | None:
        if self._layout is None:
            self._layout = self._build_layout()
        return self._layout

    def survey_pseudo(self) -> PseudoPoints | None:
        return None

    def survey_traces(self, group: str, channels: Sequence[str]) -> TraceSet | None:
        index = self.chosen_run(group)
        if index is None:
            return None
        run = self.runs[index]
        if self.calibrated:
            run = run.calibrated()
        present = [c for c in COMPONENTS if c in run.channels] + [
            c for c in run.channels if c not in COMPONENTS
        ]
        wanted = [c for c in present if not channels or c in channels]
        if not wanted:
            return None
        values = run.array(wanted)
        units = [str(run.channels[c].units or "") for c in wanted]
        labels = tuple(f"{c.upper()} ({u})" if u else c.upper() for c, u in zip(wanted, units, strict=True))
        unit = units[0] if len(set(units)) == 1 else ""
        rate = float(run.sample_rate)
        t = (
            np.arange(values.shape[1], dtype=float) / rate
            if rate > 0
            else np.arange(values.shape[1], dtype=float)
        )
        if index not in self._line:
            self._line[index] = _line_frequency(self.runs[index])
        line = self._line[index]
        return TraceSet(
            t,
            values,
            tuple(wanted),
            unit=unit,
            labels=labels,
            keys=tuple(("channel", group, index, c) for c in wanted),
            windows=_windows(t),
            title=f"{group} · {rate:g} Hz",
            line_frequency=line,
        )

    # -- layout -----------------------------------------------------------------------------------
    def _positions(self) -> list[tuple[str, float, float, float, str]]:
        """``(name, longitude, latitude, elevation, kind)`` of every site, transfer functions first."""
        seen: dict[str, tuple[str, float, float, float, str]] = {}
        for i, tf in enumerate(self.sites):
            name = site_name(tf, f"site {i + 1}")
            seen.setdefault(name, (name, tf.longitude, tf.latitude, tf.elevation, "site"))
        for i, run in enumerate(self.runs):
            name = site_name(run, f"run {i + 1}")
            seen.setdefault(name, (name, run.longitude, run.latitude, run.elevation, "rx"))
        return list(seen.values())

    def _build_layout(self) -> SurveyLayout | None:
        places = self._positions()
        if not places:
            return None
        lon = np.array([p[1] for p in places], float)
        lat = np.array([p[2] for p in places], float)
        located = np.isfinite(lon) & np.isfinite(lat)
        east = np.zeros(len(places))
        north = np.zeros(len(places))
        if located.any():
            east[located], north[located] = local_projection(lon[located], lat[located])
        # Sites without coordinates are placed in a row after the located ones.
        spacing = 100.0
        for k, j in enumerate(np.flatnonzero(~located)):
            east[j], north[j] = float(np.max(east, initial=0.0)) + spacing * (k + 1), 0.0
        elevation = np.array([p[3] if np.isfinite(p[3]) else 0.0 for p in places], float)
        names = [p[0] for p in places]
        ids: list[str] = list(names)
        roles: list[str] = [p[4] for p in places]
        groups: list[str] = list(names)
        xyz: list[tuple[float, float, float]] = []
        keys: list[tuple[Any, ...]] = []
        for i, name in enumerate(names):
            xyz.append((float(east[i]), float(north[i]), float(elevation[i])))
            keys.append(("site", name))
        frame = LineFrame.fit(np.column_stack([east, north])) if len(places) > 1 else None
        starts: list[int] = []
        ends: list[int] = []
        kinds: list[str] = []
        link_groups: list[str] = []
        for site_index, name in enumerate(names):
            index = self.chosen_run(name)
            if index is None:
                continue
            for component in ("ex", "ey"):
                channel = self.runs[index].channels.get(component)
                if channel is None:
                    continue
                length = float(getattr(channel, "dipole_length", float("nan")))
                if not np.isfinite(length) or length <= 0:
                    continue
                azimuth = np.radians(float(getattr(channel, "azimuth", 0.0 if component == "ex" else 90.0)))
                half = np.array([np.sin(azimuth), np.cos(azimuth)]) * length / 2.0
                centre = np.array([east[site_index], north[site_index]])
                for end in (centre - half, centre + half):
                    ids.append(f"{name}-{component}-{len(ids)}")
                    roles.append("electrode")
                    xyz.append((float(end[0]), float(end[1]), float(elevation[site_index])))
                    groups.append(name)
                    keys.append(("electrode", name, component, len(ids)))
                starts.append(len(ids) - 2)
                ends.append(len(ids) - 1)
                kinds.append(f"dipole_{component}")
                link_groups.append(name)
        points = SurveyPoints(
            tuple(ids),
            tuple(roles),
            np.asarray(xyz, float).reshape(-1, 3),
            tuple(groups),
            keys=tuple(keys),
            attrs={"Elevation (m)": np.asarray([p[2] for p in xyz], float)},
        )
        links = SurveyLinks(np.asarray(starts), np.asarray(ends), tuple(kinds), tuple(link_groups))
        return SurveyLayout(points, links, frame=frame, crs=None, title="MT")


def _windows(t: np.ndarray) -> tuple[Window, ...]:
    if t.size < 2:
        return ()
    start, end = float(t[0]), float(t[-1])
    windows = [Window("Whole record", start, max(end, start + 1e-6), "record")]
    if end - start > 120.0:
        windows.append(Window("First minute", start, start + 60.0, "signal"))
        windows.append(Window("Last minute", end - 60.0, end, "noise"))
    return tuple(windows)


def _line_frequency(run: Any) -> float | None:
    try:
        from PyHydroGeophysX.data_processing.mt.timeseries import powerline_frequency

        found = powerline_frequency(run)
    except (ValueError, IndexError, KeyError, ImportError):
        return None
    return float(found) if found else None


__all__ = ["COMPONENTS", "MTSurvey", "site_name"]
