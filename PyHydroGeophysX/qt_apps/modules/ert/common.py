"""Shared imports, constants and helpers of the ERT page (plan M4.5).

The top of the former ``ert_processing.py``, unchanged: the page's parts import
what they use from here.

Imports resistivity data from many instrument/file formats (the user picks the
device), shows the electrode layout and a QC apparent-resistivity pseudosection,
runs a pygimli ERT inversion, and shows the inverted resistivity section. The
electrode geometry can still be edited and exported.

Loading reuses ``data_processing.ert_data_agent.load_ert_resipy`` for the
device/format the user selects (there is no auto-detect: pygimli's native reader
silently mis-parses several common formats, e.g. E4D). ``pygimli.physics.ert.load``
remains an internal fallback when a device parser raises.
"""

from __future__ import annotations

import contextlib
import json
import os
from pathlib import Path
import re
import shutil
from typing import Any, Callable, Dict, List, Optional, Tuple
import uuid

import numpy as np
from PySide6.QtCore import QCoreApplication, QEventLoop, Qt, QTimer, Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QAbstractSpinBox,
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QSpinBox,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from PyHydroGeophysX.data_processing import run_inputs
from PyHydroGeophysX.data_processing import ert_io as ert_load
from PyHydroGeophysX.data_processing import survey_timing
from PyHydroGeophysX.data_processing import table_io
from PyHydroGeophysX.qt_apps import i18n, io_utils, theme
from PyHydroGeophysX.qt_apps.modules.base import BaseModule, LogFn
from PyHydroGeophysX.qt_apps.qt_utils import (
    BusyStateController,
    ContentWidthScrollArea,
    PlainDoubleSpinBox,
    ReproduceBar,
    merged_row,
    select_directory,
)
from PyHydroGeophysX.qt_apps.widgets import colormaps as cmaps
from PyHydroGeophysX.qt_apps.widgets import length_units
from PyHydroGeophysX.qt_apps.widgets.color_range import ColorRange
from PyHydroGeophysX.qt_apps.widgets.readout import toolbar_row
from PyHydroGeophysX.qt_apps.widgets import temperature_panel
from PyHydroGeophysX.qt_apps.widgets.mesh_preview import MeshPreviewView
from PyHydroGeophysX.qt_apps.widgets.mesh_view import MeshResultView
from PyHydroGeophysX.qt_apps.widgets.quality_view import InversionQualityView
from PyHydroGeophysX.qt_apps.widgets.reciprocal_view import ReciprocalErrorView
from PyHydroGeophysX.qt_apps.widgets.run_controls import progress_with_stop
from PyHydroGeophysX.qt_apps.workers import (
    ProcessProbeWorker,
    ProcessWorkflowWorker,
    TaskWorker,
)
from PyHydroGeophysX.qt_apps.modules.ert_mesh_preview import derive_preview, mesh_build_spec
from PyHydroGeophysX.qt_apps.process_jobs import scratch_process_worker
from PyHydroGeophysX.data_processing.ert_io import save_edited_ert_container
from PyHydroGeophysX.visualization.axis_units import length_factor, set_length_axis
from PyHydroGeophysX.workflows import (
    ArtifactRef,
    WorkflowRunResult,
    WorkflowSpec,
    export_workflow_bundle,
)

# Imported rather than repeated: lambda_search needs nothing but numpy, so this
# module stays importable without pygimli, which ert_inversion pulls in.
from PyHydroGeophysX.inversion.lambda_search import (  # noqa: E402
    LAMBDA_BOUNDS as _LAMBDA_BOUNDS,
)
import logging

_logger = logging.getLogger(__name__)

#: The highest mesh quality offered, ert_mesh.MAX_MESH_QUALITY: Triangle
#: never finishes much above it. Repeated here because ert_mesh pulls in
#: pygimli, which this module does not import.
_MAX_MESH_QUALITY = 34.0

_TC_WAITING = ("Run an inversion - one survey or a time-lapse series; Apply then "
               "corrects the model shown here, without inverting again.")

#: The Reciprocal errors tab before data are loaded, and how to get pairs.
_RECIP_NO_DATA = ("Load ERT data to see how far each reading and its reciprocal disagree. "
                  "In time-lapse mode the tab shows every survey of the list.")
_RECIP_HOW = ("To get them, measure reciprocals in the field - each reading repeated with "
              "its current and potential electrodes exchanged; most instruments can add "
              "them to a protocol. For a survey written as two files, add the reciprocal "
              "file to the list as well and keep “Pair reciprocal files with their forward "
              "file” ticked.")

