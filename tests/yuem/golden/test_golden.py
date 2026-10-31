"""Golden regression: fresh runs must reproduce the recorded outputs (plan M1.4).

A failure means a numerical result changed. If the change is intended, record
it with ``python tools/yuem/golden.py --update --case <name> --reason "..."``.
"""

from __future__ import annotations

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
    for key, value in expected.items():
        np.testing.assert_allclose(
            actual[key], value, rtol=case.rtol, atol=case.atol, err_msg=f"{case.name}: {key}"
        )
