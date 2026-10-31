"""Domain exceptions and how each boundary reports them (plan M2.3)."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from PyHydroGeophysX.errors import (
    EXIT_DOMAIN_ERROR,
    Cancelled,
    ConvergenceError,
    DataValidationError,
    PHGXError,
    ResourceLimitError,
    describe,
)


def test_data_validation_error_names_its_location() -> None:
    exc = DataValidationError("negative resistance", file="/data/line 2.dat", line=17, field="r")
    assert str(exc) == "line 2.dat, line 17, field 'r': negative resistance"
    assert exc.file == "/data/line 2.dat" and exc.line == 17 and exc.field == "r"


def test_domain_errors_are_caught_by_existing_handlers() -> None:
    with pytest.raises(ValueError):
        raise DataValidationError("bad")
    with pytest.raises(RuntimeError):
        raise ConvergenceError("chi2 stalled at 12")
    with pytest.raises(RuntimeError):
        raise ResourceLimitError("needs 40 GB")
    assert issubclass(Cancelled, PHGXError)


def test_describe_in_both_languages() -> None:
    exc = ConvergenceError("chi2 stalled at 12", hint="raise lambda")
    assert describe(exc) == "The inversion did not converge: chi2 stalled at 12 - raise lambda."
    assert describe(exc, "zh").startswith("反演未收敛: chi2 stalled at 12")


def test_worker_turns_the_cli_line_into_a_plain_sentence() -> None:
    pytest.importorskip("PySide6")
    from PyHydroGeophysX.qt_apps.workers import _process_failure_message

    line = "DataValidationError: a.dat, line 3: no electrodes (hint: check the format)"
    message = _process_failure_message(EXIT_DOMAIN_ERROR, False, last_exception=line)
    assert message.startswith("The input data could not be used (DataValidationError: a.dat, line 3")


def test_in_process_worker_message() -> None:
    pytest.importorskip("PySide6")
    from PyHydroGeophysX.qt_apps.workers import _error_message

    exc = DataValidationError("no electrodes", file="a.dat", line=3)
    assert _error_message(exc) == describe(exc)
    assert _error_message(ValueError("plain")) == "plain"


def test_cli_reports_a_domain_error_in_one_line(tmp_path: Path) -> None:
    recipe = tmp_path / "recipe.json"
    recipe.write_text(
        json.dumps(
            {
                "schema_version": "1",
                "workflow_id": "gravmag.process",
                "inputs": {"x": [0.0, 1.0], "y": [0.0], "values": [1.0, 2.0]},
                "output_dir": str(tmp_path / "out"),
            }
        )
    )
    done = subprocess.run(
        [sys.executable, "-m", "PyHydroGeophysX.workflows.cli", "run", str(recipe)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert done.returncode == EXIT_DOMAIN_ERROR, done.stderr
    assert "Traceback" not in done.stderr
    last = done.stderr.strip().splitlines()[-1]
    assert last.startswith("DataValidationError: gravmag.process requires x, y, and values of equal length")
    assert "(got 2, 1, 2)" in last and "(hint: " in last
