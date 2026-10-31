"""Heavy steps of a page run in a child process; killing it leaves the window alive (plan M2.6)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

pytest.importorskip("PySide6")
pytest.importorskip("pygimli")
pytestmark = pytest.mark.gui

from PyHydroGeophysX.qt_apps.modules import build_module  # noqa: E402
from PyHydroGeophysX.qt_apps.state import StudioState  # noqa: E402
from PyHydroGeophysX.qt_apps.workers import ProcessWorkflowWorker  # noqa: E402


@pytest.fixture
def ert_page(qtbot: Any, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, examples_data: Path) -> Any:
    monkeypatch.setenv("PHGX_PROJECT_DIR", str(tmp_path / "project"))
    monkeypatch.chdir(tmp_path)
    page = build_module("ert", StudioState.from_context(None), lambda *_: None)
    qtbot.addWidget(page)
    outcome = page.agent_apply(
        "load_data", {"path": str(examples_data / "ERT" / "Bert" / "fielddataline2.dat")}
    )
    assert outcome.get("status") == "ok", outcome
    qtbot.waitUntil(lambda: page._ert_data is not None and not page.activity(), timeout=60000)
    yield page
    page.stop_workers(wait_ms=5000)


def test_mesh_preview_is_built_in_a_child_process(qtbot: Any, ert_page: Any) -> None:
    ert_page._refresh_mesh_preview(force=True)
    assert isinstance(ert_page._mesh_worker, ProcessWorkflowWorker)
    qtbot.waitUntil(lambda: bool(ert_page._mesh_tab.preview()), timeout=120000)
    preview = ert_page._mesh_tab.preview()
    assert preview["dim"] == 2 and preview["cells"] > 0
    assert ert_page._mesh_summary()["current"]


def test_killing_the_mesh_process_leaves_the_page_running(qtbot: Any, ert_page: Any) -> None:
    ert_page._refresh_mesh_preview(force=True)
    worker = ert_page._mesh_worker
    assert isinstance(worker, ProcessWorkflowWorker)
    qtbot.waitUntil(lambda: worker.process.processId() > 0, timeout=30000)
    worker.process.kill()  # stands in for a native crash of the mesh generator
    qtbot.waitUntil(lambda: not worker.isRunning(), timeout=30000)
    qtbot.waitUntil(lambda: ert_page._mesh_preview_pending is None, timeout=30000)
    assert not ert_page._mesh_tab.preview()
    # The page still answers and can build again.
    assert isinstance(ert_page.agent_describe(), dict)
    ert_page._refresh_mesh_preview(force=True)
    qtbot.waitUntil(lambda: bool(ert_page._mesh_tab.preview()), timeout=120000)
