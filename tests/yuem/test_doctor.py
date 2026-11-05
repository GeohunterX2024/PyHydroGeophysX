"""Environment self-check (plan M1.6)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from PyHydroGeophysX import doctor
from PyHydroGeophysX.doctor import Check, exit_code, format_report, run_checks


def test_every_check_runs_and_reports_a_known_status(tmp_path: Path) -> None:
    checks = run_checks(project=tmp_path)
    names = {check.name for check in checks}
    for expected in ("Python", "PyHydroGeophysX", "Core libraries", "pyGIMLi core", "Project folder"):
        assert expected in names
    assert {check.status for check in checks} <= {"ok", "warn", "error"}


def test_survey_3d_check_names_the_simple_view_when_forced(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PHGX_SURVEY_3D", "simple")
    check = doctor._check_survey_3d()
    assert check.status == "ok" and "PHGX_SURVEY_3D" in check.detail
    monkeypatch.delenv("PHGX_SURVEY_3D")
    assert doctor._check_survey_3d().name == "Survey 3D view"


def test_exit_code_reflects_the_worst_status() -> None:
    assert exit_code([Check("a", "ok", "")]) == 0
    assert exit_code([Check("a", "ok", ""), Check("b", "warn", "")]) == 1
    assert exit_code([Check("a", "warn", ""), Check("b", "error", "")]) == 2


def test_report_shows_hints_only_for_problems() -> None:
    text = format_report([Check("a", "ok", "fine", "unused"), Check("b", "error", "broken", "fix it")])
    assert "unused" not in text
    assert "-> fix it" in text
    assert "[FAIL] b: broken" in text


def test_a_crashing_check_is_reported_not_raised(monkeypatch: pytest.MonkeyPatch) -> None:
    def boom() -> Check:
        raise RuntimeError("kaput")

    monkeypatch.setattr(doctor, "_check_qt", boom)
    checks = run_checks()
    crashed = [c for c in checks if "kaput" in c.detail]
    assert crashed and crashed[0].status == "error"


def test_macos_missing_libblas_is_an_error(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    package = tmp_path / "pgcore"
    (package / ".dylibs").mkdir(parents=True)
    (package / ".dylibs" / "libopenblas.0.dylib").write_bytes(b"")

    class Spec:
        submodule_search_locations = (str(package),)

    real_find_spec = doctor.importlib.util.find_spec
    monkeypatch.setattr(doctor.sys, "platform", "darwin")
    monkeypatch.setattr(
        doctor.importlib.util,
        "find_spec",
        lambda name: Spec() if name == "pgcore" else real_find_spec(name),
    )
    check = doctor._check_pygimli_core()
    if real_find_spec("pygimli") is None:
        pytest.skip("pygimli not installed")
    assert check.status == "error"
    assert "libblas.3.dylib" in check.detail


def test_json_output(capsys: pytest.CaptureFixture[str], tmp_path: Path) -> None:
    code = doctor.main(["--json", "--project", str(tmp_path)])
    report = json.loads(capsys.readouterr().out)
    assert report["exit_code"] == code
    assert {"name", "status", "detail", "hint"} <= set(report["checks"][0])
