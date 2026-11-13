"""Several groups drawn together: curves, spectra, the plan and section marks, and the report figures."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
from typing import Any

import numpy as np
import pytest

from PyHydroGeophysX.survey.series import encode, normalized
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


class _OldProvider:
    """A provider written before several groups could be shown: no multi_traces, no origin."""

    def __init__(self, channels: int = 2) -> None:
        self.channels = channels
        self.capabilities = frozenset(("layout", "pseudo", "traces", "spectrum"))
        self.asked: list[tuple[str, object]] = []

    def survey_capabilities(self) -> frozenset[str]:
        return self.capabilities

    def survey_layout(self) -> Any:
        return synth.layout()

    def survey_pseudo(self) -> Any:
        return synth.pseudo()

    def survey_traces(self, group: str, channels: Any) -> TraceSet:
        self.asked.append(("traces", group))
        plain = _set(group, self.channels)
        return TraceSet(plain.t, plain.values, plain.channels, keys=plain.keys, windows=plain.windows)


class _Provider(_OldProvider):
    def __init__(self, channels: int = 2) -> None:
        super().__init__(channels)
        self.capabilities = self.capabilities | {"multi_traces"}

    def survey_traces(self, group: str, channels: Any) -> TraceSet:
        self.asked.append(("traces", group))
        return _set(group, self.channels)

    def survey_trace_sets(self, groups: Any, channels: Any) -> TraceCollection:
        self.asked.append(("sets", tuple(groups)))
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


def test_normalising_has_its_own_window_and_the_band_takes_every_curve(bench: Any) -> None:
    from PyHydroGeophysX.qt_apps.widgets.survey.trace_view import style_count

    bench.set_provider(_Provider(channels=20))
    bench.selection.set_group("s1")
    bench.traces._limit.setValue(32)
    bench.set_groups(("s1", "s2"))
    bench.show_tab("traces")
    view = bench.traces
    assert view._norm_window.currentData() == "On" and not view._norm_window.isEnabled()
    shown_window = view._window.currentData()
    view._normalize.setChecked(True)
    assert view._norm_window.isEnabled()
    assert view._window.currentData() == shown_window
    focus = bench.current_traces()
    inside = (focus.t >= 0.1) & (focus.t <= 0.4)
    np.testing.assert_allclose(view._values(focus), normalized(focus.values, inside))
    view._time_mode.setCurrentIndex(view._time_mode.findData("relative"))
    view._draw.setCurrentIndex(view._draw.findData("band"))
    labels = [label.text for _sample, label in view._legend.items]
    assert labels == [style_count(40)]
    assert "32" not in view._info.text().split("    ")[-1]


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
    misses = bench.spectrum._cache.misses
    bench.set_groups(("s2", "s1"))
    bench.spectrum._reference.toggle()
    assert bench.spectrum._cache.misses == misses
    assert table.rowCount() == 4


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


def test_the_plan_rings_the_other_shots_on_screen(bench: Any) -> None:
    bench.set_provider(_Provider())
    bench.selection.set_group("s1")
    bench.show_tab("layout")
    assert bench.plan._shown is None
    bench.set_groups(("s1", "s2"))
    ring = bench.plan._shown
    assert ring is not None and ring in bench.plan._plot.getPlotItem().items
    assert ring.opts["size"] == bench.plan._style.symbol("shown").size
    layout = synth.layout()
    a_of_s2 = [
        index
        for index, (group, role) in enumerate(zip(layout.points.group, layout.points.role, strict=True))
        if group == "s2" and role == "A"
    ]
    x, y = ring.getData()
    np.testing.assert_allclose(x, layout.points.xyz[a_of_s2, 0])
    np.testing.assert_allclose(y, layout.points.xyz[a_of_s2, 1])
    bench.set_groups(("s1",))
    assert bench.plan._shown is None


def test_many_curves_switch_to_a_compact_legend(bench: Any) -> None:
    from PySide6.QtCore import QCoreApplication

    bench.set_provider(_Provider(channels=6))
    bench.selection.set_group("s1")
    bench.set_groups(("s1", "s2"))
    bench.show_tab("traces")
    assert len(bench.traces._legend.items) == 12
    bench.set_provider(_Provider(channels=20))
    bench.selection.set_group("s1")
    bench.set_groups(("s1", "s2"))
    bench.show_tab("traces")
    labels = [label.text for _sample, label in bench.traces._legend.items]
    assert len(labels) == 9
    assert labels[-1] == QCoreApplication.translate("PHGX", "{0} curves").format(40)


def test_a_clicked_curve_is_announced_and_drawn_thicker(bench: Any) -> None:
    picked: list[tuple[str, object]] = []
    bench.traces.curvePicked.connect(lambda group, key: picked.append((group, key)))
    bench.set_provider(_Provider())
    bench.selection.set_group("s1")
    bench.set_groups(("s1", "s2"))
    bench.show_tab("traces")
    curves = [item for item in bench.traces._plot.getPlotItem().listDataItems() if item.curve.clickable]
    assert len(curves) == 4
    curves[2].sigClicked.emit(curves[2], None)
    assert picked == [("s2", ("trace", "s2", "ch0"))]
    assert "s2 · ch0" in bench.traces._info.text()
    widths = [
        item.opts["pen"].widthF()
        for item in bench.traces._plot.getPlotItem().listDataItems()
        if item.curve.clickable
    ]
    assert widths.count(max(widths)) == 1 and widths[2] == max(widths)


def test_a_provider_without_multi_traces_keeps_the_one_group_path(bench: Any) -> None:
    hits: list[tuple[int, int]] = []
    bench.limitReached.connect(lambda have, drawn: hits.append((have, drawn)))
    provider = _OldProvider()
    bench.set_provider(provider)
    bench.selection.set_group("s1")
    bench.set_groups(("s1", "s2"))
    bench.show_tab("traces")
    assert provider.asked and all(asked == ("traces", "s1") for asked in provider.asked)
    collection = bench.current_collection()
    assert collection is not None and len(collection.sets) == 1 and collection.size == 2
    traces = bench.current_traces()
    assert traces is not None and traces.channels == ("ch0", "ch1")
    assert not bench.traces._time_mode.isVisible()
    assert not bench.traces._draw.isEnabled()
    bench.show_tab("spectrum")
    assert bench.spectrum._table.rowCount() == 2
    assert hits == []


def test_changes_in_a_batch_are_fetched_once(bench: Any) -> None:
    provider = _Provider()
    bench.set_provider(provider)
    bench.selection.set_group("s1")
    bench.show_tab("traces")
    provider.asked.clear()
    with bench.batch():
        bench.selection.set_group("s2")
        bench.set_channels(["ch1"])
        bench.set_groups(("s2", "s3"))
        bench.selection.set_display_keys([("trace", "s3", "ch1")])
        assert provider.asked == []
    assert provider.asked == [("sets", ("s2", "s3"))]
    collection = bench.current_collection()
    assert collection is not None and collection.focus == "s2"


def test_the_focused_group_leads_wherever_the_provider_lists_it(bench: Any) -> None:
    bench.set_provider(_Provider())
    bench.selection.set_group("s3")
    bench.set_groups(("s1", "s2", "s3"))
    bench.show_tab("traces")
    collection = bench.current_collection()
    assert collection is not None and collection.focus == "s3"
    traces = bench.current_traces()
    assert traces is not None and traces.group == "s3"
    assert bench.traces._traces is traces
    bench.show_tab("spectrum")
    assert {metric.channel for metric in bench.spectrum.metrics()} == {"ch0", "ch1"}
    assert bench.spectrum._collection.focus == "s3"


def test_one_group_uses_the_old_call_even_when_the_provider_offers_more(bench: Any) -> None:
    provider = _Provider()
    bench.set_provider(provider)
    bench.selection.set_group("s1")
    bench.show_tab("traces")
    assert provider.asked and all(kind == "traces" for kind, _ in provider.asked)
    bench.set_groups(("s1", "s2"))
    assert provider.asked[-1] == ("sets", ("s1", "s2"))
