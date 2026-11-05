"""Shared survey views: plan and section (pyqtgraph), 3-D (PyVista, Matplotlib fallback),
curves and spectra, joined by one selection and offered as a tabbed workbench.

What they draw is described by :mod:`PyHydroGeophysX.survey`; a page hands a
:class:`~PyHydroGeophysX.survey.provider.SurveyProvider` to
:class:`~.workbench.SurveyWorkbench` and keeps its own lists and QC bar.
"""

from __future__ import annotations

from PyHydroGeophysX.qt_apps.widgets.survey.selection import SurveySelection
from PyHydroGeophysX.qt_apps.widgets.survey.workbench import SurveyWorkbench

__all__ = ["SurveySelection", "SurveyWorkbench"]
