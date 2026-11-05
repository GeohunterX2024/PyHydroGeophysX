"""A small synthetic pole-dipole line for the survey tests: 4 shots, 8 dipoles, a remote B."""

from __future__ import annotations

import numpy as np

from PyHydroGeophysX.survey.layout import SurveyLayout, SurveyLinks, SurveyPoints, TopographyProfile
from PyHydroGeophysX.survey.pseudo import PseudoPoints, zond_coordinates
from PyHydroGeophysX.survey.traces import TraceSet, windows_from_cycle

SPACING = 20.0
STATIONS = np.arange(9) * SPACING  # electrode positions north, east = 0
SHOTS = {"s1": -40.0, "s2": -20.0, "s3": 180.0, "s4": 200.0}
REMOTE_B = (6000.0, -800.0, 40.0)


def topography() -> TopographyProfile:
    distance = np.linspace(-60.0, 220.0, 29)
    return TopographyProfile(distance, 100.0 + 5.0 * np.sin(distance / 40.0))


def layout() -> SurveyLayout:
    topo = topography()
    ids, roles, xyz, groups, keys = [], [], [], [], []
    for i, north in enumerate(STATIONS):
        ids.append(f"e{i}")
        roles.append("electrode")
        xyz.append((0.0, north, float(topo.at(north))))
        groups.append("")
        keys.append(("electrode", i))
    for shot, north in SHOTS.items():
        ids.append(f"A-{shot}")
        roles.append("A")
        xyz.append((0.0, north, float(topo.at(north))))
        groups.append(shot)
        keys.append(("shot", shot))
    ids.append("B")
    roles.append("B")
    xyz.append(REMOTE_B)
    groups.append("")
    keys.append(("remote", "B"))
    remote = np.array([r == "B" for r in roles])
    n = len(ids)
    along = np.array([p[1] for p in xyz])
    points = SurveyPoints(
        tuple(ids),
        tuple(roles),
        np.array(xyz),
        tuple(groups),
        keys=tuple(keys),
        along=along,
        remote=remote,
        attrs={"index": np.arange(n, dtype=float)},
    )
    b = n - 1
    starts, ends, kinds, link_groups = [], [], [], []
    for k, shot in enumerate(SHOTS):
        starts.append(len(STATIONS) + k)
        ends.append(b)
        kinds.append("AB")
        link_groups.append(shot)
        starts.append(1)
        ends.append(2)
        kinds.append("MN")
        link_groups.append(shot)
    links = SurveyLinks(np.array(starts), np.array(ends), tuple(kinds), tuple(link_groups))
    return SurveyLayout(points, links, topography=topo, title="synthetic")


def readings() -> tuple[np.ndarray, np.ndarray, np.ndarray, list[str]]:
    xa, xm, xn, group = [], [], [], []
    for shot, north in SHOTS.items():
        for i in range(len(STATIONS) - 1):
            xa.append(north)
            xm.append(STATIONS[i])
            xn.append(STATIONS[i + 1])
            group.append(shot)
    return np.array(xa), np.array(xm), np.array(xn), group


def pseudo() -> PseudoPoints:
    xa, xm, xn, group = readings()
    x, depth = zond_coordinates(xa, xm, xn)
    keys = tuple(("trace", g, i % 8, 1) for i, g in enumerate(group))
    rho = 50.0 + np.arange(x.size, dtype=float)
    return PseudoPoints(
        x, depth, "pole_dipole_zond", keys=keys, group=tuple(group), attrs={"rho_a": rho}
    ).on_ground(topography())


def traces(seed: int = 3, hum: float = 0.002) -> TraceSet:
    """A 6 s on / 6 s off record at 250 Hz: a step plus 50 Hz hum and white noise."""
    rng = np.random.default_rng(seed)
    t = np.arange(3000) * 0.004
    on = t < 6.0
    rows = []
    for level in (-0.02, -0.01):
        rows.append(
            np.where(on, level, 0.0) + hum * np.sin(2 * np.pi * 50.0 * t) + 1e-4 * rng.standard_normal(t.size)
        )
    current = np.where(on, -15.0, 0.0)
    return TraceSet(
        t,
        np.array(rows),
        ("ch1", "ch2"),
        "V",
        reference=current,
        reference_label="Current",
        reference_unit="A",
        windows=windows_from_cycle(6.0, 6.0),
        line_frequency=50.0,
        keys=(("trace", "s1", 1, 1), ("trace", "s1", 2, 1)),
    )
