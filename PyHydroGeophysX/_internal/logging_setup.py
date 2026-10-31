"""Logging of PyHydroGeophysX: the application log and the per-run log (plan M2.4).

* :func:`configure_app_logging` - the Studio's rotating log, ``phgx.log`` in
  :func:`app_log_dir` (``~/Library/Logs/PHGX`` on macOS). Optionally it also
  captures what the process writes to stdout and stderr, so the output of
  upstream code that prints reaches the log without editing that code.
* :func:`run_log` - ``run.log.jsonl`` in a run's folder: one JSON object per
  log record, plus each line the run printed.

Modules log through ``logging.getLogger(__name__)``; every logger of the
package sits under :data:`LOGGER_NAME`, where the handlers are attached.
Configuring logging never raises: a log that cannot be written must not stop
the application or a run.
"""

from __future__ import annotations

import contextlib
import io
import json
import logging
import logging.handlers
import os
import sys
import threading
from datetime import datetime, timezone
from pathlib import Path
from types import TracebackType
from typing import TextIO, cast

from PyHydroGeophysX._internal import platform_dirs

LOGGER_NAME = "PyHydroGeophysX"
OUTPUT_LOGGER_NAME = f"{LOGGER_NAME}.output"
APP_LOG_NAME = "phgx.log"
RUN_LOG_NAME = "run.log.jsonl"
APP_LOG_MAX_BYTES = 5 * 1024 * 1024
APP_LOG_BACKUPS = 5
#: Tracebacks from one place kept before further ones are dropped.
REPEAT_LIMIT = 3

_APP_FORMAT = "%(asctime)s %(levelname)-7s [%(process)d %(threadName)s] %(name)s: %(message)s"
_lock = threading.Lock()
_app_handler: logging.Handler | None = None
_original_streams: tuple[TextIO | None, TextIO | None] | None = None


def app_log_dir() -> Path:
    """Folder of the application log; ``PHGX_LOG_DIR`` overrides it."""
    return platform_dirs.log_dir()


class RepeatFilter(logging.Filter):
    """Pass at most :data:`REPEAT_LIMIT` tracebacks from one place.

    A failure caught in a redraw or mouse handler can repeat many times a
    second; without this its tracebacks would rotate everything else out of the
    log. Records without a traceback always pass.
    """

    def __init__(self, limit: int = REPEAT_LIMIT) -> None:
        super().__init__()
        self.limit = limit
        self._seen: dict[tuple[str, int, str], int] = {}
        self._lock = threading.Lock()

    def filter(self, record: logging.LogRecord) -> bool:
        if not record.exc_info or record.exc_info[0] is None:
            return True
        key = (record.pathname, record.lineno, record.exc_info[0].__name__)
        with self._lock:
            count = self._seen.get(key, 0) + 1
            self._seen[key] = count
        if count == self.limit:
            record.msg = f"{record.msg} (further identical tracebacks from here are not logged)"
        return count <= self.limit


