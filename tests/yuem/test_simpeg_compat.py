"""SimPEG keyword compatibility (台账 P-0004)."""

from __future__ import annotations

import pytest

from PyHydroGeophysX._internal.simpeg_compat import cg_keywords


class _New:
    def __init__(self, *, cg_maxiter: int = 5, cg_rtol: float = 1e-3, **kwargs: object) -> None:
        pass


class _Old:
    def __init__(self, **kwargs: object) -> None:
        pass


def test_new_api_names() -> None:
    assert cg_keywords(_New, maxiter=20, rtol=1e-3) == {"cg_maxiter": 20, "cg_rtol": 1e-3}


def test_old_api_names() -> None:
    assert cg_keywords(_Old, maxiter=20, rtol=1e-3) == {"maxIterCG": 20, "tolCG": 1e-3}


def test_installed_simpeg_optimizers_accept_the_keywords() -> None:
    optimization = pytest.importorskip("simpeg.optimization")
    for name in ("ProjectedGNCG", "InexactGaussNewton"):
        cls = getattr(optimization, name)
        cls(maxIter=2, **cg_keywords(cls, maxiter=10, rtol=1e-3))
