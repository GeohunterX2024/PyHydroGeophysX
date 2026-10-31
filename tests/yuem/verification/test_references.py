"""Numerical verification against analytic and cross-code references (plan M1.3).

Every case names its reference, the error measure and the tolerance; the
tolerance is set from the discretisation the case uses, not from what the code
happened to return. ``docs/yuem/verification.md`` is generated from these.
"""

from __future__ import annotations

import numpy as np
import pytest

from .conftest import Verify

pytestmark = pytest.mark.numerical

MU0 = 4e-7 * np.pi
G = 6.67430e-11
MGAL = 1.0e5


# --------------------------------------------------------------------------- ERT
def _wenner_two_layer(rho1: float, rho2: float, h: float, a: np.ndarray) -> np.ndarray:
    """Wenner apparent resistivity of a two-layer earth (image series, Telford et al. 1990)."""
    k = (rho2 - rho1) / (rho2 + rho1)
    n = np.arange(1, 600)[:, None]
    terms = k**n * (1.0 / np.sqrt(1.0 + (2.0 * n * h / a) ** 2) - 1.0 / np.sqrt(4.0 + (2.0 * n * h / a) ** 2))
    return rho1 * (1.0 + 4.0 * np.sum(terms, axis=0))


def _wenner_setup() -> tuple[object, object, np.ndarray, np.ndarray]:
    pg = pytest.importorskip("pygimli")
    import pygimli.meshtools as mt
    from pygimli.physics import ert

    data = ert.createData(elecs=np.linspace(0.0, 47.0, 48), schemeName="wa")
    world = mt.createWorld(start=[-250, 0], end=[297, -250], layers=[-5.0], worldMarker=True)
    for sensor in data.sensors():
        world.createNode(sensor)
        world.createNode(sensor + pg.RVector3(0, -0.1))
    mesh = mt.createMesh(world, quality=34, area=25.0)
    depth = np.asarray(mesh.cellCenters())[:, 1]
    xa = np.array([data.sensor(int(i)).x() for i in data["a"]])
    xm = np.array([data.sensor(int(i)).x() for i in data["m"]])
    return data, mesh, depth, np.abs(xm - xa)


def test_ert_homogeneous_half_space(verify: Verify) -> None:
    from PyHydroGeophysX.forward.ert_forward import ERTForwardModeling

    data, mesh, depth, _ = _wenner_setup()
    rhoa = ERTForwardModeling(mesh, data).forward(np.full(depth.size, 100.0), log_transform=False)
    verify(
        case="V-ERT-01",
        title="ERT homogeneous half-space, Wenner, 48 electrodes",
        method="ERT 2.5D",
        engine="PHGX ERTForwardModeling (pyGIMLi core)",
        reference="analytic: apparent resistivity equals 100 ohm-m",
        metric="max relative error of rhoa",
        value=float(np.max(np.abs(rhoa - 100.0) / 100.0)),
        tolerance=5e-3,
    )


def test_ert_two_layer_wenner(verify: Verify) -> None:
    from PyHydroGeophysX.forward.ert_forward import ERTForwardModeling

    data, mesh, depth, spacing = _wenner_setup()
    model = np.where(depth > -5.0, 100.0, 10.0)
    rhoa = ERTForwardModeling(mesh, data).forward(model, log_transform=False)
    reference = _wenner_two_layer(100.0, 10.0, 5.0, spacing)
    verify(
        case="V-ERT-02",
        title="ERT two-layer earth (100/10 ohm-m, h = 5 m), Wenner, per-cell model",
        method="ERT 2.5D",
        engine="PHGX ERTForwardModeling (pyGIMLi core)",
        reference="image series, Telford et al. (1990)",
        metric="max relative error of rhoa",
        value=float(np.max(np.abs(rhoa - reference) / reference)),
        tolerance=1e-2,
        note="Before the fix of 2026-10-31 a per-cell model on a mesh with a marker-1 region "
        "was mapped onto the wrong cells (error up to 284 %).",
    )


