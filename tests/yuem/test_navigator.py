"""Order of the geophysics navigator, and the drawn EM and DCIP marks."""

from __future__ import annotations

import pytest

pytest.importorskip("PySide6")

from PyHydroGeophysX.qt_apps.widgets.project_tree import TREE_STRUCTURE, sort_group_items

_GROUP = "Geophysical Data Processing"
_ORDER = (
    "mt",
    "em",
    "dcip",
    "ert",
    "gpr",
    "gravmag",
    "seismic",
    "boreholes",
    "mesh3d",
    "joint_inversion",
)


def test_geophysics_pages_follow_the_method_order() -> None:
    items = [
        ("Joint Inversion", "joint_inversion"),
        ("Seismic", "seismic"),
        ("DCIP", "dcip"),
        ("EM", "em"),
        ("Magnetotellurics", "mt"),
        ("ERT", "ert"),
        ("GPR", "gpr"),
        ("Gravity / Magnetics", "gravmag"),
        ("Boreholes", "boreholes"),
        ("3D Mesh Builder", "mesh3d"),
        ("Extra", "future_method"),
    ]
    sort_group_items(_GROUP, items)
    assert [key for _label, key in items] == [*_ORDER, "future_method"]


def test_the_builtin_geophysics_group_is_in_that_order() -> None:
    keys = [key for _label, key in dict(TREE_STRUCTURE)[_GROUP] if key != "dcip"]
    assert keys == [key for key in _ORDER if key != "dcip"]


@pytest.mark.gui
def test_em_and_dcip_icons_are_drawn(qtbot: object) -> None:
    from PyHydroGeophysX.qt_apps.widgets.project_tree import navigator_icon

    del qtbot
    for label in ("EM", "DCIP", "Seismic"):
        image = navigator_icon(label).pixmap(32, 32).toImage()
        assert image.width() > 0
        assert any(
            image.pixelColor(x, y).alpha() > 20 for y in range(image.height()) for x in range(image.width())
        )
