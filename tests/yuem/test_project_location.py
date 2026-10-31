"""A Project's folder is checked against the source tree (finding F-10)."""

from __future__ import annotations

from pathlib import Path

import pytest

import PyHydroGeophysX
from PyHydroGeophysX.qt_apps.state import StudioState, project_location_problem

PACKAGE = Path(PyHydroGeophysX.__file__).resolve().parent


def test_inside_the_package_is_refused(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    assert project_location_problem(PACKAGE / "my_project")[0] == "error"  # type: ignore[index]
    monkeypatch.setenv("PHGX_PROJECT_DIR", str(tmp_path / "default"))
    state = StudioState.from_context(None)
    with pytest.raises(ValueError, match="inside the PyHydroGeophysX package"):
        state.set_results_store(PACKAGE / "my_project")


def test_examples_warn_and_elsewhere_is_fine(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    examples = PACKAGE.parent / "examples"
    if (PACKAGE.parent / "pyproject.toml").is_file():
        assert project_location_problem(examples / "survey")[0] == "warn"  # type: ignore[index]
    assert project_location_problem(tmp_path / "Survey 2026") is None
    monkeypatch.setenv("PHGX_PROJECT_DIR", str(tmp_path / "default"))
    state = StudioState.from_context(None)
    state.set_results_store(tmp_path / "Survey 2026")
    assert state.project_warning == ""
