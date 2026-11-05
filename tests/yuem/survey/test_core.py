"""The Qt-free survey descriptions: layout, pseudo-depth, traces, spectra, 3-D scene."""

from __future__ import annotations

import numpy as np
import pytest

from PyHydroGeophysX.survey.layout import LineFrame, SurveyPoints, TopographyProfile, local_projection
from PyHydroGeophysX.survey.pseudo import (
    PYGIMLI_DEPTH_FACTOR,
    PseudoPoints,
    pygimli_coordinates,
    zond_coordinates,
)
from PyHydroGeophysX.survey.scene import LineLayer, PointLayer, SceneOptions, SurfaceLayer, build_scene
from PyHydroGeophysX.survey.spectra import (
    apparent_frequency,
    line_harmonics,
    noise_metrics,
    psd,
    segment_length,
    trace_spectrum,
)
from PyHydroGeophysX.survey.traces import TraceSet, Window, windows_from_cycle

from . import synth

# -- layout ------------------------------------------------------------------


def test_points_validate_their_shapes() -> None:
    with pytest.raises(ValueError, match="roles"):
        SurveyPoints(("a",), ("Q",), np.zeros((1, 3)))
    with pytest.raises(ValueError, match="shape"):
        SurveyPoints(("a",), ("A",), np.zeros((1, 2)))
    with pytest.raises(ValueError, match="attribute"):
        SurveyPoints(("a",), ("A",), np.zeros((1, 3)), attrs={"v": np.zeros(2)})


def test_layout_groups_extent_and_positions() -> None:
    layout = synth.layout()
    assert layout.groups() == tuple(synth.SHOTS)
    xmin, xmax, ymin, ymax, *_ = layout.extent()
    assert (xmin, xmax) == (0.0, 0.0)
    assert ymin == min(synth.SHOTS.values()) and ymax == max(synth.SHOTS.values())
    assert layout.extent(include_remote=True)[1] == synth.REMOTE_B[0]
    xy = layout.position_at(np.array([10.0, 50.0]))
    np.testing.assert_allclose(xy, [[0.0, 10.0], [0.0, 50.0]])
    assert layout.line_length() == pytest.approx(240.0)


def test_line_frame_matches_mt_station_distances() -> None:
    from types import SimpleNamespace

    from PyHydroGeophysX.data_processing.mt.inversion2d import station_distances

    lat = 34.47 + np.array([0.0, 0.004, 0.0085, 0.013, 0.0172])
    lon = -108.71 + np.array([0.0, 0.003, 0.0061, 0.0094, 0.0125])
    sites = [
        SimpleNamespace(latitude=float(la), longitude=float(lo)) for la, lo in zip(lat, lon, strict=True)
    ]
    expected, azimuth = station_distances(sites)
    east, north = local_projection(lon, lat)
    frame = LineFrame.fit(np.column_stack([east, north]))
    np.testing.assert_allclose(frame.along(np.column_stack([east, north])), expected, atol=1e-6)
    assert frame.azimuth == pytest.approx(azimuth, abs=1e-6)


def test_topography_interpolates_and_holds_its_ends() -> None:
    topo = TopographyProfile([10.0, 0.0], [2.0, 1.0])
    np.testing.assert_allclose(topo.at([-5.0, 5.0, 20.0]), [1.0, 1.5, 2.0])


# -- pseudo-depth --------------------------------------------------------------


def _dcip_reference(xa: np.ndarray, xm: np.ndarray, xn: np.ndarray, xb: np.ndarray | None) -> tuple:
    """``phgx_dcip.figures.pseudo_coordinates`` as the plugin ships it (copied verbatim)."""
    xa, xm, xn = (np.asarray(v, float) for v in (xa, xm, xn))
    near = np.where(np.abs(xm - xa) <= np.abs(xn - xa), xm, xn)
    px, pz = 0.5 * (xa + near), 0.5 * np.abs(near - xa)
    if xb is not None:
        xb = np.asarray(xb, float)
        rows = np.isfinite(xb)
        if np.any(rows):
            px[rows] = 0.25 * (xa[rows] + xb[rows] + xm[rows] + xn[rows])
            pz[rows] = 0.25 * np.abs(xa[rows] + xb[rows] - xm[rows] - xn[rows])
    return px, pz


