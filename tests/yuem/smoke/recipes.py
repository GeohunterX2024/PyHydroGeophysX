"""Minimal recipes for every registered workflow (plan M1.1).

One builder per workflow ID. Each returns a :class:`WorkflowSpec` small enough to
run in seconds, on the bundled example data or on synthetic arrays written into
the workspace. Builders of workflows that consume another workflow's output
(an ERT model, a 3D mesh, a velocity section) run that prerequisite first,
in-process, and point at what it wrote.

``tests/yuem/smoke/test_workflows.py`` checks that every ID in the registry has
a builder here, so a new workflow cannot ship without a smoke recipe.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np

from PyHydroGeophysX.workflows.models import ArtifactRef, RunContext, WorkflowRunResult, WorkflowSpec
from PyHydroGeophysX.workflows.runner import run_workflow


@dataclass
class Workspace:
    """A project folder for smoke runs, plus the example data it may read."""

    root: Path
    examples: Path
    results: dict[str, WorkflowRunResult] = field(default_factory=dict)

    def ref(self, path: Path, artifact_id: str, kind: str, **metadata: Any) -> ArtifactRef:
        return ArtifactRef.from_path(
            Path(path), artifact_id=artifact_id, kind=kind, base_dir=self.root, metadata=metadata
        )

    def write(self, name: str, array: np.ndarray) -> Path:
        path = self.root / "inputs" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        np.save(path, np.asarray(array, dtype=float))
        return path

    def context(self, workflow_id: str) -> RunContext:
        return RunContext(project_root=self.root, output_dir=self.root / "prereq" / workflow_id)

    def prerequisite(self, workflow_id: str) -> WorkflowRunResult:
        """Run another workflow's smoke recipe once and keep its result."""
        if workflow_id not in self.results:
            self.results[workflow_id] = run_workflow(BUILDERS[workflow_id](self), self.context(workflow_id))
        return self.results[workflow_id]


Builder = Callable[[Workspace], WorkflowSpec]
BUILDERS: dict[str, Builder] = {}


def builder(workflow_id: str) -> Callable[[Builder], Builder]:
    def register(function: Builder) -> Builder:
        BUILDERS[workflow_id] = function
        return function

    return register


def _gravity_stations(ws: Workspace, n: int = 7) -> dict[str, ArtifactRef]:
    xs, ys = np.meshgrid(np.linspace(-60.0, 60.0, n), np.linspace(-60.0, 60.0, n))
    # Off a perfect grid: four stations on one circle leave the Delaunay
    # triangulation of a gridding ambiguous, and rounding then decides it
    # differently on each platform (docs/yuem/findings.md F-19).
    rng = np.random.default_rng(11)
    x = xs.ravel() + rng.uniform(-0.5, 0.5, xs.size)
    y = ys.ravel() + rng.uniform(-0.5, 0.5, ys.size)
    r2 = x**2 + y**2 + 25.0**2
    values = 0.05 * 25.0 / r2**1.5 * 1.0e4
    return {
        "x": ws.ref(ws.write("grav_x.npy", x), "grav-x", "array"),
        "y": ws.ref(ws.write("grav_y.npy", y), "grav-y", "array"),
        "values": ws.ref(ws.write("grav_values.npy", values), "grav-values", "array"),
    }


@builder("gravmag.forward_bodies")
def _gravmag_forward(ws: Workspace) -> WorkflowSpec:
    x = np.linspace(-50.0, 50.0, 11)
    return WorkflowSpec(
        workflow_id="gravmag.forward_bodies",
        inputs={
            "x": ws.ref(ws.write("fwd_x.npy", x), "fwd-x", "array"),
            "y": ws.ref(ws.write("fwd_y.npy", np.zeros_like(x)), "fwd-y", "array"),
        },
        parameters={"kind": "gravity", "bodies": [{"type": "sphere", "z0": 20.0, "radius": 5.0}]},
    )


@builder("gravmag.process")
def _gravmag_process(ws: Workspace) -> WorkflowSpec:
    return WorkflowSpec(workflow_id="gravmag.process", inputs=_gravity_stations(ws), parameters={})


@builder("gravmag.invert")
def _gravmag_invert(ws: Workspace) -> WorkflowSpec:
    return WorkflowSpec(
        workflow_id="gravmag.invert",
        inputs=_gravity_stations(ws, n=6),
        parameters={"kind": "gravity", "n_xy": 8, "n_z": 5, "max_iterations": 3, "auto_beta": False},
        seed=7,
    )


