"""Recorder for the numerical verification set (plan M1.3).

Each case calls ``verify(...)`` once with its reference, the error it measured
and its tolerance; the fixture asserts the tolerance and keeps the record. When
``PHGX_VERIFICATION_JSON`` names a file, every record of the session is written
there, and ``tools/yuem/verification_report.py`` turns it into
``docs/yuem/verification.md``.
"""

from __future__ import annotations

import json
import os
import time
from collections.abc import Callable, Iterator
from pathlib import Path
from typing import Any

import pytest

RECORDS: list[dict[str, Any]] = []
OUTPUT_ENV = "PHGX_VERIFICATION_JSON"

Verify = Callable[..., None]


@pytest.fixture
def verify(request: pytest.FixtureRequest) -> Iterator[Verify]:
    started = time.monotonic()
    recorded: list[dict[str, Any]] = []

    def record(
        *,
        case: str,
        title: str,
        method: str,
        engine: str,
        reference: str,
        metric: str,
        value: float,
        tolerance: float,
        note: str = "",
    ) -> None:
        entry = {
            "case": case,
            "title": title,
            "method": method,
            "engine": engine,
            "reference": reference,
            "metric": metric,
            "value": float(value),
            "tolerance": float(tolerance),
            "passed": bool(float(value) <= float(tolerance)),
            "note": note,
            "test": request.node.nodeid,
        }
        recorded.append(entry)
        assert entry["passed"], f"{case}: {metric} = {value:.3e} exceeds {tolerance:.3e}"

    yield record
    for entry in recorded:
        entry["seconds"] = round(time.monotonic() - started, 2)
        RECORDS.append(entry)


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    target = os.environ.get(OUTPUT_ENV)
    if target:
        Path(target).write_text(json.dumps(RECORDS, indent=2, ensure_ascii=False), encoding="utf-8")
