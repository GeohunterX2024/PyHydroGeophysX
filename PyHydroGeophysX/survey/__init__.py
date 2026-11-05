"""Method-independent survey views: what a survey's layout, curves and spectra are.

The modules here describe a survey without drawing it, so every method feeds
the same views (``qt_apps.widgets.survey``) and the same publication figures
(``visualization.styles.survey``), and the numbers can be tested without Qt.

- :mod:`.layout` - electrodes, sources, receivers and sites, their links and the terrain;
- :mod:`.pseudo` - pseudo-depth points of a resistivity or IP line;
- :mod:`.traces` - recorded curves with their time windows;
- :mod:`.spectra` - power spectra, power-line harmonics and noise measures;
- :mod:`.scene` - the layers of a 3-D view, built from the above;
- :mod:`.provider` - what a method page hands to the views.

Coordinates are metres in a local projected frame: ``x`` east, ``y`` north,
``z`` elevation (up). Selection keys are tuples shaped like the keys of
:class:`PyHydroGeophysX.datastore.qc.QCLog`, so a selection in any view can be
rejected through the page's QC log.
"""

from __future__ import annotations

from PyHydroGeophysX.survey.layout import (
    Key,
    LineFrame,
    SurveyLayout,
    SurveyLinks,
    SurveyPoints,
    TopographyGrid,
    TopographyProfile,
    local_projection,
)
from PyHydroGeophysX.survey.provider import CAPABILITIES, SurveyProvider
from PyHydroGeophysX.survey.pseudo import PseudoPoints
from PyHydroGeophysX.survey.traces import TraceSet, Window

__all__ = [
    "CAPABILITIES",
    "Key",
    "LineFrame",
    "PseudoPoints",
    "SurveyLayout",
    "SurveyLinks",
    "SurveyPoints",
    "SurveyProvider",
    "TopographyGrid",
    "TopographyProfile",
    "TraceSet",
    "Window",
    "local_projection",
]
