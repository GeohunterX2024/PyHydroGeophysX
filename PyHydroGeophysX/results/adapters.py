"""Existing result types -> ModelResultV2 (plan M3.2).

One function per result type the package produces:

* :func:`from_model_result` - ``inversion.model_result.ModelResult`` and
  PyGIMLi managers (ERT, SRT): mesh, model, response, coverage;
* :func:`from_inversion_result` - ``inversion.base.InversionResult``;
* :func:`from_em1d_result` - ``TDEMInversionResult`` / ``FDEMInversionResult``;
* :func:`from_lci_result` - ``em1d_lci.LCIResult`` (laterally constrained line);
* :func:`from_occam1d_result` - MT ``Occam1DResult``;
* :func:`from_mt_profile_result` - MT ``ProfileInversionResult`` (2-D);
* :func:`from_gravmag_payload` - the mapping ``inversion.gravmag.invert_gravmag`` returns;
* :func:`from_em_sounding_payload` / :func:`from_em_line_payload` - the objects
  of the ``em.inversion`` and ``em.line_inversion`` workflows;
* :func:`from_workflow_result` - any model-producing workflow's result, by id.

Meshes are read through the PyGIMLi mesh interface (``positions``, ``cells``,
``cellCenters``, ``dim``) without importing PyGIMLi here; the mesh object is
kept in ``native["mesh"]`` for viewers that draw it directly.
"""

from __future__ import annotations

from typing import Any

import numpy as np

from .protocol import DataFit, GridGeometry, LayeredGeometry, MeshGeometry, ModelResultV2, Parameter


def mesh_geometry(mesh: Any) -> MeshGeometry:
    """The geometry of a PyGIMLi mesh (or anything with its interface)."""
    dim = int(mesh.dim())
    nodes = np.array([[p[0], p[1], p[2]] for p in mesh.positions()], dtype=float)[:, :dim]
    cells_nodes = [[node.id() for node in cell.nodes()] for cell in mesh.cells()]
    width = max((len(c) for c in cells_nodes), default=0)
    cells = np.full((len(cells_nodes), width), -1, dtype=np.int64)
    for row, ids in enumerate(cells_nodes):
        cells[row, : len(ids)] = ids
    centers = np.array([[p[0], p[1], p[2]] for p in mesh.cellCenters()], dtype=float)[:, :dim]
    return MeshGeometry(nodes=nodes, cells=cells, cell_centers=centers, dim=dim)


def _coverage(source: Any) -> np.ndarray | None:
    method = getattr(source, "coverage", None)
    if method is None:
        return None
    try:
        value = method() if callable(method) else method
    except (AttributeError, RuntimeError, ValueError):
        return None
    return None if value is None else np.asarray(value, dtype=float)


def from_model_result(result: Any, *, method: str = "ERT", data: Any = None) -> ModelResultV2:
    """A mesh result: ERT resistivity, or SRT velocity when the result has one.

    ``result`` is a ``ModelResult`` or a fitted PyGIMLi manager (``paraDomain``,
    ``model``, optional ``coverage()`` and ``response``). ``data`` (a data
    container with ``rhoa``/``err`` or ``t``/``err``) fills the fit.
    """
    mesh = result.paraDomain
    geometry = mesh_geometry(mesh)
    velocity = getattr(result, "velocity", None)
    is_srt = method.upper() in ("SRT", "SEISMIC") or velocity is not None
    if is_srt and velocity is not None:
        parameters = {"velocity": Parameter("velocity", np.asarray(velocity), "m/s")}
    else:
        parameters = {
            "resistivity": Parameter("resistivity", np.asarray(result.model), "ohm.m", log_scale=True)
        }
    fit = None
    response = getattr(result, "response", None)
    if response is not None:
        fit = DataFit(predicted=np.asarray(response, dtype=float))
        if data is not None:
            key = "t" if is_srt else "rhoa"
            if data.haveData(key):
                fit.observed = np.asarray(data[key], dtype=float)
            if data.haveData("err"):
                err = np.asarray(data["err"], dtype=float)
                fit.error = err if is_srt else err * np.abs(fit.observed if fit.observed is not None else 1.0)
    return ModelResultV2(
        method="SRT" if is_srt else method.upper(),
        geometry=geometry,
        parameters=parameters,
        fit=fit,
        coverage=_coverage(result),
        coverage_kind="rays" if is_srt else "log10_sensitivity",
        provenance={"adapter": "results.adapters.from_model_result", "source": type(result).__name__},
        native={"mesh": mesh, "source": result},
    )


