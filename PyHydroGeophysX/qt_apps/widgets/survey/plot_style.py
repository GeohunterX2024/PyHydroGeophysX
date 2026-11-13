"""How a 2-D survey plot looks: axes, ticks, grid, aspect, legend, colour bar, symbols and lines.

A :class:`PlotStyle` is plain data, kept per view as JSON in the Studio
settings. :func:`apply_frame` puts its axis, grid, aspect, legend and
background choices on a pyqtgraph plot; the views read its symbols and lines
when they draw. Ranges and tick intervals are in the display length unit
(``axis_units.length_factor``), as the axes are labelled.
"""

from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass, field, fields, replace
from typing import Any

import pyqtgraph as pg
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from PyHydroGeophysX.survey.scene import FADED, LINK_COLOURS, ROLE_STYLE
from PyHydroGeophysX.visualization import axis_units

_logger = logging.getLogger(__name__)

#: pyqtgraph symbol code -> name (English source text, translated when shown).
SYMBOLS = dict(
    (
        ("o", "Circle"),
        ("s", "Square"),
        ("t1", "Triangle up"),
        ("t", "Triangle down"),
        ("t2", "Triangle right"),
        ("t3", "Triangle left"),
        ("d", "Diamond"),
        ("p", "Pentagon"),
        ("h", "Hexagon"),
        ("star", "Star"),
        ("+", "Plus"),
        ("x", "Cross"),
    )
)
#: Line style key -> name (English source text).
DASHES = dict(
    (("solid", "Solid line"), ("dash", "Dashed line"), ("dot", "Dotted line"), ("dashdot", "Dash-dot line"))
)
_PEN_STYLES = {
    "solid": Qt.PenStyle.SolidLine,
    "dash": Qt.PenStyle.DashLine,
    "dot": Qt.PenStyle.DotLine,
    "dashdot": Qt.PenStyle.DashDotLine,
}
#: Legend corner key -> name (English source text).
CORNERS = dict(
    (
        ("top-right", "Top right"),
        ("top-left", "Top left"),
        ("bottom-right", "Bottom right"),
        ("bottom-left", "Bottom left"),
    )
)
#: Aspect key -> name (English source text).
ASPECTS = dict(
    (("free", "Fit the window"), ("equal", "Equal scales (1:1)"), ("exaggerated", "Vertical exaggeration"))
)
#: Space left above a top legend for the plot's mouse tools, in pixels.
TOOLBAR_CLEARANCE = 40

_SHAPE_CODES = {
    "triangle": "t1",
    "triangle_down": "t",
    "square": "s",
    "diamond": "d",
    "circle": "o",
    "sphere": "o",
}


@dataclass
class SymbolStyle:
    """A point symbol: shape, size in pixels, fill and edge (an empty fill draws a hollow symbol)."""

    symbol: str = "o"
    size: float = 7.0
    fill: str = "#6b7280"
    edge: str = "#1f2937"
    edge_width: float = 0.6

    def pen(self) -> Any:
        return pg.mkPen(self.edge, width=self.edge_width) if self.edge and self.edge_width > 0 else None

    def brush(self) -> Any:
        return pg.mkBrush(self.fill) if self.fill else None


@dataclass
class LineStyle:
    """A line: colour, width in pixels and dash."""

    colour: str = "#374151"
    width: float = 1.6
    dash: str = "solid"

    def pen(self) -> Any:
        pen = pg.mkPen(self.colour, width=self.width)
        pen.setStyle(_PEN_STYLES.get(self.dash, Qt.PenStyle.SolidLine))
        return pen


@dataclass
class AxisStyle:
    """One axis: its label (empty: the view's), range (in the display unit) and tick intervals."""

    label: str = ""
    auto_range: bool = True
    minimum: float = 0.0
    maximum: float = 0.0
    major: float = 0.0
    minor_divisions: int = 0
    inverted: bool = False


@dataclass
class PlotStyle:
    """Everything a user sets about a 2-D survey plot's drawing."""

    title: str = ""
    title_size: int = 11
    x: AxisStyle = field(default_factory=AxisStyle)
    y: AxisStyle = field(default_factory=AxisStyle)
    label_size: int = 10
    tick_size: int = 9
    tick_length: int = 5
    ticks_inside: bool = False
    frame: bool = True
    grid_x: bool = True
    grid_y: bool = True
    grid_opacity: float = 0.2
    aspect: str = "free"
    exaggeration: float = 1.0
    background: str = ""
    foreground: str = ""
    legend: bool = True
    legend_corner: str = "top-right"
    legend_size: int = 9
    legend_frame: bool = True
    legend_columns: int = 1
    colour_bar: bool = True
    colour_bar_label: str = ""
    point_labels: bool = False
    label_every: int = 5
    point_label_size: int = 8
    symbols: dict[str, SymbolStyle] = field(default_factory=dict)
    lines: dict[str, LineStyle] = field(default_factory=dict)

    def symbol(self, key: str) -> SymbolStyle:
        return self.symbols.get(key) or SymbolStyle()

    def line(self, key: str) -> LineStyle:
        return self.lines.get(key) or LineStyle()

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False)

    def merged(self, data: dict[str, Any]) -> PlotStyle:
        """This style with the fields of ``data`` (a stored style) that are still known and valid."""
        simple = {f.name for f in fields(self)} - {"x", "y", "symbols", "lines"}
        changes: dict[str, Any] = {}
        for name in simple:
            if name in data and isinstance(data[name], type(getattr(self, name))):
                changes[name] = data[name]
            elif name in data and isinstance(getattr(self, name), float) and isinstance(data[name], int):
                changes[name] = float(data[name])
        for name in ("x", "y"):
            if isinstance(data.get(name), dict):
                changes[name] = _merge_dataclass(getattr(self, name), data[name])
        for name in ("symbols", "lines"):
            stored = data.get(name)
            if isinstance(stored, dict):
                current = dict(getattr(self, name))
                for key, value in stored.items():
                    if key in current and isinstance(value, dict):
                        current[key] = _merge_dataclass(current[key], value)
                changes[name] = current
        return replace(self, **changes)


