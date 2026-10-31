"""The ERT page: the page: its controls and setup (plan M4.5).

Part of :class:`~.page.ERTProcessingModule`, split from the former
``ert_processing.py`` by area; the methods are unchanged.
"""

from __future__ import annotations

from .common import (
    Any,
    BaseModule,
    BusyStateController,
    ColorRange,
    ContentWidthScrollArea,
    Dict,
    InversionQualityView,
    List,
    LogFn,
    MeshPreviewView,
    MeshResultView,
    Optional,
    Path,
    PlainDoubleSpinBox,
    ProcessProbeWorker,
    QAbstractItemView,
    QAbstractSpinBox,
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QCoreApplication,
    QFormLayout,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QSpinBox,
    QTabWidget,
    QTimer,
    QVBoxLayout,
    QWidget,
    Qt,
    ReciprocalErrorView,
    ReproduceBar,
    TaskWorker,
    Tuple,
    _EMPTY_DATA_MESSAGE,
    _INSTRUMENTS,
    _LAMBDA_BOUNDS,
    _PLATEAU_TIP,
    _QC_DEFAULTS,
    _TIME_FORMATS_TIP,
    cmaps,
    i18n,
    length_units,
    np,
    progress_with_stop,
    theme,
    toolbar_row,
)
from .qc_panel import _QCPanel
from .inversion_panel import _InversionPanel
from .import_panel import _ImportPanel
from .mesh_panel import _MeshPanel
from .timelapse_panel import _TimelapsePanel
from .results_panel import _ResultsPanel
from .presenter import _Presenter


