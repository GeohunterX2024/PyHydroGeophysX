"""Project database: lossless round trips, linked versions, moves, index, raw files (plan M3.1)."""

from __future__ import annotations

import dataclasses
import json
import shutil
from pathlib import Path
from typing import Any

import numpy as np
import pytest

from PyHydroGeophysX.datastore import Dataset, DatasetStore, external_files, from_dataset, to_dataset
from PyHydroGeophysX.errors import DataValidationError


def _equal(a: Any, b: Any) -> bool:
    """Deep equality with NaN == NaN, exact dtypes and container types."""
    if isinstance(a, np.ndarray) or isinstance(b, np.ndarray):
        if not (isinstance(a, np.ndarray) and isinstance(b, np.ndarray)):
            return False
        if a.dtype != b.dtype or a.shape != b.shape:
            return False
        return bool(np.array_equal(a, b, equal_nan=a.dtype.kind in "fc"))
    if isinstance(a, dict):
        return isinstance(b, dict) and list(a) == list(b) and all(_equal(a[k], b[k]) for k in a)
    if isinstance(a, (list, tuple)):
        return (
            type(a) is type(b) and len(a) == len(b) and all(_equal(x, y) for x, y in zip(a, b, strict=True))
        )
    if isinstance(a, float) and isinstance(b, float) and np.isnan(a) and np.isnan(b):
        return True
    return type(a) is type(b) and a == b


def _roundtrip(dataset: Dataset, tmp_path: Path) -> Dataset:
    path = dataset.save(tmp_path / "one.h5")
    return Dataset.load(path)


def test_tree_keeps_every_kind_of_value(tmp_path: Path) -> None:
    tree = {
        "f64": np.linspace(0, 1, 5),
        "f32": np.arange(4, dtype=np.float32),
        "i8": np.array([1, -2], dtype=np.int8),
        "c128": np.array([1 + 2j, np.nan]),
        "text": np.array(["a", "längere"], dtype="<U7"),
        "objects": np.array(["x", "y"], dtype=object),
        "flags": np.array([True, False]),
        "big": np.random.default_rng(1).normal(size=(400_000,)),
        "scalars": {"none": None, "flag": True, "n": 3, "x": float("nan"), "inf": float("inf"), "z": 1 - 1j},
        "np_scalars": {"i": np.int32(7), "f": np.float32(0.5), "b": np.bool_(True), "c": np.complex64(1j)},
        "sequence": (1, "two", (3.0, None)),
        "mixed_list": [np.zeros(2), {"inner": np.ones(1)}, "s"],
        "a/b": "slash in a key",
        7: "int key",
    }
    loaded = _roundtrip(Dataset("OTHER", "test.tree", observations=tree), tmp_path)
    assert _equal(loaded.observations, tree)


def test_ert_container_round_trips_losslessly(tmp_path: Path, examples_data: Path) -> None:
    pg = pytest.importorskip("pygimli")
    data = pg.DataContainerERT(str(examples_data / "ERT" / "Bert" / "fielddataline2.dat"))
    dataset = to_dataset(data)
    assert dataset.method == "ERT" and dataset.masks["valid"].dtype == np.bool_
    back = from_dataset(_roundtrip(dataset, tmp_path))
    original, restored = data.dataMap(), back.dataMap()
    assert sorted(original.keys()) == sorted(restored.keys())
    for name in sorted(original.keys()):
        assert np.array_equal(np.asarray(original[name]), np.asarray(restored[name])), name
    assert np.array_equal(np.array(data.sensors()), np.array(back.sensors()))
    assert str(back.tokenList()) == str(data.tokenList())


@pytest.mark.parametrize(
    ("relative", "method"), [("EM/synthetic_fdem.csv", "FDEM"), ("EM/synthetic_tem_lci", "TDEM")]
)
def test_em_sounding_round_trips_losslessly(
    tmp_path: Path, examples_data: Path, relative: str, method: str
) -> None:
    from PyHydroGeophysX.workflows import em1d

    options = {"moment": "LM+HM"} if method == "TDEM" else {}
    head = em1d.load_sounding(str(examples_data / relative), method, **options)
    dataset = to_dataset(head)
    assert dataset.meta["em_method"] == method
    assert _equal(from_dataset(_roundtrip(dataset, tmp_path)), head)


def test_mt_transfer_function_round_trips_losslessly(tmp_path: Path, examples_data: Path) -> None:
    from PyHydroGeophysX.data_processing.mt.io import read_transfer_function

    tf = read_transfer_function(examples_data / "MT" / "NMX20.xml")
    back = from_dataset(_roundtrip(to_dataset(tf), tmp_path))
    for field in dataclasses.fields(tf):
        assert _equal(getattr(back, field.name), getattr(tf, field.name)), field.name


