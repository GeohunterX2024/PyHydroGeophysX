"""Forwarding entry of the ERT page, which lives in ``qt_apps/modules/ert/`` (plan M4.5).

``MODULE_SPECS`` and scripts load ``ERTProcessingModule`` from here; the page's
constants and helpers are reachable here as before.
"""

from __future__ import annotations

from typing import Any

from PyHydroGeophysX.qt_apps.modules.ert import common as _common
from PyHydroGeophysX.qt_apps.modules.ert.page import ERTProcessingModule

# Redirects names that 0.3.0 scripts imported from this page to where they live.
from PyHydroGeophysX._internal.deprecations import legacy_names as _legacy_names

_legacy = _legacy_names(__name__, {
    "metrics_from_manager": "PyHydroGeophysX.inversion.metrics.metrics_from_manager",
})


def __getattr__(name: str) -> Any:
    if hasattr(_common, name):
        return getattr(_common, name)
    return _legacy(name)


__all__ = ["ERTProcessingModule"]
