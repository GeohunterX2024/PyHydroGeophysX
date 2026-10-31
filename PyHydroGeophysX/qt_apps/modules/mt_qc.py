"""The MT page: estimates rejected by hand on the apparent resistivity and phase curves (plan M4.4).

Drag across the curves to select periods, then Reject or Restore them; the
rejected periods are shaded on both panels. A log per site keeps the
decisions, by frequency, and a 1-D inversion of the site leaves those
frequencies out (``mt.invert_1d``'s ``rejected_frequencies``).
"""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional

import numpy as np
from PySide6.QtCore import QCoreApplication
from PySide6.QtWidgets import QHBoxLayout, QPushButton, QWidget

from PyHydroGeophysX.datastore.qc import QCLog
from PyHydroGeophysX.qt_apps.widgets.qc_actions import QCActionBar, SpanSelection


def site_key(tf: Any) -> str:
    """One site's log key: its station and frequency range."""
    frequency = np.asarray(tf.frequency, dtype=float)
    return f"{tf.station or 'site'}:{frequency.min():.6g}-{frequency.max():.6g}:{frequency.size}"


class MTFrequencyQC(QWidget):
    """Reject and restore an MT site's estimates by period; ``redraw`` draws the sounding again."""

    def __init__(self, redraw: Callable[[], None], parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._redraw = redraw
        self._logs: Dict[str, QCLog] = {}
        self._log: Optional[QCLog] = None
        self._periods = np.zeros(0)
        self._span: Optional[SpanSelection] = None
        self._select = QPushButton(QCoreApplication.translate("PHGX", "Select periods"))
        self._select.setCheckable(True)
        self._select.setToolTip(QCoreApplication.translate(
            "PHGX", "Drag across the curves to select periods, then Reject or Restore them."))
        self._select.toggled.connect(lambda on: self._span.set_enabled(on) if self._span else None)
        self.bar = QCActionBar(self._selected, self, what="frequencies")
        self.bar.changed.connect(self._changed)
        row = QHBoxLayout(self)
        row.setContentsMargins(0, 0, 0, 0)
        row.addWidget(self._select)
        row.addWidget(self.bar, 1)

    def attach(self, axes: Any, tf: Any) -> None:
        """After the sounding is drawn on ``axes`` (apparent resistivity, phase): shade and select."""
        frequency = np.asarray(tf.frequency, dtype=float)
        key = site_key(tf)
        log = self._logs.get(key)
        if log is None:
            log = self._logs[key] = QCLog([float(f) for f in frequency], name="manual_frequencies")
        self._log = log
        self.bar.set_log(log)
        self._periods = 1.0 / frequency
        rejected = ~log.mask
        for ax in np.atleast_1d(axes):
            for period in self._periods[rejected]:
                ax.axvspan(period / 1.08, period * 1.08, color="#8e8e93", alpha=0.35, zorder=0, linewidth=0)
        first = np.atleast_1d(axes)[0]
        self._span = SpanSelection(first, lambda: self._periods)
        self._span.set_enabled(self._select.isChecked())

    def _selected(self) -> List[int]:
        return [] if self._span is None else self._span.selected()

    def _changed(self) -> None:
        if self._span is not None:
            self._span.clear()
        self._redraw()

    def rejected_frequencies(self, tf: Any) -> List[float]:
        """The frequencies of ``tf`` rejected by hand (Hz)."""
        log = self._logs.get(site_key(tf))
        return [float(f) for f in log.rejected()] if log is not None else []


__all__ = ["MTFrequencyQC", "site_key"]
