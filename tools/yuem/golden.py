"""Record or inspect the golden regression outputs (plan M1.4).

    python tools/yuem/golden.py --list
    python tools/yuem/golden.py --update --reason "why the results should change"
    python tools/yuem/golden.py --update --case ert_single --reason "..."

``--update`` runs the cases, writes ``tests/yuem/golden/data/<case>.npz`` and a
``<case>.json`` with the environment and the keys, and appends the reason and
the largest change per case to ``tests/yuem/golden/CHANGES.md``. A golden
output may only change with a reason; ``test_golden.py`` compares against it.
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from datetime import date
from pathlib import Path
from typing import Any, cast

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from PyHydroGeophysX._internal.provenance import collect_environment  # noqa: E402
from tests.yuem.golden.cases import BY_NAME, CASES, DATA, compute  # noqa: E402
from tests.yuem.smoke.recipes import Workspace  # noqa: E402

CHANGES = ROOT / "tests" / "yuem" / "golden" / "CHANGES.md"


def _largest_change(old: dict[str, np.ndarray], new: dict[str, np.ndarray]) -> str:
    if not old:
        return "new"
    if set(old) != set(new):
        added, removed = sorted(set(new) - set(old)), sorted(set(old) - set(new))
        return f"keys changed (+{added}, -{removed})"
    worst, where = 0.0, ""
    for key, value in new.items():
        before = old[key]
        if before.shape != value.shape:
            return f"{key}: shape {before.shape} -> {value.shape}"
        if value.size:
            change = float(np.nanmax(np.abs(value - before) / np.maximum(np.abs(before), 1e-300)))
            if change > worst:
                worst, where = change, key
    return f"max relative change {worst:.2e}" + (f" ({where})" if where else "")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--update", action="store_true")
    parser.add_argument("--case", action="append", default=[])
    parser.add_argument("--reason", default="")
    args = parser.parse_args(argv)

    if args.list:
        for case in CASES:
            state = "recorded" if (DATA / f"{case.name}.npz").exists() else "MISSING"
            print(f"{case.name:<20}{case.workflow_id:<28}rtol={case.rtol:g}  {state}")
        return 0
    if not args.update:
        parser.print_help()
        return 2
    if not args.reason.strip():
        parser.error("--update needs --reason")
    unknown = [name for name in args.case if name not in BY_NAME]
    if unknown:
        parser.error(f"unknown case(s): {', '.join(unknown)}")
    selected = [BY_NAME[name] for name in args.case] if args.case else list(CASES)

    DATA.mkdir(parents=True, exist_ok=True)
    environment = collect_environment()
    lines = []
    with tempfile.TemporaryDirectory() as scratch:
        root = Path(scratch) / "golden workspace"
        root.mkdir()
        workspace = Workspace(root, ROOT / "examples" / "data")
        for case in selected:
            arrays = compute(case, workspace)
            target = DATA / f"{case.name}.npz"
            old: dict[str, np.ndarray] = {}
            if target.exists():
                with np.load(target) as archive:
                    old = {key: archive[key] for key in archive.files}
            change = _largest_change(old, arrays)
            np.savez_compressed(target, **cast("dict[str, Any]", arrays))
            meta = {
                "case": case.name,
                "workflow_id": case.workflow_id,
                "rtol": case.rtol,
                "atol": case.atol,
                "note": case.note,
                "keys": sorted(arrays),
                "environment": environment,
            }
            (DATA / f"{case.name}.json").write_text(
                json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
            )
            lines.append(f"  - `{case.name}`：{change}")
            print(f"{case.name}: {change}")
    with CHANGES.open("a", encoding="utf-8") as stream:
        if stream.tell() == 0:
            stream.write("# 金标准变更记录\n\n每次更新金标准都在此追加：日期、原因、各用例的最大变化。\n\n")
        stream.write(
            f"- {date.today().isoformat()}（PyHydroGeophysX {environment['phgx_version']}）：{args.reason}\n"
        )
        stream.write("\n".join(lines) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
