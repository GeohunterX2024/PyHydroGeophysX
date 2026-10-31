"""Environment self-check for PyHydroGeophysX (``phgx-doctor``, plan M1.6).

    phgx-doctor                     check this installation
    phgx-doctor --project DIR       also check a project folder's space and permissions
    phgx-doctor --network           also open an HTTPS connection to PyPI
    phgx-doctor --json              machine-readable report

Exit code: 0 all checks passed, 1 warnings only, 2 at least one error. The
Studio's Help > Environment Check runs the same checks.

The checks target the failures a real install has hit: pyGIMLi's compiled core
missing ``libblas.3.dylib`` on macOS, an interpreter without a CA bundle, no
Qt platform plugin, no OpenGL for VTK, no CJK font for Chinese labels, and a
project folder on a full or read-only disk.
"""

from __future__ import annotations

import argparse
import importlib
import importlib.util
import json
import os
import platform
import shutil
import ssl
import sys
import tempfile
from collections.abc import Callable, Sequence
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Literal

Status = Literal["ok", "warn", "error"]

#: Families matplotlib and Qt can use for Chinese text, in order of preference.
CJK_FONTS: tuple[str, ...] = (
    "PingFang SC",
    "Hiragino Sans GB",
    "Songti SC",
    "STHeiti",
    "Microsoft YaHei",
    "SimHei",
    "SimSun",
    "Noto Sans CJK SC",
    "Source Han Sans SC",
    "WenQuanYi Micro Hei",
)
#: Optional engines: (import name, what it enables, install hint).
OPTIONAL_ENGINES: tuple[tuple[str, str, str], ...] = (
    ("pygimli", "ERT/SRT engines and meshes", "uv sync --extra geophysics (or conda -c gimli pygimli)"),
    ("simpeg", "EM, MT and potential-field inversions", 'pip install "pyhydrogeophysx[geophysics]"'),
    ("pyvista", "3D viewers", 'pip install "pyhydrogeophysx[desktop-3d]"'),
    ("h5py", "HDF5 project datasets and hydrology outputs", 'pip install "pyhydrogeophysx[hydrology]"'),
    ("resipy", "extra ERT instrument formats (GPL-3.0)", "pip install resipy"),
    ("adtlert", "GPU ERT (CUDA only)", 'pip install "pyhydrogeophysx[adtlert]"'),
)
FREE_SPACE_WARN = 5 * 1024**3
FREE_SPACE_ERROR = 512 * 1024**2


@dataclass(frozen=True)
class Check:
    name: str
    status: Status
    detail: str
    hint: str = ""


def _check_python() -> Check:
    version = platform.python_version()
    detail = f"{version} ({platform.python_implementation()}, {platform.machine()}) at {sys.executable}"
    if sys.version_info[:2] not in ((3, 11), (3, 12), (3, 13)):
        return Check("Python", "warn", detail, "the fork is tested on 3.11-3.13")
    return Check("Python", "ok", detail)


def _check_package() -> Check:
    try:
        import PyHydroGeophysX
    except Exception as exc:  # noqa: BLE001 - any import failure is the finding
        return Check("PyHydroGeophysX", "error", f"import failed: {exc}", "reinstall the package")
    return Check(
        "PyHydroGeophysX", "ok", f"{PyHydroGeophysX.__version__} at {Path(PyHydroGeophysX.__file__).parent}"
    )


def _check_core_libraries() -> Check:
    missing = []
    for name in ("numpy", "scipy", "matplotlib", "pandas"):
        if importlib.util.find_spec(name) is None:
            missing.append(name)
    if missing:
        return Check(
            "Core libraries", "error", f"missing: {', '.join(missing)}", "pip install PyHydroGeophysX"
        )
    import numpy
    import scipy

    return Check("Core libraries", "ok", f"numpy {numpy.__version__}, scipy {scipy.__version__}")


