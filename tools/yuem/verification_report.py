"""Run the numerical verification set and write docs/yuem/verification.md (plan M1.3).

    python tools/yuem/verification_report.py           # run, write the report
    python tools/yuem/verification_report.py --check   # run, fail on any failed case, write nothing

The report lists every case with its reference, error measure, measured value
and tolerance, plus the environment it ran in, so a release can cite it.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "docs" / "yuem" / "verification.md"


def run_cases() -> tuple[int, list[dict[str, Any]]]:
    with tempfile.TemporaryDirectory() as scratch:
        target = Path(scratch) / "records.json"
        env = {**os.environ, "PHGX_VERIFICATION_JSON": str(target), "MPLBACKEND": "Agg"}
        done = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                "-q",
                "-p",
                "no:cacheprovider",
                "-m",
                "numerical",
                "tests/yuem/verification",
            ],
            cwd=ROOT,
            env=env,
            check=False,
        )
        records = json.loads(target.read_text(encoding="utf-8")) if target.exists() else []
    return done.returncode, records


def _environment() -> str:
    sys.path.insert(0, str(ROOT))
    from PyHydroGeophysX._internal.provenance import collect_environment

    env = collect_environment()
    packages = env["packages"]
    names = ("numpy", "scipy", "pygimli", "pgcore", "simpeg", "empymod")
    listed = ", ".join(f"{name} {packages[name]}" for name in names if name in packages)
    blas = ", ".join(
        f"{pool['internal_api']} {pool['version']}" for pool in env["blas"] if pool.get("user_api") == "blas"
    )
    return (
        f"PyHydroGeophysX {env['phgx_version']} ({env['git'] or 'no git'}); "
        f"Python {env['python']['version']} on {env['platform']['system']} {env['platform']['machine']}; "
        f"{listed}; BLAS {blas or 'unknown'}"
    )


def render(records: list[dict[str, Any]]) -> str:
    passed = sum(1 for r in records if r["passed"])
    lines = [
        "# 数值验证报告",
        "",
        "由 `python tools/yuem/verification_report.py` 生成，请勿手工编辑。"
        "用例在 `tests/yuem/verification/`，标记 `numerical`。",
        "",
        f"- 生成日期：{date.today().isoformat()}",
        f"- 环境：{_environment()}",
        f"- 结果：{passed}/{len(records)} 通过",
        "",
        "| 编号 | 方法 | 用例 | 被测实现 | 参考解 | 误差指标 | 实测 | 容差 | 结论 |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for r in sorted(records, key=lambda item: item["case"]):
        status = "通过" if r["passed"] else "**未通过**"
        lines.append(
            f"| {r['case']} | {r['method']} | {r['title']} | {r['engine']} | {r['reference']} | "
            f"{r['metric']} | {r['value']:.2e} | {r['tolerance']:.0e} | {status} |"
        )
    notes = [r for r in records if r.get("note")]
    if notes:
        lines += ["", "## 说明", ""]
        lines += [f"- **{r['case']}**：{r['note']}" for r in sorted(notes, key=lambda item: item["case"])]
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--check", action="store_true", help="run and fail on failures; do not write")
    args = parser.parse_args(argv)
    code, records = run_cases()
    if not records:
        print("No verification records were produced.", file=sys.stderr)
        return 1
    failed = [r["case"] for r in records if not r["passed"]]
    if not args.check:
        REPORT.parent.mkdir(parents=True, exist_ok=True)
        REPORT.write_text(render(records), encoding="utf-8")
        print(f"Wrote {REPORT.relative_to(ROOT)} ({len(records)} cases)")
    if failed or code != 0:
        print(f"Failed cases: {', '.join(failed) or '(pytest error)'}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
