"""A side panel of view options that folds away to a thin strip.

The 3-D view keeps its layer switches, colouring, exaggeration and camera here;
folded, the plot takes the whole width and one button brings the panel back.
The folded state is remembered per view.
"""

from __future__ import annotations

from PySide6.QtCore import QCoreApplication, Qt
from PySide6.QtWidgets import QFrame, QScrollArea, QSizePolicy, QToolButton, QVBoxLayout, QWidget

from PyHydroGeophysX.qt_apps import theme
from PyHydroGeophysX.qt_apps.widgets.survey.common import Settings


class CollapsiblePanel(QWidget):
    """A titled panel whose body (a scrollable column) can be folded away."""

    def __init__(self, title: str, view: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._settings = Settings(view)
        self._toggle = QToolButton()
        self._toggle.setObjectName("surveyOptionsToggle")
        self._toggle.setCheckable(True)
        self._toggle.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self._toggle.setText(title)  # i18n: as written
        self._toggle.setToolTip(QCoreApplication.translate("PHGX", "Show or hide the view options"))
        self._toggle.toggled.connect(self._on_toggled)
        self._body = QWidget()
        self.body_layout = QVBoxLayout(self._body)
        self.body_layout.setContentsMargins(4, 4, 4, 4)
        self.body_layout.setSpacing(6)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setWidget(self._body)
        self._scroll = scroll
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        layout.addWidget(self._toggle, 0, Qt.AlignmentFlag.AlignTop)
        layout.addWidget(scroll, 1)
        self.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Expanding)
        self._toggle.setChecked(self._settings.get("options_open", True))
        self._on_toggled(self._toggle.isChecked())

    def is_open(self) -> bool:
        return self._toggle.isChecked()

    def set_open(self, on: bool) -> None:
        self._toggle.setChecked(bool(on))

    def _on_toggled(self, on: bool) -> None:
        self._scroll.setVisible(on)
        self._toggle.setIcon(theme.icon("fa5s.chevron-right" if on else "fa5s.sliders-h"))
        self.setMinimumWidth(220 if on else 0)
        self.setMaximumWidth(320 if on else 16777215)
        self._settings.set("options_open", bool(on))


__all__ = ["CollapsiblePanel"]
