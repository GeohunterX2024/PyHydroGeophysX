"""Per-user folders of PyHydroGeophysX: logs and caches (plan M2.4, M2.5).

Each has an environment override for tests, CI and managed installs:
``PHGX_LOG_DIR`` and ``PHGX_CACHE_DIR``. Without platformdirs the platform's
conventional folders are used.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

APP_NAME = "PHGX"


def _fallback(kind: str) -> Path:
    home = Path.home()
    if sys.platform == "darwin":
        return home / "Library" / ("Logs" if kind == "log" else "Caches") / APP_NAME
    if sys.platform == "win32":
        local = Path(os.environ.get("LOCALAPPDATA", home / "AppData" / "Local"))
        return local / APP_NAME / ("Logs" if kind == "log" else "Cache")
    if kind == "log":
        return Path(os.environ.get("XDG_STATE_HOME", home / ".local" / "state")) / APP_NAME / "log"
    return Path(os.environ.get("XDG_CACHE_HOME", home / ".cache")) / APP_NAME


def log_dir() -> Path:
    """Folder of the application log (``~/Library/Logs/PHGX`` on macOS)."""
    override = os.environ.get("PHGX_LOG_DIR")
    if override:
        return Path(override).expanduser()
    try:
        import platformdirs
    except ImportError:
        return _fallback("log")
    return Path(platformdirs.user_log_dir(APP_NAME, appauthor=False))


def cache_dir() -> Path:
    """Folder for caches that can be rebuilt (``~/Library/Caches/PHGX`` on macOS)."""
    override = os.environ.get("PHGX_CACHE_DIR")
    if override:
        return Path(override).expanduser()
    try:
        import platformdirs
    except ImportError:
        return _fallback("cache")
    return Path(platformdirs.user_cache_dir(APP_NAME, appauthor=False))


__all__ = ["APP_NAME", "cache_dir", "log_dir"]
