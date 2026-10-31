"""Measure test coverage of PyHydroGeophysX and record the baseline (plan M1.8).

    python tools/yuem/coverage.py                 # every tier; print the summary
    python tools/yuem/coverage.py --record        # also write .yuem/metrics/coverage-baseline.json
    python tools/yuem/coverage.py -m "not slow"   # a subset of the tiers

Subprocess runs (the workflow smoke tests) are measured through coverage's
startup hook. Per-package figures make the target of the plan measurable: 80 %
of the core algorithm paths (data_processing, forward, inversion).
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from collections import defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASELINE = ROOT / ".yuem" / "metrics" / "coverage-baseline.json"
CORE = ("data_processing", "forward", "inversion")


def measure(marker: str | None) -> dict[str, object]:
    with tempfile.TemporaryDirectory() as scratch:
        report = Path(scratch) / "coverage.json"
        rcfile = Path(scratch) / ".coveragerc"
        rcfile.write_text(
            "[run]\nsource = PyHydroGeophysX\nbranch = true\nparallel = true\n"
            "omit = */agents/*\n    */llm/*\n    */mcp_server.py\n",
            encoding="utf-8",
        )
        env = {
            **os.environ,
            "COVERAGE_PROCESS_START": str(rcfile),
            "COVERAGE_FILE": str(Path(scratch) / ".coverage"),
            "MPLBACKEND": "Agg",
            "QT_QPA_PLATFORM": "offscreen",
        }
        command = [
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "-p",
            "no:cacheprovider",
            "--cov=PyHydroGeophysX",
            f"--cov-config={rcfile}",
            f"--cov-report=json:{report}",
        ]
        if marker:
            command += ["-m", marker]
        subprocess.run(command, cwd=ROOT, env=env, check=False)
        data = json.loads(report.read_text(encoding="utf-8"))
    by_package: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    for name, entry in data["files"].items():
        parts = Path(name).parts
        package = parts[parts.index("PyHydroGeophysX") + 1] if "PyHydroGeophysX" in parts else "?"
        package = package.removesuffix(".py")
        summary = entry["summary"]
        by_package[package][0] += int(summary["covered_lines"])
        by_package[package][1] += int(summary["num_statements"])
    packages = {
        name: round(100.0 * covered / total, 1)
        for name, (covered, total) in sorted(by_package.items())
        if total
    }
    core_covered = sum(by_package[name][0] for name in CORE)
    core_total = sum(by_package[name][1] for name in CORE)
    return {
        "date": date.today().isoformat(),
        "marker": marker or "all tiers",
        "percent": round(float(data["totals"]["percent_covered"]), 1),
        "core_percent": round(100.0 * core_covered / core_total, 1) if core_total else None,
        "packages": packages,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--record", action="store_true")
    parser.add_argument("-m", dest="marker", default=None)
    args = parser.parse_args(argv)
    result = measure(args.marker)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    if args.record:
        BASELINE.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"Wrote {BASELINE.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
