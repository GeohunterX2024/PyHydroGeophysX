"""Several groups drawn together: curves, spectra, the plan and section marks, and the report figures."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
from typing import Any

import numpy as np
import pytest

from PyHydroGeophysX.survey.series import encode
from PyHydroGeophysX.survey.traces import TraceCollection, TraceSet, Window

from ..survey import synth

pytest.importorskip("PySide6")
pytestmark = pytest.mark.gui


@pytest.fixture(autouse=True)
def memory_settings(monkeypatch: pytest.MonkeyPatch) -> Iterator[dict[str, Any]]:
    """Remembered choices stay in memory, never in the user's Studio settings."""
    from PyHydroGeophysX.qt_apps.widgets.survey import common

    store: dict[str, Any] = {}
    monkeypatch.setattr(
        common.Settings, "get", lambda self, name, default: store.get(self._prefix + name, default)
    )
    monkeypatch.setattr(
        common.Settings, "set", lambda self, name, value: store.__setitem__(self._prefix + name, value)
    )
    yield store


def _set(group: str, n_channels: int) -> TraceSet:
    t = np.linspace(0.0, 1.0, 64)
    values = np.vstack([np.sin(2 * np.pi * (index + 1) * t) for index in range(n_channels)])
    names = tuple(f"ch{index}" for index in range(n_channels))
    return TraceSet(
        t,
        values,
        names,
        labels=names,
        keys=tuple(("trace", group, name) for name in names),
        group=group,
        origin=0.25,
        windows=(Window("On", 0.1, 0.4, "on"),),
        title=group,
    )


class _Provider:
    def __init__(self, channels: int = 2) -> None:
        self.channels = channels
        self.capabilities = frozenset(("layout", "pseudo", "traces", "spectrum", "multi_traces"))

    def survey_capabilities(self) -> frozenset[str]:
        return self.capabilities

    def survey_layout(self) -> Any:
        return synth.layout()

    def survey_pseudo(self) -> Any:
        return synth.pseudo()

    def survey_traces(self, group: str, channels: Any) -> TraceSet:
        return _set(group, self.channels)

    def survey_trace_sets(self, groups: Any, channels: Any) -> TraceCollection:
        return TraceCollection(
            tuple(_set(str(group), self.channels) for group in groups), focus=str(groups[0])
        )


@pytest.fixture
def bench(qtbot: Any) -> Any:
    from PyHydroGeophysX.qt_apps.widgets.survey import SurveyWorkbench

    workbench = SurveyWorkbench()
    qtbot.addWidget(workbench)
    workbench.resize(1200, 800)
    workbench.show()
    return workbench


def test_two_groups_draw_and_the_limit_is_reported(bench: Any, qtbot: Any) -> None:
    hits: list[tuple[int, int]] = []
    bench.limitReached.connect(lambda have, drawn: hits.append((have, drawn)))
    bench.set_provider(_Provider(channels=20))
    bench.selection.set_group("s1")
    bench.traces._limit.setValue(32)
    bench.set_groups(("s1", "s2"))
    bench.show_tab("traces")
    collection = bench.current_collection()
    assert collection is not None and collection.size == 40
    assert hits == [(40, 32)]
    assert "Showing 32 of 40" in bench.traces._info.text()
    assert bench.traces._time_mode.isVisible()
    assert not bench.traces._draw.isEnabled()
    bench.traces._time_mode.setCurrentIndex(bench.traces._time_mode.findData("relative"))
    bench.traces._normalize.setChecked(True)
    assert bench.traces._draw.isEnabled()
    styles = list(encode(collection))
    bench.traces._on_curve(styles[3])
    assert bench.traces._picked == styles[3].key


def test_the_spectrum_table_lists_every_group_and_a_row_picks(bench: Any) -> None:
    picked: list[tuple[str, object]] = []
    bench.spectrum.curvePicked.connect(lambda group, key: picked.append((group, key)))
    bench.set_provider(_Provider())
    bench.selection.set_group("s1")
    bench.set_groups(("s1", "s2"))
    bench.show_tab("spectrum")
    table = bench.spectrum._table
    assert table.columnCount() == 6
    assert table.rowCount() == 4
    assert {table.item(row, 0).text() for row in range(table.rowCount())} == {"s1", "s2"}
    bench.spectrum._on_row(table.item(0, 0))
    assert picked and picked[0][0] in {"s1", "s2"}


def test_other_groups_are_marked_and_the_figure_exports(bench: Any, tmp_path: Path) -> None:
    bench.set_provider(_Provider())
    bench.selection.set_group("s1")
    bench.set_groups(("s1", "s2"))
    bench.show_tab("layout")
    bench.selection.set_display_keys([("trace", "s2", 0, 1)])
    assert bench.section._shown.opts["size"] == 8
    path = bench.export_figure("traces", tmp_path / "curves.png")
    assert path is not None and path.stat().st_size > 1000
    path = bench.export_figure("spectrum", tmp_path / "spectra.png")
    assert path is not None and path.stat().st_size > 1000