class ERTProcessingModule(_QCPanel, _InversionPanel, _ImportPanel, _MeshPanel, _TimelapsePanel, _ResultsPanel, _Presenter, BaseModule):
    module_key = "ert_processing"
    module_title = "ERT Processing"

    def __init__(self, state: Any, log: LogFn, parent=None) -> None:
        super().__init__(state, log, parent)
        self._x: List[float] = []
        self._z: List[float] = []
        # A 3-D survey's electrodes cover an area: each has a y as well, and
        # the data are drawn and inverted in 3-D (ert_io.survey_is_3d).
        self._y: List[float] = []
        self._survey_3d = False
        self._labels: List[str] = []
        self._electrode_origins: List[Optional[int]] = []
        self._electrode_path: Optional[Path] = None
        # The electrodes as chosen from that file, as plain x y z columns: what
        # the instrument readers are handed on the next load.
        self._electrode_table: Optional[Path] = None
        self._data_path: Optional[Path] = None
        # The file the single-inversion model on screen was inverted from. A
        # preview loaded since replaces _data_path while that model stays up.
        self._inv_source: Optional[Path] = None
        # The thresholds of the last "Apply filter", until Reset: what a
        # time-lapse run applies to every one of its surveys.
        self._qc_applied: Optional[Dict[str, Any]] = None
        # What that filter did to the data loaded now: the run's QC report.
        self._qc_report: Optional[Dict[str, Any]] = None
        self._pseudo: List[Tuple[float, float, float]] = []
        self._n_meas = 0
        self._ert_data = None        # pygimli DataContainerERT for inversion (filtered)
        self._ert_data_full = None   # unfiltered original
        self._data_note = ""         # why the loaded file has no usable container
        self._qc_mask: Optional[List[bool]] = None
        self._inv_worker: Optional[Any] = None
        self._inv_busy: Optional[BusyStateController] = None
        self._adtlert_probe_worker: Optional[ProcessProbeWorker] = None
        self._adtlert_probe_serial = 0
        self._adtlert_runtime_ready: Optional[bool] = None
        self._adtlert_single_ready: Optional[bool] = None
        self._adtlert_timelapse_ready: Optional[bool] = None
        self._adtlert_checks: Dict[str, str] = {}
        self._e4d_probe_worker: Optional[ProcessProbeWorker] = None
        self._e4d_probe_serial = 0
        self._e4d_found: Optional[Dict[str, Any]] = None   # the last E4D check
        self._r2_probe_worker: Optional[ProcessProbeWorker] = None
        self._r2_probe_serial = 0
        self._r2_found: Optional[Dict[str, Any]] = None    # the last R2/R3t check
        self._ert_recipe_path: str = ""
        # The running runs' inversion_settings.txt, which their outcome is added
        # to; the time-lapse one with the parameters it was launched with.
        self._ert_settings_path: Optional[Path] = None
        self._tl_settings: Optional[Tuple[Path, Dict[str, Any]]] = None
        # Set by the Mode selector, which trades the pre-inversion checks against
        # turnaround. Quick skips them; Full validates and repairs k. A k that
        # disagrees with the geometry rescales the whole section while leaving
        # chi2 untouched, so Quick cannot warn you that it went wrong: the result
        # panel and the log only report that the check did not run. Scripts and
        # the agent can still set "check" or "off" directly through set_params.
        self._geom_policy = "off"
        # Single-inversion results. When the auto-λ search moves off the requested
        # λ, both runs are kept: _inv_choices holds one entry per selectable model
        # and _inv_mgr always points at the one on screen.
        self._inv_mgr = None
        self._inv_choices: List[Dict[str, Any]] = []
        self._agent_run_state = "idle"
        self._agent_run_error = ""
        # A temperature correction of the single-inversion model on screen: what
        # was applied, and the corrected model. The manager keeps the model as
        # inverted, so the correction can be changed or taken off.
        self._inv_correction: Optional[Dict[str, Any]] = None
        self._inv_corrected: Optional[np.ndarray] = None
        self._load_worker: Optional[TaskWorker] = None
        # Every file added to the list, reciprocal files included, in the order
        # the list keeps them. _tl_files holds the surveys made of them: while
        # "Pair reciprocal files" is ticked, a forward file stands for itself and
        # its reciprocal (_tl_partner), and a reciprocal file no forward file
        # matches is left out (_tl_left_out).
        self._tl_all: List[str] = []
        self._tl_partner: Dict[str, str] = {}
        self._tl_left_out: List[str] = []
        # The reciprocal file merged with the survey on screen, and its counts.
        self._data_partner: Optional[Path] = None
        self._pair_info: Optional[Dict[str, Any]] = None
        self._tl_files: List[str] = []
        self._tl_labels: List[str] = []
        self._tl_times: List[float] = []
        self._tl_timing: Optional[Any] = None   # acquisition times of the sequence
        self._tl_worker: Optional[Any] = None
        self._tl_busy: Optional[BusyStateController] = None
        self._tl_recipe_path = ""
        self._tl_out: Optional[str] = None
        self._tl_result: Optional[dict] = None
        self._tl_mesh = None              # in-memory time-lapse result for the
        self._tl_models = None            # interactive per-step viewer
        # The models as inverted, kept beside the ones on screen so a
        # temperature correction can be applied, changed and taken off again
        # without inverting; and what that correction was, or None.
        self._tl_models_raw = None
        self._tl_correction: Optional[Dict[str, Any]] = None
        self._tl_coverage = None
        self._tl_step_titles: List[str] = []
        # The pseudosection's colour map: viridis unless the user picks another,
        # remembered for the session like every other view's.
        self._pseudo_colormap = cmaps.ColormapChooser(
            cmaps.APPARENT_RESISTIVITY, "viridis",
            shared=cmaps.colormap_settings(self.state))
        self._pseudo_colormap.colormapChanged.connect(self._on_pseudo_colormap_changed)
        self._cmap = cmaps.to_pyqtgraph(self._pseudo_colormap.colormap())

        root = QHBoxLayout(self)
        self._tabs = QTabWidget()
        # View > Length Units: the pseudosection and the electrode line of the
        # data panel relabel in the new unit; the data stay in metres.
        length_units.notifier().changed.connect(self._on_length_unit_changed)
        # Files dropped anywhere on the page join the list, as Add files… does:
        # a series of hundreds of surveys is dragged in from a folder.
        self.setAcceptDrops(True)

        # Render the apparent-resistivity section with Matplotlib rather than a
        # pyqtgraph ScatterPlotItem.  On some Windows Qt/pyqtgraph combinations
        # the scatter loses the ViewBox transform after a resize: axes remain in
        # data coordinates while markers are painted as scene pixels above/left
        # of the plot.  This section is intentionally static; reliable placement
        # is more important than per-point hover/pick interaction here.
        self._pseudo_widget = QWidget()
        pseudo_layout = QVBoxLayout(self._pseudo_widget)
        pseudo_layout.setContentsMargins(0, 0, 0, 0)
        pseudo_layout.setSpacing(4)
        from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
        from matplotlib.figure import Figure

        self._pseudo_figure = Figure(facecolor="white", constrained_layout=True)
        self._pseudo_canvas = FigureCanvasQTAgg(self._pseudo_figure)
        self._pseudo_ax = self._pseudo_figure.add_subplot(111)
        # Zoom, pan and Save as on every plot. The colour limits are typed in
        # under it, beside the colour scale they set.
        pseudo_bar, self._pseudo_toolbar = toolbar_row(self._pseudo_canvas, self._pseudo_widget)
        pseudo_layout.addWidget(pseudo_bar)
        pseudo_layout.addWidget(self._pseudo_canvas, stretch=1)

        self._pseudo_legend = QWidget()
        # Reserve the legend's full text height; the canvas takes the remaining
        # space, including in short windows and with larger display fonts.
        self._pseudo_legend.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        legend_layout = QVBoxLayout(self._pseudo_legend)
        legend_layout.setContentsMargins(8, 0, 8, 6)
        legend_layout.setSpacing(1)
        # The colour map beside the colour scale it changes. The title takes the
        # stretch itself: the page lets long labels elide, and an eliding label
        # beside a separate stretch is given no width at all.
        legend_title = QHBoxLayout()
        legend_title.setContentsMargins(0, 0, 0, 0)
        legend_title.addWidget(QLabel(QCoreApplication.translate("PHGX", "Apparent resistivity (Ω·m)")), 1)
        # Locked, every survey of a series previews on one scale.
        self._pseudo_range = ColorRange(positive=True, what="the apparent resistivity")
        self._pseudo_range.changed.connect(self._draw_pseudosection)
        legend_title.addWidget(self._pseudo_range)
        legend_title.addWidget(self._pseudo_colormap)
        legend_layout.addLayout(legend_title)
        self._pseudo_scale_bar = QFrame()
        self._pseudo_scale_bar.setFixedHeight(12)
        self._paint_pseudo_scale()
        legend_layout.addWidget(self._pseudo_scale_bar)
        scale_row = QHBoxLayout()
        scale_row.setContentsMargins(0, 0, 0, 0)
        scale_row.setSpacing(2)
        self._pseudo_scale_labels: List[QLabel] = []
        for index in range(5):
            label = QLabel("—")
            label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
            label.setAlignment(
                Qt.AlignLeft if index == 0 else Qt.AlignRight if index == 4 else Qt.AlignCenter
            )
            scale_row.addWidget(label, stretch=1)
            self._pseudo_scale_labels.append(label)
        legend_layout.addLayout(scale_row)
        pseudo_layout.addWidget(self._pseudo_legend)
        # Until data arrive the tab says what to do. Left as built it would show
        # an empty 0-1 axis over a colour bar of "—" placeholders, which reads
        # as a bar whose numbers are covered.
        self._show_pseudosection_message(_EMPTY_DATA_MESSAGE)

        # The studio state's colormap choices, shared with Saved Results: a
        # section recoloured on either page is recoloured on both.
        self._model_view = MeshResultView(colormaps=cmaps.colormap_settings(self.state))
        # Tools that act on the model sit beside it and serve whichever result is
        # on screen - a single inversion or a time-lapse step - rather than living
        # in one run mode's settings, where the other mode's results cannot reach
        # them. Saved Results puts the same panel in the same place.
        self._model_view.add_side_panel(self._build_temperature_group())
        self._model_view._side.setSizes([1000, 360])
        # The "Resistivity model" tab shows the single inversion OR any time step
        # of a time-lapse run, picked with the step selector (hidden until a
        # time-lapse result is available) — so there is no separate time-lapse tab.
        model_tab = QWidget()
        self._model_tab = model_tab
        model_layout = QVBoxLayout(model_tab)
        model_layout.setContentsMargins(0, 0, 0, 0)
        self._tl_step_row = QWidget()
        step_bar = QHBoxLayout(self._tl_step_row)
        step_bar.setContentsMargins(6, 2, 6, 2)
        step_bar.addWidget(QLabel(QCoreApplication.translate("PHGX", "Time step:")))
        self._tl_step_combo = QComboBox()
        self._tl_step_combo.setToolTip(QCoreApplication.translate("PHGX", "Which time-lapse inversion result is displayed."))
        self._tl_step_combo.currentIndexChanged.connect(self._show_tl_step)
        step_bar.addWidget(self._tl_step_combo, stretch=1)
        self._tl_prev_btn = QPushButton("◀"); self._tl_prev_btn.setMaximumWidth(34)
        self._tl_prev_btn.setToolTip(QCoreApplication.translate("PHGX", "Previous time step"))
        self._tl_prev_btn.clicked.connect(lambda: self._step_tl(-1))
        self._tl_next_btn = QPushButton("▶"); self._tl_next_btn.setMaximumWidth(34)
        self._tl_next_btn.setToolTip(QCoreApplication.translate("PHGX", "Next time step"))
        self._tl_next_btn.clicked.connect(lambda: self._step_tl(1))
        step_bar.addWidget(self._tl_prev_btn); step_bar.addWidget(self._tl_next_btn)
        # Absolute resistivity is dominated by the static structure, which is the
        # same in every step; the change against the first survey is what the
        # repeat measurement was made to see.
        step_bar.addWidget(QLabel(QCoreApplication.translate("PHGX", "Show:")))
        self._tl_view_mode = QComboBox()
        self._tl_view_mode.addItem(QCoreApplication.translate("PHGX", "Resistivity"), "model")
        self._tl_view_mode.addItem("% change from baseline", "change")
        self._tl_view_mode.setToolTip(
            QCoreApplication.translate("PHGX", "Resistivity shows the inverted model. “% change from baseline” shows "
            "100 × (ρ − ρ₀) / ρ₀ against the first time step, on a diverging scale "
            "centred on zero."))
        self._tl_view_mode.currentIndexChanged.connect(self._on_tl_view_mode_changed)
        step_bar.addWidget(self._tl_view_mode)
        self._tl_step_row.setVisible(False)
        model_layout.addWidget(self._tl_step_row)
        # When the auto-λ search settles on a different λ than the one typed, both
        # models are kept and this row switches which of the two is displayed.
        self._lam_pick_row = QWidget()
        pick_bar = QHBoxLayout(self._lam_pick_row)
        pick_bar.setContentsMargins(6, 2, 6, 2)
        pick_bar.addWidget(QLabel(QCoreApplication.translate("PHGX", "Model:")))
        self._lam_pick = QComboBox()
        self._lam_pick.setToolTip(
            QCoreApplication.translate("PHGX", "The auto-λ search re-inverted at a different λ. Selects between that "
            "model and the one at the λ set above."))
        self._lam_pick.currentIndexChanged.connect(self._show_lambda_choice)
        pick_bar.addWidget(self._lam_pick, stretch=1)
        self._lam_pick_row.setVisible(False)
        model_layout.addWidget(self._lam_pick_row)
        # A profile inverted on a 3D mesh: the section is drawn here, and the
        # whole volume opens in the 3D viewer.
        self._model_3d_path = ""
        self._model_3d_btn = QPushButton(QCoreApplication.translate("PHGX", "Open 3D model"))
        self._model_3d_btn.setIcon(theme.icon("fa5s.cube"))
        self._model_3d_btn.setToolTip(
            QCoreApplication.translate("PHGX", "The inversion ran on a 3D mesh; this section is the model along the "
            "line. Open the whole 3D model in the 3D viewer."))
        self._model_3d_btn.clicked.connect(
            lambda: self._model_3d_path and self.viewMeshRequested.emit(self._model_3d_path))
        self._model_3d_row = QWidget()
        model_3d_bar = QHBoxLayout(self._model_3d_row)
        model_3d_bar.setContentsMargins(6, 2, 6, 2)
        model_3d_bar.addStretch(1)
        model_3d_bar.addWidget(self._model_3d_btn)
        self._model_3d_row.setVisible(False)
        model_layout.addWidget(self._model_3d_row)
        model_layout.addWidget(self._model_view, stretch=1)

        self._quality_view = InversionQualityView()

        # The mesh the next run will invert on, built the way the run builds it,
        # with the a-priori zones drawn on it. Rebuilt when the tab is opened
        # after the data or the mesh settings changed, a moment after the last
        # change while it is open, and on request.
        self._mesh_tab = MeshPreviewView()
        self._mesh_tab.rebuildRequested.connect(
            lambda: self._refresh_mesh_preview(force=True))
        # A zone edit rebuilds the mesh while it follows the zone outlines; the
        # two zone options also change what the Inversion panel says.
        self._mesh_tab.zonesChanged.connect(self._mesh_inputs_changed)
        self._mesh_tab.conformChanged.connect(self._mesh_inputs_changed)
        self._mesh_tab.decoupleChanged.connect(self._mesh_inputs_changed)
        self._mesh_preview_key: Optional[tuple] = None      # inputs of the mesh shown
        self._mesh_preview_pending: Optional[tuple] = None  # inputs being built
        self._mesh_worker: Optional[TaskWorker] = None
        self._mesh_timer = QTimer(self)
        self._mesh_timer.setSingleShot(True)
        self._mesh_timer.setInterval(400)
        self._mesh_timer.timeout.connect(self._refresh_mesh_preview)

        # Each reciprocal pair's error against its resistance, with the error
        # model fitted through them: the survey on screen, or every survey of a
        # time-lapse list. Its "Fit to" chooser is the page's one setting for
        # which pairs the model is fitted to - the data errors, the QC report,
        # the settings file and the run's figure all follow it.
        self._recip_view = ReciprocalErrorView()
        self._recip_view.fitToChanged.connect(self._on_error_fit_changed)
        self._recip_view.useRequested.connect(self._use_reciprocal_errors)
        # The loaded survey's pairing, made with it off the UI thread.
        self._loaded_pairing: Optional[Dict[str, Any]] = None
        # Each survey's QC report - its pairing among it - as read for the
        # series view or by the time-lapse QC: {survey key: {filter key:
        # report}} (_recip_survey_key, _recip_qc_key). A long series takes
        # minutes to read, so it is read once per file and filter.
        self._recip_cache: Dict[tuple, Dict[str, Dict[str, Any]]] = {}
        self._recip_worker: Optional[TaskWorker] = None
        self._recip_reading: Optional[tuple] = None
        self._recip_timer = QTimer(self)
        self._recip_timer.setSingleShot(True)
        self._recip_timer.setInterval(500)
        self._recip_timer.timeout.connect(self._refresh_recip_view)

        # The data come first, loaded beside their pseudosection, so a series
        # is clicked through without switching tabs for every survey. The
        # electrodes are drawn along the top of the pseudosection and on the
        # Mesh tab, and summed up in the data panel.
        self._tabs.addTab(self._pseudo_widget, QCoreApplication.translate("PHGX", "Data"))
        self._tabs.addTab(self._recip_view, QCoreApplication.translate("PHGX", "Reciprocal errors"))
        self._tabs.addTab(self._mesh_tab, QCoreApplication.translate("PHGX", "Mesh"))
        self._tabs.addTab(model_tab, QCoreApplication.translate("PHGX", "Resistivity model"))
        self._tabs.addTab(self._quality_view, QCoreApplication.translate("PHGX", "Inversion quality"))
        self._tabs.currentChanged.connect(self._on_tab_changed)
        self._reproduce = ReproduceBar()
        center = QWidget()
        center_layout = QVBoxLayout(center)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.addWidget(self._tabs, stretch=1)
        center_layout.addWidget(self._reproduce)
        root.addWidget(center, stretch=1)
        self._controls = self._build_controls()
        self._sync_recip_use()
        root.addWidget(self._controls)
        self._sync_tab_controls()

    # -- controls ------------------------------------------------------------
    def _build_controls(self) -> QWidget:
        # Vertical scrolling only, so the column must never be narrower than its
        # widest row: 450-500 px is the preferred width, and the column widens
        # past it when the content needs more - a fixed 500 px would cut the
        # file-list buttons and hint off at the right edge when the font is
        # wider than the one it was sized with.
        scroll = ContentWidthScrollArea(minimum=450, maximum=500)
        panel = QWidget()
        scroll.setWidget(panel)
        layout = QVBoxLayout(panel)

        loader = QGroupBox(QCoreApplication.translate("PHGX", "Load resistivity data"))
        self._load_group = loader
        lform = QFormLayout(loader)

        # One survey or a series is the first thing settled: it decides what
        # the list below is for and which Run button the column ends with, so
        # it sits above that list, not in the Run group at the bottom.
        # Two joined buttons, the chosen one filled (theme: QPushButton[segment]);
        # as radio buttons the choice shows as a lone dot, easy to misread.
        self._single_mode = QPushButton(QCoreApplication.translate("PHGX", "One survey"))
        self._single_mode.setIcon(theme.icon("fa5s.file-alt"))
        self._single_mode.setToolTip(
            QCoreApplication.translate("PHGX", "Invert the survey selected in the list - the one on the Data tab."))
        self._tl_mode = QPushButton(QCoreApplication.translate("PHGX", "Time-lapse series"))
        self._tl_mode.setIcon(theme.icon("fa5s.layer-group"))
        self._tl_mode.setToolTip(
            QCoreApplication.translate("PHGX", "Invert every survey in the list together, in list order: the first is "
            "the baseline, and each later one is compared with the one before it. "
            "The time-lapse options appear below the inversion settings."))
        self._run_kind = QButtonGroup(self)      # exclusive: one is always chosen
        for place, button in (("first", self._single_mode), ("last", self._tl_mode)):
            button.setCheckable(True)
            button.setProperty("segment", place)
            button.setCursor(Qt.PointingHandCursor)
            self._run_kind.addButton(button)
        self._single_mode.setChecked(True)
        self._tl_mode.toggled.connect(self._on_tl_mode)
        kind_row = QHBoxLayout()
        kind_row.setContentsMargins(0, 0, 0, 0)
        kind_row.setSpacing(0)
        kind_row.addWidget(self._single_mode)
        kind_row.addWidget(self._tl_mode)
        kind_row.addStretch(1)
        lform.addRow(QCoreApplication.translate("PHGX", "Invert as"), kind_row)

        self._instrument = QComboBox()
        for label, value in _INSTRUMENTS:
            self._instrument.addItem(i18n.tr(label), value)
        # Don't let the longest item ("BERT / Unified (.ohm/.dat)") force the whole
        # control panel wide; elide in the closed box (full text in the dropdown).
        self._instrument.setSizeAdjustPolicy(QComboBox.AdjustToMinimumContentsLengthWithIcon)
        self._instrument.setMinimumContentsLength(12)
        # A time-lapse run reads its first survey with this reader to build the
        # mesh, and so does the Mesh tab's preview of it; the Reciprocal errors
        # tab reads a series' surveys with it.
        self._instrument.currentIndexChanged.connect(self._mesh_inputs_changed)
        self._instrument.currentIndexChanged.connect(self._recip_inputs_changed)
        self._resipy_ready = QLabel()
        self._resipy_ready.setWordWrap(False)
        instrument_row = QHBoxLayout()
        instrument_row.setSpacing(8)
        instrument_row.addWidget(self._instrument, stretch=1)
        instrument_row.addWidget(self._resipy_ready)
        lform.addRow(QCoreApplication.translate("PHGX", "Instrument / format"), instrument_row)

        # Which reader handled the file is not visible in the result, and the two
        # do not always agree on how many measurements a file holds, so it is
        # stated rather than left to the log.
        self._reader_status = QLabel()
        theme.set_tone(self._reader_status, "hint")
        self._reader_status.setWordWrap(True)
        lform.addRow("", self._reader_status)
        self._show_reader_status()

        # A file whose first lines name another format than the one chosen,
        # said beside the chooser with the switch one click away. Never made
        # on its own: the guess reads a few header lines, and an automatic
        # choice has a cost - pygimli's own reader reads a DAS-1 file as one
        # electrode and one reading without a word.
        self._format_guess: Optional[Tuple[str, str]] = None   # (format, file)
        self._format_hint = QWidget()
        hint_row = QHBoxLayout(self._format_hint)
        hint_row.setContentsMargins(0, 0, 0, 0)
        self._format_hint_text = QLabel()
        self._format_hint_text.setWordWrap(True)
        theme.set_tone(self._format_hint_text, "warn")
        self._format_hint_btn = QPushButton()
        self._format_hint_btn.clicked.connect(self._take_format_hint)
        hint_row.addWidget(self._format_hint_text, 1)
        hint_row.addWidget(self._format_hint_btn)
        self._format_hint.setVisible(False)
        lform.addRow(i18n.tr(self._format_hint))
        # Changing the format by hand reads the survey on screen again with it.
        self._instrument.activated.connect(self._reload_with_format)

        self._tl_list = QListWidget()
        self._tl_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self._tl_list.setMaximumHeight(150)
        self._tl_list.setToolTip(QCoreApplication.translate("PHGX", "Click a row to preview it. Each file is one time step; "
                                 "the list runs from earliest at the top to latest at the bottom. "
                                 "Use Sort by time to order the sequence."))
        self._tl_list.itemSelectionChanged.connect(self._on_tl_selection_changed)
        self._tl_list.itemClicked.connect(self._preview_tl_item)
        lform.addRow(i18n.tr(self._tl_list))

        tl_btns = QHBoxLayout()
        add_btn = QPushButton(QCoreApplication.translate("PHGX", "Add files…"))
        add_btn.setToolTip(QCoreApplication.translate("PHGX", "Add one or more ERT files, one per survey for time-lapse. "
                           "Choose the instrument / format first."))
        add_btn.setProperty("primary", True)
        add_btn.setIcon(theme.icon("fa5s.file-import", color="#ffffff"))
        add_btn.clicked.connect(self._add_tl_files)
        rm_btn = QPushButton(QCoreApplication.translate("PHGX", "Remove")); rm_btn.setIcon(theme.icon("fa5s.minus"))
        rm_btn.clicked.connect(self._remove_tl_files)
        up_btn = QPushButton("↑"); up_btn.setToolTip(QCoreApplication.translate("PHGX", "Move selected up")); up_btn.setMaximumWidth(34)
        up_btn.clicked.connect(lambda: self._move_tl_files(-1))
        down_btn = QPushButton("↓"); down_btn.setToolTip(QCoreApplication.translate("PHGX", "Move selected down")); down_btn.setMaximumWidth(34)
        down_btn.clicked.connect(lambda: self._move_tl_files(1))
        sort_btn = QPushButton(QCoreApplication.translate("PHGX", "Sort by time")); sort_btn.setIcon(theme.icon("fa5s.clock"))
        sort_btn.setToolTip(
            QCoreApplication.translate("PHGX", "Put the files in acquisition order, using the times read from their "
            "names or headers. A time-lapse inversion compares each survey with "
            "the one before it, so the order is part of the result."))
        sort_btn.clicked.connect(self._sort_tl_files_by_time)
        clr_btn = QPushButton(QCoreApplication.translate("PHGX", "Clear")); clr_btn.setIcon(theme.icon("fa5s.trash"))
        clr_btn.clicked.connect(self._clear_tl_files)
        # Two rows rather than one: all six in a row would be the widest thing in
        # the column. Adding and removing files on top, ordering them below.
        for b in (add_btn, rm_btn, clr_btn):
            tl_btns.addWidget(b)
        lform.addRow(i18n.tr(tl_btns))
        order_btns = QHBoxLayout()
        for b in (up_btn, down_btn, sort_btn):
            order_btns.addWidget(b)
        order_btns.addStretch(1)
        lform.addRow(i18n.tr(order_btns))

        self._tl_info = QLabel(QCoreApplication.translate("PHGX", "No files added.")); self._tl_info.setWordWrap(True)
        # The accepted time formats on hover, so the line itself stays short.
        self._tl_info.setToolTip(i18n.tr(_TIME_FORMATS_TIP))
        lform.addRow(i18n.tr(self._tl_info))

        # The escape hatch for files whose names and headers carry no time, under
        # the line that says which files those are, and only while there are
        # some.
        self._tl_use_mtime = QCheckBox(QCoreApplication.translate("PHGX", "Date undated files by when they were last saved"))
        self._tl_use_mtime.setToolTip(
            QCoreApplication.translate("PHGX", "Use each file's last-modified time as its acquisition time when neither "
            "its name nor its header gives one. Off by default: a file that was copied "
            "or re-exported carries the time of the copy, not of the survey."))
        self._tl_use_mtime.toggled.connect(self._on_tl_time_source_changed)
        self._tl_use_mtime.setVisible(False)
        lform.addRow(i18n.tr(self._tl_use_mtime))

        # Shown only when names in the list look like forward/reciprocal halves,
        # and on then: the detection goes by name and time, so it can be wrong,
        # and unticking it puts every file back as a survey of its own.
        self._tl_pair_box = QCheckBox(QCoreApplication.translate("PHGX", "Pair reciprocal files with their forward file"))
        self._tl_pair_box.setChecked(True)
        self._tl_pair_box.setToolTip(
            QCoreApplication.translate("PHGX", "Some instruments write each survey as two files: the forward readings, "
            "and a few minutes later the reciprocal readings (“recip” in the name). "
            "Ticked, each reciprocal file is joined to the forward file measured just "
            "before it with the same name, and the two are one survey: one row in "
            "the list, at the forward file's time, one time step, and the readings "
            "of both in one data set, so each reading can be compared with its "
            "reciprocal.\n\n"
            "A forward file with no reciprocal stays a survey on its own. A "
            "reciprocal file with no forward file is left out, and the line above "
            "names it.\n\n"
            "Untick it if a file was joined to the wrong partner: every file is "
            "then a survey of its own again."))
        self._tl_pair_box.toggled.connect(self._on_tl_pairing_changed)
        self._tl_pair_box.setVisible(False)
        lform.addRow(i18n.tr(self._tl_pair_box))

        load_e = QPushButton(QCoreApplication.translate("PHGX", "Electrode file (optional)…"))
        load_e.setIcon(theme.icon("fa5s.folder-open"))
        load_e.clicked.connect(self._load_electrodes)
        fmt_btn = QPushButton(QCoreApplication.translate("PHGX", "Data format"))
        fmt_btn.setIcon(theme.icon("fa5s.file-alt"))
        fmt_btn.setToolTip(QCoreApplication.translate("PHGX", "The file formats this page reads, the electrode file, and "
                           "how to give each survey its time."))
        fmt_btn.clicked.connect(self._show_format_help)
        elec_row = QHBoxLayout()
        elec_row.addWidget(load_e)
        elec_row.addWidget(fmt_btn)
        lform.addRow(i18n.tr(elec_row))
        layout.addWidget(loader)

        self._info = QLabel(QCoreApplication.translate("PHGX", "No data loaded."))
        self._info.setWordWrap(True)
        layout.addWidget(self._info)

        qc = QGroupBox(QCoreApplication.translate("PHGX", "Data QC / filter"))
        self._qc_group = qc
        qform = QFormLayout(qc)
        # Check 0, before every other check.
        # Off by default: kept apart, the two readings of a pair let the fit see
        # how far they disagree, and an averaged pair hides that.
        self._qc_average = QCheckBox(QCoreApplication.translate("PHGX", "Average each reading with its reciprocal"))
        self._qc_average.setChecked(False)
        self._qc_average.setEnabled(False)
        self._qc_average.setToolTip(QCoreApplication.translate("PHGX", "Load ERT data first."))
        self._qc_average.toggled.connect(self._sync_error_rows)
        qform.addRow(i18n.tr(self._qc_average))
        self._rmin = PlainDoubleSpinBox(); self._rmin.setRange(0.0, 1e6); self._rmin.setValue(0.0); self._rmin.setSuffix(" Ω·m")
        self._rmax = PlainDoubleSpinBox(); self._rmax.setRange(1.0, 1e7); self._rmax.setValue(100000.0); self._rmax.setSuffix(" Ω·m")
        self._max_err = PlainDoubleSpinBox(); self._max_err.setRange(0.0, 100.0)
        self._max_err.setValue(_QC_DEFAULTS["max_error"]); self._max_err.setSuffix(" %")
        self._max_err.setToolTip(
            QCoreApplication.translate("PHGX", "Drop measurements with relative error above this (0 = off). 20 % drops "
            "the readings a file's own error column calls noisy; a file with none of "
            "its own carries the 5 % assumed for every reading, and loses nothing."))
        qform.addRow(QCoreApplication.translate("PHGX", "Min ρa"), self._rmin)
        qform.addRow(QCoreApplication.translate("PHGX", "Max ρa"), self._rmax)
        qform.addRow(QCoreApplication.translate("PHGX", "Max error"), self._max_err)

        # The rest of the criteria are folded away, because which of them a file
        # can even support varies by instrument: voltage and current come with
        # some formats and not others, and a reciprocal error needs the survey to
        # contain reciprocal pairs at all. Each row is enabled against the loaded
        # data in _refresh_qc_availability, so an unusable one says why rather
        # than filtering on a field that is not there.
        self._qc_more = QGroupBox(QCoreApplication.translate("PHGX", "More checks"))
        self._qc_more.setCheckable(True)
        self._qc_more.setChecked(False)
        self._qc_more.setToolTip(
            QCoreApplication.translate("PHGX", "Extra QC criteria. They stay folded because most surveys need none of "
            "them, and the ones a given file cannot support are disabled with the "
            "reason in their tooltip."))
        more_outer = QVBoxLayout(self._qc_more)
        more_outer.setContentsMargins(0, 0, 0, 0)
        self._qc_more_body = QWidget()
        mform = QFormLayout(self._qc_more_body)
        mform.setContentsMargins(0, 6, 0, 0)

        self._qc_drop_neg = QCheckBox(QCoreApplication.translate("PHGX", "Drop ρa ≤ 0"))
        self._qc_drop_neg.setChecked(_QC_DEFAULTS["drop_nonpositive"])
        self._qc_drop_neg.setToolTip(
            QCoreApplication.translate("PHGX", "A non-positive apparent resistivity is a polarity or geometry error "
            "rather than a measurement, and the inversion cannot use it. On with "
            "More checks. Min ρa above already removes negatives once it is set "
            "above zero."))
        mform.addRow(i18n.tr(self._qc_drop_neg))

        # Six decimals, because files that report volts and amperes need floors
        # of a tenth of a millivolt or milliampere; three decimals would silently
        # turn 0.0001 into 0, which switches the check off.
        self._qc_min_v = PlainDoubleSpinBox(); self._qc_min_v.setRange(0.0, 1e6)
        self._qc_min_v.setDecimals(6); self._qc_min_v.setValue(_QC_DEFAULTS["min_voltage"])
        mform.addRow(QCoreApplication.translate("PHGX", "Min |V|"), self._qc_min_v)

        self._qc_min_i = PlainDoubleSpinBox(); self._qc_min_i.setRange(0.0, 1e6)
        self._qc_min_i.setDecimals(6); self._qc_min_i.setValue(_QC_DEFAULTS["min_current"])
        mform.addRow(QCoreApplication.translate("PHGX", "Min |I|"), self._qc_min_i)

        # |k| scales with the electrode spacing - from a few hundred m on a short
        # surface line to tens of thousands of m on a large survey - so no one
        # number suits every survey. Until it is set by hand the cap follows each
        # file loaded, at a multiple of its median (_refresh_qc_availability).
        self._qc_max_k_follows_file = True
        self._qc_max_k = PlainDoubleSpinBox(); self._qc_max_k.setRange(0.0, 1e9)
        self._qc_max_k.setDecimals(0); self._qc_max_k.setValue(0.0)
        self._qc_max_k.setToolTip(
            QCoreApplication.translate("PHGX", "Drop configurations whose geometric factor exceeds this (0 = off). A large "
            "|k| multiplies the measured resistance, and its noise with it, which is how "
            "a clean-looking rhoa outlier is produced by geometry rather than by ground. "
            "Set from the file once one is loaded."))
        self._qc_max_k.valueChanged.connect(self._max_k_set_by_hand)
        mform.addRow(QCoreApplication.translate("PHGX", "Max |k|"), self._qc_max_k)

        self._qc_max_rc = PlainDoubleSpinBox(); self._qc_max_rc.setRange(0.0, 1e9)
        self._qc_max_rc.setDecimals(0); self._qc_max_rc.setValue(_QC_DEFAULTS["max_contact_r"])
        self._qc_max_rc.setSuffix(" Ω")
        mform.addRow(QCoreApplication.translate("PHGX", "Max contact R"), self._qc_max_rc)

        # Percent, like the reciprocal error below it, though the spread can run
        # to thousands of percent on a failing electrode.
        self._qc_max_stack = PlainDoubleSpinBox(); self._qc_max_stack.setRange(0.0, 1e6)
        self._qc_max_stack.setDecimals(1); self._qc_max_stack.setValue(_QC_DEFAULTS["max_stack"])
        self._qc_max_stack.setSuffix(" %")
        self._qc_max_stack.setToolTip(
            QCoreApplication.translate("PHGX", "Drop readings whose potential scattered by more than this across its own "
            "samples, as a percentage of the potential (0 = off). Subsurface Insights "
            "records it. A few percent is normal; hundreds of percent is an electrode "
            "or a contact failing."))
        mform.addRow(QCoreApplication.translate("PHGX", "Max stacking spread"), self._qc_max_stack)

        self._qc_max_recip = PlainDoubleSpinBox(); self._qc_max_recip.setRange(0.0, 100.0)
        self._qc_max_recip.setDecimals(2); self._qc_max_recip.setValue(_QC_DEFAULTS["max_reciprocal"])
        self._qc_max_recip.setSuffix(" %")
        mform.addRow(QCoreApplication.translate("PHGX", "Max recip. error"), self._qc_max_recip)

        self._qc_support_note = QLabel(QCoreApplication.translate("PHGX", "Load data to see which checks are available."))
        self._qc_support_note.setWordWrap(True)
        theme.set_tone(self._qc_support_note, "hint")
        mform.addRow(i18n.tr(self._qc_support_note))

        more_outer.addWidget(self._qc_more_body)
        self._qc_more_body.setVisible(False)
        self._qc_more.toggled.connect(self._qc_more_body.setVisible)
        qform.addRow(i18n.tr(self._qc_more))

        qrow = QHBoxLayout()
        apply_btn = QPushButton(QCoreApplication.translate("PHGX", "Apply filter"))
        apply_btn.setIcon(theme.icon("fa5s.filter"))
        apply_btn.clicked.connect(self._apply_filter)
        reset_btn = QPushButton(QCoreApplication.translate("PHGX", "Reset"))
        reset_btn.setIcon(theme.icon("fa5s.undo"))
        reset_btn.clicked.connect(self._reset_filter)
        qrow.addWidget(apply_btn); qrow.addWidget(reset_btn)
        qform.addRow(i18n.tr(qrow))
        layout.addWidget(qc)

        # The inversion controls are split three ways: what defines the run, how
        # the data are weighted, and what the software is allowed to change on its
        # own. Everything configurable comes before the Run button at the bottom.
        # λ / iterations / errors / mesh quality are shared by single and
        # time-lapse inversion; choosing "Time-lapse series" reveals the
        # time-lapse-only options and swaps the Run button.
        inv = QGroupBox(QCoreApplication.translate("PHGX", "Inversion"))
        self._inversion_group = inv
        iform = QFormLayout(inv)
        self._inv_form = iform

        # Mode comes first because it overrides several controls below it. The
        # split is by cost: the geometric-factor check is one extra forward run,
        # and the auto-λ search is a full inversion per trial.
        self._inv_mode = QComboBox()
        # Named for what each does, so the label says which checks Thorough adds.
        for label, value in (("Quick: invert only", "quick"),
                             ("Thorough: check k, search λ", "full")):
            self._inv_mode.addItem(i18n.tr(label), value)
        self._inv_mode.setToolTip(
            QCoreApplication.translate("PHGX", "Quick runs the inversion and nothing else, which is the shorter run "
            "while λ and the mesh are still being settled.\n\n"
            "Thorough adds the two stages Quick drops. It checks the geometric factors "
            "(k) against the mesh, repairing them when they disagree, and it searches "
            "λ for the target χ².\n\n"
            "The k check is the one with the most evidence behind it: a wrong k scales "
            "the whole section by a constant and χ² never notices, so a Quick result "
            "that looks perfect can still be uniformly wrong. Re-run Thorough whenever "
            "the resistivities themselves look off, not only when the fit looks bad."))
        self._inv_mode.currentIndexChanged.connect(self._on_inv_mode_changed)
        iform.addRow(QCoreApplication.translate("PHGX", "Mode"), self._inv_mode)

        self._engine = QComboBox()
        for label, value in (("In-house Gauss-Newton", "pyhydro"),
                             ("PyGIMLi ERTManager", "pygimli"),
                             ("ADTLERT 2.5D/3D (CUDA)", "adtlert"),
                             ("E4D 3D (PNNL, external)", "e4d"),
                             ("R2 2D (Binley, external)", "r2"),
                             ("R3t 3D (Binley, external)", "r3t")):
            self._engine.addItem(i18n.tr(label), value)
        self._engine.setToolTip(
            QCoreApplication.translate("PHGX", "Solver. The in-house Gauss-Newton inversion exposes its own stopping rule "
            "and line search, so the fit assistance below drives it directly. The "
            "PyGIMLi manager runs its own loop and is available as a cross-check.\n\n"
            "ADTLERT uses a CUDA-accelerated cuDSS forward solve and GPU CGLS: 2.5D "
            "on a profile, 3D on an imported tetrahedral mesh. A CUDA 12 GPU is "
            "required; cuDSS and NVRTC come with ADTLERT. Windows is supported; Linux "
            "is recommended for the best performance. Pole arrays (remote electrodes) "
            "run too. The controls below remain available when this engine is "
            "selected.\n\n"
            "E4D is PNNL's parallel 3D code, run as an external program under MPI; "
            "it is not installed with PyHydroGeophysX. It runs on Linux, on Windows "
            "only inside WSL 2, and on macOS when built from source. A profile is "
            "inverted in 3D on a mesh built around the line and shown as the "
            "section along it. A time-lapse series runs as E4D's own time-lapse "
            "inversion: the first survey is the baseline, and each later one starts "
            "from the solution before it, with the change from it smoothed.\n\n"
            "R2 (2D profiles) and R3t (3D surveys, or a profile on a 3D mesh around "
            "the line) are Andrew Binley's codes, the ones ResIPy runs; they are found "
            "in an installed ResIPy unless named below. They are Windows programs: "
            "native on Windows, through Wine on Linux and macOS, free for "
            "non-commercial use. Both choose their own smoothing weight at every "
            "iteration, so λ and auto-λ do not apply; they hold fixed zones fixed. A "
            "time-lapse series is their difference inversion against the first survey."))
        self._engine.currentIndexChanged.connect(self._on_engine_changed)
        self._engine.currentIndexChanged.connect(self._sync_mesh_engine)
        iform.addRow(QCoreApplication.translate("PHGX", "Engine"), self._engine)
        self._adtlert_status = QLabel()
        self._adtlert_status.setWordWrap(True)
        self._adtlert_status.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self._adtlert_status.setVisible(False)
        iform.addRow("", self._adtlert_status)
        self._build_e4d_rows(iform)
        self._build_r2_rows(iform)

        self._lam = PlainDoubleSpinBox()
        self._lam.setDecimals(3)
        self._lam.setRange(*_LAMBDA_BOUNDS); self._lam.setValue(50.0)
        self._lam.setStepType(QAbstractSpinBox.StepType.AdaptiveDecimalStepType)
        self._lam.setToolTip(
            QCoreApplication.translate("PHGX", "Spatial regularization strength (smoothness). Lower fits the data harder, higher gives a smoother model. Start on the smooth side: the auto-λ search relaxes downward, continuing each λ from the previous solution, and that direction is the stable one. Values below 1 are allowed; the range is {0:g} to {1:g} and the arrows step by one significant digit.").format(_LAMBDA_BOUNDS[0], _LAMBDA_BOUNDS[1]))
        iform.addRow(QCoreApplication.translate("PHGX", "Lambda"), self._lam)

        # How long an inversion may run, and when it counts as done. Each mode and
        # engine shows only the limits it obeys (_sync_iteration_rows): the three
        # numbers on one line read as one setting, and two of them never applied
        # to a time-lapse run.
        self._iter_ceiling = QSpinBox(); self._iter_ceiling.setRange(5, 400)
        self._iter_ceiling.setValue(60)
        self._iter_ceiling.setToolTip(
            QCoreApplication.translate("PHGX", "The most iterations the inversion may take (for each λ when Auto-λ is "
            "on). It normally stops sooner, once χ² stops improving (next row). "
            "Reaching this limit means the fit could still improve, and the log "
            "says so."))
        iform.addRow(QCoreApplication.translate("PHGX", "Max iterations"), self._iter_ceiling)
        # A single run checks its progress after this many iterations and goes on
        # from its own model while still improving, so λ is never judged on an
        # unfinished descent. That checkpoint is an internal detail there; a
        # time-lapse run has no continuation, and this is its whole limit.
        self._iter = QSpinBox(); self._iter.setRange(2, 60); self._iter.setValue(15)
        self._iter.setToolTip(
            QCoreApplication.translate("PHGX", "The most iterations of the time-lapse inversion; with Windowed on, of "
            "each window."))
        iform.addRow(QCoreApplication.translate("PHGX", "Max iterations"), self._iter)

        self._plateau = PlainDoubleSpinBox()
        self._plateau.setRange(0.01, 10.0); self._plateau.setDecimals(2)
        self._plateau.setSingleStep(0.1); self._plateau.setValue(0.5)
        self._plateau.setPrefix("< ")
        self._plateau.setSuffix(" % per iteration")
        self._plateau.setToolTip(i18n.tr(_PLATEAU_TIP))
        iform.addRow(QCoreApplication.translate("PHGX", "Stop when χ² improves"), self._plateau)

        # The mesh settings live on the Mesh tab, next to the mesh they build;
        # this row says what is set and leads there.
        self._mesh_tab.set_settings_panel(self._build_mesh_settings())
        self._mesh_link = QLabel()
        self._mesh_link.setWordWrap(True)
        self._mesh_link.setTextFormat(Qt.RichText)
        theme.set_tone(self._mesh_link, "hint")
        self._mesh_link.setToolTip(
            QCoreApplication.translate("PHGX", "The mesh, its sizing and what the a-priori zones do to it are set on "
            "the Mesh tab, which draws the mesh the run will invert on."))
        self._mesh_link.linkActivated.connect(
            lambda _link: self._tabs.setCurrentWidget(self._mesh_tab))
        iform.addRow(QCoreApplication.translate("PHGX", "Mesh"), self._mesh_link)
        self._update_mesh_link()
        layout.addWidget(inv)

        # -- data errors -----------------------------------------------------
        errs = QGroupBox(QCoreApplication.translate("PHGX", "Data errors"))
        self._errors_group = errs
        eform = QFormLayout(errs)
        self._err_source = QComboBox()
        for label, value in (("File err column", "file"),
                             ("Estimate from the values below", "estimate"),
                             ("Larger of the two", "max"),
                             ("Stacking spread with the estimate", "stack"),
                             ("From the reciprocal error model", "reciprocal")):
            self._err_source.addItem(i18n.tr(label), value)
        self._err_source.setSizeAdjustPolicy(QComboBox.AdjustToMinimumContentsLengthWithIcon)
        self._err_source.setMinimumContentsLength(16)
        self._err_source.setToolTip(
            QCoreApplication.translate("PHGX", "Where the per-measurement error comes from. Most instruments write an err "
            "column; replacing it with an assumed percentage makes χ² report on an error "
            "model the data never had. The stacking spread is offered for data that "
            "record it, the reciprocal error model for data measured both ways."))
        self._err_source.currentIndexChanged.connect(self._sync_error_rows)
        # The Reciprocal errors tab says whether the next run uses its model.
        self._err_source.currentIndexChanged.connect(self._sync_recip_use)
        eform.addRow(QCoreApplication.translate("PHGX", "Taken from"), self._err_source)

        self._relerr = PlainDoubleSpinBox(); self._relerr.setRange(0.005, 1.0)
        self._relerr.setDecimals(3); self._relerr.setSingleStep(0.01); self._relerr.setValue(0.05)
        self._relerr.setToolTip(
            QCoreApplication.translate("PHGX", "Assumed relative data error, used when estimating and as the fallback where "
            "the file has no usable value."))
        self._abserr = PlainDoubleSpinBox(); self._abserr.setRange(0.0, 100.0)
        self._abserr.setDecimals(4); self._abserr.setSingleStep(0.001); self._abserr.setValue(0.0)
        self._abserr.setSuffix(" Ω")
        self._abserr.setToolTip(
            QCoreApplication.translate("PHGX", "Absolute resistance error, added as absolute/|R|. It raises the error bar on "
            "weak readings, which is where a flat percentage is most optimistic. Leave at "
            "0 when the survey spans a narrow signal range."))
        # Laid out as the formula it is, so the two numbers read as one model
        # rather than as two unrelated settings.
        err_row = QHBoxLayout()
        err_row.setContentsMargins(0, 0, 0, 0)
        err_row.addWidget(self._relerr)
        err_row.addWidget(QLabel("+"))
        err_row.addWidget(self._abserr)
        err_row.addWidget(QLabel("/ |R|"))
        err_row.addStretch(1)
        self._errmodel_row = QWidget(); self._errmodel_row.setLayout(err_row)
        eform.addRow(QCoreApplication.translate("PHGX", "Estimate"), self._errmodel_row)

        # The smallest error a reciprocal can give a reading. 1 %: what the
        # in-house and ADTLERT time-lapse engines take as their own minimum, so
        # the errors recorded are the errors used; and a pair that agrees to a
        # tenth of a percent still shares every error that cannot differ
        # between its two directions.
        self._recip_floor = PlainDoubleSpinBox()
        self._recip_floor.setRange(0.1, 20.0); self._recip_floor.setDecimals(1)
        self._recip_floor.setSingleStep(0.5); self._recip_floor.setValue(1.0)
        self._recip_floor.setSuffix(" %")
        self._recip_floor.setToolTip(
            QCoreApplication.translate("PHGX", "No reading is given a smaller error than this when its error comes from "
            "reciprocals: the error model, or an averaged pair's own difference. Two "
            "directions that agree closely still share the errors that cannot differ "
            "between them - the electrode positions, the 2-D assumption - so a "
            "near-perfect pair is not an error-free reading. 1 % is also the smallest "
            "error the in-house and ADTLERT time-lapse inversions accept. Averaged pairs "
            "take it when Apply filter averages them; the model takes it when the "
            "inversion runs."))
        eform.addRow(QCoreApplication.translate("PHGX", "Minimum"), self._recip_floor)
        self._refresh_error_sources(None)
        # Data errors are settled before the inversion is, so the group sits
        # between the QC and the inversion settings: load, QC, errors, invert.
        layout.insertWidget(layout.indexOf(inv), errs)

        # -- fit assistance --------------------------------------------------
        assist = QGroupBox(QCoreApplication.translate("PHGX", "Fit assistance"))
        self._fit_group = assist
        aform = QFormLayout(assist)

        # Kept short enough to fit the panel; the tooltip carries the detail.
        self._auto_lam = QCheckBox(QCoreApplication.translate("PHGX", "Auto-λ: re-invert to reach target χ²"))
        # Off in Quick, which is the default mode; Full turns it back on.
        self._auto_lam.setChecked(False)
        self._auto_lam.setToolTip(
            QCoreApplication.translate("PHGX", "The inversion at the λ above always runs first and is always kept. If its χ² "
            "misses the target band, the same mesh is re-inverted at other λ values "
            "(bracket, then bisect in log λ) and the closest one becomes the displayed "
            "model. Each trial continues from the nearest λ already solved rather than "
            "restarting, so the later ones are cheap, but every trial is still a full "
            "inversion."))
        self._auto_lam.toggled.connect(self._on_auto_lambda)
        aform.addRow(i18n.tr(self._auto_lam))

        self._target_chi2 = PlainDoubleSpinBox()
        self._target_chi2.setRange(0.1, 100.0); self._target_chi2.setDecimals(2)
        self._target_chi2.setSingleStep(0.1); self._target_chi2.setValue(1.0)
        self._target_chi2.setToolTip(
            QCoreApplication.translate("PHGX", "χ² = 1 means the model explains the data to within the assumed relative "
            "error. A larger target accepts a looser fit, matching data noisier than "
            "the error estimate describes."))
        self._chi2_tol = PlainDoubleSpinBox()
        self._chi2_tol.setRange(0.01, 10.0); self._chi2_tol.setDecimals(2)
        self._chi2_tol.setSingleStep(0.05); self._chi2_tol.setValue(0.2)
        self._chi2_tol.setToolTip(
            QCoreApplication.translate("PHGX", "Half-width of the accepted band. The search stops as soon as a trial lands "
            "inside target ± tolerance."))
        chi_row = QHBoxLayout()
        chi_row.addWidget(self._target_chi2)
        chi_row.addWidget(QLabel("±")); chi_row.addWidget(self._chi2_tol)
        chi_row.addStretch(1)
        self._chi2_row = QWidget(); self._chi2_row.setLayout(chi_row)
        chi_row.setContentsMargins(0, 0, 0, 0)
        aform.addRow(QCoreApplication.translate("PHGX", "Target χ²"), self._chi2_row)

        self._lam_trials = QSpinBox(); self._lam_trials.setRange(1, 20); self._lam_trials.setValue(6)
        self._lam_trials.setToolTip(
            QCoreApplication.translate("PHGX", "Upper bound on the extra inversions the λ search may run, on top of the "
            "first one at the λ set above. Reached only when the target stays out of "
            "range."))
        aform.addRow(QCoreApplication.translate("PHGX", "Max λ trials"), self._lam_trials)

        self._reject = QCheckBox(QCoreApplication.translate("PHGX", "Reject outliers: drop data the model cannot explain"))
        self._reject.setChecked(False)
        self._reject.setToolTip(
            QCoreApplication.translate("PHGX", "After the inversion converges, the measurements whose residual exceeds "
            "the threshold below are dropped and the inversion runs again. This "
            "addresses a high χ² caused by individual bad readings rather than by the "
            "model.\n\n"
            "It also shrinks the dataset; the floor below bounds how much can be "
            "removed."))
        self._reject.toggled.connect(self._on_reject_outliers)
        aform.addRow(i18n.tr(self._reject))

        self._reject_sigma = PlainDoubleSpinBox()
        self._reject_sigma.setRange(1.5, 20.0); self._reject_sigma.setDecimals(1)
        self._reject_sigma.setSingleStep(0.5); self._reject_sigma.setValue(3.0)
        self._reject_sigma.setToolTip(
            QCoreApplication.translate("PHGX", "Rejection cut in units of the assumed error. A datum at 3 means the model "
            "misses it by three times its own error bar."))
        self._reject_passes = QSpinBox(); self._reject_passes.setRange(1, 5)
        self._reject_passes.setValue(2)
        self._reject_passes.setToolTip(
            QCoreApplication.translate("PHGX", "How many reject-and-re-invert cycles to run. Each pass is a full inversion."))
        rej_row = QHBoxLayout()
        rej_row.setContentsMargins(0, 0, 0, 0)
        rej_row.addWidget(self._reject_sigma)
        rej_row.addWidget(QLabel(QCoreApplication.translate("PHGX", "σ, passes"))); rej_row.addWidget(self._reject_passes)
        rej_row.addStretch(1)
        self._reject_row = QWidget(); self._reject_row.setLayout(rej_row)
        aform.addRow(QCoreApplication.translate("PHGX", "Cut beyond"), self._reject_row)

        self._min_keep = PlainDoubleSpinBox()
        self._min_keep.setRange(10.0, 100.0); self._min_keep.setDecimals(0)
        self._min_keep.setSingleStep(5.0); self._min_keep.setValue(50.0)
        self._min_keep.setSuffix(" %")
        self._min_keep.setToolTip(
            QCoreApplication.translate("PHGX", "Rejection stops before it would leave less than this share of the "
            "measurements. A χ² bought by deleting most of the survey is not a fit."))
        aform.addRow(QCoreApplication.translate("PHGX", "Keep at least"), self._min_keep)
        layout.addWidget(assist)

        # The time-lapse options, after the settings they add to; shown in
        # time-lapse mode on the tabs that show the inversion settings.
        layout.addWidget(self._build_timelapse_panel())
        self._sync_iteration_rows()
        # Reflect the initial checkbox states; setChecked() above emitted nothing.
        self._on_inv_mode_changed()
        self._on_auto_lambda(self._auto_lam.isChecked())
        self._on_reject_outliers(self._reject.isChecked())

        # Electrode editing has no panel. The operations are agent actions
        # (add/move/delete/label/clear/list electrodes), which are more precise
        # and reproducible than placing electrodes by mouse. The electrode file
        # and the survey geometry are exported from the toolbar's Export menu.

        # Result exports belong beside the result, where model post-processing
        # remains available without retaining the entire preparation column -
        # the single model's or the series', whichever the tab shows.
        self._model_export_btn = QPushButton(QCoreApplication.translate("PHGX", "Export resistivity model…"))
        self._model_export_btn.setIcon(theme.icon("fa5s.cube"))
        self._model_export_btn.setToolTip(QCoreApplication.translate("PHGX", "Export the inverted model as npy + pygimli mesh (.bms) + VTK."))
        self._model_export_btn.setEnabled(False)
        self._model_export_btn.clicked.connect(self._export_resistivity_model)
        self._tl_export_btn = QPushButton(QCoreApplication.translate("PHGX", "Export time-lapse results…"))
        self._tl_export_btn.setIcon(theme.icon("fa5s.cube"))
        self._tl_export_btn.setToolTip(QCoreApplication.translate("PHGX", "Saves the time-lapse models to a chosen folder: a combined VTK, "
                                       "per-step VTKs, final_models.npy, the mesh (.bms), times CSV, and the figure."))
        self._tl_export_btn.setEnabled(False)
        self._tl_export_btn.clicked.connect(self._export_tl_results)
        self._tl_open = QPushButton(QCoreApplication.translate("PHGX", "Open output folder"))
        self._tl_open.setIcon(theme.icon("fa5s.folder-open"))
        self._tl_open.setEnabled(False)
        self._tl_open.clicked.connect(self._open_tl_output)
        self._model_export_group = QGroupBox(QCoreApplication.translate("PHGX", "Export model"))
        model_exports = QVBoxLayout(self._model_export_group)
        model_exports.addWidget(self._model_export_btn)
        model_exports.addWidget(self._tl_export_btn)
        model_exports.addWidget(self._tl_open)
        model_exports.addWidget(self.map_export_button())
        self._postprocess_layout.addWidget(self._model_export_group)
        self._postprocess_layout.addStretch(1)
        self._sync_model_exports()
        self._postprocess_scroll.fit_to_content()

        layout.addStretch(1)
        scroll.fit_to_content()
        self._controls_scroll = scroll

        # -- run: pinned under the column ------------------------------------
        # The column is longer than a screen once a series and its options are
        # in it, and a Run button at its end would scroll out of sight. It
        # stays pinned below the settings, with what still stops it from
        # running said above it.
        footer = QWidget()
        self._run_group = footer
        flayout = QVBoxLayout(footer)
        flayout.setContentsMargins(6, 4, 6, 6)
        flayout.setSpacing(6)
        rule = QFrame()
        rule.setFrameShape(QFrame.HLine)
        rule.setFrameShadow(QFrame.Plain)
        flayout.addWidget(rule)
        self._run_reason = QLabel()
        self._run_reason.setWordWrap(True)
        theme.set_tone(self._run_reason, "hint")
        flayout.addWidget(self._run_reason)

        self._invert_btn = QPushButton(QCoreApplication.translate("PHGX", "Run inversion"))
        self._invert_btn.setProperty("primary", True)
        self._invert_btn.setIcon(theme.icon("fa5s.play", color="#ffffff"))
        self._invert_btn.clicked.connect(self._run_inversion)
        flayout.addWidget(self._invert_btn)
        self._inv_progress = QProgressBar()
        self._inv_progress.setVisible(False)
        self._inv_stop = self.stop_button()
        self._inv_progress_row = progress_with_stop(self._inv_progress, self._inv_stop)
        flayout.addWidget(self._inv_progress_row)

        self._tl_btn = QPushButton(QCoreApplication.translate("PHGX", "Run time-lapse inversion"))
        self._tl_btn.setProperty("primary", True)
        self._tl_btn.setIcon(theme.icon("fa5s.history", color="#ffffff"))
        self._tl_btn.clicked.connect(self._run_timelapse)
        flayout.addWidget(self._tl_btn)
        self._tl_progress = QProgressBar(); self._tl_progress.setVisible(False)
        self._tl_stop = self.stop_button("The time-lapse inversion")
        self._tl_progress_row = progress_with_stop(self._tl_progress, self._tl_stop)
        flayout.addWidget(self._tl_progress_row)

        column = QWidget()
        column_layout = QVBoxLayout(column)
        column_layout.setContentsMargins(0, 0, 0, 0)
        column_layout.setSpacing(0)
        column_layout.addWidget(scroll, 1)
        column_layout.addWidget(footer)
        self._show_run_buttons(False)
        self._sync_run_ready()
        return column
