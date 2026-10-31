"""The ERT page's mesh builds as workflows, so they run in a process of their own (plan M2.6).

Triangle, TetGen and PyGIMLi's mesh generators are native code: a crash there
in a thread of the Studio takes the window with it, and a large 3-D build
holds the GIL for seconds. As workflows the Studio runs them with
``ProcessWorkflowWorker``, which a crash or Stop ends without touching the
window.

* ``ert.mesh_build`` - the inversion mesh the next run would build (the Mesh
  tab's preview); the mesh and the data it was built around come back as
  objects.
* ``ert.e4d_mesh`` - an E4D configuration's mesh, built once and saved as
  ``.bms`` for the inversion to use.
"""

from __future__ import annotations

import inspect
from pathlib import Path
from typing import Any, Dict

from PyHydroGeophysX.errors import DataValidationError

from .models import ArtifactRef, RunContext, WorkflowRunResult, WorkflowSpec

#: What ``ert.mesh_build`` is built around.
MESH_BUILD_KINDS = ("single", "timelapse", "mesh")


def run_ert_mesh_build(spec: WorkflowSpec, context: RunContext) -> WorkflowRunResult:
    """Build the inversion mesh as the ERT runs build theirs.

    ``kind`` "single": ``inputs.data`` is the survey saved with the page's
    electrode edits applied. "timelapse": ``inputs.data`` is the first survey of
    the series, read with ``parameters.instrument`` and placed from
    ``inputs.electrodes`` when given. "mesh": only an imported mesh
    (``options.mesh_file``). ``parameters.options`` are the keywords of
    ``build_inversion_mesh``.
    """
    from PyHydroGeophysX.data_processing import ert_io
    from PyHydroGeophysX.inversion.ert_mesh import build_inversion_mesh

    parameters = dict(spec.parameters)
    kind = str(parameters.get("kind", ""))
    if kind not in MESH_BUILD_KINDS:
        raise DataValidationError(f"kind must be one of {MESH_BUILD_KINDS}, got {kind!r}", field="kind")
    options: Dict[str, Any] = dict(parameters.get("options") or {})
    accepted = set(inspect.signature(build_inversion_mesh).parameters) - {"data", "log", "report"}
    unknown = sorted(set(options) - accepted)
    if unknown:
        raise DataValidationError(f"unknown mesh options {unknown}; known: {sorted(accepted)}", field="options")
    data = None
    if kind in ("single", "timelapse"):
        reference = spec.inputs.get("data")
        if not isinstance(reference, ArtifactRef):
            raise DataValidationError("ert.mesh_build needs inputs.data as an ArtifactRef.", field="data")
        path = context.resolve_artifact(reference)
        if kind == "single":
            data = ert_io.load_ert_container(str(path), instrument=None)
        else:
            electrodes = spec.inputs.get("electrodes")
            data = ert_io.load_ert_container(
                str(path),
                instrument=parameters.get("instrument"),
                electrode_file=(
                    str(context.resolve_artifact(electrodes)) if isinstance(electrodes, ArtifactRef) else None
                ),
            )
    context.progress("Building the inversion mesh")
    report: Dict[str, Any] = {}
    mesh = build_inversion_mesh(data, **options, log=context.progress, report=report)
    objects: Dict[str, Any] = {"mesh": mesh}
    if data is not None:
        objects["data"] = data
    return WorkflowRunResult(
        status="completed",
        summary={
            "kind": kind,
            "cells": int(mesh.cellCount()),
            "nodes": int(mesh.nodeCount()),
            "build": {str(k): v for k, v in report.items() if isinstance(v, (str, int, float, bool))},
        },
        objects=objects,
    )


def run_ert_e4d_mesh(spec: WorkflowSpec, context: RunContext) -> WorkflowRunResult:
    """Build ``inputs.config``'s mesh, as E4D would, and save it as ``<name>.bms`` in the output folder."""
    from PyHydroGeophysX.core.e4d_mesh import build_e4d_mesh, read_e4d_config

    reference = spec.inputs.get("config")
    if not isinstance(reference, ArtifactRef):
        raise DataValidationError("ert.e4d_mesh needs inputs.config as an ArtifactRef.", field="config")
    config_path = context.resolve_artifact(reference)
    name = str(spec.parameters.get("name") or Path(config_path).stem)
    context.progress(f"Building the mesh {config_path.name} describes")
    built = build_e4d_mesh(read_e4d_config(config_path), context.output_dir, name=name)
    target = Path(context.output_dir) / f"{name}.bms"
    built["mesh"].save(str(target))
    return WorkflowRunResult(
        status="completed",
        summary={"mesher": str(built["mesher"]), "mesh_path": str(target), "cells": int(built["mesh"].cellCount())},
        artifacts=[ArtifactRef.from_path(target, artifact_id="ert:e4d_mesh", kind="mesh", format="bms")],
    )


__all__ = ["MESH_BUILD_KINDS", "run_ert_e4d_mesh", "run_ert_mesh_build"]
