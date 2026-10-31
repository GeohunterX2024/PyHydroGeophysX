"""Paths PyGIMLi's C++ core can open.

On Windows PyGIMLi's file functions (``pg.load``, ``Mesh.save``,
``DataContainer.save``, ``exportVTK``, the ``DataContainer`` constructors, and
``ert.load``/``tt.load`` built on them) take a narrow string and open it in the
system code page, so a path with characters outside it - a Chinese folder name
on most systems - cannot be opened (docs/yuem/findings.md F-16). The 8.3 short
form of a path is ASCII and opens everywhere.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

_WINDOWS = sys.platform == "win32"


def pygimli_path(path: str | os.PathLike[str], *, create: bool = False) -> str:
    """``path`` as a string PyGIMLi's C++ file functions can open.

    Elsewhere than on Windows, and for an ASCII path, that is the path itself.
    On Windows a path with other characters is given 8.3 short names: the
    folder's when the file name is ASCII, so PyGIMLi may still add a suffix to
    it or write a new file; otherwise the file's own, which ``create`` makes
    (empty) first for a file about to be written. A volume without short names
    leaves the path unchanged, and the call fails as it would have.
    """
    text = os.fspath(path)
    if not _WINDOWS or text.isascii():
        return text
    target = Path(text)
    if target.name.isascii():
        folder = _short_name(target.parent)
        return os.path.join(folder, target.name) if folder is not None else text
    if create and not target.exists():
        target.touch()
    short = _short_name(target)
    return short if short is not None else text


def _short_name(path: Path) -> str | None:
    """The 8.3 form of an existing ``path``, if it is ASCII (Windows only)."""
    if sys.platform != "win32":
        return None
    import ctypes
    from ctypes import wintypes

    get = ctypes.windll.kernel32.GetShortPathNameW
    get.argtypes = (wintypes.LPCWSTR, wintypes.LPWSTR, wintypes.DWORD)
    get.restype = wintypes.DWORD
    size = get(str(path), None, 0)
    if not size:
        return None
    buffer = ctypes.create_unicode_buffer(size)
    if not get(str(path), buffer, size):
        return None
    value: str = buffer.value
    return value if value.isascii() else None


__all__ = ["pygimli_path"]
