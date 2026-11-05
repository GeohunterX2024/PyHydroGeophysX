"""What a method page hands to the survey views.

A page (or an adapter it owns) implements :class:`SurveyProvider`; the views ask
it for the layout, the pseudo-depth points and the curves of a group, and show
only the tabs its :meth:`~SurveyProvider.survey_capabilities` name.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol, runtime_checkable

from PyHydroGeophysX.survey.layout import SurveyLayout
from PyHydroGeophysX.survey.pseudo import PseudoPoints
from PyHydroGeophysX.survey.traces import TraceSet

#: ``layout``: a plan and a 3-D view; ``pseudo``: pseudo-depth points on the
#: section and in 3-D; ``traces``: a curve view; ``spectrum``: a spectrum view.
CAPABILITIES = ("layout", "pseudo", "traces", "spectrum")


@runtime_checkable
class SurveyProvider(Protocol):
    def survey_capabilities(self) -> frozenset[str]:
        """The subset of :data:`CAPABILITIES` this provider has data for now."""
        ...

    def survey_layout(self) -> SurveyLayout | None:
        """The layout, or None when nothing is loaded."""
        ...

    def survey_pseudo(self) -> PseudoPoints | None:
        """Pseudo-depth points with their surface elevation, or None."""
        ...

    def survey_traces(self, group: str, channels: Sequence[str]) -> TraceSet | None:
        """Curves of ``group`` restricted to ``channels`` (all of them when empty), or None."""
        ...


__all__ = ["CAPABILITIES", "SurveyProvider"]
