"""The ERT page: the run pinned under the controls, results, exports, rendering and publishing (plan M4.5).

Part of :class:`~.page.ERTProcessingModule`, split from the former
``ert_processing.py`` by area; the methods are unchanged.
"""

from __future__ import annotations

from .common import (
    Any,
    Callable,
    ContentWidthScrollArea,
    Dict,
    List,
    Optional,
    Path,
    PlainDoubleSpinBox,
    ProcessProbeWorker,
    QCheckBox,
    QComboBox,
    QCoreApplication,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
    Signal,
    TaskWorker,
    Tuple,
    _PLATEAU_TIP,
    _TC_WAITING,
    _logger,
    _value_name,
    i18n,
    io_utils,
    np,
    select_directory,
    shutil,
    survey_timing,
    temperature_panel,
    theme,
)


class _ResultsPanel:

    def _build_timelapse_panel(self) -> QWidget:
        """The time-lapse-only options, shown only in time-lapse mode. The ERT file
        list (which doubles as the single-file loader) lives in the Load group at
        the top; shared λ / iterations / relative error / mesh quality live in the
        Inversion group above; the Run button is pinned under the column. Only the
        temporal controls are here."""
        panel = QGroupBox(QCoreApplication.translate("PHGX", "Time-lapse"))
        self._tl_panel = panel
        tlform = QFormLayout(panel)
        self._tl_alpha = PlainDoubleSpinBox(); self._tl_alpha.setRange(0.0, 1000.0); self._tl_alpha.setValue(10.0)
        self._tl_alpha.setToolTip(QCoreApplication.translate("PHGX", "Temporal regularization strength (couples consecutive time steps)."))
        tlform.addRow(QCoreApplication.translate("PHGX", "Alpha (temporal)"), self._tl_alpha)
        self._tl_type = QComboBox(); self._tl_type.addItems(["L2", "L1", "L1L2"])
        self._tl_type.setToolTip(QCoreApplication.translate("PHGX", "Temporal norm: L2 smooth, L1 blocky, L1L2 hybrid."))
        tlform.addRow(QCoreApplication.translate("PHGX", "Norm"), self._tl_type)

        self._tl_dt_weight = QCheckBox(QCoreApplication.translate("PHGX", "Weight by the interval between surveys"))
        self._tl_dt_weight.setChecked(True)
        self._tl_dt_weight.setToolTip(
            QCoreApplication.translate("PHGX", "Penalize the rate of change rather than the raw difference, so a "
            "month-long gap is allowed proportionally more change than an hour-long "
            "one. Weights are normalized by the median interval, so an evenly "
            "sampled series is unchanged and Alpha keeps its meaning. Untick to "
            "constrain every pair equally."))
        tlform.addRow(i18n.tr(self._tl_dt_weight))

        self._tl_windowed = QCheckBox(QCoreApplication.translate("PHGX", "Windowed (sliding window)"))
        self._tl_windowed.setToolTip(QCoreApplication.translate("PHGX", "Process consecutive time steps in overlapping windows: "
                                     "cheaper and lower-memory for long monitoring sequences."))
        self._tl_window = QSpinBox(); self._tl_window.setRange(2, 50); self._tl_window.setValue(3)
        self._tl_window.setEnabled(False)
        self._tl_windowed.toggled.connect(self._tl_window.setEnabled)
        tlform.addRow(i18n.tr(self._tl_windowed))
        tlform.addRow(QCoreApplication.translate("PHGX", "Window size"), self._tl_window)
        self._tl_lowmem = QCheckBox(QCoreApplication.translate("PHGX", "Low memory (sparse)"))
        self._tl_lowmem.setToolTip(QCoreApplication.translate("PHGX", "Use single-precision sparse operators to cut RAM "
                                   "(for many files / large meshes). Auto-enabled for "
                                   "large problems; check to force it on."))
        tlform.addRow(i18n.tr(self._tl_lowmem))

        panel.setVisible(False)
        return panel

    def _build_temperature_group(self) -> QWidget:
        """The shared temperature-correction panel, beside the model it corrects.

        Nothing is decided before the run. The inversion does not depend on the
        ground temperature, only what its models are reported at, so the user
        inverts, then sets the options and presses Apply, and the model on screen
        is corrected in place - and can be corrected differently, or put back,
        without inverting again. That holds for one survey as much as for a
        series. A correction applied with a guessed temperature is its own error
        source, which is why it is a button and never a default.

        The panel lives in widgets/temperature_panel.py and keeps its settings in
        the studio state, so Saved Results offers the same correction, with the
        same choices, on a result reopened there.
        """
        self._tc_box = temperature_panel.TemperatureOptions(
            shared=getattr(self.state, "temperature_settings", None))
        self._tc_box.applyRequested.connect(self._apply_temperature)
        self._tc_box.removeRequested.connect(lambda: self._apply_temperature(None))
        self._tc_box.set_available(False, _TC_WAITING)
        panel = QWidget()
        self._postprocess_layout = QVBoxLayout(panel)
        self._postprocess_layout.setContentsMargins(0, 0, 4, 0)
        self._postprocess_layout.addWidget(self._tc_box)
        side = ContentWidthScrollArea(minimum=320, maximum=380)
        side.setWidget(panel)
        self._postprocess_scroll = side
        return side

    def _apply_temperature(self, spec: Optional[Dict[str, Any]]) -> Tuple[bool, str]:
        """Correct the model on screen, whichever kind of result it is."""
        kind = getattr(self, "_map_result_kind", "")
        if kind == "timelapse" and self._tl_models_raw is not None:
            return self._apply_tl_temperature(spec)
        if kind == "single" and self._inv_mgr is not None:
            return self._apply_single_temperature(spec)
        self._tc_box.set_available(False, _TC_WAITING)
        return False, "Run an inversion first."

    def _single_survey_times(self) -> Tuple[Optional[list], Optional[list]]:
        """``(days, dates)`` of the one survey behind the single inversion.

        Its acquisition date, from the file name or header, is what places it
        in a dated temperature record; undated, only a constant or a
        single profile can correct it, and the correction says so. The file is
        the one recorded with the model, not whichever was previewed since.
        """
        stamp, _where = self._survey_time(self._inv_source)
        return ([0.0], [stamp]) if stamp is not None else (None, None)

    def _survey_time(self, path: Optional[Path]) -> Tuple[Optional[Any], str]:
        """``(time, where)`` one survey file was acquired, or ``(None, "")``.

        Read the way the file list reads a sequence - the name, then a date line
        at the top of the file - and ``where`` says which ("file name" or "file
        header"). Kept per file and modification time, because the data panel
        asks on every redraw and a file given a date line since must be read again.
        """
        if path is None:
            return None, ""
        try:
            key = (str(path), Path(path).stat().st_mtime)
        except OSError:
            key = (str(path), None)
        cache = getattr(self, "_survey_times", None)
        if cache is None:
            cache = self._survey_times = {}
        if key not in cache:
            timing = survey_timing.survey_timing([str(path)])
            stamp = timing.timestamps[0] if timing.timestamps else None
            cache[key] = (stamp, timing.sources[0] if stamp is not None else "")
        return cache[key]

    def _single_title(self) -> str:
        """The single model's heading, with the survey's time when it has one.

        Saved results heads the same run the same way, from the time the run
        recorded (``survey_time`` in its summary).
        """
        when = survey_timing.format_time(self._survey_time(self._inv_source)[0])
        return f"Resistivity · {when}" if when else "Resistivity"

    def _survey_time_record(self, path: Optional[Path]) -> Dict[str, Any]:
        """What the run records about the survey it inverts, for Saved results.

        The run stages the data under a generic name, so the file it came from
        and the time it was acquired survive only if they are written down here.
        """
        if path is None:
            return {}
        stamp, where = self._survey_time(path)
        record: Dict[str, Any] = {"source_file": Path(path).name}
        if stamp is not None:
            record.update(acquired=stamp.isoformat(sep=" "), acquired_from=where)
        return record

    def _show_format_help(self) -> None:
        """The ERT input-format note: formats, electrode file, survey times."""
        from PySide6.QtWidgets import QDialog, QTextBrowser

        doc_path = Path(__file__).with_name("ert_input_format.md")
        try:
            text = doc_path.read_text(encoding="utf-8")
        except Exception:  # noqa: BLE001
            _logger.debug("ERTProcessingModule._show_format_help: ignored error", exc_info=True)
            text = ("Pick the instrument / format, then add one file per survey. "
                    "Name each file with its time, year first: "
                    "site_2026-01-12_05-50-38.dat.")
        dlg = QDialog(self); dlg.setWindowTitle(QCoreApplication.translate("PHGX", "ERT input formats"))
        dlg.resize(760, 640); lay = QVBoxLayout(dlg)
        browser = QTextBrowser(); browser.setOpenExternalLinks(True)
        try:
            browser.setMarkdown(text)
        except Exception:  # noqa: BLE001
            _logger.debug("ERTProcessingModule._show_format_help: ignored error", exc_info=True)
            browser.setPlainText(text)
        lay.addWidget(browser)
        close = QPushButton(QCoreApplication.translate("PHGX", "Close")); close.clicked.connect(dlg.accept); lay.addWidget(close)
        dlg.exec()

    def _apply_single_temperature(self, spec: Optional[Dict[str, Any]]) -> Tuple[bool, str]:
        """Correct the single-inversion model on screen, or put the inverted one back."""
        mgr = self._inv_mgr
        if spec is None:
            self._inv_correction = None
            self._show_single_model(None)
            self.log("Temperature correction removed; the section shows the "
                     "resistivity as inverted.", "info")
            self._tc_box.show_applied(None)
            return True, ""
        days, dates = self._single_survey_times()
        try:
            corrected, report = temperature_panel.correct_series(
                mgr.paraDomain, np.asarray(mgr.model, dtype=float), spec,
                days=days, dates=dates)
        except Exception as exc:  # noqa: BLE001 - report it, never lose the result
            self.log(f"Temperature correction not applied: {exc}", "warn")
            self._tc_box.show_problem(f"Not applied: {exc}")
            return False, str(exc)
        self._inv_correction = {**report, "spec": dict(spec)}
        self._show_single_model(corrected)
        self.log(f"Temperature correction: {report['note']}", "success")
        self._tc_box.show_applied(report)
        return True, str(report["note"])

    def _show_single_model(self, corrected: Optional[np.ndarray]) -> None:
        """Draw the single model: as inverted, or corrected and titled as such."""
        mgr = self._inv_mgr
        self._inv_corrected = None if corrected is None else np.asarray(corrected, dtype=float)
        if self._inv_corrected is None:
            self._model_view.show_model(mgr, kind="ert", title=self._single_title())
        else:
            # The coverage the uncorrected view would fade by, accepted on the same
            # terms: a flat or empty coverage is no mask at all, and handed over as
            # one it would make every cell transparent.
            coverage = None
            try:
                cov = np.asarray(mgr.coverage(), dtype=float)
                if (cov.size == self._inv_corrected.size and np.isfinite(cov).any()
                        and float(np.nanmax(cov)) > float(np.nanmin(cov))):
                    coverage = cov
            except Exception:  # noqa: BLE001 - coverage is optional
                _logger.debug("ERTProcessingModule._show_single_model: coverage is optional", exc_info=True)
            self._model_view.show_field(
                mgr.paraDomain, self._inv_corrected, kind="ert", coverage=coverage,
                title=self._single_title()
                + temperature_panel.title_suffix(self._inv_correction))
        self._tabs.setCurrentWidget(self._model_tab)

    def _tl_summary(self) -> Dict[str, Any]:
        """The time-lapse result as its run recorded it, step titles included."""
        return {**(self._tl_result or {}), "step_titles": list(self._tl_step_titles)}

    def _apply_tl_temperature(self, spec: Optional[Dict[str, Any]]) -> Tuple[bool, str]:
        """Correct the time-lapse sections on screen, or put the inverted ones back.

        Works on the models this page holds; the correction is the same code
        Saved Results uses, so a run corrected on either page reads the same.
        Returns ``(ok, message)``.
        """
        raw = self._tl_models_raw
        if raw is None or self._tl_mesh is None:
            self._tc_box.set_available(False, _TC_WAITING)
            return False, "Run the time-lapse inversion first."
        if spec is None:
            self._tl_models = raw
            self._tl_correction = None
            self._redraw_tl()
            self.log("Temperature correction removed; the sections show the "
                     "resistivity as inverted.", "info")
            self._tc_box.show_applied(None)
            return True, ""
        days, dates = temperature_panel.series_survey_times(
            self._tl_summary(), raw.shape[1])
        try:
            corrected, report = temperature_panel.correct_series(
                self._tl_mesh, raw, spec, days=days, dates=dates)
        except Exception as exc:  # noqa: BLE001 - report it, never lose the result
            self.log(f"Temperature correction not applied: {exc}", "warn")
            self._tc_box.show_problem(f"Not applied: {exc}")
            return False, str(exc)
        self._tl_models = corrected
        # The spec travels with the report: it is what an export records as
        # having been applied, and it embeds the temperature data it read.
        self._tl_correction = {**report, "spec": dict(spec)}
        self._redraw_tl()
        self.log(f"Temperature correction: {report['note']}", "success")
        self._tc_box.show_applied(report)
        return True, str(report["note"])

    def _redraw_tl(self) -> None:
        """Show the current step again, on a scale fitted to the models now held."""
        self._seed_tl_color_range()
        self._show_tl_step(max(0, self._tl_step_combo.currentIndex()))
        self._tabs.setCurrentWidget(self._model_tab)

    def _on_tl_time_source_changed(self, *_args: Any) -> None:
        """Re-read the acquisition times when the allowed sources change; the
        pairs of forward and reciprocal files are found by them too."""
        if self._tl_all:
            self._set_tl_files(self._tl_all)

    def _set_timelapse(self, on: bool) -> None:
        """Choose time-lapse (True) or one survey (False), as the two buttons do.

        ``setChecked(False)`` on the checked button of an exclusive pair does
        nothing, so a script turning time-lapse off checks "One survey" instead.
        """
        (self._tl_mode if on else self._single_mode).setChecked(True)

    def _show_run_buttons(self, timelapse: bool) -> None:
        """The Run button of the mode chosen, and its progress row.

        A run still going keeps its progress row whatever the mode shows now.
        """
        self._invert_btn.setVisible(not timelapse)
        self._tl_btn.setVisible(timelapse)
        self._inv_progress_row.setVisible(not timelapse or self._inv_progress.isVisible())
        self._tl_progress_row.setVisible(timelapse or self._tl_progress.isVisible())

    def _run_blocker(self) -> str:
        """Why the Run button of the mode chosen cannot run now; "" when it can."""
        if self._tl_mode.isChecked():
            if len(self._tl_files) < 2:
                return ("Add at least two surveys to the list for a time-lapse run "
                        "- one file per survey, or drop a folder of them on the page.")
            if self._data_note and self._data_path is not None:
                return (f"{self._data_path.name} cannot be read for inversion as "
                        f"{self._instrument.currentText()}: {self._data_note} Every "
                        "survey is read with that format.")
            return ""
        if self._ert_data is None:
            if self._data_note:
                return f"This survey cannot be inverted: {self._data_note}"
            return "Add an ERT data file to run an inversion."
        return ""

    def _sync_run_ready(self) -> None:
        """Enable the Run button only when it can run, and say why it cannot.

        A file read under the wrong format would otherwise let the run start,
        and it would fail a minute later with pyGIMLi's IndexError.
        """
        if not hasattr(self, "_run_reason"):
            return
        reason = self._run_blocker()
        self._run_reason.setText(i18n.tr(reason))
        self._run_reason.setVisible(bool(reason))
        # A run in progress keeps its busy state; it is settled again after.
        if self._inv_busy is None:
            self._invert_btn.setEnabled(not reason or self._tl_mode.isChecked())
        if self._tl_busy is None:
            self._tl_btn.setEnabled(not reason or not self._tl_mode.isChecked())

    def _on_tl_mode(self, checked: bool) -> None:
        """Toggle between single-file and time-lapse inversion."""
        self._show_run_buttons(bool(checked))
        self._sync_tab_controls()
        self._sync_run_ready()
        # A time-lapse run builds its mesh from the first survey of the series.
        self._sync_mesh_engine()
        self._mesh_inputs_changed()
        self._sync_iteration_rows()
        # The Reciprocal errors tab shows the whole series in time-lapse mode.
        self._recip_inputs_changed()

    def _sync_iteration_rows(self) -> None:
        """Show the iteration limits the next run obeys, and only those.

        A single run stops at "Max iterations" or once χ² stops improving, on
        every engine. A time-lapse run on the in-house engine obeys both, its
        own iteration count and the χ² rule; ADTLERT takes the count and stops
        on the size of its model step instead of χ²; E4D runs each survey until
        χ² stops improving and takes no count; R2 and R3t decide both
        themselves. A greyed row says why on hover.
        """
        from PyHydroGeophysX.qt_apps.qt_utils import set_rows_enabled

        timelapse = self._tl_mode.isChecked()
        engine = self._engine.currentData()
        # The two limits share a name, so only the mode's own is on screen; a
        # limit the engine ignores stays visible but greyed, as elsewhere.
        self._set_rows_visible([self._iter_ceiling], not timelapse)
        self._set_rows_visible([self._iter], timelapse)
        set_rows_enabled([self._iter], engine not in ("e4d", "r2", "r3t"))
        plateau_applies = not timelapse or engine in ("pyhydro", "e4d")
        set_rows_enabled([self._plateau], plateau_applies)
        self._plateau.setToolTip(i18n.tr(_PLATEAU_TIP) if plateau_applies else (
            QCoreApplication.translate("PHGX", "Not used by this engine's time-lapse inversion: ADTLERT stops when its "
            "model step gets small, or at Max iterations.")
            if engine == "adtlert" else
            QCoreApplication.translate("PHGX", "Not used: R2 and R3t decide for themselves when the inversion is done.")))

    def _on_engine_changed(self, _index: int = -1) -> None:
        """Probe the selected CUDA backend without changing user parameters."""
        e4d = self._engine.currentData() == "e4d"
        self._set_rows_visible(self._e4d_rows, e4d)
        self._sync_iteration_rows()
        if e4d:
            self._check_e4d()
        program = self._r2_program_name()
        self._set_rows_visible(self._r2_rows, program is not None)
        if program is not None:
            self._load_r2_settings(program)
            self._check_r2()
        previous = self._adtlert_probe_worker
        if previous is not None and previous.isRunning():
            previous.cancel()
        if self._engine.currentData() != "adtlert":
            self._adtlert_probe_serial += 1
            self._adtlert_status.setVisible(False)
            return
        self._adtlert_probe_serial += 1
        serial = self._adtlert_probe_serial
        self._adtlert_runtime_ready = None
        self._adtlert_single_ready = None
        self._adtlert_timelapse_ready = None
        self._adtlert_checks = {}
        self._adtlert_status.setText(QCoreApplication.translate("PHGX", "Checking CUDA, cuDSS, NVRTC and GPU CGLS…"))
        theme.set_tone(self._adtlert_status, "hint")
        self._adtlert_status.setVisible(True)
        worker = ProcessProbeWorker(
            "PyHydroGeophysX.inversion.adtlert_diagnostics",
            arguments=["--stage", "runtime"],
            timeout_ms=60000,
        )
        worker.succeeded.connect(
            lambda result, token=serial: self._on_adtlert_probe_ok(token, result)
        )
        worker.failed.connect(
            lambda message, token=serial: self._on_adtlert_probe_failed(
                token, message
            )
        )
        self._adtlert_probe_worker = self.register_worker(worker, activity="Checking the GPU inversion engine")
        worker.start()

    def _on_adtlert_probe_ok(self, serial: int, result: Dict[str, Any]) -> None:
        if serial != self._adtlert_probe_serial:
            return
        if self._engine.currentData() != "adtlert":
            return
        self._adtlert_runtime_ready = True
        self._adtlert_checks["runtime"] = f"CUDA: ready ({result['device']})"
        self._start_adtlert_numerical_check(serial, "single")

    def _start_adtlert_numerical_check(self, serial: int, stage: str) -> None:
        self._adtlert_status.setText(
            " · ".join(self._adtlert_checks.values()) + f" · Checking {stage} inversion…"
        )
        worker = ProcessProbeWorker(
            "PyHydroGeophysX.inversion.adtlert_diagnostics",
            arguments=["--stage", stage], timeout_ms=120000,
        )
        worker.succeeded.connect(lambda result: self._finish_adtlert_numerical_check(serial, stage, True, ""))
        worker.failed.connect(lambda error: self._finish_adtlert_numerical_check(serial, stage, False, error))
        self._adtlert_probe_worker = self.register_worker(worker, activity="Checking the GPU inversion engine")
        worker.start()

    def _finish_adtlert_numerical_check(self, serial: int, stage: str, ok: bool, error: str) -> None:
        if serial != self._adtlert_probe_serial or self._engine.currentData() != "adtlert":
            return
        setattr(self, f"_adtlert_{stage}_ready", ok)
        label = "Single GPU" if stage == "single" else "Time-lapse GPU"
        self._adtlert_checks[stage] = f"{label}: {'passed' if ok else 'failed'}"
        if error:
            self.log(f"{label} self-test failed: {error}. Select In-house Gauss-Newton / PyHydro for this mode. "
                     "Run python -m PyHydroGeophysX.inversion.adtlert_diagnostics --report gpu-check.json for full diagnostics.", "warn")
        if stage == "single":
            self._start_adtlert_numerical_check(serial, "timelapse")
        else:
            self._adtlert_status.setText(i18n.tr(" · ".join(self._adtlert_checks.values())))
            healthy = self._adtlert_single_ready and self._adtlert_timelapse_ready
            theme.set_tone(self._adtlert_status, "ok" if healthy else "error")

    def _on_adtlert_probe_failed(self, serial: int, message: str) -> None:
        if serial != self._adtlert_probe_serial:
            return
        if self._engine.currentData() != "adtlert":
            return
        self._adtlert_runtime_ready = False
        self._adtlert_single_ready = False
        self._adtlert_timelapse_ready = False
        self._adtlert_status.setText(
            QCoreApplication.translate("PHGX", "CUDA check failed; GPU inversion is not verified. Select PyHydro CPU. {0}").format(message)
        )
        theme.set_tone(self._adtlert_status, "error")

    def _on_tl_ok(self, result: dict) -> None:
        self._agent_run_state = "completed"
        self._agent_run_error = ""
        # Pull out the in-memory mesh + models for the interactive viewer, then
        # drop them so the published result stays JSON-serializable.
        self._tl_mesh = result.pop("mesh", None)
        self._tl_models = result.pop("final_models", None)
        self._tl_coverage = result.pop("coverage", None)
        self._tl_step_titles = list(result.pop("step_titles", []) or [])
        self._tl_result = result
        self._tl_out = result.get("output_dir")
        self._tl_open.setEnabled(bool(self._tl_out))
        self._tl_export_btn.setEnabled(True)
        self._tl_correction = None
        self._tl_models_raw = None
        if self._tl_models is not None and self._tl_mesh is not None:
            self._tl_models_raw = np.asarray(self._tl_models, dtype=float)
            n_steps = int(self._tl_models_raw.shape[1])
            days, dates = temperature_panel.series_survey_times(
                self._tl_summary(), n_steps)
            self._tc_box.set_context(n_steps, dates is not None, days=days, dates=dates)
            self._tc_box.set_available(True)
            self._tc_box.show_applied(None)

        self._populate_tl_steps()
        engine = str(result.get("engine") or "pyhydro")
        requested_engine = str(result.get("engine_requested") or engine)
        solver = str(result.get("linearized_solver") or "")
        compute_note = "Joint χ² over all time steps."
        if engine == "e4d":
            compute_note = ("E4D time-lapse: χ² of each survey in turn, the last one "
                            "shown; each started from the solution before it.")
        elif engine in ("r2", "r3t"):
            compute_note = (f"{'R2' if engine == 'r2' else 'R3t'} difference inversion: χ² "
                            "of each survey in turn, the last one shown; each later survey "
                            "inverted against the first. λ is not used.")
        elif engine == "adtlert":
            compute_note += f" cuDSS forward · {solver or 'gpu_cgls'}."
        elif requested_engine == "adtlert":
            compute_note += " ADTLERT was unavailable; original PyHydro ERT used."
        self._quality_view.show_quality(
            {"chi2": result.get("chi2"), "iterations": len(result.get("chi2_history") or []) or None,
             "n_data": result.get("n_data"),
             # R2 and R3t choose their own smoothing; a λ shown would be one never used.
             "lambda": None if engine in ("r2", "r3t") else self._lam.value(),
             "method": (f"{engine} time-lapse "
                        f"{result.get('inversion_type', '')} "
                        f"({result.get('n_times')} steps)"),
             "note": compute_note},
            result.get("chi2_history"), title="Time-lapse ERT inversion")
        lowmem = " · low-memory" if result.get("save_memory") else ""
        n_vtk = len(result.get("vtk_step_paths") or [])
        self.log(f"Time-lapse inversion complete "
                 f"({engine}, {result.get('mode')}{lowmem}): "
                 f"{result.get('n_times')} steps, {result.get('mesh_cells')} cells. "
                 f"Saved VTK (combined + {n_vtk} per-step), npy, mesh. "
                 f"Pick a step in the Resistivity model tab; “Export results…” saves them.", "success")
        solid = dict(result.get("volume") or {})
        if solid.get("survey_3d"):
            self.log(f"Each step is a 3D model on {solid.get('cells', '?')} cells, drawn in "
                     "3D; the overview figure shows them in plan.", "info")
        elif solid:
            self.log(f"Inverted in 3D on {solid.get('cells', '?')} cells; each step is "
                     "shown as the section along the line, and Open 3D model shows its "
                     "volume.", "info")
        if requested_engine == "adtlert" and engine != "adtlert":
            self.log(
                "ADTLERT was requested but the time-lapse run used the original "
                "PyHydro ERT engine.",
                "warn",
            )
        elif engine == "adtlert":
            self.log(
                f"Compute backend: ADTLERT · cuDSS forward · {solver or 'gpu_cgls'}.",
                "info",
            )
        e4d = dict(result.get("e4d") or {})
        if e4d.get("run_dir"):
            self.log(f"E4D's own files (e4d.log, tl_sig*) and the 3D models "
                     f"resistivity_3d_timelapse.vtk are in {e4d['run_dir']}", "info")
            if e4d.get("missing_fit"):
                self.log("E4D overwrote the simulated data of survey(s) "
                         + ", ".join(str(int(s) + 1) for s in e4d["missing_fit"])
                         + " before they could be kept: their models are shown, their "
                         "fit is not known.", "warn")
        for engine_key, name in (("r2", "R2"), ("r3t", "R3t")):
            own = dict(result.get(engine_key) or {})
            if own.get("run_dir"):
                self.log(f"{name}'s own files: the baseline in {own.get('baseline_run_dir')}, "
                         f"the later surveys (f002_res.dat, ...) in {own['run_dir']}", "info")
                stops = list(own.get("stop") or [])
                if "iteration_cap" in stops:
                    self.log(f"{name} reached the iteration limit on survey(s) "
                             + ", ".join(str(i + 1) for i, s in enumerate(stops)
                                         if s == "iteration_cap")
                             + "; raise Max iterations to let them converge.", "warn")
        self.report_result(result)
        self.offer_map_export()

    def _populate_tl_steps(self) -> None:
        """Fill the step selector from the loaded time-lapse models and show step 0."""
        import numpy as np
        if self._tl_models is None or self._tl_mesh is None:
            self._tl_step_row.setVisible(False)
            return
        n = int(np.asarray(self._tl_models).shape[1])
        self._tl_step_combo.blockSignals(True)
        self._tl_step_combo.clear()
        for i in range(n):
            title = self._tl_step_titles[i] if i < len(self._tl_step_titles) else f"Time step {i + 1}"
            self._tl_step_combo.addItem(f"{i + 1}/{n}  ·  {title}", i)
        self._tl_step_combo.setCurrentIndex(0)
        self._tl_step_combo.blockSignals(False)
        self._tl_view_mode.blockSignals(True)
        self._tl_view_mode.setCurrentIndex(0)
        self._tl_view_mode.blockSignals(False)
        self._tl_step_row.setVisible(n > 1)
        # A profile's series inverted in 3-D: each step's volume one click away.
        self._model_3d_row.setVisible(bool(self._tl_volume_paths()))
        self._seed_tl_color_range()
        self._show_tl_step(0)
        self._tabs.setCurrentWidget(self._model_tab)

    def _tl_volume_paths(self) -> List[str]:
        """Each step's whole volume, when a profile's series was inverted in 3-D."""
        base = (Path(self._tl_recipe_path).resolve().parent
                if self._tl_recipe_path else Path.cwd())
        return [str(path if path.is_absolute() else base / path)
                for path in (Path(str(p)) for p in
                             (self._tl_result or {}).get("vtk_3d_step_paths") or [])]

    def _step_tl(self, delta: int) -> None:
        n = self._tl_step_combo.count()
        if n:
            self._tl_step_combo.setCurrentIndex((self._tl_step_combo.currentIndex() + delta) % n)

    def _on_tl_view_mode_changed(self, _index: int) -> None:
        """Switch between absolute resistivity and change from the baseline."""
        self._seed_tl_color_range()
        self._show_tl_step(self._tl_step_combo.currentIndex())

    @staticmethod
    def _percent_change(models, idx: int):
        """Percentage change of step ``idx`` against the first survey.

        The definition lives in the shared series widget, so this panel and the
        saved-results browser cannot drift into two different percentages.
        """
        from PyHydroGeophysX.qt_apps.widgets.series_view import percent_change

        return percent_change(models, idx)

    def _seed_tl_color_range(self) -> None:
        """Put every time step on one colour scale, for the mode on screen.

        The viewer sees a single step at a time, so left alone it autoscales each
        one to its own extremes and the change between steps is rescaled away.
        Limits come from the whole series at the 2–98 percentile, matching the
        exported summary figure, so a handful of poorly covered cells cannot
        flatten everything else.
        """
        from PyHydroGeophysX.qt_apps.widgets.series_view import series_color_limits

        if self._tl_models is None:
            return
        limits = series_color_limits(
            self._tl_models, str(self._tl_view_mode.currentData() or "model"))
        if limits is not None:
            self._model_view.set_color_range(*limits)

    def _show_tl_step(self, idx: int) -> None:
        import numpy as np
        if self._tl_models is None or self._tl_mesh is None:
            return
        models = np.asarray(self._tl_models, dtype=float)
        if idx < 0 or idx >= models.shape[1]:
            return
        self._map_result_kind = 'timelapse'
        self._sync_model_exports()
        cov = None
        if self._tl_coverage is not None:
            cov_all = np.asarray(self._tl_coverage, dtype=float)
            if cov_all.ndim == 2 and idx < cov_all.shape[0] and cov_all.shape[1] == models.shape[0]:
                cov = cov_all[idx]  # raw log-coverage, matching ERTManager.coverage()
        title = self._tl_step_titles[idx] if idx < len(self._tl_step_titles) else f"Time step {idx + 1}"
        if self._tl_view_mode.currentData() == "change":
            baseline = (self._tl_step_titles[0] if self._tl_step_titles
                        else "Time step 1")
            values, kind = self._percent_change(models, idx), "change"
            title = f"{title} − {baseline}" if idx else f"{title} (baseline)"
        else:
            values, kind = models[:, idx], "ert"
        # A corrected section looks exactly like an uncorrected one, so its
        # title says which it is.
        title += temperature_panel.title_suffix(self._tl_correction)
        volumes = self._tl_volume_paths()
        if idx < len(volumes):
            self._model_3d_path = volumes[idx]
        self._model_view.show_field(self._tl_mesh, values, kind=kind, coverage=cov, title=title)

    def _on_tl_failed(self, message: str, backend: bool) -> None:
        self._agent_run_state = "failed"
        self._agent_run_error = message
        self.fail_persisted_run(message, "ert.timelapse_inversion")
        text = f"Time-lapse inversion {'unavailable' if backend else 'failed'}: {message}"
        self.log(text, "warn" if backend else "error")
        # On the panel too: a survey its reader refused is the usual cause, and
        # the reason belongs where the files are listed, not only in the log.
        self._tl_info.setText(i18n.tr(text))

    def _reset_tl_button(self) -> None:
        if self._tl_busy is not None:
            self._tl_busy.finish()
            self._tl_busy = None
        self._tl_btn.setText(QCoreApplication.translate("PHGX", "Run time-lapse inversion"))
        self._tl_progress.setVisible(False)
        self._show_run_buttons(self._tl_mode.isChecked())
        self._sync_run_ready()

    def _tl_result_files(self) -> List[str]:
        """All result files worth exporting (figure + data + config), de-duplicated."""
        res = self._tl_result or {}
        files: List[str] = []
        for key in ("figure_paths", "data_paths"):
            files.extend(res.get(key) or [])
        if res.get("config_path"):
            files.append(res["config_path"])
        seen, unique = set(), []
        for f in files:
            if f and f not in seen and Path(f).exists():
                seen.add(f); unique.append(f)
        return unique

    class _ExportWorker(TaskWorker):
        """A TaskWorker that reports ``progressed(current, total, label)``.

        The page's status bar shows that line while the export runs.
        """

        progressed = Signal(int, int, str)

        def __init__(self, fn: Callable[..., Any], **kwargs: Any) -> None:
            super().__init__(fn, **kwargs)
            self._kwargs["progress"] = self.progressed.emit

    def _export_tl_results(self, folder: Optional[str] = None) -> Optional[str]:
        """Copy the time-lapse result files (VTK, npy, mesh, CSV, figure) to a folder.

        Chosen here, on the page, the export runs on a worker thread with its
        progress in the status bar: for a long series it is hundreds of VTK
        files and a table of millions of numbers, which would hold the window
        still. Given a ``folder`` - the assistant's export - it runs
        to the end before returning, as that caller expects.
        """
        if not self._tl_result:
            self.log("Run the time-lapse inversion first.", "warn")
            return None
        files = self._tl_result_files()
        if not files:
            self.log("No time-lapse result files found to export.", "warn")
            return None
        interactive = not folder
        if not folder:
            selected = select_directory(
                self, QCoreApplication.translate("PHGX", "Export time-lapse results to folder"),
                self.state.output_dir or Path.cwd(),
            )
            folder = str(selected) if selected else ""
            if not folder:
                return None
        dest = io_utils.ensure_dir(Path(folder))
        # What is on screen now, so a step or a correction changed while the
        # export runs does not reach half of it.
        job = dict(
            files=files, src_root=Path(self._tl_result.get("output_dir") or ""), dest=dest,
            mesh=self._tl_mesh,
            models=None if self._tl_models is None else np.array(self._tl_models, dtype=float),
            coverage=self._tl_coverage, step_labels=list(self._tl_step_titles or []) or None,
            correction=dict(self._tl_correction) if self._tl_correction else None,
        )
        if not interactive:
            self._on_tl_exported(self._export_timelapse(**job))
            return str(dest)
        worker = self._ExportWorker(self._export_timelapse, **job)
        worker.succeeded.connect(self._on_tl_exported)
        worker.failed.connect(
            lambda message: self.log(f"Time-lapse export failed: {message}", "error"))
        worker.finished.connect(lambda: self._tl_export_btn.setEnabled(bool(self._tl_result)))
        self._tl_export_btn.setEnabled(False)
        self.log(f"Exporting the time-lapse results to {dest}…", "info")
        self.register_worker(worker, activity="Exporting the time-lapse results")
        worker.start()
        return str(dest)

    def _on_tl_exported(self, summary: Dict[str, Any]) -> None:
        """Report a finished time-lapse export."""
        for warning in summary.get("warnings") or []:
            self.log(warning, "warn")
        self.log(f"Exported {summary.get('files', 0)} time-lapse result file(s) to "
                 f"{summary.get('dest', '')}", "success")
        correction = summary.get("correction")
        if correction:
            reference = float(correction.get("reference_temperature_C", 25.0))
            self.log(
                f"The series on screen, corrected to {reference:g} °C, is in "
                f"final_models_temperature_corrected.npy, "
                f"timelapse_resistivity_temperature_corrected.vtk and the cell CSV; "
                f"temperature_correction.json records what was applied. "
                f"final_models.npy, the per-step VTKs and the figure are the "
                f"models as inverted.", "info")

    @staticmethod
    def _export_timelapse(*, files: List[str], src_root: Path, dest: Path, mesh: Any,
                          models: Any, coverage: Any, step_labels: Optional[List[str]],
                          correction: Optional[Dict[str, Any]],
                          progress: Optional[Callable[[int, int, str], None]] = None,
                          ) -> Dict[str, Any]:
        """Write a time-lapse export into ``dest``; safe to run off the GUI thread.

        Copies the run's files, keeping the ``vtk_steps`` folder, then writes
        the per-cell table and, with a temperature correction on screen, the
        corrected series. Touches no widget: what went wrong comes back in the
        summary's ``warnings`` for the page to log.
        """
        report = progress or (lambda current, total, label: None)
        warnings: List[str] = []
        total = len(files)
        every = max(1, -(-total // 20))          # about twenty updates, however many files
        copied = 0
        report(0, total, f"Exporting: copying files 0/{total}")
        for index, f in enumerate(files, start=1):
            try:
                src = Path(f)
                # Preserve the vtk_steps/ subfolder so per-step VTKs stay grouped.
                rel = src.relative_to(src_root) if src_root and src_root in src.parents else Path(src.name)
                target = dest / rel
                io_utils.ensure_dir(target.parent)
                shutil.copy2(str(src), str(target))
                copied += 1
            except Exception as exc:  # noqa: BLE001
                warnings.append(f"Could not copy {Path(f).name}: {exc}")
            if index % every == 0 or index == total:
                report(index, total, f"Exporting: copying files {index}/{total}")
        written = 0
        # The per-cell table: the copied files are all PyGIMLi meshes and NumPy
        # arrays, and this is the one export a collaborator can open without
        # either, with one row per cell and one column per time step.
        if mesh is None or models is None:
            warnings.append("Time-lapse models are not in memory, so no CSV was written; "
                            "the mesh and .npy files were still copied.")
        else:
            report(0, 1, "Exporting: writing the per-cell table (CSV)")
            try:
                from PyHydroGeophysX.data_processing.model_csv import export_model_csv

                # The table holds the series on screen; with a correction applied
                # its columns say the temperature they are reported at.
                written += len(export_model_csv(
                    dest, mesh, models, value_name=_value_name(correction), units="ohm.m",
                    coverage=coverage, step_labels=step_labels))
            except Exception as exc:  # noqa: BLE001 - the copies already succeeded
                warnings.append(f"Could not write the time-lapse CSV: {exc}")
        # The temperature-corrected series beside the inverted one. The files
        # copied from the run are the models as inverted; with a correction on
        # screen, an export of only those would hand over a different series
        # from the one being looked at, and nothing in it would say so.
        if correction and models is not None:
            report(0, 1, "Exporting: writing the temperature-corrected series")
            series = np.asarray(models, dtype=float)
            try:
                np.save(dest / "final_models_temperature_corrected.npy", series)
                written += 1
                io_utils.write_json(dest / "temperature_correction.json", correction)
                written += 1
                try:
                    import pygimli as pygimli

                    from PyHydroGeophysX.core.mesh_serialization import via_ascii_path

                    combined = pygimli.Mesh(mesh)
                    for index in range(series.shape[1]):
                        combined[f"resistivity_t{index}"] = series[:, index]
                    via_ascii_path(combined.exportVTK,
                                   dest / "timelapse_resistivity_temperature_corrected.vtk",
                                   mode="write")
                    written += 1
                except Exception as exc:  # noqa: BLE001 - the arrays are already written
                    warnings.append(f"Temperature-corrected VTK skipped: {exc}")
            except Exception as exc:  # noqa: BLE001 - the copies already succeeded
                warnings.append(f"Could not write the temperature-corrected models: {exc}")
        return {"dest": str(dest), "files": copied + written, "warnings": warnings,
                "correction": correction}

    def _sync_model_exports(self) -> None:
        """Offer the export of the result the model tab shows: one model or a series."""
        series = getattr(self, "_map_result_kind", "") == "timelapse"
        self._model_export_btn.setVisible(not series)
        self._tl_export_btn.setVisible(series)
        self._tl_open.setVisible(series)

    def _open_tl_output(self) -> None:
        out = self._tl_out or str(self.state.output_dir or "")
        if out and Path(out).exists():
            from PySide6.QtCore import QUrl
            from PySide6.QtGui import QDesktopServices
            QDesktopServices.openUrl(QUrl.fromLocalFile(out))
        else:
            self.log("No time-lapse output yet.", "warn")

    # -- rendering / publish -------------------------------------------------
    def _update_info(self) -> None:
        """The data panel: the electrodes, the readings, the file and its time."""
        if not self._x and self._data_path is None:
            self._info.setText(QCoreApplication.translate("PHGX", "No data loaded."))
            return
        rhoa_txt = ""
        if self._pseudo:
            vals = np.asarray([p[2] for p in self._pseudo], dtype=float)
            vals = vals[np.isfinite(vals) & (vals > 0)]
            if vals.size:
                rhoa_txt = f"<br>ρa: {vals.min():.0f}–{vals.max():.0f} Ω·m"
        # A file read under the wrong format still fills this panel with a
        # plausible electrode and measurement count, so the reason it cannot be
        # inverted belongs next to those numbers and not only in the log.
        note_txt = ""
        if self._data_note:
            note_txt = (f"<br><span style='color:{theme.color('red')}'>Not usable for "
                        f"inversion: {self._data_note} Check the Instrument / "
                        f"format setting.</span>")
        # When the survey was measured, and from what: the same reading the file
        # list and the model heading use, so the three never disagree.
        stamp, where = self._survey_time(self._data_path)
        when_txt = (f"<br>Acquired: {survey_timing.format_time(stamp, seconds=True)} "
                    f"(from the {where})" if stamp is not None else "")
        partner_txt = (f"<br>+ reciprocal file: {self._data_partner.name}"
                       if self._data_partner is not None else "")
        self._info.setText(
            QCoreApplication.translate("PHGX", "{0}<br>Measurements: {1:,}<br>Data: {2}{3}{4}{5}{6}").format(self._electrode_summary(), int(self._n_meas or 0), self._data_path.name if self._data_path else '—', partner_txt, when_txt, rhoa_txt, note_txt)
        )

    def _refresh(self) -> None:
        self._update_info()
        self._draw_pseudosection()
        self._sync_run_ready()
        self._publish()
        # Every change of data or electrodes passes through here, and the mesh
        # is built around the electrodes.
        self._mesh_inputs_changed()

    def _coords(self) -> List[List[float]]:
        """``[x, z]`` per electrode; ``[x, y, z]`` for a 3-D survey."""
        if self._survey_3d:
            return [[self._x[i], self._y[i], self._z[i]] for i in range(len(self._x))]
        return [[self._x[i], self._z[i]] for i in range(len(self._x))]

    def _export_electrodes(self) -> None:
        if not self._x:
            self.log("No electrodes to export.", "warn")
            return
        path, _ = QFileDialog.getSaveFileName(self, QCoreApplication.translate("PHGX", "Export electrodes"), "electrodes.csv", "CSV (*.csv)")
        if not path:
            return
        if self._survey_3d:
            rows = [(self._labels[i], self._x[i], self._y[i], self._z[i])
                    for i in range(len(self._x))]
            io_utils.write_csv(path, rows, header=["label", "x", "y", "z"])
        else:
            rows = [(self._labels[i], self._x[i], self._z[i]) for i in range(len(self._x))]
            io_utils.write_csv(path, rows, header=["label", "x", "z"])
        self._electrode_path = Path(path)
        self.log(f"Exported {len(rows)} electrodes to {path}", "success")
        self._publish()

    def _export_geometry(self) -> None:
        if not self._x:
            self.log("No electrodes to export.", "warn")
            return
        path, _ = QFileDialog.getSaveFileName(self, QCoreApplication.translate("PHGX", "Export geometry"), "ert_geometry.json", "JSON (*.json)")
        if not path:
            return
        geometry = {
            "method": "ERT",
            "instrument": self._instrument.currentText(),
            "num_electrodes": len(self._x),
            "num_measurements": self._n_meas,
            "electrodes": self._coords(),
            "labels": self._labels,
            "data_file": str(self._data_path) if self._data_path else "",
        }
        io_utils.write_json(path, geometry)
        self.log(f"Exported survey geometry to {path}", "success")
        self._publish(geometry_path=path)

    def _export_resistivity_model(self) -> None:
        mgr = getattr(self, "_inv_mgr", None)
        if mgr is None:
            self.log("Run the ERT inversion first.", "warn")
            return
        folder = select_directory(
            self, QCoreApplication.translate("PHGX", "Export resistivity model to folder"),
            self.state.output_dir or Path.cwd(),
        )
        if not folder:
            return
        try:
            import numpy as np

            from PyHydroGeophysX.core.mesh_serialization import via_ascii_path
            from PyHydroGeophysX.data_processing.model_csv import export_model_csv

            out = io_utils.ensure_dir(folder)
            mesh = mgr.paraDomain
            model = np.asarray(mgr.model, dtype=float)  # resistivity (ohm-m)
            # The table holds what is on screen, so a temperature-corrected model
            # is exported as one, with the temperature in its column name.
            shown = self._inv_corrected if self._inv_corrected is not None else model
            np.save(out / "resistivity_model.npy", model)
            try:
                cov = np.asarray(mgr.coverage(), dtype=float)
                np.save(out / "coverage.npy", cov)
            except Exception:  # noqa: BLE001 - coverage is optional
                _logger.debug("ERTProcessingModule._export_resistivity_model: coverage is optional", exc_info=True)
                cov = None
            # The CSV is written before the PyGIMLi files because it is the one
            # a collaborator without PyGIMLi can actually open, and a .bms write
            # that fails should not cost them the table as well.
            export_model_csv(
                out, mesh, shown,
                value_name=_value_name(self._inv_correction if shown is not model else None),
                units="ohm.m", coverage=cov,
            )
            # numpy takes wide paths, PyGIMLi's writers do not; a folder Windows'
            # ANSI codepage cannot represent (a localized "Documents" folder,
            # say) needs the write staged through a temporary ASCII one.
            # Otherwise the .npy is written and the .bms fails.
            via_ascii_path(mesh.save, out / "resistivity_mesh.bms", mode="write")
            mesh["resistivity"] = model
            via_ascii_path(mesh.exportVTK, out / "resistivity_model.vtk", mode="write")
            if shown is not model:
                # Beside the inverted model, never in place of it.
                np.save(out / "resistivity_model_temperature_corrected.npy", shown)
                io_utils.write_json(out / "temperature_correction.json", self._inv_correction)
                mesh["resistivity"] = shown
                via_ascii_path(mesh.exportVTK,
                               out / "resistivity_model_temperature_corrected.vtk",
                               mode="write")
                mesh["resistivity"] = model
                self.log(
                    f"The model on screen, corrected to "
                    f"{float(self._inv_correction['reference_temperature_C']):g} °C, is "
                    f"in resistivity_model_temperature_corrected.npy/.vtk and the cell "
                    f"CSV; temperature_correction.json records what was applied. "
                    f"resistivity_model.npy/.vtk are the model as inverted.", "info")
            self.log(f"Exported resistivity model (csv + npy + bms + vtk) to {out}", "success")
        except Exception as exc:  # noqa: BLE001
            self.log(f"Resistivity model export failed: {exc}", "error")

    def export_actions(self):
        actions = []
        if getattr(self, "_inv_mgr", None) is not None or self._tl_result:
            actions.append(("Add displayed result to Project Map…", self.add_to_map))
        if getattr(self, "_inv_mgr", None) is not None:
            actions.append((
                "Resistivity model (CSV + npy + mesh + VTK)",
                self._export_resistivity_model,
            ))
        if self._tl_result:
            actions.append((
                "Time-lapse results (CSV + npy + mesh + VTK + figures)",
                self._export_tl_results,
            ))
        if self._x:
            actions.append(("Electrode positions (CSV)", self._export_electrodes))
            actions.append(("Survey geometry (JSON)", self._export_geometry))
        return actions

    def _publish(self, geometry_path: Optional[str] = None) -> None:
        result = {
            "instrument": self._instrument.currentText(),
            "num_electrodes": len(self._x),
            "num_measurements": self._n_meas,
            "electrodes": self._coords(),
            "electrode_file": str(self._electrode_path) if self._electrode_path else "",
            "data_file": str(self._data_path) if self._data_path else "",
        }
        if geometry_path:
            result["geometry_path"] = geometry_path
        self.report_result(result)
