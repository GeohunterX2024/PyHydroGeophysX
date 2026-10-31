"""Every model result reaches the Model Viewer through ModelResultV2, masked by default (plan M3.5)."""

from __future__ import annotations

import contextlib
import io
from pathlib import Path
from typing import Any

import numpy as np
import pytest

pytest.importorskip("PySide6")
pytestmark = pytest.mark.gui

from PyHydroGeophysX.qt_apps.artifact_renderers import select_renderer  # noqa: E402
from PyHydroGeophysX.qt_apps.modules.model_viewer_render import model_result_view  # noqa: E402
from PyHydroGeophysX.qt_apps.widgets.model_result_view import ModelResultView  # noqa: E402
from PyHydroGeophysX.results.adapters import MODEL_WORKFLOWS  # noqa: E402
from PyHydroGeophysX.results.protocol import LayeredGeometry, ModelResultV2, Parameter  # noqa: E402
from PyHydroGeophysX.workflows.runner import MODEL_RESULT_NAME  # noqa: E402


def test_masks_are_on_by_default_and_the_caption_says_why(qtbot: Any) -> None:
    result = ModelResultV2(
        method="TDEM",
        geometry=LayeredGeometry(
            thickness=np.array([5.0, 10.0]), n_soundings=3, positions=np.array([0.0, 10.0, 20.0])
        ),
        parameters={
            "resistivity": Parameter("resistivity", np.linspace(10, 1000, 9), "ohm.m", log_scale=True),
            "conductivity": Parameter("conductivity", 1 / np.linspace(10, 1000, 9), "S/m", log_scale=True),
        },
        doi=np.array([12.0, 3.0, 30.0]),
    )
    view = ModelResultView()
    qtbot.addWidget(view)
    view.set_result(result)
    assert view._mask.isChecked()
    assert view.caption() == "Masked: blank below the depth of investigation."
    view._mask.setChecked(False)
    assert view.caption().startswith("Unmasked")
    view._parameter.setCurrentIndex(1)
    assert "conductivity [S/m]" in view._parameter.currentText()


def test_a_result_without_coverage_says_so(qtbot: Any) -> None:
    result = ModelResultV2(
        "TDEM",
        LayeredGeometry(thickness=np.array([5.0])),
        {"resistivity": Parameter("resistivity", [1.0, 2.0], "ohm.m")},
    )
    view = ModelResultView()
    qtbot.addWidget(view)
    view.set_result(result)
    assert not view._mask.isEnabled() and "every cell is shown" in view.caption()


@pytest.fixture(scope="module")
def saved_models(tmp_path_factory: pytest.TempPathFactory) -> dict[str, Path]:
    from ..smoke.recipes import Workspace

    examples = Path(__file__).resolve().parents[3] / "examples" / "data"
    if not examples.is_dir():
        pytest.skip("examples/data is not present")
    workspace = Workspace(tmp_path_factory.mktemp("models"), examples)
    saved = {}
    with contextlib.redirect_stdout(io.StringIO()):
        for workflow_id in MODEL_WORKFLOWS:
            result = workspace.prerequisite(workflow_id)
            artifact = next(a for a in result.artifacts if a.kind == "model_result_v2")
            assert select_renderer(artifact.to_dict()["$artifact"]) == "model_result"
            saved[workflow_id] = workspace.context(workflow_id).output_dir / MODEL_RESULT_NAME
    return saved


@pytest.mark.slow
@pytest.mark.parametrize("workflow_id", MODEL_WORKFLOWS)
def test_every_model_workflow_shows_in_the_viewer(
    qtbot: Any, saved_models: dict[str, Path], workflow_id: str
) -> None:
    path = saved_models[workflow_id]
    assert path.is_file()
    view = model_result_view(path)
    qtbot.addWidget(view)
    assert isinstance(view, ModelResultView)
    assert view._parameter.count() >= 1
    loaded = ModelResultV2.load(path)
    if loaded.display_mask()[0] is not None:
        assert view.caption().startswith("Masked:")
