"""Industry formats written and read back (plan M3.4)."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from PyHydroGeophysX.errors import DataValidationError
from PyHydroGeophysX.results.exports import (
    grid_section,
    read_cells_csv,
    read_geosoft_xyz,
    read_res2dinv_general,
    read_surfer_grd,
    write_cells_csv,
    write_geosoft_xyz,
    write_res2dinv_general,
    write_surfer_grd,
)
from PyHydroGeophysX.results.protocol import GridGeometry, LayeredGeometry, ModelResultV2, Parameter


@pytest.mark.parametrize("with_ip", [False, True])
def test_res2dinv_general_array_round_trips(tmp_path: Path, with_ip: bool) -> None:
    pytest.importorskip("pygimli")
    from pygimli.physics import ert

    data = ert.createData(elecs=np.linspace(0.0, 23.0, 24), schemeName="dd")
    rng = np.random.default_rng(3)
    data["rhoa"] = 100.0 * np.exp(rng.normal(0.0, 0.3, data.size()))
    if with_ip:
        data["ip"] = rng.uniform(1.0, 20.0, data.size())
    path = write_res2dinv_general(data, tmp_path / "line.dat")
    electrodes, table = read_res2dinv_general(path)
    sensors_x = np.array([p[0] for p in data.sensors()])
    assert np.allclose(electrodes[:, 0], sensors_x)
    for token in ("a", "b", "m", "n"):
        assert np.array_equal(table[token].to_numpy() - 1, np.asarray(data[token]).astype(int))
    assert np.allclose(table["rhoa"], np.asarray(data["rhoa"]), rtol=1e-9)
    if with_ip:
        assert np.allclose(table["ip"], np.asarray(data["ip"]), rtol=1e-9)
        assert table.attrs["ip_unit"] == "mV/V"
    else:
        assert table["ip"].isna().all()


def test_surfer_grd_round_trips_with_blanks(tmp_path: Path) -> None:
    x, y = np.linspace(0.0, 90.0, 10), np.linspace(-30.0, 0.0, 7)
    z = np.add.outer(y, x)
    z[0, :3] = np.nan
    back = read_surfer_grd(write_surfer_grd(tmp_path / "s.grd", x, y, z))
    assert np.allclose(back[0], x) and np.allclose(back[1], y)
    assert np.array_equal(np.isnan(back[2]), np.isnan(z))
    assert np.allclose(back[2], z, equal_nan=True)
    with pytest.raises(DataValidationError, match="equally spaced"):
        write_surfer_grd(tmp_path / "t.grd", np.array([0.0, 1.0, 3.0]), y, np.zeros((7, 3)))


def test_geosoft_xyz_round_trips_by_line(tmp_path: Path) -> None:
    columns = {
        "X": np.array([1.0, 2.0, 3.0, 4.0]),
        "Y": np.array([5.0, 6.0, 7.0, 8.0]),
        "rho": np.array([10.0, np.nan, 30.0, 40.0]),
    }
    path = write_geosoft_xyz(tmp_path / "a.xyz", columns, lines=[100, 100, 200, 200])
    back, lines = read_geosoft_xyz(path)
    assert list(back) == ["X", "Y", "rho"]
    for name, values in columns.items():
        assert np.allclose(back[name], values, equal_nan=True)
    assert lines.tolist() == ["100", "100", "200", "200"]


def test_cells_csv_round_trips_units_and_mask(tmp_path: Path) -> None:
    result = ModelResultV2(
        method="TDEM",
        geometry=LayeredGeometry(
            thickness=np.array([5.0, 10.0]), n_soundings=2, positions=np.array([0.0, 25.0])
        ),
        parameters={"resistivity": Parameter("resistivity", np.arange(1.0, 7.0), "ohm.m")},
        doi=np.array([12.0, 3.0]),
    )
    columns, units = read_cells_csv(write_cells_csv(tmp_path / "cells.csv", result))
    assert np.allclose(columns["resistivity"], np.arange(1.0, 7.0))
    assert units == {"distance": "m", "depth": "m", "resistivity": "ohm.m"}
    assert columns["shown"].tolist() == [1, 1, 0, 1, 0, 0]
    assert np.allclose(columns["distance"], [0, 0, 0, 25, 25, 25])
    assert np.allclose(columns["depth"], [2.5, 10.0, 20.0, 2.5, 10.0, 20.0])


def test_grid_section_blanks_what_the_mask_hides() -> None:
    grid = GridGeometry(edges=(np.linspace(0.0, 40.0, 5), np.linspace(-20.0, 0.0, 3)), axes=("x", "z"))
    values = np.arange(8.0)
    shown = np.ones(8, dtype=bool)
    shown[0] = False  # cell (x 0-10, z -20 to -10)
    result = ModelResultV2(
        "MT", grid, {"resistivity": Parameter("resistivity", values, "ohm.m")}, masks={"active": shown}
    )
    z = grid_section(result, "resistivity", nx=9, ny=5)[2]
    assert z.shape == (5, 9) and np.isnan(z[0, 0]) and z[-1, -1] == 7.0
    unmasked = grid_section(result, "resistivity", nx=9, ny=5, masked=False)[2]
    assert not np.isnan(unmasked).any()