def test_ert_3d_per_cell_model_on_a_mesh_with_an_outer_region(verify: Verify, tmp_path: object) -> None:
    pytest.importorskip("pygimli")
    import pandas as pd
    from pygimli.physics import ert

    from PyHydroGeophysX.core import mesh_3d
    from PyHydroGeophysX.forward.ert_forward import ERTForwardModeling

    xy = [(x, y) for x in (0.0, 5.0, 10.0) for y in (0.0, 4.0, 8.0)]
    positions = np.array([(x, y, 100.0 + 0.1 * x) for x, y in xy])
    built = mesh_3d.generate_mesh(
        {
            "array_type": mesh_3d.FILE_ARRAY,
            "electrode_positions": positions,
            "mesh_type": "Surface with topography",
            "mesh_engine": "Structured grid",
            "topography_type": mesh_3d.SENSOR_GROUND,
            "electrode_refinement": 0.5,
            "attractor_distance": 5.0,
            "boundary_refinement": 2.0,
            "para_depth": 4.0,
            "dz_fine": 1.0,
            "dz_coarse": 2.0,
            "boundary_extension": 1.4,
            "output_dir": str(tmp_path),
        }
    )
    mesh = built["mesh"]
    data = mesh_3d.create_3d_ert_data_container(
        pd.DataFrame(positions, columns=["x", "y", "z"]), scheme="dd", dimension=3
    )
    model = np.where(np.asarray(mesh.cellCenters())[:, 2] < 98.0, 10.0, 100.0)
    rhoa = ERTForwardModeling(mesh, data).forward(model, log_transform=False)
    reference_op = ert.ERTModelling()
    reference_op.setData(data)
    reference_op.setMesh(mesh, ignoreRegionManager=True)
    reference = np.asarray(reference_op.response(model))
    verify(
        case="V-ERT-03",
        title="ERT 3D, per-cell layered model on a mesh with a marker-1 outer region",
        method="ERT 3D",
        engine="PHGX ERTForwardModeling (as used by ert3d.forward)",
        reference="pyGIMLi ERTModelling with the region manager ignored (as ert.simulate)",
        metric="max relative difference of rhoa",
        value=float(np.max(np.abs(rhoa - reference) / np.abs(reference))),
        tolerance=1e-10,
        note="Regression guard for the region-mapping fix (台账 P-0005).",
    )


def test_ert_3d_homogeneous_half_space_at_an_elevation(verify: Verify, tmp_path: object) -> None:
    pytest.importorskip("pygimli")
    import pandas as pd

    from PyHydroGeophysX.core import mesh_3d
    from PyHydroGeophysX.forward.ert_forward import ERTForwardModeling

    xy = [(x, y) for x in (0.0, 5.0, 10.0) for y in (0.0, 4.0, 8.0)]
    positions = np.array([(x, y, 100.0) for x, y in xy])
    built = mesh_3d.generate_mesh(
        {
            "array_type": mesh_3d.FILE_ARRAY,
            "electrode_positions": positions,
            "mesh_type": "Surface with topography",
            "mesh_engine": "Structured grid",
            "topography_type": mesh_3d.SENSOR_GROUND,
            "electrode_refinement": 0.5,
            "attractor_distance": 5.0,
            "boundary_refinement": 2.0,
            "para_depth": 4.0,
            "dz_fine": 1.0,
            "dz_coarse": 2.0,
            "boundary_extension": 1.4,
            "output_dir": str(tmp_path),
        }
    )
    mesh = built["mesh"]
    data = mesh_3d.create_3d_ert_data_container(
        pd.DataFrame(positions, columns=["x", "y", "z"]), scheme="dd", dimension=3
    )
    rhoa = ERTForwardModeling(mesh, data).forward(np.full(mesh.cellCount(), 100.0), log_transform=False)
    verify(
        case="V-ERT-04",
        title="ERT 3D homogeneous half-space, surface grid at 100 m elevation",
        method="ERT 3D",
        engine="PHGX create_3d_ert_data_container + ERTForwardModeling (as used by ert3d.forward)",
        reference="analytic: apparent resistivity equals 100 ohm-m",
        metric="max relative error of rhoa",
        value=float(np.max(np.abs(rhoa - 100.0) / 100.0)),
        tolerance=1e-3,
        note="With singularity removal a homogeneous model's response is the analytic primary "
        "field, so the error is that of the geometric factor alone. Before the fix of "
        "2026-10-31 PyGIMLi's factor treated the array as buried 100 m deep and rhoa was "
        "about 200 ohm-m (F-09, 台账 P-0007).",
    )


