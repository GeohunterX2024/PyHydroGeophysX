#!/usr/bin/env bash
# Build the macOS arm64 desktop DMG of PyHydroGeophysX Studio (plan M0.8).
#
#   tools/yuem/build_macos_dmg.sh                 Full variant from the locked conda env
#   tools/yuem/build_macos_dmg.sh --variant light Light variant (same env, engines left out)
#   tools/yuem/build_macos_dmg.sh --python PATH   build with another interpreter
#
# Steps, each one checked:
#   1. the build environment: .conda/phgx-full from packaging/conda/conda-lock.yml,
#      with rustsolve put in place of SuiteSparse exactly as upstream's Full CI
#      does (packaging/rustsolve/apply.py install + check); created once, reused;
#   2. icons and PyInstaller (packaging/pyinstaller_studio.spec);
#   3. the .app is copied out of the source tree before signing: folders under
#      ~/Desktop and iCloud carry com.apple.FinderInfo / fileprovider xattrs that
#      make codesign fail ("resource fork, Finder information ... not allowed");
#   4. ad-hoc signature, verified with codesign --verify --deep --strict;
#   5. --self-test of the signed app;
#   6. a drag-to-Applications UDZO image with the licence files and a Chinese
#      install note; 7. the image is mounted and the app self-tested again;
#   8. SHA-256 of the image. The DMG lands in dist/.
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"
VARIANT="full"
PYTHON=""
while [ $# -gt 0 ]; do
  case "$1" in
    --variant) VARIANT="$2"; shift 2 ;;
    --python) PYTHON="$2"; shift 2 ;;
    *) echo "unknown option: $1" >&2; exit 2 ;;
  esac
done
[ "$(uname -s)" = "Darwin" ] || { echo "macOS only" >&2; exit 2; }
[ "$(uname -m)" = "arm64" ] || { echo "arm64 only (the lock pins osx-arm64)" >&2; exit 2; }

MAMBA="${PHGX_MAMBA:-$(command -v mamba || echo /opt/homebrew/Caskroom/miniforge/base/bin/mamba)}"
PREFIX="$ROOT/.conda/phgx-full"

if [ -z "$PYTHON" ]; then
  if [ ! -x "$PREFIX/bin/python" ]; then
    echo "==> 1. creating $PREFIX from packaging/conda/conda-lock.yml"
    command -v conda-lock >/dev/null || { echo "conda-lock missing: uv tool install conda-lock" >&2; exit 2; }
    [ -x "$MAMBA" ] || { echo "mamba missing: brew install --cask miniforge" >&2; exit 2; }
    CONDA_EXE="$MAMBA" conda-lock install --mamba -p "$PREFIX" packaging/conda/conda-lock.yml
    "$PREFIX/bin/python" packaging/rustsolve/apply.py install --prefix "$PREFIX" \
      --record "$ROOT/.conda/rustsolve-install.txt"
  fi
  "$PREFIX/bin/python" packaging/rustsolve/apply.py check --record "$ROOT/.conda/rustsolve-install.txt"
  PYTHON="$PREFIX/bin/python"
fi
BIN="$(dirname "$PYTHON")"

VERSION="$("$PYTHON" -c 'import tomllib; print(tomllib.load(open("pyproject.toml","rb"))["project"]["version"])')"
NAME="PyHydroGeophysX-Studio-${VERSION}-macos-arm64"
[ "$VARIANT" = "full" ] || NAME="${NAME}-${VARIANT}"
STAGE="$(mktemp -d /tmp/phgx-dmg.XXXXXX)"
trap 'rm -rf "$STAGE"' EXIT

echo "==> 2. icons and PyInstaller ($VARIANT, $VERSION)"
"$PYTHON" packaging/make_icons.py
PHGX_BUILD_VARIANT="$VARIANT" QT_QPA_PLATFORM=offscreen \
  "$BIN/pyinstaller" --noconfirm --clean packaging/pyinstaller_studio.spec

APP_SRC="$ROOT/dist/PyHydroGeophysX-Studio.app"
APP="$STAGE/PyHydroGeophysX-Studio.app"
echo "==> 3. copy out of the source tree and strip extended attributes"
ditto "$APP_SRC" "$APP"
xattr -cr "$APP"

echo "==> 4. ad-hoc signature"
codesign --force --deep --sign - --timestamp=none "$APP"
codesign --verify --deep --strict "$APP"

EXE="$APP/Contents/MacOS/PyHydroGeophysX-Studio"
echo "==> 5. self-test"
QT_QPA_PLATFORM=offscreen "$EXE" --self-test

echo "==> 6. disk image"
VOL="$STAGE/volume"
mkdir -p "$VOL"
ditto "$APP" "$VOL/PyHydroGeophysX-Studio.app"
ln -s /Applications "$VOL/Applications"
cp LICENSE "$VOL/LICENSE.txt"
cp THIRD_PARTY_NOTICES.md "$VOL/THIRD_PARTY_NOTICES.md"
cat > "$VOL/安装说明.txt" <<EOF
PyHydroGeophysX Desktop Studio ${VERSION}（${VARIANT}，macOS arm64）

安装：把 PyHydroGeophysX-Studio 拖到 Applications。

首次打开：本镜像为 ad-hoc 签名，未经 Apple 公证。若提示无法验证开发者，
按住 Control 点按图标选择「打开」，或在终端执行：
  xattr -cr /Applications/PyHydroGeophysX-Studio.app

仅支持 Apple Silicon。构建信息见 GitHub Release 附带的 sha256 与构建记录。
EOF
xattr -cr "$VOL"
DMG="$STAGE/$NAME.dmg"
hdiutil create -volname "PyHydroGeophysX Studio" -srcfolder "$VOL" -ov -format UDZO \
  -imagekey zlib-level=9 "$DMG" >/dev/null

echo "==> 7. mount and self-test again"
MOUNT="$(hdiutil attach -nobrowse -readonly "$DMG" | awk -F'\t' '/\/Volumes\//{print $NF}' | tail -1)"
QT_QPA_PLATFORM=offscreen "$MOUNT/PyHydroGeophysX-Studio.app/Contents/MacOS/PyHydroGeophysX-Studio" --self-test
hdiutil detach "$MOUNT" -quiet

echo "==> 8. checksum"
mkdir -p "$ROOT/dist"
cp -f "$DMG" "$ROOT/dist/$NAME.dmg"
(cd "$ROOT/dist" && shasum -a 256 "$NAME.dmg" | tee "$NAME.dmg.sha256")
echo "DMG: $ROOT/dist/$NAME.dmg"
