"""The QC panels' shared reject / restore / record controls (plan M4.4).

:class:`QCActionBar` acts on a :class:`~PyHydroGeophysX.datastore.qc.QCLog`:
Reject and Restore take what the panel has selected (its ``selection``
callback gives positions in the log's keys), Undo takes the last decision
back, and Record shows every decision with its reason and time, to copy into
a report or save with the data. :class:`BoxSelection` lets a Matplotlib plot
select its points by dragging a box. The panel listens to ``changed`` and
redraws and re-applies its mask.
"""

from __future__ import annotations

import csv
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Any

import numpy as np
from PySide6.QtCore import QCoreApplication, Signal
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from PyHydroGeophysX.datastore.qc import QCLog
from PyHydroGeophysX.qt_apps import i18n


#: Labels of the record's Action column, here so the translation catalog has them.
_ACTION_LABELS = ("Reject", "Restore")


def _tr(text: str) -> str:
    return QCoreApplication.translate("PHGX", text)


class QCActionBar(QWidget):
    """Reject, Restore, Undo and Record for the items a panel selects."""

    changed = Signal()

    def __init__(
        self,
        selection: Callable[[], Sequence[int]],
        parent: QWidget | None = None,
        *,
        what: str = "readings",
        save_record: Callable[[QCLog], str] | None = None,
    ) -> None:
        super().__init__(parent)
        self._selection = selection
        self._save_record = save_record
        self._log: QCLog | None = None
        self._what = what
        self._reason = QLineEdit()
        self._reason.setPlaceholderText(QCoreApplication.translate("PHGX", "Reason (kept in the record)"))
        self._reject = QPushButton(QCoreApplication.translate("PHGX", "Reject selected"))
        self._restore = QPushButton(QCoreApplication.translate("PHGX", "Restore selected"))
        self._undo = QPushButton(QCoreApplication.translate("PHGX", "Undo"))
        self._record = QPushButton(QCoreApplication.translate("PHGX", "Record…"))
        self._status = QLabel()
        self._reject.setToolTip(QCoreApplication.translate(
            "PHGX", "Leave the selected items out of processing and inversion; the decision is recorded."))
        self._restore.setToolTip(QCoreApplication.translate("PHGX", "Use the selected items again; recorded too."))
        self._record.setToolTip(QCoreApplication.translate(
            "PHGX", "Every decision with its reason and time; export it, or save it with the data."))
        self._reject.clicked.connect(lambda: self._decide("reject"))
        self._restore.clicked.connect(lambda: self._decide("restore"))
        self._undo.clicked.connect(self._take_back)
        self._record.clicked.connect(self.show_record)
        row = QHBoxLayout(self)
        row.setContentsMargins(0, 0, 0, 0)
        for widget in (self._reject, self._restore, self._undo, self._reason, self._record, self._status):
            row.addWidget(widget)
        row.setStretch(3, 1)
        self.set_log(None)

    @property
    def log(self) -> QCLog | None:
        return self._log

    def set_log(self, log: QCLog | None) -> None:
        """Act on ``log`` (None: nothing loaded, the controls are off)."""
        self._log = log
        for widget in (self._reject, self._restore, self._undo, self._record, self._reason):
            widget.setEnabled(log is not None)
        self._update_status()

    def _update_status(self) -> None:
        if self._log is None:
            self._status.setText("")
            return
        rejected = len(self._log.keys) - int(self._log.mask.sum())
        self._status.setText(
            QCoreApplication.translate("PHGX", "{0} of {1} rejected").format(rejected, len(self._log.keys)))
        self._undo.setEnabled(bool(self._log.decisions))

    def _decide(self, action: str) -> None:
        if self._log is None:
            return
        positions = sorted({int(p) for p in self._selection()})
        if not positions:
            self._status.setText(QCoreApplication.translate("PHGX", "Select items first (drag a box, or pick rows)."))
            return
        reason = self._reason.text().strip()
        if action == "reject":
            self._log.reject_at(positions, reason)
        else:
            self._log.restore_at(positions, reason)
        self._update_status()
        self.changed.emit()

    def _take_back(self) -> None:
        if self._log is not None and self._log.undo() is not None:
            self._update_status()
            self.changed.emit()

    def show_record(self) -> None:
        if self._log is not None:
            QCRecordDialog(self._log, self, save_record=self._save_record).exec()


