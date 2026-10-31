"""EM soundings: the sounding mapping of ``workflows.em1d.load_sounding`` <-> dataset (plan M3.1).

The mapping is nested and mixes arrays, numbers, strings and tuples. Its
top-level keys are sorted into the dataset's groups - positions and system
geometry, measured values, uncertainties, and descriptive keys into meta -
and each value is kept exactly, so the mapping comes back as it was, key
order included.
"""

from __future__ import annotations

from typing import Any

from ..dataset import Dataset

KIND = "em.sounding"
GEOMETRY_KEYS = frozenset(
    {
        "positions",
        "x",
        "y",
        "longitude",
        "latitude",
        "elevation",
        "heights",
        "line_numbers",
        "station_ids",
        "average_data_ids",
        "rx_tx_distances",
        "rx_heights",
        "tx_heights",
        "system",
        "forward_metadata",
    }
)
ERROR_KEYS = frozenset({"relative_std", "uniform_error", "std", "error", "errors", "real_std", "imag_std"})
META_KEYS = frozenset(
    {
        "n_soundings",
        "sounding",
        "temcompany",
        "tem_moment",
        "source_format",
        "coordinate_system",
        "available_moments",
        "inversion_defaults",
        "protocol",
    }
)
UNITS = {
    "times": "s",
    "frequencies": "Hz",
    "positions": "m",
    "x": "m",
    "y": "m",
    "elevation": "m",
    "heights": "m",
}


def from_sounding(
    head: dict[str, Any], *, method: str = "", raw_files: list[dict[str, Any]] | None = None
) -> Dataset:
    """A dataset holding every key of a sounding mapping."""
    geometry: dict[str, Any] = {}
    observations: dict[str, Any] = {}
    errors: dict[str, Any] = {}
    extra: dict[str, Any] = {}
    for key, value in head.items():
        if key in GEOMETRY_KEYS:
            geometry[key] = value
        elif key in ERROR_KEYS:
            errors[key] = value
        elif key in META_KEYS:
            extra[key] = value
        else:
            observations[key] = value
    kind = method.upper() or ("TDEM" if "times" in head else "FDEM" if "frequencies" in head else "EM")
    return Dataset(
        method="EM",
        kind=KIND,
        meta={
            "em_method": kind,
            "key_order": list(head),
            "sounding_meta": extra,
            "units": {key: unit for key, unit in UNITS.items() if key in head},
        },
        geometry=geometry,
        observations=observations,
        errors=errors,
        provenance={"adapter": "datastore.adapters.em", "raw_files": list(raw_files or [])},
    )


def to_sounding(dataset: Dataset) -> dict[str, Any]:
    """The sounding mapping a dataset made by :func:`from_sounding` holds."""
    merged = {
        **dataset.geometry,
        **dataset.observations,
        **dataset.errors,
        **dataset.meta.get("sounding_meta", {}),
    }
    return {key: merged[key] for key in dataset.meta.get("key_order", list(merged))}


__all__ = ["KIND", "from_sounding", "to_sounding"]
