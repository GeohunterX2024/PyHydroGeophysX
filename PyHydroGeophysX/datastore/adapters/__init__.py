"""Adapters between the package's data objects and datasets (plan M3.1).

:func:`to_dataset` picks the adapter by the object's type; :func:`from_dataset`
by the dataset's ``kind``. Plugins can add their own with :func:`register`.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from ..dataset import Dataset
from . import em, ert, mt, seismic


@dataclass(frozen=True)
class Adapter:
    kind: str
    #: True for objects this adapter converts.
    accepts: Callable[[Any], bool]
    to_dataset: Callable[..., Dataset]
    from_dataset: Callable[[Dataset], Any]


def _type_name(obj: Any) -> str:
    return type(obj).__name__


ADAPTERS: dict[str, Adapter] = {}


def register(adapter: Adapter) -> None:
    """Add (or replace) the adapter of ``adapter.kind``."""
    ADAPTERS[adapter.kind] = adapter


register(
    Adapter(
        ert.KIND,
        lambda o: _type_name(o) in {"DataContainerERT", "DataContainer"},
        ert.from_data_container,
        ert.to_data_container,
    )
)
register(
    Adapter(
        mt.KIND,
        lambda o: _type_name(o) == "TransferFunction",
        mt.from_transfer_function,
        mt.to_transfer_function,
    )
)
register(
    Adapter(
        seismic.KIND,
        lambda o: _type_name(o) == "SeismicDataset",
        seismic.from_seismic_dataset,
        seismic.to_seismic_dataset,
    )
)
register(
    Adapter(
        em.KIND,
        lambda o: isinstance(o, dict) and ("times" in o or "frequencies" in o),
        em.from_sounding,
        em.to_sounding,
    )
)


def to_dataset(obj: Any, **options: Any) -> Dataset:
    """The dataset of ``obj``, by the first adapter that accepts it."""
    for adapter in ADAPTERS.values():
        if adapter.accepts(obj):
            return adapter.to_dataset(obj, **options)
    raise TypeError(f"no dataset adapter for {type(obj).__name__}")


def from_dataset(dataset: Dataset) -> Any:
    """The object a dataset holds, by its ``kind``."""
    adapter = ADAPTERS.get(dataset.kind)
    if adapter is None:
        raise TypeError(f"no dataset adapter for kind {dataset.kind!r}")
    return adapter.from_dataset(dataset)


__all__ = ["ADAPTERS", "Adapter", "from_dataset", "register", "to_dataset"]
