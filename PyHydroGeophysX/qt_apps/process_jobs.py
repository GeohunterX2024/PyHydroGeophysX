"""Run a workflow in a process of its own for a page's own use (plan M2.6).

A page's heavy step - a mesh build, a large forward model - runs as a
registered workflow in a child process, so a native crash or Stop ends the
child and leaves the window running. Unlike an inversion, such a step is not a
run of the Project: its recipe, result and objects go to a scratch folder, not
into the run history.
"""

from __future__ import annotations

import itertools
import json
import shutil
from pathlib import Path
from typing import Sequence

from PyHydroGeophysX.qt_apps.workers import ProcessWorkflowWorker
from PyHydroGeophysX.workflows.models import WorkflowSpec

_serial = itertools.count(1)


def scratch_process_worker(
    spec: WorkflowSpec,
    folder: str | Path,
    *,
    objects: Sequence[str] = (),
    keep_previous: bool = False,
) -> ProcessWorkflowWorker:
    """A not yet started worker running ``spec`` in a fresh subfolder of ``folder``.

    Each call gets its own subfolder, so a superseded run still being stopped
    never writes over the result of the one that replaced it. Earlier
    subfolders are removed unless ``keep_previous``.
    """
    base = Path(folder)
    if not keep_previous and base.is_dir():
        for old in base.iterdir():
            if old.is_dir():
                shutil.rmtree(old, ignore_errors=True)
    run_dir = base / f"job-{next(_serial):04d}"
    outputs = run_dir / "outputs"
    outputs.mkdir(parents=True, exist_ok=True)
    recipe = run_dir / "recipe.json"
    recipe.write_text(json.dumps(spec.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
    return ProcessWorkflowWorker(recipe, run_dir, outputs, run_dir / "result.json", objects=objects)


__all__ = ["scratch_process_worker"]
