"""The seismic 3-D model's optional render cannot take the run down (findings F-22)."""

from __future__ import annotations

from pathlib import Path

from PyHydroGeophysX.Geophy_modular.structure_integration import _render_in_child


def test_a_render_that_fails_in_its_child_process_reports_why(tmp_path: Path) -> None:
    shot = tmp_path / "volume_3d.png"

    problem = _render_in_child(tmp_path / "missing.vtk", tmp_path / "missing.npz", shot)

    assert problem.startswith("exit code ")
    assert not shot.exists()
