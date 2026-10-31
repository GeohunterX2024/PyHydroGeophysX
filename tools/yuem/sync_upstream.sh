#!/usr/bin/env bash
# Monthly upstream sync, steps 1-3 of the plan's section 2 (docs/yuem/adr/0001).
#
#   tools/yuem/sync_upstream.sh            # fetch, fast-forward `upstream`, list new commits by follow path
#   tools/yuem/sync_upstream.sh --branch   # also create yuem/sync-YYYYMM from yuem/main to cherry-pick onto
#
# Never pushes and never cherry-picks by itself: picking, the gates (fast, gui,
# golden, verification) and the merge after approval stay manual, and every
# sync is recorded in .yuem/SYNC_LOG.md.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

before=$(git rev-parse refs/heads/upstream)
git fetch upstream main
after=$(git rev-parse FETCH_HEAD)

if [ "$before" = "$after" ]; then
  echo "upstream unchanged at ${before:0:12}: nothing to sync."
  exit 0
fi
if ! git merge-base --is-ancestor "$before" "$after"; then
  echo "upstream/main was rewritten (${before:0:12} is not an ancestor of ${after:0:12}); stop and look." >&2
  exit 2
fi
git update-ref refs/heads/upstream "$after" "$before"
echo "upstream: ${before:0:12} -> ${after:0:12} ($(git rev-list --count "$before..$after") commits)"

PY=${PHGX_PYTHON:-.venv/bin/python}
follow=$("$PY" - <<'EOF'
import sys
sys.path.insert(0, "tools/yuem")
import subprocess
from _repo import ownership
own = ownership()
files = subprocess.run(["git", "ls-files", "PyHydroGeophysX"], capture_output=True, text=True, check=True).stdout.split()
tops = sorted({"/".join(f.split("/")[:2]) + ("/" if f.count("/") > 1 else "") for f in files})
print("\n".join(t for t in tops if own.classify(t if not t.endswith("/") else t + "x") == "follow"))
EOF
)
echo
echo "New commits by follow path (candidates to cherry-pick):"
while IFS= read -r path; do
  [ -n "$path" ] || continue
  log=$(git log --format='  %h %ad %s' --date=short "$before..$after" -- "$path")
  if [ -n "$log" ]; then
    echo "$path"
    echo "$log"
  fi
done <<< "$follow"
echo
echo "Touching own or frozen paths only (normally skipped):"
git log --format='  %h %s' "$before..$after" | head -50

if [ "${1:-}" = "--branch" ]; then
  branch="yuem/sync-$(date +%Y%m)"
  git branch "$branch" yuem/main
  echo
  echo "Created $branch from yuem/main. Cherry-pick with: git switch $branch && git cherry-pick -x <commit>"
fi
echo
echo "Record the range, the picked and skipped commits and the gate results in .yuem/SYNC_LOG.md."
