"""Golden regression cases (plan M1.4).

A case runs one smoke recipe in-process and reduces the result to named numeric
arrays: every ``.npy``/``.npz`` artifact, the numeric columns of every ``.csv``
artifact, and the run's numeric metrics. ``tools/yuem/golden.py`` records them
under ``tests/yuem/golden/data/``; ``test_golden.py`` compares a fresh run with
the record.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from PyHydroGeophysX.workflows.models import ArtifactRef, RunContext, WorkflowRunResult
from PyHydroGeophysX.workflows.runner import run_workflow

from ..smoke.recipes import BUILDERS, Workspace

DATA = Path(__file__).resolve().parent / "data"


@dataclass(frozen=True)
class GoldenCase:
    name: str
    workflow_id: str
    rtol: float
    atol: float
    note: str


CASES: tuple[GoldenCase, ...] = (
    GoldenCase("ert_single", "ert.single_inversion", 1e-6, 1e-9, "fielddataline2.dat, 2 iterations"),
    GoldenCase("ert_timelapse", "ert.timelapse_inversion", 1e-6, 1e-9, "three synthetic surveys"),
    GoldenCase(
        "srt",
        "seismic.srt_inversion",
        1e-3,
        1e-9,
        "srtfieldline2.dat, 2 iterations; pyGIMLi ray tracing varies ~1e-4 run to run",
    ),
    GoldenCase("fdem_sounding", "em.inversion", 1e-6, 1e-12, "synthetic FDEM sounding"),
    GoldenCase("tem_lci_line", "em.line_inversion", 1e-6, 1e-12, "LM+HM line, 3 soundings"),
    GoldenCase("mt_occam1d", "mt.invert_1d", 1e-8, 1e-12, "NMX20 EMTF XML"),
    GoldenCase("mt_processing", "mt.process", 1e-8, 1e-12, "synthetic time series"),
    GoldenCase("gravity_inversion", "gravmag.invert", 1e-6, 1e-12, "seeded SimPEG inversion"),
    GoldenCase("fdem_tdem_joint", "joint_inversion.run", 1e-6, 1e-12, "shared conductivity"),
    GoldenCase("gravity_processing", "gravmag.process", 1e-10, 1e-12, "QC grids"),
)
BY_NAME = {case.name: case for case in CASES}


def _csv_columns(path: Path) -> dict[str, np.ndarray]:
    with path.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.reader(stream))
    if len(rows) < 2:
        return {}
    header, body = rows[0], rows[1:]
    columns: dict[str, np.ndarray] = {}
    for index, name in enumerate(header):
        try:
            values = np.array([float(row[index]) for row in body if index < len(row)], dtype=float)
        except ValueError:
            continue
        columns[name] = values
    return columns


def reduce_result(result: WorkflowRunResult, root: Path) -> dict[str, np.ndarray]:
    """Named numeric arrays of a result: artifacts plus metrics, in a stable order."""
    arrays: dict[str, np.ndarray] = {}
    for artifact in result.artifacts:
        path = ArtifactRef.resolve(artifact, root)
        stem = artifact.artifact_id.replace(":", "_").replace("/", "_")
        suffix = path.suffix.lower()
        if suffix == ".npy":
            arrays[stem] = np.asarray(np.load(path, allow_pickle=False), dtype=float)
        elif suffix == ".npz":
            with np.load(path, allow_pickle=False) as archive:
                for key in archive.files:
                    value = archive[key]
                    if np.issubdtype(value.dtype, np.number):
                        arrays[f"{stem}.{key}"] = np.asarray(value, dtype=float)
        elif suffix == ".csv":
            for column, values in _csv_columns(path).items():
                arrays[f"{stem}.{column}"] = values
    for key, value in result.metrics.items():
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            arrays[f"metric.{key}"] = np.asarray([float(value)])
    # Models a handler keeps in memory rather than writing (e.g. a 1D sounding).
    for prefix, mapping in (("object", result.objects), ("summary", result.summary)):
        for key, value in mapping.items():
            numeric = _numeric(value)
            if numeric is not None:
                arrays[f"{prefix}.{key}"] = numeric
    return dict(sorted(arrays.items()))


def _numeric(value: object) -> np.ndarray | None:
    """A float array for numeric arrays and number lists; None for anything else."""
    if isinstance(value, bool):
        return None
    if isinstance(value, np.ndarray) and np.issubdtype(value.dtype, np.number):
        return np.asarray(value, dtype=float)
    if (
        isinstance(value, (list, tuple))
        and value
        and all(isinstance(item, (int, float)) and not isinstance(item, bool) for item in value)
    ):
        return np.asarray(value, dtype=float)
    return None


def compute(case: GoldenCase, workspace: Workspace) -> dict[str, np.ndarray]:
    spec = BUILDERS[case.workflow_id](workspace)
    context = RunContext(project_root=workspace.root, output_dir=workspace.root / "golden" / case.name)
    result = run_workflow(spec, context)
    return reduce_result(result, workspace.root)
