"""One version of a dataset in the project database: schema ``phgx-dataset-v1`` (plan M3.1).

A dataset is the observations of one survey or sounding set, in six groups,
after DCIP's ``dcip-line-v3``:

* ``meta`` - method, adapter kind, units of the named fields, CRS, labels;
* ``geometry`` - sources, receivers, sensors, positions, sampling axes;
* ``observations`` - measured values;
* ``errors`` - their uncertainties;
* ``masks`` - which values are used;
* ``provenance`` - read-only raw files with sha256, adapter, processing steps.

Each group is a tree (:mod:`.tree`), so every adapter round-trips its object
losslessly. A saved version is immutable; arrays a new version shares with
its base are external links into the base, not copies.
"""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np

from PyHydroGeophysX.errors import DataValidationError
from PyHydroGeophysX.results.units import require_unit

from .tree import Origins, read_tree, write_tree

SCHEMA = "phgx-dataset-v1"
READABLE = (SCHEMA,)
GROUPS = ("meta", "geometry", "observations", "errors", "masks", "provenance")
METHODS = ("ERT", "IP", "EM", "MT", "SEISMIC", "GPR", "GRAVITY", "MAGNETIC", "OTHER")


@dataclass
class Dataset:
    """A dataset in memory. ``origins`` maps each array to where a saved version keeps it."""

    method: str
    kind: str
    meta: dict[str, Any] = field(default_factory=dict)
    geometry: dict[str, Any] = field(default_factory=dict)
    observations: dict[str, Any] = field(default_factory=dict)
    errors: dict[str, Any] = field(default_factory=dict)
    masks: dict[str, Any] = field(default_factory=dict)
    provenance: dict[str, Any] = field(default_factory=dict)
    origins: Origins = field(default_factory=dict, repr=False, compare=False)

    @property
    def units(self) -> dict[str, str]:
        return dict(self.meta.get("units") or {})

    def validate(self) -> None:
        """Method known, units registered, CRS a record, masks boolean."""
        if self.method not in METHODS:
            raise DataValidationError(f"method must be one of {METHODS}, got {self.method!r}", field="method")
        if not self.kind:
            raise DataValidationError("kind (the adapter that made the dataset) is required", field="kind")
        for name, unit in self.units.items():
            require_unit(f"meta.units.{name}", unit)
        crs = self.meta.get("crs")
        if crs is not None and not (isinstance(crs, Mapping) and ("wkt" in crs or "epsg" in crs)):
            raise DataValidationError("must be a record from results.units.crs_record", field="meta.crs")
        for key_path, mask in _arrays(self.masks):
            if mask.dtype != np.bool_:
                where = ".".join(("masks", *key_path))
                raise DataValidationError(f"masks must be boolean, got {mask.dtype}", field=where)

    def save(self, path: str | Path, *, base: Dataset | None = None) -> Path:
        """Write this version to ``path``, which must not exist yet; returns it resolved.

        Arrays equal to ``base``'s (which must have been saved or loaded) are
        linked to where ``base`` keeps them. The file is written beside its
        destination and moved into place, then made read-only.
        """
        import h5py

        self.validate()
        target = Path(path).resolve()
        if target.exists():
            raise FileExistsError(f"dataset versions are immutable: {target} exists")
        target.parent.mkdir(parents=True, exist_ok=True)
        partial = target.with_name(f".{target.name}.partial")
        lookup = _base_lookup(base)
        origins: Origins = {}
        try:
            with h5py.File(partial, "w") as handle:
                handle.attrs["schema"] = SCHEMA
                handle.attrs["method"] = self.method
                handle.attrs["kind"] = self.kind
                for name in GROUPS:
                    write_tree(
                        handle.create_group(name),
                        getattr(self, name),
                        path=(name,),
                        file=target,
                        base=lookup,
                        origins=origins,
                    )
            os.replace(partial, target)
        finally:
            if partial.exists():
                partial.unlink()
        target.chmod(0o444)
        self.origins = origins
        return target

    @classmethod
    def load(cls, path: str | Path) -> Dataset:
        import h5py

        source = Path(path).resolve()
        origins: Origins = {}
        with h5py.File(source, "r") as handle:
            schema = str(handle.attrs.get("schema", ""))
            if schema not in READABLE:
                raise DataValidationError(
                    f"schema {schema!r} is not readable ({', '.join(READABLE)})", file=source
                )
            groups = {
                name: read_tree(handle[name], path=(name,), file=source, origins=origins) for name in GROUPS
            }
            dataset = cls(method=str(handle.attrs["method"]), kind=str(handle.attrs["kind"]), **groups)
        dataset.origins = origins
        return dataset


def _arrays(tree: Any, prefix: tuple[str, ...] = ()) -> list[tuple[tuple[str, ...], np.ndarray]]:
    """Every array in a tree, with its key path (keys as :mod:`.tree` records them)."""
    found: list[tuple[tuple[str, ...], np.ndarray]] = []
    if isinstance(tree, Mapping):
        items: list[tuple[Any, Any]] = list(tree.items())
    elif isinstance(tree, (list, tuple)):
        items = list(enumerate(tree))
    else:
        items = []
    for key, value in items:
        key_path = (*prefix, str(key))
        if isinstance(value, np.ndarray):
            found.append((key_path, value))
        elif isinstance(value, (Mapping, list, tuple)):
            found += _arrays(value, key_path)
    return found


def _base_lookup(base: Dataset | None) -> Any:
    """Where ``base`` keeps the array at a key path, with the array, or None."""
    if base is None or not base.origins:
        return None
    arrays: dict[tuple[str, ...], np.ndarray] = {}
    for group in GROUPS:
        for key_path, array in _arrays(getattr(base, group), (group,)):
            arrays[key_path] = array

    def lookup(key_path: tuple[str, ...]) -> tuple[np.ndarray, tuple[str, str]] | None:
        array, origin = arrays.get(key_path), base.origins.get(key_path)
        return (array, origin) if array is not None and origin is not None else None

    return lookup


def external_files(path: str | Path) -> list[Path]:
    """Files a saved version links into, resolved."""
    dataset = Dataset.load(path)
    own = str(Path(path).resolve())
    return sorted({Path(file) for file, _ in dataset.origins.values() if file != own})


__all__ = ["GROUPS", "METHODS", "READABLE", "SCHEMA", "Dataset", "external_files"]
