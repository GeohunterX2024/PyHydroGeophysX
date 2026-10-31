"""Print the quality path lists of .yuem/ownership.toml for shell scripts.

python tools/yuem/quality_paths.py strict     # existing strict paths, one per line
python tools/yuem/quality_paths.py typed      # existing mypy --strict paths
python tools/yuem/quality_paths.py rules      # strict ruff rules, comma separated
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _repo import existing, ownership


def main(argv: list[str]) -> int:
    if len(argv) != 1 or argv[0] not in ("strict", "typed", "rules"):
        print(__doc__, file=sys.stderr)
        return 2
    own = ownership()
    if argv[0] == "rules":
        print(",".join(own.strict_rules))
    else:
        paths = own.strict if argv[0] == "strict" else own.typed
        print("\n".join(existing(paths)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
