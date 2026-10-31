"""Plugin registry end to end (plan M2.1).

A throwaway plugin distribution (a package plus a ``.dist-info`` with an
``entry_points.txt``) is put on ``PYTHONPATH`` of a fresh interpreter, which is
how an installed extension package reaches PyHydroGeophysX.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

PLUGIN = """
from PyHydroGeophysX.plugins import (
    ModulePage, ReaderSpec, register_module, register_reader, register_short_code, register_workflow,
)
from PyHydroGeophysX.workflows.models import WorkflowRunResult
from PyHydroGeophysX.workflows.registry import WorkflowDescriptor


def run_echo(spec, context):
    return WorkflowRunResult(status="ok", summary={"echo": spec.parameters["text"]})


def read(path):
    return {"path": str(path)}


def register():
    register_workflow(WorkflowDescriptor("demo.echo", "yuem_demo_plugin:run_echo", "Echo a parameter."))
    register_short_code("demo.echo", "demo")
    register_reader(ReaderSpec(name="demo-text", method="Demo", loader="yuem_demo_plugin:read",
                               suffixes=(".demo",)))
    register_module(ModulePage(key="demo", import_path="yuem_demo_plugin.page", class_name="DemoPage",
                               title="Demo Page", group="Plugins", workflow_ids=("demo.echo",),
                               result_key="demo_results"))


def broken():
    raise RuntimeError("this plugin is broken")
"""

PAGE = """
from PyHydroGeophysX.qt_apps.modules.base import BaseModule


class DemoPage(BaseModule):
    module_key = "demo"
    module_title = "Demo Page"

    def agent_describe(self):
        return {"module": "demo"}
"""


@pytest.fixture
def plugin_path(tmp_path: Path) -> Path:
    package = tmp_path / "yuem_demo_plugin"
    package.mkdir()
    (package / "__init__.py").write_text(PLUGIN, encoding="utf-8")
    (package / "page.py").write_text(PAGE, encoding="utf-8")
    info = tmp_path / "yuem_demo_plugin-0.1.dist-info"
    info.mkdir()
    (info / "METADATA").write_text("Metadata-Version: 2.1\nName: yuem-demo-plugin\nVersion: 0.1\n")
    (info / "entry_points.txt").write_text(
        "[phgx.plugins]\ndemo = yuem_demo_plugin:register\nbroken = yuem_demo_plugin:broken\n"
    )
    return tmp_path


def _python(code: str, plugin_path: Path, cwd: Path) -> dict[str, object]:
    env = {
        **os.environ,
        "PYTHONPATH": os.pathsep.join([str(plugin_path), os.environ.get("PYTHONPATH", "")]),
        "QT_QPA_PLATFORM": "offscreen",
        "MPLBACKEND": "Agg",
    }
    done = subprocess.run(
        [sys.executable, "-c", textwrap.dedent(code)],
        capture_output=True,
        text=True,
        env=env,
        cwd=cwd,
        timeout=300,
        check=False,
    )
    assert done.returncode == 0, done.stderr[-3000:]
    result: dict[str, object] = json.loads(done.stdout.strip().splitlines()[-1])
    return result


def test_plugin_workflow_runs_headless_without_qt(plugin_path: Path, tmp_path: Path) -> None:
    out = _python(
        """
        import json, sys
        from PyHydroGeophysX import plugins
        from PyHydroGeophysX.workflows.models import RunContext, WorkflowSpec
        from PyHydroGeophysX.workflows.registry import module_descriptor_for
        from PyHydroGeophysX.workflows.runner import run_workflow
        result = run_workflow(WorkflowSpec("demo.echo", parameters={"text": "hi"}),
                              RunContext(output_dir="out"))
        print(json.dumps({
            "summary": result.summary,
            "qt_loaded": "PySide6" in sys.modules,
            "descriptor": module_descriptor_for("demo_results").navigation_key,
            "reader": plugins.find_reader("x.DEMO").name,
            "failures": list(plugins.load_failures()),
        }))
        """,
        plugin_path,
        tmp_path,
    )
    assert out["summary"] == {"echo": "hi"}
    assert out["qt_loaded"] is False
    assert out["descriptor"] == "demo"
    assert out["reader"] == "demo-text"
    failures = out["failures"]
    assert isinstance(failures, list) and len(failures) == 1 and "broken" in failures[0]


def test_plugin_workflow_runs_through_the_cli(plugin_path: Path, tmp_path: Path) -> None:
    recipe = tmp_path / "recipe.json"
    recipe.write_text(
        json.dumps({"schema_version": "1", "workflow_id": "demo.echo", "parameters": {"text": "cli"}})
    )
    out = _python(
        f"""
        import json, subprocess, sys
        done = subprocess.run([sys.executable, "-m", "PyHydroGeophysX.workflows.cli", "run",
                               {str(recipe)!r}], capture_output=True, text=True)
        print(json.dumps({{"code": done.returncode, "result": json.loads(done.stdout)}}))
        """,
        plugin_path,
        tmp_path,
    )
    assert out["code"] == 0
    result = out["result"]
    assert isinstance(result, dict) and result["summary"] == {"echo": "cli"}


@pytest.mark.gui
def test_plugin_page_joins_the_studio(plugin_path: Path, tmp_path: Path) -> None:
    pytest.importorskip("PySide6")
    out = _python(
        """
        import json
        from PySide6.QtWidgets import QApplication
        app = QApplication([])
        from PyHydroGeophysX.qt_apps.modules import MODULE_ORDER, MODULE_SPECS, build_module
        from PyHydroGeophysX.qt_apps.results_store import _SHORT_CODES
        from PyHydroGeophysX.qt_apps.state import StudioState
        from PyHydroGeophysX.qt_apps.widgets.project_tree import TREE_STRUCTURE
        page = build_module("demo", StudioState.from_context(None), lambda *a, **k: None)
        groups = [group for group, _ in TREE_STRUCTURE]
        print(json.dumps({
            "spec": list(MODULE_SPECS["demo"]),
            "before_map": MODULE_ORDER.index("demo") < MODULE_ORDER.index("project_map"),
            "group_before_project": groups.index("Plugins") < groups.index("Project"),
            "page": type(page).__name__,
            "code": _SHORT_CODES.get("demo.echo"),
        }))
        """,
        plugin_path,
        tmp_path,
    )
    assert out["spec"] == ["yuem_demo_plugin.page", "DemoPage", "Demo Page"]
    assert out["before_map"] is True
    assert out["group_before_project"] is True
    assert out["page"] == "DemoPage"
    assert out["code"] == "demo"
