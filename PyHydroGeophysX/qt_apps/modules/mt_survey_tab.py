"""The MT page's "Sites and data quality" tab: where the sites are, and what their recordings hold.

Left, the sites (transfer functions and recordings) with each site's
recordings under it; right, PHGX's survey workbench: the sites on a plan and
in 3-D (with a recording's electric dipoles), the chosen recording's channels
over time and their spectra with the power-line harmonics marked. The tab reads
the page's sites and recordings when it is shown, so nothing else on the page
has to tell it.
"""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import QCoreApplication, Qt
from PySide6.QtWidgets import QCheckBox, QSplitter, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget

from PyHydroGeophysX.qt_apps.widgets import colormaps as cmaps
from PyHydroGeophysX.qt_apps.widgets.survey import SurveyWorkbench
from PyHydroGeophysX.survey.adapters.mt import MTSurvey, site_name

_SITE_ROLE = Qt.ItemDataRole.UserRole
_RUN_ROLE = Qt.ItemDataRole.UserRole + 1


class MTSurveyTab(QWidget):
    """Sites and recordings beside the survey workbench."""

    def __init__(self, page: Any) -> None:
        super().__init__()
        self.page = page
        self.provider = MTSurvey()
        self._signature: tuple[Any, ...] = ()
        self.tree = QTreeWidget()
        self.tree.setObjectName("mt_survey_sites")
        self.tree.setHeaderLabels(
            [QCoreApplication.translate("PHGX", "Site"), QCoreApplication.translate("PHGX", "Recording")]
        )
        self.tree.itemSelectionChanged.connect(self._picked)
        self.field_units = QCheckBox(QCoreApplication.translate("PHGX", "Field units (mV/km, nT)"))
        self.field_units.setToolTip(
            QCoreApplication.translate("PHGX", "Remove the instrument response before drawing the curves")
        )
        self.field_units.toggled.connect(self._on_units)
        side = QWidget()
        column = QVBoxLayout(side)
        column.setContentsMargins(0, 0, 0, 0)
        column.addWidget(self.tree, 1)
        column.addWidget(self.field_units)
        self.workbench = SurveyWorkbench(colormaps=cmaps.colormap_settings(page.state), settings_key="mt")
        self.workbench.selection.groupChanged.connect(self._group_picked)
        self.workbench.viewChanged.connect(page.resultsUpdated.emit)
        split = QSplitter(Qt.Orientation.Horizontal)
        split.addWidget(side)
        split.addWidget(self.workbench)
        split.setSizes([260, 900])
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(split)

    def showEvent(self, event: Any) -> None:
        super().showEvent(event)
        self.refresh()

    def refresh(self, force: bool = False) -> None:
        """Read the page's sites and recordings again when they changed."""
        sites = [entry["tf"] for entry in getattr(self.page, "_sites", [])]
        runs = list(getattr(self.page, "_runs", []))
        signature = (tuple(id(s) for s in sites), tuple(id(r) for r in runs), self.field_units.isChecked())
        if signature == self._signature and not force:
            return
        self._signature = signature
        self.provider = MTSurvey(sites, runs, calibrated=self.field_units.isChecked())
        self._fill_tree()
        self.workbench.set_provider(self.provider)
        group = self.workbench.selection.group()
        if not group and self.tree.topLevelItemCount():
            self.tree.setCurrentItem(self.tree.topLevelItem(0))

    def _fill_tree(self) -> None:
        provider = self.provider
        self.tree.blockSignals(True)
        self.tree.clear()
        names: list[str] = []
        for i, tf in enumerate(provider.sites):
            names.append(site_name(tf, f"site {i + 1}"))
        for i, run in enumerate(provider.runs):
            names.append(site_name(run, f"run {i + 1}"))
        for name in dict.fromkeys(names):
            item = QTreeWidgetItem([name, ""])
            item.setData(0, _SITE_ROLE, name)
            for index in provider.runs_of(name):
                run = provider.runs[index]
                minutes = run.duration / 60.0
                text = QCoreApplication.translate("PHGX", "{0:g} Hz · {1:.1f} min").format(
                    run.sample_rate, minutes
                )
                child = QTreeWidgetItem(["", text])
                child.setData(0, _SITE_ROLE, name)
                child.setData(0, _RUN_ROLE, index)
                item.addChild(child)
            self.tree.addTopLevelItem(item)
            item.setExpanded(True)
        self.tree.resizeColumnToContents(0)
        self.tree.blockSignals(False)

    def _picked(self) -> None:
        items = self.tree.selectedItems()
        if not items:
            return
        item = items[0]
        site = str(item.data(0, _SITE_ROLE) or "")
        run = item.data(0, _RUN_ROLE)
        if run is not None:
            self.provider.choose_run(site, int(run))
            self.workbench.refresh()
        self.workbench.selection.set_group(site)
        self.workbench.refresh_traces()

    def _group_picked(self, site: str) -> None:
        current = self.tree.selectedItems()
        if current and str(current[0].data(0, _SITE_ROLE) or "") == site:
            return
        for i in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            if item.data(0, _SITE_ROLE) == site:
                self.tree.blockSignals(True)
                self.tree.setCurrentItem(item)
                self.tree.blockSignals(False)
                return

    def _on_units(self, _on: bool) -> None:
        self.refresh(force=True)


__all__ = ["MTSurveyTab"]
