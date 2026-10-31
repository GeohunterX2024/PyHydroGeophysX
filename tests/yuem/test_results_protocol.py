"""ModelResultV2 and the adapters from every existing result type (plan M3.2)."""

from __future__ import annotations

import contextlib
import io
from pathlib import Path
from typing import Any

import numpy as np
import pytest

from PyHydroGeophysX.errors import DataValidationError
from PyHydroGeophysX.results.adapters import (
    from_em1d_result,
    from_gravmag_payload,
    from_inversion_result,
    from_lci_result,
    from_model_result,
    from_workflow_result,
)
from PyHydroGeophysX.results.protocol import (
    COVERAGE_LOG10_THRESHOLD,
    DataFit,
    GridGeometry,
    LayeredGeometry,
    ModelResultV2,
    Parameter,
)


def _layered(doi: Any = None) -> ModelResultV2:
    values = np.array([[10.0, 100.0, 1000.0], [20.0, 200.0, 2000.0]])
    return ModelResultV2(
        method="TDEM",
        geometry=LayeredGeometry(thickness=np.array([5.0, 10.0]), n_soundings=2),
        parameters={"resistivity": Parameter("resistivity", values.ravel(), "ohm.m", log_scale=True)},
        doi=doi,
    )


def test_units_reserved_names_and_sizes_are_checked() -> None:
    _layered().validate()
    grid = GridGeometry(edges=(np.arange(4.0), np.arange(3.0)), axes=("x", "z"))
    with pytest.raises(DataValidationError, match="not registered"):
        ModelResultV2("ERT", grid, {"resistivity": Parameter("resistivity", np.ones(6), "ohmm")}).validate()
    with pytest.raises(DataValidationError, match="reserved for chargeability"):
        ModelResultV2("IP", grid, {"m": Parameter("m", np.ones(6), "ohm.m")}).validate()
    with pytest.raises(DataValidationError, match="5 values for 6 cells"):
        ModelResultV2("ERT", grid, {"resistivity": Parameter("resistivity", np.ones(5), "ohm.m")}).validate()
    spectral = ModelResultV2(
        "IP",
        grid,
        {
            "rho0": Parameter("rho0", np.ones(6), "ohm.m"),
            "m": Parameter("m", np.full(6, 50.0), "mV/V"),
            "tau": Parameter("tau", np.full(6, 0.1), "s"),
            "c": Parameter("c", np.full(6, 0.5), "1"),
        },
    )
    spectral.validate()


def test_coverage_doi_and_resolution_masks_and_their_legend() -> None:
    result = _layered(doi=np.array([12.0, 3.0]))
    mask, basis = result.display_mask()
    # tops are 0, 5, 15 m: sounding 1 sees down to 12 m, sounding 2 to 3 m
    assert mask is not None and mask.tolist() == [True, True, False, True, False, False]
    assert basis == "blank below the depth of investigation"

    grid = GridGeometry(edges=(np.arange(3.0), np.arange(2.0)), axes=("x", "z"))
    ert = ModelResultV2(
        "ERT",
        grid,
        {"resistivity": Parameter("resistivity", np.ones(2), "ohm.m")},
        coverage=np.array([COVERAGE_LOG10_THRESHOLD + 0.5, COVERAGE_LOG10_THRESHOLD - 0.5]),
        resolution=np.array([0.5, 0.5]),
    )
    mask, basis = ert.display_mask()
    assert mask is not None and mask.tolist() == [True, False]
    assert "coverage < 10^-2" in basis and "resolution < 0.05" in basis
    rays = ModelResultV2(
        "SRT",
        grid,
        {"velocity": Parameter("velocity", np.ones(2), "m/s")},
        coverage=np.array([3.0, 0.0]),
        coverage_kind="rays",
    )
    assert rays.display_mask()[0].tolist() == [True, False]  # type: ignore[union-attr]
    assert ModelResultV2(
        "ERT", grid, {"resistivity": Parameter("resistivity", np.ones(2), "ohm.m")}
    ).display_mask() == (
        None,
        "",
    )


def test_chi2_overall_and_per_group() -> None:
    fit = DataFit(
        observed=np.array([1.0, 2.0, 3.0, 4.0]),
        predicted=np.array([1.0, 1.0, 3.0, 2.0]),
        error=np.array([1.0, 1.0, 1.0, 1.0]),
        groups={"HM": np.array([0, 1]), "LM": np.array([False, False, True, True])},
    )
    assert fit.chi2_by_group() == {"all": 1.25, "HM": 0.5, "LM": 2.0}


@pytest.mark.parametrize(
    "result",
    [
        _layered(doi=np.array([12.0, 3.0])),
        ModelResultV2(
            "GRAVITY",
            GridGeometry(edges=(np.arange(3.0), np.arange(3.0), np.arange(2.0))),
            {"density_contrast": Parameter("density_contrast", np.arange(4.0), "g/cm3", std=np.ones(4))},
            fit=DataFit(
                observed=np.ones(3), predicted=np.zeros(3), error=np.ones(3), groups={"a": np.arange(2)}
            ),
            history=[{"iteration": 1, "chi2": 3.0}],
            meta={"label": "density"},
        ),
    ],
)
def test_results_save_and_load(tmp_path: Path, result: ModelResultV2) -> None:
    loaded = ModelResultV2.load(result.save(tmp_path / "r.h5"))
    assert loaded.method == result.method and type(loaded.geometry) is type(result.geometry)
    for name, parameter in result.parameters.items():
        assert np.array_equal(loaded.parameters[name].values, parameter.values)
    (loaded_mask, loaded_basis), (mask, basis) = loaded.display_mask(), result.display_mask()
    assert loaded_basis == basis and (mask is None) == (loaded_mask is None)
    assert mask is None or np.array_equal(loaded_mask, mask)
    assert loaded.history == result.history and loaded.meta == result.meta


