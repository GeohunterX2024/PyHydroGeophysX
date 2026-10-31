"""The project database of PyHydroGeophysX: dataset schema ``phgx-dataset-v1`` (plan M3.1).

* :class:`Dataset` - one version of a survey's observations in six groups
  (meta, geometry, observations, errors, masks, provenance), saved as HDF5.
* :class:`DatasetStore` - immutable versions under ``<project>/datasets``,
  shared arrays linked rather than copied, a rebuildable JSON index, and
  read-only raw-file references with sha256.
* :mod:`.adapters` - ERT (pyGIMLi DataContainer), EM soundings, MT transfer
  functions and SEG-Y datasets to and from datasets, losslessly.
"""

from __future__ import annotations

from .adapters import from_dataset, to_dataset
from .dataset import GROUPS, SCHEMA, Dataset, external_files
from .store import DatasetStore, DatasetVersion, sha256_of

__all__ = [
    "GROUPS",
    "SCHEMA",
    "Dataset",
    "DatasetStore",
    "DatasetVersion",
    "external_files",
    "from_dataset",
    "sha256_of",
    "to_dataset",
]
