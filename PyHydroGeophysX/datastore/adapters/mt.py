"""MT sites: ``data_processing.mt.TransferFunction`` <-> dataset (plan M3.1)."""

from __future__ import annotations

import dataclasses
from typing import Any

import numpy as np

from ..dataset import Dataset

KIND = "mt.transfer_function"
OBSERVATION_FIELDS = ("z", "tipper")
ERROR_FIELDS = (
    "z_err",
    "tipper_err",
    "inverse_signal_power",
    "z_residual_covariance",
    "tipper_residual_covariance",
)
SITE_FIELDS = ("station", "latitude", "longitude", "elevation", "x", "y", "declination")
UNITS = {"frequency": "Hz", "z": "ohm", "z_err": "ohm", "tipper": "1", "tipper_err": "1", "rotation": "deg"}


def from_transfer_function(tf: Any, *, raw_files: list[dict[str, Any]] | None = None) -> Dataset:
    """A dataset holding every field of ``tf``; fields that are None are left out."""
    present = {f.name: getattr(tf, f.name) for f in dataclasses.fields(tf)}
    return Dataset(
        method="MT",
        kind=KIND,
        meta={
            "site": {name: present[name] for name in SITE_FIELDS},
            "metadata": dict(present.get("metadata") or {}),
            "units": {name: unit for name, unit in UNITS.items() if present.get(name) is not None},
        },
        geometry={"frequency": np.asarray(tf.frequency), "rotation": np.asarray(tf.rotation)},
        observations={name: present[name] for name in OBSERVATION_FIELDS if present[name] is not None},
        errors={name: present[name] for name in ERROR_FIELDS if present[name] is not None},
        provenance={"adapter": "datastore.adapters.mt", "raw_files": list(raw_files or [])},
    )


def to_transfer_function(dataset: Dataset) -> Any:
    """The ``TransferFunction`` a dataset made by :func:`from_transfer_function` holds."""
    from PyHydroGeophysX.data_processing.mt.transfer_function import TransferFunction

    fields: dict[str, Any] = {
        "frequency": dataset.geometry["frequency"],
        "rotation": dataset.geometry["rotation"],
        **{name: dataset.observations.get(name) for name in OBSERVATION_FIELDS},
        **{name: dataset.errors.get(name) for name in ERROR_FIELDS},
        **dataset.meta["site"],
        "metadata": dict(dataset.meta.get("metadata") or {}),
    }
    return TransferFunction(**fields)


__all__ = ["KIND", "from_transfer_function", "to_transfer_function"]
