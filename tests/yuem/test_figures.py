"""Report figures: style, decorations, sections and pseudosections, PDF and PNG (plan M4.3)."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from PyHydroGeophysX.results.protocol import GridGeometry, LayeredGeometry, ModelResultV2, Parameter
from PyHydroGeophysX.visualization.styles import pseudosection_figure, save_publication, section_figure
from PyHydroGeophysX.visualization.styles.publication import cjk_fonts, nice_length, publication_rc


def _line() -> ModelResultV2:
    values = np.outer(np.linspace(1, 2, 12), np.logspace(1, 3, 6)).ravel()
    return ModelResultV2(
        method="TDEM",
        geometry=LayeredGeometry(
            thickness=np.array([2.0, 4.0, 8.0, 16.0, 32.0]), n_soundings=12, positions=np.arange(12) * 25.0
        ),
        parameters={"resistivity": Parameter("resistivity", values, "ohm.m", log_scale=True)},
        doi=np.full(12, 40.0),
    )


def _texts(fig: object) -> list[str]:
    from matplotlib.text import Text

    from PyHydroGeophysX.visualization.styles.figures import _table_cells

    texts = [t.get_text() for t in fig.findobj(Text)]  # type: ignore[attr-defined]
    return texts + [cell.get_text().get_text() for cell in _table_cells(fig)]


def test_round_scale_bar_lengths() -> None:
    assert nice_length(1234.0) == 200.0
    assert nice_length(48.0) == 10.0
    assert nice_length(0.0) == 1.0


def test_style_embeds_truetype_and_uses_cjk_fonts() -> None:
    rc = publication_rc("zh")
    assert rc["pdf.fonttype"] == 42 and rc["xtick.direction"] == "in"
    if cjk_fonts():
        assert rc["font.sans-serif"][0] in cjk_fonts() and rc["axes.unicode_minus"] is False
    assert "font.sans-serif" not in publication_rc("en")


def test_layered_section_in_chinese_with_title_block(tmp_path: Path) -> None:
    fig = section_figure(
        _line(),
        language="zh",
        title="TEM 测线 L1",
        title_block={
            "title": "L1 电阻率断面",
            "project": "示范工程",
            "crs": "CGCS2000 / EPSG:4544",
            "date": "2026-10-31",
        },
    )
    texts = _texts(fig)
    assert "距离 (m)" in texts and "深度 (m)" in texts
    assert any(t.startswith("电阻率 (ohm.m)") for t in texts)
    assert "图签" not in texts and "坐标系" in texts and "CGCS2000 / EPSG:4544" in texts
    assert "遮罩: 探测深度以下置空" in texts  # the mask's basis, in the figure's language
    pdf = save_publication(fig, tmp_path / "line.pdf")
    content = pdf.read_bytes()
    assert content.startswith(b"%PDF") and b"/FontFile2" in content  # TrueType embedded: text stays text
    png = save_publication(fig, tmp_path / "line.png")
    assert png.stat().st_size > 20_000


def test_grid_and_mesh_sections_in_english(tmp_path: Path) -> None:
    grid = ModelResultV2(
        "MT",
        GridGeometry(edges=(np.linspace(0, 1000, 21), np.linspace(-500, 0, 11)), axes=("x", "z")),
        {"resistivity": Parameter("resistivity", np.logspace(0, 3, 200), "ohm.m", log_scale=True)},
    )
    fig = section_figure(grid, language="en", scale_bar=True)
    assert "x (m)" in _texts(fig) and "200 m" in _texts(fig)
    save_publication(fig, tmp_path / "grid.png")
    pg = pytest.importorskip("pygimli")
    from PyHydroGeophysX.inversion.model_result import ModelResult
    from PyHydroGeophysX.results.adapters import from_model_result

    mesh = pg.createGrid(x=np.linspace(0, 40, 21), y=np.linspace(-10, 0, 6))
    result = from_model_result(ModelResult(mesh, np.linspace(10, 500, 100), coverage=np.linspace(-4, 0, 100)))
    fig = section_figure(result, language="en")
    assert "Elevation (m)" in _texts(fig)
    save_publication(fig, tmp_path / "mesh.pdf")
    with pytest.raises(ValueError, match="save as"):
        save_publication(fig, tmp_path / "mesh.jpg")


def test_pseudosection_from_an_ert_container(tmp_path: Path, examples_data: Path) -> None:
    pg = pytest.importorskip("pygimli")
    data = pg.DataContainerERT(str(examples_data / "ERT" / "Bert" / "fielddataline2.dat"))
    fig = pseudosection_figure(data, language="zh", title="视电阻率拟断面")
    texts = _texts(fig)
    assert "伪深度 (m)" in texts and any(t.startswith("视电阻率") for t in texts)
    assert save_publication(fig, tmp_path / "pseudo.pdf").stat().st_size > 5_000
