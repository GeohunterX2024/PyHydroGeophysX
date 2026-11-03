"""PyInstaller runtime hook: the frozen Studio runs the workflow processes it starts (findings F-23).

``ProcessWorkflowWorker`` starts ``<sys.executable> -m PyHydroGeophysX.workflows.cli run ...``.
In the frozen Studio ``sys.executable`` is the Studio itself, whose launcher takes no ``-m``,
so every workflow run in a process failed there. For the modules named below only, this hook
runs the module as ``python -m`` would and exits with its status; any other start goes on to
the Studio as before.
"""

import sys

RUNNABLE_MODULES = ("PyHydroGeophysX.workflows.cli",)

if (
    getattr(sys, "frozen", False)
    and len(sys.argv) > 2
    and sys.argv[1] == "-m"
    and sys.argv[2] in RUNNABLE_MODULES
):
    import runpy

    _module = sys.argv[2]
    sys.argv = [_module, *sys.argv[3:]]
    try:
        runpy.run_module(_module, run_name="__main__", alter_sys=True)
    except SystemExit as _exit:
        _code = _exit.code
    else:
        _code = 0
    sys.stdout.flush()
    sys.stderr.flush()
    sys.exit(_code)
