"""Trace collections and the colour/line encoding of several groups at once."""

from __future__ import annotations

import numpy as np
import pytest

from PyHydroGeophysX.survey.series import encode, normalized, percentile_band
from PyHydroGeophysX.survey.traces import TraceCollection, TraceSet, Window


def _set(
    group: str, channels: tuple[str, ...], *, origin: float | None = None, scale: float = 1.0
) -> TraceSet:
    t = np.array([0.0, 1.0, 2.0, 3.0])
    values = np.vstack([scale * (row + 1) * np.ones(4) for row in range(len(channels))])
    return TraceSet(
        t,
        values,
        channels,
        labels=channels,
        keys=tuple(("trace", group, name) for name in channels),
        group=group,
        origin=origin,
        windows=(Window("On", 1.0, 2.0, "on"),),
    )


def test_a_collection_rejects_a_missing_or_repeated_group() -> None:
    bare = TraceSet(np.array([0.0, 1.0]), np.ones((1, 2)), ("a",))
    with pytest.raises(ValueError, match="group"):
        TraceCollection((bare,))
    one = _set("s1", ("a",))
    with pytest.raises(ValueError, match="duplicate"):
        TraceCollection((one, one))


def test_single_wraps_a_set_that_has_no_group() -> None:
    bare = TraceSet(np.array([0.0, 1.0]), np.array([[2.0, 3.0]]), ("a",), labels=("A",))
    collection = TraceCollection.single(bare)
    assert collection.focus == "group" and collection.size == 1
    assert collection.focus_set() is not None and collection.focus_set().group == "group"
    assert collection.pairs() == (("group", "a", ("trace", "group", "a")),)


def test_encode_colours_channels_groups_or_every_curve() -> None:
    one = TraceCollection((_set("s1", ("a", "b")),), focus="s1")
    assert [style.dash for style in encode(one)] == [0, 0]
    assert [style.colour for style in encode(one)] == [0, 1]
    assert [style.label for style in encode(one)] == ["a", "b"]

    by_group = TraceCollection((_set("s1", ("a",)), _set("s2", ("a",))), focus="s1")
    styles = encode(by_group)
    assert [style.colour for style in styles] == [0, 1]
    assert styles[1].label == "s2 · a"

    both = TraceCollection((_set("s1", ("a", "b")), _set("s2", ("a", "b"))), focus="s1")
    styles = encode(both)
    assert [(style.colour, style.dash) for style in styles] == [(0, 0), (1, 0), (0, 1), (1, 1)]

    many = TraceCollection(tuple(_set(f"s{i}", ("a", "b")) for i in range(5)), focus="s0")
    styles = encode(many)
    assert [style.colour for style in styles] == list(range(10))
    assert {style.dash for style in styles} == {0}


def test_normalising_uses_the_window_mean_and_the_band_resamples() -> None:
    values = np.array([[0.0, 2.0, 2.0, 0.0], [0.0, 4.0, 4.0, 0.0]])
    mask = np.array([False, True, True, False])
    out = normalized(values, mask)
    assert out[:, 1] == pytest.approx([1.0, 1.0])
    grid = np.array([0.0, 1.0])
    median, low, high = percentile_band(
        ((np.array([0.0, 1.0]), np.array([0.0, 2.0])), (np.array([0.0, 1.0]), np.array([0.0, 4.0]))),
        grid,
    )
    assert median[1] == pytest.approx(3.0)
    assert low[1] == pytest.approx(2.2) and high[1] == pytest.approx(3.8)


def test_series_colours_match_the_studio_palette() -> None:
    from PyHydroGeophysX.qt_apps.theme import SERIES_COLORS
    from PyHydroGeophysX.survey.series import COLOURS

    assert COLOURS == SERIES_COLORS