# --------------------------------------------------------------------------- SRT
def test_srt_two_layer_refraction(verify: Verify) -> None:
    pytest.importorskip("pygimli")
    import pygimli.meshtools as mt
    import pygimli.physics.traveltime as tt

    from PyHydroGeophysX.forward.srt_forward import SeismicForwardModeling

    v1, v2, h = 500.0, 2000.0, 10.0
    sensors = np.linspace(0.0, 100.0, 51)
    scheme = tt.createRAData(sensors)
    world = mt.createWorld(start=[-20, 0], end=[120, -60], layers=[-h], worldMarker=True)
    for x in sensors:
        world.createNode([x, 0.0])
    mesh = mt.createMesh(world, quality=33, area=2.0)
    velocity = np.where(np.asarray(mesh.cellCenters())[:, 1] > -h, v1, v2)
    times = np.asarray(SeismicForwardModeling(mesh, scheme).forward(velocity, slowness=False))
    offset = np.abs(sensors[np.asarray(scheme["g"], int)] - sensors[np.asarray(scheme["s"], int)])
    critical = np.arcsin(v1 / v2)
    reference = np.minimum(offset / v1, offset / v2 + 2.0 * h * np.cos(critical) / v1)
    keep = offset > 0
    verify(
        case="V-SRT-01",
        title="SRT two-layer refraction (500/2000 m/s, h = 10 m), 51 geophones",
        method="SRT",
        engine="PHGX SeismicForwardModeling (pyGIMLi Dijkstra)",
        reference="analytic first arrival: direct wave and head wave",
        metric="max relative error of first-arrival time",
        value=float(np.max(np.abs(times[keep] - reference[keep]) / reference[keep])),
        tolerance=2e-2,
        note="Shortest-path ray tracing on a 2 m^2 mesh; the error is the graph discretisation.",
    )


# --------------------------------------------------------------------------- EM
def test_tdem_central_loop_half_space(verify: Verify) -> None:
    pytest.importorskip("simpeg")
    from scipy.special import erf

    from PyHydroGeophysX.forward.em1d import tdem_forward

    rho, radius = 100.0, 10.0
    geometry = {
        "t_min": 1e-5,
        "t_max": 1e-3,
        "n_times": 15,
        "source_radius": radius,
        "height": 0.01,
        "orientation": "z",
        "waveform": "step_off",
        "waveform_repeat": False,
        "receiver_type": "b",
    }
    out = tdem_forward({"thickness": [], "resistivity": [rho]}, geometry)
    theta_a = np.sqrt(MU0 / rho / (4.0 * out["times"])) * radius
    hz = (
        1.0
        / (2.0 * radius)
        * (
            3.0 / (np.sqrt(np.pi) * theta_a) * np.exp(-(theta_a**2))
            + (1.0 - 3.0 / (2.0 * theta_a**2)) * erf(theta_a)
        )
    )
    reference = MU0 * hz
    verify(
        case="V-TDEM-01",
        title="TDEM central loop (a = 10 m) on a 100 ohm-m half-space, step-off Bz, 10 us-1 ms",
        method="TDEM 1D",
        engine="PHGX em1d.tdem_forward (SimPEG)",
        reference="analytic, Ward & Hohmann (1988) eq. 4.98",
        metric="max relative error of Bz",
        value=float(np.max(np.abs(out["response"] - reference) / reference)),
        tolerance=2e-3,
        note="Loop 1 cm above ground; the analytic solution is for a loop on the surface.",
    )


def _fdem_case(model: dict[str, list[float]]) -> float:
    pytest.importorskip("simpeg")
    empymod = pytest.importorskip("empymod")
    from PyHydroGeophysX.forward.em1d import fdem_forward

    geometry = {
        "freq_min": 100.0,
        "freq_max": 1.0e4,
        "n_freq": 9,
        "tx_rx_sep": 10.0,
        "height": 30.0,
        "orientation": "z",
        "component": "secondary",
        "waveform": "dipole",
    }
    out = fdem_forward(model, geometry)
    frequencies = out["frequencies"]
    depth = [0.0, *np.cumsum(model["thickness"]).tolist()]
    reflected = np.asarray(
        empymod.dipole(
            src=[0.0, 0.0, -30.0],
            rec=[10.0, 0.0, -30.0],
            depth=depth,
            res=[2e14, *model["resistivity"]],
            freqtime=frequencies,
            ab=66,
            xdirect=None,
            verb=0,
            htarg={"dlf": "anderson_801_1982"},
        )
    )
    # empymod's magnetic source is a magnetic current of strength i*omega*mu0*m.
    reference = reflected * 1j * 2.0 * np.pi * frequencies * MU0
    computed = out["real"] + 1j * out["imag"]
    return float(np.max(np.abs(computed - reference) / np.abs(reference)))


FDEM_NOTE = (
    "Reference: reflected field only (xdirect=None) with the 801-point Anderson filter; "
    "empymod's shorter filters disagree with it by several percent above ~5 kHz at this "
    "geometry, so the band is limited to 10 kHz."
)