def from_inversion_result(result: Any, *, method: str = "ERT") -> ModelResultV2:
    """``InversionResult``: final model on its mesh, coverage, posterior std, chi² history."""
    std = getattr(result, "model_log_std", None)
    parameter = Parameter(
        "resistivity",
        np.asarray(result.final_model),
        "ohm.m",
        log_scale=True,
        std=None if std is None else np.asarray(std),
        std_log10=std is not None,
    )
    history = [{"iteration": i + 1, "chi2": float(c)} for i, c in enumerate(result.iteration_chi2 or [])]
    predicted = getattr(result, "predicted_data", None)
    return ModelResultV2(
        method=method.upper(),
        geometry=mesh_geometry(result.mesh),
        parameters={"resistivity": parameter},
        fit=None
        if predicted is None
        else DataFit(
            predicted=np.asarray(predicted, dtype=float), chi2=history[-1]["chi2"] if history else None
        ),
        coverage=None if result.coverage is None else np.asarray(result.coverage, dtype=float),
        history=history,
        meta=dict(result.meta or {}),
        provenance={"adapter": "results.adapters.from_inversion_result", "source": type(result).__name__},
        native={"mesh": result.mesh, "source": result},
    )


def from_em1d_result(result: Any, *, method: str = "") -> ModelResultV2:
    """``TDEMInversionResult`` or ``FDEMInversionResult``: one layered sounding."""
    conductivity = np.asarray(result.recovered_conductivity, dtype=float).ravel()
    kind = method.upper() or ("FDEM" if hasattr(result, "frequencies") else "TDEM")
    history = [
        {"iteration": i + 1, "phi_d": float(v)}
        for i, v in enumerate(getattr(result, "convergence_history", []) or [])
    ]
    predicted = getattr(result, "predicted_data", None)
    return ModelResultV2(
        method=kind,
        geometry=LayeredGeometry(
            thickness=np.asarray(result.thicknesses, dtype=float).ravel(), n_soundings=1
        ),
        parameters={
            "resistivity": Parameter("resistivity", 1.0 / conductivity, "ohm.m", log_scale=True),
            "conductivity": Parameter("conductivity", conductivity, "S/m", log_scale=True),
        },
        fit=None
        if predicted is None
        else DataFit(
            predicted=np.asarray(predicted, dtype=float),
            chi2=None if result.chi2 is None else float(result.chi2),
        ),
        history=history,
        provenance={"adapter": "results.adapters.from_em1d_result", "source": type(result).__name__},
        native={"source": result},
    )


def from_lci_result(
    result: Any,
    *,
    thickness: Any,
    positions: Any = None,
    doi: Any = None,
    method: str = "TDEM",
) -> ModelResultV2:
    """``LCIResult``: a laterally constrained line of layered soundings.

    ``thickness`` is the layer thicknesses the line was inverted with; ``doi``
    the depth of investigation per sounding, when computed.
    """
    models = np.asarray(result.models, dtype=float)
    n_soundings = models.shape[0]
    per_sounding = np.asarray(result.chi2_per_sounding, dtype=float)
    history = [{"iteration": i + 1, "chi2": float(c)} for i, c in enumerate(result.chi2_history)]
    return ModelResultV2(
        method=method.upper(),
        geometry=LayeredGeometry(
            thickness=np.asarray(thickness, dtype=float),
            n_soundings=n_soundings,
            positions=None if positions is None else np.asarray(positions, dtype=float),
        ),
        parameters={"resistivity": Parameter("resistivity", models.ravel(), "ohm.m", log_scale=True)},
        fit=DataFit(chi2=float(result.chi2)),
        doi=None if doi is None else np.asarray(doi, dtype=float),
        history=history,
        meta={
            "chi2_per_sounding": per_sounding,
            "iterations": int(result.iterations),
            "stop_reason": str(result.stop_reason),
            "lambda_vertical": float(result.lambda_vertical),
            "lambda_lateral": float(result.lambda_lateral),
        },
        provenance={"adapter": "results.adapters.from_lci_result", "source": type(result).__name__},
        native={"source": result},
    )