@builder("em.inversion")
def _em_inversion(ws: Workspace) -> WorkflowSpec:
    path = ws.examples / "EM" / "synthetic_fdem.csv"
    return WorkflowSpec(
        workflow_id="em.inversion",
        inputs={"data": ws.ref(path, "em-sounding", "em_sounding")},
        parameters={
            "method": "FDEM",
            "geometry": {
                "source_radius": 10.0,
                "tx_rx_sep": 10.0,
                "height": 30.0,
                "orientation": "z",
                "component": "secondary",
                "waveform": "dipole",
            },
            "n_layers": 6,
            "max_iterations": 4,
            "auto_scale": False,
        },
    )


@builder("em.line_inversion")
def _em_line_inversion(ws: Workspace) -> WorkflowSpec:
    from PyHydroGeophysX.workflows import em1d

    project = ws.examples / "EM" / "synthetic_tem_lci"
    head = em1d.load_sounding(str(project), "TDEM", moment="LM+HM")
    defaults = {
        key: (value.tolist() if isinstance(value, np.ndarray) else value)
        for key, value in head["inversion_defaults"].items()
    }
    inversion = {
        **defaults,
        "max_iterations": 2,
        "lateral_smoothness": 1.3,
        "auto_scale": False,
    }
    return WorkflowSpec(
        workflow_id="em.line_inversion",
        inputs={"data": ws.ref(project, "em-line-soundings", "em_sounding")},
        parameters={
            "method": "TDEM",
            "geometry": {**head["system"], "tem_moment": "LM+HM"},
            "inversion": inversion,
            "max_soundings": 3,
            "doi_blank": False,
        },
    )


@builder("ert.single_inversion")
def _ert_single(ws: Workspace) -> WorkflowSpec:
    path = ws.examples / "ERT" / "Bert" / "fielddataline2.dat"
    return WorkflowSpec(
        workflow_id="ert.single_inversion",
        inputs={"data": ws.ref(path, "ert-data", "ert_data")},
        parameters={"lambda": 20.0, "max_iterations": 2, "max_total_iterations": 4, "mesh_quality": 30.0},
    )


@builder("ert.mesh_build")
def _ert_mesh_build(ws: Workspace) -> WorkflowSpec:
    path = ws.examples / "ERT" / "Bert" / "fielddataline2.dat"
    return WorkflowSpec(
        workflow_id="ert.mesh_build",
        inputs={"data": ws.ref(path, "ert-mesh-data", "ert_data")},
        parameters={"kind": "single", "options": {"mesh_quality": 30.0}},
    )


@builder("ert.e4d_mesh")
def _ert_e4d_mesh(ws: Workspace) -> WorkflowSpec:
    from PyHydroGeophysX.core.e4d_mesh import e4d_config_from_electrodes, write_e4d_config

    electrodes = np.array([(x, y, 0.0) for x in (0.0, 4.0, 8.0) for y in (0.0, 4.0)])
    config, _ = e4d_config_from_electrodes(
        electrodes, outer_distance=20.0, bottom_depth=20.0, fine_volume=4.0
    )
    path = write_e4d_config(config, ws.root / "inputs" / "smoke_e4d.cfg")
    return WorkflowSpec(
        workflow_id="ert.e4d_mesh",
        inputs={"config": ws.ref(path, "ert-e4d-config", "e4d_mesh_configuration")},
        parameters={"name": "smoke_e4d"},
    )


@builder("seismic.srt_inversion")
def _srt(ws: Workspace) -> WorkflowSpec:
    path = ws.examples / "Seismic" / "srtfieldline2.dat"
    return WorkflowSpec(
        workflow_id="seismic.srt_inversion",
        inputs={"traveltime": ws.ref(path, "srt-traveltime", "traveltime")},
        parameters={"lam": 50.0, "max_iterations": 2, "max_total_iterations": 4},
    )


@builder("mt.invert_1d")
def _mt_1d(ws: Workspace) -> WorkflowSpec:
    path = ws.examples / "MT" / "NMX20.xml"
    return WorkflowSpec(
        workflow_id="mt.invert_1d",
        inputs={"transfer_function": ws.ref(path, "mt-tf", "mt_transfer_function")},
        parameters={"mode": "det", "max_iterations": 4},
    )


@builder("mesh3d.build")
def _mesh3d(ws: Workspace) -> WorkflowSpec:
    xy = [(x, y) for x in (0.0, 5.0, 10.0) for y in (0.0, 4.0, 8.0)]
    positions = np.array([(x, y, 100.0 + 0.1 * x) for x, y in xy])
    return WorkflowSpec(
        workflow_id="mesh3d.build",
        inputs={
            "electrode_positions": ws.ref(ws.write("mesh3d_electrodes.npy", positions), "m3-el", "array")
        },
        parameters={
            "array_type": "From file (x, y, z)",
            "mesh_type": "Surface with topography",
            "mesh_engine": "Structured grid",
            "topography_type": "Sensor elevations",
            "electrode_refinement": 0.5,
            "attractor_distance": 5.0,
            "boundary_refinement": 2.0,
            "para_depth": 4.0,
            "dz_fine": 1.0,
            "dz_coarse": 2.0,
            "boundary_extension": 1.4,
            "output_formats": [],
            "output_name": "smoke_mesh",
        },
    )


