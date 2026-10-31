"""A Matplotlib figure with the Studio's navigation toolbar above it, and a row for a page's controls."""

from __future__ import annotations

import logging
import warnings

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget

from PyHydroGeophysX.qt_apps.widgets.readout import navigation_toolbar

_logger = logging.getLogger(__name__)


class FigurePane(QWidget):
    """A matplotlib figure with the studio's navigation toolbar above it."""

    def __init__(self, figsize=(8, 6), parent=None) -> None:
        super().__init__(parent)
        self.figure = Figure(figsize=figsize)
        self.canvas = FigureCanvas(self.figure)
        toolbar, readout = navigation_toolbar(self.canvas, self)
        bar = QHBoxLayout()
        bar.addWidget(toolbar)
        bar.addWidget(readout, 1)
        self.controls = QHBoxLayout()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(self.controls)
        layout.addLayout(bar)
        layout.addWidget(self.canvas, 1)

    def reset(self) -> Figure:
        """An empty figure to draw on.

        Clearing axes that share a log x axis makes matplotlib warn about the
        limits it is discarding; nothing is drawn with them, so it is quiet here.
        """
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", message="Attempt to set non-positive")
            self.figure.clear()
        return self.figure

    def message(self, text: str) -> None:
        """Clear the figure and say why there is nothing to draw."""
        self.reset()
        self.figure.text(0.5, 0.5, text, ha="center", va="center", color="#6e6e73", wrap=True)
        self.canvas.draw_idle()

    def finish(self) -> None:
        try:
            self.figure.tight_layout()
        except Exception:  # noqa: BLE001 - a crowded figure still draws
            _logger.debug("FigurePane.finish: a crowded figure still draws", exc_info=True)
        self.canvas.draw_idle()


__all__ = ["FigurePane"]
