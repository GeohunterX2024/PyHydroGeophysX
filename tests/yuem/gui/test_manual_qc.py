"""Reject, restore and record ERT readings on the pseudosection (plan M4.4)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pytest

pytest.importorskip("PySide6")
pg = pytest.importorskip("pygimli")
pytestmark = pytest.mark.gui

from PyHydroGeophysX.datastore import DatasetStore  # noqa: E402
from PyHydroGeophysX.qt_apps.modules import build_module  # noqa: E402
from PyHydroGeophysX.qt_apps.state import StudioState  # noqa: E402


@pytest.fixture
def dd_survey(tmp_path: Path) -> Path:
    from pygimli.physics import ert

    data = ert.createData(elecs=np.linspace(0.0, 23.0, 24), schemeName="dd")
    data["rhoa"] = 100.0 * np.exp(np.random.default_rng(5).normal(0.0, 0.2, data.size()))
    data["err"] = np.full(data.size(), 0.03)
    path = tmp_path / "line_dd.dat"
    data.save(str(path))
    return path


def test_rejected_readings_leave_the_survey_and_are_recorded(
    qtbot: Any, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, dd_survey: Path
) -> None:
    monkeypatch.setenv("PHGX_PROJECT_DIR", str(tmp_path / "project"))
    monkeypatch.chdir(tmp_path)
    page = build_module("ert", StudioState.from_context(None), lambda *_: None)
    qtbot.addWidget(page)
    assert page.agent_apply("load_data", {"path": str(dd_survey)}).get("status") == "ok"
    qtbot.waitUntil(lambda: page._ert_data is not None and not page.activity(), timeout=60000)
    total = int(page._ert_data_full.size())
    assert page._manual_qc is not None and len(page._manual_qc.keys) == total

    # Drag a box over the shallow readings on the left, reject them.
    xy = page._manual_points()
    page._qc_select.setChecked(True)
    chosen = page._qc_box.select_box(-1.0, 0.0, 6.0, 1.5)
    assert chosen and all(xy[i, 0] <= 6.0 and xy[i, 1] <= 1.5 for i in chosen)
    page._qc_bar._reason.setText("contact problem at electrodes 1-3")
    page._qc_bar._decide("reject")
    assert int(page._ert_data.size()) == total - len(chosen)
    assert not any(page._qc_mask[i] for i in chosen)

    # The automatic filter and Reset keep the readings rejected by hand.
    page._apply_filter()
    assert not any(page._qc_mask[i] for i in chosen)
    page._reset_filter()
    assert int(page._ert_data.size()) == total - len(chosen)

    record = page._manual_qc_record()
    assert record is not None and sorted(record["rejected"]) == sorted(chosen)
    assert record["decisions"][0]["reason"] == "contact problem at electrodes 1-3"

    # Saved with the data: a dataset version holding the mask and the decisions.
    message = page._save_qc_record(page._manual_qc)
    assert "version 1" in message
    store = DatasetStore(page.state.ensure_results_store().root)
    saved = store.load(store.entries()[0].dataset_id)
    assert (~saved.masks["manual_qc"]).sum() == len(chosen)
    assert saved.provenance["qc"][0]["reason"] == "contact problem at electrodes 1-3"
    assert saved.provenance["raw_files"][0]["sha256"]

    # Undo, then restore everything.
    page._qc_bar._take_back()
    assert int(page._ert_data.size()) == total
    page._qc_bar._decide("reject")
    page._manual_qc.restore_all("all fine after all")
    page._on_manual_qc_changed()
    assert int(page._ert_data.size()) == total
    page.stop_workers(wait_ms=5000)


def test_em_gates_are_rejected_by_moment_and_time(qtbot: Any) -> None:
    from PyHydroGeophysX.qt_apps.widgets.em_gate_view import EMGateView

    times = np.array([1e-5, 2e-5, 4e-5])
    moment = {
        "times": times,
        "open": times * 0.9,
        "close": times * 1.1,
        "values": np.array([3.0, 2.0, 1.0]),
        "relative_std": np.full(3, 0.05),
        "flags": np.zeros(3),
        "status": np.array(["kept"] * 3, dtype=object),
    }
    view = EMGateView()
    qtbot.addWidget(view)
    view.set_report({"station": "S1", "moments": {"LM": dict(moment), "HM": dict(moment)}})
    view._table.sortItems(2)  # sorted by centre time: rows no longer follow the moments
    row = next(
        r
        for r in range(view._table.rowCount())
        if view._table.item(r, 0).text() == "HM" and view._table.item(r, 1).text() == "3"
    )
    view._table.selectRow(row)
    view._qc_bar._decide("reject")
    assert view.rejected_gates() == {"HM": [4e-5]}
    verdicts = [view._table.item(r, 8).text() for r in range(view._table.rowCount())]
    assert verdicts.count("rejected by hand") == 1
    view.set_report({"station": "S2", "moments": {"LM": dict(moment)}})
    assert view.rejected_gates() == {}
    view.set_report({"station": "S1", "moments": {"LM": dict(moment), "HM": dict(moment)}})
    assert view.rejected_gates() == {"HM": [4e-5]}  # kept per station


def test_mt_frequencies_are_rejected_by_period(qtbot: Any, examples_data: Path) -> None:
    from matplotlib.figure import Figure

    from PyHydroGeophysX.data_processing.mt.io import read_transfer_function
    from PyHydroGeophysX.qt_apps.modules.mt_qc import MTFrequencyQC

    tf = read_transfer_function(examples_data / "MT" / "NMX20.xml")
    redraws: list[int] = []
    qc = MTFrequencyQC(lambda: redraws.append(1))
    qtbot.addWidget(qc)
    axes = Figure().subplots(2, 1, sharex=True)
    qc.attach(axes, tf)
    periods = np.sort(1.0 / np.asarray(tf.frequency))
    qc._span.select_span(periods[0] * 0.99, periods[2] * 1.01)
    qc.bar._decide("reject")
    rejected = qc.rejected_frequencies(tf)
    assert len(rejected) == 3 and redraws == [1]
    assert np.allclose(sorted(1.0 / np.asarray(rejected)), periods[:3])