def _merge_dataclass(item: Any, data: dict[str, Any]) -> Any:
    changes: dict[str, Any] = {}
    for f in fields(item):
        value = data.get(f.name)
        default = getattr(item, f.name)
        if isinstance(value, type(default)) or (isinstance(default, float) and isinstance(value, int)):
            changes[f.name] = type(default)(value)
    return replace(item, **changes)


def load_style(default: PlotStyle, stored: Any) -> PlotStyle:
    """``default`` with a stored JSON style laid over it (anything unreadable is ignored)."""
    if not stored:
        return default
    try:
        data = json.loads(str(stored))
    except ValueError:
        _logger.debug("load_style: unreadable stored style", exc_info=True)
        return default
    return default.merged(data) if isinstance(data, dict) else default


def role_symbol(role: str) -> SymbolStyle:
    colour, shape, size = ROLE_STYLE[role]
    return SymbolStyle(_SHAPE_CODES.get(shape, "o"), size, colour, "#1f2937", 0.6)


def plan_default() -> PlotStyle:
    """The plan's default look: equal scales, roles in their survey colours."""
    symbols = {role: role_symbol(role) for role in ROLE_STYLE}
    symbols["others"] = SymbolStyle("t1", 7.0, FADED, "#1f2937", 0.6)
    symbols["current"] = SymbolStyle("o", 22.0, "", "#f59e0b", 2.5)
    symbols["selected"] = SymbolStyle("o", 16.0, "", "#f59e0b", 2.0)
    symbols["shown"] = SymbolStyle("o", 16.0, "", "#2563eb", 1.6)
    lines = {kind: LineStyle(colour, 2.0, "solid") for kind, colour in LINK_COLOURS.items()}
    return PlotStyle(aspect="equal", symbols=symbols, lines=lines)


def section_default() -> PlotStyle:
    """The section's default look: free aspect, small grey pseudo-depth points."""
    symbols = {
        "electrode": SymbolStyle("t", 7.0, "#1f2937", "", 0.0),
        "pseudo": SymbolStyle("o", 7.0, "#6b7280", "", 0.0),
        "current": SymbolStyle("o", 9.0, "", "#f59e0b", 1.6),
        "selected": SymbolStyle("o", 11.0, "", "#111827", 1.6),
        "shown": SymbolStyle("o", 8.0, "", "#2563eb", 1.2),
    }
    lines = {"terrain": LineStyle("#4d7c0f", 1.6, "solid")}
    return PlotStyle(symbols=symbols, lines=lines, point_labels=False)


#: Element keys of each view -> names (English source text).
PLAN_SYMBOL_NAMES = dict(
    (
        ("A", "Current electrode A"),
        ("B", "Current electrode B"),
        ("M", "Potential electrode M"),
        ("N", "Potential electrode N"),
        ("electrode", "Electrode"),
        ("site", "Site"),
        ("tx", "Transmitter"),
        ("rx", "Receiver"),
        ("others", "Other shots"),
        ("current", "Current shot ring"),
        ("selected", "Selected points"),
        ("shown", "Shots on screen"),
    )
)
PLAN_LINE_NAMES = dict(
    (
        ("AB", "Current pair A-B"),
        ("MN", "Potential pair M-N"),
        ("dipole_ex", "Ex dipole"),
        ("dipole_ey", "Ey dipole"),
        ("tx_loop", "Transmitter loop"),
    )
)
SECTION_SYMBOL_NAMES = dict(
    (
        ("electrode", "Electrode"),
        ("pseudo", "Pseudo-depth points"),
        ("current", "Current shot ring"),
        ("selected", "Selected points"),
        ("shown", "Readings on screen"),
    )
)
SECTION_LINE_NAMES = dict((("terrain", "Terrain"),))


def _font(size: int) -> QFont:
    font = QFont()
    font.setPointSize(max(5, int(size)))
    return font


