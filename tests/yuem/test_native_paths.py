"""Paths PyGIMLi's C++ core can open (findings F-16)."""

from __future__ import annotations

import os
from pathlib import Path

import numpy as np
import pytest

from PyHydroGeophysX._internal import native_paths
from PyHydroGeophysX._internal.native_paths import pygimli_path

FOLDER = "工程 数据"


def test_an_ascii_path_is_returned_as_given(tmp_path: Path) -> None:
    assert pygimli_path(tmp_path / "mesh.bms") == str(tmp_path / "mesh.bms")


@pytest.fixture
def windows(monkeypatch: pytest.MonkeyPatch) -> dict[str, str]:
    """Windows behaviour, with short names drawn from a table."""
    names: dict[str, str] = {}
    monkeypatch.setattr(native_paths, "_WINDOWS", True)
    monkeypatch.setattr(native_paths, "_short_name", lambda path: names.get(str(path)))
    return names


def test_the_folder_of_an_ascii_file_name_gets_its_short_name(
    tmp_path: Path, windows: dict[str, str]
) -> None:
    folder = tmp_path / FOLDER
    windows[str(folder)] = "C:\\TMP\\9F1C~1"

    assert pygimli_path(folder / "mesh.bms") == os.path.join("C:\\TMP\\9F1C~1", "mesh.bms")


def test_a_non_ascii_file_name_gets_its_own_short_name(tmp_path: Path, windows: dict[str, str]) -> None:
    target = tmp_path / "剖面.dat"
    windows[str(target)] = "C:\\TMP\\5A2B~1.DAT"

    assert pygimli_path(target) == "C:\\TMP\\5A2B~1.dat"
    assert not target.exists()


def test_a_file_about_to_be_written_is_created_for_its_short_name(
    tmp_path: Path, windows: dict[str, str]
) -> None:
    target = tmp_path / "剖面.dat"
    windows[str(target)] = "C:\\TMP\\5A2B~1.DAT"

    assert pygimli_path(target, create=True) == "C:\\TMP\\5A2B~1.dat"
    assert target.is_file()


def test_a_suffix_the_short_name_cuts_leaves_the_path_as_it_was(
    tmp_path: Path, windows: dict[str, str]
) -> None:
    target = tmp_path / "剖面.json"
    windows[str(target)] = "C:\\TMP\\5A2B~1.JSO"

    assert pygimli_path(target) == str(target)


def test_without_short_names_the_path_is_left_as_it_was(tmp_path: Path, windows: dict[str, str]) -> None:
    target = tmp_path / FOLDER / "mesh.bms"

    assert pygimli_path(target) == str(target)


def test_pygimli_reads_and_writes_in_a_non_ascii_folder(tmp_path: Path) -> None:
    pg = pytest.importorskip("pygimli")
    folder = tmp_path / FOLDER
    folder.mkdir()
    mesh = pg.createGrid(np.arange(4.0), np.arange(3.0))
    data = pg.DataContainerERT()
    for x in range(4):
        data.createSensor([float(x), 0.0, 0.0])
    data.createFourPointData(0, 0, 1, 2, 3)

    mesh.save(pygimli_path(folder / "mesh.bms"))
    data.save(pygimli_path(folder / "data.dat"))
    mesh.exportVTK(pygimli_path(folder / "mesh.vtk"))
    mesh.save(pygimli_path(folder / "网格.bms", create=True))

    assert pg.load(pygimli_path(folder / "mesh.bms")).cellCount() == mesh.cellCount()
    assert pg.load(pygimli_path(folder / "网格.bms")).cellCount() == mesh.cellCount()
    assert pg.DataContainerERT(pygimli_path(folder / "data.dat")).size() == 1
    assert (folder / "mesh.vtk").stat().st_size > 0