def test_zond_convention_equals_the_dcip_plugin() -> None:
    rng = np.random.default_rng(7)
    xa = rng.uniform(-400, 400, 200)
    xm = rng.uniform(-400, 400, 200)
    xn = xm + rng.choice([-40.0, 40.0], 200)
    xb = np.where(rng.random(200) < 0.3, rng.uniform(-400, 400, 200), np.nan)
    for b in (None, xb):
        got = zond_coordinates(xa, xm, xn, b)
        want = _dcip_reference(xa, xm, xn, b)
        np.testing.assert_array_equal(got[0], want[0])
        np.testing.assert_array_equal(got[1], want[1])
    try:
        from phgx_dcip.figures import pseudo_coordinates
    except ImportError:
        return
    plugin = pseudo_coordinates(xa, xm, xn, xb)
    np.testing.assert_array_equal(zond_coordinates(xa, xm, xn, xb)[0], plugin[0])
    np.testing.assert_array_equal(zond_coordinates(xa, xm, xn, xb)[1], plugin[1])


def test_pygimli_convention_equals_ert_io() -> None:
    from PyHydroGeophysX.data_processing import ert_io

    assert PYGIMLI_DEPTH_FACTOR == ert_io.PSEUDO_DEPTH_FACTOR
    rng = np.random.default_rng(11)
    x = np.sort(rng.uniform(0, 300, 48))
    abmn = rng.integers(0, 50, size=(300, 4))  # some indices fall outside x
    px, pz, inside = pygimli_coordinates(x, *abmn.T)
    table = ert_io.pseudosection_points(x, *abmn.T, np.ones(300))
    np.testing.assert_array_equal(px, table[:, 0])
    np.testing.assert_array_equal(pz, table[:, 1])
    assert int(inside.sum()) == table.shape[0]
    one_based = pygimli_coordinates([0.0, 1.0, 2.0, 3.0], [1], [4], [2], [3])
    np.testing.assert_allclose([one_based[0][0], one_based[1][0]], [1.5, 0.57])


def test_pseudo_points_sit_under_the_ground() -> None:
    points = synth.pseudo()
    np.testing.assert_allclose(points.elevation, synth.topography().at(points.along) - points.depth)
    assert "AM" in points.legend
    with pytest.raises(ValueError, match="convention"):
        PseudoPoints(np.zeros(1), np.zeros(1), "nonsense")


# -- traces ----------------------------------------------------------------


def test_traces_windows_and_selection() -> None:
    traces = synth.traces()
    assert traces.sample_rate == pytest.approx(250.0)
    names = [w.name for w in traces.windows]
    assert names == ["Whole record", "On-time (steady)", "End of on-time", "Off-time"]
    off = traces.window("Off-time")
    assert off is not None and traces.mask(off).sum() == pytest.approx(1450, abs=2)
    picked = traces.select(["ch2", "missing"])
    assert picked.channels == ("ch2",) and picked.keys == (("trace", "s1", 2, 1),)
    with pytest.raises(ValueError, match="before it starts"):
        Window("bad", 2.0, 1.0)
    with pytest.raises(ValueError, match="samples"):
        TraceSet(np.arange(3.0), np.zeros((1, 4)), ("a",))
    assert [w.kind for w in windows_from_cycle(0.3, 0.1)] == ["record"]


# -- spectra ----------------------------------------------------------------


def test_harmonics_fold_above_nyquist() -> None:
    tones = line_harmonics(250.0, 50.0, 4)
    assert [t.apparent for t in tones] == [50.0, 100.0, 100.0, 50.0]
    assert [t.aliased for t in tones] == [False, False, True, True]
    assert apparent_frequency(60.0, 0.0) == 60.0


