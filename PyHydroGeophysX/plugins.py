"""Plugin registry: Studio pages, workflows, data readers and run short codes (plan M2.1).

An extension package (DCIP, LOTEM, an institute's own method) adds itself to
PyHydroGeophysX without editing it:

* :func:`register_module` - a Studio page, its place in the navigator, the
  workflows it runs and the key its results are filed under;
* :func:`register_workflow` - a workflow the CLI, the Studio's worker process
  and the assistants can run (the existing workflow registry, re-exported);
* :func:`register_reader` - a data-file reader, found by suffix or by sniffing;
* :func:`register_short_code` - the abbreviation run folders are named with.

Packages announce themselves through entry points; each entry point names a
callable that takes no arguments and makes its registrations::

    [project.entry-points."phgx.plugins"]
    dcip = "phgx_dcip.plugin:register"

:func:`load_entry_points` runs them once per process. The Studio launcher and
the workflow registry call it, so a plugin's workflows also exist in the worker
process that runs them.

The built-in tables (``qt_apps.modules.MODULE_SPECS``, ``MODULE_ORDER``,
``qt_apps.widgets.project_tree.TREE_STRUCTURE``,
``workflows.registry.MODULE_DESCRIPTORS``, ``qt_apps.results_store._SHORT_CODES``)
keep their shapes and are updated in place, so every existing reader of them
sees plugin entries without change.
"""

from __future__ import annotations

import importlib
import sys
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from PyHydroGeophysX._internal.plugin_loader import (
    ENTRY_POINT_GROUPS,
    load_entry_points,
    load_failures,
    record_failure,
)
from PyHydroGeophysX.workflows.registry import (
    MODULE_DESCRIPTORS,
    ModuleDescriptor,
    WorkflowDescriptor,
)
from PyHydroGeophysX.workflows.registry import register_workflow as _register_workflow

#: Navigator group a page lands in when it names none.
DEFAULT_GROUP = "Geophysical Data Processing"


@dataclass(frozen=True)
class ModulePage:
    """A Studio page contributed by a plugin.

    ``import_path`` is the absolute module path of the page class. ``group`` is
    the navigator group (an existing one, or a new group placed before
    "Project"); ``label`` is the item's text there, ``title`` the page title.
    """

    key: str
    import_path: str
    class_name: str
    title: str
    group: str = DEFAULT_GROUP
    label: str = ""
    workflow_ids: tuple[str, ...] = ()
    result_key: str = ""
    aliases: tuple[str, ...] = ()


@dataclass(frozen=True)
class ReaderSpec:
    """A data-file reader. ``loader`` is ``"package.module:function"``.

    ``suffixes`` are matched case-insensitively against the file name;
    ``sniff`` (same form, optional) is called with the path and returns True for
    files it recognises, for formats a suffix cannot tell apart.
    """

    name: str
    method: str
    loader: str
    suffixes: tuple[str, ...] = ()
    sniff: str = ""
    description: str = ""

    def load_function(self, spec: str | None = None) -> Callable[..., Any]:
        module_name, _, attribute = (spec or self.loader).partition(":")
        if not attribute:
            raise ValueError(f"reader {self.name!r}: {spec or self.loader!r} must be 'module:function'")
        function: Callable[..., Any] = getattr(importlib.import_module(module_name), attribute)
        if not callable(function):
            raise TypeError(f"reader {self.name!r}: {spec or self.loader!r} is not callable")
        return function


@dataclass
class _State:
    readers: dict[str, ReaderSpec] = field(default_factory=dict)
    pages: dict[str, ModulePage] = field(default_factory=dict)
    applied: set[str] = field(default_factory=set)


_STATE = _State()


def register_workflow(descriptor: WorkflowDescriptor, *, replace: bool = False) -> None:
    """Register a workflow (see :func:`PyHydroGeophysX.workflows.registry.register_workflow`)."""
    _register_workflow(descriptor, replace=replace)


def register_short_code(workflow_id: str, code: str) -> None:
    """Name run folders of ``workflow_id`` with ``code`` (letters and digits, at most 8)."""
    if not code.isalnum() or len(code) > 8:
        raise ValueError(f"short code {code!r} must be 1-8 letters or digits")
    from PyHydroGeophysX.qt_apps import results_store

    existing = results_store._SHORT_CODES.get(workflow_id)
    if existing is not None and existing != code:
        raise KeyError(f"workflow {workflow_id!r} already has short code {existing!r}")
    results_store._SHORT_CODES[workflow_id] = code


