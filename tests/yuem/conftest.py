"""Shared setup for the YUEM test tree.

Matplotlib and Qt are pinned to their headless backends before any test module
imports them, so the suite behaves the same on a desktop and on CI runners.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

os.environ.setdefault("MPLBACKEND", "Agg")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

REPO_ROOT = Path(__file__).resolve().parents[2]
EXAMPLES_DATA = REPO_ROOT / "examples" / "data"


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return REPO_ROOT


@pytest.fixture(scope="session")
def examples_data() -> Path:
    if not EXAMPLES_DATA.is_dir():
        pytest.skip("examples/data is not present in this checkout")
    return EXAMPLES_DATA
