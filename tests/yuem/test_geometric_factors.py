"""Analytic ERT geometric factors of 3-D surveys (F-09, 台账 P-0007)."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
import pytest

pg = pytest.importorskip("pygimli")

from PyHydroGeophysX._internal.ert_factors import surface_geometric_factors  # noqa: E402
from PyHydroGeophysX.core import mesh_3d  # noqa: E402

GRID = [(x, y) for x in (0.0, 5.0, 10.0) for y in (0.0, 4.0, 8.0)]


def _container(positions: list[tuple[float, float, float]]) -> Any:
    return mesh_3d.create_3d_ert_data_container(
        pd.DataFrame(positions, columns=["x", "y", "z"]), scheme="dd", dimension=3
    )


def _factors(data: Any) -> np.ndarray:
    # data["k"] views the container's memory; copy it while the container lives.
    k = np.array(data["k"], dtype=float)
    assert k.size == data.size() > 0
    return k


def test_a_surface_grid_at_an_elevation_has_the_factors_it_has_at_z_0() -> None:
    at_zero = _container([(x, y, 0.0) for x, y in GRID])
    raised = _container([(x, y, 100.0) for x, y in GRID])

    np.testing.assert_allclose(_factors(raised), _factors(at_zero), rtol=1e-12)


def test_the_factors_at_z_0_are_pygimlis_flat_earth_factors() -> None:
    data = _container([(x, y, 0.0) for x, y in GRID])

    np.testing.assert_allclose(
        _factors(data), np.asarray(pg.core.geometricFactors(data, 3, True)), rtol=1e-12
    )


def test_a_borehole_keeps_pygimlis_factors_below_a_ground_at_z_0() -> None:
    positions = [(0.0, 0.0, -z) for z in (1.0, 2.0, 3.0, 4.0, 5.0, 6.0)]
    positions += [(6.0, 0.0, -z) for z in (1.0, 2.0, 3.0, 4.0, 5.0, 6.0)]
    data = _container(positions)

    np.testing.assert_allclose(
        _factors(data), np.asarray(pg.core.geometricFactors(data, 3, False)), rtol=1e-12
    )


def test_a_file_survey_and_a_synthetic_one_get_the_same_factors() -> None:
    from PyHydroGeophysX.data_processing.ert_io import analytic_geometric_factors

    data = _container([(x, y, 100.0 + 0.1 * x) for x, y in GRID])

    np.testing.assert_allclose(_factors(data), analytic_geometric_factors(data), rtol=1e-12)


def test_a_pole_adds_no_term() -> None:
    data = pg.DataContainerERT()
    for x in (0.0, 1.0, 2.0):
        data.createSensor([x, 0.0, 50.0])
    data.createFourPointData(0, 0, -1, 1, 2)

    k = surface_geometric_factors(data)

    np.testing.assert_allclose(k, [2.0 * np.pi / (1.0 - 0.5)])
