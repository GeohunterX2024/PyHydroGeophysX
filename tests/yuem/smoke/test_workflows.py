"""Every registered workflow runs end to end through the command line (plan M1.1).

Each recipe from ``recipes.py`` is written to JSON and run in a subprocess with
``python -m PyHydroGeophysX.workflows.cli run``, exactly as the Studio's
``ProcessWorkflowWorker`` does. The project folder has a Chinese name with a
space in it, so path handling is exercised on every run (plan section 5).
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from PyHydroGeophysX.workflows.models import ArtifactRef, file_checksum
from PyHydroGeophysX.workflows.registry import list_workflows

from .recipes import BUILDERS, Workspace, write_recipe

#: Workflows whose smoke run (prerequisites included) takes more than ~10 s.
SLOW = {
    "ert.timelapse_inversion",
    "geo_hydrology.ert_to_wc",
    "hydro_geophysics.forward",
}
OK_STATUSES = {"ok", "success", "completed"}


@pytest.fixture(scope="module")
def workspace(tmp_path_factory: pytest.TempPathFactory, examples_data: Path) -> Workspace:
    root = tmp_path_factory.mktemp("smoke") / "冒烟 工程"
    root.mkdir()
    return Workspace(root, examples_data)


def test_every_registered_workflow_has_a_smoke_recipe() -> None:
    registered = {descriptor.workflow_id for descriptor in list_workflows()}
    assert registered == set(BUILDERS), {
        "without a recipe": sorted(registered - set(BUILDERS)),
        "recipe for an unknown workflow": sorted(set(BUILDERS) - registered),
    }


def _cases() -> list[object]:
    return [
        pytest.param(wid, marks=[pytest.mark.slow] if wid in SLOW else [], id=wid)
        for wid in sorted(d.workflow_id for d in list_workflows())
    ]


@pytest.mark.parametrize("workflow_id", _cases())
def test_workflow_runs_through_the_cli(workspace: Workspace, workflow_id: str) -> None:
    spec = BUILDERS[workflow_id](workspace)
    run_dir = workspace.root / "runs" / workflow_id
    recipe = write_recipe(spec, run_dir / "recipe.json")
    result_file = run_dir / "result.json"
    env = {**os.environ, "MPLBACKEND": "Agg", "QT_QPA_PLATFORM": "offscreen", "PYTHONUTF8": "1"}
    done = subprocess.run(
        [
            sys.executable,
            "-m",
            "PyHydroGeophysX.workflows.cli",
            "run",
            str(recipe),
            "--project-root",
            str(workspace.root),
            "--output-dir",
            str(run_dir / "outputs"),
            "--result-file",
            str(result_file),
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
        timeout=900,
        check=False,
    )
    assert done.returncode == 0, done.stderr[-4000:]
    result = json.loads(result_file.read_text(encoding="utf-8"))
    assert result["status"] in OK_STATUSES
    json.dumps({k: v for k, v in result.items() if k != "objects"}, allow_nan=False)

    for item in result["artifacts"]:
        ref = ArtifactRef.from_dict({"$artifact": item})
        path = ref.resolve(workspace.root)
        assert path.is_file(), f"{ref.artifact_id}: {path} missing"
        if ref.checksum:
            algorithm = ref.checksum.partition(":")[0]
            assert file_checksum(path, algorithm) == ref.checksum, ref.artifact_id

    provenance = result["provenance"]
    assert provenance["workflow_id"] == workflow_id
    assert provenance["environment"]["schema"] == "phgx-provenance-v1"
    assert provenance["parameters_digest"].startswith("sha256:")