def test_fdem_vmd_half_space(verify: Verify) -> None:
    verify(
        case="V-FDEM-01",
        title="FDEM vertical magnetic dipole, 30 m height, 10 m offset, 100 ohm-m half-space, 0.1-10 kHz",
        method="FDEM 1D",
        engine="PHGX em1d.fdem_forward (SimPEG)",
        reference="empymod (cross-code)",
        metric="max relative error of secondary Hz",
        value=_fdem_case({"thickness": [], "resistivity": [100.0]}),
        tolerance=1e-3,
        note=FDEM_NOTE,
    )


def test_fdem_vmd_three_layers(verify: Verify) -> None:
    verify(
        case="V-FDEM-02",
        title="FDEM vertical magnetic dipole over 50/200/20 ohm-m (10/20 m), 0.1-10 kHz",
        method="FDEM 1D",
        engine="PHGX em1d.fdem_forward (SimPEG)",
        reference="empymod (cross-code)",
        metric="max relative error of secondary Hz",
        value=_fdem_case({"thickness": [10.0, 20.0], "resistivity": [50.0, 200.0, 20.0]}),
        tolerance=1e-3,
        note=FDEM_NOTE,
    )


# --------------------------------------------------------------------------- MT
def _wait_recursion(rho: np.ndarray, thickness: np.ndarray, frequency: np.ndarray) -> np.ndarray:
    """Surface impedance of a layered earth by the classical recursion (Wait 1954)."""
    omega = 2.0 * np.pi * frequency
    gamma = np.sqrt(1j * omega[:, None] * MU0 / rho[None, :])  # propagation constant
    zeta = np.sqrt(1j * omega[:, None] * MU0 * rho[None, :])  # intrinsic impedance
    z = zeta[:, -1]
    for layer in range(rho.size - 2, -1, -1):
        t = np.tanh(gamma[:, layer] * thickness[layer])
        z = zeta[:, layer] * (z + zeta[:, layer] * t) / (zeta[:, layer] + z * t)
    return z


def test_mt_half_space(verify: Verify) -> None:
    from PyHydroGeophysX.data_processing import mt

    frequency = np.logspace(-3, 3, 25)
    z = np.asarray(mt.impedance_1d(np.array([100.0]), np.array([]), frequency))
    rho_a = np.abs(z) ** 2 / (2.0 * np.pi * frequency * MU0)
    phase = np.degrees(np.angle(z))
    error = max(float(np.max(np.abs(rho_a - 100.0) / 100.0)), float(np.max(np.abs(phase - 45.0)) / 45.0))
    verify(
        case="V-MT-01",
        title="MT 1D homogeneous half-space, 100 ohm-m, 1 mHz-1 kHz",
        method="MT 1D",
        engine="PHGX data_processing.mt.impedance_1d",
        reference="analytic: rho_a = 100 ohm-m, phase = 45 deg",
        metric="max relative error of rho_a and phase",
        value=error,
        tolerance=1e-10,
    )


def test_mt_layered_earth(verify: Verify) -> None:
    from PyHydroGeophysX.data_processing import mt

    rho = np.array([100.0, 10.0, 1000.0])
    thickness = np.array([500.0, 2000.0])
    frequency = np.logspace(-3, 3, 25)
    z = np.asarray(mt.impedance_1d(rho, thickness, frequency))
    reference = _wait_recursion(rho, thickness, frequency)
    # Sign conventions differ between texts (e^{+iwt} vs e^{-iwt}); compare |Z| and |phase|.
    error = max(
        float(np.max(np.abs(np.abs(z) - np.abs(reference)) / np.abs(reference))),
        float(np.max(np.abs(np.abs(np.angle(z)) - np.abs(np.angle(reference))))),
    )
    verify(
        case="V-MT-02",
        title="MT 1D three layers (100/10/1000 ohm-m, 500/2000 m), 1 mHz-1 kHz",
        method="MT 1D",
        engine="PHGX data_processing.mt.impedance_1d",
        reference="independent impedance recursion, Wait (1954)",
        metric="max relative error of |Z| and absolute error of |phase| (rad)",
        value=error,
        tolerance=1e-9,
    )


# --------------------------------------------------------------------------- potential fields
def test_gravity_prism_bouguer_slab(verify: Verify) -> None:
    from PyHydroGeophysX.forward.gravmag import gravity_prism

    drho, top, bottom, half = 300.0, 10.0, 20.0, 5.0e4
    body = {
        "x1": -half,
        "x2": half,
        "y1": -half,
        "y2": half,
        "z1": top,
        "z2": bottom,
        "density_contrast": drho,
    }
    value = float(np.asarray(gravity_prism(np.array([0.0]), np.array([0.0]), body))[0])
    reference = 2.0 * np.pi * G * drho * (bottom - top) * MGAL
    verify(
        case="V-GRAV-01",
        title="Gravity of a 100 km wide, 10 m thick prism under its centre",
        method="Gravity",
        engine="PHGX forward.gravmag.gravity_prism (Nagy 1966)",
        reference="analytic: infinite Bouguer slab 2 pi G drho t",
        metric="relative error of gz",
        value=abs(value - reference) / reference,
        tolerance=1e-3,
        note="The finite width contributes about t/w ~ 1e-4.",
    )


