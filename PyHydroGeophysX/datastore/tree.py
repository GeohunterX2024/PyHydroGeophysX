"""A nested mapping of arrays and plain values in an HDF5 group, losslessly (phgx-dataset-v1).

Arrays become datasets (their exact dtype kept, Unicode stored as UTF-8 and
restored to its width); nested mappings become groups; lists and tuples that
hold arrays or mappings become groups with numbered members. Every other value
- None, bool, int, float (NaN and inf too), complex, str, NumPy scalars, and
lists/tuples of those - goes into the group's ``phgx_tree`` JSON attribute
with a type tag where JSON alone would lose it. Key order is kept.

An array equal to one in a base version is written as an HDF5 external link to
where that version keeps it, with a path relative to the new file, so a
project folder can be moved as a whole.
"""

from __future__ import annotations

import json
import os
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any

import numpy as np

from PyHydroGeophysX.errors import DataValidationError

TREE_ATTR = "phgx_tree"
#: Arrays above this size are written in row blocks: h5py holds the GIL
#: during a write, so one large write would stop a GUI thread meanwhile.
BLOCK_BYTES = 2 * 1024 * 1024

#: (group path, key, ...) of an array -> (file holding it, its HDF5 path).
Origins = dict[tuple[str, ...], tuple[str, str]]
#: Looks up the base version's array at a key path, or None.
BaseLookup = Callable[[tuple[str, ...]], "tuple[np.ndarray, tuple[str, str]] | None"]


def _escape(key: str) -> str:
    name = key.replace("%", "%25").replace("/", "%2F")
    return "%2E" if name == "." else name


def _key_record(key: object) -> list[Any]:
    if isinstance(key, bool) or not isinstance(key, (str, int)):
        raise DataValidationError(
            f"mapping keys must be str or int, got {type(key).__name__}", field=str(key)
        )
    return [key, "int" if isinstance(key, int) else "str"]


def _tag(value: Any, where: str) -> Any:
    """A JSON-ready form of a plain value, tagged where JSON would lose its type."""
    if value is None or isinstance(value, (bool, str)):
        return value
    if isinstance(value, np.generic):
        if isinstance(value, np.complexfloating):
            return {"$np": value.dtype.str, "v": [float(value.real), float(value.imag)]}
        return {"$np": value.dtype.str, "v": value.item()}
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return value
    if isinstance(value, complex):
        return {"$complex": [value.real, value.imag]}
    if isinstance(value, tuple):
        return {"$tuple": [_tag(item, f"{where}[{index}]") for index, item in enumerate(value)]}
    if isinstance(value, list):
        return [_tag(item, f"{where}[{index}]") for index, item in enumerate(value)]
    raise DataValidationError(f"cannot store a {type(value).__name__}", field=where)


def _untag(value: Any) -> Any:
    if isinstance(value, list):
        return [_untag(item) for item in value]
    if isinstance(value, dict):
        if "$tuple" in value:
            return tuple(_untag(item) for item in value["$tuple"])
        if "$complex" in value:
            real, imag = value["$complex"]
            return complex(real, imag)
        if "$np" in value:
            dtype = np.dtype(value["$np"])
            raw = value["v"]
            item = complex(raw[0], raw[1]) if dtype.kind == "c" else raw
            return np.array(item, dtype=dtype)[()]
    return value


def _is_plain(value: Any) -> bool:
    """True for values that go into the JSON attribute rather than a dataset or group."""
    if isinstance(value, (Mapping, np.ndarray)):
        return False
    if isinstance(value, (list, tuple)):
        return all(_is_plain(item) for item in value)
    return True


def _encode(array: np.ndarray, where: str) -> tuple[np.ndarray, str]:
    if array.dtype.kind == "U":
        return np.char.encode(array, "utf-8"), array.dtype.str
    if array.dtype.kind == "M" or array.dtype.kind == "m":
        return array.view(np.int64), array.dtype.str
    if array.dtype.kind == "O":
        if all(isinstance(item, str) for item in array.ravel()):
            text = array.astype(str)
            return np.char.encode(text, "utf-8"), "object-str"
        raise DataValidationError("object arrays other than strings cannot be stored", field=where)
    return array, array.dtype.str


def _decode(raw: np.ndarray, dtype: str) -> np.ndarray:
    if dtype == "object-str":
        return np.char.decode(raw, "utf-8").astype(object)
    target = np.dtype(dtype)
    if target.kind == "U":
        return np.char.decode(raw, "utf-8").astype(target)
    if target.kind in "Mm":
        return raw.view(target)
    return raw.astype(target, copy=False)