#: Where the Data QC checks start. None acts until Apply filter is pressed, and
#: those under "More checks" only while it is unfolded, so none changes a run
#: nobody filtered. Each starts where it drops readings that are plainly bad
#: and leaves the bulk of a survey alone.
_QC_DEFAULTS: Dict[str, Any] = {
    "max_error": 20.0,           # %; a file with no error column of its own is all 5 %
    "drop_nonpositive": True,    # a polarity or geometry error, not a measurement
    "min_voltage": 1e-5,         # V; 10 uV, the noise floor the DAS-1 reader filters at
    "min_current": 1e-4,         # A; below 0.1 mA the injection failed
    "k_over_median": 20.0,       # |k| cap, as a multiple of the loaded file's median
    "max_contact_r": 3e4,        # ohm; 30 kOhm, as the DAS-1 reader filters
    "max_stack": 50.0,           # %; the potential scattered by half of itself
    "max_reciprocal": 5.0,       # %; the usual reciprocal-error limit
}


def _value_name(correction: Optional[Dict[str, Any]]) -> str:
    """Column name for exported resistivity: it says the temperature when corrected."""
    if not correction:
        return "resistivity"
    reference = float(correction.get("reference_temperature_C", 25.0))
    return f"resistivity_at_{reference:g}C".replace(".", "p")

_ELEC_FILTER = "Electrodes (*.csv *.txt *.dat);;All files (*)"
_DATA_FILTER = ("ERT data (*.dat *.ohm *.txt *.csv *.Data *.bin *.stg *.amp *.udf *.tab)"
                ";;All files (*)")
#: The files of a folder dropped on the page that join the list: the data
#: filter's extensions, matched without regard to case.
_DATA_SUFFIXES = (".dat", ".ohm", ".txt", ".csv", ".data", ".bin", ".stg", ".amp", ".udf",
                  ".tab")
#: The χ² stopping rule's tooltip, while the engine and mode use it.
_PLATEAU_TIP = ("The inversion is done when one more iteration lowers χ² by less than "
                "this. Larger stops sooner; smaller makes sure the fit has really run "
                "out of room. A time-lapse run judges χ² over all its surveys.")
#: What the Data tab says before anything is loaded.
#: The electrodes drawn along the top of the pseudosection: the canvas text
#: colour (theme PALETTE["canvas_text"]); the canvas is white in either theme.
_ELECTRODE_MARK = "#1d1d1f"
_EMPTY_DATA_MESSAGE = ("Drop ERT data files or a folder here,\n"
                       "or choose the format and use Add files… on the right.")

#: How the file list finds each survey's time, on hover over its summary line.
#: survey_timing reads every form listed; ert_input_format.md says the same.
_TIME_FORMATS_TIP = (
    "How survey times are read\n\n"
    "1. From the file name. Put the year first:\n"
    "      site_2026-01-12_05-50-38.dat   (recommended)\n"
    "      site_2026_01_12_05_50_38.dat\n"
    "      site_20260112_055038.dat\n"
    "      site_2026-01-12T05-50-38.dat\n"
    "2. Otherwise from a date line at the top of the file, e.g.\n"
    "      # date: 2026-01-12 05:50:38\n"
    "   (for BERT / pyGIMLi files: the very first line, before the electrode count).\n"
    "3. Otherwise, if “Use file times” is ticked, from each file's modified time.\n\n"
    "Avoid month-first or day-first names such as 01-12-2026: they can be read two\n"
    "ways. Hover over a file to see where its time came from. Data format has more.")

_INSTRUMENTS: List[Tuple[str, Optional[str]]] = [
    ("BERT / Unified (.ohm/.dat)", "BERT"),
    ("E4D", "E4D"),
    ("DAS-1", "DAS-1"),
    ("Syscal", "Syscal"),
    ("ABEM-Lund", "ABEM-Lund"),
    ("Res2DInv", "ResInv"),
    ("Protocol DC", "Protocol DC"),
    ("Protocol IP", "Protocol IP"),
    ("Sting / SuperSting", "Sting"),
    ("ARES", "ARES"),
    ("Lippmann", "Lippmann"),
    ("Electra", "Electra"),
    ("Subsurface Insights (.csv)", "Subsurface Insights"),
    ("BGS PRIME / RESIMGR (.tab)", "PRIME/RESIMGR"),
    ("Custom", "Custom"),
]
