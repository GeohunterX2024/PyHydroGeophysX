"""Random-number determinism (plan M1.7)."""

from __future__ import annotations

import numpy as np
import pytest


def _gravity_magnetics(seed: int) -> np.ndarray:
    pytest.importorskip("simpeg")
    from PyHydroGeophysX.forward.gravmag import gravity_sphere, magnetic_dipole
    from PyHydroGeophysX.inversion.joint_gravity_magnetics import JointGravityMagneticsInversion

    grid_x, grid_y = np.meshgrid(np.linspace(-100.0, 100.0, 7), np.linspace(-100.0, 100.0, 7))
    x, y = grid_x.ravel(), grid_y.ravel()
    z = np.ones(x.size)
    body = {"x0": 0.0, "y0": 0.0, "z0": 45.0, "radius": 28.0, "density": 0.3, "susceptibility": 0.035}
    field = {"strength": 50000.0, "inclination": 60.0, "declination": 0.0}
    joint = JointGravityMagneticsInversion(
        gravity_data={"x": x, "y": y, "z": z, "value": gravity_sphere(x, y, body)},
        magnetics_data={"x": x, "y": y, "z": z, "value": magnetic_dipole(x, y, body, field)},
        field=field,
        n_xy=6,
        n_z=4,
        max_iterations=2,
        run_baseline=False,
        random_seed=seed,
    ).run()
    return np.r_[np.asarray(joint.density, dtype=float), np.asarray(joint.susceptibility, dtype=float)]


def test_joint_gravity_magnetics_is_reproducible_with_a_seed() -> None:
    """SimPEG >= 0.23 seeds its beta estimate from the directive, not the global state."""
    np.random.seed(1)
    first = _gravity_magnetics(seed=11)
    np.random.seed(2)
    second = _gravity_magnetics(seed=11)
    np.testing.assert_array_equal(first, second)


def test_kriging_search_and_split_take_an_explicit_seed() -> None:
    import inspect

    from PyHydroGeophysX.core import kriging_3d

    for function in (kriging_3d.optimize_variogram_model, kriging_3d.krige_seismic_velocity_3d):
        assert "random_seed" in inspect.signature(function).parameters
