"""Industry figure styles and report figures (plan M4.3)."""

from __future__ import annotations

from .figures import pseudosection_figure, save_publication, section_figure
from .publication import (
    add_colorbar,
    add_north_arrow,
    add_scale_bar,
    add_title_block,
    publication_rc,
    publication_style,
)

__all__ = [
    "add_colorbar",
    "add_north_arrow",
    "add_scale_bar",
    "add_title_block",
    "pseudosection_figure",
    "publication_rc",
    "publication_style",
    "save_publication",
    "section_figure",
]
