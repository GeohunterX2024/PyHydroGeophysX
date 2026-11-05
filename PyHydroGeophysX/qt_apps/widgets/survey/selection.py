"""One selection shared by every survey view and the page that owns them.

The current *group* is the shot, injection or site on screen; the *keys* are the
selected objects, shaped like QC log keys. Views and page lists set both and
follow both; setting the value already held emits nothing, so two widgets that
follow each other do not loop.
"""

from __future__ import annotations

from collections.abc import Iterable

from PySide6.QtCore import QObject, Signal

from PyHydroGeophysX.survey.layout import Key


class SurveySelection(QObject):
    """The current group and the selected keys."""

    groupChanged = Signal(str)
    keysChanged = Signal(object)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._group = ""
        self._keys: tuple[Key, ...] = ()

    def group(self) -> str:
        return self._group

    def keys(self) -> tuple[Key, ...]:
        return self._keys

    def set_group(self, group: str) -> None:
        group = str(group or "")
        if group != self._group:
            self._group = group
            self.groupChanged.emit(group)

    def set_keys(self, keys: Iterable[Key]) -> None:
        chosen = tuple(dict.fromkeys(tuple(k) for k in keys))
        if chosen != self._keys:
            self._keys = chosen
            self.keysChanged.emit(chosen)

    def clear(self) -> None:
        self.set_keys(())


__all__ = ["SurveySelection"]
