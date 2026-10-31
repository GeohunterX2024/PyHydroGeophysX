"""The ERT page: readings rejected by hand on the pseudosection (plan M4.4).

Drag a box over the pseudosection to select readings, then Reject or
Restore them; rejected readings stay drawn as grey crosses so they can be
selected and restored. The decisions are a :class:`QCLog` over the rows of
the survey as loaded: Apply filter and Reset take the rejected rows out
before the automatic checks, the run's QC file records them, and Record can
save them with the survey as a version of the project's dataset.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

import numpy as np
from PySide6.QtCore import QCoreApplication
from PySide6.QtWidgets import QHBoxLayout, QPushButton, QWidget

from PyHydroGeophysX.data_processing.ert_io import PSEUDO_DEPTH_FACTOR
from PyHydroGeophysX.datastore.qc import QCLog
from PyHydroGeophysX.qt_apps.widgets.qc_actions import BoxSelection, QCActionBar

from .common import _logger


def aligned_pseudosection(data: Any) -> np.ndarray:
    """``(n, 2)`` pseudosection position of every reading of ``data``, NaN where it has none.

    The placement of ``ert_io.pseudosection_points`` (what the page draws), one
    row per reading, so a position is also the reading's row.
    """
    x = np.asarray(data.sensors(), dtype=float)[:, 0]
    ids = np.stack([np.asarray(data[t], dtype=int) for t in ("a", "b", "m", "n")], axis=1)
    if ids.size and ids.min() >= 1 and ids.max() >= x.size:
        ids = ids - 1
    out = np.full((ids.shape[0], 2), np.nan)
    inside = ((ids >= 0) & (ids < x.size)).all(axis=1)
    if inside.any():
        xs = x[ids[inside]]
        spread = xs.max(axis=1) - xs.min(axis=1)
        out[inside, 0] = xs.mean(axis=1)
        out[inside, 1] = np.maximum(spread * PSEUDO_DEPTH_FACTOR, 0.01)
    return out


class _ManualQC:
    _manual_qc: Optional[QCLog] = None
    _manual_xy: Optional[np.ndarray] = None
    _qc_box: Optional[BoxSelection] = None

    def _build_manual_qc(self) -> QWidget:
        box = QWidget()
        row = QHBoxLayout(box)
        row.setContentsMargins(4, 0, 4, 0)
        self._qc_select = QPushButton(QCoreApplication.translate("PHGX", "Box select"))
        self._qc_select.setCheckable(True)
        self._qc_select.setToolTip(QCoreApplication.translate(
            "PHGX", "Drag a box on the pseudosection to select readings, then Reject or Restore them."))
        self._qc_select.toggled.connect(self._on_box_select_toggled)
        self._qc_bar = QCActionBar(self._manual_selection, box, what="readings", save_record=self._save_qc_record)
        self._qc_bar.changed.connect(self._on_manual_qc_changed)
        row.addWidget(self._qc_select)
        row.addWidget(self._qc_bar, 1)
        return box

    def _reset_manual_qc(self) -> None:
        """A new survey: a fresh log over its readings."""
        data = self._ert_data_full
        try:
            self._manual_xy = aligned_pseudosection(data) if data is not None and hasattr(data, "sensors") else None
        except (AttributeError, IndexError, ValueError, RuntimeError):
            _logger.debug("no pseudosection positions for manual QC", exc_info=True)
            self._manual_xy = None
        size = 0 if self._manual_xy is None else self._manual_xy.shape[0]
        self._manual_qc = QCLog(range(size), name="manual_qc") if size else None
        if hasattr(self, "_qc_bar"):
            self._qc_bar.set_log(self._manual_qc)
            self._qc_select.setChecked(False)

    def _manual_points(self) -> np.ndarray:
        return np.zeros((0, 2)) if self._manual_xy is None else self._manual_xy

    def _manual_selection(self) -> list:
        return [] if self._qc_box is None else self._qc_box.selected()

    def _on_box_select_toggled(self, enabled: bool) -> None:
        if enabled and hasattr(self, "_pseudo_toolbar"):
            # The toolbar's zoom or pan would take the same drag.
            mode = str(getattr(self._pseudo_toolbar, "mode", "") or "")
            if "zoom" in mode.lower():
                self._pseudo_toolbar.zoom()
            elif "pan" in mode.lower():
                self._pseudo_toolbar.pan()
        self._attach_box_selection()

    def _attach_box_selection(self) -> None:
        """(Re)attach the box selector: clearing the axes for a redraw removes its artists."""
        enabled = bool(getattr(self, "_qc_select", None) and self._qc_select.isChecked())
        self._qc_box = BoxSelection(self._pseudo_ax, self._manual_points, on_select=self._draw_manual_rejections)
        self._qc_box.set_enabled(enabled)

    def _draw_manual_rejections(self) -> None:
        """Rejected readings as grey crosses, the selection outlined; called after each redraw."""
        if self._manual_qc is None or self._manual_xy is None:
            return
        for artist in list(getattr(self, "_qc_artists", [])):
            try:
                artist.remove()
            except (ValueError, NotImplementedError):
                _logger.debug("a QC marker was already gone", exc_info=True)
        self._qc_artists = []
        xy = self._manual_xy
        rejected = ~self._manual_qc.mask
        if rejected.any():
            self._qc_artists.append(self._pseudo_ax.scatter(
                xy[rejected, 0], xy[rejected, 1], marker="x", s=30, c="#8e8e93", linewidths=1.0, zorder=4))
        chosen = self._manual_selection()
        if chosen:
            self._qc_artists.append(self._pseudo_ax.scatter(
                xy[chosen, 0], xy[chosen, 1], marker="o", s=60, facecolors="none", edgecolors="#ff3b30",
                linewidths=1.0, zorder=5))
        self._pseudo_canvas.draw_idle()

    def _on_manual_qc_changed(self) -> None:
        if self._qc_box is not None:
            self._qc_box.clear()
        if self._qc_applied is not None:
            self._apply_filter()
        else:
            self._apply_manual_only()

    def _survey_without_rejected(self) -> tuple:
        """``(survey, rows)``: the loaded survey without the rejected rows, and which rows it holds."""
        import pygimli as pg

        full = pg.DataContainerERT(self._ert_data_full)
        if self._manual_qc is None or self._manual_qc.mask.all():
            return full, np.arange(int(full.size()))
        mask = self._manual_qc.mask
        full.markInvalid(np.flatnonzero(~mask).tolist())
        full.removeInvalid()
        return full, np.flatnonzero(mask)

    def _qc_survey_with_manual(self, qc: Dict[str, Any], report: Dict[str, Any]) -> tuple:
        """Apply filter's checks on the survey after the rejected readings are taken out."""
        survey, rows = self._survey_without_rejected()
        data, keep_rows, reasons = self._qc_survey(survey, qc, report)
        keep = np.zeros(int(self._ert_data_full.size()), dtype=bool)
        keep[rows[np.asarray(keep_rows, dtype=bool)]] = True
        if self._manual_qc is not None and not self._manual_qc.mask.all():
            report["manual"] = self._manual_qc.to_record()
            reasons = [self._manual_qc.summary(), *reasons]
        return data, keep, reasons

    def _apply_manual_only(self) -> None:
        """No automatic filter: the survey as loaded, less what was rejected by hand."""
        if self._ert_data_full is None:
            return
        try:
            survey, rows = self._survey_without_rejected()
        except (ImportError, RuntimeError, ValueError):
            _logger.debug("manual QC needs pyGIMLi", exc_info=True)
            return
        keep = np.zeros(int(self._ert_data_full.size()), dtype=bool)
        keep[rows] = True
        self._ert_data = survey
        self._qc_mask = keep.tolist()
        self._pseudo = self._pseudo_from_data(survey)
        self._n_meas = int(survey.size())
        self._refresh()
        self._recip_inputs_changed()

    def _manual_qc_record(self) -> Optional[Dict[str, Any]]:
        """What the run's QC file records of the readings rejected by hand."""
        if self._manual_qc is None or not self._manual_qc.decisions:
            return None
        return self._manual_qc.to_record()

    def _save_qc_record(self, log: QCLog) -> str:
        """Save the survey, its manual-QC mask and the decisions as a version of the project's dataset."""
        from PyHydroGeophysX.datastore import DatasetStore
        from PyHydroGeophysX.datastore.adapters.ert import from_data_container

        store = DatasetStore(self.state.ensure_results_store().root)
        raw = []
        if self._data_path is not None and self._data_path.is_file():
            raw.append(store.reference_raw(self._data_path))
        dataset = log.write_to(from_data_container(self._ert_data_full, raw_files=raw))
        stem = self._data_path.stem if self._data_path is not None else "ert-survey"
        dataset_id = "".join(c if c.isalnum() or c in "._-" else "-" for c in stem).strip("-.") or "ert-survey"
        entry = store.put(dataset, f"ert-{dataset_id}", label=log.summary())
        self.log(f"Saved the manual QC of {stem} as dataset {entry.dataset_id} v{entry.version}.", "success")
        return QCoreApplication.translate("PHGX", "Saved as dataset {0}, version {1}").format(
            entry.dataset_id, entry.version)


__all__ = ["aligned_pseudosection"]
