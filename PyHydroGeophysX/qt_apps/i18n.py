"""The Studio's languages: English as written, Simplified Chinese from phgx_zh_CN.qm (plan M4.1).

Texts written in the code are translated where they are shown, through
``QCoreApplication.translate("PHGX", ...)`` for literals and :func:`tr` for
texts held in variables. :func:`install_translator` loads the translation
the user chose - by default the system's language - before the window is
built; a change of language takes effect at the next start.

Only what is shown is translated. Combo-box entries whose text the code also
reads back as a value stay as written; logs stay in English, for support.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from PySide6.QtCore import QCoreApplication, QLibraryInfo, QLocale, QSettings, QTranslator

CONTEXT = "PHGX"
SETTINGS_KEY = "ui/language"
#: Choices of the Language menu: setting value -> label (each in its own language).
LANGUAGES = {"system": "System default", "en": "English", "zh_CN": "简体中文"}
TRANSLATIONS = Path(__file__).resolve().parent / "translations"
_installed: list[QTranslator] = []


def tr(text: Any) -> Any:
    """``text`` in the Studio's language when it is a string; anything else unchanged."""
    if isinstance(text, str) and text:
        return QCoreApplication.translate(CONTEXT, text)
    return text


def chosen_language() -> str:
    value = str(QSettings("PyHydroGeophysX", "Studio").value(SETTINGS_KEY, "system") or "system")
    return value if value in LANGUAGES else "system"


def set_language(language: str) -> None:
    """Remember ``language`` (a key of :data:`LANGUAGES`) for the next start."""
    if language not in LANGUAGES:
        raise ValueError(f"unknown language {language!r}")
    QSettings("PyHydroGeophysX", "Studio").setValue(SETTINGS_KEY, language)


def resolve(language: str) -> str:
    """The language a setting stands for: "system" becomes "zh_CN" on a Chinese system, else "en"."""
    if language == "system":
        return "zh_CN" if QLocale.system().name().lower().startswith("zh") else "en"
    return language


def install_translator(app: Any, language: str | None = None) -> str:
    """Load the translation of ``language`` (default: the saved choice) into ``app``; returns what is used.

    Qt's own translation is loaded too, so standard dialogs and buttons
    (Open, Cancel, ...) follow. A missing translation file leaves English.
    """
    for translator in _installed:
        app.removeTranslator(translator)
    _installed.clear()
    used = resolve(language or chosen_language())
    if used == "en":
        return used
    ours = QTranslator(app)
    if not ours.load(str(TRANSLATIONS / f"phgx_{used}.qm")):
        return "en"
    app.installTranslator(ours)
    _installed.append(ours)
    qt_own = QTranslator(app)
    if qt_own.load(f"qtbase_{used}", QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath)):
        app.installTranslator(qt_own)
        _installed.append(qt_own)
    return used


__all__ = ["CONTEXT", "LANGUAGES", "chosen_language", "install_translator", "resolve", "set_language", "tr"]
