"""ERT/IP surveys: pyGIMLi ``DataContainerERT`` <-> dataset (plan M3.1).

Geometry holds the sensor positions and the a/b/m/n sensor indices (-1 for
none, as pyGIMLi stores them); every other token of the container goes to
observations, errors (``err``, ``iperr``, names ending in ``err``) or masks
(``valid``, as booleans). The token list and index base are kept in meta, so
the container comes back token for token.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

from PyHydroGeophysX._internal.native_paths import pygimli_path

from ..dataset import Dataset

KIND = "pygimli.DataContainerERT"
INDEX_TOKENS = ("a", "b", "m", "n")
UNITS = {
    "sensors": "m",
    "r": "ohm",
    "rhoa": "ohm.m",
    "u": "V",
    "i": "A",
    "k": "m",
    "ip": "mrad",
    "err": "1",
    "iperr": "mrad",
}


def _is_error(name: str) -> bool:
    return name == "err" or name.endswith("err")


def from_data_container(data: Any, *, raw_files: list[dict[str, Any]] | None = None) -> Dataset:
    """A dataset holding every token and sensor of ``data``."""
    fields = data.dataMap()
    names = list(fields.keys())
    geometry: dict[str, Any] = {
        "sensors": np.array([[p[0], p[1], p[2]] for p in data.sensors()], dtype=float)
    }
    observations: dict[str, Any] = {}
    errors: dict[str, Any] = {}
    masks: dict[str, Any] = {}
    for name in names:
        values = np.asarray(fields[name], dtype=float)
        if name in INDEX_TOKENS:
            geometry[name] = np.asarray(data[name]).astype(np.int64)
        elif name == "valid":
            masks["valid"] = values != 0
        elif _is_error(name):
            errors[name] = values
        else:
            observations[name] = values
    extra = getattr(data, "additionalPoints", None)
    points = (
        np.array([[p[0], p[1], p[2]] for p in extra()], dtype=float) if callable(extra) else np.zeros((0, 3))
    )
    if points.size:
        geometry["additional_points"] = points
    has_ip = "ip" in observations and bool(np.any(observations["ip"]))
    return Dataset(
        method="IP" if has_ip else "ERT",
        kind=KIND,
        meta={
            "units": {
                name: unit for name, unit in UNITS.items() if name in {*geometry, *observations, *errors}
            },
            "tokens": names,
            "token_list": str(data.tokenList()),
            "sensor_index_from_one": bool(data.sensorIndexOnFileFromOne()),
            "size": int(data.size()),
        },
        geometry=geometry,
        observations=observations,
        errors=errors,
        masks=masks,
        provenance={"adapter": "datastore.adapters.ert", "raw_files": list(raw_files or [])},
    )


def to_data_container(dataset: Dataset) -> Any:
    """The ``DataContainerERT`` a dataset made by :func:`from_data_container` holds."""
    import pygimli as pg

    data = pg.DataContainerERT()
    data.setSensorPositions(np.asarray(dataset.geometry["sensors"], dtype=float))
    data.resize(int(dataset.meta["size"]))
    for name in dataset.meta["tokens"]:
        if name in INDEX_TOKENS:
            data[name] = np.asarray(dataset.geometry[name]).astype(int)
        elif name == "valid":
            data[name] = np.asarray(dataset.masks["valid"], dtype=float)
        elif name in dataset.errors:
            data[name] = np.asarray(dataset.errors[name], dtype=float)
        else:
            data[name] = np.asarray(dataset.observations[name], dtype=float)
    points = dataset.geometry.get("additional_points")
    if points is not None and hasattr(data, "addAdditionalPoint"):
        for point in np.asarray(points, dtype=float):
            data.addAdditionalPoint(pg.Pos(*point))
    data.setSensorIndexOnFileFromOne(bool(dataset.meta.get("sensor_index_from_one", True)))
    return data


def read_file(path: str | Path, raw_files: list[dict[str, Any]] | None = None) -> Dataset:
    """Read an ERT file with pyGIMLi and wrap it."""
    import pygimli as pg

    return from_data_container(pg.DataContainerERT(pygimli_path(str(path))), raw_files=raw_files)


__all__ = ["KIND", "from_data_container", "read_file", "to_data_container"]
