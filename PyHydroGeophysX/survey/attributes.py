"""Names of the values a survey view colours points by, shared by every method.

An adapter keys :attr:`SurveyPoints.attrs` and :attr:`PseudoPoints.attrs` by
these names (English source text, with the unit), so the views translate them
and know which to draw on a log scale. A method may add names of its own; they
are shown as given.
"""

from __future__ import annotations

APPARENT_RESISTIVITY = "Apparent resistivity (ohm.m)"
CHARGEABILITY = "Chargeability (%)"
GEOMETRIC_FACTOR = "Geometric factor (m)"
REJECTED = "Rejected (1) or kept (0)"
ERROR = "Error (%)"
LINE_PEAK = "Line peak (dB)"
NOISE_RMS = "Noise RMS"
SNR = "SNR (dB)"
ELEVATION = "Elevation (m)"
CURRENT = "Current (A)"
VP = "Primary voltage Vp"

#: Every shared name, in the order a list offers them.
ALL = (
    APPARENT_RESISTIVITY,
    CHARGEABILITY,
    GEOMETRIC_FACTOR,
    REJECTED,
    ERROR,
    LINE_PEAK,
    NOISE_RMS,
    SNR,
    ELEVATION,
    CURRENT,
    VP,
)
#: Values drawn on a log scale by default.
LOG_SCALE = frozenset({APPARENT_RESISTIVITY, GEOMETRIC_FACTOR, NOISE_RMS})

__all__ = [
    "ALL",
    "APPARENT_RESISTIVITY",
    "CHARGEABILITY",
    "CURRENT",
    "ELEVATION",
    "ERROR",
    "GEOMETRIC_FACTOR",
    "LINE_PEAK",
    "LOG_SCALE",
    "NOISE_RMS",
    "REJECTED",
    "SNR",
    "VP",
]