def from_occam1d_result(result: Any) -> ModelResultV2:
    """MT ``Occam1DResult``: layered resistivity, static shifts per mode, fit per mode."""
    shifts = dict(result.static_shift or {})
    observed, predicted, error, groups = [], [], [], {}
    start = 0
    sounding = result.sounding
    for k, mode in enumerate(sounding.modes):
        pred = result.predicted.get(mode) if isinstance(result.predicted, dict) else None
        if not isinstance(pred, dict):
            continue
        for quantity, obs, err in (
            ("log_rho", sounding.log_rho[k], sounding.log_rho_err[k]),
            ("phase", sounding.phase[k], sounding.phase_err[k]),
        ):
            values = np.asarray(pred.get(quantity, np.full(len(obs), np.nan)), dtype=float)
            observed.append(np.asarray(obs, dtype=float))
            predicted.append(values)
            error.append(np.asarray(err, dtype=float))
            groups[f"{mode}.{quantity}"] = np.arange(start, start + len(values))
            start += len(values)
    fit = DataFit(
        observed=np.concatenate(observed) if observed else None,
        predicted=np.concatenate(predicted) if predicted else None,
        error=np.concatenate(error) if error else None,
        groups=groups,
        chi2=float(result.rms) ** 2,
    )
    return ModelResultV2(
        method="MT",
        geometry=LayeredGeometry(thickness=np.asarray(result.thickness, dtype=float), n_soundings=1),
        parameters={
            "resistivity": Parameter("resistivity", np.asarray(result.resistivity), "ohm.m", log_scale=True)
        },
        fit=fit,
        history=[dict(h) for h in result.history],
        meta={
            "rms": float(result.rms),
            "static_shift": {str(m): float(v) for m, v in shifts.items()},
            "station": str(getattr(sounding, "station", "")),
            "converged": bool(result.converged),
        },
        provenance={"adapter": "results.adapters.from_occam1d_result", "source": type(result).__name__},
        native={"source": result},
    )


def from_mt_profile_result(result: Any) -> ModelResultV2:
    """MT ``ProfileInversionResult``: the 2-D section on its tensor mesh, air and padding masked."""
    mesh = result.profile.mesh
    full = np.full(int(mesh.n_cells), np.nan)
    active = np.asarray(result.profile.active)
    full[active] = np.asarray(result.resistivity, dtype=float)
    shown = np.zeros(int(mesh.n_cells), dtype=bool)
    shown[active] = True
    return ModelResultV2(
        method="MT",
        geometry=GridGeometry(edges=(np.asarray(mesh.nodes_x), np.asarray(mesh.nodes_y)), axes=("x", "z")),
        parameters={"resistivity": Parameter("resistivity", full, "ohm.m", log_scale=True)},
        fit=DataFit(chi2=float(result.rms) ** 2),
        masks={"active": shown},
        history=[dict(h) for h in result.history],
        meta={
            "rms": float(result.rms),
            "modes": list(result.modes),
            "frequencies": np.asarray(result.frequencies),
        },
        provenance={"adapter": "results.adapters.from_mt_profile_result", "source": type(result).__name__},
        native={"source": result},
    )


def from_gravmag_payload(payload: dict[str, Any]) -> ModelResultV2:
    """The mapping ``invert_gravmag`` returns: a 3-D density contrast or susceptibility grid."""
    edges = tuple(np.asarray(e, dtype=float) for e in payload["edges"])
    gravity = str(payload.get("kind", "gravity")).lower().startswith("grav")
    name, unit = ("density_contrast", "g/cm3") if gravity else ("susceptibility", "SI")
    model = np.asarray(payload["model3d"], dtype=float).ravel(order="F")
    fit_raw = payload.get("fit") or {}
    fit = DataFit(
        observed=None if "observed" not in fit_raw else np.asarray(fit_raw["observed"], dtype=float),
        predicted=None if "predicted" not in fit_raw else np.asarray(fit_raw["predicted"], dtype=float),
        error=None if "std" not in fit_raw else np.asarray(fit_raw["std"], dtype=float),
        chi2=None if payload.get("chi2") is None else float(payload["chi2"]),
    )
    return ModelResultV2(
        method="GRAVITY" if gravity else "MAGNETIC",
        geometry=GridGeometry(edges=edges, axes=("x", "y", "z")),
        parameters={name: Parameter(name, model, unit)},
        fit=fit,
        meta={key: payload[key] for key in ("label", "n_data") if key in payload},
        provenance={"adapter": "results.adapters.from_gravmag_payload"},
    )


