"""Unit registry and CRS records (plan M3.3)."""

from __future__ import annotations

import numpy as np
import pytest

from PyHydroGeophysX.errors import DataValidationError
from PyHydroGeophysX.results.units import (
    UNITS,
    check_units,
    convert,
    crs_from_record,
    crs_record,
    require_unit,
)


def test_registered_units_pass_and_others_name_the_field() -> None:
    assert require_unit("rhoa", "ohm.m") == "ohm.m"
    with pytest.raises(DataValidationError) as caught:
        require_unit("rhoa", "Ohm-m")
    assert caught.value.field == "rhoa"


def test_every_parameter_needs_a_unit() -> None:
    assert check_units({"rho": "ohm.m", "m": "mV/V"}, ["rho", "m"]) == {"rho": "ohm.m", "m": "mV/V"}
    with pytest.raises(DataValidationError, match="has no unit"):
        check_units({"rho": "ohm.m"}, ["rho", "tau"])


def test_conversion_within_a_quantity_only() -> None:
    assert np.allclose(convert([10.0, 20.0], "mS/m", "S/m"), [0.01, 0.02])
    assert np.allclose(convert(2.5, "ms", "s"), 0.0025)
    assert np.allclose(convert(180.0, "deg", "rad"), np.pi)
    assert convert([1.0], "m", "m") == [1.0]
    with pytest.raises(DataValidationError, match="cannot convert"):
        convert(1.0, "ohm.m", "S/m")
    with pytest.raises(DataValidationError, match="not registered"):
        convert(1.0, "degC", "degF")


def test_quantities_have_a_base_unit() -> None:
    for quantity in {unit.quantity for unit in UNITS.values()}:
        assert any(u.factor == 1.0 for u in UNITS.values() if u.quantity == quantity), quantity


def test_cgcs2000_crs_round_trips() -> None:
    pytest.importorskip("pyproj")
    record = crs_record("EPSG:4544")
    assert record["epsg"] == 4544 and "CGCS2000" in record["name"]
    assert crs_from_record(record).to_epsg() == 4544
    with pytest.raises(DataValidationError):
        crs_record("EPSG:999999999")
