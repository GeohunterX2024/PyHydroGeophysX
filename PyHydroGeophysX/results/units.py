"""Units and coordinate reference systems of datasets and results (plan M3.3).

A light registry of unit strings instead of a units library: every named
parameter and observation carries one of these strings, :func:`require_unit`
rejects anything else, and :func:`convert` changes between units of one
quantity. Coordinate reference systems are stored as WKT plus EPSG code
(:func:`crs_record`), e.g. CGCS2000 / 3-degree Gauss-Kruger CM 117E is
EPSG:4544; pyproj validates them when it is installed.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Any

import numpy as np

from PyHydroGeophysX.errors import DataValidationError


@dataclass(frozen=True)
class Unit:
    """A unit symbol: the quantity it measures and its factor to that quantity's base unit."""

    symbol: str
    quantity: str
    factor: float = 1.0
    description: str = ""


_UNITS = (
    Unit("1", "dimensionless", 1.0, "ratio, count or index"),
    Unit("%", "dimensionless", 0.01, "percent"),
    Unit("ppm", "dimensionless", 1e-6, "parts per million"),
    Unit("m", "length", 1.0, "metre"),
    Unit("km", "length", 1e3, "kilometre"),
    Unit("cm", "length", 1e-2, "centimetre"),
    Unit("s", "time", 1.0, "second"),
    Unit("ms", "time", 1e-3, "millisecond"),
    Unit("us", "time", 1e-6, "microsecond"),
    Unit("ns", "time", 1e-9, "nanosecond"),
    Unit("Hz", "frequency", 1.0, "hertz"),
    Unit("kHz", "frequency", 1e3, "kilohertz"),
    Unit("ohm.m", "resistivity", 1.0, "ohm metre"),
    Unit("S/m", "conductivity", 1.0, "siemens per metre"),
    Unit("mS/m", "conductivity", 1e-3, "millisiemens per metre"),
    Unit("uS/cm", "conductivity", 1e-4, "microsiemens per centimetre (fluid conductivity)"),
    Unit("ohm", "resistance", 1.0, "ohm (transfer resistance, MT impedance)"),
    Unit("V", "voltage", 1.0, "volt"),
    Unit("mV", "voltage", 1e-3, "millivolt"),
    Unit("A", "current", 1.0, "ampere"),
    Unit("mA", "current", 1e-3, "milliampere"),
    Unit("mV/V", "chargeability", 1e-3, "millivolt per volt"),
    Unit("V/V", "chargeability", 1.0, "volt per volt"),
    Unit("mrad", "angle", 1e-3, "milliradian (IP phase)"),
    Unit("rad", "angle", 1.0, "radian"),
    Unit("deg", "angle", np.pi / 180.0, "degree"),
    Unit("m/s", "velocity", 1.0, "metre per second"),
    Unit("km/s", "velocity", 1e3, "kilometre per second"),
    Unit("s/m", "slowness", 1.0, "second per metre"),
    Unit("mGal", "acceleration", 1e-5, "milligal"),
    Unit("m/s2", "acceleration", 1.0, "metre per second squared"),
    Unit("nT", "magnetic flux density", 1e-9, "nanotesla"),
    Unit("T", "magnetic flux density", 1.0, "tesla"),
    Unit("SI", "susceptibility", 1.0, "volume susceptibility (SI)"),
    Unit("kg/m3", "density", 1.0, "kilogram per cubic metre"),
    Unit("g/cm3", "density", 1e3, "gram per cubic centimetre"),
    Unit("V/(A.m2)", "normalized voltage", 1.0, "TEM dB/dt per transmitter moment"),
    Unit("V/A", "normalized voltage", 1.0, "voltage per transmitter current"),
    Unit("mV/km/nT", "MT impedance (field units)", 1.0, "electric over magnetic field, field units"),
    Unit("m3/m3", "volumetric content", 1.0, "volumetric water content"),
    Unit("degC", "temperature", 1.0, "degree Celsius (offset scale: not converted)"),
)

#: Every registered unit, by symbol.
UNITS: dict[str, Unit] = {unit.symbol: unit for unit in _UNITS}

#: Units of quantities with an offset (no factor conversion).
_OFFSET_QUANTITIES = frozenset({"temperature"})


def is_unit(symbol: object) -> bool:
    return isinstance(symbol, str) and symbol in UNITS


def require_unit(name: str, symbol: object) -> str:
    """``symbol`` if it is a registered unit, else a :class:`DataValidationError` naming ``name``."""
    if not is_unit(symbol):
        known = ", ".join(sorted(UNITS))
        raise DataValidationError(f"unit {symbol!r} is not registered (known: {known})", field=name)
    return str(symbol)


def check_units(units: Mapping[str, object], names: Iterable[str]) -> dict[str, str]:
    """Every name in ``names`` has a registered unit in ``units``; returns the checked mapping."""
    checked: dict[str, str] = {}
    for name in names:
        if name not in units:
            raise DataValidationError("has no unit; every parameter must carry one", field=str(name))
        checked[str(name)] = require_unit(str(name), units[name])
    return checked


def convert(values: Any, from_unit: str, to_unit: str) -> Any:
    """``values`` in ``from_unit`` expressed in ``to_unit``; both must measure the same quantity."""
    source, target = UNITS[require_unit("from_unit", from_unit)], UNITS[require_unit("to_unit", to_unit)]
    if source.quantity != target.quantity:
        raise DataValidationError(
            f"cannot convert {source.quantity} ({from_unit}) to {target.quantity} ({to_unit})", field="unit"
        )
    if source.symbol == target.symbol:
        return values
    if source.quantity in _OFFSET_QUANTITIES:
        raise DataValidationError(
            f"{source.quantity} has an offset scale; convert it explicitly", field="unit"
        )
    return np.asarray(values, dtype=float) * (source.factor / target.factor)


def crs_record(crs: object) -> dict[str, Any]:
    """A JSON-ready record of a CRS: ``{"wkt", "epsg", "name"}``.

    ``crs`` is anything pyproj accepts ("EPSG:4544", an int, WKT, a
    ``pyproj.CRS``). Without pyproj only an "EPSG:<code>" string or an int is
    accepted and stored unvalidated.
    """
    try:
        from pyproj import CRS
        from pyproj.exceptions import CRSError
    except ImportError:
        text = str(crs)
        code = int(text.split(":", 1)[1]) if text.upper().startswith("EPSG:") else int(text)
        return {"wkt": "", "epsg": code, "name": f"EPSG:{code}"}
    try:
        parsed = CRS.from_user_input(crs)
    except (CRSError, TypeError, ValueError) as exc:
        raise DataValidationError(f"not a coordinate reference system: {crs!r} ({exc})", field="crs") from exc
    return {"wkt": parsed.to_wkt(), "epsg": parsed.to_epsg(), "name": parsed.name}


def crs_from_record(record: Mapping[str, Any]) -> Any:
    """The ``pyproj.CRS`` of a :func:`crs_record`."""
    from pyproj import CRS

    if record.get("wkt"):
        return CRS.from_wkt(str(record["wkt"]))
    return CRS.from_epsg(int(record["epsg"]))


__all__ = [
    "UNITS",
    "Unit",
    "check_units",
    "convert",
    "crs_from_record",
    "crs_record",
    "is_unit",
    "require_unit",
]
