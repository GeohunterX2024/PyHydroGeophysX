"""Consistency of the fork's packaging metadata (ADR 0002)."""

from __future__ import annotations

import re
from pathlib import Path

import tomllib

import PyHydroGeophysX


def _pyproject(repo_root: Path) -> dict[str, object]:
    return tomllib.loads((repo_root / "pyproject.toml").read_text(encoding="utf-8"))


def _extras(repo_root: Path) -> dict[str, list[str]]:
    project = _pyproject(repo_root)["project"]
    assert isinstance(project, dict)
    extras = project["optional-dependencies"]
    assert isinstance(extras, dict)
    return extras


def test_package_version_matches_pyproject(repo_root: Path) -> None:
    project = _pyproject(repo_root)["project"]
    assert isinstance(project, dict)
    assert PyHydroGeophysX.__version__ == project["version"]


def test_version_is_a_yuem_local_version(repo_root: Path) -> None:
    assert re.fullmatch(r"\d+\.\d+\.\d+\+yuem\.\d+", PyHydroGeophysX.__version__)


def test_dev_extra_and_dev_group_list_the_same_tools(repo_root: Path) -> None:
    data = _pyproject(repo_root)
    project = data["project"]
    groups = data["dependency-groups"]
    assert isinstance(project, dict) and isinstance(groups, dict)
    assert sorted(project["optional-dependencies"]["dev"]) == sorted(groups["dev"])


def test_extras_that_need_cuda_do_not_break_macos(repo_root: Path) -> None:
    extras = _extras(repo_root)
    for name in ("gpu", "all"):
        for requirement in extras[name]:
            if requirement.startswith("cupy"):
                assert "sys_platform != 'darwin'" in requirement, requirement
    for requirement in extras["adtlert"]:
        if requirement.startswith("adtlert"):
            assert "sys_platform != 'darwin'" in requirement, requirement


def test_pftools_is_a_separate_opt_in(repo_root: Path) -> None:
    extras = _extras(repo_root)
    assert any(r.startswith("pftools") for r in extras["parflow-tools"])
    for name in ("geophysics", "all"):
        assert not any(r.startswith("pftools") for r in extras[name])
