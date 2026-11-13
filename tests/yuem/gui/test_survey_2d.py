"""The 2-D survey plots: guarded mouse zoom, view history, plot styles, the split and the options panel."""

from __future__ import annotations

import json
from collections.abc import Iterator, Sequence
from dataclasses import replace
from typing import Any

import pytest

from PyHydroGeophysX.survey.layout import SurveyLayout
from PyHydroGeophysX.survey.pseudo import PseudoPoints
from PyHydroGeophysX.survey.traces import TraceSet

from ..survey import synth

pytest.importorskip("PySide6")
pytestmark = pytest.mark.gui


class _Provider:
    def survey_capabilities(self) -> frozenset[str]:
        return frozenset(("layout", "pseudo", "traces", "spectrum"))

    def survey_layout(self) -> SurveyLayout | None:
        return synth.layout()

    def survey_pseudo(self) -> PseudoPoints | None:
        return synth.pseudo()

    def survey_traces(self, group: str, channels: Sequence[str]) -> TraceSet | None:
        return synth.traces()


@pytest.fixture(autouse=True)
def memory_settings(monkeypatch: pytest.MonkeyPatch) -> Iterator[dict[str, Any]]:
    """The views' remembered choices in memory, never in the user's Studio settings."""
    from PyHydroGeophysX.qt_apps.widgets.survey import common

    store: dict[str, Any] = {}
    monkeypatch.setattr(
        common.Settings, "get", lambda self, name, default: store.get(self._prefix + name, default)
    )
    monkeypatch.setattr(
        common.Settings, "set", lambda self, name, value: store.__setitem__(self._prefix + name, value)
    )
    yield store


@pytest.fixture
def bench(qtbot: Any) -> Any:
    from PyHydroGeophysX.qt_apps.widgets.survey import SurveyWorkbench

    workbench = SurveyWorkbench()
    qtbot.addWidget(workbench)
    workbench.resize(1300, 820)
    workbench.show()
    qtbot.waitExposed(workbench)
    workbench.set_provider(_Provider())
    workbench.selection.set_group("s1")
    return workbench


class _Drag:
    """The parts of a pyqtgraph mouse drag event the view box reads."""

    def __init__(
        self, start: tuple[float, float], end: tuple[float, float], button: Any, finish: bool = True
    ) -> None:
        from PySide6.QtCore import QPointF

        self._start, self._end = QPointF(*start), QPointF(*end)
        self._button, self._finish = button, finish
        self.accepted = self.ignored = False

    def button(self) -> Any:
        return self._button

    def buttonDownPos(self, *_args: Any) -> Any:
        return self._start

    def pos(self) -> Any:
        return self._end

    def lastPos(self) -> Any:
        return self._end

    def isStart(self) -> bool:
        return False

    def isFinish(self) -> bool:
        return self._finish

    def accept(self) -> None:
        self.accepted = True

    def ignore(self) -> None:
        self.ignored = True


def _width(view: Any) -> float:
    (x0, x1), _y = view.viewRange()
    return float(x1 - x0)


def test_drag_right_zooms_drag_left_resets_short_drag_does_nothing(bench: Any) -> None:
    from PySide6.QtCore import Qt

    view = bench.plan._view
    assert view.mode() == "zoom"
    full = _width(view)
    box = view.boundingRect()
    left, top = box.left() + 0.3 * box.width(), box.top() + 0.3 * box.height()
    right, bottom = box.left() + 0.6 * box.width(), box.top() + 0.6 * box.height()
    view.mouseDragEvent(_Drag((left, top), (left + 3, top + 2), Qt.MouseButton.LeftButton))
    assert _width(view) == pytest.approx(full)
    view.mouseDragEvent(_Drag((left, top), (right, bottom), Qt.MouseButton.LeftButton))
    zoomed = _width(view)
    assert zoomed < 0.6 * full
    assert view.can_go_back()
    view.mouseDragEvent(_Drag((right, bottom), (left, top), Qt.MouseButton.LeftButton))
    assert _width(view) == pytest.approx(full, rel=0.05)
    view.back()
    assert _width(view) == pytest.approx(zoomed, rel=0.01)
    view.forward()
    assert _width(view) == pytest.approx(full, rel=0.05)


def test_right_drag_and_wheel_do_nothing_unless_asked(bench: Any) -> None:
    from PySide6.QtCore import Qt

    view = bench.plan._view
    full = _width(view)
    drag = _Drag((10, 10), (200, 200), Qt.MouseButton.RightButton)
    view.mouseDragEvent(drag)
    assert drag.ignored and _width(view) == pytest.approx(full)
    assert not view.wheel_zoom()
    bench.plan.toolbar.buttons["wheel"].setChecked(True)
    assert view.wheel_zoom()


def test_toolbar_modes_follow_the_studio_toolbar(bench: Any) -> None:
    import pyqtgraph as pg

    plan = bench.plan
    plan.toolbar.buttons["select"].setChecked(True)
    assert plan._view.mode() == "select" and plan._view.selecting()
    plan._view.setMouseMode(pg.ViewBox.PanMode)
    assert plan._view.mode() == "pan" and plan.toolbar.buttons["pan"].isChecked()
    assert not plan._view.selecting()
    plan._view.setMouseMode(pg.ViewBox.RectMode)
    assert plan.toolbar.buttons["zoom"].isChecked()


def test_zoom_buttons_and_full_view_keep_a_history(bench: Any) -> None:
    plan = bench.plan
    full = _width(plan._view)
    plan.toolbar.buttons["zoom_in"].click()
    assert _width(plan._view) < full
    assert plan.toolbar.buttons["back"].isEnabled()
    plan.toolbar.buttons["home"].click()
    assert _width(plan._view) == pytest.approx(full, rel=0.05)