def test_segy_dataset_round_trips_losslessly(tmp_path: Path, examples_data: Path) -> None:
    from PyHydroGeophysX.data_processing.seismic import read_segy

    data = read_segy(examples_data / "Seismic" / "AP_411.sgy")
    back = from_dataset(_roundtrip(to_dataset(data), tmp_path))
    assert _equal(back.traces, data.traces) and _equal(back.time, data.time)
    assert back.headers == data.headers and back.metadata == data.metadata and back.path == data.path


def test_a_new_version_links_what_it_shares_and_survives_a_move(tmp_path: Path) -> None:
    project = tmp_path / "Survey"
    store = DatasetStore(project)
    traces = np.random.default_rng(0).normal(size=(2000, 48))
    first = store.put(
        Dataset("SEISMIC", "test.lines", observations={"traces": traces}, masks={"good": np.ones(48, bool)}),
        "line-1",
    )
    edited = store.load("line-1")
    edited.masks["good"][3] = False
    second = store.put(edited, "line-1", label="trace 3 removed")
    assert (first.version, second.version) == (1, 2)
    v1, v2 = store.root / first.path, store.root / second.path
    assert v2.stat().st_size < v1.stat().st_size / 10  # the traces are a link, not a copy
    assert external_files(v2) == [v1.resolve()]

    moved = tmp_path / "Moved" / "Survey"
    moved.parent.mkdir()
    shutil.move(str(project), str(moved))
    again = DatasetStore(moved).load("line-1")
    assert np.array_equal(again.observations["traces"], traces)
    assert not again.masks["good"][3] and again.meta["label"] == "trace 3 removed"


def test_versions_are_immutable(tmp_path: Path) -> None:
    store = DatasetStore(tmp_path)
    entry = store.put(Dataset("OTHER", "test.x", observations={"v": np.zeros(3)}), "x")
    path = store.root / entry.path
    with pytest.raises(FileExistsError):
        Dataset("OTHER", "test.x").save(path)
    with pytest.raises(PermissionError):
        path.open("r+b")


def test_index_is_rebuilt_from_the_files(tmp_path: Path) -> None:
    store = DatasetStore(tmp_path)
    store.put(Dataset("OTHER", "test.x", observations={"v": np.zeros(3)}), "x")
    store.put(Dataset("OTHER", "test.x", observations={"v": np.ones(3)}), "x")
    store.put(Dataset("MT", "test.y"))
    expected = [(e.dataset_id, e.version) for e in store.entries()]
    (store.root / "index.json").unlink()
    assert sorted((e.dataset_id, e.version) for e in DatasetStore(tmp_path).entries()) == sorted(expected)
    (store.root / "index.json").write_text("{broken", encoding="utf-8")
    assert len(DatasetStore(tmp_path).entries()) == 3
    assert json.loads((store.root / "index.json").read_text())["schema"] == "phgx-dataset-index-v1"


def test_raw_files_are_referenced_with_their_checksum(tmp_path: Path) -> None:
    raw = tmp_path / "raw" / "line 1.dat"
    raw.parent.mkdir()
    raw.write_text("electrodes\n", encoding="utf-8")
    store = DatasetStore(tmp_path)
    reference = store.reference_raw(raw)
    assert reference["path"] == "raw/line 1.dat" and len(reference["sha256"]) == 64
    dataset = Dataset("ERT", "test.raw", provenance={"raw_files": [reference]})
    assert store.verify_raw(dataset) == []
    raw.write_text("edited\n", encoding="utf-8")
    assert store.verify_raw(dataset) == ["raw/line 1.dat: changed since it was read (sha256 differs)"]
    raw.unlink()
    assert store.verify_raw(dataset) == ["raw/line 1.dat: missing"]


def test_units_and_masks_are_validated(tmp_path: Path) -> None:
    with pytest.raises(DataValidationError, match="not registered"):
        Dataset("ERT", "test.u", meta={"units": {"rhoa": "ohmm"}}).save(tmp_path / "a.h5")
    with pytest.raises(DataValidationError, match="boolean"):
        Dataset("ERT", "test.m", masks={"valid": np.ones(3)}).save(tmp_path / "b.h5")
    with pytest.raises(DataValidationError, match="dataset ids"):
        DatasetStore(tmp_path).put(Dataset("ERT", "test.id"), "../escape")
