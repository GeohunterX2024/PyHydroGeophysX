"""Shared helpers for the YUEM fork tools: repository paths, ownership, git.

Every tool under ``tools/yuem`` reads the ownership map through here, so the
classification rules (most specific prefix wins, directories end in ``/``) live
in one place.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from functools import cache
from pathlib import Path

import tomllib

ROOT = Path(__file__).resolve().parents[2]
OWNERSHIP = ROOT / ".yuem" / "ownership.toml"
CLASSES = ("own", "follow", "shared", "frozen")


@dataclass(frozen=True)
class Ownership:
    """The parsed ``.yuem/ownership.toml``."""

    base_commit: str
    default_class: str
    prefixes: tuple[tuple[str, str], ...]
    strict: tuple[str, ...]
    typed: tuple[str, ...]
    strict_rules: tuple[str, ...]
    max_file_lines: int

    def classify(self, path: str) -> str:
        """Return the class of a repository-relative POSIX path."""
        best = ""
        found = self.default_class
        for prefix, cls in self.prefixes:
            matches = path.startswith(prefix) if prefix.endswith("/") else path == prefix
            if matches and len(prefix) > len(best):
                best, found = prefix, cls
        return found

    def is_strict(self, path: str) -> bool:
        return _under(path, self.strict)

    def is_typed(self, path: str) -> bool:
        return _under(path, self.typed)


def _under(path: str, prefixes: tuple[str, ...]) -> bool:
    return any(path.startswith(p) if p.endswith("/") else path == p for p in prefixes)


@cache
def ownership() -> Ownership:
    data = tomllib.loads(OWNERSHIP.read_text(encoding="utf-8"))
    meta = data["meta"]
    prefixes: list[tuple[str, str]] = []
    for cls in CLASSES:
        prefixes.extend((p, cls) for p in data["classes"].get(cls, []))
    quality = data.get("quality", {})
    return Ownership(
        base_commit=str(meta["base_commit"]),
        default_class=str(meta.get("default_class", "follow")),
        prefixes=tuple(prefixes),
        strict=tuple(quality.get("strict", [])),
        typed=tuple(quality.get("typed", [])),
        strict_rules=tuple(quality.get("strict_rules", [])),
        max_file_lines=int(quality.get("max_file_lines", 1500)),
    )


def git(*args: str, check: bool = True) -> str:
    """Run git in the repository root and return stdout without the final newline."""
    done = subprocess.run(
        ["git", *args], cwd=ROOT, check=check, capture_output=True, text=True, encoding="utf-8"
    )
    return done.stdout.rstrip("\n")


def ref_exists(ref: str) -> bool:
    return (
        subprocess.run(
            ["git", "rev-parse", "--verify", "--quiet", ref], cwd=ROOT, capture_output=True
        ).returncode
        == 0
    )


def upstream_ref() -> str:
    """The commit the fork's own changes are measured against.

    The local ``upstream`` branch when present; otherwise the recorded base
    commit, which every clone of the fork contains.
    """
    # The full ref: a remote named "upstream" makes the bare name ambiguous.
    branch = "refs/heads/upstream"
    return branch if ref_exists(branch) else ownership().base_commit


def changed_files(base: str, *, include_worktree: bool = True) -> list[str]:
    """Paths changed between ``merge-base(base, HEAD)`` and HEAD (plus the worktree).

    Deleted files are included; callers that read contents must check existence.
    """
    merge_base = git("merge-base", base, "HEAD")
    names = set(git("diff", "--name-only", merge_base, "HEAD").splitlines())
    if include_worktree:
        names.update(git("diff", "--name-only", "HEAD").splitlines())
        names.update(git("ls-files", "--others", "--exclude-standard").splitlines())
    return sorted(n for n in names if n)


def file_at(ref: str, path: str) -> str | None:
    """Contents of ``path`` at ``ref``, or None when it does not exist there."""
    done = subprocess.run(
        ["git", "show", f"{ref}:{path}"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return done.stdout if done.returncode == 0 else None


def tracked_python_files(*roots: str) -> list[Path]:
    """Tracked plus untracked-but-not-ignored ``.py`` files under the given roots."""
    listed = git("ls-files", "--cached", "--others", "--exclude-standard", "--", *roots)
    return sorted(ROOT / p for p in listed.splitlines() if p.endswith(".py") and (ROOT / p).exists())


def existing(paths: tuple[str, ...]) -> list[str]:
    """The subset of configured path prefixes that exist on disk."""
    return [p for p in paths if (ROOT / p).exists()]
