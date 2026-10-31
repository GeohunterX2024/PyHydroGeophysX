"""Shared setup for the YUEM test tree.

Matplotlib and Qt are pinned to their headless backends before any test module
imports them, so the suite behaves the same on a desktop and on CI runners.
"""

from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path
from types import ModuleType

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


def load_tool(name: str) -> ModuleType:
    """Import ``tools/yuem/<name>.py`` without leaving tools/yuem on sys.path.

    Its scripts are named like packages (coverage, metrics, golden), so a path
    entry left behind would shadow those packages for every later import.
    """
    module_name = f"yuem_tool_{name}"
    if module_name in sys.modules:
        return sys.modules[module_name]
    saved = list(sys.path)
    spec = importlib.util.spec_from_file_location(module_name, REPO_ROOT / "tools" / "yuem" / f"{name}.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module  # dataclasses look their module up while it executes
    try:
        sys.path.insert(0, str(REPO_ROOT / "tools" / "yuem"))
        spec.loader.exec_module(module)
    except BaseException:
        del sys.modules[module_name]
        raise
    finally:
        sys.path[:] = saved
    return module
