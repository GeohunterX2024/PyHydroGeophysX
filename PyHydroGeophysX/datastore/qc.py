"""Reject, restore, record: one QC log for every method's data (plan M4.4).

A :class:`QCLog` keeps the decisions taken on a set of data items - ERT
readings by row, EM gates by moment and time, MT estimates by frequency -
as a list: each says what was rejected or restored, why, by what criterion
and when. The mask (True = used) is what replaying them gives, so the record
and the data can never disagree, and an undo is taking the last one off.
:meth:`QCLog.write_to` puts both into a dataset: the mask among its masks,
the decisions appended to its provenance.
"""

from __future__ import annotations

from collections.abc import Hashable, Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

import numpy as np

from PyHydroGeophysX.errors import DataValidationError

from .dataset import Dataset

ACTIONS = ("reject", "restore")


def _plain(key: Hashable) -> Any:
    """A key as JSON holds it (tuples as lists, NumPy scalars as Python numbers)."""
    if isinstance(key, tuple):
        return [_plain(part) for part in key]
    if isinstance(key, np.generic):
        return key.item()
    return key


def _key(value: Any) -> Hashable:
    """A key back from JSON (lists as tuples)."""
    if isinstance(value, list):
        return tuple(_key(part) for part in value)
    key: Hashable = value
    return key


@dataclass(frozen=True)
class QCDecision:
    """One decision on some items."""

    action: str
    keys: tuple[Hashable, ...]
    reason: str = ""
    criterion: str = "manual"
    time: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat(timespec="seconds"))

    def to_record(self) -> dict[str, Any]:
        return {
            "action": self.action,
            "keys": [_plain(k) for k in self.keys],
            "reason": self.reason,
            "criterion": self.criterion,
            "time": self.time,
        }

    @classmethod
    def from_record(cls, record: Mapping[str, Any]) -> QCDecision:
        return cls(
            action=str(record["action"]),
            keys=tuple(_key(k) for k in record.get("keys") or []),
            reason=str(record.get("reason", "")),
            criterion=str(record.get("criterion", "manual")),
            time=str(record.get("time", "")),
        )


class QCLog:
    """Decisions on the items ``keys``; the mask is what replaying them gives."""

    def __init__(
        self, keys: Iterable[Hashable], *, name: str = "manual_qc", decisions: Iterable[QCDecision] = ()
    ) -> None:
        self.keys: tuple[Hashable, ...] = tuple(keys)
        self.name = name
        self._index = {key: i for i, key in enumerate(self.keys)}
        if len(self._index) != len(self.keys):
            raise DataValidationError("QC keys must be unique", field="keys")
        self.decisions: list[QCDecision] = []
        for decision in decisions:
            self._check(decision)
            self.decisions.append(decision)

    def _check(self, decision: QCDecision) -> None:
        if decision.action not in ACTIONS:
            raise DataValidationError(f"action must be one of {ACTIONS}", field="action")
        unknown = [k for k in decision.keys if k not in self._index]
        if unknown:
            raise DataValidationError(
                f"{len(unknown)} items not in this QC log, e.g. {unknown[0]!r}", field="keys"
            )

    # -- decisions -----------------------------------------------------------------
    def _decide(
        self, action: str, keys: Sequence[Hashable], reason: str, criterion: str
    ) -> QCDecision | None:
        if not keys:
            return None
        decision = QCDecision(action, tuple(keys), reason, criterion)
        self._check(decision)
        self.decisions.append(decision)
        return decision

    def reject(
        self, keys: Sequence[Hashable], reason: str = "", criterion: str = "manual"
    ) -> QCDecision | None:
        return self._decide("reject", keys, reason, criterion)

    def restore(
        self, keys: Sequence[Hashable], reason: str = "", criterion: str = "manual"
    ) -> QCDecision | None:
        return self._decide("restore", keys, reason, criterion)

    def reject_at(
        self, positions: Iterable[int], reason: str = "", criterion: str = "manual"
    ) -> QCDecision | None:
        """Reject the items at these positions of :attr:`keys` (a table's rows, a plot's points)."""
        return self.reject([self.keys[int(p)] for p in positions], reason, criterion)

    def restore_at(
        self, positions: Iterable[int], reason: str = "", criterion: str = "manual"
    ) -> QCDecision | None:
        return self.restore([self.keys[int(p)] for p in positions], reason, criterion)

    def restore_all(self, reason: str = "") -> QCDecision | None:
        return self.restore(self.rejected(), reason or "restore all")

    def undo(self) -> QCDecision | None:
        """Take the last decision back; returns it, or None when there was none."""
        return self.decisions.pop() if self.decisions else None

    # -- state ---------------------------------------------------------------------
    @property
    def mask(self) -> np.ndarray:
        """True for each item in use, in the order of :attr:`keys`."""
        used = np.ones(len(self.keys), dtype=bool)
        for decision in self.decisions:
            positions = [self._index[k] for k in decision.keys]
            used[positions] = decision.action == "restore"
        return used

    def rejected(self) -> list[Hashable]:
        mask = self.mask
        return [key for key, kept in zip(self.keys, mask, strict=True) if not kept]

    def summary(self) -> str:
        rejected = len(self.keys) - int(self.mask.sum())
        return f"{rejected} of {len(self.keys)} rejected by hand ({len(self.decisions)} decisions)"

    # -- records -------------------------------------------------------------------
    def to_record(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "keys": [_plain(k) for k in self.keys],
            "decisions": [d.to_record() for d in self.decisions],
            "rejected": [_plain(k) for k in self.rejected()],
        }

    @classmethod
    def from_record(cls, record: Mapping[str, Any]) -> QCLog:
        return cls(
            [_key(k) for k in record.get("keys") or []],
            name=str(record.get("name", "manual_qc")),
            decisions=[QCDecision.from_record(d) for d in record.get("decisions") or []],
        )

    def write_to(self, dataset: Dataset) -> Dataset:
        """Put the mask into ``dataset.masks[name]`` and append the decisions to its provenance."""
        dataset.masks[self.name] = self.mask
        # The log holds this mask's whole history; entries of other masks stay.
        history = [entry for entry in dataset.provenance.get("qc") or [] if entry.get("mask") != self.name]
        history += [{"mask": self.name, **decision.to_record()} for decision in self.decisions]
        dataset.provenance["qc"] = history
        return dataset


__all__ = ["ACTIONS", "QCDecision", "QCLog"]