def _check_pygimli_core() -> Check:
    if importlib.util.find_spec("pygimli") is None:
        return Check("pyGIMLi core", "warn", "pygimli not installed", OPTIONAL_ENGINES[0][2])
    spec = importlib.util.find_spec("pgcore")
    if sys.platform == "darwin" and spec is not None and spec.submodule_search_locations:
        dylibs = Path(next(iter(spec.submodule_search_locations))) / ".dylibs"
        if (
            dylibs.is_dir()
            and (dylibs / "libopenblas.0.dylib").exists()
            and not (dylibs / "libblas.3.dylib").exists()
        ):
            return Check(
                "pyGIMLi core",
                "error",
                f"{dylibs} lacks libblas.3.dylib that libumfpack links against",
                f"ln -s libopenblas.0.dylib {dylibs / 'libblas.3.dylib'}  (tools/yuem/dev_env.sh does this)",
            )
    try:
        core = importlib.import_module("pgcore")
        importlib.import_module("pygimli")
    except Exception as exc:  # noqa: BLE001 - any import failure is the finding
        return Check("pyGIMLi core", "error", f"import failed: {exc}", OPTIONAL_ENGINES[0][2])
    from importlib import metadata

    version = metadata.version("pygimli")
    location = Path(str(getattr(core, "__file__", ""))).parent
    return Check("pyGIMLi core", "ok", f"pygimli {version}, pgcore at {location}")


def _check_hidden_files() -> Check:
    """macOS: files flagged hidden are skipped by Python (.pth) and Qt (plugins)."""
    if sys.platform != "darwin":
        return Check("Hidden files", "ok", "not applicable on this platform")
    import sysconfig

    site = Path(sysconfig.get_paths()["purelib"])
    hidden_flag = getattr(__import__("stat"), "UF_HIDDEN", 0x8000)
    candidates = list(site.glob("*.pth")) + list(site.glob("PySide6/Qt/plugins/platforms/*"))
    hidden = [p for p in candidates if getattr(p.lstat(), "st_flags", 0) & hidden_flag]
    if hidden:
        names = ", ".join(sorted(p.name for p in hidden)[:4])
        return Check(
            "Hidden files",
            "error",
            f"{len(hidden)} file(s) flagged hidden in {site} ({names}); Python skips hidden .pth "
            "files and Qt skips hidden plugins",
            f"chflags -R nohidden {site}  (tools/yuem/dev_env.sh does this)",
        )
    return Check("Hidden files", "ok", "no hidden .pth files or Qt platform plugins")


def _check_certificates(network: bool) -> Check:
    paths = ssl.get_default_verify_paths()
    configured = os.environ.get("SSL_CERT_FILE") or paths.cafile
    has_bundle = bool(configured and Path(configured).exists()) or bool(
        paths.capath and Path(paths.capath).is_dir() and any(Path(paths.capath).iterdir())
    )
    hint = 'set SSL_CERT_FILE to python -c "import certifi; print(certifi.where())"'
    if network:
        import urllib.request

        try:
            urllib.request.urlopen("https://pypi.org/simple/", timeout=10)
        except Exception as exc:  # noqa: BLE001 - any failure is the finding
            return Check("HTTPS certificates", "error", f"HTTPS to pypi.org failed: {exc}", hint)
        return Check("HTTPS certificates", "ok", f"HTTPS to pypi.org works (bundle {configured})")
    if not has_bundle:
        return Check(
            "HTTPS certificates", "warn", f"no CA bundle at {configured or paths.openssl_cafile}", hint
        )
    return Check("HTTPS certificates", "ok", f"CA bundle {configured}")


def _check_qt() -> Check:
    if importlib.util.find_spec("PySide6") is None:
        return Check(
            "Qt",
            "warn",
            "PySide6 not installed (Studio unavailable)",
            'pip install "pyhydrogeophysx[desktop]"',
        )
    try:
        from PySide6 import __version__ as pyside_version
        from PySide6.QtCore import QLibraryInfo
    except Exception as exc:  # noqa: BLE001 - any import failure is the finding
        return Check("Qt", "error", f"PySide6 import failed: {exc}", "reinstall PySide6")
    plugins = Path(QLibraryInfo.path(QLibraryInfo.LibraryPath.PluginsPath)) / "platforms"
    found = (
        sorted(p.stem.removeprefix("lib").removeprefix("q") for p in plugins.glob("*"))
        if plugins.is_dir()
        else []
    )
    if not found:
        return Check("Qt", "error", f"no platform plugins in {plugins}", "reinstall PySide6")
    return Check("Qt", "ok", f"PySide6 {pyside_version}; platform plugins: {', '.join(found)}")