def _same(a: np.ndarray, b: np.ndarray) -> bool:
    if a.shape != b.shape or a.dtype != b.dtype:
        return False
    if a.dtype.kind in "fc":
        return bool(np.array_equal(a, b, equal_nan=True))
    return bool(np.array_equal(a, b))


def _write_array(group: Any, name: str, array: np.ndarray, where: str) -> Any:
    data, dtype = _encode(np.asarray(array), where)
    if data.ndim == 0 or data.nbytes <= BLOCK_BYTES or data.dtype.kind == "S":
        node = group.create_dataset(name, data=data)
    else:
        node = group.create_dataset(name, shape=data.shape, dtype=data.dtype)
        rows = max(1, BLOCK_BYTES // max(1, data[0].nbytes))
        for start in range(0, data.shape[0], rows):
            node[start : start + rows] = data[start : start + rows]
    node.attrs["dtype"] = dtype
    return node


def write_tree(
    group: Any,
    tree: Mapping[Any, Any] | list[Any] | tuple[Any, ...],
    *,
    path: tuple[str, ...],
    file: Path,
    base: BaseLookup | None,
    origins: Origins,
) -> None:
    """Write ``tree`` into the h5py ``group``; record each array's origin in ``origins``."""
    import h5py

    if isinstance(tree, Mapping):
        items = list(tree.items())
        kind = "dict"
    else:
        items = list(enumerate(tree))
        kind = "tuple" if isinstance(tree, tuple) else "list"
    order: list[list[Any]] = []
    values: dict[str, Any] = {}
    for key, value in items:
        record = _key_record(key)
        order.append(record)
        name = _escape(str(key))
        where = "/".join((*path, str(key)))
        key_path = (*path, str(key))
        if isinstance(value, np.ndarray):
            match = base(key_path) if base is not None else None
            if match is not None and _same(np.asarray(value), match[0]):
                origin_file, origin_path = match[1]
                group[name] = h5py.ExternalLink(os.path.relpath(origin_file, file.parent), origin_path)
                origins[key_path] = (origin_file, origin_path)
            else:
                node = _write_array(group, name, value, where)
                origins[key_path] = (str(file), node.name)
        elif _is_plain(value):
            values[name] = _tag(value, where)
        else:
            child = group.create_group(name)
            write_tree(child, value, path=key_path, file=file, base=base, origins=origins)
    group.attrs[TREE_ATTR] = json.dumps({"kind": kind, "order": order, "values": values}, ensure_ascii=False)


def read_tree(group: Any, *, path: tuple[str, ...], file: Path, origins: Origins) -> Any:
    """Read what :func:`write_tree` wrote; record each array's origin (links followed)."""
    import h5py

    header = json.loads(group.attrs.get(TREE_ATTR, '{"kind": "dict", "order": [], "values": {}}'))
    out: dict[Any, Any] = {}
    for key, key_type in header["order"]:
        name = _escape(str(key))
        actual_key: Any = int(key) if key_type == "int" else key
        key_path = (*path, str(key))
        if name in header["values"]:
            out[actual_key] = _untag(header["values"][name])
            continue
        link = group.get(name, getlink=True)
        node = group[name]
        if isinstance(node, h5py.Group):
            out[actual_key] = read_tree(node, path=key_path, file=file, origins=origins)
            continue
        out[actual_key] = _decode(np.asarray(node[()]), str(node.attrs.get("dtype", node.dtype.str)))
        if isinstance(link, h5py.ExternalLink):
            origins[key_path] = resolve_origin((file.parent / link.filename).resolve(), link.path)
        else:
            origins[key_path] = (str(file), node.name)
    if header["kind"] == "dict":
        return out
    items = [out[index] for index in range(len(out))]
    return tuple(items) if header["kind"] == "tuple" else items


def resolve_origin(file: Path, h5path: str) -> tuple[str, str]:
    """Follow a chain of external links to the file that really holds an array."""
    import h5py

    for _ in range(32):
        try:
            with h5py.File(file, "r") as handle:
                parent, _, leaf = h5path.rpartition("/")
                link = handle[parent or "/"].get(leaf, getlink=True)
        except (OSError, KeyError):
            break
        if not isinstance(link, h5py.ExternalLink):
            break
        file, h5path = (file.parent / link.filename).resolve(), link.path
    return str(file), h5path


__all__ = ["BLOCK_BYTES", "TREE_ATTR", "Origins", "read_tree", "resolve_origin", "write_tree"]