def from_em_sounding_payload(objects: dict[str, Any], summary: dict[str, Any] | None = None) -> ModelResultV2:
    """The ``em.inversion`` workflow's objects: one layered sounding and its fit."""
    summary = dict(summary or {})
    resistivity = np.asarray(objects["resistivity"], dtype=float)
    parts = [key for key in ("real", "imag") if f"obs_{key}" in objects and f"pred_{key}" in objects]
    observed = [np.asarray(objects[f"obs_{key}"], dtype=float) for key in parts]
    predicted = [np.asarray(objects[f"pred_{key}"], dtype=float) for key in parts]
    groups: dict[str, np.ndarray] = {}
    start = 0
    for key, values in zip(parts, observed, strict=True):
        groups[key] = np.arange(start, start + values.size)
        start += values.size
    if "fit_mask" in objects:
        groups["fitted"] = np.flatnonzero(np.asarray(objects["fit_mask"], dtype=bool))
    method = str(summary.get("method") or ("FDEM" if "frequencies" in objects else "TDEM")).upper()
    return ModelResultV2(
        method=method,
        geometry=LayeredGeometry(thickness=np.asarray(objects["thickness"], dtype=float), n_soundings=1),
        parameters={"resistivity": Parameter("resistivity", resistivity, "ohm.m", log_scale=True)},
        fit=DataFit(
            observed=np.concatenate(observed) if observed else None,
            predicted=np.concatenate(predicted) if predicted else None,
            groups=groups,
            chi2=None if summary.get("chi2") is None else float(summary["chi2"]),
        ),
        meta={key: summary[key] for key in ("label",) if key in summary},
        provenance={"adapter": "results.adapters.from_em_sounding_payload"},
    )


def from_em_line_payload(objects: dict[str, Any], summary: dict[str, Any] | None = None) -> ModelResultV2:
    """The ``em.line_inversion`` workflow's objects: soundings along a line, with DOI."""
    summary = dict(summary or {})
    thickness = np.asarray(objects["thickness"], dtype=float)
    model = np.asarray(objects["model3d"], dtype=float)
    n_soundings = model.shape[0]
    values = model.reshape(n_soundings, -1)

    def optional(key: str) -> np.ndarray | None:
        return None if objects.get(key) is None else np.asarray(objects[key], dtype=float)

    return ModelResultV2(
        method=str(summary.get("method", "TDEM")).upper(),
        geometry=LayeredGeometry(
            thickness=thickness,
            n_soundings=n_soundings,
            positions=optional("positions"),
            x=optional("x"),
            y=optional("y"),
            elevation=optional("surface_elevation"),
        ),
        parameters={"resistivity": Parameter("resistivity", values.ravel(), "ohm.m", log_scale=True)},
        fit=DataFit(chi2=None if summary.get("chi2") is None else float(summary["chi2"])),
        doi=optional("doi"),
        meta={
            "sensitivity": optional("sensitivity"),
            "station_ids": None if objects.get("station_ids") is None else np.asarray(objects["station_ids"]),
            **{
                key: summary[key] for key in ("coordinate_system", "doi_threshold", "label") if key in summary
            },
        },
        provenance={"adapter": "results.adapters.from_em_line_payload"},
    )


