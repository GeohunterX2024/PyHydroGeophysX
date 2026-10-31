"""FlowLayout while Qt tears it down (a GUI-tier failure on Linux CI)."""

from __future__ import annotations

from typing import Any

import pytest

pytest.importorskip("PySide6")
pytestmark = pytest.mark.gui

from PySide6.QtWidgets import QLabel, QWidget  # noqa: E402

from PyHydroGeophysX.qt_apps.widgets.flow_layout import FlowLayout  # noqa: E402


def test_a_layout_whose_attributes_are_cleared_answers_as_an_empty_one(qtbot: Any) -> None:
    host = QWidget()
    qtbot.addWidget(host)
    flow = FlowLayout(host, spacing=4)
    flow.addWidget(QLabel("one"))
    flow.addWidget(QLabel("two"))
    assert flow.count() == 2

    # What garbage collection leaves while the C++ layout still gets calls.
    vars(flow).clear()

    assert flow.count() == 0
    assert flow.itemAt(0) is None
    assert flow.takeAt(0) is None
    assert flow.sizeHint().width() >= 0
    assert flow.heightForWidth(100) >= 0