def register_module(page: ModulePage, *, replace: bool = False) -> None:
    """Add a Studio page: page table, navigator order and tree, module descriptor.

    Safe without Qt: the module descriptor (workflow IDs, result key) applies at
    once; the Qt-side tables are updated when ``qt_apps.modules`` is imported,
    or at once if it already is. A headless worker loading the same plugin
    therefore still registers its workflows.
    """
    if page.key in _STATE.pages and not replace:
        raise KeyError(f"Studio page {page.key!r} is already registered")
    _STATE.pages[page.key] = page
    if page.workflow_ids or page.result_key:
        MODULE_DESCRIPTORS[page.key] = ModuleDescriptor(
            page.key, page.result_key or page.key, tuple(page.workflow_ids), tuple(page.aliases)
        )
    if "PyHydroGeophysX.qt_apps.modules" in sys.modules:
        apply_pages()


def apply_pages() -> None:
    """Put registered plugin pages into the Studio's tables (idempotent).

    Called by ``qt_apps.modules`` when it is imported. A page whose key is
    already a built-in page is refused and recorded in :func:`load_failures`.
    """
    from PyHydroGeophysX.qt_apps.modules import MODULE_ORDER, MODULE_SPECS
    from PyHydroGeophysX.qt_apps.widgets.project_tree import TREE_STRUCTURE

    for page in _STATE.pages.values():
        entry = (page.import_path, page.class_name, page.title)
        if page.key in MODULE_SPECS and MODULE_SPECS[page.key] != entry:
            if page.key not in _STATE.applied:
                record_failure(f"{page.key}: page key collides with an existing Studio page")
            continue
        MODULE_SPECS[page.key] = entry
        if page.key not in MODULE_ORDER:
            anchor = "project_map" if "project_map" in MODULE_ORDER else None
            MODULE_ORDER.insert(MODULE_ORDER.index(anchor) if anchor else len(MODULE_ORDER), page.key)
        _add_to_tree(TREE_STRUCTURE, page)
        _STATE.applied.add(page.key)


def _add_to_tree(tree: list[tuple[str, list[tuple[str, str]]]], page: ModulePage) -> None:
    label = page.label or page.title
    for group, items in tree:
        if group == page.group:
            if all(key != page.key for _, key in items):
                items.append((label, page.key))
            from PyHydroGeophysX.qt_apps.widgets.project_tree import sort_group_items

            sort_group_items(group, items)
            return
    position = next((i for i, (group, _) in enumerate(tree) if group == "Project"), len(tree))
    tree.insert(position, (page.group, [(label, page.key)]))


def register_reader(reader: ReaderSpec, *, replace: bool = False) -> None:
    """Add a data-file reader."""
    if reader.name in _STATE.readers and not replace:
        raise KeyError(f"reader {reader.name!r} is already registered")
    _STATE.readers[reader.name] = reader


def readers(method: str | None = None) -> tuple[ReaderSpec, ...]:
    """Registered readers, optionally of one method, in registration order."""
    found = _STATE.readers.values()
    return tuple(r for r in found if method is None or r.method.lower() == method.lower())


def find_reader(path: str | Path, method: str | None = None) -> ReaderSpec | None:
    """The first reader whose sniffer accepts ``path``, else the first whose suffix matches."""
    path = Path(path)
    candidates = readers(method)
    for reader in candidates:
        if reader.sniff:
            try:
                if reader.load_function(reader.sniff)(path):
                    return reader
            except (OSError, ValueError, UnicodeDecodeError):
                continue
    name = path.name.lower()
    return next((r for r in candidates if any(name.endswith(s.lower()) for s in r.suffixes)), None)


def plugin_pages() -> tuple[ModulePage, ...]:
    return tuple(_STATE.pages.values())


__all__ = [
    "DEFAULT_GROUP",
    "ENTRY_POINT_GROUPS",
    "ModulePage",
    "ReaderSpec",
    "apply_pages",
    "find_reader",
    "load_entry_points",
    "load_failures",
    "plugin_pages",
    "readers",
    "register_module",
    "register_reader",
    "register_short_code",
    "register_workflow",
]
