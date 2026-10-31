"""Check that local edits to upstream-tracked paths are logged in .yuem/PATCHES.md.

    python tools/yuem/patch_ledger.py --check            # ledger vs. diff from upstream
    python tools/yuem/patch_ledger.py --check --changelog-base yuem/main
    python tools/yuem/patch_ledger.py --list             # changed files with their class

Rules (ADR 0001, section 5):

* ``frozen`` paths may not differ from upstream at all;
* every ``follow`` or ``shared`` path that differs must appear in an active
  ledger entry;
* an active entry whose files no longer differ from upstream is stale and must
  be removed (or marked as reverted).

With ``--changelog-base`` the check also requires ``CHANGELOG-YUEM.md`` to change
whenever the branch changes anything relative to that base.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _repo import ROOT, changed_files, git, ownership, ref_exists, upstream_ref

LEDGER = ROOT / ".yuem" / "PATCHES.md"
CHANGELOG = "CHANGELOG-YUEM.md"
ACTIVE = "生效"
ENTRY_RE = re.compile(r"^\|\s*(P-\d{4})\s*\|(.*)$")


@dataclass(frozen=True)
class Entry:
    ident: str
    files: tuple[str, ...]
    status: str


def read_ledger(text: str) -> list[Entry]:
    entries = []
    for line in text.splitlines():
        match = ENTRY_RE.match(line.strip())
        if not match:
            continue
        cells = [c.strip() for c in match.group(2).split("|")]
        # cells: files, summary, reason, upstreamable, pr, status, ""
        files_cell, status = cells[0], cells[5] if len(cells) > 5 else ""
        files = tuple(f.strip().strip("`") for f in re.split(r"<br>|,", files_cell) if f.strip())
        entries.append(Entry(match.group(1), files, status))
    return entries


def check(changelog_base: str | None) -> list[str]:
    own = ownership()
    base = upstream_ref()
    entries = read_ledger(LEDGER.read_text(encoding="utf-8"))
    logged = {f for e in entries if e.status == ACTIVE for f in e.files}
    changed = changed_files(base)
    problems: list[str] = []

    ids = [e.ident for e in entries]
    for dup in sorted({i for i in ids if ids.count(i) > 1}):
        problems.append(f"duplicate ledger id {dup}")

    for rel in changed:
        cls = own.classify(rel)
        if cls == "frozen":
            problems.append(f"{rel}: frozen path differs from upstream")
        elif cls in ("follow", "shared") and rel not in logged:
            problems.append(f"{rel}: {cls} path changed but not logged in .yuem/PATCHES.md")

    changed_set = set(changed)
    for entry in entries:
        if entry.status != ACTIVE:
            continue
        stale = [f for f in entry.files if f not in changed_set]
        if stale:
            problems.append(f"{entry.ident}: logged files no longer differ from upstream: {', '.join(stale)}")

    if changelog_base and ref_exists(changelog_base):
        head = git("rev-parse", "HEAD")
        if git("rev-parse", changelog_base) != head:
            branch_changes = changed_files(changelog_base)
            if branch_changes and CHANGELOG not in branch_changes:
                problems.append(f"{CHANGELOG} has no entry for the changes since {changelog_base}")
    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--changelog-base", default=None)
    args = parser.parse_args(argv)

    if args.list:
        own = ownership()
        for rel in changed_files(upstream_ref()):
            print(f"{own.classify(rel):<7} {rel}")
    if args.check:
        problems = check(args.changelog_base)
        if problems:
            print("Patch ledger check failed:\n  " + "\n  ".join(problems), file=sys.stderr)
            return 1
        print("Patch ledger OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
