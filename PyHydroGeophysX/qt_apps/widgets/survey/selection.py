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
    #: The groups drawn together (the focused group stays :meth:`group`).
    groupsChanged = Signal(object)
    #: Keys of everything on screen, for the plan and section to mark.
    displayChanged = Signal(object)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._group = ""
        self._keys: tuple[Key, ...] = ()
        self._groups: tuple[str, ...] = ()
        self._display: tuple[Key, ...] = ()

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

    def groups(self) -> tuple[str, ...]:
        """Groups drawn together: those set, else just the focused group."""
        if self._groups:
            return self._groups
        return (self._group,) if self._group else ()

    def set_groups(self, groups: Iterable[str]) -> None:
        chosen = tuple(dict.fromkeys(str(group) for group in groups if str(group)))
        if chosen != self._groups:
            self._groups = chosen
            self.groupsChanged.emit(chosen)

    def display_keys(self) -> tuple[Key, ...]:
        return self._display

    def set_display_keys(self, keys: Iterable[Key]) -> None:
        chosen = tuple(dict.fromkeys(tuple(key) for key in keys))
        if chosen != self._display:
            self._display = chosen
            self.displayChanged.emit(chosen)


__all__ = ["SurveySelection"]
