"""Report figures of a survey: plan, section, record and spectrum, in both languages."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from PyHydroGeophysX.survey.spectra import trace_spectrum
from PyHydroGeophysX.visualization.styles import save_publication
from PyHydroGeophysX.visualization.styles.survey import (
    spectrum_figure,
    survey_plan_figure,
    survey_section_figure,
    trace_figure,
)

from . import synth


def _texts(fig: Any) -> str:
    from matplotlib.text import Text

    return " ".join(t.get_text() for t in fig.findobj(Text))


@pytest.mark.parametrize("language", ["zh", "en"])
def test_every_survey_figure_saves(tmp_path: Path, language: str) -> None:
    layout, pseudo, traces = synth.layout(), synth.pseudo(), synth.traces()
    spectrum = trace_spectrum(traces, traces.window("On-time (steady)"))
    figures = {
        "plan": survey_plan_figure(layout, group="s1", language=language, title_block={"line": "L1"}),
        "section": survey_section_figure(
            layout, pseudo, colour_by="rho_a", log_scale=True, unit="ohm.m", language=language
        ),
        "trace": trace_figure(traces, window="Off-time", language=language),
        "spectrum": spectrum_figure(spectrum, language=language),
    }
    for name, fig in figures.items():
        for suffix in (".png", ".pdf"):
            path = save_publication(fig, tmp_path / f"{name}{suffix}")
            assert path.stat().st_size > 1000
    plan = _texts(figures["plan"])
    assert ("东" in plan) == (language == "zh")
    assert "6000" in plan  # the remote B is named, not drawn
    assert "AM" in _texts(figures["section"])
