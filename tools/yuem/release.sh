#!/usr/bin/env bash
# Prepare a YUEM release (docs/yuem/release_checklist.md, plan M5.2).
#
#   tools/yuem/release.sh            check versions, run every gate tier, build the DMG with the
#                                    release audit, and print the GitHub release command
#   tools/yuem/release.sh --publish  ...and create the draft release (needs the maintainer's approval:
#                                    it pushes a tag and uploads to GitHub)
#
# The tag is yuem-<version without +yuem>.<N>, e.g. 0.5.0+yuem.1 -> yuem-0.5.0.1.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
PY=${PHGX_PYTHON:-.venv/bin/python}

version=$("$PY" -c 'import tomllib; print(tomllib.load(open("pyproject.toml","rb"))["project"]["version"])')
package=$("$PY" -c 'import re; print(re.search(r"__version__ = \"([^\"]+)\"", open("PyHydroGeophysX/__init__.py").read()).group(1))')
echo "==> 1. versions: pyproject $version, package $package"
[ "$version" = "$package" ] || { echo "pyproject.toml and PyHydroGeophysX/__init__.py disagree" >&2; exit 1; }
case "$version" in
  *+yuem.*) ;;
  *) echo "a YUEM release version is <upstream>+yuem.<N>, got $version" >&2; exit 1 ;;
esac
tag="yuem-${version%%+*}.${version##*+yuem.}"
grep -q "$version" CHANGELOG-YUEM.md || { echo "CHANGELOG-YUEM.md has no entry for $version" >&2; exit 1; }
[ -z "$(git status --porcelain)" ] || { echo "the working tree has uncommitted changes" >&2; exit 1; }

echo "==> 2. every gate tier"
tools/yuem/gates.sh --full

echo "==> 3. translations and verification report"
"$PY" tools/yuem/i18n.py check
"$PY" tools/yuem/verification_report.py --check

echo "==> 4. macOS DMG with the release audit"
PHGX_RELEASE_AUDIT=1 PHGX_RELEASE_STRICT=1 tools/yuem/build_macos_dmg.sh
dmg="dist/PyHydroGeophysX-Studio-${version}-macos-arm64.dmg"
[ -f "$dmg" ] && [ -f "$dmg.sha256" ] || { echo "the DMG or its checksum is missing" >&2; exit 1; }

notes="dist/RELEASE_NOTES-${tag}.md"
{
  echo "# PyHydroGeophysX YUEM ${version}"
  echo
  echo "Changes: see CHANGELOG-YUEM.md. Signing: $([ -n "${PHGX_SIGN_IDENTITY:-}" ] && echo "Developer ID${PHGX_NOTARY_PROFILE:+, notarized}" || echo "ad-hoc (see the install note in the image)")."
  echo
  echo "SHA-256:"
  echo '```'
  cat "$dmg.sha256"
  echo '```'
} > "$notes"

command=(gh release create "$tag" "$dmg" "$dmg.sha256" --repo GeohunterX2024/PyHydroGeophysX
         --target yuem/main --draft --title "PyHydroGeophysX YUEM ${version}" --notes-file "$notes")
echo "==> 5. GitHub release"
if [ "${1:-}" = "--publish" ]; then
  "${command[@]}"
else
  printf 'Ready. To publish a draft (after approval):\n  '
  printf '%q ' "${command[@]}"
  echo
fi
