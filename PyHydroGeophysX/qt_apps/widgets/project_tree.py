"""Left navigator tree that emits a module key when an item is selected."""

from __future__ import annotations

import math
from typing import Callable, List, Tuple

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QColor, QIcon, QImage, QPainter, QPainterPath, QPen, QPixmap
from PySide6.QtWidgets import QTreeWidget, QTreeWidgetItem

from PyHydroGeophysX.qt_apps import i18n, theme

_MODULE_ROLE = Qt.UserRole

_GROUP_ICONS = {
    "Geophysical Data Processing": "fa5s.wave-square",
    "Hydro → Geophysics": "fa5s.water",
    "Geophy → Hydrology": "fa5s.mountain",
    "Project": "fa5s.folder-open",
}
_CHILD_ICONS = {
    "Seismic": "fa5s.wave-square",
    "ERT": "fa5s.bolt",
    "3D Mesh Builder": "fa5s.cube",
    "EM": "fa5s.broadcast-tower",
    "Gravity / Magnetics": "fa5s.magnet",
    "Magnetotellurics": "fa5s.globe-americas",
    "GPR": "fa5s.broadcast-tower",
    "Boreholes": "fa5s.ruler-vertical",
    "Joint Inversion": "fa5s.project-diagram",
    "Simulate surveys": "fa5s.play-circle",
    "Inverted Model": "fa5s.database",
    "Layers": "fa5s.layer-group",
    "Target": "fa5s.bullseye",
    "Estimation": "fa5s.dice",
    "Seismic Lines": "fa5s.wave-square",
    "Interface": "fa5s.mountain",
    "3D Grid": "fa5s.th",
    "Build Model": "fa5s.cubes",
    "Seismic → Structure": "fa5s.cube",
    "ERT → Water Content": "fa5s.tint",
    "Saved Results": "fa5s.history",
    "Map": "fa5s.map-marked-alt",
}

# Pages in a navigator group, by module key. A plugin page listed here (dcip)
# is placed when it registers; anything not listed keeps its relative order
# after these.
GROUP_PAGE_ORDER = {
    "Geophysical Data Processing": (
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
    ),
}

# (group label, [(child label, module key), ...]). One entry per page: the
# stages of a page are on the page, not in the tree.
TREE_STRUCTURE: List[Tuple[str, List[Tuple[str, str]]]] = [
    ("Workflow", [("Data & reports", "one_click")]),
    (
        "Geophysical Data Processing",
        [
            ("Magnetotellurics", "mt"),
            ("EM", "em"),
            ("ERT", "ert"),
            ("GPR", "gpr"),
            ("Gravity / Magnetics", "gravmag"),
            ("Seismic", "seismic"),
            ("Boreholes", "boreholes"),
            ("3D Mesh Builder", "mesh3d"),
            ("Joint Inversion", "joint_inversion"),
        ],
    ),
    (
        "Hydro → Geophysics",
        [
            ("Simulate surveys", "hydro_geophysics"),
        ],
    ),
    (
        "Geophy → Hydrology",
        [
            ("Seismic → Structure", "seismic3d"),
            ("ERT → Water Content", "geo_hydrology"),
        ],
    ),
    # Every computation is recorded in the active Project, so the history needs a
    # permanent home in the navigator rather than only a Tools menu entry.
    (
        "Project",
        [
            ("Saved Results", "model_viewer"),
            ("Map", "project_map"),
        ],
    ),
]


def item_icon(label: str) -> str:
    """The qtawesome name the navigator draws beside the group or item ``label``."""
    if label in _GROUP_ICONS:
        return _GROUP_ICONS[label]
    return _CHILD_ICONS.get(label, "fa5s.circle")


def sort_group_items(group: str, items: List[Tuple[str, str]]) -> None:
    """Order ``items`` by :data:`GROUP_PAGE_ORDER`, leaving unknown keys at the end."""
    order = GROUP_PAGE_ORDER.get(group)
    if not order:
        return
    rank = {key: index for index, key in enumerate(order)}
    tail = len(rank)
    items.sort(key=lambda item: rank.get(item[1], tail))


def _stroke(color: str) -> QPen:
    pen = QPen(QColor(color))
    pen.setWidthF(1.45)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    return pen


def _paint_ac(painter: QPainter, color: str) -> None:
    """One period of a sine wave, the AC mark ∿, crest first."""
    painter.setPen(_stroke(color))
    path = QPainterPath()
    for step in range(33):
        fraction = step / 32
        x = 1.1 + fraction * 13.8
        y = 8.0 - math.sin(fraction * 2 * math.pi) * 4.8
        if step == 0:
            path.moveTo(x, y)
        else:
            path.lineTo(x, y)
    painter.drawPath(path)


