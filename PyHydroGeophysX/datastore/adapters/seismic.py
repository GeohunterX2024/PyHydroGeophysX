"""Seismic records: ``data_processing.seismic.SeismicDataset`` <-> dataset (plan M3.1).

Traces (samples x traces) are the observations; the sample times and the
trace headers, stored column by column with their own types, are the
geometry; the SEG-Y summary goes to meta.
"""

from __future__ import annotations

import dataclasses
from typing import Any

import numpy as np

from ..dataset import Dataset

KIND = "seismic.segy"
UNITS = {
    "time": "s",
    "source_x": "m",
    "source_y": "m",
    "source_z": "m",
    "receiver_x": "m",
    "receiver_y": "m",
    "receiver_z": "m",
    "offset": "m",
}


def from_seismic_dataset(data: Any, *, raw_files: list[dict[str, Any]] | None = None) -> Dataset:
    """A dataset holding the traces, times, every trace header and the SEG-Y summary."""
    from PyHydroGeophysX.data_processing.seismic import SeismicTraceHeader

    names = [f.name for f in dataclasses.fields(SeismicTraceHeader)]
    types = {f.name: f.type for f in dataclasses.fields(SeismicTraceHeader)}
    headers = {
        name: np.array(
            [getattr(h, name) for h in data.headers], dtype=np.int64 if types[name] in (int, "int") else float
        )
        for name in names
    }
    return Dataset(
        method="SEISMIC",
        kind=KIND,
        meta={
            "path": str(data.path),
            "segy": dataclasses.asdict(data.metadata),
            "header_fields": names,
            "units": {name: unit for name, unit in UNITS.items() if name in headers or name == "time"},
        },
        geometry={"time": np.asarray(data.time), "headers": headers},
        observations={"traces": np.asarray(data.traces)},
        provenance={"adapter": "datastore.adapters.seismic", "raw_files": list(raw_files or [])},
    )


def to_seismic_dataset(dataset: Dataset) -> Any:
    """The ``SeismicDataset`` a dataset made by :func:`from_seismic_dataset` holds."""
    from PyHydroGeophysX.data_processing.seismic import SegyMetadata, SeismicDataset, SeismicTraceHeader

    columns = dataset.geometry["headers"]
    names = list(dataset.meta["header_fields"])
    count = len(columns[names[0]]) if names else 0
    headers = [SeismicTraceHeader(**{name: columns[name][i].item() for name in names}) for i in range(count)]
    return SeismicDataset(
        path=str(dataset.meta["path"]),
        traces=dataset.observations["traces"],
        time=dataset.geometry["time"],
        headers=headers,
        metadata=SegyMetadata(**dataset.meta["segy"]),
    )


__all__ = ["KIND", "from_seismic_dataset", "to_seismic_dataset"]
