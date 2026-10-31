"""Translation of the Studio's own pages (plan M4.1)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from .conftest import load_tool

ROOT = Path(__file__).resolve().parents[2]


def test_every_ui_text_is_translatable_and_translated() -> None:
    assert load_tool("i18n").check() == []


def test_the_codemod_wraps_literals_fstrings_and_variables(tmp_path: Path) -> None:
    i18n_tool = load_tool("i18n")
    page = tmp_path / "page.py"
    page.write_text(
        "from PySide6.QtCore import Qt\n"
        "from PySide6.QtWidgets import QLabel\n"
        "def build(self, n, name):\n"
        "    QLabel('Load data')\n"
        "    self.status.setText(f'Loaded {n:d} files')\n"
        "    self.status.setToolTip(name)\n"
        "    self.combo.addItem('Quick')\n"
        "    self.combo.addItem('Full mode', 'full')\n"
        "    self.combo.setCurrentText('Quick')\n"
        "    _logger.warning('cannot %s', name)\n"
        "    self.ok.setText('Done' if n else 'Waiting for data')\n",
        encoding="utf-8",
    )
    assert i18n_tool.wrap(page) == 6
    text = page.read_text(encoding="utf-8")
    assert "from PySide6.QtCore import QCoreApplication, Qt" in text
    assert "QLabel(QCoreApplication.translate(\"PHGX\", 'Load data'))" in text
    assert 'QCoreApplication.translate("PHGX", "Loaded {0:d} files").format(n)' in text
    assert "setToolTip(i18n.tr(name))" in text
    assert "addItem('Quick')" in text and "setCurrentText('Quick')" in text  # read back as values
    assert "addItem(QCoreApplication.translate(\"PHGX\", 'Full mode'), 'full')" in text
    assert "_logger.warning('cannot %s', name)" in text  # logs stay in English
    assert "QCoreApplication.translate(\"PHGX\", 'Done') if n else" in text
    assert i18n_tool.scan(page, dynamic=True) == []


def test_translations_keep_placeholders_and_markup() -> None:
    translations = json.loads(
        (ROOT / "PyHydroGeophysX/qt_apps/translations/zh_CN.json").read_text(encoding="utf-8")
    )
    assert translations["&File"] == "文件(&F)"
    assert translations["Run inversion"] == "运行反演"
    assert "{0}" in translations["Module: {0}"]


@pytest.mark.gui
def test_the_chinese_translation_is_shown(qtbot: object) -> None:
    pytest.importorskip("PySide6")
    from PySide6.QtCore import QCoreApplication
    from PySide6.QtWidgets import QApplication

    from PyHydroGeophysX.qt_apps import i18n

    app = QApplication.instance()
    assert app is not None
    try:
        assert i18n.install_translator(app, "zh_CN") == "zh_CN"
        assert QCoreApplication.translate("PHGX", "Run inversion") == "运行反演"
        assert i18n.tr("Model Viewer") == "模型查看器"
        assert i18n.tr(42) == 42  # anything but text passes through
    finally:
        i18n.install_translator(app, "en")
    assert QCoreApplication.translate("PHGX", "Run inversion") == "Run inversion"


def test_system_language_resolves() -> None:
    pytest.importorskip("PySide6")
    from PyHydroGeophysX.qt_apps import i18n

    assert i18n.resolve("zh_CN") == "zh_CN" and i18n.resolve("en") == "en"
    assert i18n.resolve("system") in ("zh_CN", "en")