def _paint_seismic(painter: QPainter, color: str) -> None:
    """Four vertical wiggles, positive peaks filled, as a seismic record."""
    ink = QColor(color)
    pen = QPen(ink)
    pen.setWidthF(0.8)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    cycles = 2
    amplitude = 1.05
    for center in (2.5, 6.15, 9.8, 13.45):
        points = []
        for step in range(41):
            fraction = step / 40
            y = 1.0 + fraction * 14.0
            x = center - amplitude * math.sin(fraction * 2 * math.pi * cycles)
            points.append((x, y))
        fill = QPainterPath()
        positive = False
        for x, y in points:
            if x >= center:
                if not positive:
                    fill.moveTo(center, y)
                    positive = True
                fill.lineTo(x, y)
            elif positive:
                fill.lineTo(center, y)
                fill.closeSubpath()
                positive = False
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(ink)
        painter.drawPath(fill)
        stroke = QPainterPath()
        stroke.moveTo(*points[0])
        for point in points[1:]:
            stroke.lineTo(*point)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(stroke)


def _paint_dcip(painter: QPainter, color: str) -> None:
    """A square-wave pulse crossing a baseline: the DCIP mark."""
    ink = QColor(color)
    baseline = QPen(ink)
    baseline.setWidthF(0.7)
    baseline.setCapStyle(Qt.PenCapStyle.RoundCap)
    painter.setPen(baseline)
    painter.drawLine(0.7, 7.7, 15.3, 7.7)
    pen = QPen(ink)
    pen.setWidthF(1.55)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    path = QPainterPath()
    path.moveTo(2.05, 7.7)
    path.lineTo(2.05, 3.5)
    path.quadTo(2.05, 2.15, 3.4, 2.15)
    path.lineTo(4.15, 2.15)
    path.quadTo(5.5, 2.15, 5.5, 3.5)
    path.lineTo(5.5, 6.6)
    path.lineTo(7.85, 8.8)
    path.lineTo(7.85, 11.9)
    path.quadTo(7.85, 13.45, 9.3, 13.45)
    path.lineTo(10.15, 13.45)
    path.quadTo(11.6, 13.45, 11.6, 11.9)
    path.lineTo(11.6, 7.7)
    painter.setPen(pen)
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.drawPath(path)


_DRAWN_ICONS: dict[str, Callable[[QPainter, str], None]] = {
    "EM": _paint_ac,
    "DCIP": _paint_dcip,
    "Seismic": _paint_seismic,
}


def _drawn_icon(paint: Callable[[QPainter, str], None]) -> QIcon:
    color = theme.PALETTE["accent"]
    icon = QIcon()
    for extent in (16, 32):
        image = QImage(extent, extent, QImage.Format.Format_ARGB32_Premultiplied)
        image.fill(Qt.GlobalColor.transparent)
        painter = QPainter(image)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.scale(extent / 16, extent / 16)
        paint(painter, color)
        painter.end()
        pixmap = QPixmap.fromImage(image)
        pixmap.setDevicePixelRatio(extent / 16)
        icon.addPixmap(pixmap)
    return icon


def navigator_icon(label: str) -> QIcon:
    """The icon beside a navigator entry. EM is ∿; seismic is a wiggle trace; DCIP is a square-wave pulse."""
    paint = _DRAWN_ICONS.get(label)
    if paint is not None:
        return _drawn_icon(paint)
    color = theme.PALETTE["primary"] if label in _GROUP_ICONS else theme.PALETTE["accent"]
    return theme.icon(item_icon(label), color=color)


class ProjectTree(QTreeWidget):
    """A two-group navigator. Emits ``moduleSelected(module_key)`` on click."""

    moduleSelected = Signal(str)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setHeaderHidden(True)
        self.setMinimumWidth(220)
        self.setIconSize(QSize(16, 16))
        self.setIndentation(12)
        self._key_to_item = {}
        self._build()
        self.itemClicked.connect(self._on_item_clicked)

    def _build(self) -> None:
        for group_label, children in TREE_STRUCTURE:
            sort_group_items(group_label, children)
            group = QTreeWidgetItem([i18n.tr(group_label)])
            group.setFlags(group.flags() & ~Qt.ItemIsSelectable)
            font = group.font(0)
            font.setBold(True)
            group.setFont(0, font)
            group.setIcon(
                0, theme.icon(_GROUP_ICONS.get(group_label, "fa5s.folder"), color=theme.PALETTE["primary"])
            )
            self.addTopLevelItem(group)
            for child_label, module_key in children:
                child = QTreeWidgetItem([i18n.tr(child_label)])
                child.setData(0, _MODULE_ROLE, module_key)
                child.setIcon(0, navigator_icon(child_label))
                group.addChild(child)
                self._key_to_item.setdefault(module_key, child)
            group.setExpanded(True)

    def _on_item_clicked(self, item: QTreeWidgetItem, _column: int) -> None:
        key = item.data(0, _MODULE_ROLE)
        if key:
            self.moduleSelected.emit(str(key))

    def select_module(self, module_key: str) -> None:
        """Programmatically highlight the first tree item for ``module_key``."""
        item = self._key_to_item.get(module_key)
        if item is not None:
            self.setCurrentItem(item)

    def focus_modules(self, keys=()):
        """A reversible domain focus; the View menu can restore every tool."""
        allowed = set(keys)
        for index in range(self.topLevelItemCount()):
            group = self.topLevelItem(index)
            visible = 0
            for j in range(group.childCount()):
                child = group.child(j)
                show = not allowed or child.data(0, _MODULE_ROLE) in allowed
                child.setHidden(not show)
                visible += show
            group.setHidden(not visible)
