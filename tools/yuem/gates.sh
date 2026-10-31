#!/usr/bin/env bash
# YUEM quality gates (docs/yuem/adr/0003-quality-gates.md).
#
#   tools/yuem/gates.sh              fast tier: every PR, and pre-commit
#   tools/yuem/gates.sh --full       fast tier + gui, slow, numerical and golden tests
#   tools/yuem/gates.sh --no-tests   static checks only (pre-commit uses this)
#
# Uses the development environment in .venv (tools/yuem/dev_env.sh); set
# PHGX_PYTHON to use another interpreter. Every step runs even after a failure,
# and the script exits non-zero if any step failed.
set -uo pipefail

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"
PY="${PHGX_PYTHON:-$ROOT/.venv/bin/python}"
BIN="$(dirname "$PY")"
FULL=0
TESTS=1
for arg in "$@"; do
  case "$arg" in
    --full) FULL=1 ;;
    --no-tests) TESTS=0 ;;
    *) echo "unknown option: $arg" >&2; exit 2 ;;
  esac
done

export MPLBACKEND=Agg
export QT_QPA_PLATFORM=offscreen

if [ ! -x "$PY" ]; then
  echo "No interpreter at $PY; run tools/yuem/dev_env.sh first." >&2
  exit 2
fi

FAILED=""
step() {
  local name="$1"; shift
  printf '\n==> %s\n' "$name"
  if "$@"; then
    printf '    ok: %s\n' "$name"
  else
    printf '    FAILED: %s\n' "$name"
    FAILED="$FAILED\n  - $name"
  fi
}

STRICT="$("$PY" tools/yuem/quality_paths.py strict | tr '\n' ' ')"
TYPED="$("$PY" tools/yuem/quality_paths.py typed | tr '\n' ' ')"
RULES="$("$PY" tools/yuem/quality_paths.py rules)"

# shellcheck disable=SC2086  # the path lists are intentionally word-split
step "ruff (baseline rules, whole tree)" "$BIN/ruff" check .
if [ -n "$STRICT" ]; then
  step "ruff (strict rules, strict paths)" "$BIN/ruff" check --select "$RULES" $STRICT
  step "ruff format (strict paths)" "$BIN/ruff" format --check $STRICT
fi
if [ -n "$TYPED" ]; then
  step "mypy --strict (typed paths)" "$BIN/mypy" --strict $TYPED
fi
if [ -f .importlinter ]; then
  step "import-linter (layer contracts)" "$BIN/lint-imports" --config .importlinter
fi
step "ratchet metrics" "$PY" tools/yuem/metrics.py --check
CHANGELOG_BASE="yuem/main"
if [ "$(git rev-parse --abbrev-ref HEAD)" = "yuem/main" ]; then
  CHANGELOG_BASE=""
fi
if [ -n "$CHANGELOG_BASE" ]; then
  step "patch ledger + changelog" "$PY" tools/yuem/patch_ledger.py --check --changelog-base "$CHANGELOG_BASE"
else
  step "patch ledger" "$PY" tools/yuem/patch_ledger.py --check
fi

if [ "$TESTS" = 1 ]; then
  step "pytest fast tier" "$PY" -m pytest -q -p no:cacheprovider \
    -m "not slow and not golden and not numerical and not gui and not network and not packaging"
  if [ "$FULL" = 1 ]; then
    step "pytest gui tier" "$PY" -m pytest -q -p no:cacheprovider -m "gui and not slow"
    step "pytest slow tier" "$PY" -m pytest -q -p no:cacheprovider -m "slow and not golden and not numerical"
    step "pytest numerical + golden tiers" "$PY" -m pytest -q -p no:cacheprovider -m "numerical or golden"
  fi
fi

if [ -n "$FAILED" ]; then
  printf '\nGates FAILED:%b\n' "$FAILED"
  exit 1
fi
printf '\nAll gates passed.\n'
