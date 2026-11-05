"""The 2-D options panel: the drawing of the plan and the section, one tab each.

Each tab edits a :class:`~.plot_style.PlotStyle` - title and axis labels,
fonts, ticks and ranges, aspect, grid, symbols, lines, point labels, legend,
colour bar and colours - and hands every change to its view at once. The
panel folds away like the 3-D options.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import replace
from typing import Any

from PySide6.QtCore import QCoreApplication, Signal
from PySide6.QtGui import QColor, QIcon, QPixmap
from PySide6.QtWidgets import (
    QCheckBox,
    QColorDialog,
    QComboBox,
    QDoubleSpinBox,
    QGridLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QMenu,
    QPushButton,
    QSpinBox,
    QTabWidget,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from PyHydroGeophysX.qt_apps import i18n
from PyHydroGeophysX.qt_apps.widgets.survey.options import CollapsiblePanel
from PyHydroGeophysX.qt_apps.widgets.survey.plot_style import (
    ASPECTS,
    CORNERS,
    DASHES,
    SYMBOLS,
    AxisStyle,
    LineStyle,
    PlotStyle,
    SymbolStyle,
)
from PyHydroGeophysX.visualization import axis_units

#: Returns the view on screen as (x min, x max, y min, y max) in metres.
ViewRange = Callable[[], tuple[float, float, float, float]]


class ColourButton(QToolButton):
    """A colour swatch; a click chooses a colour, the arrow can clear it (when the colour is optional)."""

    colourChanged = Signal(str)

    def __init__(self, *, empty_text: str = "", parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._colour = ""
        self._empty_text = empty_text
        self.setMinimumWidth(64)
        self.clicked.connect(self._choose)
        if empty_text:
            menu = QMenu(self)
            menu.addAction(QCoreApplication.translate("PHGX", "Choose…"), self._choose)
            menu.addAction(empty_text, lambda: self._set_and_emit(""))  # i18n: as written
            self.setMenu(menu)
            self.setPopupMode(QToolButton.ToolButtonPopupMode.MenuButtonPopup)
        self._show()

    def colour(self) -> str:
        return self._colour

    def set_colour(self, colour: str) -> None:
        self._colour = colour
        self._show()

    def _show(self) -> None:
        if self._colour:
            pixmap = QPixmap(28, 14)
            pixmap.fill(QColor(self._colour))
            self.setIcon(QIcon(pixmap))
            self.setText("")
            self.setToolTip(self._colour)  # i18n: as written
        else:
            self.setIcon(QIcon())
            self.setText(self._empty_text)  # i18n: as written
            self.setToolTip(self._empty_text)  # i18n: as written

    def _choose(self) -> None:
        start = QColor(self._colour) if self._colour else QColor("#ffffff")
        chosen = QColorDialog.getColor(start, self, QCoreApplication.translate("PHGX", "Choose a colour"))
        if chosen.isValid():
            self._set_and_emit(chosen.name())

    def _set_and_emit(self, colour: str) -> None:
        self.set_colour(colour)
        self.colourChanged.emit(colour)


def _spin(lo: int, hi: int, suffix: str = "") -> QSpinBox:
    box = QSpinBox()
    box.setRange(lo, hi)
    box.setSuffix(suffix)  # i18n: as written
    return box


def _double(lo: float, hi: float, step: float, decimals: int) -> QDoubleSpinBox:
    box = QDoubleSpinBox()
    box.setRange(lo, hi)
    box.setSingleStep(step)
    box.setDecimals(decimals)
    return box


def _combo(names: dict[str, str]) -> QComboBox:
    combo = QComboBox()
    for key, text in names.items():
        combo.addItem(i18n.tr(text), key)
    return combo


class PlotStyleEditor(QWidget):
    """Controls for one :class:`PlotStyle`; :attr:`styleChanged` carries the edited style."""

    styleChanged = Signal(object)

    def __init__(
        self,
        style: PlotStyle,
        default: Callable[[], PlotStyle],
        *,
        symbol_names: dict[str, str],
        line_names: dict[str, str],
        view_range: ViewRange | None = None,
        point_labels: bool = True,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._style = style
        self._default = default
        self._view_range = view_range
        self._loading = False
        self._loaders: list[Callable[[], None]] = []
        column = QVBoxLayout(self)
        column.setContentsMargins(0, 0, 0, 0)
        column.setSpacing(6)
        column.addWidget(self._labels_group())
        column.addWidget(self._axes_group())
        column.addWidget(self._range_group())
        column.addWidget(self._grid_group())
        column.addWidget(self._symbol_group(symbol_names))
        column.addWidget(self._line_group(line_names))
        if point_labels:
            column.addWidget(self._point_label_group())
        column.addWidget(self._legend_group())
        column.addWidget(self._colour_group())
        reset = QPushButton(QCoreApplication.translate("PHGX", "Reset to defaults"))
        reset.clicked.connect(self.reset)
        column.addWidget(reset)
        column.addStretch(1)
        self._load()

    # -- the style ------------------------------------------------------------
    def style(self) -> PlotStyle:
        return self._style

    def set_style(self, style: PlotStyle) -> None:
        self._style = style
        self._load()

    def reset(self) -> None:
        self.set_style(self._default())
        self.styleChanged.emit(self._style)

    def _load(self) -> None:
        self._loading = True
        try:
            for loader in self._loaders:
                loader()
        finally:
            self._loading = False

    def _edit(self, **changes: Any) -> None:
        if self._loading:
            return
        self._style = replace(self._style, **changes)
        self.styleChanged.emit(self._style)

    def _edit_axis(self, name: str, **changes: Any) -> None:
        if self._loading:
            return
        axis: AxisStyle = getattr(self._style, name)
        self._edit(**{name: replace(axis, **changes)})

    # -- groups ---------------------------------------------------------------
    def _form(self, title: str) -> tuple[QGroupBox, QGridLayout]:
        box = QGroupBox(title)  # i18n: as written
        grid = QGridLayout(box)
        grid.setContentsMargins(6, 6, 6, 6)
        grid.setHorizontalSpacing(6)
        grid.setVerticalSpacing(4)
        return box, grid

    def _row(self, grid: QGridLayout, text: str, *widgets: QWidget) -> None:
        row = grid.rowCount()
        grid.addWidget(QLabel(text), row, 0)  # i18n: as written
        for index, widget in enumerate(widgets):
            grid.addWidget(widget, row, 1 + index, 1, 1 if len(widgets) > 1 else 2)

    def _labels_group(self) -> QGroupBox:
        box, grid = self._form(QCoreApplication.translate("PHGX", "Title and labels"))
        title = QLineEdit()
        title.setPlaceholderText(QCoreApplication.translate("PHGX", "No title"))
        title.textEdited.connect(lambda text: self._edit(title=text))
        title_size = _spin(6, 32, " pt")
        title_size.valueChanged.connect(lambda v: self._edit(title_size=v))
        x_label, y_label = QLineEdit(), QLineEdit()
        for edit in (x_label, y_label):
            edit.setPlaceholderText(QCoreApplication.translate("PHGX", "Automatic"))
        x_label.textEdited.connect(lambda text: self._edit_axis("x", label=text))
        y_label.textEdited.connect(lambda text: self._edit_axis("y", label=text))
        label_size = _spin(6, 24, " pt")
        label_size.valueChanged.connect(lambda v: self._edit(label_size=v))
        self._row(grid, QCoreApplication.translate("PHGX", "Title"), title)
        self._row(grid, QCoreApplication.translate("PHGX", "Title size"), title_size)
        self._row(grid, QCoreApplication.translate("PHGX", "X-axis label"), x_label)
        self._row(grid, QCoreApplication.translate("PHGX", "Y-axis label"), y_label)
        self._row(grid, QCoreApplication.translate("PHGX", "Label size"), label_size)

        def load() -> None:
            style = self._style
            title.setText(style.title)  # i18n: as written
            title_size.setValue(style.title_size)
            x_label.setText(style.x.label)  # i18n: as written
            y_label.setText(style.y.label)  # i18n: as written
            label_size.setValue(style.label_size)

        self._loaders.append(load)
        return box

    def _axes_group(self) -> QGroupBox:
        box, grid = self._form(QCoreApplication.translate("PHGX", "Axes and ticks"))
        tick_size = _spin(5, 20, " pt")
        tick_size.valueChanged.connect(lambda v: self._edit(tick_size=v))
        tick_length = _spin(0, 15, " px")
        tick_length.valueChanged.connect(lambda v: self._edit(tick_length=v))
        inside = QCheckBox(QCoreApplication.translate("PHGX", "Ticks inside the plot"))
        inside.toggled.connect(lambda on: self._edit(ticks_inside=on))
        frame = QCheckBox(QCoreApplication.translate("PHGX", "Closed frame (top and right axes)"))
        frame.toggled.connect(lambda on: self._edit(frame=on))
        self._row(grid, QCoreApplication.translate("PHGX", "Tick label size"), tick_size)
        self._row(grid, QCoreApplication.translate("PHGX", "Tick length"), tick_length)
        grid.addWidget(inside, grid.rowCount(), 0, 1, 3)
        grid.addWidget(frame, grid.rowCount(), 0, 1, 3)
        aspect = _combo(ASPECTS)
        exaggeration = _double(0.1, 50.0, 0.5, 2)
        exaggeration.setSuffix(" \u00d7")
        exaggeration.setToolTip(QCoreApplication.translate("PHGX", "Vertical exaggeration of the plot"))
        aspect.currentIndexChanged.connect(lambda _i: self._edit(aspect=str(aspect.currentData())))
        exaggeration.valueChanged.connect(lambda v: self._edit(exaggeration=float(v)))
        self._row(grid, QCoreApplication.translate("PHGX", "Aspect"), aspect)
        self._row(grid, QCoreApplication.translate("PHGX", "Exaggeration"), exaggeration)

        def load() -> None:
            style = self._style
            tick_size.setValue(style.tick_size)
            tick_length.setValue(style.tick_length)
            inside.setChecked(style.ticks_inside)
            frame.setChecked(style.frame)
            aspect.setCurrentIndex(max(aspect.findData(style.aspect), 0))
            exaggeration.setValue(style.exaggeration)
            exaggeration.setEnabled(style.aspect == "exaggerated")

        aspect.currentIndexChanged.connect(
            lambda _i: exaggeration.setEnabled(aspect.currentData() == "exaggerated")
        )
        self._loaders.append(load)
        return box

    def _range_group(self) -> QGroupBox:
        box, grid = self._form(QCoreApplication.translate("PHGX", "Ranges and tick intervals"))
        controls: dict[
            str, tuple[QCheckBox, QDoubleSpinBox, QDoubleSpinBox, QDoubleSpinBox, QSpinBox, QCheckBox]
        ] = {}
        for name, title in (
            ("x", QCoreApplication.translate("PHGX", "X axis")),
            ("y", QCoreApplication.translate("PHGX", "Y axis")),
        ):
            auto = QCheckBox(QCoreApplication.translate("PHGX", "Automatic range"))
            low, high = _double(-1.0e9, 1.0e9, 10.0, 2), _double(-1.0e9, 1.0e9, 10.0, 2)
            major = _double(0.0, 1.0e8, 10.0, 2)
            major.setSpecialValueText(QCoreApplication.translate("PHGX", "Automatic"))
            minor = _spin(0, 10)
            minor.setSpecialValueText(QCoreApplication.translate("PHGX", "None"))
            minor.setToolTip(QCoreApplication.translate("PHGX", "Minor ticks: divisions of a major interval"))
            inverted = QCheckBox(QCoreApplication.translate("PHGX", "Reversed"))
            auto.toggled.connect(lambda on, n=name: self._edit_axis(n, auto_range=on))
            auto.toggled.connect(lambda on, a=low, b=high: (a.setEnabled(not on), b.setEnabled(not on)))
            low.valueChanged.connect(lambda v, n=name: self._edit_axis(n, minimum=float(v)))
            high.valueChanged.connect(lambda v, n=name: self._edit_axis(n, maximum=float(v)))
            major.valueChanged.connect(lambda v, n=name: self._edit_axis(n, major=float(v)))
            minor.valueChanged.connect(lambda v, n=name: self._edit_axis(n, minor_divisions=int(v)))
            inverted.toggled.connect(lambda on, n=name: self._edit_axis(n, inverted=on))
            heading = QLabel(f"<b>{title}</b>")  # i18n: as written
            grid.addWidget(heading, grid.rowCount(), 0, 1, 3)
            grid.addWidget(auto, grid.rowCount(), 0, 1, 3)
            grid.addWidget(inverted, grid.rowCount(), 0, 1, 3)
            self._row(grid, QCoreApplication.translate("PHGX", "From"), low)
            self._row(grid, QCoreApplication.translate("PHGX", "To"), high)
            self._row(grid, QCoreApplication.translate("PHGX", "Major interval"), major)
            self._row(grid, QCoreApplication.translate("PHGX", "Minor ticks"), minor)
            controls[name] = (auto, low, high, major, minor, inverted)
        take = QPushButton(QCoreApplication.translate("PHGX", "Use the view on screen"))
        take.setToolTip(QCoreApplication.translate("PHGX", "Fix both ranges to what the plot shows now"))
        take.clicked.connect(self._take_view)
        take.setEnabled(self._view_range is not None)
        grid.addWidget(take, grid.rowCount(), 0, 1, 3)

        def load() -> None:
            unit = f" {axis_units.get_length_unit()}"
            for name, (auto, low, high, major, minor, inverted) in controls.items():
                axis: AxisStyle = getattr(self._style, name)
                auto.setChecked(axis.auto_range)
                for spin, value in ((low, axis.minimum), (high, axis.maximum), (major, axis.major)):
                    spin.setSuffix(unit)  # i18n: as written
                    spin.setValue(value)
                low.setEnabled(not axis.auto_range)
                high.setEnabled(not axis.auto_range)
                minor.setValue(axis.minor_divisions)
                inverted.setChecked(axis.inverted)

        self._loaders.append(load)
        return box

    def _take_view(self) -> None:
        if self._view_range is None:
            return
        factor = axis_units.length_factor()
        x0, x1, y0, y1 = (value * factor for value in self._view_range())
        x = replace(self._style.x, auto_range=False, minimum=round(x0, 2), maximum=round(x1, 2))
        y = replace(self._style.y, auto_range=False, minimum=round(y0, 2), maximum=round(y1, 2))
        self._style = replace(self._style, x=x, y=y)
        self._load()
        self.styleChanged.emit(self._style)

    def _grid_group(self) -> QGroupBox:
        box, grid = self._form(QCoreApplication.translate("PHGX", "Grid"))
        grid_x = QCheckBox(QCoreApplication.translate("PHGX", "Vertical lines"))
        grid_y = QCheckBox(QCoreApplication.translate("PHGX", "Horizontal lines"))
        opacity = _spin(0, 100, " %")
        grid_x.toggled.connect(lambda on: self._edit(grid_x=on))
        grid_y.toggled.connect(lambda on: self._edit(grid_y=on))
        opacity.valueChanged.connect(lambda v: self._edit(grid_opacity=v / 100.0))
        row = grid.rowCount()
        grid.addWidget(grid_x, row, 0, 1, 2)
        grid.addWidget(grid_y, row, 2)
        self._row(grid, QCoreApplication.translate("PHGX", "Opacity"), opacity)

        def load() -> None:
            grid_x.setChecked(self._style.grid_x)
            grid_y.setChecked(self._style.grid_y)
            opacity.setValue(round(self._style.grid_opacity * 100))

        self._loaders.append(load)
        return box

    def _symbol_group(self, names: dict[str, str]) -> QGroupBox:
        box, grid = self._form(QCoreApplication.translate("PHGX", "Symbols"))
        element = _combo(names)
        shape = _combo(SYMBOLS)
        size = _double(1.0, 60.0, 1.0, 1)
        size.setSuffix(" px")  # i18n: as written
        fill = ColourButton(empty_text=QCoreApplication.translate("PHGX", "Hollow"))
        edge = ColourButton(empty_text=QCoreApplication.translate("PHGX", "No edge"))
        edge_width = _double(0.0, 8.0, 0.2, 1)
        edge_width.setSuffix(" px")  # i18n: as written
        self._row(grid, QCoreApplication.translate("PHGX", "Element"), element)
        self._row(grid, QCoreApplication.translate("PHGX", "Shape"), shape)
        self._row(grid, QCoreApplication.translate("PHGX", "Size"), size)
        self._row(grid, QCoreApplication.translate("PHGX", "Fill"), fill)
        self._row(grid, QCoreApplication.translate("PHGX", "Edge"), edge, edge_width)

        def current() -> SymbolStyle:
            return self._style.symbol(str(element.currentData()))

        def edit(**changes: Any) -> None:
            if self._loading:
                return
            key = str(element.currentData())
            symbols = dict(self._style.symbols)
            symbols[key] = replace(current(), **changes)
            self._edit(symbols=symbols)

        def load() -> None:
            was = self._loading
            self._loading = True
            symbol = current()
            shape.setCurrentIndex(max(shape.findData(symbol.symbol), 0))
            size.setValue(symbol.size)
            fill.set_colour(symbol.fill)
            edge.set_colour(symbol.edge)
            edge_width.setValue(symbol.edge_width)
            self._loading = was

        element.currentIndexChanged.connect(lambda _i: load())
        shape.currentIndexChanged.connect(lambda _i: edit(symbol=str(shape.currentData())))
        size.valueChanged.connect(lambda v: edit(size=float(v)))
        fill.colourChanged.connect(lambda c: edit(fill=c))
        edge.colourChanged.connect(lambda c: edit(edge=c))
        edge_width.valueChanged.connect(lambda v: edit(edge_width=float(v)))
        self._loaders.append(load)
        return box

    def _line_group(self, names: dict[str, str]) -> QGroupBox:
        box, grid = self._form(QCoreApplication.translate("PHGX", "Lines"))
        element = _combo(names)
        colour = ColourButton()
        width = _double(0.2, 10.0, 0.2, 1)
        width.setSuffix(" px")  # i18n: as written
        dash = _combo(DASHES)
        self._row(grid, QCoreApplication.translate("PHGX", "Element"), element)
        self._row(grid, QCoreApplication.translate("PHGX", "Colour"), colour)
        self._row(grid, QCoreApplication.translate("PHGX", "Width"), width)
        self._row(grid, QCoreApplication.translate("PHGX", "Style"), dash)

        def current() -> LineStyle:
            return self._style.line(str(element.currentData()))

        def edit(**changes: Any) -> None:
            if self._loading:
                return
            lines = dict(self._style.lines)
            lines[str(element.currentData())] = replace(current(), **changes)
            self._edit(lines=lines)

        def load() -> None:
            was = self._loading
            self._loading = True
            line = current()
            colour.set_colour(line.colour)
            width.setValue(line.width)
            dash.setCurrentIndex(max(dash.findData(line.dash), 0))
            self._loading = was

        element.currentIndexChanged.connect(lambda _i: load())
        colour.colourChanged.connect(lambda c: edit(colour=c))
        width.valueChanged.connect(lambda v: edit(width=float(v)))
        dash.currentIndexChanged.connect(lambda _i: edit(dash=str(dash.currentData())))
        self._loaders.append(load)
        return box

    def _point_label_group(self) -> QGroupBox:
        box, grid = self._form(QCoreApplication.translate("PHGX", "Point labels"))
        show = QCheckBox(QCoreApplication.translate("PHGX", "Label electrodes and stations"))
        every = _spin(1, 100)
        every.setPrefix(QCoreApplication.translate("PHGX", "every "))
        size = _spin(5, 20, " pt")
        show.toggled.connect(lambda on: self._edit(point_labels=on))
        every.valueChanged.connect(lambda v: self._edit(label_every=v))
        size.valueChanged.connect(lambda v: self._edit(point_label_size=v))
        grid.addWidget(show, grid.rowCount(), 0, 1, 3)
        self._row(grid, QCoreApplication.translate("PHGX", "Spacing"), every)
        self._row(grid, QCoreApplication.translate("PHGX", "Size"), size)

        def load() -> None:
            show.setChecked(self._style.point_labels)
            every.setValue(self._style.label_every)
            size.setValue(self._style.point_label_size)

        self._loaders.append(load)
        return box

    def _legend_group(self) -> QGroupBox:
        box, grid = self._form(QCoreApplication.translate("PHGX", "Legend and colour bar"))
        show = QCheckBox(QCoreApplication.translate("PHGX", "Legend"))
        corner = _combo(CORNERS)
        size = _spin(5, 20, " pt")
        frame = QCheckBox(QCoreApplication.translate("PHGX", "Framed"))
        columns = _spin(1, 4)
        bar = QCheckBox(QCoreApplication.translate("PHGX", "Colour bar"))
        bar_label = QLineEdit()
        bar_label.setPlaceholderText(QCoreApplication.translate("PHGX", "Automatic"))
        show.toggled.connect(lambda on: self._edit(legend=on))
        corner.currentIndexChanged.connect(lambda _i: self._edit(legend_corner=str(corner.currentData())))
        size.valueChanged.connect(lambda v: self._edit(legend_size=v))
        frame.toggled.connect(lambda on: self._edit(legend_frame=on))
        columns.valueChanged.connect(lambda v: self._edit(legend_columns=v))
        bar.toggled.connect(lambda on: self._edit(colour_bar=on))
        bar_label.textEdited.connect(lambda text: self._edit(colour_bar_label=text))
        row = grid.rowCount()
        grid.addWidget(show, row, 0, 1, 2)
        grid.addWidget(frame, row, 2)
        self._row(grid, QCoreApplication.translate("PHGX", "Position"), corner)
        self._row(grid, QCoreApplication.translate("PHGX", "Text size"), size)
        self._row(grid, QCoreApplication.translate("PHGX", "Columns"), columns)
        grid.addWidget(bar, grid.rowCount(), 0, 1, 3)
        self._row(grid, QCoreApplication.translate("PHGX", "Colour bar title"), bar_label)

        def load() -> None:
            style = self._style
            show.setChecked(style.legend)
            corner.setCurrentIndex(max(corner.findData(style.legend_corner), 0))
            size.setValue(style.legend_size)
            frame.setChecked(style.legend_frame)
            columns.setValue(style.legend_columns)
            bar.setChecked(style.colour_bar)
            bar_label.setText(style.colour_bar_label)  # i18n: as written

        self._loaders.append(load)
        return box

    def _colour_group(self) -> QGroupBox:
        box, grid = self._form(QCoreApplication.translate("PHGX", "Colours"))
        theme_text = QCoreApplication.translate("PHGX", "Appearance")
        background = ColourButton(empty_text=theme_text)
        foreground = ColourButton(empty_text=theme_text)
        background.colourChanged.connect(lambda c: self._edit(background=c))
        foreground.colourChanged.connect(lambda c: self._edit(foreground=c))
        self._row(grid, QCoreApplication.translate("PHGX", "Background"), background)
        self._row(grid, QCoreApplication.translate("PHGX", "Axes and text"), foreground)

        def load() -> None:
            background.set_colour(self._style.background)
            foreground.set_colour(self._style.foreground)

        self._loaders.append(load)
        return box


class TwoDOptions(CollapsiblePanel):
    """The folding panel beside the plan and section, one :class:`PlotStyleEditor` tab per plot."""

    def __init__(self, view: str, parent: QWidget | None = None) -> None:
        super().__init__(QCoreApplication.translate("PHGX", "2D options"), view, parent)
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.body_layout.addWidget(self.tabs)
        self.editors: dict[str, PlotStyleEditor] = {}

    def add_editor(self, key: str, title: str, editor: PlotStyleEditor) -> None:
        self.editors[key] = editor
        self.tabs.addTab(editor, title)  # i18n: as written

    def show_editor(self, key: str) -> None:
        editor = self.editors.get(key)
        if editor is not None:
            self.tabs.setCurrentWidget(editor)


__all__ = ["ColourButton", "PlotStyleEditor", "TwoDOptions", "ViewRange"]