class QCRecordDialog(QDialog):
    """Every decision of a QC log, exportable as CSV and, where the panel can, saved with the data."""

    COLUMNS = ("Time", "Action", "Items", "Reason", "Criterion")

    def __init__(self, log: QCLog, parent: QWidget | None = None, *,
                 save_record: Callable[[QCLog], str] | None = None) -> None:
        super().__init__(parent)
        self._log = log
        self._save_record = save_record
        self.setWindowTitle(QCoreApplication.translate("PHGX", "QC record"))
        self.table = QTableWidget(len(log.decisions), len(self.COLUMNS))
        self.table.setHorizontalHeaderLabels([_tr(c) for c in self.COLUMNS])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        for row, decision in enumerate(log.decisions):
            values = (decision.time, _tr(decision.action.capitalize()), str(len(decision.keys)), decision.reason,
                      decision.criterion)
            for column, value in enumerate(values):
                self.table.setItem(row, column, QTableWidgetItem(value))
        self.note = QLabel(i18n.tr(log.summary()))
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        export = buttons.addButton(QCoreApplication.translate("PHGX", "Export CSV…"),
                                   QDialogButtonBox.ButtonRole.ActionRole)
        export.clicked.connect(self._export)
        if save_record is not None:
            save = buttons.addButton(QCoreApplication.translate("PHGX", "Save with the data"),
                                     QDialogButtonBox.ButtonRole.ActionRole)
            save.clicked.connect(self._save)
        buttons.rejected.connect(self.reject)
        layout = QVBoxLayout(self)
        layout.addWidget(self.table)
        layout.addWidget(self.note)
        layout.addWidget(buttons)
        self.resize(720, 360)

    def export_csv(self, path: str | Path) -> Path:
        target = Path(path)
        with target.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.writer(stream)
            writer.writerow(["time", "action", "keys", "reason", "criterion"])
            for decision in self._log.decisions:
                record = decision.to_record()
                writer.writerow([record["time"], record["action"], record["keys"], record["reason"],
                                 record["criterion"]])
        return target

    def _export(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, QCoreApplication.translate("PHGX", "Export QC record"), "",
                                              "CSV (*.csv)")
        if path:
            self.export_csv(path)
            self.note.setText(QCoreApplication.translate("PHGX", "Saved {0}").format(path))

    def _save(self) -> None:
        if self._save_record is not None:
            self.note.setText(i18n.tr(self._save_record(self._log)))


class BoxSelection:
    """Select a Matplotlib plot's points by dragging a box over them.

    ``points`` gives the ``(n, 2)`` data coordinates of what is drawn, in the
    order of the positions the panel maps to its QC log; ``selected()`` is
    what the last box held. Active while ``enabled``.
    """

    def __init__(self, ax: Any, points: Callable[[], np.ndarray], on_select: Callable[[], None] | None = None) -> None:
        from matplotlib.widgets import RectangleSelector

        self._points = points
        self._on_select = on_select
        self._selected: list[int] = []
        self.selector = RectangleSelector(ax, self._chosen, useblit=False, button=[1], interactive=False,
                                          minspanx=0, minspany=0, spancoords="data")
        self.selector.set_active(False)

    @property
    def enabled(self) -> bool:
        return bool(self.selector.active)

    def set_enabled(self, enabled: bool) -> None:
        self.selector.set_active(bool(enabled))

    def select_box(self, x0: float, y0: float, x1: float, y1: float) -> list[int]:
        """Select the points inside the box with these corners (what a drag does)."""
        xy = np.asarray(self._points(), dtype=float).reshape(-1, 2)
        lo_x, hi_x = sorted((x0, x1))
        lo_y, hi_y = sorted((y0, y1))
        inside = (xy[:, 0] >= lo_x) & (xy[:, 0] <= hi_x) & (xy[:, 1] >= lo_y) & (xy[:, 1] <= hi_y)
        self._selected = np.flatnonzero(inside).tolist()
        if self._on_select is not None:
            self._on_select()
        return self._selected

    def _chosen(self, press: Any, release: Any) -> None:
        if None in (press.xdata, press.ydata, release.xdata, release.ydata):
            return
        self.select_box(press.xdata, press.ydata, release.xdata, release.ydata)

    def selected(self) -> list[int]:
        return list(self._selected)

    def clear(self) -> None:
        self._selected = []


class SpanSelection:
    """Select along a Matplotlib plot's x axis by dragging (periods, frequencies, times).

    ``values`` gives the x value of each item, in the order of the positions
    the panel maps to its QC log; ``selected()`` is what the last span held.
    """

    def __init__(self, ax: Any, values: Callable[[], np.ndarray], on_select: Callable[[], None] | None = None) -> None:
        from matplotlib.widgets import SpanSelector

        self._values = values
        self._on_select = on_select
        self._selected: list[int] = []
        self.selector = SpanSelector(ax, self.select_span, "horizontal", useblit=False, interactive=False,
                                     props={"alpha": 0.2, "facecolor": "#ff3b30"})
        self.selector.set_active(False)

    def set_enabled(self, enabled: bool) -> None:
        self.selector.set_active(bool(enabled))

    def select_span(self, x0: float, x1: float) -> list[int]:
        values = np.asarray(self._values(), dtype=float).ravel()
        lo, hi = sorted((x0, x1))
        self._selected = np.flatnonzero((values >= lo) & (values <= hi)).tolist()
        if self._on_select is not None:
            self._on_select()
        return self._selected

    def selected(self) -> list[int]:
        return list(self._selected)

    def clear(self) -> None:
        self._selected = []


__all__ = ["BoxSelection", "QCActionBar", "QCRecordDialog", "SpanSelection"]
