"""Reject, restore, record (plan M4.4): the log, datasets, and what inversions receive."""

from __future__ import annotations

import contextlib
import io
from pathlib import Path

import numpy as np
import pytest

from PyHydroGeophysX.datastore import Dataset, DatasetStore
from PyHydroGeophysX.datastore.qc import QCLog
from PyHydroGeophysX.errors import DataValidationError
from PyHydroGeophysX.workflows.qc_masks import blank_rejected_mt, drop_rejected_em


def test_the_mask_is_the_replay_of_the_decisions() -> None:
    log = QCLog(range(6), name="valid_manual")
    log.reject_at([1, 2, 4], reason="spikes in the pseudosection")
    log.restore([2], reason="looked again")
    assert log.mask.tolist() == [True, False, True, True, False, True]
    assert log.rejected() == [1, 4]
    assert log.undo() is not None and log.rejected() == [1, 2, 4]
    log.restore_all()
    assert log.mask.all() and len(log.decisions) == 2
    with pytest.raises(DataValidationError):
        log.reject([99])


def test_keys_can_be_moments_and_times_and_survive_json() -> None:
    log = QCLog([("LM", 1.2e-5), ("LM", 2.4e-5), ("HM", 1.0e-4)], name="gates")
    log.reject([("HM", 1.0e-4)], reason="noisy late gate", criterion="tail cut")
    again = QCLog.from_record(log.to_record())
    assert again.rejected() == [("HM", 1.0e-4)]
    assert again.decisions[0].criterion == "tail cut" and again.decisions[0].reason == "noisy late gate"


def test_decisions_go_into_the_dataset_masks_and_provenance(tmp_path: Path) -> None:
    store = DatasetStore(tmp_path)
    dataset = Dataset("ERT", "test.qc", observations={"rhoa": np.arange(1.0, 6.0)})
    log = QCLog(range(5))
    log.reject_at([0, 3], reason="electrode 4 lost contact")
    log.write_to(dataset)
    log.restore([0], reason="false alarm")
    log.write_to(dataset)  # the mask's history is replaced, not duplicated
    saved = store.load(store.put(dataset, "line-1").dataset_id)
    assert saved.masks["manual_qc"].tolist() == [True, True, True, False, True]
    history = saved.provenance["qc"]
    assert [entry["action"] for entry in history] == ["reject", "restore"]
    assert history[0]["keys"] == [0, 3] and history[0]["reason"] == "electrode 4 lost contact"


def test_rejected_gates_leave_a_copy_of_the_sounding() -> None:
    sounding = {
        "times": np.array([1e-5, 2e-5, 4e-5, 8e-5]),
        "response": np.array([4.0, 3.0, 2.0, 1.0]),
        "relative_std": np.full(4, 0.05),
        "uniform_error": 0.03,
    }
    trimmed, removed = drop_rejected_em(sounding, {"": [4.0000001e-5]})
    assert removed == 1 and trimmed["times"].tolist() == [1e-5, 2e-5, 8e-5]
    assert trimmed["response"].tolist() == [4.0, 3.0, 1.0] and trimmed["uniform_error"] == 0.03
    assert sounding["times"].size == 4  # the cached original is untouched
    joint = {"moments": {"LM": dict(sounding), "HM": dict(sounding)}}
    trimmed, removed = drop_rejected_em(joint, {"HM": [8e-5, 1e-5]})
    assert (
        removed == 2
        and trimmed["moments"]["HM"]["times"].size == 2
        and trimmed["moments"]["LM"]["times"].size == 4
    )
    fdem = {"frequencies": np.array([100.0, 1000.0]), "real": np.ones(2), "imag": np.ones(2)}
    assert drop_rejected_em(fdem, {"FDEM": [1000.0]})[0]["real"].size == 1


def test_rejected_frequencies_become_missing(examples_data: Path) -> None:
    from PyHydroGeophysX.data_processing.mt.io import read_transfer_function

    tf = read_transfer_function(examples_data / "MT" / "NMX20.xml")
    picked = [float(tf.frequency[3]), float(tf.frequency[7])]
    blanked, count = blank_rejected_mt(tf, picked)
    assert count == 2 and np.isnan(blanked.z[3]).all() and np.isfinite(blanked.z[4]).all()
    assert np.isfinite(tf.z[3]).all()  # the original is untouched


@pytest.mark.slow
def test_inversions_leave_out_what_was_rejected(tmp_path: Path, examples_data: Path) -> None:
    from PyHydroGeophysX.workflows.models import RunContext, WorkflowSpec
    from PyHydroGeophysX.workflows.runner import run_workflow

    from .smoke.recipes import BUILDERS, Workspace

    workspace = Workspace(tmp_path, examples_data)
    base = BUILDERS["mt.invert_1d"](workspace)
    with contextlib.redirect_stdout(io.StringIO()):
        full = run_workflow(base, RunContext(project_root=tmp_path, output_dir=tmp_path / "full"))
        frequencies = np.asarray(full.objects["result"].sounding.frequency)
        spec = WorkflowSpec(
            base.workflow_id, base.inputs, {**base.parameters, "rejected_frequencies": list(frequencies[:3])}
        )
        trimmed = run_workflow(spec, RunContext(project_root=tmp_path, output_dir=tmp_path / "trimmed"))
    used = lambda r: int(np.isfinite(np.asarray(r.objects["result"].sounding.log_rho)).sum())  # noqa: E731
    assert used(trimmed) < used(full)
