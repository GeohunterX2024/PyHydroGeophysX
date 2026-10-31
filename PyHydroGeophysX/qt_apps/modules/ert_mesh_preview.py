"""The ERT page's Mesh tab: build in a child process, derive the preview in a thread (plan M2.6).

The build is ``ert.mesh_build`` (``workflows.mesh_jobs``), which runs the
mesh generator the inversions use in a process of its own. The preview - the
cell outlines, counts and, for a volume, the PyVista parts - is derived from
the mesh it hands back, which is array work and stays in the Studio.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

import numpy as np

from PyHydroGeophysX.data_processing.ert_io import save_edited_ert_container
from PyHydroGeophysX.workflows.models import ArtifactRef, WorkflowRunResult, WorkflowSpec


def mesh_build_spec(
    kind: str,
    source: Any,
    instrument: Optional[str],
    electrodes: Any,
    options: Dict[str, Any],
    scratch: Path,
) -> WorkflowSpec:
    """The ``ert.mesh_build`` recipe for one preview request of the page.

    "single": ``source`` is the loaded survey and ``electrodes`` the page's
    electrode rows; the survey is saved with those edits applied, as the run
    saves it. "timelapse": ``source`` is the series' first file and
    ``electrodes`` the electrode file, if any. "mesh": an imported mesh only.
    """
    inputs: Dict[str, Any] = {}
    if kind == "single":
        path = save_edited_ert_container(source, Path(scratch) / "mesh_preview_data.dat", electrodes)
        inputs["data"] = ArtifactRef.from_path(Path(path), artifact_id="ert:mesh_preview_data", kind="ert_data")
    elif kind == "timelapse":
        inputs["data"] = ArtifactRef.from_path(Path(source), artifact_id="ert:mesh_preview_first", kind="ert_data")
        if electrodes:
            inputs["electrodes"] = ArtifactRef.from_path(
                Path(electrodes), artifact_id="ert:electrode_file", kind="electrode_layout"
            )
    return WorkflowSpec(
        workflow_id="ert.mesh_build",
        inputs=inputs,
        parameters={"kind": kind, "instrument": instrument, "options": dict(options)},
        metadata={"source": "qt", "purpose": "mesh preview"},
    )


def derive_preview(result: WorkflowRunResult) -> Dict[str, Any]:
    """What the Mesh tab draws, from the mesh and data ``ert.mesh_build`` handed back."""
    from PyHydroGeophysX.inversion.ert_mesh import mesh_preview

    mesh = result.objects["mesh"]
    data = result.objects.get("data")
    preview = mesh_preview(mesh, data)
    preview["build"] = dict(result.summary.get("build") or {})
    if preview["dim"] == 3:
        # A volume of a few hundred thousand cells takes seconds; without
        # PyVista the tab says so and the counts still show.
        from PyHydroGeophysX.qt_apps.widgets.mesh_preview import volume_parts

        try:
            preview.update(volume_parts(mesh))
        except Exception as exc:  # noqa: BLE001 - the counts still show
            preview["grid_error"] = str(exc)
    if data is not None and data.haveData("rhoa"):
        rhoa = np.asarray(data["rhoa"], dtype=float)
        rhoa = rhoa[np.isfinite(rhoa) & (rhoa > 0)]
        preview["median_rhoa"] = float(np.median(rhoa)) if rhoa.size else None
    return preview


__all__ = ["derive_preview", "mesh_build_spec"]
