"""Golden regression: fresh runs must reproduce the recorded outputs (plan M1.4).

A failure means a numerical result changed. If the change is intended, record
it with ``python tools/yuem/golden.py --update --case <name> --reason "..."``.
"""

from __future__ import annotations

import json
import platform
from pathlib import Path

import numpy as np
import pytest

from ..smoke.recipes import Workspace
from .cases import CASES, DATA, GoldenCase, compute

pytestmark = pytest.mark.golden


@pytest.fixture(scope="module")
def workspace(tmp_path_factory: pytest.TempPathFactory, examples_data: Path) -> Workspace:
    root = tmp_path_factory.mktemp("golden") / "金标准 工程"
    root.mkdir()
    return Workspace(root, examples_data)


@pytest.mark.parametrize("case", CASES, ids=[case.name for case in CASES])
def test_golden(case: GoldenCase, workspace: Workspace) -> None:
    target = DATA / f"{case.name}.npz"
    if not target.exists():
        pytest.fail(f"no golden record for {case.name}; run tools/yuem/golden.py --update --case {case.name}")
    with np.load(target) as archive:
        expected = {key: archive[key] for key in archive.files}
    actual = compute(case, workspace)
    assert sorted(actual) == sorted(expected), "the set of outputs changed"
    recorded = json.loads((DATA / f"{case.name}.json").read_text(encoding="utf-8"))["environment"]["platform"]
    cross = case.cross_platform is not None and (recorded["system"], recorded["machine"]) != (
        platform.system(),
        platform.machine(),
    )
    report = []
    for key, value in sorted(expected.items()):
        got = np.asarray(actual[key], dtype=float)
        want = np.asarray(value, dtype=float)
        if got.shape != want.shape:
            report.append(f"{key}: shape {got.shape} != {want.shape}")
            continue
        diff = np.abs(got - want)
        if cross:
            scale = float(np.nanmax(np.abs(want))) if want.size else 0.0
            if not np.nanmax(diff, initial=0.0) > case.cross_platform * scale + case.atol:
                continue
        elif np.allclose(got, want, rtol=case.rtol, atol=case.atol, equal_nan=True):
            continue
        rel = diff / np.maximum(np.abs(want), np.finfo(float).tiny)
        report.append(f"{key}: max abs {np.nanmax(diff):.3e}, max rel {np.nanmax(rel):.3e}")
    limits = (
        f"cross-platform {case.cross_platform:g} of each array's largest value"
        if cross
        else f"rtol {case.rtol:g}, atol {case.atol:g}"
    )
    assert not report, f"{case.name} ({limits}):\n" + "\n".join(report)