class JsonLinesFormatter(logging.Formatter):
    """One JSON object per record: time, level, logger, message, thread, traceback."""

    def format(self, record: logging.LogRecord) -> str:
        entry: dict[str, object] = {
            "time": datetime.fromtimestamp(record.created, timezone.utc).isoformat(timespec="milliseconds"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "thread": record.threadName,
        }
        if record.exc_info:
            entry["exc"] = self.formatException(record.exc_info)
        return json.dumps(entry, ensure_ascii=False, default=str)


class _StreamTee:
    """Write through to the original stream and log each complete line."""

    def __init__(self, original: TextIO | None, logger: logging.Logger, level: int) -> None:
        self.original = original
        self.encoding = getattr(original, "encoding", None) or "utf-8"
        self.errors = getattr(original, "errors", None) or "strict"
        self._logger = logger
        self._level = level
        self._pending = ""
        self._busy = threading.local()

    def writable(self) -> bool:
        return True

    def isatty(self) -> bool:
        return bool(self.original is not None and self.original.isatty())

    def fileno(self) -> int:
        if self.original is None:
            raise io.UnsupportedOperation("fileno")
        return self.original.fileno()

    def write(self, text: str) -> int:
        if self.original is not None:
            with contextlib.suppress(OSError, ValueError):
                self.original.write(text)
        if getattr(self._busy, "on", False):
            return len(text)
        self._busy.on = True
        try:
            self._pending += text
            *lines, self._pending = self._pending.split("\n")
            for line in lines:
                if line.strip():
                    self._logger.log(self._level, line.rstrip("\r"))
        finally:
            self._busy.on = False
        return len(text)

    def flush(self) -> None:
        if self.original is not None:
            with contextlib.suppress(OSError, ValueError):
                self.original.flush()


def _tee_streams() -> tuple[TextIO | None, TextIO | None]:
    """Route sys.stdout and sys.stderr through tees; returns the originals."""
    originals = (sys.stdout, sys.stderr)
    # Libraries write ordinary progress to stderr as well, so its lines are not
    # warnings; the logger name tells the streams apart.
    sys.stdout = cast(
        TextIO, _StreamTee(sys.stdout, logging.getLogger(f"{OUTPUT_LOGGER_NAME}.stdout"), logging.INFO)
    )
    sys.stderr = cast(
        TextIO, _StreamTee(sys.stderr, logging.getLogger(f"{OUTPUT_LOGGER_NAME}.stderr"), logging.INFO)
    )
    return originals


def _restore_streams(originals: tuple[TextIO | None, TextIO | None]) -> None:
    """Put back the streams :func:`_tee_streams` replaced (None under pythonw)."""
    sys.stdout, sys.stderr = cast(TextIO, originals[0]), cast(TextIO, originals[1])


def _ensure_level(logger: logging.Logger, level: int) -> int:
    """Lower the logger's level to ``level`` if needed; returns the old level."""
    old = logger.level
    if old == logging.NOTSET or old > level:
        logger.setLevel(level)
    return old


def configure_app_logging(
    *,
    level: int | str | None = None,
    directory: Path | None = None,
    capture_output: bool = False,
) -> Path | None:
    """Attach the rotating application log; returns its path, or None if it cannot be written.

    ``level`` defaults to ``PHGX_LOG_LEVEL`` or DEBUG, so failures that the
    Studio deliberately swallows still leave a traceback. Calling it again
    keeps the first configuration.
    """
    global _app_handler, _original_streams
    with _lock:
        if _app_handler is not None:
            filename = getattr(_app_handler, "baseFilename", None)
            return Path(filename) if filename else None
        folder = directory or app_log_dir()
        try:
            folder.mkdir(parents=True, exist_ok=True)
            handler = logging.handlers.RotatingFileHandler(
                folder / APP_LOG_NAME,
                maxBytes=APP_LOG_MAX_BYTES,
                backupCount=APP_LOG_BACKUPS,
                encoding="utf-8",
                delay=True,
            )
        except OSError:
            return None
        chosen = level if level is not None else os.environ.get("PHGX_LOG_LEVEL", "DEBUG")
        numeric = logging.getLevelName(str(chosen).upper()) if isinstance(chosen, str) else chosen
        if not isinstance(numeric, int):
            numeric = logging.DEBUG
        handler.setLevel(numeric)
        handler.setFormatter(logging.Formatter(_APP_FORMAT))
        handler.addFilter(RepeatFilter())
        logger = logging.getLogger(LOGGER_NAME)
        _ensure_level(logger, numeric)
        logger.addHandler(handler)
        _app_handler = handler
        if capture_output and _original_streams is None:
            _original_streams = _tee_streams()
        logger.info("application log opened (pid %d, Python %s)", os.getpid(), sys.version.split()[0])
        return folder / APP_LOG_NAME


def shutdown_app_logging() -> None:
    """Detach the application log and restore the streams (tests, orderly exit)."""
    global _app_handler, _original_streams
    with _lock:
        if _original_streams is not None:
            _restore_streams(_original_streams)
            _original_streams = None
        if _app_handler is not None:
            logging.getLogger(LOGGER_NAME).removeHandler(_app_handler)
            _app_handler.close()
            _app_handler = None


class RunLog:
    """Write ``run.log.jsonl`` in ``run_dir`` while the block runs.

    Records of the package's loggers at INFO and above go to the file, and with
    ``capture_output`` so does every line printed to stdout or stderr - which
    still reaches the original streams, so a parent process reading them sees
    no difference. An exception leaving the block is recorded with its
    traceback and propagates. ``with`` yields the log's path, or None if it
    cannot be written.
    """

    def __init__(self, run_dir: str | Path, *, capture_output: bool = True) -> None:
        self.path = Path(run_dir) / RUN_LOG_NAME
        self.capture_output = capture_output
        self._handler: logging.Handler | None = None
        self._originals: tuple[TextIO | None, TextIO | None] | None = None
        self._old_level = logging.NOTSET

    def __enter__(self) -> Path | None:
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            handler = logging.FileHandler(self.path, mode="a", encoding="utf-8")
        except OSError:
            return None
        handler.setLevel(logging.INFO)
        handler.setFormatter(JsonLinesFormatter())
        logger = logging.getLogger(LOGGER_NAME)
        self._old_level = _ensure_level(logger, logging.INFO)
        logger.addHandler(handler)
        self._handler = handler
        if self.capture_output:
            self._originals = _tee_streams()
        return self.path

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if self._handler is None:
            return
        logger = logging.getLogger(LOGGER_NAME)
        if exc_type is not None and exc is not None:
            logger.error("run failed: %s: %s", exc_type.__name__, exc, exc_info=(exc_type, exc, traceback))
        if self._originals is not None:
            for stream in (sys.stdout, sys.stderr):
                if isinstance(stream, _StreamTee):
                    stream.flush()
            _restore_streams(self._originals)
            self._originals = None
        logger.removeHandler(self._handler)
        self._handler.close()
        self._handler = None
        logger.setLevel(self._old_level)


#: ``with run_log(folder) as path:`` reads as the action it is.
run_log = RunLog


__all__ = [
    "APP_LOG_NAME",
    "LOGGER_NAME",
    "OUTPUT_LOGGER_NAME",
    "RUN_LOG_NAME",
    "JsonLinesFormatter",
    "RepeatFilter",
    "RunLog",
    "app_log_dir",
    "configure_app_logging",
    "run_log",
    "shutdown_app_logging",
]
