"""How the curves of a :class:`~PyHydroGeophysX.survey.traces.TraceCollection` are told apart.

Colour and line style are indices, so a Qt view and a matplotlib figure draw the
same curve the same way. One group: colour by channel, solid. One channel:
colour by group. Several of each: colour by channel and line style by group,
up to four styles; beyond that every curve gets its own colour.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np

from PyHydroGeophysX.survey.layout import Key
from PyHydroGeophysX.survey.traces import TraceCollection, Window

#: The same series colours as ``qt_apps.theme.SERIES_COLORS`` (kept equal by a test).
COLOURS: tuple[str, ...] = (
    "#007aff",
    "#ff9500",
    "#34c759",
    "#ff3b30",
    "#af52de",
    "#30b0c7",
    "#a2845e",
    "#ff2d55",
)
#: Matplotlib line styles, in the order of :attr:`SeriesStyle.dash`.
DASHES: tuple[str, ...] = ("-", "--", ":", "-.")
#: Groups that still get a line style of their own; more than this and each curve is coloured alone.
MAX_DASH_GROUPS = 4


@dataclass(frozen=True)
class SeriesStyle:
    """One drawn curve."""

    colour: int
    dash: int
    label: str
    group: str
    channel: str
    key: Key


def encode(collection: TraceCollection) -> tuple[SeriesStyle, ...]:
    """A style per curve of ``collection``, in draw order."""
    sets = collection.sets
    channels: list[str] = []
    for item in sets:
        for name in item.channels:
            if name not in channels:
                channels.append(name)
    several_groups = len(sets) > 1
    one_channel = len(channels) <= 1
    own_colour = several_groups and not one_channel and len(sets) > MAX_DASH_GROUPS
    styles: list[SeriesStyle] = []
    flat = 0
    for group_index, item in enumerate(sets):
        for row, channel in enumerate(item.channels):
            if not several_groups:
                colour, dash = channels.index(channel), 0
            elif one_channel:
                colour, dash = group_index, 0
            elif own_colour:
                colour, dash = flat, 0
            else:
                colour, dash = channels.index(channel), group_index
            label = item.labels[row]
            if several_groups:
                label = f"{item.group} · {label}"
            key: Key = item.keys[row] if item.keys else ("trace", item.group, channel)
            styles.append(SeriesStyle(colour, dash, label, item.group, channel, key))
            flat += 1
    return tuple(styles)


def window_mask(t: np.ndarray, window: Window | None) -> np.ndarray:
    """Samples of ``t`` inside ``window`` (all of them when there is no window)."""
    if window is None:
        return np.ones(t.size, dtype=bool)
    return np.asarray((t >= window.start) & (t <= window.end), dtype=bool)


#: Below this fraction of the mean absolute value, a window's signed mean counts as zero.
SIGNED_MEAN_FLOOR = 1e-3


def normalized(values: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """Each row divided by its signed mean on ``mask``: V/Vp over the steady on-time.

    The sign makes a reversed primary (the source on the other side of the
    receiver) give the same ratio. A window whose mean is about zero (it crosses
    zero, like a noise window) divides by its mean absolute value instead, and
    a row that is zero there is left as it is.
    """
    used = mask if mask.any() else np.ones(values.shape[1], dtype=bool)
    with np.errstate(invalid="ignore"):
        signed = np.nanmean(values[:, used], axis=1)
        absolute = np.nanmean(np.abs(values[:, used]), axis=1)
    ok_abs = np.isfinite(absolute) & (absolute > 0)
    ok_signed = ok_abs & np.isfinite(signed) & (np.abs(signed) > SIGNED_MEAN_FLOOR * absolute)
    scale = np.where(ok_signed, signed, np.where(ok_abs, absolute, 1.0))
    return values / scale[:, None]


def percentile_band(
    curves: Sequence[tuple[np.ndarray, np.ndarray]], grid: np.ndarray
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """``(median, 10th, 90th)`` of ``curves`` (each ``(time, values)``) resampled onto ``grid``."""
    stack = np.vstack([np.interp(grid, time, values, left=np.nan, right=np.nan) for time, values in curves])
    return (
        np.nanmedian(stack, axis=0),
        np.nanpercentile(stack, 10, axis=0),
        np.nanpercentile(stack, 90, axis=0),
    )


__all__ = [
    "COLOURS",
    "DASHES",
    "MAX_DASH_GROUPS",
    "SIGNED_MEAN_FLOOR",
    "SeriesStyle",
    "encode",
    "normalized",
    "percentile_band",
    "window_mask",
]
