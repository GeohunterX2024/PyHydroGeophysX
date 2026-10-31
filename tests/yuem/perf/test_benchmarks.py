"""Timing of key workflows against a per-machine baseline (plan M5.3).

Run with ``tools/yuem/perf.py``, which records or checks the baseline; plain
pytest skips these (marker ``benchmark``). Each workload is a full workflow
run as a user starts it, with the example data.
"""

from __future__ import annotations

import contextlib
import io
from pathlib import Path
from typing import Any

import pytest

from PyHydroGeophysX.workflows.models import RunContext, WorkflowSpec
from PyHydroGeophysX.workflows.runner import run_workflow

from ..smoke.recipes import BUILDERS, Workspace

pytestmark = pytest.mark.benchmark


def _spec(workspace: Workspace, workflow_id: str, **parameters: Any) -> WorkflowSpec:
    base = BUILDERS[workflow_id](workspace)
    return WorkflowSpec(base.workflow_id, base.inputs, {**base.parameters, **parameters}, seed=base.seed)


#: Workload name -> (workflow, parameters over the smoke recipe's).
WORKLOADS: dict[str, tuple[str, dict[str, Any]]] = {
    # The ERT page's defaults on fielddataline2.dat: about 10 s on the reference machine.
    "ert_single_inversion": ("ert.single_inversion", {"max_iterations": 20, "max_total_iterations": 40}),
    "tem_lci_line": ("em.line_inversion", {"max_soundings": 9}),
    "mt_occam1d": ("mt.invert_1d", {"max_iterations": 20}),
}


@pytest.mark.parametrize("name", sorted(WORKLOADS))
def test_workflow_timing(benchmark: Any, tmp_path: Path, examples_data: Path, name: str) -> None:
    workflow_id, parameters = WORKLOADS[name]
    workspace = Workspace(tmp_path, examples_data)
    spec = _spec(workspace, workflow_id, **parameters)
    runs = iter(range(1000))

    def run() -> Any:
        output = tmp_path / f"run{next(runs)}"
        with contextlib.redirect_stdout(io.StringIO()):
            return run_workflow(spec, RunContext(project_root=tmp_path, output_dir=output))

    result = benchmark.pedantic(run, rounds=3, iterations=1, warmup_rounds=0)
    assert result.status in ("ok", "completed", "success")
