"""The project database: immutable dataset versions under ``<project>/datasets`` (plan M3.1).

Layout::

    <project>/datasets/index.json            rebuildable from the files
    <project>/datasets/<dataset_id>/v0001.h5 one immutable version each

A new version of a dataset links the arrays it shares with the latest one, so
an edited mask costs a mask, not a copy of every trace. Raw instrument files
are referenced read-only - path and sha256, never copied or modified - and
:meth:`DatasetStore.verify_raw` says when one changed or went missing. Like
the ResultsStore's run index, the JSON index is only a cache of what the files
say: :meth:`DatasetStore.rebuild_index` recreates it.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from PyHydroGeophysX.errors import DataValidationError

from .dataset import Dataset

INDEX_NAME = "index.json"
INDEX_SCHEMA = "phgx-dataset-index-v1"
_VERSION_FILE = re.compile(r"^v(\d{4,})\.h5$")
_SAFE_ID = re.compile(r"[^A-Za-z0-9._-]+")


@dataclass(frozen=True)
class DatasetVersion:
    """One saved version, as the index lists it. ``path`` is relative to the datasets folder."""

    dataset_id: str
    version: int
    path: str
    method: str
    kind: str
    label: str
    created: str


def sha256_of(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


class DatasetStore:
    """Dataset versions of one project folder."""

    def __init__(self, project_root: str | Path) -> None:
        self.project_root = Path(project_root).resolve()
        self.root = self.project_root / "datasets"

    # -- writing ---------------------------------------------------------------
    def put(self, dataset: Dataset, dataset_id: str | None = None, *, label: str = "") -> DatasetVersion:
        """Save ``dataset`` as the next version of ``dataset_id`` (a new id from its kind if None)."""
        dataset_id = self._new_id(dataset) if dataset_id is None else self._checked_id(dataset_id)
        # Read before the new file exists, which a rebuild of a missing index would list.
        index = self._read_index()
        existing = sorted((e for e in index if e.dataset_id == dataset_id), key=lambda e: e.version)
        base = self.load(dataset_id) if existing else None
        number = (existing[-1].version + 1) if existing else 1
        relative = f"{dataset_id}/v{number:04d}.h5"
        if label:
            dataset.meta["label"] = label
        dataset.meta.setdefault("label", dataset_id)
        dataset.meta["dataset_id"] = dataset_id
        dataset.meta["version"] = number
        dataset.meta["created"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
        dataset.save(self.root / relative, base=base)
        entry = DatasetVersion(
            dataset_id=dataset_id,
            version=number,
            path=relative,
            method=dataset.method,
            kind=dataset.kind,
            label=str(dataset.meta["label"]),
            created=str(dataset.meta["created"]),
        )
        index.append(entry)
        self._write_index(index)
        return entry

    def reference_raw(self, path: str | Path) -> dict[str, Any]:
        """A read-only reference to a raw file for ``provenance["raw_files"]``.

        The path is kept relative to the project folder when the file is inside
        it, so the project can move; outside files keep their absolute path.
        """
        source = Path(path).resolve()
        if not source.is_file():
            raise DataValidationError("raw file not found", file=source)
        try:
            stored = source.relative_to(self.project_root).as_posix()
        except ValueError:
            stored = str(source)
        return {"path": stored, "sha256": sha256_of(source), "size": source.stat().st_size}

    # -- reading ---------------------------------------------------------------
    def entries(self) -> list[DatasetVersion]:
        return list(self._read_index())

    def versions(self, dataset_id: str) -> list[DatasetVersion]:
        return sorted((e for e in self._read_index() if e.dataset_id == dataset_id), key=lambda e: e.version)

    def load(self, dataset_id: str, version: int | None = None) -> Dataset:
        versions = self.versions(dataset_id)
        if not versions:
            raise KeyError(f"no dataset {dataset_id!r} in {self.root}")
        chosen = (
            versions[-1] if version is None else next((v for v in versions if v.version == version), None)
        )
        if chosen is None:
            raise KeyError(f"dataset {dataset_id!r} has no version {version}")
        return Dataset.load(self.root / chosen.path)

    def verify_raw(self, dataset: Dataset) -> list[str]:
        """Problems with the raw files ``dataset`` references: missing, or changed since."""
        problems = []
        for record in dataset.provenance.get("raw_files") or []:
            stored = str(record.get("path", ""))
            path = Path(stored)
            resolved = path if path.is_absolute() else self.project_root / path
            if not resolved.is_file():
                problems.append(f"{stored}: missing")
            elif sha256_of(resolved) != record.get("sha256"):
                problems.append(f"{stored}: changed since it was read (sha256 differs)")
        return problems

    # -- index -------------------------------------------------------------------
    def rebuild_index(self) -> list[DatasetVersion]:
        """Recreate ``index.json`` from the version files themselves."""
        entries = []
        if self.root.is_dir():
            for folder in sorted(p for p in self.root.iterdir() if p.is_dir()):
                for file in sorted(folder.iterdir()):
                    match = _VERSION_FILE.match(file.name)
                    if not match:
                        continue
                    dataset = Dataset.load(file)
                    entries.append(
                        DatasetVersion(
                            dataset_id=folder.name,
                            version=int(match.group(1)),
                            path=f"{folder.name}/{file.name}",
                            method=dataset.method,
                            kind=dataset.kind,
                            label=str(dataset.meta.get("label", folder.name)),
                            created=str(dataset.meta.get("created", "")),
                        )
                    )
        self._write_index(entries)
        return entries

    def _read_index(self) -> list[DatasetVersion]:
        path = self.root / INDEX_NAME
        if not path.is_file():
            return self.rebuild_index() if self.root.is_dir() else []
        try:
            document = json.loads(path.read_text(encoding="utf-8"))
            return [DatasetVersion(**item) for item in document["datasets"]]
        except (OSError, ValueError, KeyError, TypeError):
            return self.rebuild_index()

    def _write_index(self, entries: list[DatasetVersion]) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        document = {"schema": INDEX_SCHEMA, "datasets": [asdict(e) for e in entries]}
        partial = self.root / f".{INDEX_NAME}.partial"
        partial.write_text(json.dumps(document, indent=2, ensure_ascii=False), encoding="utf-8")
        os.replace(partial, self.root / INDEX_NAME)

    # -- ids -----------------------------------------------------------------------
    def _checked_id(self, dataset_id: str) -> str:
        if not dataset_id or _SAFE_ID.search(dataset_id) or dataset_id.startswith("."):
            raise DataValidationError(
                "dataset ids use letters, digits, '.', '_' and '-' only", field="dataset_id"
            )
        return dataset_id

    def _new_id(self, dataset: Dataset) -> str:
        stem = _SAFE_ID.sub("-", f"{dataset.method.lower()}-{dataset.kind.rsplit('.', 1)[-1].lower()}").strip(
            "-"
        )
        taken = {e.dataset_id for e in self._read_index()}
        number = 1
        while f"{stem}-{number:03d}" in taken:
            number += 1
        return f"{stem}-{number:03d}"


__all__ = ["INDEX_NAME", "DatasetStore", "DatasetVersion", "sha256_of"]
