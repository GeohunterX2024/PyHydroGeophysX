"""SpectrumCache gives what trace_spectrum and noise_metrics give, and only recomputes what changed."""

from __future__ import annotations

from dataclasses import replace

import numpy as np

from PyHydroGeophysX.survey.spectra import NoiseMetrics, SpectrumCache, noise_metrics, trace_spectrum
from PyHydroGeophysX.survey.traces import TraceSet, windows_from_cycle


def _traces(channels: int = 6, seed: int = 0) -> TraceSet:
    rng = np.random.default_rng(seed)
    t = np.arange(3000) / 250.0
    hum = np.sin(2 * np.pi * 50.0 * t)
    step = np.where(t < 6.0, 1.0, 0.0)
    values = step + 0.05 * hum + 0.01 * rng.normal(size=(channels, t.size))
    names = tuple(f"ch{i}" for i in range(channels))
    return TraceSet(
        t,
        values,
        names,
        keys=tuple(("trace", "s1", i, 1) for i in range(channels)),
        reference=step * 2.0,
        windows=windows_from_cycle(6.0, 6.0),
        group="s1",
    )


def _windows(traces: TraceSet) -> dict[str, object]:
    return {
        "signal_window": traces.window("End of on-time"),
        "noise_window": traces.window("Late off-time") or traces.window("Off-time"),
    }


def _same(got: tuple[NoiseMetrics, ...], want: tuple[NoiseMetrics, ...]) -> None:
    """Equal to rounding: Welch over a different batch of channels rounds the last bits differently."""
    assert [item.channel for item in got] == [item.channel for item in want]
    for a, b in zip(got, want, strict=True):
        np.testing.assert_allclose(
            [a.line_db, *a.harmonics_db, a.floor, a.noise_rms, a.snr_db],
            [b.line_db, *b.harmonics_db, b.floor, b.noise_rms, b.snr_db],
            rtol=1e-12,
        )


def test_cached_results_equal_the_direct_ones() -> None:
    traces = _traces()
    window = traces.window("On-time (steady)")
    cache = SpectrumCache()
    spectrum, metrics = cache.measure(traces, window, line_frequency=50.0, **_windows(traces))
    direct = trace_spectrum(traces, window)
    np.testing.assert_array_equal(spectrum.frequency, direct.frequency)
    np.testing.assert_array_equal(spectrum.power, direct.power)
    assert spectrum.reference is not None and direct.reference is not None
    np.testing.assert_array_equal(spectrum.reference, direct.reference)
    assert (spectrum.channels, spectrum.window, spectrum.sample_rate) == (
        direct.channels,
        direct.window,
        direct.sample_rate,
    )
    expected = noise_metrics(traces, direct, line_frequency=50.0, **_windows(traces))
    assert metrics == expected
    assert cache.metrics(traces, window, line_frequency=50.0, **_windows(traces)) == expected
    np.testing.assert_array_equal(cache.spectrum(traces, window).power, direct.power)


def test_only_new_or_changed_channels_are_computed() -> None:
    traces = _traces()
    window = traces.window("On-time (steady)")
    cache = SpectrumCache()
    few = traces.select(["ch0", "ch1"])
    cache.measure(few, window, line_frequency=50.0, **_windows(traces))
    misses = cache.misses
    cache.measure(few, window, line_frequency=50.0, **_windows(traces))
    assert cache.misses == misses
    cache.measure(traces, window, line_frequency=50.0, **_windows(traces))
    assert cache.misses == misses + 2 * 4

    changed = replace(traces, values=traces.values * np.array([[2.0]] + [[1.0]] * 5))
    before = cache.misses
    _, metrics = cache.measure(changed, window, line_frequency=50.0, **_windows(traces))
    assert cache.misses == before + 2
    _same(
        metrics,
        noise_metrics(changed, trace_spectrum(changed, window), line_frequency=50.0, **_windows(traces)),
    )

    before = cache.misses
    cache.measure(traces, window, line_frequency=60.0, **_windows(traces))
    assert cache.misses == before + 6
    cache.measure(traces, traces.window("Off-time"), line_frequency=50.0, **_windows(traces))
    assert cache.misses > before + 6


def test_names_follow_the_set_and_the_size_is_bounded() -> None:
    traces = _traces()
    window = traces.window("On-time (steady)")
    cache = SpectrumCache(max_entries=8)
    cache.measure(traces, window, line_frequency=50.0, **_windows(traces))
    assert len(cache) <= 8
    renamed = replace(traces, channels=tuple(f"x{i}" for i in range(6)), labels=())
    metrics = cache.metrics(renamed, window, line_frequency=50.0, **_windows(traces))
    assert [item.channel for item in metrics] == list(renamed.channels)
    cache.clear()
    assert len(cache) == 0 and cache.hits == cache.misses == 0


def test_an_empty_set_has_an_empty_spectrum() -> None:
    traces = _traces().select([])
    spectrum, metrics = SpectrumCache().measure(traces, traces.window("On-time (steady)"))
    assert spectrum.power.shape[0] == 0 and metrics == ()