def _check_vtk() -> Check:
    if importlib.util.find_spec("vtkmodules") is None:
        return Check(
            "VTK / OpenGL", "warn", "VTK not installed (3D viewers unavailable)", OPTIONAL_ENGINES[2][2]
        )
    try:
        from vtkmodules import vtkRenderingOpenGL2  # noqa: F401 - loads the OpenGL backend
        from vtkmodules.vtkCommonCore import vtkVersion
    except Exception as exc:  # noqa: BLE001 - any import failure is the finding
        return Check(
            "VTK / OpenGL", "error", f"OpenGL backend failed to load: {exc}", "check the graphics driver"
        )
    return Check("VTK / OpenGL", "ok", f"VTK {vtkVersion.GetVTKVersion()} with the OpenGL2 backend")


def _check_cjk_font() -> Check:
    try:
        from matplotlib import font_manager
    except ImportError:
        return Check("CJK font", "warn", "matplotlib not installed")
    available = {entry.name for entry in font_manager.fontManager.ttflist}
    found = [name for name in CJK_FONTS if name in available]
    if not found:
        return Check(
            "CJK font",
            "warn",
            "no Chinese-capable font found; Chinese labels render as boxes",
            "install Noto Sans CJK SC (Linux) or use the system fonts on macOS/Windows",
        )
    return Check("CJK font", "ok", ", ".join(found[:3]))


def _check_project(project: Path | None) -> Check:
    from PyHydroGeophysX.qt_apps.state import default_project_root

    folder = project if project is not None else default_project_root()
    probe_root = folder
    while not probe_root.exists() and probe_root.parent != probe_root:
        probe_root = probe_root.parent
    free = shutil.disk_usage(probe_root).free
    detail = f"{folder} ({free / 1024**3:.1f} GiB free)"
    if free < FREE_SPACE_ERROR:
        return Check("Project folder", "error", detail, "free disk space before running inversions")
    try:
        with tempfile.NamedTemporaryFile(dir=probe_root, prefix=".phgx-doctor-"):
            pass
    except OSError as exc:
        return Check(
            "Project folder", "error", f"{detail}: not writable ({exc})", "choose a writable project folder"
        )
    if free < FREE_SPACE_WARN:
        return Check("Project folder", "warn", detail, "less than 5 GiB free; 3D runs may fill the disk")
    return Check("Project folder", "ok", detail)


def _check_engines() -> list[Check]:
    # Optional by design (GPL, CUDA-only, ...): absence is reported, not warned.
    checks = []
    for module, purpose, hint in OPTIONAL_ENGINES[1:]:
        if module == "pyvista":
            continue
        installed = importlib.util.find_spec(module) is not None
        state = "installed" if installed else f"not installed (optional; {hint})"
        checks.append(Check(f"Engine {module}", "ok", f"{purpose}: {state}"))
    return checks


def run_checks(*, project: Path | None = None, network: bool = False) -> list[Check]:
    """Run every check; never raises."""
    steps: list[Callable[[], Check | list[Check]]] = [
        _check_python,
        _check_package,
        _check_core_libraries,
        _check_pygimli_core,
        _check_hidden_files,
        lambda: _check_certificates(network),
        _check_qt,
        _check_vtk,
        _check_cjk_font,
        lambda: _check_project(project),
        _check_engines,
    ]
    results: list[Check] = []
    for step in steps:
        try:
            outcome = step()
        except Exception as exc:  # noqa: BLE001 - a crashing check is reported, not raised
            name = getattr(step, "__name__", "check").removeprefix("_check_")
            outcome = Check(name, "error", f"check crashed: {exc!r}")
        results.extend(outcome if isinstance(outcome, list) else [outcome])
    return results


def exit_code(checks: Sequence[Check]) -> int:
    statuses = {check.status for check in checks}
    if "error" in statuses:
        return 2
    return 1 if "warn" in statuses else 0


def format_report(checks: Sequence[Check]) -> str:
    marks = {"ok": "[ OK ]", "warn": "[WARN]", "error": "[FAIL]"}
    lines = []
    for check in checks:
        lines.append(f"{marks[check.status]} {check.name}: {check.detail}")
        if check.hint and check.status != "ok":
            lines.append(f"       -> {check.hint}")
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="phgx-doctor", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--project", type=Path, default=None)
    parser.add_argument("--network", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    checks = run_checks(project=args.project, network=args.network)
    code = exit_code(checks)
    if args.json:
        print(
            json.dumps(
                {"exit_code": code, "checks": [asdict(c) for c in checks]}, indent=2, ensure_ascii=False
            )
        )
    else:
        print(format_report(checks))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
