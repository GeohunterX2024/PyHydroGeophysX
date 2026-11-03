#!/usr/bin/env bash
# Build the macOS arm64 desktop DMG of PyHydroGeophysX Studio (plan M0.8).
#
#   tools/yuem/build_macos_dmg.sh                 Full variant from the locked conda env
#   tools/yuem/build_macos_dmg.sh --variant light Light variant (same env, engines left out)
#   tools/yuem/build_macos_dmg.sh --python PATH   build with another interpreter
#
# PHGX_PLUGIN_WHEELS (wheel files separated by ":") puts Studio plugins into the app: they are
# installed without dependencies into a build folder the spec collects them from, and the
# frozen Studio must list their workflows before the image is made.
#
# Steps, each one checked:
#   1. the build environment: .conda/phgx-full from packaging/conda/conda-lock.yml,
#      with rustsolve put in place of SuiteSparse exactly as upstream's Full CI
#      does (packaging/rustsolve/apply.py install + check); created once, reused;
#   2. icons and PyInstaller (packaging/pyinstaller_studio.spec);
#   3. the .app is copied out of the source tree before signing: folders under
#      ~/Desktop and iCloud carry com.apple.FinderInfo / fileprovider xattrs that
#      make codesign fail ("resource fork, Finder information ... not allowed");
#   4. signature, verified with codesign --verify --deep --strict: Developer ID
#      with hardened runtime when PHGX_SIGN_IDENTITY names one (e.g.
#      "Developer ID Application: Name (TEAMID)"), ad-hoc otherwise;
#   5. --self-test of the signed app;
#   6. a drag-to-Applications UDZO image with the licence files and a Chinese
#      install note; 7. the image is mounted and the app self-tested again;
#   8. with PHGX_SIGN_IDENTITY the image is signed, and with PHGX_NOTARY_PROFILE
#      (a notarytool keychain profile) notarized, stapled and checked by spctl;
#   9. SHA-256 of the image. The DMG lands in dist/.
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

