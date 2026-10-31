"""Application log, per-run log, and the silent-except ratchet (plan M2.4)."""

from __future__ import annotations

import json
import logging
import subprocess
import sys
from collections.abc import Iterator
from pathlib import Path
from types import SimpleNamespace

import pytest

from PyHydroGeophysX._internal import logging_setup
from PyHydroGeophysX._internal.logging_setup import (
    APP_LOG_NAME,
    LOGGER_NAME,
    RUN_LOG_NAME,
    RepeatFilter,
    app_log_dir,
    configure_app_logging,
    run_log,
    shutdown_app_logging,
)

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def app_log(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[Path]:
    monkeypatch.setenv("PHGX_LOG_DIR", str(tmp_path / "logs"))
    shutdown_app_logging()
    try:
        yield tmp_path / "logs" / APP_LOG_NAME
    finally:
        shutdown_app_logging()


def _records(path: Path) -> list[dict[str, str]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def test_log_dir_override(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("PHGX_LOG_DIR", str(tmp_path))
    assert app_log_dir() == tmp_path
    monkeypatch.delenv("PHGX_LOG_DIR")
    if sys.platform == "darwin":
        assert app_log_dir() == Path.home() / "Library" / "Logs" / "PHGX"


def test_app_log_records_swallowed_failures_and_prints(
    app_log: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = configure_app_logging(capture_output=True)
    assert path == app_log
    assert configure_app_logging() == app_log  # idempotent
    try:
        raise KeyError("missing column")
    except KeyError:
        logging.getLogger(f"{LOGGER_NAME}.qt_apps.example").debug("redraw: ignored", exc_info=True)
    print("upstream progress line")
    shutdown_app_logging()
    text = app_log.read_text(encoding="utf-8")
    assert "redraw: ignored" in text and "KeyError: 'missing column'" in text
    assert "INFO    [" in text and "PyHydroGeophysX.output.stdout: upstream progress line" in text
    assert "upstream progress line" in capsys.readouterr().out  # still reaches the console
    assert not isinstance(sys.stdout, logging_setup._StreamTee)


def test_repeat_filter_keeps_the_first_tracebacks_from_one_place() -> None:
    flt = RepeatFilter(limit=2)
    passed = []
    for _ in range(5):
        try:
            raise ValueError("again")
        except ValueError:
            record = logging.LogRecord("x", logging.DEBUG, "f.py", 7, "m", None, sys.exc_info())
        passed.append(flt.filter(record))
    assert passed == [True, True, False, False, False]
    assert flt.filter(logging.LogRecord("x", logging.INFO, "f.py", 7, "plain", None, None))


def test_run_log_writes_records_output_and_failure(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    logger = logging.getLogger(f"{LOGGER_NAME}.workflows.example")
    with pytest.raises(RuntimeError), run_log(tmp_path) as path:
        assert path == tmp_path / RUN_LOG_NAME
        logger.info("mesh has %d cells", 120)
        logger.debug("not at INFO")
        print("iteration 1 chi2 = 3.2")
        raise RuntimeError("solver stopped")
    entries = _records(tmp_path / RUN_LOG_NAME)
    messages = [e["message"] for e in entries]
    assert "mesh has 120 cells" in messages and "iteration 1 chi2 = 3.2" in messages
    assert "not at INFO" not in messages
    failure = entries[-1]
    assert failure["level"] == "ERROR" and "RuntimeError: solver stopped" in failure["exc"]
    assert "iteration 1 chi2 = 3.2" in capsys.readouterr().out
    assert not isinstance(sys.stdout, logging_setup._StreamTee)
    assert logging.getLogger(LOGGER_NAME).handlers == []


def test_cli_run_leaves_a_run_log(tmp_path: Path) -> None:
    recipe = tmp_path / "recipe.json"
    out = tmp_path / "out"
    recipe.write_text(
        json.dumps(
            {
                "schema_version": "1",
                "workflow_id": "gravmag.process",
                "inputs": {"x": [0.0, 1.0], "y": [0.0], "values": [1.0, 2.0]},
                "output_dir": str(out),
            }
        )
    )
    subprocess.run(
        [sys.executable, "-m", "PyHydroGeophysX.workflows.cli", "run", str(recipe), "--output-dir", str(out)],
        capture_output=True,
        text=True,
        check=False,
    )
    entries = _records(out / RUN_LOG_NAME)
    assert entries[-1]["level"] == "ERROR"
    assert "DataValidationError" in entries[-1]["exc"]


class _Page:
    """Stands in for a BaseModule: what BaseModule.log touches."""

    def __init__(self) -> None:
        self.shown: list[tuple[str, str]] = []
        self.log_listeners: list[object] = []

    def _log_fn(self, message: str, level: str) -> None:
        self.shown.append((message, level))

    def _keep_log_line(self, message: str, level: str) -> None:
        pass


def test_page_log_reaches_logging(caplog: pytest.LogCaptureFixture) -> None:
    pytest.importorskip("PySide6")
    from PyHydroGeophysX.qt_apps.modules.base import BaseModule

    page = _Page()
    with caplog.at_level(logging.DEBUG, logger=__name__):
        BaseModule.log(page, "electrode spacing looks irregular", "warn")
    assert page.shown == [("electrode spacing looks irregular", "warn")]
    record = next(r for r in caplog.records if r.name == __name__)
    assert record.levelno == logging.WARNING


def test_silent_except_metric() -> None:
    sys.path.insert(0, str(ROOT / "tools" / "yuem"))
    from metrics import silent_broad_excepts

    source = SimpleNamespace(
        silent="try:\n    f()\nexcept Exception:\n    pass\n",
        bare="try:\n    f()\nexcept:\n    x = 1\n",
        logged="try:\n    f()\nexcept Exception:\n    _logger.debug('f', exc_info=True)\n",
        used="try:\n    f()\nexcept Exception as exc:\n    show(str(exc))\n",
        raised="try:\n    f()\nexcept Exception:\n    cleanup()\n    raise\n",
        narrow="try:\n    f()\nexcept ValueError:\n    pass\n",
    )
    counts = {name: silent_broad_excepts(text) for name, text in vars(source).items()}
    assert counts == {"silent": 1, "bare": 1, "logged": 0, "used": 0, "raised": 0, "narrow": 0}
