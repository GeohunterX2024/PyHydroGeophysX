"""The Streamlit bridge behaves as before after leaving StudioState (plan M2.7)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from PyHydroGeophysX.qt_apps.state import RESULT_FILENAME, StudioState


@pytest.fixture
def context_file(tmp_path: Path) -> Path:
    folder = tmp_path / "qt_bridge"
    folder.mkdir()
    path = folder / "context.json"
    path.write_text(
        json.dumps(
            {
                "app_key": "hydro",
                "project_root": str(tmp_path / "proj"),
                "output_dir": str(tmp_path / "out"),
                "hydro_data_dir": str(tmp_path / "hydro"),
                "hydro_output_dir": str(tmp_path / "hydro_out"),
                "initial_module": "ert",
                "demo_mode": True,
            }
        ),
        encoding="utf-8",
    )
    return path


def test_context_sets_paths_module_and_result_file(context_file: Path, tmp_path: Path) -> None:
    state = StudioState.from_context(str(context_file))
    assert state.context_path == context_file
    assert state.context["app_key"] == "hydro"
    assert state.project_root == tmp_path / "proj"
    assert state.output_dir == tmp_path / "out"
    assert state.hydro_data_dir == tmp_path / "hydro"
    assert state.hydro_output_dir == tmp_path / "hydro_out"
    assert state.selected_module == "ert"
    assert state.result_path == context_file.parent / RESULT_FILENAME
    assert not state.default_project
    summary = state.context_summary()
    assert summary["app_key"] == "hydro" and summary["demo_mode"] is True
    assert summary["result_path"] == str(context_file.parent / RESULT_FILENAME)


def test_missing_or_broken_context_gives_an_empty_one(tmp_path: Path) -> None:
    broken = tmp_path / "context.json"
    broken.write_text("{not json", encoding="utf-8")
    state = StudioState.from_context(str(broken))
    assert state.context == {}
    assert state.selected_module == "home"
    assert state.result_path == tmp_path / RESULT_FILENAME


def test_standalone_uses_the_default_project(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PHGX_PROJECT_DIR", str(tmp_path / "default"))
    state = StudioState.from_context(None)
    assert state.context_path is None and state.context == {}
    assert state.default_project
    assert state.output_dir == tmp_path / "default"
    assert state.result_path == tmp_path / "default" / "qt_bridge" / RESULT_FILENAME


def test_save_result_writes_the_document_streamlit_reads(context_file: Path) -> None:
    state = StudioState.from_context(str(context_file))
    state.update_module_result("ert", {"rms": 1.2})
    state.update_workflow_result("ert", "ert.single_inversion", {"status": "ok"}, recipe_path="r.json")
    path = state.save_result()
    assert path == context_file.parent / RESULT_FILENAME
    document = json.loads(path.read_text(encoding="utf-8"))
    assert document["app"] == "PyHydroGeophysX Professional Studio"
    assert document["status"] == "saved"
    assert document["selected_module"] == "ert"
    assert document["context_path"] == str(context_file)
    assert document["module_results"] == {"ert": {"rms": 1.2}}
    assert document["workflow_id"] == "ert.single_inversion"
    assert document["recipe_path"] == "r.json"
    assert document["workflow_results"]["ert"]["result"] == {"status": "ok"}
    assert "created_time" in document


def test_opening_a_project_moves_the_standalone_result_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("PHGX_PROJECT_DIR", str(tmp_path / "default"))
    state = StudioState.from_context(None)
    store = state.set_results_store(tmp_path / "Survey 2026")
    assert state.output_dir == store.root
    assert state.result_path == store.root / "qt_bridge" / RESULT_FILENAME


def test_opening_a_project_keeps_the_bridge_result_file(context_file: Path, tmp_path: Path) -> None:
    state = StudioState.from_context(str(context_file))
    state.set_results_store(tmp_path / "Survey 2026")
    assert state.result_path == context_file.parent / RESULT_FILENAME
