"""The shared survey views: workbench tabs, plan, section, 3-D, curves, spectrum and selection."""

from __future__ import annotations

from collections.abc import Iterator, Sequence
from pathlib import Path
from typing import Any

import numpy as np
import pytest

from PyHydroGeophysX.survey.layout import SurveyLayout
from PyHydroGeophysX.survey.pseudo import PseudoPoints
from PyHydroGeophysX.survey.traces import TraceSet

from ..survey import synth

pytest.importorskip("PySide6")
pytestmark = pytest.mark.gui


class _Provider:
    def __init__(self, capabilities: Sequence[str] = ("layout", "pseudo", "traces", "spectrum")) -> None:
        self.capabilities = frozenset(capabilities)
        self.asked: list[tuple[str, tuple[str, ...]]] = []

    def survey_capabilities(self) -> frozenset[str]:
        return self.capabilities

    def survey_layout(self) -> SurveyLayout | None:
        return synth.layout()

    def survey_pseudo(self) -> PseudoPoints | None:
        return synth.pseudo()

    def survey_traces(self, group: str, channels: Sequence[str]) -> TraceSet | None:
        self.asked.append((group, tuple(channels)))
        traces = synth.traces()
        return traces.select(channels) if channels else traces


@pytest.fixture(autouse=True)
def memory_settings(monkeypatch: pytest.MonkeyPatch) -> Iterator[dict[str, Any]]:
    """The views' remembered choices in memory, never in the user's Studio settings."""
    from PyHydroGeophysX.qt_apps.widgets.survey import common

    store: dict[str, Any] = {}

    def get(self: Any, name: str, default: Any) -> Any:
        return store.get(self._prefix + name, default)

    def put(self: Any, name: str, value: Any) -> None:
        store[self._prefix + name] = value

    monkeypatch.setattr(common.Settings, "get", get)
    monkeypatch.setattr(common.Settings, "set", put)
    yield store


@pytest.fixture
def bench(qtbot: Any) -> Any:
    from PyHydroGeophysX.qt_apps.widgets.survey import SurveyWorkbench

    workbench = SurveyWorkbench()
    qtbot.addWidget(workbench)
    workbench.resize(1100, 760)
    workbench.show()
    qtbot.waitExposed(workbench)
    return workbench


def test_tabs_follow_the_provider(bench: Any) -> None:
    bench.set_provider(_Provider(("layout", "pseudo")))
    assert bench.tabs.isTabVisible(0) and not bench.tabs.isTabVisible(1) and not bench.tabs.isTabVisible(2)
    bench.set_provider(_Provider())
    assert all(bench.tabs.isTabVisible(i) for i in range(3))


def test_plan_and_section_draw_and_select(bench: Any) -> None:
    from PySide6.QtCore import QRectF

    provider = _Provider()
    bench.set_provider(provider)
    bench.selection.set_group("s1")
    layout, pseudo = bench.layout_data()
    assert layout is not None and pseudo is not None
    rect = QRectF(-1.0, float(np.min(pseudo.elevation)) - 1, 60.0, 200.0)
    bench.section._on_box(rect)
    keys = bench.selection.keys()
    assert keys and all(k[0] == "trace" for k in keys)
    xs = [p for p, k in zip(pseudo.along, pseudo.keys, strict=True) if k in set(keys)]
    assert all(-1.0 <= x <= 59.0 for x in xs)
    bench.plan._on_box(QRectF(-5.0, -50.0, 10.0, 40.0))
    picked = bench.selection.keys()
    assert ("shot", "s1") in picked and ("shot", "s2") in picked


def test_plan_click_picks_the_group(bench: Any) -> None:
    bench.set_provider(_Provider())

    class _Spot:
        def __init__(self, index: int) -> None:
            self._index = index

        def data(self) -> int:
            return self._index

    index = synth.layout().points.ids.index("A-s3")
    bench.plan._on_clicked(None, [_Spot(index)])
    assert bench.selection.group() == "s3"
    assert bench.selection.keys() == (("shot", "s3"),)


