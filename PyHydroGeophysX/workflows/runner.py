"""Public workflow execution entry point."""

from __future__ import annotations

import logging
from typing import Any, Mapping

from PyHydroGeophysX._internal.provenance import collect_environment, parameters_digest

from .models import ArtifactRef, RunContext, WorkflowRunResult, WorkflowSpec, iter_artifact_refs
from .registry import get_workflow

_logger = logging.getLogger(__name__)

#: File every model-producing workflow leaves in its output folder (plan M3.5).
MODEL_RESULT_NAME = "model_result.phgx.h5"


def _with_provenance(result: WorkflowRunResult, spec: WorkflowSpec, runtime: RunContext) -> None:
    """Stamp what reproduces this run on the result: inputs, seed, parameters, environment.

    The handler's own provenance keys are kept; these are added on top.
    """
    provenance = dict(result.provenance)
    provenance.setdefault("workflow_id", spec.workflow_id)
    provenance.setdefault("schema_version", spec.schema_version)
    provenance["seed"] = spec.seed
    # Not "inputs": some handlers record their input artifacts under that key.
    provenance["input_checksums"] = {
        ref.artifact_id: ref.checksum for ref in iter_artifact_refs(spec.inputs)
    }
    provenance["parameters_digest"] = parameters_digest(spec.to_dict())
    provenance["environment"] = collect_environment()
    provenance["threads"] = runtime.threads
    result.provenance = provenance


def _attach_model_result(result: WorkflowRunResult, spec: WorkflowSpec, runtime: RunContext) -> None:
    """Save the result as ModelResultV2 beside the others and register it as an artifact.

    Viewers read every model through this one protocol. A model the adapter
    cannot convert is logged and left out; the run itself has succeeded.
    """
    from PyHydroGeophysX.results.adapters import MODEL_WORKFLOWS, from_workflow_result

    if spec.workflow_id not in MODEL_WORKFLOWS or not result.objects:
        return
    try:
        converted = from_workflow_result(spec.workflow_id, result)
        converted.provenance["seed"] = spec.seed
        path = converted.save(runtime.output_dir / MODEL_RESULT_NAME)
    except (KeyError, TypeError, ValueError, AttributeError, OSError, RuntimeError):
        _logger.warning("could not save %s as ModelResultV2", spec.workflow_id, exc_info=True)
        return
    result.artifacts.append(
        ArtifactRef.from_path(path, artifact_id=f"{spec.workflow_id}:model_result", kind="model_result_v2",
                              format="h5", base_dir=runtime.project_root)
    )


def run_workflow(
    spec: WorkflowSpec | Mapping[str, Any],
    context: RunContext | None = None,
) -> WorkflowRunResult:
    """Validate and execute one registered workflow synchronously.

    spec may be a WorkflowSpec or its JSON-compatible mapping. Stochastic
    workflows require an explicit seed. context supplies the project, output
    and cache folders, the thread budget (applied around the handler), the
    progress callback and cancellation predicate; a default context
    writes under the current directory's workflow_results folder.

    The output directory is created before calling the handler. Return a
    WorkflowRunResult whose serializable view has been validated; optional
    in-process objects remain on the result. Validation, import and handler
    exceptions propagate to the caller rather than becoming a success result.
    """
    if not isinstance(spec, WorkflowSpec):
        spec = WorkflowSpec.from_dict(spec)
    descriptor = get_workflow(spec.workflow_id)
    spec.validate(stochastic=descriptor.stochastic)
    runtime = context or RunContext()
    runtime.prepare()
    runtime.progress(f"Starting {spec.workflow_id}")
    handler = descriptor.load_handler()
    with runtime.thread_limits():
        result = handler(spec, runtime)
    if not isinstance(result, WorkflowRunResult):
        raise TypeError(
            f"Workflow {spec.workflow_id!r} returned {type(result).__name__}; "
            "handlers must return WorkflowRunResult."
        )
    _attach_model_result(result, spec, runtime)
    _with_provenance(result, spec, runtime)
    result.to_dict()
    runtime.progress(f"Finished {spec.workflow_id}: {result.status}")
    return result


__all__ = ["run_workflow"]