def test_em1d_and_lci_results() -> None:
    from PyHydroGeophysX.inversion.em1d_lci import LCIResult
    from PyHydroGeophysX.inversion.tdem_inversion import TDEMInversionResult

    tdem = TDEMInversionResult(
        recovered_conductivity=np.array([0.1, 0.01, 0.001]),
        thicknesses=np.array([5.0, 10.0]),
        predicted_data=np.ones(4),
        chi2=1.1,
        convergence_history=[9.0, 2.0],
    )
    converted = from_em1d_result(tdem)
    converted.validate()
    assert np.allclose(converted.parameters["resistivity"].values, [10.0, 100.0, 1000.0])
    assert converted.history[-1] == {"iteration": 2, "phi_d": 2.0}

    lci = LCIResult(
        models=np.full((3, 4), 50.0),
        chi2=0.9,
        chi2_per_sounding=np.array([0.8, 1.0, 0.9]),
        chi2_history=[5.0, 0.9],
        iterations=2,
        stop_reason="target",
    )
    line = from_lci_result(
        lci, thickness=np.array([2.0, 4.0, 8.0]), positions=[0.0, 10.0, 20.0], doi=np.array([20.0, 20.0, 5.0])
    )
    line.validate()
    assert line.geometry.n_cells == 12 and line.display_mask()[0].sum() == 4 + 4 + 2  # type: ignore[union-attr]


def test_mesh_results_from_pygimli() -> None:
    pg = pytest.importorskip("pygimli")
    from PyHydroGeophysX.inversion.base import InversionResult
    from PyHydroGeophysX.inversion.model_result import ModelResult

    mesh = pg.createGrid(x=np.linspace(0, 4, 5), y=np.linspace(-2, 0, 3))
    model = ModelResult(mesh, np.arange(8.0) + 1, coverage=np.linspace(-4, 0, 8))
    converted = from_model_result(model)
    converted.validate()
    assert converted.geometry.n_cells == 8 and converted.geometry.cells.shape == (8, 4)  # type: ignore[union-attr]
    assert converted.display_mask()[0].sum() == int(np.sum(np.linspace(-4, 0, 8) >= -2.0))  # type: ignore[union-attr]

    inversion = InversionResult()
    inversion.final_model, inversion.mesh, inversion.coverage = np.ones(8), mesh, np.zeros(8)
    inversion.model_log_std, inversion.iteration_chi2 = np.full(8, 0.1), [4.0, 1.2]
    converted = from_inversion_result(inversion)
    converted.validate()
    assert converted.parameters["resistivity"].std_log10 and converted.history[-1]["chi2"] == 1.2


def test_gravmag_payload() -> None:
    edges = (np.arange(4.0), np.arange(3.0), -np.arange(3.0)[::-1])
    payload = {
        "kind": "magnetic",
        "edges": edges,
        "model3d": np.zeros((3, 2, 2)),
        "fit": {"observed": np.ones(2), "predicted": np.ones(2), "std": np.ones(2)},
        "chi2": 0.5,
    }
    converted = from_gravmag_payload(payload)
    converted.validate()
    assert converted.method == "MAGNETIC" and "susceptibility" in converted.parameters


MODEL_WORKFLOWS = (
    "ert.single_inversion",
    "seismic.srt_inversion",
    "em.inversion",
    "em.line_inversion",
    "mt.invert_1d",
    "mt.invert_profile",
    "gravmag.invert",
)


@pytest.fixture(scope="module")
def workflow_results(tmp_path_factory: pytest.TempPathFactory) -> dict[str, Any]:
    from .smoke.recipes import Workspace

    examples = Path(__file__).resolve().parents[2] / "examples" / "data"
    if not examples.is_dir():
        pytest.skip("examples/data is not present")
    workspace = Workspace(tmp_path_factory.mktemp("results"), examples)
    with contextlib.redirect_stdout(io.StringIO()):
        return {wid: workspace.prerequisite(wid) for wid in MODEL_WORKFLOWS}


@pytest.mark.slow
@pytest.mark.parametrize("workflow_id", MODEL_WORKFLOWS)
def test_every_model_workflow_converts(
    workflow_results: dict[str, Any], workflow_id: str, tmp_path: Path
) -> None:
    converted = from_workflow_result(workflow_id, workflow_results[workflow_id])
    converted.validate()
    assert converted.provenance["workflow_id"] == workflow_id
    loaded = ModelResultV2.load(converted.save(tmp_path / "model.h5"))
    first = next(iter(converted.parameters))
    assert np.array_equal(loaded.parameters[first].values, converted.parameters[first].values, equal_nan=True)
