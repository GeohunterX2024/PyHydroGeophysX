#!/usr/bin/env bash
# Build the YUEM development environment in .venv (docs/yuem/adr/0002).
#
#   tools/yuem/dev_env.sh            create or update .venv from uv.lock
#   tools/yuem/dev_env.sh --python 3.11
#
# Steps: uv sync against the lock file with the desktop, 3D, geophysics and
# hydrology extras and the dev group; then the macOS repairs the 2026-10-30
# install needed, applied only when the problem is actually present:
#   * pgcore's macOS wheel links @rpath/libblas.3.dylib but ships only
#     libopenblas.0.dylib, so pygimli cannot import - link the one to the other;
#   * an interpreter without a usable CA bundle cannot open HTTPS - point
#     SSL_CERT_FILE at certifi through a sitecustomize in the venv.
# Finally runs phgx-doctor when it is installed.
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"
PYVER="3.12"
while [ $# -gt 0 ]; do
  case "$1" in
    --python) PYVER="$2"; shift 2 ;;
    *) echo "unknown option: $1" >&2; exit 2 ;;
  esac
done

if ! command -v uv >/dev/null 2>&1; then
  echo "uv is not installed: brew install uv" >&2
  exit 2
fi

# The lock already pins the PyPI index; clear any mirror a user pip config sets.
unset PIP_INDEX_URL PIP_EXTRA_INDEX_URL UV_INDEX_URL UV_EXTRA_INDEX_URL || true

echo "==> uv sync (Python $PYVER)"
uv sync --locked --python "$PYVER" \
  --extra desktop --extra desktop-3d --extra geophysics --extra hydrology \
  --group dev

PY="$ROOT/.venv/bin/python"
SITE="$("$PY" -c 'import sysconfig; print(sysconfig.get_paths()["purelib"])')"

if [ "$(uname -s)" = "Darwin" ]; then
  DYLIBS="$SITE/pgcore/.dylibs"
  if [ -d "$DYLIBS" ] && [ ! -e "$DYLIBS/libblas.3.dylib" ] && [ -e "$DYLIBS/libopenblas.0.dylib" ]; then
    echo "==> repair: pgcore libblas.3.dylib -> libopenblas.0.dylib"
    ln -s libopenblas.0.dylib "$DYLIBS/libblas.3.dylib"
  fi
fi

if ! "$PY" - <<'EOF' >/dev/null 2>&1
import ssl, urllib.request
urllib.request.urlopen("https://pypi.org/simple/", timeout=10, context=ssl.create_default_context())
EOF
then
  echo "==> repair: SSL_CERT_FILE -> certifi (via sitecustomize in .venv)"
  cat > "$SITE/sitecustomize.py" <<'EOF'
# Written by tools/yuem/dev_env.sh: this interpreter has no usable CA bundle,
# so HTTPS falls back to certifi's unless the user set SSL_CERT_FILE.
import os

try:
    import certifi
except ImportError:
    pass
else:
    os.environ.setdefault("SSL_CERT_FILE", certifi.where())
EOF
fi

echo "==> import check"
"$PY" - <<'EOF'
import importlib
for name in ("PyHydroGeophysX", "numpy", "scipy", "pygimli", "simpeg", "PySide6", "pyvista", "h5py"):
    module = importlib.import_module(name)
    print(f"  {name:<16} {getattr(module, '__version__', 'ok')}")
EOF

if [ -x "$ROOT/.venv/bin/phgx-doctor" ]; then
  echo "==> phgx-doctor"
  "$ROOT/.venv/bin/phgx-doctor" || true
fi
echo "Development environment ready: source .venv/bin/activate"
