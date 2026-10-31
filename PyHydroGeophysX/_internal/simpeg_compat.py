"""Keyword compatibility across SimPEG releases.

SimPEG 0.25 renamed the conjugate-gradient options of its Gauss-Newton
optimizers (``maxIterCG`` -> ``cg_maxiter``, ``tolCG`` -> ``cg_rtol``, same
meaning) and 0.26 removed the old names, so a call written for one release
raises on the other. The supported range is ``simpeg>=0.24,<1.0``.
"""

from __future__ import annotations

import inspect
from typing import Any


def cg_keywords(optimizer: type, *, maxiter: int, rtol: float) -> dict[str, Any]:
    """CG keyword arguments for ``optimizer`` under the installed SimPEG."""
    try:
        names = set(inspect.signature(optimizer).parameters)
    except (TypeError, ValueError):
        names = set()
    if "cg_maxiter" in names:
        return {"cg_maxiter": int(maxiter), "cg_rtol": float(rtol)}
    return {"maxIterCG": int(maxiter), "tolCG": float(rtol)}


__all__ = ["cg_keywords"]
