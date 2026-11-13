"""The survey workbench: layout (plan and section, or 3-D), curves and spectrum, in tabs.

A page keeps its own lists (shots, channels, sites) and its QC bar, and hands
the workbench a :class:`~PyHydroGeophysX.survey.provider.SurveyProvider`. The
workbench shows the tabs the provider has data for, draws only the tab on
screen (the others when they are opened), and shares one
:class:`~.selection.SurveySelection` between its views and the page.

In 2-D the plan's colouring choices share the row of the 2-D/3-D switch, the
plan and section split the height (the divider is dragged, either plot can be
hidden or fill the space) and the 2-D options fold out at the right.
"""

from __future__ import annotations

import logging
from collections.abc import Iterator, Sequence
from contextlib import contextmanager
from dataclasses import replace
from pathlib import Path
from typing import Any

from PySide6.QtCore import QCoreApplication, Qt, Signal
from PySide6.QtWidgets import (
    QButtonGroup,
    QFileDialog,
    QHBoxLayout,
    QMenu,
    QPushButton,
    QSplitter,
    QStackedWidget,
    QTabWidget,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from PyHydroGeophysX.qt_apps import i18n, theme
from PyHydroGeophysX.qt_apps.widgets.survey.common import Settings
from PyHydroGeophysX.qt_apps.widgets.survey.plan_view import SurveyPlanView
from PyHydroGeophysX.qt_apps.widgets.survey.plot_style import (
    PLAN_LINE_NAMES,
    PLAN_SYMBOL_NAMES,
    SECTION_LINE_NAMES,
    SECTION_SYMBOL_NAMES,
    plan_default,
    section_default,
)
from PyHydroGeophysX.qt_apps.widgets.survey.section_view import SurveySectionView
from PyHydroGeophysX.qt_apps.widgets.survey.selection import SurveySelection
from PyHydroGeophysX.qt_apps.widgets.survey.spectrum_view import SurveySpectrumView
from PyHydroGeophysX.qt_apps.widgets.survey.style_panel import PlotStyleEditor, TwoDOptions
from PyHydroGeophysX.qt_apps.widgets.survey.trace_view import SurveyTraceView
from PyHydroGeophysX.qt_apps.widgets.survey.view3d import Survey3DView
from PyHydroGeophysX.survey.layout import SurveyLayout
from PyHydroGeophysX.survey.provider import MultiGroupProvider, SurveyProvider
from PyHydroGeophysX.survey.pseudo import PseudoPoints
from PyHydroGeophysX.survey.traces import TraceCollection, TraceSet

_logger = logging.getLogger(__name__)

#: Tab keys, in order.
TABS = ("layout", "traces", "spectrum")
#: The 2-D plots, in their order in the split.
PLOTS = ("plan", "section")


class SurveyWorkbench(QWidget):
    """Layout, curve and spectrum tabs over one provider and one selection."""

    #: The tab on screen or the 2-D/3-D choice changed (a page refreshes its toolbar on it).
    viewChanged = Signal()
    #: More curves than the curve view draws: ``(available, drawn)``.
    limitReached = Signal(int, int)

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        selection: SurveySelection | None = None,
        colormaps: Any = None,
        settings_key: str = "workbench",
    ) -> None:
        super().__init__(parent)
        self.selection = selection or SurveySelection(self)
        self._settings = Settings(settings_key)
        self._provider: SurveyProvider | None = None
        self._channels: tuple[str, ...] = ()
        self._layout: SurveyLayout | None = None
        self._pseudo: PseudoPoints | None = None
        self._traces: TraceSet | None = None
        self._collection: TraceCollection | None = None
        self._dirty = set(TABS)
        self._batch = 0
        self.plan = SurveyPlanView(self.selection, colormaps=colormaps, controls_outside=True)
        self.section = SurveySectionView(self.selection, colormaps=colormaps)
        self.view3d = Survey3DView(self.selection, colormaps=colormaps, settings_key=f"{settings_key}/3d")
        self.traces = SurveyTraceView()
        self.spectrum = SurveySpectrumView()

        self.split = QSplitter(Qt.Orientation.Vertical)
        self.split.setObjectName("surveySplit")
        self.split.setStyleSheet(
            "QSplitter#surveySplit::handle { background: rgba(100, 116, 139, 70); margin: 1px 40px;"
            " border-radius: 2px; }"
            "QSplitter#surveySplit::handle:hover { background: rgba(37, 99, 235, 150); }"
        )
        self.split.setHandleWidth(7)
        self.split.setChildrenCollapsible(False)
        self.split.addWidget(self.plan)
        self.split.addWidget(self.section)
        self.split.setStretchFactor(0, 3)
        self.split.setStretchFactor(1, 2)
        self.split.splitterMoved.connect(lambda _pos, _index: self._remember_split())
        self.options2d = TwoDOptions(f"{settings_key}/2d")
        for key, view, default, symbols, lines, title in (
            (
                "plan",
                self.plan,
                plan_default,
                PLAN_SYMBOL_NAMES,
                PLAN_LINE_NAMES,
                QCoreApplication.translate("PHGX", "Plan"),
            ),
            (
                "section",
                self.section,
                section_default,
                SECTION_SYMBOL_NAMES,
                SECTION_LINE_NAMES,
                QCoreApplication.translate("PHGX", "Section"),
            ),
        ):
            editor = PlotStyleEditor(
                view.style(),
                default,
                symbol_names=symbols,
                line_names=lines,
                view_range=view.view_range,
                point_labels=key == "plan",
            )
            editor.styleChanged.connect(view.set_style)
            self.options2d.add_editor(key, title, editor)
            view.toolbar.maximizeToggled.connect(lambda on, k=key: self._on_maximize(k, on))
        two_d = QWidget()
        two_d_row = QHBoxLayout(two_d)
        two_d_row.setContentsMargins(0, 0, 0, 0)
        two_d_row.addWidget(self.split, 1)
        two_d_row.addWidget(self.options2d)
        self._stack = QStackedWidget()
        self._stack.addWidget(two_d)
        self._stack.addWidget(self.view3d)
        self._mode = QButtonGroup(self)
        switch = QHBoxLayout()
        switch.setContentsMargins(0, 0, 0, 0)
        switch.setSpacing(0)
        for index, (text, tip) in enumerate(
            (
                (
                    QCoreApplication.translate("PHGX", "2D"),
                    QCoreApplication.translate("PHGX", "Plan and section"),
                ),
                (
                    QCoreApplication.translate("PHGX", "3D"),
                    QCoreApplication.translate("PHGX", "Three-dimensional view"),
                ),
            )
        ):
            button = QPushButton(text)  # i18n: as written
            button.setCheckable(True)
            button.setToolTip(tip)  # i18n: as written
            button.setProperty("segment", "first" if index == 0 else "last")
            self._mode.addButton(button, index)
            switch.addWidget(button, 0, Qt.AlignmentFlag.AlignTop)
        switch.addSpacing(10)
        switch.addWidget(self.plan.controls, 1)
        self._shown: dict[str, QToolButton] = {}
        toggles = QWidget()
        toggle_row = QHBoxLayout(toggles)
        toggle_row.setContentsMargins(6, 0, 0, 0)
        toggle_row.setSpacing(2)
        for key, icon, text, tip in (
            (
                "plan",
                "fa5s.map",
                QCoreApplication.translate("PHGX", "Plan"),
                QCoreApplication.translate("PHGX", "Show or hide the plan"),
            ),
            (
                "section",
                "mdi.chart-scatter-plot",
                QCoreApplication.translate("PHGX", "Section"),
                QCoreApplication.translate("PHGX", "Show or hide the section"),
            ),
        ):
            toggle = QToolButton()
            toggle.setCheckable(True)
            toggle.setIcon(theme.icon(icon))
            toggle.setText(text)  # i18n: as written
            toggle.setToolTip(tip)  # i18n: as written
            toggle.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
            toggle.setChecked(self._settings.get(f"show_{key}", True))
            toggle.toggled.connect(lambda _on, k=key: self._on_shown(k))
            toggle_row.addWidget(toggle)
            self._shown[key] = toggle
        self._toggles = toggles
        switch.addWidget(toggles, 0, Qt.AlignmentFlag.AlignTop)
        self._mode.idToggled.connect(self._on_mode)
        layout_page = QWidget()
        column = QVBoxLayout(layout_page)
        column.setContentsMargins(0, 0, 0, 0)
        column.addLayout(switch)
        column.addWidget(self._stack, 1)

        self.tabs = QTabWidget()
        self.tabs.setObjectName("surveyWorkbenchTabs")
        for page, icon, text in (
            (layout_page, "fa5s.map-marked-alt", QCoreApplication.translate("PHGX", "Layout")),
            (self.traces, "fa5s.wave-square", QCoreApplication.translate("PHGX", "Curves")),
            (self.spectrum, "fa5s.chart-area", QCoreApplication.translate("PHGX", "Spectrum")),
        ):
            self.tabs.addTab(page, theme.icon(icon), text)  # i18n: as written
        self.tabs.currentChanged.connect(self._on_tab)
        export = QToolButton()
        export.setText(QCoreApplication.translate("PHGX", "Export figure"))
        export.setIcon(theme.icon("fa5s.file-export"))
        export.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        export.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        menu = QMenu(export)  # i18n: as written
        for key, text in (
            ("plan", QCoreApplication.translate("PHGX", "Plan figure…")),
            ("section", QCoreApplication.translate("PHGX", "Section figure…")),
            ("traces", QCoreApplication.translate("PHGX", "Curve figure…")),
            ("spectrum", QCoreApplication.translate("PHGX", "Spectrum figure…")),
        ):
            menu.addAction(text, lambda k=key: self.export_figure(k))
        export.setMenu(menu)
        self.tabs.setCornerWidget(export, Qt.Corner.TopRightCorner)
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.addWidget(self.tabs)
        self.selection.groupChanged.connect(self._on_group)
        self._restore_split()
        self._apply_shown()
        self._mode.button(int(self._settings.get("mode", 0))).setChecked(True)
        self._sync_mode_row()

    # -- what the page sets -------------------------------------------------
    def set_provider(self, provider: SurveyProvider | None) -> None:
        self._provider = provider
        self.refresh()

    def set_channels(self, channels: Sequence[str]) -> None:
        """The channels of the current group whose curves and spectra are shown."""
        channels = tuple(channels)
        if channels != self._channels:
            self._channels = channels
            self._dirty.update(("traces", "spectrum"))
            self._refresh_visible()

    def refresh_traces(self) -> None:
        """Ask for the current group's curves again (the page chose another recording of it)."""
        self._dirty.update(("traces", "spectrum"))
        self._refresh_visible()

    def refresh(self) -> None:
        """Ask the provider again (after a new line, version or QC decision)."""
        provider = self._provider
        capabilities = provider.survey_capabilities() if provider is not None else frozenset()
        self._layout = provider.survey_layout() if provider is not None and "layout" in capabilities else None
        self._pseudo = provider.survey_pseudo() if provider is not None and "pseudo" in capabilities else None
        self.tabs.setTabVisible(0, "layout" in capabilities or provider is None)
        self.tabs.setTabVisible(1, "traces" in capabilities)
        self.tabs.setTabVisible(2, "spectrum" in capabilities)
        self._dirty = set(TABS)
        self._refresh_visible()

    @contextmanager
    def batch(self) -> Iterator[None]:
        """Several changes (group, groups, channels, display keys) redrawn once, when the block ends."""
        self._batch += 1
        try:
            yield
        finally:
            self._batch -= 1
            if self._batch == 0:
                self._refresh_visible()

    def show_tab(self, key: str, *, three_d: bool | None = None) -> None:
        """Bring tab ``key`` (``layout``, ``traces``, ``spectrum``) forward; optionally choose 2-D or 3-D."""
        self.tabs.setCurrentIndex(TABS.index(key))
        if three_d is not None:
            self._mode.button(1 if three_d else 0).setChecked(True)

    def current_tab(self) -> str:
        return TABS[self.tabs.currentIndex()]

    def is_3d(self) -> bool:
        return self._stack.currentIndex() == 1

    def layout_data(self) -> tuple[SurveyLayout | None, PseudoPoints | None]:
        return self._layout, self._pseudo

    def set_groups(self, groups: Sequence[str]) -> None:
        """Draw these groups together (the focused group stays whatever the page last picked)."""
        self.selection.set_groups(groups)
        self._dirty.update(("traces", "spectrum"))
        self._refresh_visible()

    def current_traces(self) -> TraceSet | None:
        return self._traces

    def current_collection(self) -> TraceCollection | None:
        return self._collection

    # -- drawing ------------------------------------------------------------
    def _refresh_visible(self) -> None:
        tab = self.current_tab()
        if self._batch or tab not in self._dirty:
            return
        self._dirty.discard(tab)
        if tab == "layout":
            if self.is_3d():
                self.view3d.set_data(self._layout, self._pseudo)
            else:
                self.plan.set_layout(self._layout)
                self.section.set_data(self._layout, self._pseudo)
            return
        self._collection = self._fetch_traces()
        self._traces = None if self._collection is None else self._collection.focus_set()
        shown = self._collection if self._collection is not None else self._traces
        if tab == "traces":
            self.traces.set_traces(shown)
        else:
            self.spectrum.set_traces(shown)

    def _fetch_traces(self) -> TraceCollection | None:
        provider = self._provider
        groups = self.selection.groups()
        if provider is None or not groups or "traces" not in provider.survey_capabilities():
            return None
        collection: TraceCollection | None
        if (
            len(groups) > 1
            and "multi_traces" in provider.survey_capabilities()
            and isinstance(provider, MultiGroupProvider)
        ):
            collection = provider.survey_trace_sets(groups, self._channels)
            focus = self.selection.group()
            if (
                collection is not None
                and focus != collection.focus
                and any(item.group == focus for item in collection.sets)
            ):
                collection = replace(collection, focus=focus)
        else:
            one = provider.survey_traces(groups[0], self._channels)
            collection = TraceCollection.single(one) if one is not None else None
        if collection is not None and collection.size > self.traces.curve_limit():
            self.limitReached.emit(collection.size, self.traces.curve_limit())
        return collection

    def _on_group(self, _group: str) -> None:
        self._dirty.update(("traces", "spectrum"))
        if self.is_3d():
            self._dirty.add("layout")
        self._refresh_visible()

    def _on_tab(self, _index: int) -> None:
        self._refresh_visible()
        self.viewChanged.emit()

    def _on_mode(self, index: int, checked: bool) -> None:
        if not checked:
            return
        self._stack.setCurrentIndex(index)
        self._settings.set("mode", index)
        self._sync_mode_row()
        self._dirty.add("layout")
        self._refresh_visible()
        self.viewChanged.emit()

    def _sync_mode_row(self) -> None:
        two_d = self._stack.currentIndex() == 0
        self.plan.controls.setVisible(two_d and self._shown["plan"].isChecked())
        self._toggles.setVisible(two_d)

    # -- the 2-D split --------------------------------------------------------
    def shown_plots(self) -> tuple[str, ...]:
        """The 2-D plots on screen (``plan``, ``section``)."""
        return tuple(key for key in PLOTS if self._shown[key].isChecked())

    def show_plots(self, *keys: str) -> None:
        """Show only the 2-D plots ``keys`` (at least one)."""
        wanted = [key for key in keys if key in PLOTS] or list(PLOTS)
        for key in PLOTS:
            toggle = self._shown[key]
            toggle.blockSignals(True)
            toggle.setChecked(key in wanted)
            toggle.blockSignals(False)
        self._apply_shown()

    def _on_shown(self, key: str) -> None:
        if not self.shown_plots():
            toggle = self._shown[key]
            toggle.blockSignals(True)
            toggle.setChecked(True)
            toggle.blockSignals(False)
        self._apply_shown()

    def _apply_shown(self) -> None:
        shown = self.shown_plots()
        for key, view in (("plan", self.plan), ("section", self.section)):
            on = key in shown
            view.setVisible(on)
            view.toolbar.set_maximized(on and len(shown) == 1)
            self._settings.set(f"show_{key}", on)
        self._sync_mode_row()
        self.options2d.show_editor(shown[0] if len(shown) == 1 else self.options2d_key())

    def options2d_key(self) -> str:
        index = self.options2d.tabs.currentIndex()
        return PLOTS[index] if 0 <= index < len(PLOTS) else "plan"

    def _on_maximize(self, key: str, on: bool) -> None:
        if on:
            self.show_plots(key)
        else:
            self.show_plots(*PLOTS)

    def _remember_split(self) -> None:
        sizes = self.split.sizes()
        if all(size > 0 for size in sizes):
            self._settings.set("split", ",".join(str(size) for size in sizes))

    def _restore_split(self) -> None:
        stored = str(self._settings.get("split", "") or "")
        try:
            sizes = [int(part) for part in stored.split(",")] if stored else []
        except ValueError:
            sizes = []
        if len(sizes) == len(PLOTS) and all(size > 0 for size in sizes):
            self.split.setSizes(sizes)

    # -- report figures -----------------------------------------------------
    def export_figure(self, key: str, path: str | Path | None = None) -> Path | None:
        """Save a report figure of ``key`` (``plan``, ``section``, ``traces``, ``spectrum``)."""
        from PyHydroGeophysX.visualization.styles import save_publication
        from PyHydroGeophysX.visualization.styles import survey as figures

        language = "zh" if i18n.resolve(i18n.chosen_language()).startswith("zh") else "en"
        layout, pseudo, group = self._layout, self._pseudo, self.selection.group()
        figure: Any = None
        if key == "plan" and layout is not None:
            figure = figures.survey_plan_figure(layout, group=group, language=language, title=layout.title)
        elif key == "section" and layout is not None:
            figure = figures.survey_section_figure(
                layout,
                pseudo,
                colour_by=self.section.attribute(),
                log_scale=self.section.log_scale(),
                language=language,
            )
        elif key == "traces":
            collection = self._collection or self._fetch_traces()
            if collection is not None:
                window = self.traces.window()
                figure = figures.trace_figure(
                    collection, window=window.name if window else "", language=language
                )
        elif key == "spectrum":
            collection = self._collection or self._fetch_traces()
            if collection is not None:
                figure = figures.spectrum_figure(
                    collection, line_frequency=self.spectrum.line_frequency(), language=language
                )
        if figure is None:
            return None
        if path is None:
            chosen, _ = QFileDialog.getSaveFileName(
                self,
                QCoreApplication.translate("PHGX", "Save figure"),
                f"{key}.pdf",
                QCoreApplication.translate("PHGX", "PDF (*.pdf);;PNG (*.png);;SVG (*.svg)"),
            )
            if not chosen:
                return None
            path = chosen
        try:
            return save_publication(figure, path)
        except (OSError, ValueError) as exc:
            _logger.warning("SurveyWorkbench.export_figure: %s", exc)
            return None


__all__ = ["TABS", "SurveyWorkbench"]
