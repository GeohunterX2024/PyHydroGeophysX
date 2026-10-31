#!/usr/bin/env bash
# Build the YUEM development environment in .venv (docs/yuem/adr/0002).
#
#   tools/yuem/dev_env.sh            create or update .venv from uv.lock
#   tools/yuem/dev_env.sh --python 3.11
#
# Steps: uv sync against the lock file with the desktop, 3D, geophysics and
# hydrology extras and the dev group; then the macOS repairs real installs
# needed, applied only when the problem is actually present:
#   * files flagged hidden are skipped: .pth files by Python >= 3.12, so the
#     editable install imports only from the repository root, and Qt's
#     platform plugins by Qt. iCloud's Desktop & Documents sync keeps setting
#     the flag inside dot-directories, so such checkouts get their venv outside
#     iCloud (see below); any flag left is cleared;
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

# iCloud Drive's "Desktop & Documents" sync keeps setting the hidden flag on
# files inside dot-directories, within seconds of it being cleared, and Python
# then skips the venv's .pth files and Qt its plugins. A checkout under those
# folders gets its environment outside them; .venv is a link to it.
if [ "$(uname -s)" = "Darwin" ] && [ -z "${UV_PROJECT_ENVIRONMENT:-}" ]; then
  case "$ROOT/" in
    "$HOME/Desktop/"*|"$HOME/Documents/"*)
      UV_PROJECT_ENVIRONMENT="$HOME/Library/Caches/phgx-venvs/$(basename "$ROOT")-$(printf '%s' "$ROOT" | shasum | cut -c1-8)"
      export UV_PROJECT_ENVIRONMENT
      if [ -d "$ROOT/.venv" ] && [ ! -L "$ROOT/.venv" ]; then
        echo "==> moving the environment out of the iCloud-synced folder"
        rm -rf "$ROOT/.venv"
      fi
      mkdir -p "$(dirname "$UV_PROJECT_ENVIRONMENT")"
      ln -sfn "$UV_PROJECT_ENVIRONMENT" "$ROOT/.venv"
      echo "==> environment: $UV_PROJECT_ENVIRONMENT (linked as .venv)"
      ;;
  esac
fi

echo "==> uv sync (Python $PYVER)"
uv sync --locked --python "$PYVER" \
  --extra desktop --extra desktop-3d --extra geophysics --extra hydrology \
  --group dev

if [ -x "$ROOT/.venv/Scripts/python.exe" ]; then
  PY="$ROOT/.venv/Scripts/python.exe"   # Windows venv layout
else
  PY="$ROOT/.venv/bin/python"
fi
SITE="$("$PY" -c 'import sysconfig; print(sysconfig.get_paths()["purelib"])')"

if [ "$(uname -s)" = "Darwin" ]; then
  # Python >= 3.12 skips .pth files flagged UF_HIDDEN (the editable install,
  # coverage's hook) and Qt skips hidden platform plugins: nothing may be hidden.
  if [ -n "$(find "$ROOT/.venv" -flags +hidden -print -quit 2>/dev/null)" ]; then
    echo "==> repair: clear the hidden flag on files in .venv"
    chflags -R nohidden "$ROOT/.venv"
  fi
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

if "$PY" -c "import PyHydroGeophysX.doctor" >/dev/null 2>&1; then
  echo "==> phgx-doctor"
  "$PY" -m PyHydroGeophysX.doctor || true
fi
echo "Development environment ready: source .venv/bin/activate"
