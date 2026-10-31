"""Data rejected by hand, applied before an inversion (plan M4.4).

The Studio's QC panels record rejections by the item's own coordinate, not by
a row of some table: an EM gate by its moment and centre time, an MT estimate
by its frequency. These helpers take those records off a copy of the data the
inversion receives. A value matches within a relative tolerance, so a time
read back from JSON still finds its gate.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

import numpy as np

#: Relative tolerance of a recorded time or frequency against the data's.
TOLERANCE = 1e-6


def _matches(values: np.ndarray, rejected: Iterable[float]) -> np.ndarray:
    """True where ``values`` equals one of ``rejected`` within :data:`TOLERANCE`."""
    marks = np.zeros(values.shape, dtype=bool)
    for target in rejected:
        marks |= np.isclose(values, float(target), rtol=TOLERANCE, atol=0.0)
    return marks


def _drop(block: Mapping[str, Any], axis_key: str, rejected: Iterable[float]) -> tuple[dict[str, Any], int]:
    """``block`` without the entries whose ``axis_key`` value was rejected; also how many went."""
    axis = np.asarray(block[axis_key], dtype=float)
    keep = ~_matches(axis, rejected)
    out: dict[str, Any] = {}
    for key, value in block.items():
        same_axis = isinstance(value, np.ndarray) and value.shape[:1] == axis.shape
        out[key] = value[keep] if same_axis else value
    return out, int((~keep).sum())


def drop_rejected_em(
    data: Mapping[str, Any], rejected: Mapping[str, Iterable[float]]
) -> tuple[dict[str, Any], int]:
    """A copy of an EM sounding without the gates (or frequencies) rejected by hand.

    ``rejected`` maps a moment ("LM", "HM") to the centre times, in seconds,
    of its rejected gates; a single-moment TDEM sounding uses the key "" or
    its moment, and an FDEM sounding the key "FDEM" with frequencies in Hz.
    Returns the copy and the number of values removed.
    """
    copy = dict(data)
    removed = 0
    if "moments" in copy and isinstance(copy["moments"], Mapping):
        moments = {}
        for name, block in copy["moments"].items():
            values = list(rejected.get(str(name), ()))
            moments[name], count = _drop(block, "times", values) if values else (dict(block), 0)
            removed += count
        copy["moments"] = moments
    elif "times" in copy:
        names = ("", "TDEM", str(copy.get("tem_moment", "")))
        values = [t for key, times in rejected.items() if key in names for t in times]
        if values:
            copy, removed = _drop(copy, "times", values)
    elif "frequencies" in copy:
        values = list(rejected.get("FDEM", ()))
        if values:
            copy, removed = _drop(copy, "frequencies", values)
    return copy, removed


def blank_rejected_mt(tf: Any, frequencies: Iterable[float]) -> tuple[Any, int]:
    """A copy of an MT transfer function with the estimates at ``frequencies`` set to NaN (missing)."""
    import dataclasses

    values = list(frequencies)
    if not values:
        return tf, 0
    marks = _matches(np.asarray(tf.frequency, dtype=float), values)
    changes: dict[str, Any] = {}
    for name in ("z", "z_err", "tipper", "tipper_err"):
        array = getattr(tf, name)
        if array is not None:
            blanked = np.array(array, copy=True)
            blanked[marks] = np.nan
            changes[name] = blanked
    return dataclasses.replace(tf, **changes), int(marks.sum())


__all__ = ["TOLERANCE", "blank_rejected_mt", "drop_rejected_em"]