def apply_frame(
    plot: pg.PlotWidget, style: PlotStyle, x_label: str, y_label: str, legend: Any = None
) -> None:
    """Put the axes, ticks, grid, aspect, background and legend of ``style`` on ``plot``.

    ``x_label`` and ``y_label`` are the view's own labels, used where the style leaves its label empty.
    """
    item = plot.getPlotItem()
    if style.background:
        plot.setBackground(style.background)
    foreground = style.foreground or None
    text_style = {"font-size": f"{style.label_size}pt"}
    if foreground:
        text_style["color"] = foreground
    for side, axis_style, default in (("bottom", style.x, x_label), ("left", style.y, y_label)):
        axis = item.getAxis(side)
        item.setLabel(side, axis_style.label or default, **text_style)
        _style_axis(axis, style, foreground)
        if axis_style.major > 0:
            divisions = max(int(axis_style.minor_divisions), 1)
            axis.setTickSpacing(axis_style.major, axis_style.major / divisions)
        else:
            axis.setTickSpacing()
    for side in ("top", "right"):
        if style.frame:
            item.showAxis(side)
            axis = item.getAxis(side)
            _style_axis(axis, style, foreground)
            axis.setStyle(showValues=False)
            axis.setScale(item.getAxis("bottom" if side == "top" else "left").scale)
        else:
            item.hideAxis(side)
    item.showGrid(x=style.grid_x, y=style.grid_y, alpha=max(0.0, min(1.0, style.grid_opacity)))
    view = item.getViewBox()
    view.invertY(style.y.inverted)
    view.invertX(style.x.inverted)
    if style.aspect == "equal":
        view.setAspectLocked(True, ratio=1.0)
    elif style.aspect == "exaggerated":
        view.setAspectLocked(True, ratio=1.0 / max(style.exaggeration, 1e-3))
    else:
        view.setAspectLocked(False)
    if style.title:
        title_style: dict[str, Any] = {"size": f"{style.title_size}pt"}
        if foreground:
            title_style["color"] = foreground
        item.setTitle(style.title, **title_style)  # i18n: as written
    else:
        item.setTitle(None)
    if legend is not None:
        style_legend(legend, style)


def _style_axis(axis: Any, style: PlotStyle, foreground: str | None) -> None:
    length = abs(int(style.tick_length))
    axis.setStyle(tickLength=-length if style.ticks_inside else length, tickFont=_font(style.tick_size))
    if foreground:
        axis.setPen(pg.mkPen(foreground))
        axis.setTextPen(pg.mkPen(foreground))


def style_legend(legend: Any, style: PlotStyle) -> None:
    """Corner, font, frame and columns of a pyqtgraph legend."""
    legend.setVisible(style.legend)
    corner = style.legend_corner if style.legend_corner in CORNERS else "top-right"
    right = corner.endswith("right")
    top = corner.startswith("top")
    offset_x = -10 if right else 10
    offset_y = 10 if top else -10
    if top and not right:
        offset_y += TOOLBAR_CLEARANCE
    anchor = (1.0 if right else 0.0, 0.0 if top else 1.0)
    try:
        legend.anchor(anchor, anchor, (offset_x, offset_y))
    except (AttributeError, TypeError):
        _logger.debug("style_legend: the legend is not placed yet", exc_info=True)
    legend.setLabelTextSize(f"{style.legend_size}pt")
    if style.foreground:
        legend.setLabelTextColor(style.foreground)
    if style.legend_frame:
        legend.setPen(pg.mkPen("#9ca3af"))
        legend.setBrush(pg.mkBrush(255, 255, 255, 200))
    else:
        legend.setPen(pg.mkPen(None))
        legend.setBrush(pg.mkBrush(None))
    legend.setColumnCount(max(1, int(style.legend_columns)))


def apply_ranges(plot: pg.PlotWidget, style: PlotStyle) -> bool:
    """Set the fixed axis ranges of ``style`` (display unit); True if any axis is fixed."""
    view = plot.getPlotItem().getViewBox()
    factor = axis_units.length_factor() or 1.0
    fixed = False
    for axis_style, axis in ((style.x, view.XAxis), (style.y, view.YAxis)):
        if axis_style.auto_range or axis_style.maximum <= axis_style.minimum:
            continue
        lo, hi = axis_style.minimum / factor, axis_style.maximum / factor
        if axis == view.XAxis:
            view.setXRange(lo, hi, padding=0.0)
        else:
            view.setYRange(lo, hi, padding=0.0)
        fixed = True
    return fixed


__all__ = [
    "ASPECTS",
    "CORNERS",
    "DASHES",
    "PLAN_LINE_NAMES",
    "PLAN_SYMBOL_NAMES",
    "SECTION_LINE_NAMES",
    "SECTION_SYMBOL_NAMES",
    "SYMBOLS",
    "TOOLBAR_CLEARANCE",
    "AxisStyle",
    "LineStyle",
    "PlotStyle",
    "SymbolStyle",
    "apply_frame",
    "apply_ranges",
    "load_style",
    "plan_default",
    "role_symbol",
    "section_default",
    "style_legend",
]
