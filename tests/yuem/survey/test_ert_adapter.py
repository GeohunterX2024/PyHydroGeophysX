"""ERT data as survey descriptions, and the ERT page's survey-layout tab."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pytest

from PyHydroGeophysX.survey import attributes
from PyHydroGeophysX.survey.adapters.ert import ERTSurvey, injection_name


def _line() -> ERTSurvey:
    x = np.arange(12) * 5.0
    elevation = 100.0 + np.sin(x / 10.0)
    rows = [(a, a + 3, a + 1, a + 2) for a in range(9)] + [(a, a + 6, a + 2, a + 4) for a in range(6)]
    a, b, m, n = (np.array(column) for column in zip(*rows, strict=True))
    values = {
        attributes.APPARENT_RESISTIVITY: np.linspace(50, 150, len(rows)),
        attributes.REJECTED: np.zeros(len(rows)),
    }
    return ERTSurvey(np.column_stack([x, elevation, np.zeros_like(x)]), a, b, m, n, values)


def test_pseudo_points_are_the_ert_pages_placement() -> None:
    from PyHydroGeophysX.data_processing import ert_io

    survey = _line()
    pseudo = survey.survey_pseudo()
    assert pseudo is not None and pseudo.convention == "pygimli"
    table = ert_io.pseudosection_points(
        survey.along(), survey.a, survey.b, survey.m, survey.n, np.ones(survey.a.size)
    )
    np.testing.assert_array_equal(pseudo.along, table[:, 0])
    np.testing.assert_array_equal(pseudo.depth, table[:, 1])
    np.testing.assert_allclose(pseudo.elevation, survey.terrain().at(pseudo.along) - pseudo.depth)
    assert pseudo.keys[0] == ("reading", 0) and pseudo.group[0] == injection_name(0, 3)


def test_layout_has_electrodes_and_injection_links() -> None:
    survey = _line()
    layout = survey.survey_layout()
    assert layout is not None and layout.points.size == 12
    np.testing.assert_allclose(layout.points.xyz[:, 2], survey.elevation())
    groups = dict(survey.injections())
    assert groups["A1-B4"] == 1 and len(groups) == 15
    mine = [k for k, g in zip(layout.links.kind, layout.links.group, strict=True) if g == "A1-B4"]
    assert mine == ["AB", "MN"]
    assert survey.survey_capabilities() == frozenset({"layout", "pseudo"})


def test_from_a_pygimli_container() -> None:
    ert = pytest.importorskip("pygimli.physics.ert")
    data = ert.createData(elecs=np.linspace(0, 47, 48), schemeName="dd")
    data["rhoa"] = np.full(data.size(), 100.0)
    survey = ERTSurvey.from_container(data)
    assert survey.two_d and survey.sensors.shape == (48, 3)
    pseudo = survey.survey_pseudo()
    assert pseudo is not None and pseudo.size == data.size()
    assert np.all(pseudo.attrs[attributes.APPARENT_RESISTIVITY] == 100.0)


@pytest.mark.gui
def test_the_ert_page_has_a_survey_layout_tab(
    qtbot: Any, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    pytest.importorskip("PySide6")
    ert = pytest.importorskip("pygimli.physics.ert")
    from PyHydroGeophysX.qt_apps.modules import build_module
    from PyHydroGeophysX.qt_apps.state import StudioState

    monkeypatch.setenv("PHGX_PROJECT_DIR", str(tmp_path / "project"))
    page = build_module("ert", StudioState.from_context(None), lambda *a, **k: None)
    qtbot.addWidget(page)
    data = ert.createData(elecs=np.linspace(0, 23, 24), schemeName="wa")
    page._ert_data = data
    page.show()
    page._tabs.setCurrentWidget(page._survey_tab)
    tab = page._survey_tab
    qtbot.waitUntil(lambda: tab.injections.count() > 0)
    tab.injections.setCurrentRow(0)
    assert tab.workbench.selection.group() == tab.provider.injections()[0][0]
    assert not page._controls.isVisible()
    page.stop_workers(wait_ms=2000)