def test_toolbar_fades_until_the_mouse_comes_near(bench: Any, memory_settings: dict[str, Any]) -> None:
    from PySide6.QtCore import QPoint

    from PyHydroGeophysX.qt_apps.widgets.survey.plot_tools import IDLE_OPACITY

    toolbar = bench.plan.toolbar
    assert not toolbar.pinned() and not toolbar.revealed()
    assert toolbar.graphicsEffect().opacity() == pytest.approx(IDLE_OPACITY)
    corner = toolbar.geometry().bottomRight()
    assert toolbar.is_near(corner + QPoint(10, 10))
    assert not toolbar.is_near(corner + QPoint(300, 200))
    toolbar.reveal(toolbar.is_near(corner + QPoint(10, 10)), animate=False)
    assert toolbar.revealed() and toolbar.graphicsEffect().opacity() == pytest.approx(1.0)
    toolbar.reveal(False, animate=False)
    assert toolbar.graphicsEffect().opacity() == pytest.approx(IDLE_OPACITY)
    toolbar.buttons["pin"].setChecked(True)
    toolbar.reveal(False, animate=False)
    assert toolbar.revealed() and toolbar.graphicsEffect().opacity() == pytest.approx(1.0)
    assert memory_settings["survey/plot_tools/pinned"] is True


def test_style_draws_symbols_and_is_remembered(bench: Any, memory_settings: dict[str, Any]) -> None:
    import pyqtgraph as pg

    plan = bench.plan
    style = plan.style()
    symbols = dict(style.symbols)
    symbols["A"] = replace(symbols["A"], symbol="s", size=19.0)
    plan.set_style(replace(style, symbols=symbols, grid_opacity=0.5, title="Line 4", frame=False))
    scatters = [i for i in plan._plot.getPlotItem().items if isinstance(i, pg.ScatterPlotItem)]
    assert any(i.opts.get("size") == 19.0 and i.opts.get("symbol") == "s" for i in scatters)
    assert not plan._plot.getPlotItem().getAxis("top").isVisible()
    stored = json.loads(memory_settings["survey/plan/style"])
    assert stored["symbols"]["A"]["size"] == 19.0 and stored["title"] == "Line 4"


def test_fixed_ranges_and_exaggeration(bench: Any) -> None:
    section = bench.section
    style = section.style()
    section.set_style(
        replace(
            style,
            x=replace(style.x, auto_range=False, minimum=0.0, maximum=50.0),
            aspect="exaggerated",
            exaggeration=2.0,
        )
    )
    (x0, x1), _y = section._view.viewRange()
    assert (x0, x1) == pytest.approx((0.0, 50.0), abs=1.0)
    px, py = section._view.viewPixelSize()
    assert py == pytest.approx(px / 2.0, rel=0.05)
    section.toolbar.buttons["zoom_out"].click()
    section.toolbar.buttons["home"].click()
    (x0, x1), _y = section._view.viewRange()
    assert (x0, x1) == pytest.approx((0.0, 50.0), abs=1.0)


def test_stored_style_survives_unknown_and_bad_fields() -> None:
    from PyHydroGeophysX.qt_apps.widgets.survey.plot_style import load_style, plan_default

    default = plan_default()
    assert load_style(default, "not json") == default
    style = load_style(
        default, json.dumps({"tick_size": 14, "bogus": 1, "grid_x": "yes", "x": {"major": 25}})
    )
    assert style.tick_size == 14 and style.grid_x is True and style.x.major == 25.0
    assert set(style.symbols) == set(default.symbols)


def test_plan_controls_share_the_switch_row(bench: Any) -> None:
    controls = bench.plan.controls
    assert controls.isVisible()
    assert controls.parentWidget() is not bench.plan
    bench.show_tab("layout", three_d=True)
    assert not controls.isVisible()
    bench.show_tab("layout", three_d=False)
    assert controls.isVisible()


def test_plots_hide_and_fill_but_never_both_hidden(bench: Any, memory_settings: dict[str, Any]) -> None:
    bench.show_plots("section")
    assert not bench.plan.isVisible() and bench.section.isVisible()
    assert not bench.plan.controls.isVisible()
    assert bench.section.toolbar.buttons["maximize"].isChecked()
    bench._shown["section"].setChecked(False)
    assert bench.shown_plots() == ("section",)
    bench.section.toolbar.buttons["maximize"].click()
    assert bench.shown_plots() == ("plan", "section")
    bench.plan.toolbar.buttons["maximize"].click()
    assert bench.shown_plots() == ("plan",)
    assert memory_settings["survey/workbench/show_section"] is False


def test_split_sizes_are_remembered(bench: Any, memory_settings: dict[str, Any]) -> None:
    bench.split.setSizes([200, 500])
    bench._remember_split()
    stored = [int(v) for v in memory_settings["survey/workbench/split"].split(",")]
    assert stored[0] < stored[1]


def test_options_panel_edits_the_view(bench: Any) -> None:
    from PySide6.QtWidgets import QSpinBox

    editor = bench.options2d.editors["plan"]
    opacity = next(box for box in editor.findChildren(QSpinBox) if box.suffix() == " %")
    opacity.setValue(55)
    assert bench.plan.style().grid_opacity == pytest.approx(0.55)
    editor.reset()
    assert bench.plan.style().grid_opacity == pytest.approx(0.2)
    assert set(bench.options2d.editors) == {"plan", "section"}
