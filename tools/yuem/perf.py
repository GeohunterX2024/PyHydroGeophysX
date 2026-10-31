"""Timing baseline of key workflows, per machine (plan M5.3).

    python tools/yuem/perf.py record              # time the workloads, keep them as this machine's baseline
    python tools/yuem/perf.py check               # time them again; warn where one is >20 % slower
    python tools/yuem/perf.py check --strict      # ...and exit 1 then (CI can choose)

Workloads are in tests/yuem/perf/test_benchmarks.py: ERT single inversion,
TEM LCI line, MT Occam 1-D, each run three times; the median counts. A
baseline is only compared on the machine it was recorded on (CI runners by
operating system and architecture), since another machine's time says
nothing about a slowdown.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _repo import ROOT

BASELINE = ROOT / ".yuem" / "metrics" / "perf-baseline.json"
THRESHOLD = 0.20


def machine_key() -> str:
    """CI: ``ci-<system>-<machine>``; elsewhere the host, hashed, and its CPU count."""
    base = f"{platform.system()}-{platform.machine()}".lower()
    if os.environ.get("CI"):
        return f"ci-{base}"
    host = hashlib.sha256(platform.node().encode()).hexdigest()[:8]
    return f"{base}-{host}-{os.cpu_count()}cpu"


def measure() -> dict[str, float]:
    """Median seconds of each workload, from a pytest-benchmark run."""
    with tempfile.TemporaryDirectory() as folder:
        report = Path(folder) / "bench.json"
        done = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                "-q",
                "-p",
                "no:cacheprovider",
                "tests/yuem/perf",
                f"--benchmark-json={report}",
                "--benchmark-disable-gc",
            ],
            cwd=ROOT,
            env={**os.environ, "PHGX_PERF": "1"},
            check=False,
        )
        if done.returncode != 0 or not report.exists():
            raise SystemExit(f"benchmarks failed (exit {done.returncode})")
        data = json.loads(report.read_text(encoding="utf-8"))
    times = {}
    for bench in data["benchmarks"]:
        name = str(bench["param"] or bench["name"])
        times[name] = round(float(bench["stats"]["median"]), 3)
    return times


def load() -> dict[str, dict[str, object]]:
    if not BASELINE.exists():
        return {}
    return dict(json.loads(BASELINE.read_text(encoding="utf-8")))


def record() -> int:
    baselines = load()
    times = measure()
    baselines[machine_key()] = {
        "recorded": date.today().isoformat(),
        "python": platform.python_version(),
        "seconds": times,
    }
    BASELINE.parent.mkdir(parents=True, exist_ok=True)
    BASELINE.write_text(json.dumps(baselines, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    for name, seconds in sorted(times.items()):
        print(f"  {name:<24}{seconds:8.2f} s")
    print(f"Recorded as the baseline of {machine_key()} in {BASELINE.relative_to(ROOT)}")
    return 0


def check(strict: bool, threshold: float) -> int:
    entry = load().get(machine_key())
    if not entry:
        print(f"No baseline for {machine_key()}; record one with: python tools/yuem/perf.py record")
        return 0
    seconds_by_name = entry.get("seconds")
    reference = dict(seconds_by_name) if isinstance(seconds_by_name, dict) else {}
    times = measure()
    slower = []
    for name, seconds in sorted(times.items()):
        base = float(reference.get(name, 0.0))
        change = (seconds - base) / base if base > 0 else 0.0
        flag = "  SLOWER" if change > threshold else ""
        print(f"  {name:<24}{seconds:8.2f} s  (baseline {base:.2f} s, {change:+.0%}){flag}")
        if change > threshold:
            slower.append(f"{name}: {seconds:.2f} s vs {base:.2f} s ({change:+.0%})")
    for line in slower:
        if os.environ.get("GITHUB_ACTIONS"):
            print(f"::warning title=Performance::{line}")
    if slower:
        print(f"{len(slower)} workload(s) more than {threshold:.0%} slower than the baseline.")
    return 1 if (slower and strict) else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("record")
    checking = sub.add_parser("check")
    checking.add_argument("--strict", action="store_true")
    checking.add_argument("--threshold", type=float, default=THRESHOLD)
    args = parser.parse_args(argv)
    return record() if args.command == "record" else check(args.strict, args.threshold)


if __name__ == "__main__":
    raise SystemExit(main())
