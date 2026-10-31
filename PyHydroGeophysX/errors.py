"""Domain exceptions of PyHydroGeophysX (plan M2.3).

Raise these instead of bare ``ValueError``/``RuntimeError`` where the cause is
known, so every boundary can tell the user what went wrong and what to do:

* the Studio's worker process (``qt_apps.workers``) turns the last exception
  line a workflow process printed into a plain sentence;
* ``pyhydrogeophysx-workflow run`` prints one line and exits with
  :data:`EXIT_DOMAIN_ERROR` instead of a traceback;
* the Studio's in-process workers show :func:`describe`.

Messages carry their location (file, line, field) in ``str(exc)``, because a
worker process hands only the text of the exception back to the Studio.

The classes subclass the built-in exception callers already catch
(``ValueError`` for bad data, ``RuntimeError`` for a failed solve), so raising
them in place of those breaks no existing ``except``.
"""

from __future__ import annotations

from pathlib import Path

from PyHydroGeophysX._internal.optional_dependencies import BackendUnavailable

#: Exit code of the workflow CLI for a domain error (a traceback exits with 1).
EXIT_DOMAIN_ERROR = 2


class PHGXError(Exception):
    """Base class. ``hint`` says what the user can do about it."""

    default_hint = ""

    def __init__(self, message: str, *, hint: str = "") -> None:
        super().__init__(message)
        self.message = message
        self.hint = hint or self.default_hint


class DataValidationError(PHGXError, ValueError):
    """Input data that cannot be used as given: a bad value, column, geometry or file."""

    default_hint = "check the file, its format setting and the column it names"

    def __init__(
        self,
        message: str,
        *,
        file: str | Path | None = None,
        line: int | None = None,
        field: str | None = None,
        hint: str = "",
    ) -> None:
        self.file = None if file is None else str(file)
        self.line = line
        self.field = field
        where = []
        if self.file:
            where.append(Path(self.file).name)
        if line is not None:
            where.append(f"line {line}")
        if field:
            where.append(f"field {field!r}")
        text = f"{', '.join(where)}: {message}" if where else message
        super().__init__(text, hint=hint)


class ConvergenceError(PHGXError, RuntimeError):
    """An iterative solve that did not reach an acceptable result."""

    default_hint = "relax the regularization, check the error model, or allow more iterations"


class Cancelled(PHGXError):
    """The user stopped the run. Not a failure: boundaries report it as cancelled."""


class ResourceLimitError(PHGXError, RuntimeError):
    """The run needs more memory, disk or time than is available."""

    default_hint = "use a coarser mesh or fewer cells, free memory or disk space, and run again"


#: Plain-language meaning of each class, in the Studio's language (en) and Chinese (zh).
MEANINGS: dict[str, tuple[str, str]] = {
    "DataValidationError": ("The input data could not be used", "输入数据无法使用"),
    "ConvergenceError": ("The inversion did not converge", "反演未收敛"),
    "Cancelled": ("The run was cancelled", "运行已取消"),
    "ResourceLimitError": ("The run needs more resources than are available", "运行所需资源超出可用范围"),
    "BackendUnavailable": ("A required computing engine is not available", "所需的计算引擎不可用"),
}


def describe(exc: BaseException, language: str = "en") -> str:
    """One sentence for the user: the meaning, the detail, and the hint."""
    index = 1 if language.lower().startswith("zh") else 0
    meaning = MEANINGS.get(type(exc).__name__)
    detail = str(exc).strip()
    text = f"{meaning[index]}: {detail}" if meaning else f"{type(exc).__name__}: {detail}"
    hint = getattr(exc, "hint", "")
    return f"{text.rstrip('.')} - {hint}." if hint else text


__all__ = [
    "EXIT_DOMAIN_ERROR",
    "MEANINGS",
    "BackendUnavailable",
    "Cancelled",
    "ConvergenceError",
    "DataValidationError",
    "PHGXError",
    "ResourceLimitError",
    "describe",
]