@builder("ert.timelapse_inversion")
def _ert_timelapse(ws: Workspace) -> WorkflowSpec:
    folder = ws.examples / "TL_measurements" / "appres"
    names = ("synthetic_data30.dat", "synthetic_data60.dat", "synthetic_data90.dat")
    return WorkflowSpec(
        workflow_id="ert.timelapse_inversion",
        inputs={
            "data_files": [ws.ref(folder / name, f"tl-{i}", "ert_data") for i, name in enumerate(names)],
            "measurement_times": [30, 60, 90],
            "time_labels": ["day 30", "day 60", "day 90"],
            "time_unit": "d",
        },
        parameters={"max_iterations": 2, "min_iterations": 1},
    )


@builder("ert3d.forward")
def _ert3d_forward(ws: Workspace) -> WorkflowSpec:
    from PyHydroGeophysX.core.mesh_serialization import save_mesh_artifact

    mesh_result = ws.prerequisite("mesh3d.build")
    folder = ws.root / "inputs" / "ert3d"
    folder.mkdir(parents=True, exist_ok=True)
    mesh_path, structure_path = folder / "mesh.bms", folder / "mesh.bms.structure.json"
    save_mesh_artifact(mesh_result.objects["mesh"], mesh_path, structure_path)
    positions = np.load(ws.root / "inputs" / "mesh3d_electrodes.npy")
    sensors = folder / "sensors.csv"
    sensors.write_text("x,y,z\n" + "".join(f"{x},{y},{z}\n" for x, y, z in positions), encoding="utf-8")
    return WorkflowSpec(
        workflow_id="ert3d.forward",
        inputs={
            "mesh": ws.ref(mesh_path, "ert3d:mesh", "pygimli_mesh"),
            "mesh_structure": ws.ref(structure_path, "ert3d:mesh_structure", "mesh_structure"),
            "sensors": ws.ref(sensors, "ert3d:sensors", "electrode_geometry"),
        },
        parameters={"scheme": "dd", "background_res": 100.0, "noise": 0.03},
        seed=42,
    )


@builder("geo_hydrology.ert_to_wc")
def _geo_hydrology(ws: Workspace) -> WorkflowSpec:
    from PyHydroGeophysX.Geophy_modular.ERT_to_WC import find_model_files

    model_dir = Path(str(ws.prerequisite("ert.timelapse_inversion").summary["output_dir"]))

    files = {key: str(path) for key, path in find_model_files(model_dir).items() if path is not None}
    return WorkflowSpec(
        workflow_id="geo_hydrology.ert_to_wc",
        inputs={"context": {}, "model_files": files},
        parameters={
            "n_realizations": 3,
            "products": ["water_content"],
            # A time-lapse run writes no marker file, so every cell is marker 0.
            "layers": [
                {
                    "marker": 0,
                    "name": "Whole section",
                    "m": {"mean": 1.5, "std": 0.1},
                    "rho_fluid": {"mean": 20.0, "std": 0.0},
                    "n": {"mean": 2.0, "std": 0.1},
                    "sigma_sur": {"mean": 0.0, "std": 0.0},
                    "porosity": {"mean": 0.35, "std": 0.05},
                }
            ],
        },
        seed=11,
    )


@builder("hydro_geophysics.forward")
def _hydro_geophysics(ws: Workspace) -> WorkflowSpec:
    names = ("Watercontent.npy", "Porosity.npy", "top.npy", "bot.npy")
    files = {name: str(ws.examples / name) for name in names}
    return WorkflowSpec(
        workflow_id="hydro_geophysics.forward",
        inputs={"context": {}, "hydro_files": files},
        parameters={"methods": ["ERT"], "point1": [115, 70], "point2": [95, 180], "num_samples": 60},
        seed=5,
    )


@builder("joint_inversion.run")
def _joint(ws: Workspace) -> WorkflowSpec:
    from PyHydroGeophysX.data_processing import em1d as em_data
    from PyHydroGeophysX.data_processing.joint_io import save_joint_observations

    references = {}
    for method, name in (("FDEM", "joint_synthetic_fdem.csv"), ("TDEM", "joint_synthetic_tdem.csv")):
        soundings = em_data.read_survey(str(ws.examples / "EM" / name), method)
        payload = soundings[0] if len(soundings) == 1 else {"soundings": soundings}
        stored = save_joint_observations(method, payload, ws.root / "inputs" / f"joint_{method.lower()}")
        references[method] = ws.ref(stored, f"joint-input:{method.lower()}", "joint_observations")
    return WorkflowSpec(
        workflow_id="joint_inversion.run",
        inputs={"data": references},
        parameters={
            "method_a": "FDEM",
            "method_b": "TDEM",
            "strategy": "shared_conductivity",
            "run_baseline": False,
            "max_iterations": 3,
        },
    )


