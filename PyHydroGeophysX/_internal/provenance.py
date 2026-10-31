"""Run provenance: the environment a result was computed in, and how it differs now.

Every workflow result and every saved Studio run carries
``provenance["environment"]`` from :func:`collect_environment`, so a result can
be traced to the code version, the interpreter, the numerical libraries and the
BLAS that produced it, and a rerun can say what changed since.

Package versions come from the installed distributions' metadata, never from a
module's ``__version__``: pyGIMLi's ``__version__``, for one, reports the git
state of the current working directory rather than its own release.
"""

from __future__ import annotations

import copy
import hashlib
import json
import os
import platform
import subprocess
import sys
from collections.abc import Iterable, Mapping
from functools import cache
from importlib import metadata
from pathlib import Path
from typing import Any

#: Distributions whose versions decide numerical results or the GUI.
TRACKED_DISTRIBUTIONS: tuple[str, ...] = (
    "PyHydroGeophysX",
    "numpy",
    "scipy",
    "pandas",
    "matplotlib",
    "pygimli",
    "pgcore",
    "simpeg",
    "discretize",
    "pymatsolver",
    "empymod",
    "numba",
    "h5py",
    "pyproj",
    "vtk",
    "pyvista",
    "PySide6",
    "adtlert",
    "resipy",
)

#: Thread-count variables that change floating-point summation order.
THREAD_VARIABLES: tuple[str, ...] = (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
    "NUMBA_NUM_THREADS",
)

SCHEMA = "phgx-provenance-v1"
_PACKAGE_DIR = Path(__file__).resolve().parents[1]


def _distribution_versions(names: Iterable[str]) -> dict[str, str]:
    versions: dict[str, str] = {}
    for name in names:
        try:
            versions[name] = metadata.version(name)
        except metadata.PackageNotFoundError:
            continue
    return versions


def _git_describe() -> str | None:
    """``git describe`` of the source tree the package was imported from, if any."""
    repo = _PACKAGE_DIR.parent
    if not (repo / ".git").exists():
        return None
    try:
        done = subprocess.run(
            ["git", "describe", "--tags", "--always", "--dirty"],
            cwd=repo,
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    described = done.stdout.strip()
    return described or None


def _blas() -> list[dict[str, Any]]:
    try:
        from threadpoolctl import threadpool_info
    except ImportError:
        return []
    import numpy  # loaded first, so threadpoolctl can see its BLAS

    pools = []
    for info in threadpool_info():
        pools.append(
            {
                "user_api": info.get("user_api"),
                "internal_api": info.get("internal_api"),
                "version": info.get("version"),
                "num_threads": info.get("num_threads"),
                "library": Path(str(info.get("filepath", ""))).name,
            }
        )
    if not any(pool["user_api"] == "blas" for pool in pools):
        # threadpoolctl cannot see Apple Accelerate, which NumPy's macOS arm64
        # wheels link; NumPy's build configuration still names it.
        try:
            config = numpy.show_config(mode="dicts")
            blas = config["Build Dependencies"]["blas"]
            pools.append(
                {
                    "user_api": "blas",
                    "internal_api": str(blas.get("name")),
                    "version": str(blas.get("version")),
                    "num_threads": None,
                    "library": "numpy build configuration",
                }
            )
        except (KeyError, TypeError, ValueError):
            pass
    return pools


def _phgx_version() -> str:
    # The package is always imported before this submodule; reading it from
    # sys.modules keeps provenance from importing (and depending on) the whole package.
    package = sys.modules.get("PyHydroGeophysX")
    return str(getattr(package, "__version__", "unknown"))


@cache
def _environment() -> dict[str, Any]:
    frozen = bool(getattr(sys, "frozen", False))
    return {
        "schema": SCHEMA,
        "phgx_version": _phgx_version(),
        "git": None if frozen else _git_describe(),
        "frozen": frozen,
        "python": {
            "version": platform.python_version(),
            "implementation": platform.python_implementation(),
        },
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
        },
        "packages": _distribution_versions(TRACKED_DISTRIBUTIONS),
        "blas": _blas(),
        "threads": {name: os.environ[name] for name in THREAD_VARIABLES if name in os.environ},
        "cpu_count": os.cpu_count(),
    }


def collect_environment() -> dict[str, Any]:
    """The current environment as a JSON-compatible mapping (cached per process)."""
    return copy.deepcopy(_environment())


def parameters_digest(payload: Mapping[str, Any]) -> str:
    """SHA-256 of a JSON-compatible mapping in canonical form."""
    text = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def environment_diff(recorded: Mapping[str, Any], current: Mapping[str, Any] | None = None) -> list[str]:
    """Human-readable differences between a recorded environment and the current one.

    Covers the fork version, Python, platform, tracked package versions and the
    BLAS implementation; an empty list means a rerun uses the same stack.
    """
    now = collect_environment() if current is None else current
    changes: list[str] = []

    def compare(label: str, before: Any, after: Any) -> None:
        if before != after:
            changes.append(f"{label}: {before} -> {after}")

    compare("PyHydroGeophysX", recorded.get("phgx_version"), now.get("phgx_version"))
    compare(
        "Python",
        (recorded.get("python") or {}).get("version"),
        (now.get("python") or {}).get("version"),
    )
    rec_platform = recorded.get("platform") or {}
    now_platform = now.get("platform") or {}
    compare(
        "platform",
        f"{rec_platform.get('system')} {rec_platform.get('machine')}",
        f"{now_platform.get('system')} {now_platform.get('machine')}",
    )
    rec_packages = recorded.get("packages") or {}
    now_packages = now.get("packages") or {}
    for name in sorted(set(rec_packages) | set(now_packages)):
        compare(name, rec_packages.get(name, "absent"), now_packages.get(name, "absent"))

    def blas_names(env: Mapping[str, Any]) -> list[str]:
        return sorted(
            f"{pool.get('internal_api')} {pool.get('version')}"
            for pool in env.get("blas") or []
            if pool.get("user_api") == "blas"
        )

    compare("BLAS", blas_names(recorded), blas_names(now))
    return changes


__all__ = [
    "SCHEMA",
    "THREAD_VARIABLES",
    "TRACKED_DISTRIBUTIONS",
    "collect_environment",
    "environment_diff",
    "parameters_digest",
]