def test_gravity_sphere_and_prism_agree_in_the_far_field(verify: Verify) -> None:
    from PyHydroGeophysX.forward.gravmag import gravity_prism, gravity_sphere

    side, depth, drho = 2.0, 50.0, 300.0
    x = np.linspace(-100.0, 100.0, 21)
    y = np.zeros_like(x)
    cube = {
        "x1": -side / 2,
        "x2": side / 2,
        "y1": -side / 2,
        "y2": side / 2,
        "z1": depth - side / 2,
        "z2": depth + side / 2,
        "density_contrast": drho,
    }
    radius = (3.0 * side**3 / (4.0 * np.pi)) ** (1.0 / 3.0)
    sphere = {"x0": 0.0, "y0": 0.0, "z0": depth, "radius": radius, "density_contrast": drho}
    point_mass = G * drho * side**3 * depth / (x**2 + depth**2) ** 1.5 * MGAL
    error = max(
        float(np.max(np.abs(np.asarray(gravity_prism(x, y, cube)) - point_mass) / point_mass)),
        float(np.max(np.abs(np.asarray(gravity_sphere(x, y, sphere)) - point_mass) / point_mass)),
    )
    verify(
        case="V-GRAV-02",
        title="Gravity of a 2 m cube and an equal-mass sphere at 50 m depth, 200 m profile",
        method="Gravity",
        engine="PHGX gravity_prism and gravity_sphere",
        reference="analytic point mass G M z / r^3",
        metric="max relative error of gz (both bodies)",
        value=error,
        tolerance=1e-3,
    )


def test_magnetic_sphere_at_the_pole(verify: Verify) -> None:
    from PyHydroGeophysX.forward.gravmag import magnetic_dipole

    depth, radius, chi, field_nt = 30.0, 5.0, 0.05, 50000.0
    x = np.linspace(-90.0, 90.0, 37)
    y = np.zeros_like(x)
    computed = np.asarray(
        magnetic_dipole(
            x,
            y,
            {"x0": 0.0, "y0": 0.0, "z0": depth, "radius": radius, "susceptibility": chi},
            {"strength": field_nt, "inclination": 90.0, "declination": 0.0},
        )
    )
    moment = chi * (field_nt * 1e-9 / MU0) * 4.0 / 3.0 * np.pi * radius**3
    r = np.sqrt(x**2 + depth**2)
    reference = 1e-7 * moment * (2.0 * depth**2 - x**2) / r**5 * 1e9
    verify(
        case="V-MAG-01",
        title="Total-field anomaly of an induced sphere at the magnetic pole (I = 90 deg)",
        method="Magnetics",
        engine="PHGX forward.gravmag.magnetic_dipole",
        reference="analytic vertical dipole field mu0 m (2z^2 - x^2) / (4 pi r^5)",
        metric="max absolute error / peak anomaly",
        value=float(np.max(np.abs(computed - reference)) / np.max(np.abs(reference))),
        tolerance=1e-10,
    )


# --------------------------------------------------------------------------- petrophysics
def test_waxman_smits_round_trip(verify: Verify) -> None:
    from PyHydroGeophysX.petrophysics.resistivity_models import (
        resistivity_to_water_content,
        water_content_to_resistivity,
    )

    porosity = np.full(50, 0.35)
    water = np.linspace(0.05, 0.34, 50)
    for sigma_sur in (0.0, 0.002):
        rho = water_content_to_resistivity(water, 50.0, 2.0, porosity, sigma_sur)
        back = resistivity_to_water_content(rho, 50.0, 2.0, porosity, sigma_sur)
        error = float(np.max(np.abs(np.asarray(back) - water)))
        verify(
            case="V-PET-01" if sigma_sur == 0.0 else "V-PET-02",
            title=f"Waxman-Smits water content -> resistivity -> water content (sigma_sur = {sigma_sur})",
            method="Petrophysics",
            engine="PHGX petrophysics.resistivity_models",
            reference="identity (forward then inverse)",
            metric="max absolute error of water content",
            value=error,
            tolerance=1e-8,
        )