PLUGIN_SITE=""
PLUGIN_WORKFLOWS=()
if [ -n "${PHGX_PLUGIN_WHEELS:-}" ]; then
  PLUGIN_SITE="$STAGE/plugins"
  IFS=":" read -r -a WHEELS <<< "$PHGX_PLUGIN_WHEELS"
  echo "==> 1b. plugins: ${WHEELS[*]}"
  for wheel in "${WHEELS[@]}"; do
    [ -f "$wheel" ] || { echo "plugin wheel not found: $wheel" >&2; exit 2; }
  done
  "$PYTHON" -m pip install --quiet --no-deps --no-compile --target "$PLUGIN_SITE" "${WHEELS[@]}"
  # The workflows each plugin registers, which the frozen Studio must list (step 5).
  while IFS= read -r workflow; do PLUGIN_WORKFLOWS+=("$workflow"); done < <(
    PYTHONPATH="$PLUGIN_SITE:$ROOT" QT_QPA_PLATFORM=offscreen "$PYTHON" -c '
from PyHydroGeophysX.plugins import load_entry_points, load_failures
from PyHydroGeophysX.workflows.registry import list_workflows
load_entry_points()
assert not load_failures(), load_failures()
for w in list_workflows():
    if not w.handler_path.startswith("PyHydroGeophysX."):
        print(w.workflow_id)')
  [ "${#PLUGIN_WORKFLOWS[@]}" -gt 0 ] || { echo "the plugin wheels register no workflow" >&2; exit 2; }
fi

echo "==> 2. icons and PyInstaller ($VARIANT, $VERSION)"
"$PYTHON" packaging/make_icons.py
PHGX_BUILD_VARIANT="$VARIANT" PHGX_PLUGIN_SITE="$PLUGIN_SITE" QT_QPA_PLATFORM=offscreen \
  "$BIN/pyinstaller" --noconfirm --clean packaging/pyinstaller_studio.spec

APP_SRC="$ROOT/dist/PyHydroGeophysX-Studio.app"
APP="$STAGE/PyHydroGeophysX-Studio.app"
echo "==> 3. copy out of the source tree and strip extended attributes"
ditto "$APP_SRC" "$APP"
xattr -cr "$APP"

IDENTITY="${PHGX_SIGN_IDENTITY:-}"
if [ -n "$IDENTITY" ]; then
  echo "==> 4. Developer ID signature, hardened runtime: $IDENTITY"
  ENTITLEMENTS="$ROOT/packaging/macos/entitlements.plist"
  sign() { codesign --force --options runtime --timestamp --entitlements "$ENTITLEMENTS" --sign "$IDENTITY" "$1"; }
  # Inside out: every Mach-O file first, then the bundle that seals them.
  while IFS= read -r -d '' file; do
    if file -b "$file" | grep -q "Mach-O"; then sign "$file"; fi
  done < <(find "$APP/Contents" -type f -print0)
  sign "$APP"
else
  echo "==> 4. ad-hoc signature (set PHGX_SIGN_IDENTITY for Developer ID)"
  codesign --force --deep --sign - --timestamp=none "$APP"
fi
codesign --verify --deep --strict "$APP"

EXE="$APP/Contents/MacOS/PyHydroGeophysX-Studio"
echo "==> 5. self-test"
QT_QPA_PLATFORM=offscreen "$EXE" --self-test
# The workflow processes the Studio starts run in the frozen app too (findings F-23), and see
# every bundled plugin's workflows.
LISTED="$(QT_QPA_PLATFORM=offscreen "$EXE" -m PyHydroGeophysX.workflows.cli list | cut -f1)"
for workflow in ${PLUGIN_WORKFLOWS[@]+"${PLUGIN_WORKFLOWS[@]}"}; do
  grep -qx "$workflow" <<< "$LISTED" || { echo "the frozen Studio does not list $workflow" >&2; exit 1; }
done
echo "    workflow processes run; $(wc -l <<< "$LISTED" | tr -d ' ') workflows listed"

if [ -n "$IDENTITY" ] && [ -n "${PHGX_NOTARY_PROFILE:-}" ]; then
  OPEN_NOTE="首次打开：本镜像经 Developer ID 签名并已通过 Apple 公证，双击即可打开。"
else
  OPEN_NOTE="首次打开：本镜像为 ad-hoc 签名，未经 Apple 公证。若提示无法验证开发者，
按住 Control 点按图标选择「打开」，或在终端执行：
  xattr -cr /Applications/PyHydroGeophysX-Studio.app"
fi

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

${OPEN_NOTE}

仅支持 Apple Silicon。构建信息见 GitHub Release 附带的 sha256 与构建记录。
EOF
if [ "${PHGX_RELEASE_AUDIT:-0}" = "1" ]; then
  # As upstream's release workflow does: BUILD_INFO.txt, SOURCE_CODE.md and
  # LICENSES/ at the image's root, every bundled file traced to its source.
  # Needs network (Qt licence sources); PHGX_RELEASE_STRICT=1 stops on a failed check.
  echo "    release audit (packaging/release_audit.py stage)"
  audit_args=(--conda-prefix "$ROOT/.conda/phgx-full")
  if [ "$VARIANT" = "full" ]; then audit_args+=(--rustsolve); fi
  if [ "${PHGX_RELEASE_STRICT:-0}" = "1" ]; then audit_args+=(--strict); fi
  mkdir -p "$ROOT/dist"
  "$PYTHON" packaging/release_audit.py stage --os macos --variant "$VARIANT" \
    --bundle "$VOL/PyHydroGeophysX-Studio.app" --stage "$VOL" --workpath build/pyinstaller_studio \
    "${audit_args[@]}" --commit "$(git rev-parse HEAD)" --report "$ROOT/dist/$NAME.audit.md"
fi
xattr -cr "$VOL"
DMG="$STAGE/$NAME.dmg"
hdiutil create -volname "PyHydroGeophysX Studio" -srcfolder "$VOL" -ov -format UDZO \
  -imagekey zlib-level=9 "$DMG" >/dev/null

echo "==> 7. mount and self-test again"
MOUNT="$(hdiutil attach -nobrowse -readonly "$DMG" | awk -F'\t' '/\/Volumes\//{print $NF}' | tail -1)"
QT_QPA_PLATFORM=offscreen "$MOUNT/PyHydroGeophysX-Studio.app/Contents/MacOS/PyHydroGeophysX-Studio" --self-test
hdiutil detach "$MOUNT" -quiet

if [ -n "$IDENTITY" ]; then
  echo "==> 8. sign the image"
  codesign --force --timestamp --sign "$IDENTITY" "$DMG"
  if [ -n "${PHGX_NOTARY_PROFILE:-}" ]; then
    echo "    notarize (notarytool profile $PHGX_NOTARY_PROFILE) and staple"
    xcrun notarytool submit "$DMG" --keychain-profile "$PHGX_NOTARY_PROFILE" --wait
    xcrun stapler staple "$DMG"
    spctl --assess --type open --context context:primary-signature --verbose "$DMG"
  fi
fi

echo "==> 9. checksum"
mkdir -p "$ROOT/dist"
cp -f "$DMG" "$ROOT/dist/$NAME.dmg"
(cd "$ROOT/dist" && shasum -a 256 "$NAME.dmg" | tee "$NAME.dmg.sha256")
echo "DMG: $ROOT/dist/$NAME.dmg"
