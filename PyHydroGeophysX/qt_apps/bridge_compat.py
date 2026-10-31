"""The Streamlit <-> Qt JSON bridge, kept apart from the Studio's project state (plan M2.7).

Streamlit starts the Studio with a context file (where the project lives,
where to read hydrology data, which page to open) and polls a result file
beside it. :class:`BridgeLink` holds that link; :func:`load_context` applies
a context to a :class:`~PyHydroGeophysX.qt_apps.state.StudioState` and
:func:`save_result` writes the result document Streamlit reads. Nothing here
imports PySide6.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Optional

from PyHydroGeophysX._internal.utils import utc_now
from PyHydroGeophysX.qt_apps import io_utils

if TYPE_CHECKING:
    from PyHydroGeophysX.qt_apps.state import StudioState

RESULT_FILENAME = "full_studio_result.json"
APP_NAME = "PyHydroGeophysX Professional Studio"


@dataclass
class BridgeLink:
    """Where Streamlit's context came from, what it said, and where the result goes."""

    context_path: Optional[Path] = None
    result_path: Optional[Path] = None
    context: Dict[str, Any] = field(default_factory=dict)


def _as_path(value: Any) -> Optional[Path]:
    return Path(value) if value else None


def load_context(state: "StudioState") -> Dict[str, Any]:
    """Read ``state``'s context file and apply it; a missing or invalid file yields ``{}``."""
    link = state.bridge
    context = io_utils.read_json(link.context_path) if link.context_path else None
    link.context = context or {}
    state.project_root = _as_path(link.context.get("project_root"))
    state.output_dir = _as_path(link.context.get("output_dir"))
    state.hydro_data_dir = _as_path(link.context.get("hydro_data_dir"))
    state.hydro_output_dir = _as_path(link.context.get("hydro_output_dir"))
    initial_module = link.context.get("initial_module") or "home"
    if initial_module:
        state.selected_module = str(initial_module)
    # The result file lives next to the context file in the qt_bridge dir.
    if link.context_path is not None:
        link.result_path = link.context_path.parent / RESULT_FILENAME
    elif state.output_dir is not None:
        link.result_path = state.output_dir / "qt_bridge" / RESULT_FILENAME
    return link.context


def default_result_path(output_dir: Path) -> Path:
    """The result file of a Studio started without a context, under ``output_dir``."""
    return Path(output_dir) / "qt_bridge" / RESULT_FILENAME


def build_result(state: "StudioState") -> Dict[str, Any]:
    """The result document in the schema Streamlit expects."""
    link = state.bridge
    return {
        "app": APP_NAME,
        "status": "saved",
        "selected_module": state.selected_module,
        "created_time": utc_now(),
        "context_path": str(link.context_path) if link.context_path else "",
        "output_dir": str(state.output_dir) if state.output_dir else "",
        "module_results": state.module_results,
        "workflow_id": state.active_workflow_id,
        "recipe_path": state.active_recipe_path,
        "workflow_results": state.workflow_results,
    }


def save_result(state: "StudioState") -> Path:
    """Write the result document to the bridge result file."""
    link = state.bridge
    if link.result_path is None:
        link.result_path = default_result_path(state.output_dir or Path.cwd())
    return Path(io_utils.write_json(link.result_path, build_result(state)))


__all__ = [
    "APP_NAME",
    "RESULT_FILENAME",
    "BridgeLink",
    "build_result",
    "default_result_path",
    "load_context",
    "save_result",
]