def _mt_run(seed: int = 3, sample_rate: float = 64.0, n: int = 2**14) -> Any:
    """Natural-field-like H and the E a layered earth makes of it (as tests/test_core.py)."""
    from PyHydroGeophysX.data_processing import mt

    rng = np.random.default_rng(seed)

    def field() -> np.ndarray:
        walk = np.cumsum(rng.standard_normal(n)) * 0.02 + rng.standard_normal(n)
        return walk - walk.mean()

    hx, hy = field(), field()
    f = np.fft.rfftfreq(n, 1.0 / sample_rate)
    z = np.zeros(f.size, complex)
    z[1:] = mt.impedance_1d(np.array([100.0, 10.0, 1000.0]), np.array([500.0, 2000.0]), f[1:])
    z /= mt.FIELD_TO_OHM
    ex = np.fft.irfft(z * np.fft.rfft(hy), n=n)
    ey = np.fft.irfft(-z * np.fft.rfft(hx), n=n)
    channels = [
        mt.Channel("ex", ex, "mV/km"),
        mt.Channel("ey", ey, "mV/km"),
        mt.Channel("hx", hx, "nT"),
        mt.Channel("hy", hy, "nT"),
    ]
    return mt.TimeSeriesRun(channels, sample_rate, "2024-01-01T00:00:00", station="T1")


@builder("mt.process")
def _mt_process(ws: Workspace) -> WorkflowSpec:
    from PyHydroGeophysX.data_processing import mt

    stored = mt.save_runs(ws.root / "inputs" / "mt_runs.npz", [_mt_run()])
    return WorkflowSpec(
        workflow_id="mt.process",
        inputs={"recording": ws.ref(Path(stored), "mt-recording", "mt_timeseries")},
        parameters={},
    )


@builder("mt.invert_profile")
def _mt_profile(ws: Workspace) -> WorkflowSpec:
    from PyHydroGeophysX.data_processing import mt

    frequencies = np.logspace(0, 3, 6)
    refs = []
    for k in range(3):
        z = np.zeros((frequencies.size, 2, 2), dtype=complex)
        z1d = mt.impedance_1d(np.array([100.0, 30.0]), np.array([200.0]), frequencies)
        z[:, 0, 1], z[:, 1, 0] = z1d, -z1d
        tf = mt.TransferFunction(
            frequency=frequencies, z=z, z_err=0.03 * np.abs(z) + 1e-12, station=f"P{k:02d}"
        )
        path = mt.write_edi(tf, ws.root / "inputs" / f"P{k:02d}.edi")
        refs.append(ws.ref(Path(path), f"mt-site-{k}", "mt_transfer_function"))
    return WorkflowSpec(
        workflow_id="mt.invert_profile",
        inputs={"transfer_functions": refs},
        parameters={"positions": [0.0, 200.0, 400.0], "max_iterations": 2},
        seed=3,
    )


@builder("seismic3d.build")
def _seismic3d(ws: Workspace) -> WorkflowSpec:
    srt = ws.prerequisite("seismic.srt_inversion")
    manager = srt.objects["manager"]
    folder = ws.root / "inputs" / "seismic3d"
    folder.mkdir(parents=True, exist_ok=True)
    mesh_path, velocity_path = folder / "velmesh.bms", folder / "Vinvmodel.npy"
    manager.paraDomain.save(str(mesh_path))
    np.save(velocity_path, np.asarray(manager.model, dtype=float))
    lines = [
        {
            "name": "L1",
            "mesh": str(mesh_path),
            "velocity": str(velocity_path),
            "x0": 0.0,
            "y0": 0.0,
            "x1": 100.0,
            "y1": 0.0,
        },
        {
            "name": "L2",
            "mesh": str(mesh_path),
            "velocity": str(velocity_path),
            "x0": 0.0,
            "y0": 40.0,
            "x1": 100.0,
            "y1": 40.0,
        },
    ]
    return WorkflowSpec(
        workflow_id="seismic3d.build",
        inputs={"context": {}, "lines": lines},
        parameters={
            "threshold": 1200.0,
            "interval": 4.0,
            "grid_resolution": 10,
            "depth": 20.0,
            "n_layers": 6,
            "interp_method": "linear",
        },
    )


def write_recipe(spec: WorkflowSpec, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(spec.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
    return path
