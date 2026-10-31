"""Engineering metrics of the fork and the ratchet that keeps them from regressing.

    python tools/yuem/metrics.py                    # print metrics and the delta to the baseline
    python tools/yuem/metrics.py --json             # machine-readable output
    python tools/yuem/metrics.py --check            # gate: fail when any metric got worse
    python tools/yuem/metrics.py --update-baseline --reason "..."

Down-only metrics may never rise above the baseline; ``tests`` may never fall
below it. ``--update-baseline`` rewrites the baseline with the current values and
appends the reason to ``.yuem/metrics/CHANGES.md``; raising a down-only metric
also needs ``--allow-regression`` (for example after a sync brings in upstream
code), which the reviewer must approve. The check also enforces the file-length
rule of ADR 0003 on files changed since the upstream base.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

import tomllib

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _repo import ROOT, changed_files, file_at, ownership, tracked_python_files, upstream_ref

BASELINE = ROOT / ".yuem" / "metrics" / "baseline-0.5.0.json"
CHANGES = ROOT / ".yuem" / "metrics" / "CHANGES.md"
PACKAGE = "PyHydroGeophysX"

PATTERNS: dict[str, re.Pattern[str]] = {
    "broad_except": re.compile(r"^\s*except\s*(?:\(\s*)?(?:Exception|BaseException)\b|^\s*except\s*:", re.M),
    "print_calls": re.compile(r"^\s*print\(", re.M),
    "suppressions": re.compile(r"#\s*(?:noqa|type:\s*ignore)\b"),
    "logging_getlogger": re.compile(r"logging\.getLogger\("),
    "os_environ": re.compile(r"\bos\.environ\b"),
    "global_np_random": re.compile(
        r"\bnp\.random\.(?:seed|rand|randn|randint|random|normal|uniform|choice|shuffle|permutation)\("
    ),
}
WORKER_RE = re.compile(r"\b(?:TaskWorker|WorkflowWorker)\b")
TEST_RE = re.compile(r"^\s*(?:async\s+)?def\s+test_\w*\(", re.M)

DOWN_ONLY = (
    "broad_except",
    "print_calls",
    "suppressions",
    "files_over_2000",
    "os_environ",
    "global_np_random",
    "inprocess_worker_modules",
    "layer_exceptions",
)
UP_ONLY = ("tests", "logging_getlogger")
LONG_FILE = 2000


ALLOWLIST = ROOT / ".yuem" / "metrics_allowlist.toml"


def _rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def load_allowlist() -> dict[str, dict[str, str]]:
    """metric -> {file: reason} from .yuem/metrics_allowlist.toml."""
    if not ALLOWLIST.exists():
        return {}
    data = tomllib.loads(ALLOWLIST.read_text(encoding="utf-8"))
    return {metric: {str(k): str(v) for k, v in files.items()} for metric, files in data.items()}


def collect() -> dict[str, object]:
    """Count every metric over the package and the test tree."""
    own = ownership()
    allow = load_allowlist()
    totals: dict[str, int] = dict.fromkeys(PATTERNS, 0)
    allowlisted: dict[str, int] = dict.fromkeys(PATTERNS, 0)
    by_class: dict[str, dict[str, int]] = {}
    long_files: list[str] = []
    worker_modules: list[str] = []
    lines_total = 0
    for path in tracked_python_files(PACKAGE):
        text = path.read_text(encoding="utf-8", errors="replace")
        rel = _rel(path)
        cls = own.classify(rel)
        n_lines = text.count("\n") + (0 if text.endswith("\n") or not text else 1)
        lines_total += n_lines
        if n_lines > LONG_FILE:
            long_files.append(rel)
        if rel.startswith(f"{PACKAGE}/qt_apps/modules/") and WORKER_RE.search(text):
            worker_modules.append(rel)
        bucket = by_class.setdefault(cls, dict.fromkeys(PATTERNS, 0))
        for name, pattern in PATTERNS.items():
            hits = len(pattern.findall(text))
            if rel in allow.get(name, {}):
                allowlisted[name] += hits
                continue
            totals[name] += hits
            bucket[name] += hits
    # Environment reads are legitimate at the platform boundary (own paths, e.g.
    # provenance and logging setup); the ratchet targets the algorithm layers.
    totals["os_environ"] = sum(counts["os_environ"] for cls, counts in by_class.items() if cls != "own")
    tests = sum(
        len(TEST_RE.findall(p.read_text(encoding="utf-8", errors="replace")))
        for p in tracked_python_files("tests")
    )
    test_files = len([p for p in tracked_python_files("tests") if p.name.startswith("test_")])
    metrics: dict[str, object] = {
        "python_lines": lines_total,
        "tests": tests,
        "test_files": test_files,
        **totals,
        "files_over_2000": len(long_files),
        "inprocess_worker_modules": len(worker_modules),
        "by_class": by_class,
        "allowlisted": {name: count for name, count in allowlisted.items() if count},
        "long_files": sorted(long_files),
        "worker_modules": sorted(worker_modules),
    }
    metrics["layer_exceptions"] = _layer_exceptions()
    coverage = ROOT / ".yuem" / "metrics" / "coverage-baseline.json"
    if coverage.exists():
        metrics["coverage_percent"] = json.loads(coverage.read_text(encoding="utf-8")).get("percent")
    return metrics


def _layer_exceptions() -> int:
    """Upstream cross-layer imports tolerated in .importlinter (ignore_imports)."""
    config = ROOT / ".importlinter"
    if not config.exists():
        return 0
    count, inside = 0, False
    for line in config.read_text(encoding="utf-8").splitlines():
        if line.strip().startswith("ignore_imports"):
            inside = True
            continue
        if inside:
            if line.startswith((" ", "\t")) and "->" in line:
                count += 1
            elif line.strip() and not line.startswith((" ", "\t", ";")):
                inside = False
    return count


def file_length_violations() -> list[str]:
    """Changed Python files that break the length rule of ADR 0003."""
    limit = ownership().max_file_lines
    base = upstream_ref()
    problems: list[str] = []
    for rel in changed_files(base):
        path = ROOT / rel
        if not rel.endswith(".py") or not path.exists():
            continue
        lines = len(path.read_text(encoding="utf-8", errors="replace").splitlines())
        if lines <= limit:
            continue
        before = file_at(base, rel)
        if before is None:
            problems.append(f"{rel}: new file has {lines} lines (limit {limit})")
        elif lines > len(before.splitlines()):
            problems.append(f"{rel}: grew from {len(before.splitlines())} to {lines} lines (limit {limit})")
    return problems


def _count(metrics: dict[str, object], name: str, default: int) -> int:
    value = metrics.get(name, default)
    return value if isinstance(value, int) else default


def compare(current: dict[str, object], baseline: dict[str, object]) -> list[str]:
    problems = []
    for name in DOWN_ONLY:
        cur = _count(current, name, 0)
        base = _count(baseline, name, cur)
        if cur > base:
            problems.append(f"{name}: {base} -> {cur} (may not rise)")
    for name in UP_ONLY:
        cur = _count(current, name, 0)
        base = _count(baseline, name, cur)
        if cur < base:
            problems.append(f"{name}: {base} -> {cur} (may not fall)")
    return problems


def _summary(current: dict[str, object], baseline: dict[str, object] | None) -> str:
    rows = []
    for name in ("python_lines", "test_files", *UP_ONLY, *DOWN_ONLY, "coverage_percent"):
        if name not in current:
            continue
        cur = current[name]
        base = None if baseline is None else baseline.get(name)
        delta = "" if base is None or cur == base else f"  ({base} -> {cur})"
        rows.append(f"  {name:<26}{cur}{delta}")
    allowlisted = current.get("allowlisted")
    if isinstance(allowlisted, dict) and allowlisted:
        listed = ", ".join(f"{k} {v}" for k, v in sorted(allowlisted.items()))
        rows.append(f"  {'(allowlisted, not counted)':<26}{listed}")
    return "\n".join(rows)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--update-baseline", action="store_true")
    parser.add_argument("--reason", default="")
    parser.add_argument("--allow-regression", action="store_true")
    args = parser.parse_args(argv)

    current = collect()
    baseline = json.loads(BASELINE.read_text(encoding="utf-8")) if BASELINE.exists() else None

    if args.update_baseline:
        if not args.reason.strip():
            parser.error("--update-baseline needs --reason")
        regressions = compare(current, baseline) if baseline else []
        if regressions and not args.allow_regression:
            print("Refusing to raise the baseline:\n  " + "\n  ".join(regressions), file=sys.stderr)
            return 1
        BASELINE.parent.mkdir(parents=True, exist_ok=True)
        BASELINE.write_text(json.dumps(current, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        with CHANGES.open("a", encoding="utf-8") as stream:
            if stream.tell() == 0:
                stream.write("# 棘轮基线变更记录\n\n")
            note = " (regression allowed)" if regressions else ""
            stream.write(f"- {date.today().isoformat()}{note}: {args.reason.strip()}\n")
        print(f"Baseline written to {BASELINE.relative_to(ROOT)}")
        return 0

    if args.json:
        print(json.dumps(current, indent=2, ensure_ascii=False))
    else:
        print(_summary(current, baseline))

    if args.check:
        if baseline is None:
            print("No baseline recorded; run --update-baseline first.", file=sys.stderr)
            return 1
        problems = compare(current, baseline) + file_length_violations()
        if problems:
            print("Ratchet failed:\n  " + "\n  ".join(problems), file=sys.stderr)
            return 1
        print("Ratchet OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
