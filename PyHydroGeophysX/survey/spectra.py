"""Power spectra of recorded curves, power-line harmonics and per-channel noise measures.

The spectrum of a whole DC/IP record is dominated by the leakage of its
switching steps, so a spectrum is taken over a window of steady signal (the
steady on-time, or the late off-time where only noise is left). Welch's method
(Hann window, linear detrend, half-overlapping segments) keeps the estimate
stable enough to compare channels.

Harmonics above the Nyquist frequency are folded to where they appear in the
sampled record: at 250 samples per second the 150 Hz harmonic of 50 Hz mains
shows at 100 Hz, on top of the second harmonic.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import ArrayLike
from scipy import signal

from PyHydroGeophysX.survey.layout import BoolArray, FloatArray
from PyHydroGeophysX.survey.traces import TraceSet, Window

#: Power-line frequency when the data do not say (Hz).
DEFAULT_LINE_FREQUENCY = 50.0
#: Half-width of the band a harmonic's power is read in, in frequency bins.
_HARMONIC_BINS = 1


@dataclass(frozen=True)
class Harmonic:
    """The ``order``-th harmonic of the line frequency, and where sampling puts it."""

    order: int
    frequency: float
    apparent: float

    @property
    def aliased(self) -> bool:
        return not np.isclose(self.frequency, self.apparent)


@dataclass(frozen=True)
class Spectrum:
    """Power spectral density ``power`` (channels, frequencies) in unit²/Hz."""

    frequency: FloatArray
    power: FloatArray
    channels: tuple[str, ...]
    labels: tuple[str, ...]
    unit: str
    sample_rate: float
    window: str
    reference: FloatArray | None = None

    @property
    def nyquist(self) -> float:
        return self.sample_rate / 2.0

    @property
    def amplitude(self) -> FloatArray:
        """Amplitude spectral density, unit/√Hz."""
        return np.asarray(np.sqrt(np.maximum(self.power, 0.0)), dtype=np.float64)


@dataclass(frozen=True)
class NoiseMetrics:
    """Noise measures of one channel.

    ``line_db``: the line-frequency peak over the broadband floor; ``harmonics_db``
    the same for each harmonic (folded); ``floor``: median PSD outside the
    harmonics (unit²/Hz); ``noise_rms``: RMS of the noise window after a linear
    detrend (unit); ``snr_db``: the signal step over that RMS (NaN without both windows).
    """

    channel: str
    line_db: float
    harmonics_db: tuple[float, ...]
    floor: float
    noise_rms: float
    snr_db: float


def apparent_frequency(frequency: float, sample_rate: float) -> float:
    """Where a tone at ``frequency`` appears after sampling at ``sample_rate``."""
    if sample_rate <= 0:
        return float(frequency)
    folded = (float(frequency) + sample_rate / 2.0) % sample_rate - sample_rate / 2.0
    return abs(folded)


def line_harmonics(
    sample_rate: float, line_frequency: float = DEFAULT_LINE_FREQUENCY, count: int = 4
) -> tuple[Harmonic, ...]:
    """The first ``count`` harmonics of the line frequency, each with its folded frequency."""
    return tuple(
        Harmonic(order, order * line_frequency, apparent_frequency(order * line_frequency, sample_rate))
        for order in range(1, count + 1)
    )


def segment_length(n_samples: int) -> int:
    """Welch segment length: a power of two about a quarter of the record, 64 to 4096 samples."""
    if n_samples < 8:
        return max(n_samples, 1)
    target = 2 ** int(np.floor(np.log2(max(n_samples / 4.0, 1.0))))
    return int(min(n_samples, max(64, min(target, 4096))))


def psd(values: ArrayLike, sample_rate: float, nperseg: int | None = None) -> tuple[FloatArray, FloatArray]:
    """Welch PSD of each row of ``values``: ``(frequency, power)``."""
    data = np.atleast_2d(np.asarray(values, dtype=np.float64))
    n = data.shape[1]
    if n < 4 or sample_rate <= 0:
        return np.zeros(0), np.zeros((data.shape[0], 0))
    data = np.where(np.isfinite(data), data, 0.0)
    frequency, power = signal.welch(
        data,
        fs=sample_rate,
        window="hann",
        nperseg=nperseg or segment_length(n),
        detrend="linear",
        scaling="density",
        axis=-1,
    )
    return np.asarray(frequency, dtype=np.float64), np.asarray(power, dtype=np.float64)


def trace_spectrum(traces: TraceSet, window: Window | None = None, nperseg: int | None = None) -> Spectrum:
    """The spectrum of every channel (and of the reference curve) over ``window``."""
    mask = traces.mask(window)
    rate = traces.sample_rate
    frequency, power = psd(traces.values[:, mask], rate, nperseg)
    reference = None
    if traces.reference is not None:
        _, ref_power = psd(traces.reference[mask], rate, nperseg)
        reference = ref_power[0] if ref_power.size else None
    return Spectrum(
        frequency,
        power,
        traces.channels,
        traces.labels,
        traces.unit,
        rate,
        window.name if window is not None else "",
        reference,
    )


def _harmonic_mask(frequency: FloatArray, harmonics: tuple[Harmonic, ...]) -> BoolArray:
    if frequency.size < 2:
        return np.zeros(frequency.size, bool)
    step = float(frequency[1] - frequency[0])
    near = np.zeros(frequency.size, bool)
    for harmonic in harmonics:
        near |= np.abs(frequency - harmonic.apparent) <= (_HARMONIC_BINS + 0.5) * step
    return near


def _peak_db(frequency: FloatArray, power: FloatArray, at: float, floor: float) -> float:
    if frequency.size < 2 or not np.isfinite(floor) or floor <= 0:
        return float("nan")
    step = float(frequency[1] - frequency[0])
    band = np.abs(frequency - at) <= (_HARMONIC_BINS + 0.5) * step
    if not band.any():
        return float("nan")
    return float(10.0 * np.log10(max(float(np.max(power[band])), 1e-300) / floor))


def noise_metrics(
    traces: TraceSet,
    spectrum: Spectrum,
    *,
    line_frequency: float | None = None,
    signal_window: Window | None = None,
    noise_window: Window | None = None,
    harmonics: int = 4,
) -> tuple[NoiseMetrics, ...]:
    """Noise measures of every channel of ``traces`` from its ``spectrum``.

    The signal step is the difference of the channel's medians in the signal
    and noise windows (for a DC/IP shot: end of on-time against off-time).
    """
    f0 = line_frequency or traces.line_frequency or DEFAULT_LINE_FREQUENCY
    tones = line_harmonics(spectrum.sample_rate, f0, harmonics)
    near = _harmonic_mask(spectrum.frequency, tones)
    broadband = (~near) & (spectrum.frequency > 0)
    noise_mask = traces.mask(noise_window) if noise_window is not None else None
    signal_mask = traces.mask(signal_window) if signal_window is not None else None
    results = []
    for row, name in enumerate(traces.channels):
        power = spectrum.power[row] if spectrum.power.size else np.zeros(0)
        floor = float(np.median(power[broadband])) if power.size and broadband.any() else float("nan")
        line_db = _peak_db(spectrum.frequency, power, tones[0].apparent, floor) if tones else float("nan")
        harmonics_db = tuple(_peak_db(spectrum.frequency, power, h.apparent, floor) for h in tones)
        noise_rms = float("nan")
        snr_db = float("nan")
        if noise_mask is not None and noise_mask.sum() >= 4:
            noise = signal.detrend(traces.values[row, noise_mask], type="linear")
            noise_rms = float(np.sqrt(np.mean(noise**2)))
            if signal_mask is not None and signal_mask.any() and noise_rms > 0:
                step = abs(
                    float(np.median(traces.values[row, signal_mask]))
                    - float(np.median(traces.values[row, noise_mask]))
                )
                snr_db = float(20.0 * np.log10(max(step, 1e-300) / noise_rms))
        results.append(NoiseMetrics(name, line_db, harmonics_db, floor, noise_rms, snr_db))
    return tuple(results)


__all__ = [
    "DEFAULT_LINE_FREQUENCY",
    "Harmonic",
    "NoiseMetrics",
    "Spectrum",
    "apparent_frequency",
    "line_harmonics",
    "noise_metrics",
    "psd",
    "segment_length",
    "trace_spectrum",
]
