"""PyVista datasets of a survey scene: built without a window, as the VTK export writes them."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from PyHydroGeophysX.survey.scene import SceneOptions, build_scene

from ..survey import synth

pv = pytest.importorskip("pyvista")
pytestmark = pytest.mark.gui


def test_scene_becomes_pyvista_datasets(tmp_path: Path) -> None:
    from PyHydroGeophysX.qt_apps.widgets.survey.render_pyvista import scene_datasets

    scene = build_scene(synth.layout(), synth.pseudo(), SceneOptions(group="s1", colour_by="rho_a"))
    datasets = scene_datasets(pv, scene)
    assert {"terrain", "pseudo", "links", "points:electrode"} <= set(datasets)
    cloud = datasets["pseudo"]
    assert cloud.n_points == synth.pseudo().size
    np.testing.assert_allclose(cloud.point_data["value"], synth.pseudo().attrs["rho_a"])
    assert datasets["links"].n_cells == 2
    assert datasets["terrain"].n_points > 10
    blocks = pv.MultiBlock()
    for name, data in datasets.items():
        blocks[name] = data
    path = tmp_path / "scene.vtm"
    blocks.save(str(path))
    assert pv.read(str(path)).n_blocks == len(datasets)
