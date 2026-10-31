"""Analytic ERT geometric factors for electrodes on the ground."""

from __future__ import annotations

from typing import Any

import numpy as np
from numpy.typing import ArrayLike, NDArray


def surface_geometric_factors(data: Any, positions: ArrayLike | None = None) -> NDArray[np.float64]:
    """Half-space factors, 2*pi / (1/AM - 1/BM - 1/AN + 1/BN), with every
    electrode on the ground and distances taken in 3-D.

    ``data`` is a PyGIMLi ``DataContainerERT``; ``positions`` defaults to its
    sensor positions. A pole (index -1) adds no term; a configuration whose
    terms cancel gets 0.
    """
    xyz = np.asarray(data.sensorPositions() if positions is None else positions, dtype=float)
    index = {token: np.asarray(data[token], dtype=int) for token in "abmn"}

    def inverse(current: str, potential: str) -> NDArray[np.float64]:
        i, j = index[current], index[potential]
        used = (i >= 0) & (j >= 0)
        out = np.zeros(len(i))
        distance = np.linalg.norm(xyz[i[used]] - xyz[j[used]], axis=1)
        with np.errstate(divide="ignore"):
            out[used] = 1.0 / distance
        return out

    total = inverse("a", "m") - inverse("b", "m") - inverse("a", "n") + inverse("b", "n")
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.where(np.abs(total) > 0, 2.0 * np.pi / total, 0.0)


__all__ = ["surface_geometric_factors"]