def from_timelapse_objects(objects: dict[str, Any], summary: dict[str, Any] | None = None) -> ModelResultV2:
    """The ``ert.timelapse_inversion`` workflow's objects: one resistivity parameter per time step.

    Steps are named ``resistivity_step0``, ``resistivity_step1``, ...; their
    labels (survey times) are in ``meta["steps"]``. The coverage shown is the
    least of the steps', so a cell is masked when any survey leaves it
    unconstrained.
    """
    summary = dict(summary or {})
    mesh = objects["mesh"]
    models = np.asarray(objects["final_models"], dtype=float)
    if models.ndim == 1:
        models = models[:, None]
    labels = [str(label) for label in (summary.get("time_labels") or range(models.shape[1]))]
    parameters = {
        f"resistivity_step{k}": Parameter(
            f"resistivity_step{k}",
            models[:, k],
            "ohm.m",
            log_scale=True,
            description=labels[k] if k < len(labels) else "",
        )
        for k in range(models.shape[1])
    }
    coverage = objects.get("coverage")
    least = None if coverage is None else np.min(np.atleast_2d(np.asarray(coverage, dtype=float)), axis=0)
    return ModelResultV2(
        method="ERT",
        geometry=mesh_geometry(mesh),
        parameters=parameters,
        coverage=least,
        meta={"steps": labels, "time_lapse": True},
        provenance={"adapter": "results.adapters.from_timelapse_objects"},
        native={"mesh": mesh},
    )


#: The workflows whose results :func:`from_workflow_result` converts.
MODEL_WORKFLOWS = (
    "ert.single_inversion",
    "ert.timelapse_inversion",
    "seismic.srt_inversion",
    "em.inversion",
    "em.line_inversion",
    "mt.invert_1d",
    "mt.invert_profile",
    "gravmag.invert",
)


def from_workflow_result(workflow_id: str, result: Any) -> ModelResultV2:
    """A model-producing workflow's ``WorkflowRunResult`` (its objects and summary) as a ModelResultV2."""
    objects = dict(getattr(result, "objects", {}) or {})
    summary = dict(getattr(result, "summary", {}) or {})
    if workflow_id in ("ert.single_inversion", "seismic.srt_inversion"):
        method = "SRT" if workflow_id.startswith("seismic") else "ERT"
        converted = from_model_result(objects["manager"], method=method)
    elif workflow_id == "ert.timelapse_inversion":
        converted = from_timelapse_objects(objects, summary)
    elif workflow_id == "em.inversion":
        converted = from_em_sounding_payload(objects, summary)
    elif workflow_id == "em.line_inversion":
        converted = from_em_line_payload(objects, summary)
    elif workflow_id == "mt.invert_1d":
        converted = from_occam1d_result(objects["result"])
    elif workflow_id == "mt.invert_profile":
        converted = from_mt_profile_result(objects["result"])
    elif workflow_id == "gravmag.invert":
        converted = from_gravmag_payload(
            {**objects, "kind": summary.get("kind", "gravity"), "chi2": summary.get("chi2")}
        )
    else:
        raise TypeError(f"workflow {workflow_id!r} has no ModelResultV2 adapter")
    converted.provenance.setdefault("workflow_id", workflow_id)
    return converted


def to_model_result_v2(result: Any, **options: Any) -> ModelResultV2:
    """Dispatch on the result's type to the adapter above."""
    if isinstance(result, ModelResultV2):
        return result
    name = type(result).__name__
    if isinstance(result, dict) and "model3d" in result:
        return from_gravmag_payload(result)
    if name in ("TDEMInversionResult", "FDEMInversionResult"):
        return from_em1d_result(result, **options)
    if name == "LCIResult":
        return from_lci_result(result, **options)
    if name == "Occam1DResult":
        return from_occam1d_result(result)
    if name == "ProfileInversionResult":
        return from_mt_profile_result(result)
    if hasattr(result, "final_model") and hasattr(result, "mesh"):
        return from_inversion_result(result, **options)
    if hasattr(result, "paraDomain") and hasattr(result, "model"):
        return from_model_result(result, **options)
    raise TypeError(f"no ModelResultV2 adapter for {name}")


__all__ = [
    "MODEL_WORKFLOWS",
    "from_em1d_result",
    "from_em_line_payload",
    "from_em_sounding_payload",
    "from_gravmag_payload",
    "from_inversion_result",
    "from_lci_result",
    "from_model_result",
    "from_mt_profile_result",
    "from_occam1d_result",
    "from_timelapse_objects",
    "from_workflow_result",
    "mesh_geometry",
    "to_model_result_v2",
]
