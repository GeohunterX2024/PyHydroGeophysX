"""Studio state (Qt-free).

``StudioState`` holds the project state the pages share: the open Project and
its runs, per-module results, and in-session resources. The Streamlit bridge
(the context Streamlit handed over and the result file it polls) lives in
:mod:`PyHydroGeophysX.qt_apps.bridge_compat`; the attributes and methods of
the state that reach it are kept as thin delegates for existing callers.
Nothing here imports PySide6 so it stays easy to test.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

from PyHydroGeophysX.qt_apps import bridge_compat
from PyHydroGeophysX.qt_apps.bridge_compat import APP_NAME, RESULT_FILENAME, BridgeLink
from PyHydroGeophysX.qt_apps.results_store import ResultsStore, RunHandle
import logging

_logger = logging.getLogger(__name__)
#: Names the folder used when no Project is open. The cloud image sets it to a
#: folder its file browser shows, since ``~/.pyhydrogeophysx`` is hidden there.
PROJECT_DIR_ENV = "PHGX_PROJECT_DIR"


def default_project_root() -> Path:
    """The folder results go to when no Project was chosen.

    ``PHGX_PROJECT_DIR`` when set, otherwise ``~/.pyhydrogeophysx``.
    """
    configured = os.environ.get(PROJECT_DIR_ENV, "").strip()
    if configured:
        return Path(configured).expanduser()
    return Path.home() / ".pyhydrogeophysx"


def project_location_problem(path: str | Path) -> Optional[Tuple[str, str]]:
    """``("error" | "warn", message)`` when a Project would live inside the source tree, else None.

    Inside the package itself a Project is refused: its runs would be mixed
    into the code and shipped with it. Inside a source checkout's
    ``examples/`` it is allowed with a warning, since a Project opened there
    before must still open.
    """
    package = Path(__file__).resolve().parents[1]
    resolved = Path(path).expanduser().resolve()
    if resolved == package or package in resolved.parents:
        return ("error", f"A Project cannot be inside the PyHydroGeophysX package ({package}); "
                         "choose a folder outside it.")
    checkout = package.parent
    examples = checkout / "examples"
    if (checkout / "pyproject.toml").is_file() and (resolved == examples or examples in resolved.parents):
        return ("warn", f"This Project is inside the source checkout's examples folder ({examples}): "
                        "its runs mix with the example data. A folder outside the source tree is safer.")
    return None


@dataclass
class StudioState:
    """Mutable state shared across the studio main window and its modules."""

    #: The Streamlit bridge: context file, its content, and the result file.
    bridge: BridgeLink = field(default_factory=BridgeLink, repr=False)
    selected_module: str = "home"
    project_root: Optional[Path] = None
    output_dir: Optional[Path] = None
    #: User-facing Project storage.  Kept distinct from ``project_root``, which
    #: is the Streamlit bridge/source-project context.
    results_store_root: Optional[Path] = None
    results_store: Optional[ResultsStore] = field(default=None, repr=False)
    #: True while results go to the built-in fallback folder that nobody chose.
    #: Every survey of every session lands in that one Project, so the window
    #: offers to name a Project before data is first added, and says on screen
    #: which of the two is in use.
    default_project: bool = False
    hydro_data_dir: Optional[Path] = None
    hydro_output_dir: Optional[Path] = None
    selected_points: List[List[float]] = field(default_factory=list)
    active_dataset: Optional[str] = None
    map_selected_id: Optional[str] = None
    module_results: Dict[str, Any] = field(default_factory=dict)
    workflow_results: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    active_workflow_id: str = ""
    active_recipe_path: str = ""
    #: In-memory observations, models, meshes, and interfaces shared by the
    #: geophysical processing pages. Payloads can contain NumPy/PyGIMLi objects
    #: and are deliberately excluded from the Streamlit bridge JSON.
    geophysical_resources: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    #: In-session handoff payload, e.g. a seismic-derived bedrock interface passed
    #: from the Seismic structure module to the ERT -> hydrology module. Not
    #: serialized into the bridge result file.
    shared_structure: Optional[Dict[str, Any]] = None
    #: Temperature-correction settings, shared by every page that offers the
    #: correction, so the ERT page and Saved Results show the same choices.
    #: Plain values; in-session only and not written to the bridge file.
    temperature_settings: Dict[str, Any] = field(default_factory=dict)
    #: The colour map chosen for each kind of display - ``"resistivity"``,
    #: ``"resistivity_change"``, ``"velocity"``, ``"em_section"``, ... (the keys
    #: are defined in ``qt_apps/widgets/colormaps.py``) - so every view of one
    #: quantity, on any page, draws it in the same colours. Only what the user
    #: picked is stored; a view with no entry keeps its own default. Plain
    #: names; in-session only and not written to the bridge file.
    colormap_settings: Dict[str, str] = field(default_factory=dict)
    #: The Boreholes page's wells, logs, water levels and geophysical logs, kept
    #: by ``qt_apps/widgets/borehole_panel.py`` under ``"store"``. In-session
    #: only; adding the wells to the Project Map saves them with the project.
    borehole_settings: Dict[str, Any] = field(default_factory=dict)
    #: Why the open Project's folder is a poor place for one (project_location_problem), or "".
    project_warning: str = ""
    _active_run_handles: Dict[Tuple[str, str], RunHandle] = field(
        default_factory=dict, repr=False
    )
    #: Called with no arguments whenever the set of runs awaiting a save may have
    #: changed. The window uses it to keep its unsaved-run indicator honest. A
    #: plain callable rather than a signal, so this module stays Qt-free.
    on_runs_changed: Optional[Callable[[], None]] = field(default=None, repr=False)
    #: Also called, with no arguments, whenever a run may have closed: pages
    #: holding a run's log open use it to close that log (``modules/base.py``).
    run_watchers: List[Callable[[], None]] = field(default_factory=list, repr=False)

    # -- bridge (delegates to bridge_compat) ---------------------------------
    @property
    def context_path(self) -> Optional[Path]:
        return self.bridge.context_path

    @context_path.setter
    def context_path(self, value: Optional[Path]) -> None:
        self.bridge.context_path = None if value is None else Path(value)

    @property
    def result_path(self) -> Optional[Path]:
        return self.bridge.result_path

    @result_path.setter
    def result_path(self, value: Optional[Path]) -> None:
        self.bridge.result_path = None if value is None else Path(value)

    @property
    def context(self) -> Dict[str, Any]:
        return self.bridge.context

    @context.setter
    def context(self, value: Dict[str, Any]) -> None:
        self.bridge.context = dict(value or {})

    def load_context(self) -> Dict[str, Any]:
        """Load the bridge context JSON. Missing/invalid files yield ``{}``."""
        return bridge_compat.load_context(self)

    def build_result(self) -> Dict[str, Any]:
        """Assemble the result document in the schema Streamlit expects."""
        return bridge_compat.build_result(self)

    def save_result(self) -> Path:
        """Persist the current results to the bridge result file."""
        return bridge_compat.save_result(self)

    # -- construction --------------------------------------------------------
    @classmethod
    def from_context(cls, context_path: Optional[str]) -> "StudioState":
        """Build a state object, loading the context JSON when one is given."""
        state = cls()
        if context_path:
            state.context_path = Path(context_path)
            state.load_context()
        else:
            # No bridge context: still pick a sensible, stable place to write
            # results so "Save Result" never crashes when the app is launched
            # standalone. Prefer the repository results dir when the current
            # directory looks like a PyHydroGeophysX checkout; otherwise use a
            # per-user location instead of scattering qt_bridge dirs around
            # whatever directory the app happened to start in.
            cwd = Path.cwd()
            if os.environ.get(PROJECT_DIR_ENV):
                base = default_project_root()
            elif (cwd / "PyHydroGeophysX").is_dir() and (cwd / "examples").is_dir():
                base = cwd / "results" / "streamlit_workflow"
            else:
                base = default_project_root()
            state.output_dir = base
            state.default_project = True
            state.result_path = bridge_compat.default_result_path(base)
        return state

    def update_module_result(self, module_name: str, result_dict: Dict[str, Any]) -> None:
        """Record (or overwrite) the result payload for a single module."""
        self.module_results[str(module_name)] = result_dict

    def update_workflow_result(
        self,
        module_name: str,
        workflow_id: str,
        result_dict: Dict[str, Any],
        *,
        recipe_path: str = "",
    ) -> None:
        """Record a canonical workflow result while preserving the legacy bridge key."""
        module_key = str(module_name)
        key = (module_key, str(workflow_id))
        self.active_workflow_id = str(workflow_id)
        self.active_recipe_path = str(recipe_path)
        self.workflow_results[module_key] = {
            "workflow_id": self.active_workflow_id,
            "recipe_path": self.active_recipe_path,
            "result": dict(result_dict),
        }
        handle = self._active_run_handles.pop(key, None)
        if handle is not None and self.results_store is not None:
            if recipe_path:
                try:
                    handle.record.recipe_path = Path(recipe_path).resolve().relative_to(
                        handle.run_dir.resolve()
                    ).as_posix()
                except ValueError:
                    # A public API caller may keep its recipe elsewhere; managed Qt
                    # runs deliberately never persist paths outside their run root.
                    handle.record.recipe_path = ""
            self.results_store.finish_run(handle, result_dict)
            self._notify_runs_changed()

    # -- durable Result Store ----------------------------------------------
    @property
    def project_directory(self) -> Optional[Path]:
        """The active results destination, shared by all project displays."""
        if self.results_store is not None:
            return self.results_store.root
        return self.results_store_root or self.output_dir

    @property
    def project_name(self) -> str:
        if self.default_project:
            return "Default folder"
        path = self.project_directory
        return (path.name or str(path)) if path is not None else "No project open"

    def set_results_store(self, root: str | Path, *, read_only: bool = False) -> ResultsStore:
        """Open/create the folder that owns durable Qt run history."""
        requested = Path(root).expanduser().resolve()
        problem = project_location_problem(requested)
        if problem is not None and problem[0] == "error" and not read_only:
            raise ValueError(problem[1])
        self.project_warning = problem[1] if problem is not None and problem[0] == "warn" else ""
        if (
            self.results_store is not None
            and self.results_store.root == requested
            and self.results_store.read_only == bool(read_only)
        ):
            return self.results_store
        running = [
            handle.run_id for handle in self._active_run_handles.values()
            if handle.record.status == "running"
        ]
        if running:
            raise RuntimeError(
                "Cannot switch Project while a computation is running: "
                + ", ".join(running)
            )
        store = ResultsStore.open_or_create(requested, read_only=read_only)
        self.results_store_root = store.root
        self.results_store = store
        if not read_only:
            # Existing module forms still read this bridge-compatible field for
            # defaults.  New persistent writes use RunHandle directories.
            self.output_dir = store.root
            if self.context_path is None:
                self.result_path = bridge_compat.default_result_path(store.root)
        return store

    def ensure_results_store(self) -> ResultsStore:
        if self.results_store is None:
            fallback = default_project_root() / "results"
            self.set_results_store(self.output_dir or fallback)
        assert self.results_store is not None
        return self.results_store

    def begin_run(
        self,
        module_name: str,
        operation_id: str,
        workflow_id: str = "",
        *,
        label: str = "",
    ) -> RunHandle:
        module_key = str(module_name)
        operation_key = str(operation_id)
        key = (module_key, operation_key)
        existing = self._active_run_handles.get(key)
        if existing is not None and existing.record.status == "running":
            raise RuntimeError(
                f"Operation {module_key!r}/{operation_key!r} already has an active persisted run."
            )
        store = self.ensure_results_store()
        # Modules suggest data/operation names. Include the named Project once,
        # here, so every processing page and every save entry point agrees.
        # Later user edits remain verbatim, and the run directory keeps its id.
        label = str(label or "").strip()
        if not self.default_project:
            name = self.project_name
            if label != name and not label.startswith(f"{name} · "):
                label = f"{name} · {label}" if label else name
        handle = store.begin_run(module_key, operation_key, workflow_id, label=label)
        self._active_run_handles[key] = handle
        return handle

    def active_run(
        self, module_name: str, operation_id: str = ""
    ) -> Optional[RunHandle]:
        module_key = str(module_name)
        if operation_id:
            return self._active_run_handles.get((module_key, str(operation_id)))
        matches = [
            handle for (module, _operation), handle in self._active_run_handles.items()
            if module == module_key
        ]
        return matches[0] if len(matches) == 1 else None

    def _pop_active_run(
        self, module_name: str, operation_id: str = ""
    ) -> Optional[RunHandle]:
        module_key = str(module_name)
        if operation_id:
            return self._active_run_handles.pop((module_key, str(operation_id)), None)
        keys = [key for key in self._active_run_handles if key[0] == module_key]
        if len(keys) > 1:
            raise RuntimeError(
                f"Module {module_key!r} has multiple active operations; operation_id is required."
            )
        return self._active_run_handles.pop(keys[0], None) if keys else None

    def _notify_runs_changed(self) -> None:
        for watcher in [self.on_runs_changed, *self.run_watchers]:
            if watcher is None:
                continue
            try:
                watcher()
            except Exception:  # noqa: BLE001 - an indicator must not break a run
                _logger.debug("StudioState._notify_runs_changed: an indicator must not break a run", exc_info=True)

    def finish_run(
        self, module_name: str, result: Any, operation_id: str = ""
    ) -> None:
        handle = self._pop_active_run(module_name, operation_id)
        if handle is not None:
            self.ensure_results_store().finish_run(handle, result)
            self._notify_runs_changed()

    def fail_run(self, module_name: str, error: str, operation_id: str = "") -> None:
        handle = self._pop_active_run(module_name, operation_id)
        if handle is not None:
            self.ensure_results_store().fail_run(handle, error)
            self._notify_runs_changed()

    def cancel_run(
        self, module_name: str, error: str = "", operation_id: str = ""
    ) -> None:
        handle = self._pop_active_run(module_name, operation_id)
        if handle is not None:
            self.ensure_results_store().cancel_run(handle, error)
            self._notify_runs_changed()

    def cancel_module_runs(self, module_name: str, error: str = "") -> None:
        module_key = str(module_name)
        for key in [key for key in self._active_run_handles if key[0] == module_key]:
            handle = self._active_run_handles.pop(key)
            self.ensure_results_store().cancel_run(handle, error)
            self._notify_runs_changed()

    # -- saving --------------------------------------------------------------
    def has_unsaved_runs(self) -> bool:
        """Whether any finished run is still waiting on the user's decision."""
        store = self.results_store
        return bool(store is not None and store.has_unsaved())

    def unsaved_runs(self) -> List[Any]:
        store = self.results_store
        return store.list_unsaved_runs() if store is not None else []

    def save_all_runs(self) -> List[Any]:
        """Put every finished-but-unsaved run into the Project's history."""
        store = self.results_store
        if store is None:
            return []
        try:
            return store.save_all_unsaved()
        finally:
            self._notify_runs_changed()

    def name_runs(self, names: Dict[str, str]) -> None:
        """Give runs the names the user typed, keyed by run id.

        Only the label in the run's record changes. The folder keeps its id for
        a name, because modules hold paths into it that must keep resolving.
        """
        store = self.results_store
        if store is None or not names:
            return
        try:
            for run_id, label in names.items():
                store.update_run(run_id, label=label)
        finally:
            self._notify_runs_changed()

    def discard_all_runs(self) -> int:
        store = self.results_store
        if store is None:
            return 0
        try:
            return store.discard_all_unsaved()
        finally:
            self._notify_runs_changed()

    def clear_project_session(self) -> None:
        """Drop process-local results when the active Project changes."""
        if self._active_run_handles:
            raise RuntimeError("Cannot clear Project state while computations are running.")
        self.module_results.clear()
        self.workflow_results.clear()
        self.geophysical_resources.clear()
        self.shared_structure = None
        self.selected_points.clear()
        self.active_dataset = None
        self.active_workflow_id = ""
        self.active_recipe_path = ""

    def register_geophysical_resource(
        self,
        method: str,
        role: str,
        payload: Any,
        *,
        label: str = "",
        path: str = "",
        metadata: Optional[Dict[str, Any]] = None,
        resource_id: Optional[str] = None,
    ) -> str:
        """Register a process-local geophysical observation or inversion product."""
        method_key = str(method).strip().upper()
        role_key = str(role).strip().lower()
        if not method_key or not role_key:
            raise ValueError("method and role are required for a geophysical resource.")
        if payload is None:
            raise ValueError("A geophysical resource payload cannot be None.")
        if resource_id is None:
            prefix = f"{method_key.lower()}:{role_key}"
            index = 1
            resource_id = f"{prefix}:{index}"
            while resource_id in self.geophysical_resources:
                index += 1
                resource_id = f"{prefix}:{index}"
        resource_id = str(resource_id)
        self.geophysical_resources[resource_id] = {
            "id": resource_id,
            "method": method_key,
            "role": role_key,
            "label": label or f"{method_key} {role_key}",
            "path": str(path or ""),
            "metadata": dict(metadata or {}),
            "payload": payload,
        }
        return resource_id

    def list_geophysical_resources(
        self,
        method: Optional[str] = None,
        role: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """List resource descriptors without exposing non-serializable payloads."""
        method_key = str(method).strip().upper() if method else None
        role_key = str(role).strip().lower() if role else None
        resources: List[Dict[str, Any]] = []
        for item in self.geophysical_resources.values():
            if method_key and item["method"] != method_key:
                continue
            if role_key and item["role"] != role_key:
                continue
            resources.append({key: value for key, value in item.items() if key != "payload"})
        return resources

    def get_geophysical_resource(self, resource_id: str) -> Optional[Dict[str, Any]]:
        """Return a registered resource including its in-memory payload."""
        return self.geophysical_resources.get(str(resource_id))

    # -- convenience ---------------------------------------------------------
    def context_summary(self) -> Dict[str, Any]:
        """Return a compact dict for the idle properties panel."""
        return {
            "app_key": self.context.get("app_key", ""),
            "selected_module": self.selected_module,
            "project_root": str(self.project_root or ""),
            "output_dir": str(self.output_dir or ""),
            "hydro_data_dir": str(self.hydro_data_dir or ""),
            "hydro_output_dir": str(self.hydro_output_dir or ""),
            "context_path": str(self.context_path or ""),
            "result_path": str(self.result_path or ""),
            "results_store_root": str(self.results_store_root or ""),
            "demo_mode": self.context.get("demo_mode", False),
        }
