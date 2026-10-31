"""Benchmarks run only through tools/yuem/perf.py (PHGX_PERF=1): they take minutes."""

from __future__ import annotations

import os

import pytest


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    if os.environ.get("PHGX_PERF") == "1":
        for item in items:
            # pytest-benchmark 5.3 reads the private ``_nodeid`` that pytest 9 no longer has.
            if not hasattr(item, "_nodeid"):
                item._nodeid = item.nodeid  # type: ignore[attr-defined]
        return
    skip = pytest.mark.skip(reason="benchmarks run through tools/yuem/perf.py")
    for item in items:
        if "benchmark" in item.keywords and "perf" in str(item.fspath):
            item.add_marker(skip)
