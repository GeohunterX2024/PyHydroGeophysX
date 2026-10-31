"""Explicit run context: folders and the thread budget (plan M2.5)."""

from __future__ import annotations

import ast
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
import tomllib

from PyHydroGeophysX.workflows.models import RunContext, WorkflowValidationError

from .conftest import load_tool

ROOT = Path(__file__).resolve().parents[2]


def test_cache_dir_defaults_to_the_user_cache(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PHGX_CACHE_DIR", str(tmp_path / "cache"))
    context = RunContext(project_root=tmp_path, output_dir=tmp_path / "out")
    context.prepare()
    assert context.cache_dir == (tmp_path / "cache").resolve()
    tiles = context.cache_path("tiles", "osm")
    assert tiles.is_dir() and tiles.parent.parent == context.cache_dir


def test_threads_must_be_positive(tmp_path: Path) -> None:
    with pytest.raises(WorkflowValidationError):
        RunContext(project_root=tmp_path, output_dir=tmp_path, threads=0).prepare()


def test_thread_limits_apply_and_restore() -> None:
    threadpoolctl = pytest.importorskip("threadpoolctl")
    pg = pytest.importorskip("pygimli")
    pytest.importorskip("numpy")  # loads the BLAS threadpoolctl reports

    before_pg = pg.core.threadCount()
    before_blas = [info["num_threads"] for info in threadpoolctl.threadpool_info()]
    with RunContext(threads=1).thread_limits():
        assert pg.core.threadCount() == 1
        assert all(info["num_threads"] == 1 for info in threadpoolctl.threadpool_info())
    assert pg.core.threadCount() == before_pg
    assert [info["num_threads"] for info in threadpoolctl.threadpool_info()] == before_blas


def test_cli_records_the_thread_budget(tmp_path: Path) -> None:
    recipe = tmp_path / "recipe.json"
    recipe.write_text(
        json.dumps(
            {
                "schema_version": "1",
                "workflow_id": "gravmag.process",
                "inputs": {
                    "x": [0.0, 1.0, 0.0, 1.0],
                    "y": [0.0, 0.0, 1.0, 1.0],
                    "values": [1.0, 2.0, 3.0, 4.0],
                },
            }
        )
    )
    result = tmp_path / "result.json"
    done = subprocess.run(
        [
            sys.executable,
            "-m",
            "PyHydroGeophysX.workflows.cli",
            "run",
            str(recipe),
            "--output-dir",
            str(tmp_path / "out"),
            "--result-file",
            str(result),
            "--threads",
            "2",
        ],
        capture_output=True,
        text=True,
        check=False,
        env={**os.environ, "PHGX_EXIT_WITH_PARENT": "0"},
    )
    assert done.returncode == 0, done.stderr
    assert json.loads(result.read_text())["provenance"]["threads"] == 2


def _environment_reads(path: Path) -> int:
    """``os.environ`` uses and ``os.getenv`` calls in one file."""
    count = 0
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id == "os":
            count += node.attr in {"environ", "getenv", "putenv", "unsetenv"}
    return count


def test_algorithm_layers_read_no_new_environment_variables() -> None:
    """Outside own code, environment reads stay where upstream had them (ADR 0003)."""
    repo = load_tool("_repo")
    own = repo.ownership()
    allowed = tomllib.loads((ROOT / ".yuem" / "environ_reads.toml").read_text(encoding="utf-8"))["files"]
    found = {}
    for path in repo.tracked_python_files("PyHydroGeophysX"):
        rel = path.relative_to(ROOT).as_posix()
        if own.classify(rel) == "own":
            continue
        reads = _environment_reads(path)
        if reads:
            found[rel] = reads
    grown = {rel: (allowed.get(rel, 0), n) for rel, n in found.items() if n > allowed.get(rel, 0)}
    assert not grown, f"new environment reads (allowed, found): {grown}; take the setting from RunContext"
    shrunk = {rel: (n, found.get(rel, 0)) for rel, n in allowed.items() if found.get(rel, 0) < n}
    assert not shrunk, f"lower these entries in .yuem/environ_reads.toml: {shrunk}"
