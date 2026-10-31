"""Industry figure style: fonts, axes, colour bars, scale bar, north arrow, title block (plan M4.3).

Figures for reports follow one convention: a CJK font when the labels are
Chinese (TrueType embedded in PDF, so the text stays text), ticks inward,
units on every axis and colour bar, a scale bar on sections and maps, and a
title block (图签) with what a reviewer needs to identify the figure.
Nothing here needs Qt.
"""

from __future__ import annotations

from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from typing import Any

import numpy as np

#: CJK fonts tried in order, by the names Matplotlib knows them by.
CJK_FONTS = (
    "PingFang SC",
    "Hiragino Sans GB",
    "Heiti SC",
    "STHeiti",
    "Songti SC",
    "Microsoft YaHei",
    "SimHei",
    "Noto Sans CJK SC",
    "Source Han Sans SC",
    "WenQuanYi Micro Hei",
    "Arial Unicode MS",
)

#: Axis and block labels in each language.
LABELS: dict[str, dict[str, str]] = {
    "zh": {
        "distance": "距离",
        "depth": "深度",
        "elevation": "高程",
        "x": "x",
        "y": "y",
        "z": "高程",
        "pseudo_depth": "伪深度",
        "apparent_resistivity": "视电阻率",
        "masked": "遮罩",
        "title": "图名",
        "project": "工程",
        "line": "测线",
        "method": "方法",
        "date": "日期",
        "scale": "比例",
        "crs": "坐标系",
        "drawn_by": "制图",
        "software": "软件",
        "north": "N",
    },
    "en": {
        "distance": "Distance",
        "depth": "Depth",
        "elevation": "Elevation",
        "x": "x",
        "y": "y",
        "z": "Elevation",
        "pseudo_depth": "Pseudo-depth",
        "apparent_resistivity": "Apparent resistivity",
        "masked": "Masked",
        "title": "Title",
        "project": "Project",
        "line": "Line",
        "method": "Method",
        "date": "Date",
        "scale": "Scale",
        "crs": "CRS",
        "drawn_by": "Drawn by",
        "software": "Software",
        "north": "N",
    },
}
#: Order of the title block's rows.
TITLE_BLOCK_FIELDS = ("title", "project", "line", "method", "date", "scale", "crs", "drawn_by", "software")
#: Parameter names in each language, for colour-bar labels.
PARAMETER_NAMES: dict[str, dict[str, str]] = {
    "zh": {
        "resistivity": "电阻率",
        "conductivity": "电导率",
        "velocity": "速度",
        "density_contrast": "密度差",
        "susceptibility": "磁化率",
        "m": "极化率",
        "rho0": "零频电阻率",
        "tau": "时间常数",
        "c": "频率相关系数",
        "water_content": "含水量",
    },
    "en": {
        "resistivity": "Resistivity",
        "conductivity": "Conductivity",
        "velocity": "Velocity",
        "density_contrast": "Density contrast",
        "susceptibility": "Susceptibility",
        "m": "Chargeability",
        "rho0": "DC resistivity",
        "tau": "Time constant",
        "c": "Frequency exponent",
        "water_content": "Water content",
    },
}


def labels(language: str) -> dict[str, str]:
    return LABELS["zh" if language.lower().startswith("zh") else "en"]


def parameter_label(name: str, unit: str, language: str, *, log_scale: bool = False) -> str:
    """``电阻率 (ohm.m)``; ``log10`` noted when the colours are logarithmic."""
    names = PARAMETER_NAMES["zh" if language.lower().startswith("zh") else "en"]
    base = name.split("_step")[0]
    text = names.get(base, name)
    return f"{text} ({unit})" + (" [log10]" if log_scale else "")


def cjk_fonts() -> list[str]:
    """The CJK fonts of :data:`CJK_FONTS` Matplotlib can use here."""
    from matplotlib import font_manager

    known = {entry.name for entry in font_manager.fontManager.ttflist}
    return [name for name in CJK_FONTS if name in known]


def publication_rc(language: str = "zh") -> dict[str, Any]:
    """rcParams of a report figure."""
    import matplotlib as mpl

    rc: dict[str, Any] = {
        "figure.dpi": 100,
        "savefig.dpi": 300,
        "savefig.bbox": "tight",
        "savefig.facecolor": "white",
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "font.size": 9,
        "axes.labelsize": 10,
        "axes.titlesize": 11,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        "xtick.direction": "in",
        "ytick.direction": "in",
        "xtick.top": True,
        "ytick.right": True,
        "axes.linewidth": 0.8,
        "axes.grid": False,
        "legend.frameon": False,
        "text.color": "black",
        "axes.labelcolor": "black",
        "xtick.color": "black",
        "ytick.color": "black",
        "axes.edgecolor": "black",
    }
    if language.lower().startswith("zh"):
        fonts = cjk_fonts()
        if fonts:
            sans = [name for name in mpl.rcParams["font.sans-serif"] if name not in fonts]
            rc.update(
                {"font.family": "sans-serif", "font.sans-serif": fonts + sans, "axes.unicode_minus": False}
            )
    return rc


