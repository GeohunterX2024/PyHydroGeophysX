"""Recorded curves of one group (a shot, a site's run): channels on a common time axis.

A :class:`TraceSet` carries the channels, an optional reference curve on its
own axis (the transmitter current of a DC/IP shot), and named time windows
(on-time, off-time, gates) that the curve and spectrum views offer and shade.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np
from numpy.typing import ArrayLike

from PyHydroGeophysX.survey.layout import BoolArray, FloatArray, Key

#: Window kinds the views know how to shade.
WINDOW_KINDS = ("record", "on", "off", "gate", "signal", "noise")


@dataclass(frozen=True)
class Window:
    """A named stretch of the time axis, ``start`` to ``end`` in the axis' units (s)."""

    name: str
    start: float
    end: float
    kind: str = "record"

    def __post_init__(self) -> None:
        if self.kind not in WINDOW_KINDS:
            raise ValueError(f"unknown window kind {self.kind!r}; expected one of {WINDOW_KINDS}")
        if not self.end > self.start:
            raise ValueError(f"window {self.name!r} ends ({self.end}) before it starts ({self.start})")


@dataclass(frozen=True)
class TraceSet:
    """Channels ``values`` (n_channels, n_samples) sampled at ``t`` (s)."""

    t: FloatArray
    values: FloatArray
    channels: tuple[str, ...]
    unit: str = ""
    labels: tuple[str, ...] = ()
    keys: tuple[Key, ...] = ()
    reference: FloatArray | None = None
    reference_label: str = ""
    reference_unit: str = ""
    windows: tuple[Window, ...] = ()
    title: str = ""
    line_frequency: float | None = None

    def __post_init__(self) -> None:
        t = np.asarray(self.t, dtype=np.float64).ravel()
        values = np.atleast_2d(np.asarray(self.values, dtype=np.float64))
        if values.size == 0:
            values = np.zeros((0, t.size))
        if values.shape[1] != t.size:
            raise ValueError(f"values have {values.shape[1]} samples for a time axis of {t.size}")
        if len(self.channels) != values.shape[0]:
            raise ValueError(f"{len(self.channels)} channel names for {values.shape[0]} channels")
        labels = tuple(self.labels) if self.labels else tuple(self.channels)
        if len(labels) != values.shape[0]:
            raise ValueError("one label per channel")
        if self.keys and len(self.keys) != values.shape[0]:
            raise ValueError("one key per channel")
        if self.reference is not None:
            reference = np.asarray(self.reference, dtype=np.float64).ravel()
            if reference.size != t.size:
                raise ValueError("the reference curve needs one value per sample")
            object.__setattr__(self, "reference", reference)
        object.__setattr__(self, "t", t)
        object.__setattr__(self, "values", values)
        object.__setattr__(self, "channels", tuple(self.channels))
        object.__setattr__(self, "labels", labels)
        object.__setattr__(self, "windows", tuple(self.windows))

    @property
    def size(self) -> int:
        return int(self.values.shape[0])

    @property
    def sample_rate(self) -> float:
        """Samples per second, from the median step of the time axis (0 for fewer than 2 samples)."""
        if self.t.size < 2:
            return 0.0
        step = float(np.median(np.diff(self.t)))
        return 1.0 / step if step > 0 else 0.0

    def window(self, name: str) -> Window | None:
        return next((w for w in self.windows if w.name == name), None)

    def mask(self, window: Window | None) -> BoolArray:
        """Samples inside ``window`` (all of them for None)."""
        if window is None:
            return np.ones(self.t.size, bool)
        return np.asarray((self.t >= window.start) & (self.t <= window.end), dtype=bool)

    def select(self, channels: Sequence[str]) -> TraceSet:
        """The same set restricted to ``channels`` (in their order, unknown names skipped)."""
        index = {name: i for i, name in enumerate(self.channels)}
        rows = [index[name] for name in channels if name in index]
        return TraceSet(
            self.t,
            self.values[rows] if rows else np.zeros((0, self.t.size)),
            tuple(self.channels[i] for i in rows),
            self.unit,
            tuple(self.labels[i] for i in rows),
            tuple(self.keys[i] for i in rows) if self.keys else (),
            self.reference,
            self.reference_label,
            self.reference_unit,
            self.windows,
            self.title,
            self.line_frequency,
        )


def windows_from_cycle(on_seconds: float, off_seconds: float, *, settle: float = 0.2) -> tuple[Window, ...]:
    """Record, on-time, end of on-time and off-time windows of one transmitter cycle.

    The steady on-time leaves out ``settle`` seconds after switching on and
    before switching off; the off-time starts ``settle`` after the turn-off.
    """
    total = float(on_seconds) + float(off_seconds)
    windows = [Window("Whole record", 0.0, total, "record")]
    if on_seconds > 2 * settle:
        windows.append(Window("On-time (steady)", settle, on_seconds - settle, "on"))
        windows.append(Window("End of on-time", max(on_seconds - 1.2, settle), on_seconds + 0.2, "signal"))
    if off_seconds > settle:
        windows.append(Window("Off-time", on_seconds + settle, total, "off"))
    return tuple(windows)


def as_trace_values(values: ArrayLike, n_samples: int) -> FloatArray:
    """``values`` as (channels, samples), transposing a (samples, channels) array."""
    array = np.atleast_2d(np.asarray(values, dtype=np.float64))
    if array.shape[0] == n_samples and array.shape[1] != n_samples:
        array = array.T
    return np.asarray(array, dtype=np.float64)


__all__ = ["WINDOW_KINDS", "TraceSet", "Window", "as_trace_values", "windows_from_cycle"]
