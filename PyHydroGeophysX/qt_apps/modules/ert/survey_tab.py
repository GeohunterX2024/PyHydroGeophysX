"""The ERT page's "Survey layout" tab: the electrodes, the injections and the pseudo-depth points.

Left, the current injections (A-B pairs) with their number of readings; right,
PHGX's survey workbench: the electrodes on a plan and in 3-D with the chosen
injection's current pair and potential dipoles, and the section with every
reading's pseudo-depth point coloured by its apparent resistivity, error or
validity. The tab reads the page's data (the readings the inversion uses) when
it is shown. Rejecting readings stays on the Data tab, with the page's QC log.
"""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import QCoreApplication, Qt
from PySide6.QtWidgets import QLabel, QListWidget, QListWidgetItem, QSplitter, QVBoxLayout, QWidget

from PyHydroGeophysX.qt_apps.widgets import colormaps as cmaps
from PyHydroGeophysX.qt_apps.widgets.survey import SurveyWorkbench
from PyHydroGeophysX.survey.adapters.ert import ERTSurvey

_GROUP_ROLE = Qt.ItemDataRole.UserRole


class ERTSurveyTab(QWidget):
    """Injections beside the survey workbench."""

    def __init__(self, page: Any) -> None:
        super().__init__()
        self.page = page
        self.provider: ERTSurvey | None = None
        self._source: Any = None
        self.injections = QListWidget()
        self.injections.setObjectName("ert_survey_injections")
        self.injections.currentItemChanged.connect(self._picked)
        self.note = QLabel()
        self.note.setWordWrap(True)
        side = QWidget()
        column = QVBoxLayout(side)
        column.setContentsMargins(0, 0, 0, 0)
        column.addWidget(QLabel(QCoreApplication.translate("PHGX", "Current injections")))
        column.addWidget(self.injections, 1)
        column.addWidget(self.note)
        self.workbench = SurveyWorkbench(colormaps=cmaps.colormap_settings(page.state), settings_key="ert")
        self.workbench.selection.groupChanged.connect(self._group_picked)
        self.workbench.viewChanged.connect(page.resultsUpdated.emit)
        split = QSplitter(Qt.Orientation.Horizontal)
        split.addWidget(side)
        split.addWidget(self.workbench)
        split.setSizes([200, 900])
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(split)

    def showEvent(self, event: Any) -> None:
        super().showEvent(event)
        self.refresh()

    def refresh(self) -> None:
        data = getattr(self.page, "_ert_data", None)
        if data is self._source and self.provider is not None:
            return
        self._source = data
        self.provider = ERTSurvey.from_container(data) if data is not None else None
        self.workbench.set_provider(self.provider)
        self.injections.blockSignals(True)
        self.injections.clear()
        if self.provider is not None:
            for name, count in self.provider.injections():
                item = QListWidgetItem(
                    QCoreApplication.translate("PHGX", "{0} ({1} readings)").format(name, count)
                )
                item.setData(_GROUP_ROLE, name)
                self.injections.addItem(item)
        self.injections.blockSignals(False)
        self.note.setText(
            QCoreApplication.translate("PHGX", "Load a survey on the Data tab to see its layout.")
            if self.provider is None
            else ""
        )
        self.note.setVisible(self.provider is None)

    def _picked(self, item: QListWidgetItem | None, _previous: QListWidgetItem | None) -> None:
        if item is not None:
            self.workbench.selection.set_group(str(item.data(_GROUP_ROLE)))

    def _group_picked(self, group: str) -> None:
        for row in range(self.injections.count()):
            item = self.injections.item(row)
            if item.data(_GROUP_ROLE) == group and self.injections.currentItem() is not item:
                self.injections.blockSignals(True)
                self.injections.setCurrentItem(item)
                self.injections.blockSignals(False)
                return


__all__ = ["ERTSurveyTab"]