@contextmanager
def publication_style(language: str = "zh") -> Iterator[None]:
    """Draw with :func:`publication_rc` inside the block; the Studio's own style comes back after."""
    import matplotlib as mpl

    settings: Any = publication_rc(language)
    with mpl.rc_context(settings):
        yield


def nice_length(span: float) -> float:
    """A round scale-bar length near a fifth of ``span``: 1, 2 or 5 times a power of ten."""
    target = abs(float(span)) / 5.0
    if target <= 0 or not np.isfinite(target):
        return 1.0
    power = 10.0 ** np.floor(np.log10(target))
    for step in (1.0, 2.0, 5.0, 10.0):
        if step * power >= target * 0.75:
            return float(step * power)
    return float(10.0 * power)


def add_scale_bar(
    ax: Any, *, length: float | None = None, unit: str = "m", location: str = "lower right"
) -> float:
    """A scale bar in data units (equal-aspect sections and maps); returns its length."""
    x0, x1 = ax.get_xlim()
    y0, y1 = ax.get_ylim()
    bar = float(length) if length else nice_length(x1 - x0)
    # get_ylim is (bottom, top) as drawn, so this holds on a depth axis pointing down too.
    pad_x, rise = 0.04 * (x1 - x0), (y1 - y0)
    right = location.endswith("right")
    start = (x1 - pad_x - bar) if right else (x0 + pad_x)
    base = (y0 + 0.06 * rise) if location.startswith("lower") else (y1 - 0.12 * rise)
    ax.plot([start, start + bar], [base, base], color="black", linewidth=2.0, solid_capstyle="butt", zorder=5)
    label = f"{bar:g} {unit}"
    ax.text(start + bar / 2, base + 0.02 * rise, label, ha="center", va="bottom", fontsize=8, zorder=5)
    return bar


def add_north_arrow(ax: Any, *, x: float = 0.95, y: float = 0.88, language: str = "zh") -> None:
    """A north arrow at axes fraction ``(x, y)`` for maps."""
    ax.annotate(
        labels(language)["north"],
        xy=(x, y),
        xytext=(x, y - 0.12),
        xycoords="axes fraction",
        ha="center",
        va="center",
        fontsize=10,
        fontweight="bold",
        arrowprops={"arrowstyle": "-|>", "color": "black", "lw": 1.2},
    )


def add_colorbar(fig: Any, ax: Any, mappable: Any, label: str, *, log_scale: bool = False) -> Any:
    """A colour bar beside ``ax``; with ``log_scale`` the ticks show the values, not their logarithms."""
    bar = fig.colorbar(mappable, ax=ax, fraction=0.04, pad=0.02)
    bar.set_label(label)
    if log_scale:
        lo, hi = bar.mappable.get_clim()
        ticks = np.arange(np.floor(lo * 2) / 2, np.ceil(hi * 2) / 2 + 0.01, 0.5)
        ticks = ticks[(ticks >= lo - 1e-9) & (ticks <= hi + 1e-9)]
        if ticks.size >= 2:
            bar.set_ticks(ticks)
            bar.set_ticklabels([f"{10.0**t:.3g}" for t in ticks])
    bar.outline.set_linewidth(0.8)
    return bar


def add_title_block(fig: Any, fields: Mapping[str, str], *, language: str = "zh") -> Any:
    """The title block (图签) at the figure's lower right: one row per field given, in a fixed order."""
    names = labels(language)
    rows = [(names[key], str(fields[key])) for key in TITLE_BLOCK_FIELDS if fields.get(key)]
    rows += [
        (str(key), str(value)) for key, value in fields.items() if key not in TITLE_BLOCK_FIELDS and value
    ]
    if not rows:
        return None
    height = 0.035 * len(rows)
    block = fig.add_axes((0.62, 0.0 - height - 0.02, 0.36, height))
    block.axis("off")
    table = block.table(
        cellText=[[k, v] for k, v in rows], colWidths=[0.28, 0.72], loc="center", cellLoc="left"
    )
    table.auto_set_font_size(False)
    table.set_fontsize(8)
    for cell in table.get_celld().values():
        cell.set_linewidth(0.6)
    return block


__all__ = [
    "CJK_FONTS",
    "LABELS",
    "TITLE_BLOCK_FIELDS",
    "add_colorbar",
    "add_north_arrow",
    "add_scale_bar",
    "add_title_block",
    "cjk_fonts",
    "labels",
    "nice_length",
    "parameter_label",
    "publication_rc",
    "publication_style",
]
