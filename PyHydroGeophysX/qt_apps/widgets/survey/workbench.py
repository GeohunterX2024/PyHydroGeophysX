"""The survey workbench: layout (plan and section, or 3-D), curves and spectrum, in tabs.

A page keeps its own lists (shots, channels, sites) and its QC bar, and hands
the workbench a :class:`~PyHydroGeophysX.survey.provider.SurveyProvider`. The
workbench shows the tabs the provider has data for, draws only the tab on
screen (the others when they are opened), and shares one
:class:`~.selection.SurveySelection` between its views and the page.
"""

from __future__ import annotations

import logging
from collections.abc import Sequence
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
from PyHydroGeophysX.qt_apps.widgets.survey.section_view import SurveySectionView
from PyHydroGeophysX.qt_apps.widgets.survey.selection import SurveySelection
from PyHydroGeophysX.qt_apps.widgets.survey.spectrum_view import SurveySpectrumView
from PyHydroGeophysX.qt_apps.widgets.survey.trace_view import SurveyTraceView
from PyHydroGeophysX.qt_apps.widgets.survey.view3d import Survey3DView
from PyHydroGeophysX.survey.layout import SurveyLayout
from PyHydroGeophysX.survey.provider import SurveyProvider
from PyHydroGeophysX.survey.pseudo import PseudoPoints
from PyHydroGeophysX.survey.traces import TraceSet

_logger = logging.getLogger(__name__)

#: Tab keys, in order.
TABS = ("layout", "traces", "spectrum")


class SurveyWorkbench(QWidget):
    """Layout, curve and spectrum tabs over one provider and one selection."""

    #: The tab on screen or the 2-D/3-D choice changed (a page refreshes its toolbar on it).
    viewChanged = Signal()

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
        self._dirty = set(TABS)
        self.plan = SurveyPlanView(self.selection, colormaps=colormaps)
        self.section = SurveySectionView(self.selection, colormaps=colormaps)
        self.view3d = Survey3DView(self.selection, colormaps=colormaps, settings_key=f"{settings_key}/3d")
        self.traces = SurveyTraceView()
        self.spectrum = SurveySpectrumView()

        split = QSplitter(Qt.Orientation.Vertical)
        split.addWidget(self.plan)
        split.addWidget(self.section)
        split.setStretchFactor(0, 3)
        split.setStretchFactor(1, 2)
        self._stack = QStackedWidget()
        self._stack.addWidget(split)
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
            switch.addWidget(button)
        switch.addStretch(1)
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
        self._mode.button(int(self._settings.get("mode", 0))).setChecked(True)

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

    def current_traces(self) -> TraceSet | None:
        return self._traces

    # -- drawing ------------------------------------------------------------
    def _refresh_visible(self) -> None:
        tab = self.current_tab()
        if tab not in self._dirty:
            return
        self._dirty.discard(tab)
        if tab == "layout":
            if self.is_3d():
                self.view3d.set_data(self._layout, self._pseudo)
            else:
                self.plan.set_layout(self._layout)
                self.section.set_data(self._layout, self._pseudo)
            return
        self._traces = self._fetch_traces()
        if tab == "traces":
            self.traces.set_traces(self._traces)
        else:
            self.spectrum.set_traces(self._traces)

    def _fetch_traces(self) -> TraceSet | None:
        provider = self._provider
        group = self.selection.group()
        if provider is None or not group or "traces" not in provider.survey_capabilities():
            return None
        return provider.survey_traces(group, self._channels)

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
        self._dirty.add("layout")
        self._refresh_visible()
        self.viewChanged.emit()

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
            traces = self._traces or self._fetch_traces()
            if traces is not None:
                window = self.traces.window()
                figure = figures.trace_figure(traces, window=window.name if window else "", language=language)
        elif key == "spectrum":
            spectrum = self.spectrum.spectrum()
            if spectrum is None:
                self.spectrum.set_traces(self._traces or self._fetch_traces())
                spectrum = self.spectrum.spectrum()
            if spectrum is not None:
                figure = figures.spectrum_figure(
                    spectrum, line_frequency=self.spectrum.line_frequency(), language=language
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