def test_curves_and_spectrum_follow_the_group_and_channels(bench: Any, qtbot: Any) -> None:
    provider = _Provider()
    bench.set_provider(provider)
    bench.selection.set_group("s2")
    bench.set_channels(["ch1"])
    bench.show_tab("traces")
    assert provider.asked[-1] == ("s2", ("ch1",))
    traces = bench.current_traces()
    assert traces is not None and traces.channels == ("ch1",)
    windows = [bench.traces._window.itemData(i) for i in range(bench.traces._window.count())]
    assert "Off-time" in windows
    bench.show_tab("spectrum")
    metrics = bench.spectrum.metrics()
    assert len(metrics) == 1 and np.isfinite(metrics[0].line_db)
    assert bench.spectrum._table.rowCount() == 1
    spectrum = bench.spectrum.spectrum()
    assert spectrum is not None and spectrum.nyquist == pytest.approx(125.0)


def test_three_d_falls_back_offscreen_and_picks(bench: Any) -> None:
    bench.set_provider(_Provider())
    bench.selection.set_group("s1")
    bench.show_tab("layout", three_d=True)
    view = bench.view3d
    assert view.backend == "matplotlib" and "offscreen" in view.reason
    scene = view.scene()
    assert scene is not None and "pseudo" in scene.names()
    assert not view._vtk.isEnabled() and not view._measure.isEnabled()
    cloud = scene.layer("pseudo")
    view._picked("pseudo", 0)
    assert bench.selection.keys() == (cloud.keys[0],)
    view.set_camera("top")
    view._switches["show_pseudo"].setChecked(False)
    assert "pseudo" not in view.scene().names()


def test_three_d_options_are_remembered(bench: Any, memory_settings: dict[str, Any]) -> None:
    bench.set_provider(_Provider())
    bench.show_tab("layout", three_d=True)
    bench.view3d._exaggeration.setValue(3.0)
    assert any(key.endswith("exaggeration") and value == 3.0 for key, value in memory_settings.items())
    assert bench.view3d.scene().exaggeration == 3.0


def test_simple_3d_by_environment(qtbot: Any, monkeypatch: pytest.MonkeyPatch) -> None:
    from PyHydroGeophysX.qt_apps.widgets.survey.render3d import choose_backend

    monkeypatch.setenv("PHGX_SURVEY_3D", "simple")
    backend, reason = choose_backend()
    assert backend == "matplotlib" and "PHGX_SURVEY_3D" in reason


def test_report_figures_from_the_workbench(bench: Any, tmp_path: Path) -> None:
    bench.set_provider(_Provider())
    bench.selection.set_group("s1")
    bench.set_channels(["ch1", "ch2"])
    for key in ("plan", "section", "traces", "spectrum"):
        path = bench.export_figure(key, tmp_path / f"{key}.png")
        assert path is not None and path.stat().st_size > 1000


def test_shared_attribute_names_are_in_the_catalog_table() -> None:
    from PyHydroGeophysX.qt_apps.widgets.survey.common import ATTRIBUTE_TEXTS
    from PyHydroGeophysX.survey import attributes

    assert attributes.ALL == ATTRIBUTE_TEXTS


def test_views_build_in_chinese(qtbot: Any) -> None:
    from PySide6.QtWidgets import QApplication

    from PyHydroGeophysX.qt_apps import i18n
    from PyHydroGeophysX.qt_apps.widgets.survey import SurveyWorkbench

    app = QApplication.instance()
    i18n.install_translator(app, "zh_CN")
    try:
        workbench = SurveyWorkbench()
        qtbot.addWidget(workbench)
        workbench.set_provider(_Provider())
        assert workbench.tabs.tabText(0) == "布设图"
    finally:
        i18n.install_translator(app, "en")
