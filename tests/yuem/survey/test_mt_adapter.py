"""MT sites and recordings as survey descriptions, and the MT page's sites tab."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pytest

from PyHydroGeophysX.data_processing import mt
from PyHydroGeophysX.survey.adapters.mt import MTSurvey


def _run(station: str, latitude: float, longitude: float, rate: float = 250.0, hum: float = 0.5) -> Any:
    rng = np.random.default_rng(5)
    n = int(rate * 180)
    t = np.arange(n) / rate
    ex = hum * np.sin(2 * np.pi * 50.0 * t) + rng.standard_normal(n)
    channels = [
        mt.Channel("ex", ex, "mV", dipole_length=100.0),
        mt.Channel("ey", rng.standard_normal(n), "mV", dipole_length=80.0),
        mt.Channel("hx", rng.standard_normal(n), "nT"),
    ]
    return mt.TimeSeriesRun(
        channels, rate, "2024-01-01T00:00:00", station=station, latitude=latitude, longitude=longitude
    )


def _sites() -> list[Any]:
    sites = []
    for i in range(4):
        tf = mt.read_transfer_function(
            Path(__file__).resolve().parents[3] / "examples" / "data" / "MT" / "NMX20.xml"
        )
        tf.station = f"S{i}"
        tf.latitude = 34.47 + 0.004 * i
        tf.longitude = -108.71 + 0.003 * i
        sites.append(tf)
    return sites


def test_sites_are_placed_as_the_profile_projects_them(examples_data: Path) -> None:
    from PyHydroGeophysX.data_processing.mt.inversion2d import station_distances

    sites = _sites()
    survey = MTSurvey(sites, [_run("S1", sites[1].latitude, sites[1].longitude)])
    assert survey.survey_capabilities() == frozenset({"layout", "traces", "spectrum"})
    layout = survey.survey_layout()
    assert layout is not None
    on_sites = np.array([r in ("site", "rx") for r in layout.points.role])
    expected, _azimuth = station_distances(sites)
    np.testing.assert_allclose(layout.along()[on_sites], expected, atol=1e-6)
    assert layout.groups()[:4] == ("S0", "S1", "S2", "S3")
    dipoles = [k for k in layout.links.kind if k.startswith("dipole")]
    assert sorted(dipoles) == ["dipole_ex", "dipole_ey"]
    ex = layout.links.kind.index("dipole_ex")
    a, b = layout.links.start[ex], layout.links.end[ex]
    assert np.hypot(*(layout.points.xyz[a, :2] - layout.points.xyz[b, :2])) == pytest.approx(100.0)


def test_a_site_without_a_recording_has_no_curves(examples_data: Path) -> None:
    survey = MTSurvey(_sites())
    assert survey.survey_capabilities() == frozenset({"layout"})
    assert survey.survey_traces("S0", ()) is None


def test_curves_and_hum_of_a_recording() -> None:
    from PyHydroGeophysX.survey.spectra import noise_metrics, trace_spectrum

    survey = MTSurvey((), [_run("R1", 34.5, -108.7), _run("R1", 34.5, -108.7, rate=500.0)])
    assert survey.runs_of("R1") == [0, 1]
    traces = survey.survey_traces("R1", ["ex", "hx"])
    assert (
        traces is not None and traces.channels == ("ex", "hx") and traces.sample_rate == pytest.approx(250.0)
    )
    assert traces.labels == ("EX (mV)", "HX (nT)") and traces.unit == ""
    assert [w.name for w in traces.windows] == ["Whole record", "First minute", "Last minute"]
    survey.choose_run("R1", 1)
    other = survey.survey_traces("R1", ())
    assert other is not None and other.sample_rate == pytest.approx(500.0)
    metrics = noise_metrics(traces, trace_spectrum(traces), line_frequency=50.0)
    assert metrics[0].line_db > metrics[1].line_db + 10


@pytest.mark.gui
def test_the_mt_page_has_a_sites_tab(qtbot: Any, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    pytest.importorskip("PySide6")
    from PyHydroGeophysX.qt_apps.modules import build_module
    from PyHydroGeophysX.qt_apps.modules.mt_survey_tab import MTSurveyTab
    from PyHydroGeophysX.qt_apps.state import StudioState

    monkeypatch.setenv("PHGX_PROJECT_DIR", str(tmp_path / "project"))
    page = build_module("mt", StudioState.from_context(None), lambda *a, **k: None)
    qtbot.addWidget(page)
    tabs = [page._tabs.widget(i) for i in range(page._tabs.count())]
    tab = next(w for w in tabs if isinstance(w, MTSurveyTab))
    page._runs = [_run("R1", 34.5, -108.7)]
    page.show()
    page._tabs.setCurrentWidget(tab)
    qtbot.waitUntil(lambda: tab.tree.topLevelItemCount() == 1)
    tab.tree.setCurrentItem(tab.tree.topLevelItem(0).child(0))
    assert tab.workbench.selection.group() == "R1"
    tab.workbench.show_tab("spectrum")
    assert tab.workbench.spectrum.metrics()
    page.stop_workers(wait_ms=2000)
