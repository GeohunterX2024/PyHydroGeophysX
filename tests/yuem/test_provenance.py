"""Run provenance (plan M1.5): what every result records and how reruns compare."""

from __future__ import annotations

import json
from importlib import metadata
from pathlib import Path

import numpy as np
import pytest

import PyHydroGeophysX
from PyHydroGeophysX._internal.provenance import (
    collect_environment,
    environment_diff,
    parameters_digest,
)
from PyHydroGeophysX.workflows.cli import main as workflow_cli
from PyHydroGeophysX.workflows.models import ArtifactRef, RunContext, WorkflowSpec
from PyHydroGeophysX.workflows.runner import run_workflow


def test_environment_names_the_fork_python_platform_and_packages() -> None:
    env = collect_environment()
    assert env["schema"] == "phgx-provenance-v1"
    assert env["phgx_version"] == PyHydroGeophysX.__version__
    assert env["python"]["version"]
    assert env["platform"]["machine"]
    assert env["packages"]["numpy"] == metadata.version("numpy")
    json.dumps(env, allow_nan=False)


def test_package_versions_come_from_metadata_not_dunder_version() -> None:
    pytest.importorskip("pygimli")
    # pygimli.__version__ reports the git state of the working directory.
    assert collect_environment()["packages"]["pygimli"] == metadata.version("pygimli")


def test_collect_environment_returns_an_independent_copy() -> None:
    first = collect_environment()
    first["packages"]["numpy"] = "tampered"
    assert collect_environment()["packages"]["numpy"] == metadata.version("numpy")


def test_environment_diff_is_empty_for_the_same_environment() -> None:
    assert environment_diff(collect_environment()) == []


def test_environment_diff_names_changed_versions_and_blas() -> None:
    recorded = collect_environment()
    recorded["packages"]["numpy"] = "1.0.0"
    recorded["phgx_version"] = "0.4.0"
    recorded["blas"] = [{"user_api": "blas", "internal_api": "mkl", "version": "2024"}]
    changes = environment_diff(recorded)
    assert any(line.startswith("numpy: 1.0.0 ->") for line in changes)
    assert any(line.startswith("PyHydroGeophysX: 0.4.0 ->") for line in changes)
    assert any(line.startswith("BLAS:") for line in changes)


def test_parameters_digest_is_canonical() -> None:
    assert parameters_digest({"a": 1, "b": [1, 2]}) == parameters_digest({"b": [1, 2], "a": 1})
    assert parameters_digest({"a": 1}) != parameters_digest({"a": 2})


def _gravity_spec(tmp_path: Path) -> WorkflowSpec:
    x = np.linspace(-50.0, 50.0, 11)
    np.save(tmp_path / "x.npy", x)
    np.save(tmp_path / "y.npy", np.zeros_like(x))
    return WorkflowSpec(
        workflow_id="gravmag.forward_bodies",
        inputs={
            "x": ArtifactRef.from_path(tmp_path / "x.npy", artifact_id="x", kind="array", base_dir=tmp_path),
            "y": ArtifactRef.from_path(tmp_path / "y.npy", artifact_id="y", kind="array", base_dir=tmp_path),
        },
        parameters={"kind": "gravity", "bodies": [{"type": "sphere", "z0": 20.0, "radius": 5.0}]},
    )


def test_every_workflow_result_carries_full_provenance(tmp_path: Path) -> None:
    spec = _gravity_spec(tmp_path)
    result = run_workflow(spec, RunContext(project_root=tmp_path, output_dir=tmp_path / "out"))
    provenance = result.to_dict()["provenance"]
    assert provenance["workflow_id"] == "gravmag.forward_bodies"
    assert provenance["seed"] is None
    assert set(provenance["input_checksums"]) == {"x", "y"}
    assert all(value.startswith("sha256:") for value in provenance["input_checksums"].values())
    assert provenance["parameters_digest"] == parameters_digest(spec.to_dict())
    assert provenance["environment"]["phgx_version"] == PyHydroGeophysX.__version__


def test_cli_env_diff_reports_same_and_changed(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    record = tmp_path / "run.json"
    record.write_text(json.dumps({"provenance": {"environment": collect_environment()}}))
    assert workflow_cli(["env-diff", str(record)]) == 0
    changed = collect_environment()
    changed["packages"]["scipy"] = "0.1"
    record.write_text(json.dumps({"provenance": {"environment": changed}}))
    assert workflow_cli(["env-diff", str(record)]) == 1
    assert "scipy: 0.1 ->" in capsys.readouterr().out
    record.write_text("{}")
    assert workflow_cli(["env-diff", str(record)]) == 2


def test_results_store_stamps_runs_computed_in_process(tmp_path: Path) -> None:
    from PyHydroGeophysX.qt_apps.results_store import ResultsStore

    store = ResultsStore(tmp_path / "project")
    handle = store.begin_run(module_key="gravmag_processing", operation_id="gravmag.process", label="t")
    record = store.finish_run(handle, {"status": "ok", "summary": {"n": 1}})
    assert record.provenance["environment"]["phgx_version"] == PyHydroGeophysX.__version__


def test_handler_provenance_keys_are_kept(tmp_path: Path) -> None:
    """A handler's own provenance (e.g. SRT records its input artifacts) survives."""
    from PyHydroGeophysX.workflows.models import RunContext, WorkflowRunResult
    from PyHydroGeophysX.workflows.runner import _with_provenance

    spec = _gravity_spec(tmp_path)
    result = WorkflowRunResult(status="ok", provenance={"inputs": {"traveltime": {"path": "t.dat"}}})
    _with_provenance(result, spec, RunContext(threads=2))
    assert result.provenance["threads"] == 2
    assert result.provenance["inputs"] == {"traveltime": {"path": "t.dat"}}
    assert set(result.provenance["input_checksums"]) == {"x", "y"}