def test_welch_finds_the_line_frequency() -> None:
    fs = 250.0
    t = np.arange(4096) / fs
    values = np.sin(2 * np.pi * 50.0 * t) + 0.01 * np.random.default_rng(0).standard_normal(t.size)
    frequency, power = psd(values, fs)
    assert frequency[np.argmax(power[0])] == pytest.approx(50.0, abs=fs / segment_length(t.size))
    assert segment_length(3000) == 512 and segment_length(10) == 10 and segment_length(10**6) == 4096


def test_noise_metrics_follow_the_hum_and_the_noise() -> None:
    quiet, loud = synth.traces(hum=0.0005), synth.traces(hum=0.005)
    window = quiet.window("On-time (steady)")
    signal_window, noise_window = quiet.window("End of on-time"), quiet.window("Off-time")
    metrics = []
    for traces in (quiet, loud):
        spectrum = trace_spectrum(traces, window)
        assert spectrum.reference is not None and spectrum.nyquist == pytest.approx(125.0)
        metrics.append(
            noise_metrics(traces, spectrum, signal_window=signal_window, noise_window=noise_window)[0]
        )
    assert metrics[1].line_db > metrics[0].line_db + 10
    assert metrics[1].noise_rms > metrics[0].noise_rms
    assert metrics[0].snr_db > metrics[1].snr_db
    assert len(metrics[0].harmonics_db) == 4


def test_spectrum_of_a_tiny_record_is_empty() -> None:
    frequency, power = psd(np.zeros(3), 250.0)
    assert frequency.size == 0 and power.shape == (1, 0)


# -- scene --------------------------------------------------------------------


def test_scene_moves_the_remote_b_to_the_edge_unless_asked() -> None:
    layout = synth.layout()
    scene = build_scene(layout, synth.pseudo(), SceneOptions(group="s1"))
    remote = scene.layer("remote")
    assert isinstance(remote, PointLayer)
    distance = np.hypot(remote.xyz[0, 0], remote.xyz[0, 1] - 80.0)
    assert distance < 400.0
    assert scene.notes and "km" in scene.notes[0]
    full = build_scene(layout, None, SceneOptions(group="s1", include_remote=True))
    remote = full.layer("remote")
    assert isinstance(remote, PointLayer)
    np.testing.assert_allclose(remote.xyz[0, :2], synth.REMOTE_B[:2])


def test_scene_layers_follow_the_options() -> None:
    layout, pseudo = synth.layout(), synth.pseudo()
    scene = build_scene(layout, pseudo, SceneOptions(group="s1", colour_by="rho_a", exaggeration=2.0))
    names = scene.names()
    for name in (
        "terrain",
        "points:electrode",
        "points:A",
        "points:other",
        "links",
        "pseudo",
        "pseudo:current",
    ):
        assert name in names
    links = scene.layer("links")
    assert isinstance(links, LineLayer) and links.segments.shape == (2, 2, 3)
    shot_a = scene.layer("points:A")
    assert isinstance(shot_a, PointLayer) and shot_a.xyz.shape[0] == 1
    other = scene.layer("points:other")
    assert isinstance(other, PointLayer) and other.xyz.shape[0] == 3
    cloud = scene.layer("pseudo")
    assert isinstance(cloud, PointLayer) and cloud.values is not None and scene.value_range is not None
    plain = build_scene(layout, pseudo, SceneOptions(group="s1"))
    cloud_plain = plain.layer("pseudo")
    assert isinstance(cloud_plain, PointLayer)
    lift = (cloud.xyz[:, 2] - scene.z_reference) / (cloud_plain.xyz[:, 2] - plain.z_reference)
    np.testing.assert_allclose(lift, 2.0)
    bare = build_scene(
        layout,
        pseudo,
        SceneOptions(show_terrain=False, show_links=False, show_pseudo=False, show_other_groups=False),
    )
    assert not {"terrain", "links", "pseudo", "points:other"} & set(bare.names())
    clipped = build_scene(layout, pseudo, SceneOptions(depth_range=(0.0, 15.0)))
    clipped_cloud = clipped.layer("pseudo")
    assert isinstance(clipped_cloud, PointLayer) and clipped_cloud.xyz.shape[0] < pseudo.size
    terrain = scene.layer("terrain")
    assert isinstance(terrain, SurfaceLayer) and terrain.z.shape[0] == 2
