"""Entry-point loading for plugins, below every layer that registers into it.

The workflow registry calls :func:`load_entry_points` so a plugin's workflows
exist in a headless worker; the registration API itself (pages, readers, short
codes) is in :mod:`PyHydroGeophysX.plugins`, above the Studio it reaches into.
Keeping the loader here lets the registry depend downwards only.
"""

from __future__ import annotations

import logging
from collections.abc import Iterable
from importlib import metadata

logger = logging.getLogger(__name__)

#: Entry-point groups read by :func:`load_entry_points`. ``phgx.plugins`` is the
#: general one; the others exist so a package can split its registrations.
ENTRY_POINT_GROUPS: tuple[str, ...] = ("phgx.plugins", "phgx.modules", "phgx.workflows", "phgx.readers")

_loaded_groups: set[str] = set()
_failures: list[str] = []


def record_failure(message: str) -> None:
    _failures.append(message)


def load_failures() -> tuple[str, ...]:
    """Entry points or registrations that failed in this process, as ``"name: error"``."""
    return tuple(_failures)


def load_entry_points(groups: Iterable[str] = ENTRY_POINT_GROUPS) -> int:
    """Run every not-yet-loaded plugin entry point; return how many ran.

    Each entry point names a callable taking no arguments that makes its
    registrations. A plugin that fails to import or register is logged and
    recorded in :func:`load_failures`; it never stops the others or the Studio.
    """
    ran = 0
    for group in groups:
        if group in _loaded_groups:
            continue
        _loaded_groups.add(group)
        for entry_point in metadata.entry_points(group=group):
            try:
                register = entry_point.load()
                if callable(register):
                    register()
                ran += 1
            except Exception as exc:  # noqa: BLE001 - a broken plugin must not stop the others
                message = f"{entry_point.name} ({entry_point.value}): {exc}"
                record_failure(message)
                logger.warning("plugin %s failed to load", message)
    return ran


__all__ = ["ENTRY_POINT_GROUPS", "load_entry_points", "load_failures", "record_failure"]
