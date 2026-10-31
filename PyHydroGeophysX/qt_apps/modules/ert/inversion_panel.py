"""The ERT page: the inversion: settings, the E4D and R2/R3t engines, single-survey runs (plan M4.5).

Part of :class:`~.page.ERTProcessingModule`, split from the former
``ert_processing.py`` by area; the methods are unchanged.
"""

from __future__ import annotations

from .common import (
    Any,
    ArtifactRef,
    BusyStateController,
    Dict,
    List,
    Optional,
    Path,
    ProcessProbeWorker,
    ProcessWorkflowWorker,
    QComboBox,
    QCoreApplication,
    QFileDialog,
    QFormLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QTimer,
    Qt,
    Tuple,
    WorkflowRunResult,
    WorkflowSpec,
    export_workflow_bundle,
    i18n,
    io_utils,
    merged_row,
    np,
    save_edited_ert_container,
    survey_timing,
    theme,
)


class _InversionPanel:

    # -- E4D -----------------------------------------------------------------
    _E4D_KEYS = {"launcher": "ert/e4d/launcher", "executable": "ert/e4d/executable",
                 "processes": "ert/e4d/processes"}

    def _build_e4d_rows(self, form: QFormLayout) -> None:
        """How E4D is reached: shown only while E4D is the engine.

        E4D is an external program, so where it is - this computer, WSL, or
        nowhere, in which case the run folder is written for elsewhere - is the
        first thing the page says about it. The choices are kept between
        sessions, since they describe the machine rather than the survey.
        """
        from PySide6.QtCore import QSettings

        saved = QSettings("PyHydroGeophysX", "Studio")
        self._e4d_launcher = QComboBox()
        for label, value in (("Auto (this computer, then WSL)", "auto"),
                             ("This computer", "local"),
                             ("WSL (Windows)", "wsl"),
                             ("Write files only", "files")):
            self._e4d_launcher.addItem(i18n.tr(label), value)
        index = self._e4d_launcher.findData(str(saved.value(self._E4D_KEYS["launcher"], "auto")))
        self._e4d_launcher.setCurrentIndex(max(index, 0))
        self._e4d_launcher.setToolTip(
            QCoreApplication.translate("PHGX", "Where E4D runs. E4D is built from source (github.com/pnnl/E4D) with "
            "gfortran, PETSc and MPI, for Linux.\n\n"
            "This computer: Linux, or macOS with a source build; e4d and mpirun are "
            "found on PATH, through PYHYDRO_E4D / PYHYDRO_MPIRUN, or from the program "
            "given below.\n"
            "WSL: on Windows, E4D built inside a WSL 2 Linux distribution; the "
            "program below is then a Linux path. E4D has no Windows build of its own.\n"
            "Write files only: the complete E4D run folder is written and the run "
            "stops, for a cluster or another machine: run mpirun -np N e4d in it, "
            "then read it back with inversion.e4d.read_e4d_run."))
        form.addRow(QCoreApplication.translate("PHGX", "Run E4D"), self._e4d_launcher)
        self._e4d_program = QLineEdit(str(saved.value(self._E4D_KEYS["executable"], "")))
        self._e4d_program.setPlaceholderText(QCoreApplication.translate("PHGX", "e4d on PATH"))
        self._e4d_program.setToolTip(
            QCoreApplication.translate("PHGX", "The e4d program, when it is not on PATH: a path on this computer, or a "
            "Linux path for WSL. Leave empty to use PATH or PYHYDRO_E4D."))
        browse = QPushButton("…")
        browse.setMaximumWidth(32)
        browse.setToolTip(QCoreApplication.translate("PHGX", "Choose the e4d program on this computer."))
        browse.clicked.connect(self._browse_e4d)
        self._e4d_program_row = merged_row(self._e4d_program, browse)
        form.addRow(QCoreApplication.translate("PHGX", "E4D program"), self._e4d_program_row)
        self._e4d_processes = QSpinBox()
        self._e4d_processes.setRange(2, 1024)
        self._e4d_processes.setValue(int(saved.value(self._E4D_KEYS["processes"], 4) or 4))
        self._e4d_processes.setToolTip(
            QCoreApplication.translate("PHGX", "MPI processes for mpirun -np. E4D needs at least two - one master and "
            "one or more workers - and no more workers than electrodes."))
        form.addRow(QCoreApplication.translate("PHGX", "MPI processes"), self._e4d_processes)
        self._e4d_status = QLabel()
        self._e4d_status.setWordWrap(True)
        self._e4d_status.setTextInteractionFlags(Qt.TextSelectableByMouse)
        form.addRow("", self._e4d_status)
        self._e4d_rows = [self._e4d_launcher, self._e4d_program_row,
                          self._e4d_processes, self._e4d_status]
        self._set_rows_visible(self._e4d_rows, False)
        # A typed path is checked once typing pauses, not on every key.
        self._e4d_timer = QTimer(self)
        self._e4d_timer.setSingleShot(True)
        self._e4d_timer.setInterval(600)
        self._e4d_timer.timeout.connect(self._check_e4d)
        self._e4d_launcher.currentIndexChanged.connect(self._e4d_settings_changed)
        self._e4d_program.textChanged.connect(self._e4d_settings_changed)
        self._e4d_processes.valueChanged.connect(self._e4d_settings_changed)

    def _e4d_settings(self) -> Dict[str, Any]:
        """The E4D settings a run is given (``inversion.e4d.E4DSettings``)."""
        return {"launcher": str(self._e4d_launcher.currentData() or "auto"),
                "executable": self._e4d_program.text().strip(),
                "processes": int(self._e4d_processes.value())}

    def _browse_e4d(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, QCoreApplication.translate("PHGX", "Choose the e4d program"), "", "All files (*)")
        if path:
            self._e4d_program.setText(i18n.tr(path))

    def _e4d_settings_changed(self, *_args: Any) -> None:
        from PySide6.QtCore import QSettings

        saved = QSettings("PyHydroGeophysX", "Studio")
        for key, value in self._e4d_settings().items():
            saved.setValue(self._E4D_KEYS[key], value)
        if self._engine.currentData() == "e4d":
            self._e4d_timer.start()

    def _check_e4d(self) -> None:
        """Find E4D the way a run will, in a separate process: asking WSL can
        take a few seconds while its virtual machine starts."""
        previous = self._e4d_probe_worker
        if previous is not None and previous.isRunning():
            previous.cancel()
        self._e4d_probe_serial += 1
        serial = self._e4d_probe_serial
        settings = self._e4d_settings()
        self._e4d_found = None
        self._e4d_status.setText(QCoreApplication.translate("PHGX", "Looking for E4D…"))
        theme.set_tone(self._e4d_status, "hint")
        arguments = ["--json", "--launcher", settings["launcher"],
                     "--processes", str(settings["processes"])]
        if settings["executable"]:
            arguments += ["--executable", settings["executable"]]
        worker = ProcessProbeWorker("PyHydroGeophysX.inversion.e4d", arguments=arguments,
                                    timeout_ms=90000)
        worker.succeeded.connect(lambda result, token=serial: self._on_e4d_found(token, result))
        worker.failed.connect(lambda message, token=serial: self._on_e4d_found(
            token, {"runs": False, "kind": "missing",
                    "message": f"The E4D check did not finish: {message}"}))
        self._e4d_probe_worker = self.register_worker(worker, activity="Looking for E4D")
        worker.start()

    def _on_e4d_found(self, serial: int, result: Dict[str, Any]) -> None:
        if serial != self._e4d_probe_serial or self._engine.currentData() != "e4d":
            return
        self._e4d_found = dict(result)
        kind = str(result.get("kind", "missing"))
        tone = {"local": "ok", "wsl": "ok", "command": "ok",
                "files": "warn"}.get(kind, "error")
        text = str(result.get("message", ""))
        if kind == "missing":
            text += " Runs will write the E4D run folder and stop."
        self._e4d_status.setText(i18n.tr(text))
        theme.set_tone(self._e4d_status, tone)

    # -- R2 / R3t ------------------------------------------------------------
    #: The launcher is one choice for both programs; each has its own path.
    _R2_KEYS = {"launcher": "ert/r2/launcher", "r2": "ert/r2/executable",
                "r3t": "ert/r3t/executable"}

    def _r2_program_name(self) -> Optional[str]:
        """``r2`` or ``r3t`` while one of them is the engine, else None."""
        engine = str(self._engine.currentData() or "")
        return engine if engine in ("r2", "r3t") else None

    def _build_r2_rows(self, form: QFormLayout) -> None:
        """How R2 or R3t is reached: shown only while one of them is the engine.

        Like E4D they are external programs, so the page first says whether
        and how this computer runs them. The program path is kept per program
        between sessions, since it describes the machine.
        """
        self._r2_launcher = QComboBox()
        for label, value in (("Auto (this computer)", "auto"), ("Write files only", "files")):
            self._r2_launcher.addItem(i18n.tr(label), value)
        self._r2_launcher.setToolTip(
            QCoreApplication.translate("PHGX", "Whether R2/R3t is run here. They are Windows programs (R2.exe, R3t.exe) from "
            "Andrew Binley's web page or any ResIPy installation.\n\n"
            "Auto: run natively on Windows, through Wine on Linux and macOS. The program "
            "is the one given below, else PYHYDRO_R2 / PYHYDRO_R3T, else ResIPy's copy, "
            "else the first on PATH.\n"
            "Write files only: the complete run folder is written and the run stops; run "
            "R2.exe or R3t.exe in it elsewhere, then read it back with "
            "inversion.r2.read_r2_run."))
        form.addRow(QCoreApplication.translate("PHGX", "Run R2/R3t"), self._r2_launcher)
        self._r2_program = QLineEdit()
        self._r2_program.setPlaceholderText(QCoreApplication.translate("PHGX", "ResIPy's copy, or PATH"))
        self._r2_program.setToolTip(
            QCoreApplication.translate("PHGX", "The R2.exe or R3t.exe to run, when another than ResIPy's or the one on "
            "PATH. Leave empty to search for it."))
        browse = QPushButton("…")
        browse.setMaximumWidth(32)
        browse.setToolTip(QCoreApplication.translate("PHGX", "Choose the R2 or R3t program."))
        browse.clicked.connect(self._browse_r2)
        self._r2_program_row = merged_row(self._r2_program, browse)
        form.addRow(QCoreApplication.translate("PHGX", "Program"), self._r2_program_row)
        self._r2_status = QLabel()
        self._r2_status.setWordWrap(True)
        self._r2_status.setTextInteractionFlags(Qt.TextSelectableByMouse)
        form.addRow("", self._r2_status)
        self._r2_rows = [self._r2_launcher, self._r2_program_row, self._r2_status]
        self._set_rows_visible(self._r2_rows, False)
        self._r2_timer = QTimer(self)
        self._r2_timer.setSingleShot(True)
        self._r2_timer.setInterval(600)
        self._r2_timer.timeout.connect(self._check_r2)
        self._r2_launcher.currentIndexChanged.connect(self._r2_settings_changed)
        self._r2_program.textChanged.connect(self._r2_settings_changed)

    def _load_r2_settings(self, program: str) -> None:
        """Show the saved choices for ``program`` without re-saving them."""
        from PySide6.QtCore import QSettings

        saved = QSettings("PyHydroGeophysX", "Studio")
        for widget in (self._r2_launcher, self._r2_program):
            widget.blockSignals(True)
        index = self._r2_launcher.findData(str(saved.value(self._R2_KEYS["launcher"], "auto")))
        self._r2_launcher.setCurrentIndex(max(index, 0))
        self._r2_program.setText(i18n.tr(str(saved.value(self._R2_KEYS[program], "") or "")))
        self._r2_program.setPlaceholderText(
            QCoreApplication.translate("PHGX", "{0}.exe from ResIPy, or PATH").format('R2' if program == 'r2' else 'R3t'))
        for widget in (self._r2_launcher, self._r2_program):
            widget.blockSignals(False)

    def _r2_settings(self) -> Dict[str, Any]:
        """The R2/R3t settings a run is given (``inversion.r2.R2Settings``)."""
        return {"launcher": str(self._r2_launcher.currentData() or "auto"),
                "executable": self._r2_program.text().strip()}

    def _browse_r2(self) -> None:
        name = "R2" if self._r2_program_name() == "r2" else "R3t"
        path, _ = QFileDialog.getOpenFileName(self, QCoreApplication.translate("PHGX", "Choose the {0} program").format(name), "",
                                              "Programs (*.exe);;All files (*)")
        if path:
            self._r2_program.setText(i18n.tr(path))

    def _r2_settings_changed(self, *_args: Any) -> None:
        from PySide6.QtCore import QSettings

        program = self._r2_program_name()
        if program is None:
            return
        saved = QSettings("PyHydroGeophysX", "Studio")
        settings = self._r2_settings()
        saved.setValue(self._R2_KEYS["launcher"], settings["launcher"])
        saved.setValue(self._R2_KEYS[program], settings["executable"])
        self._r2_timer.start()

    def _check_r2(self) -> None:
        """Find R2 or R3t the way a run will, in a separate process."""
        program = self._r2_program_name()
        if program is None:
            return
        previous = self._r2_probe_worker
        if previous is not None and previous.isRunning():
            previous.cancel()
        self._r2_probe_serial += 1
        serial = self._r2_probe_serial
        settings = self._r2_settings()
        self._r2_found = None
        self._r2_status.setText(QCoreApplication.translate("PHGX", "Looking for the program…"))
        theme.set_tone(self._r2_status, "hint")
        arguments = ["--json", "--program", program, "--launcher", settings["launcher"]]
        if settings["executable"]:
            arguments += ["--executable", settings["executable"]]
        worker = ProcessProbeWorker("PyHydroGeophysX.inversion.r2", arguments=arguments,
                                    timeout_ms=60000)
        worker.succeeded.connect(lambda result, token=serial: self._on_r2_found(token, result))
        worker.failed.connect(lambda message, token=serial: self._on_r2_found(
            token, {"runs": False, "kind": "missing",
                    "message": f"The check did not finish: {message}"}))
        self._r2_probe_worker = self.register_worker(worker, activity="Looking for R2 / R3t")
        worker.start()

    def _on_r2_found(self, serial: int, result: Dict[str, Any]) -> None:
        if serial != self._r2_probe_serial or self._r2_program_name() is None:
            return
        self._r2_found = dict(result)
        kind = str(result.get("kind", "missing"))
        tone = {"native": "ok", "wine": "ok",
                "files": "warn"}.get(kind, "error")
        text = str(result.get("message", ""))
        if kind == "missing":
            text += " Runs will write the run folder and stop."
        # λ stays on the page for the other engines; say here that it is unused.
        text += (" It chooses its own smoothing weight at every iteration: λ and "
                 "auto-λ are not used.")
        self._r2_status.setText(i18n.tr(text))
        theme.set_tone(self._r2_status, tone)

    def _warn_external_not_running(self, what: str) -> None:
        """Before a run on E4D, R2 or R3t, say when the program will not run
        here: the run then writes its folder and stops."""
        engine = str(self._engine.currentData() or "")
        if engine == "e4d":
            found, name = self._e4d_found or {}, "E4D"
        elif engine in ("r2", "r3t"):
            found, name = self._r2_found or {}, "R2" if engine == "r2" else "R3t"
        else:
            return
        if not found.get("runs", False):
            self.log(f"{name} will not run here ("
                     + (str(found.get("message")) if found else "it has not been found yet")
                     + f"). The run writes the complete {name} {what} and stops; its path "
                     "is in the message.", "warn")

    # -- inversion -----------------------------------------------------------
    def _report_data_health(self) -> None:
        """Report what the data say about themselves, before Full mode inverts them.

        This reports and never drops. Rejecting data is the QC panel's job, where
        the thresholds are visible and the count changes in front of you; a run
        that quietly shrank its own dataset is the harder thing to review later.
        What it adds is the checks whose inputs the inversion never looks at:
        reciprocity, and whether the readings had any signal behind them.
        """
        data = self._ert_data
        if data is None:
            return
        n = int(data.size())
        notes: List[str] = []

        rec = self._reciprocal_error(data)
        if rec is not None and np.isfinite(rec).any():
            finite = rec[np.isfinite(rec)]
            median = 100.0 * float(np.median(finite))
            over5 = int((finite > 0.05).sum())
            notes.append(
                f"reciprocals: {finite.size}/{n} paired, median disagreement {median:.1f}%"
                + (f", {over5} above 5%" if over5 else ""))
            if median > 5.0:
                notes.append(
                    "the median reciprocal disagreement is above 5%, so the assumed error "
                    "model is probably optimistic and chi2 will read low")
        else:
            notes.append(f"reciprocals: none in this survey, so the {n} errors are assumed, not measured")

        for token, name in (("u", "voltage"), ("i", "current")):
            if not data.haveData(token):
                continue
            v = np.abs(np.asarray(data[token], dtype=float))
            weak = int((~np.isfinite(v) | (v <= 0)).sum())
            if weak:
                notes.append(f"{name}: {weak} reading(s) at or below zero, which carry no signal")
            else:
                notes.append(f"{name}: all finite and positive, spanning {v.min():.4g} to {v.max():.4g}")

        err = np.asarray(data["err"], dtype=float) if data.haveData("err") else None
        if err is not None and err.size:
            notes.append(f"stated error: median {100.0 * float(np.median(err)):.1f}%")

        for note in notes:
            self.log("Full-mode check · " + note, "info")

    def _run_inversion(self) -> None:
        if self._ert_data is None:
            self.log("Load ERT data with apparent resistivity first.", "warn")
            return
        if (
            self._engine.currentData() == "adtlert"
            and self._adtlert_single_ready is not True
        ):
            self.log(
                "ADTLERT single self-test has not passed. Wait for the check, "
                "or select In-house Gauss-Newton / PyHydro. "
                "To retry, switch engines and select ADTLERT again.",
                "warn",
            )
            return
        self._warn_external_not_running("run folder")
        if str(self._inv_mode.currentData() or "quick") == "full":
            self._report_data_health()
        error_source, error_model = self._single_error_model()
        try:
            run = self.begin_persisted_run(
                "ert.single_inversion", "ert.single_inversion",
                label=self._run_label([self._data_path]),
            )
        except Exception as exc:  # noqa: BLE001
            self.log(f"Could not prepare Project run: {exc}", "error")
            return
        out_path = run.outputs_dir
        input_path = run.inputs_dir / "filtered_ert_data.dat"
        electrode_rows = self._electrode_rows()
        electrode_path = run.inputs_dir / "edited_electrodes.csv"
        qc_path = run.inputs_dir / "ert_qc_mask.json"
        io_utils.write_csv(
            electrode_path,
            [
                (
                    row["order"],
                    row["label"],
                    row["x"],
                    row["z"],
                    "" if row["original_index"] is None else row["original_index"],
                )
                for row in electrode_rows
            ],
            header=("order", "label", "x", "z", "original_index"),
        )
        io_utils.write_json(
            qc_path,
            {
                "keep": list(self._qc_mask or []),
                "source_measurements": int(self._ert_data_full.size())
                if self._ert_data_full is not None else int(self._ert_data.size()),
                "filtered_measurements": int(self._ert_data.size()),
                # "keep" is over the forward and reciprocal readings together,
                # and an averaged pair is kept as its first reading.
                "reciprocal_file": self._data_partner.name if self._data_partner else "",
                "averaged_pairs": int(((self._qc_report or {}).get("averaged") or {})
                                      .get("pairs", 0)) if self._averaged_loaded() else 0,
            },
        )
        try:
            save_edited_ert_container(self._ert_data, input_path, electrode_rows)
        except Exception as exc:  # noqa: BLE001
            self.log(f"Could not serialize edited/QC-filtered ERT data: {exc}", "error")
            self.fail_persisted_run(str(exc), "ert.single_inversion")
            return
        project_root = run.run_dir
        spec = WorkflowSpec(
            workflow_id="ert.single_inversion",
            inputs={
                "data": ArtifactRef.from_path(
                    input_path,
                    artifact_id="ert:single:filtered_data",
                    kind="ert_data",
                    format="dat",
                    base_dir=project_root,
                    metadata={
                        "instrument": self._instrument.currentText(),
                        "electrodes": len(self._x),
                        "measurements": self._n_meas,
                        "qc_filtered": True,
                        **({"reciprocal_file": self._data_partner.name}
                           if self._data_partner is not None else {}),
                        **self._survey_time_record(self._data_path),
                    },
                ),
                "electrodes": ArtifactRef.from_path(
                    electrode_path,
                    artifact_id="ert:single:electrodes",
                    kind="electrode_geometry",
                    format="csv",
                    base_dir=project_root,
                ),
                "qc_mask": ArtifactRef.from_path(
                    qc_path,
                    artifact_id="ert:single:qc_mask",
                    kind="qc_mask",
                    format="json",
                    base_dir=project_root,
                ),
            },
            parameters={
                "lambda": float(self._lam.value()),
                "max_iterations": min(int(self._iter.value()),
                                      int(self._iter_ceiling.value())),
                "relative_error": float(self._relerr.value()),
                **self._mesh_options(),
                "instrument": "BERT",
                "engine": str(self._engine.currentData()),
                "geometric_factor_policy": str(self._geom_policy),
                "error_source": error_source,
                **({"error_model": error_model} if error_model else {}),
                # The lowest error a reciprocal gives, for every reading, when
                # the errors come from reciprocals: the model's, or the one the
                # pairs were averaged with.
                **({"error_floor": float(error_model["floor"])} if error_model else
                   {"error_floor": float(self._qc_applied["reciprocal_floor"])}
                   if self._averaged_loaded() else {}),
                "absolute_error": float(self._abserr.value()),
                "plateau_tolerance": float(self._plateau.value()) / 100.0,
                "max_total_iterations": int(self._iter_ceiling.value()),
                "reject_outliers": bool(self._reject.isChecked()),
                "outlier_threshold": float(self._reject_sigma.value()),
                "outlier_passes": int(self._reject_passes.value()),
                "min_data_fraction": float(self._min_keep.value()) / 100.0,
                "auto_lambda": bool(self._auto_lam.isChecked()),
                "target_chi2": float(self._target_chi2.value()),
                "chi2_tolerance": float(self._chi2_tol.value()),
                "max_lambda_trials": int(self._lam_trials.value()),
                **self._zone_parameters(),
                **({"e4d": self._e4d_settings()}
                   if self._engine.currentData() == "e4d" else {}),
                **({"r2": self._r2_settings()}
                   if self._r2_program_name() is not None else {}),
            },
            metadata={"source_instrument": self._instrument.currentText()},
        )
        recipe_path, script_path = export_workflow_bundle(spec, run.run_dir, stem="ert")
        self._reproduce.set_bundle(recipe_path, script_path)
        self._ert_recipe_path = str(recipe_path)
        self._write_single_records(run, spec)
        self._inv_busy = BusyStateController([self._invert_btn])
        self._inv_busy.start()
        self._invert_btn.setText(QCoreApplication.translate("PHGX", "Inverting…"))
        self._inv_progress.setVisible(True)
        self._inv_progress.setRange(0, 0)
        # Every ERT engine performs long native numerical work.  Run all of
        # them outside Qt's interpreter: PyGIMLi and the in-house Gauss-Newton
        # path can retain the GIL, while ADTLERT owns a CUDA context.  The
        # process-safe model bundle below restores mesh/model/response/coverage
        # into the interactive viewer when the child exits.
        self._agent_run_state = "running"
        self._agent_run_error = ""
        self._inv_worker = ProcessWorkflowWorker(
            recipe_path,
            project_root,
            out_path,
            run.result_path,
        )
        self._inv_worker.logged.connect(lambda msg: self.log(msg, "info"))
        # The survey goes with its result: a preview loaded while this runs
        # replaces _data_path, and would date the model by the wrong file.
        self._inv_worker.succeeded.connect(
            lambda result, source=self._data_path: self._on_ert_workflow_ok(result, source))
        self._inv_worker.failed.connect(self._on_inversion_failed)
        self._inv_worker.finished.connect(self._reset_invert_button)
        self.register_worker(self._inv_worker, activity="Running the ERT inversion")
        self._inv_worker.start()
        self._inv_stop.attach(self._inv_worker, "ert.single_inversion")

    def _averaged_loaded(self) -> bool:
        """Whether the data on screen had their reciprocal pairs averaged."""
        return bool(self._qc_report is not None and self._qc_applied is not None
                    and self._qc_applied.get("average_reciprocals")
                    and (self._qc_report.get("averaged") or {}).get("pairs"))

    def _single_error_model(self) -> Tuple[str, Optional[Dict[str, Any]]]:
        """``(error_source, error_model)`` for a single inversion.

        "From the reciprocal error model" fits the survey's own pairs - all of
        them as read, or those the filter kept, as the Reciprocal errors tab's
        "Fit to" says: the fit the tab draws and the QC report states - and
        hands the model to the inversion, which sets each reading's error from
        it. With too few pairs to fit, the estimate is used and the log says so.
        """
        source = str(self._err_source.currentData())
        if source != "reciprocal":
            return source, None
        from PyHydroGeophysX.qt_apps.ert_records import (
            fit_series_error_model,
            fit_to_sentence,
            power_law,
        )

        fit_to = self._error_fit_to()
        pairing = self._single_pairing() or {}
        fit = fit_series_error_model([pairing], fit_to)
        if fit is None:
            self.log(f"Data errors: the survey has {pairing.get('scored_pairs', 0)} scored "
                     "reciprocal pairs, too few to fit an error model (at least 15 are "
                     "needed), so the errors are estimated from the values under Data "
                     "errors instead.", "warn")
            return "estimate", None
        model = {"m": fit["m"], "b": fit["b"], "r2": fit["r2"], "r2_raw": fit["r2_raw"],
                 "pairs": fit["n"], "floor": self._reciprocal_floor(),
                 "fitted_over": self._fitted_over(fit, series=False)}
        self.log(f"Data errors from the reciprocal error model {power_law(model)}, fitted to "
                 f"{fit_to_sentence(fit_to, fit['filtered'])} (binned R² {fit['r2']:.3f}, "
                 f"{fit['n']} pairs), at least {100.0 * model['floor']:g} %.", "info")
        return source, model

    def _error_model_text(self, timelapse: bool = False,
                          model: Optional[Dict[str, Any]] = None) -> str:
        """The data errors a run is set to use, in a sentence for its records."""
        estimate = (f"{float(self._relerr.value()):g} + {float(self._abserr.value()):g} "
                    "ohm / |R|")
        if model:
            from PyHydroGeophysX.qt_apps.ert_records import power_law

            return (f"the reciprocal error model {power_law(model)}, never below "
                    f"{100.0 * float(model.get('floor') or 0.0):g} %")
        if timelapse:
            return (f"each survey's err column where every reading has one, otherwise "
                    f"relative error {float(self._relerr.value()):g}")
        return f"{self._err_source.currentText()} (estimate {estimate})"

    def _write_single_records(self, run, spec: WorkflowSpec) -> None:
        """Write the run's ``inversion_settings.txt`` and, for filtered data, its
        ``qc_report.txt`` (``qt_apps/ert_records.py``), from the spec the run is
        handed and the counts Apply filter recorded. A file that cannot be
        written is said in the log; the run goes ahead, its recipe being the
        record it needs to rerun."""
        from PyHydroGeophysX.qt_apps import ert_records

        self._ert_settings_path = None
        try:
            source = str(self._data_path or "")
            stamp = survey_timing.survey_timing([source]).timestamps[0] if source else None
            acquired = f"{stamp:%Y-%m-%d %H:%M:%S}" if stamp is not None else ""
            reader = self._reader_status.text().removeprefix("Data loaded by ").rstrip(".")
            inverted = int(self._ert_data.size())
            total = (int(self._ert_data_full.size()) if self._ert_data_full is not None
                     else inverted)
            # The thresholds count only when they filtered the data loaded now.
            filtered = self._qc_report is not None and self._qc_applied is not None
            pair = self._pair_record() if self._data_partner is not None else None
            model = dict(spec.parameters.get("error_model") or {}) or None
            # The pairs the error model is fitted to, said wherever there are pairs.
            fit_to = self._error_fit_to()
            paired = bool((self._single_pairing() or {}).get("scored_pairs"))
            path = ert_records.write_settings(run.run_dir, ert_records.single_settings_text(
                spec, run_id=run.run_id, source=source, acquired=acquired,
                instrument=self._instrument.currentText(), reader=reader,
                electrode_file=str(self._electrode_path or ""), electrodes=len(self._x),
                measurements=(total, inverted),
                qc=self._qc_applied if filtered else None,
                mode=self._inv_mode.currentText(),
                reciprocal=({"file": pair["reciprocal"],
                             "forward_readings": pair["forward_readings"],
                             "reciprocal_readings": pair["reciprocal_readings"]}
                            if pair else None),
                fit_to=fit_to if paired or model else None))
            self._ert_settings_path = path
            self.log(f"Inversion settings written to {path}", "info")
            # A survey of two files, or errors from its pairs, is worth its QC
            # report - the pairing and the model - even when nothing filtered it.
            if filtered or pair or model:
                if filtered:
                    qc_log = dict(self._qc_report)
                else:
                    qc_log = {"readings": total, "kept": inverted, "checks": [],
                              "pairing": self._single_pairing() or {}}
                if pair:
                    qc_log["files"] = pair
                report = ert_records.write_single_qc_report(
                    run.run_dir, source=Path(source).name, acquired=acquired,
                    reader=f"{self._instrument.currentText()}, read by {reader}",
                    qc=self._qc_applied if filtered else None, report=qc_log,
                    error_model=self._error_model_text(model=model),
                    applied_model=model, fit_to=fit_to)
                self.log(f"Data QC report written to {report}", "info")
        except Exception as exc:  # noqa: BLE001 - a record must not stop the run
            self.log(f"Could not write the run's settings file: {exc}", "warn")

    def _record_outcome(self, path: Optional[Path], kind: str, summary: Dict[str, Any],
                        extra: Dict[str, Any]) -> None:
        """Add what the finished run reported to its ``inversion_settings.txt``:
        the engine that ran, the fit, and for a time-lapse run any setting the
        engine replaced. Warnings in it are logged, so they stay with the run."""
        from PyHydroGeophysX.qt_apps import ert_records

        if path is None:
            return
        try:
            if kind == "single":
                rows, notes = ert_records.single_outcome(dict(summary), dict(extra))
            else:
                rows, notes = ert_records.timelapse_outcome(dict(summary), dict(extra))
                zones = list(summary.get("zones_not_applied") or [])
                if zones:
                    self.log("The engine did not take the a-priori zone values ("
                             + ", ".join(map(str, zones)) + "); the run used none.", "warn")
            ert_records.append_outcome(Path(path), rows, notes)
            for note in notes[1:]:
                self.log(f"The engine ran with {note.strip()} (its own default).", "info")
        except Exception as exc:  # noqa: BLE001 - a record must not lose the result
            self.log(f"Could not add the outcome to {Path(path).name}: {exc}", "warn")

    def _abs_path(self, value: Any) -> str:
        """Resolve a workflow-relative output path against the recipe directory."""
        if not value:
            return ""
        path = Path(str(value))
        if path.is_absolute() or not self._ert_recipe_path:
            return str(path)
        return str(Path(self._ert_recipe_path).resolve().parent / path)

    def _on_ert_workflow_ok(self, result: WorkflowRunResult,
                            source: Optional[Path] = None) -> None:
        self._record_outcome(self._ert_settings_path, "single", result.summary,
                             result.metrics)
        summary = dict(result.summary)
        manager = result.objects.get("manager")
        fixed_manager = result.objects.get("fixed_manager")
        if manager is None and summary.get("model_bundle"):
            manager = self._load_model_bundle(summary["model_bundle"])
        if fixed_manager is None and summary.get("fixed_model_bundle"):
            fixed_manager = self._load_model_bundle(
                summary["fixed_model_bundle"]
            )
        vtk = self._abs_path(summary.get("vtk"))
        if not vtk:
            vtk_ref = next(
                (artifact for artifact in result.artifacts if "vtk" in artifact.format),
                None,
            )
            vtk = self._abs_path(vtk_ref.path) if vtk_ref is not None else ""
        payload = {
            "mgr": manager,
            "chi2": result.metrics.get("chi2", float("nan")),
            "vtk": vtk,
            "metrics": dict(result.metrics),
            "convergence": (
                result.objects.get("convergence")
                or summary.get("convergence")
                or []
            ),
            "fixed_mgr": fixed_manager,
            "fixed_convergence": (
                result.objects.get("fixed_convergence")
                or summary.get("fixed_convergence")
                or []
            ),
            "fixed_metrics": dict(summary.get("fixed_metrics") or {}),
            "fixed_lambda": dict(summary.get("fixed_lambda") or {}),
            "fixed_vtk": self._abs_path(summary.get("fixed_vtk_path")),
            "lambda_requested": summary.get("lambda_requested"),
            "lambda_used": summary.get("lambda_used"),
            "lambda_trials": list(summary.get("lambda_trials") or []),
            "auto_lambda_status": summary.get("auto_lambda_status", "off"),
            "auto_lambda_note": summary.get("auto_lambda_note", ""),
            "data_error": dict(summary.get("data_error") or {}),
            "geometric_factors": dict(summary.get("geometric_factors") or {}),
            "cold_retry": dict(summary.get("cold_retry") or {}),
            "convergence_track": list(summary.get("convergence_track") or []),
            "outliers": dict(summary.get("outliers") or {}),
            "convergence_stop": summary.get("convergence_stop", ""),
            "engine": summary.get("engine", ""),
            "engine_requested": summary.get("engine_requested", ""),
            "e4d": dict(summary.get("e4d") or {}),
            "r2": dict(summary.get("r2") or {}),
            "r3t": dict(summary.get("r3t") or {}),
            # A profile inverted on a 3D mesh: the whole model beside the section.
            "vtk_3d_path": self._abs_path(summary.get("vtk_3d_path")),
            "volume": dict(summary.get("volume") or {}),
            "data_path": source,
        }
        try:
            self._on_inversion_ok(payload)
        finally:
            if hasattr(self.state, "update_workflow_result"):
                self.state.update_workflow_result(
                    self.module_key,
                    "ert.single_inversion",
                    result.to_dict(),
                    recipe_path=self._ert_recipe_path,
                )

    def _load_model_bundle(self, bundle: Dict[str, Any]):
        """Hydrate a process-safe ERT result into the viewer's manager shape."""
        try:
            from PyHydroGeophysX.core.mesh_serialization import read_bms
            # numpy only; the inversion code need not load in the window's process.
            from PyHydroGeophysX.inversion.model_result import ModelResult

            paths = {key: Path(str(value)) for key, value in dict(bundle).items()}
            # Without the cell-neighbour table, most of a 3-D mesh's load, spent
            # in one call that would hold the window still (see read_bms).
            mesh = read_bms(paths["mesh"], neighbours=False)
            model = np.load(paths["model"], allow_pickle=False)
            response = (
                np.load(paths["response"], allow_pickle=False)
                if "response" in paths else None
            )
            coverage = (
                np.load(paths["coverage"], allow_pickle=False)
                if "coverage" in paths else None
            )
            return ModelResult(mesh, model, response=response, coverage=coverage)
        except Exception as exc:  # noqa: BLE001 - keep metrics usable on load failure
            self.log(f"Could not load inversion model files: {exc}", "error")
            return None

    def _on_inversion_ok(self, result: dict) -> None:
        self._agent_run_state = "completed"
        self._agent_run_error = ""
        metrics = dict(result.get("metrics") or {})
        engine = str(result.get("engine") or "")
        requested_engine = str(result.get("engine_requested") or engine)
        solver = str(metrics.get("linearized_solver") or "")
        if engine in ("r2", "r3t"):
            # They choose their own smoothing weight (shown as alpha); the λ the
            # page holds was never used, so it is not shown as if it were.
            metrics.pop("lambda", None)
        if engine:
            metrics.setdefault(
                "method", f"{engine} · {self._instrument.currentText()}"
            )
        else:
            metrics.setdefault("method", self._instrument.currentText())
        note = str(result.get("auto_lambda_note") or "")
        status = str(result.get("auto_lambda_status") or "off")
        lam_used = result.get("lambda_used")
        lam_req = result.get("lambda_requested")
        trials = list(result.get("lambda_trials") or [])
        errors = dict(result.get("data_error") or {})
        geometry = dict(result.get("geometric_factors") or {})
        outliers = dict(result.get("outliers") or {})
        dropped = int(outliers.get("dropped") or 0)
        switched = (
            lam_used is not None and lam_req is not None
            and float(lam_used) != float(lam_req)
        )
        # The kept run is the one at the λ you set, on the full dataset. It is worth
        # keeping whenever either of those differs from what is on screen.
        keep_fixed = result.get("fixed_mgr") is not None and (switched or dropped > 0)

        # This panel sits above the convergence plot, so it stays to a couple of
        # short entries. Anything omitted here is in the log.
        extra: Dict[str, Any] = dict(metrics.get("extra") or {})
        if engine == "adtlert":
            forward = metrics.get("adtlert_forward")
            extra["compute"] = (f"ADTLERT {forward} · " if forward else "") + "cuDSS forward · GPU CGLS"
        elif engine == "e4d":
            elements = int(dict(result.get("e4d") or {}).get("elements") or 0)
            extra["compute"] = "E4D 3D" + (f" · {elements} elements" if elements else "")
        elif engine in ("r2", "r3t"):
            own = dict(result.get(engine) or {})
            name = "R2" if engine == "r2" else "R3t"
            elements = int(own.get("elements") or 0)
            alpha = own.get("alpha")
            extra["compute"] = f"{name} {'2D' if engine == 'r2' else '3D'}" + (
                f" · {elements} elements" if elements else "")
            if alpha is not None and alpha == alpha:
                # Its own smoothing weight stands where λ would.
                extra["alpha"] = f"{float(alpha):.4g} (chosen by {name}; λ not used)"
        if dropped:
            extra["data"] = f"{outliers.get('kept')} of {outliers.get('n_start')} kept"
            if outliers.get("limited_by_floor"):
                extra["data"] += " (floor reached)"
        # A skipped k check has no other symptom. Wrong geometric factors scale the
        # section by a constant and leave chi2 untouched, so if the panel stays
        # silent here a Quick result is indistinguishable from a validated one.
        # A pass says nothing worth a line; the other three states each do.
        # ``ok`` stays False after a successful repair, so ``repaired`` is what
        # separates a fixed run from one whose scale is still unverified.
        if not geometry.get("checked", False):
            extra["k"] = "not checked"
        elif geometry.get("repaired"):
            extra["k"] = "repaired"
        elif not geometry.get("ok", True):
            extra["k"] = "scale unverified"
        # How chi2 responded to lambda is the one thing with no other home.
        if len(trials) > 1:
            extra["λ"] = " → ".join(
                f"{float(t['lambda']):g} (χ²{float(t['chi2']):.2f})" for t in trials
            )
        if extra:
            metrics["extra"] = extra
        # The whole iteration history, so the convergence plot can show every
        # stage rather than only the run that happened to finish last.
        track = list(result.get("convergence_track") or [])
        if track:
            metrics["convergence_track"] = track
        # Only warn in the panel; the routine outcome is already in the numbers.
        if geometry.get("repaired"):
            metrics["note"] = "Geometric factors were recomputed; see the log."
        elif geometry.get("checked") and not geometry.get("ok", True):
            metrics["note"] = "⚠ Geometric factors look wrong; the scale is off."
        elif status not in ("converged", "already_on_target", "off") and note:
            metrics["note"] = note

        choices: List[Dict[str, Any]] = []
        primary = result.get("mgr")
        if primary is not None:
            parts = []
            if lam_used is not None:
                parts.append(f"{'Auto λ' if switched else 'λ'} = {float(lam_used):g}")
            if dropped:
                parts.append(f"{outliers.get('kept')} data")
            chi2 = result.get("chi2")
            if chi2 == chi2:
                parts.append(f"χ² = {float(chi2):.2f}")
            choices.append({"label": "  ·  ".join(parts) or "Model", "mgr": primary,
                            "metrics": metrics,
                            "convergence": result.get("convergence") or [],
                            "vtk": result.get("vtk") or "", "chi2": chi2,
                            "lambda": lam_used})
        if keep_fixed:
            fixed_metrics = dict(result.get("fixed_metrics") or {})
            fixed_metrics.setdefault("method", self._instrument.currentText())
            fixed_info = dict(result.get("fixed_lambda") or {})
            reasons = []
            if switched:
                reasons.append(f"before the λ search moved to {float(lam_used):g}")
            if dropped:
                reasons.append(f"before {dropped} measurement(s) were rejected")
            fixed_metrics["note"] = (
                "The run at the settings you entered, kept for comparison: "
                + " and ".join(reasons) + "."
            )
            fixed_chi2 = fixed_info.get("chi2", fixed_metrics.get("chi2"))
            parts = [f"Yours: λ = {float(lam_req):g}"]
            if dropped:
                parts.append(f"{fixed_info.get('n_data', outliers.get('n_start'))} data")
            if fixed_chi2 is not None and fixed_chi2 == fixed_chi2:
                parts.append(f"χ² = {float(fixed_chi2):.2f}")
            choices.append({"label": "  ·  ".join(parts), "mgr": result.get("fixed_mgr"),
                            "metrics": fixed_metrics,
                            "convergence": result.get("fixed_convergence") or [],
                            "vtk": result.get("fixed_vtk") or "",
                            "chi2": fixed_chi2, "lambda": lam_req})

        self._inv_choices = choices
        self._lam_pick.blockSignals(True)
        self._lam_pick.clear()
        for choice in choices:
            self._lam_pick.addItem(choice["label"])
        self._lam_pick.setCurrentIndex(0)
        self._lam_pick.blockSignals(False)
        self._lam_pick_row.setVisible(len(choices) > 1)

        if choices:
            self._tl_step_row.setVisible(False)  # single result: no step selector
            # A new result arrives as inverted; any earlier correction was of a
            # different model.
            self._inv_correction = None
            # Recorded with the result, because the correction dates the model
            # by it. A caller that does not say which file it inverted means
            # the one loaded now.
            source = result.get("data_path", self._data_path)
            self._inv_source = Path(source) if source else None
            self._show_lambda_choice(0)
            self._tabs.setCurrentWidget(self._model_tab)
            self._model_export_btn.setEnabled(True)
            days, dates = self._single_survey_times()
            self._tc_box.set_context(1, dates is not None, days=days, dates=dates)
            self._tc_box.set_available(True)
            self._tc_box.show_applied(None)
        else:
            self._inv_mgr = None
            self._quality_view.show_quality(
                metrics, result.get("convergence"), title="ERT inversion")

        # The library already logged the stage-by-stage detail while it ran. Only
        # add what it could not know, and only once: a second copy of the same
        # sentence turns this panel into a wall of text.
        chi2 = result.get("chi2")
        summary = f"ERT inversion complete: χ² = {chi2:.2f}" if chi2 == chi2 \
            else "ERT inversion complete"
        if lam_used is not None:
            summary += f" at λ = {float(lam_used):g}"
        if dropped:
            summary += f", {outliers.get('kept')}/{outliers.get('n_start')} data"
        self.log(summary + ".", "success")
        # A bad geometric factor rescales the whole section without touching chi2,
        # so this outranks anything the fit statistics say.
        if geometry.get("repaired"):
            factor = geometry.get("averted_factor")
            self.log("Geometric factors were recomputed"
                     + (f"; the section would otherwise be {float(factor):.2f}× off."
                        if factor else "."), "warn")
        elif geometry.get("checked") and not geometry.get("ok", True):
            factor = geometry.get("suspected_factor")
            self.log("Geometric factors look wrong"
                     + (f": the scale is about {1.0 / float(factor):.2f}× off."
                        if factor else "."), "error")
        if result.get("convergence_stop") == "iteration_cap":
            self.log("Still improving at the iteration ceiling; χ² is an upper bound.",
                     "warn")
        if outliers.get("limited_by_floor"):
            self.log(f"“Keep at least” capped the cut at {outliers.get('kept')} data; "
                     "outliers remain. Lower it, or QC the data first.", "warn")
        retry = dict(result.get("cold_retry") or {})
        if retry:
            self.log(f"Warm sweep stalled at χ² {retry['warm_chi2']:.1f}; a cold sweep "
                     + (f"reached {retry['cold_chi2']:.1f}." if retry.get("helped")
                        else "did not do better."), "warn")
        if keep_fixed:
            self.log("Your own settings are kept as the second entry in Model.", "info")
        if requested_engine == "adtlert" and engine != "adtlert":
            self.log(
                "ADTLERT was requested but the run used the original PyHydro "
                "ERT engine: CUDA, cuDSS or NVRTC was unavailable.",
                "warn",
            )
        elif engine == "adtlert":
            self.log(
                f"Compute backend: ADTLERT · cuDSS forward · {solver or 'gpu_cgls'}.",
                "info",
            )
        vtk = result.get("vtk")
        if vtk:
            self.log(f"Saved {Path(vtk).name} to {Path(vtk).parent}", "info")
        volume = str(result.get("vtk_3d_path") or "")
        solid = dict(result.get("volume") or {})
        # A 3-D survey's model is the volume, drawn in place; a profile's
        # section has its volume one click away.
        self._model_3d_row.setVisible(bool(volume) and not solid.get("survey_3d"))
        self._model_3d_path = volume
        if solid.get("survey_3d"):
            self.log(f"Inverted in 3D on {solid.get('cells', '?')} cells; the model is "
                     f"drawn in 3D (tick Clip plane to look inside) and saved as "
                     f"{Path(volume).name}.", "info")
        elif volume:
            self.log(f"Inverted in 3D on {solid.get('cells', '?')} "
                     f"cells; the section along the line is shown, and the whole model is "
                     f"{Path(volume).name} (Open 3D model, above the section).", "info")
        e4d = dict(result.get("e4d") or {})
        if e4d.get("run_dir"):
            self.log(f"E4D's own files (e4d.log, sigma.N) and the 3D model "
                     f"resistivity_3d.vtk are in {e4d['run_dir']}", "info")
        for engine_key, name in (("r2", "R2"), ("r3t", "R3t")):
            own = dict(result.get(engine_key) or {})
            if own.get("run_dir"):
                self.log(f"{name}'s own files ({name}.out, f001_res.dat, its VTK) are in "
                         f"{own['run_dir']}; {name} stopped with "
                         f"\"{own.get('stop_message') or 'no message'}\"", "info")

        mgr = result.get("mgr")
        if mgr is not None and hasattr(self.state, "register_geophysical_resource"):
            self.state.register_geophysical_resource(
                "ERT", "model", np.asarray(mgr.model, dtype=float),
                label="Latest ERT resistivity model", path=str(vtk or ""),
                metadata={"chi2": chi2, "mesh": getattr(mgr, "paraDomain", None),
                          "lambda": lam_used, "lambda_requested": lam_req,
                          "auto_lambda_status": status},
                resource_id="ert:model:latest",
            )
        self.report_result({"resistivity_vtk": vtk, "chi2": chi2,
                            "rrms": metrics.get("rrms"), "iterations": metrics.get("iterations"),
                            "num_measurements": metrics.get("n_data", self._n_meas),
                            "instrument": self._instrument.currentText(),
                            "engine": engine,
                            "engine_requested": requested_engine,
                            "linearized_solver": solver,
                            "lambda": lam_used, "lambda_requested": lam_req,
                            "auto_lambda_status": status,
                            "auto_lambda_note": note,
                            "lambda_trials": trials,
                            "data_error": errors,
                            "geometric_factors": geometry,
                            "outliers": outliers,
                            "convergence_stop": result.get("convergence_stop", ""),
                            "convergence_track": track,
                            "fixed_lambda": dict(result.get("fixed_lambda") or {})})
        self.offer_map_export()

    def _show_lambda_choice(self, index: int) -> None:
        """Display one of the kept single-inversion models (auto-λ or fixed λ)."""
        if not (0 <= index < len(self._inv_choices)):
            return
        choice = self._inv_choices[index]
        self._map_result_kind = 'single'
        self._sync_model_exports()
        self._inv_mgr = choice["mgr"]
        if self._inv_mgr is not None:
            if self._inv_correction:
                # The correction stays on when the other model is picked: it is a
                # statement about the ground, not about either inversion.
                self._apply_single_temperature(self._inv_correction["spec"])
            else:
                self._show_single_model(None)
        self._quality_view.show_quality(
            choice["metrics"], choice["convergence"],
            title=f"ERT inversion — {choice['label']}")

    @staticmethod
    def row_label(widget):
        """The QFormLayout label paired with ``widget``, or None.

        Resolved through the widget's own parent rather than a stored layout, so
        moving a row between group boxes cannot silently leave its label behind.
        """
        parent = widget.parentWidget()
        form = parent.layout() if parent is not None else None
        return form.labelForField(widget) if isinstance(form, QFormLayout) else None

    def _set_rows_visible(self, widgets, on: bool) -> None:
        """Hide a form row, label included, since QFormLayout keeps them separate."""
        for widget in widgets:
            widget.setVisible(bool(on))
            label = self.row_label(widget)
            if label is not None:
                label.setVisible(bool(on))
