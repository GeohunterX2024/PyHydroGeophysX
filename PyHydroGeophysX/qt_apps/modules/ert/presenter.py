"""The ERT page: the assistant's interface and electrode editing (plan M4.5).

Part of :class:`~.page.ERTProcessingModule`, split from the former
``ert_processing.py`` by area; the methods are unchanged.
"""

from __future__ import annotations

from .common import (
    Any,
    Dict,
    Path,
    QCoreApplication,
    _INSTRUMENTS,
    _LAMBDA_BOUNDS,
    _logger,
    json,
    np,
    re,
    survey_timing,
    theme,
)


class _Presenter:

    # -- AQUAH agent interface ----------------------------------------------
    def show_run_inputs(self, inputs: Dict[str, Any]) -> str:
        """Open the automatic run's surveys here so this panel is not empty.

        The workflow inverts its own copy in its own process; this loads the
        same files for display, through the same handlers the assistant uses,
        so the pseudosection and electrode layout are on screen while the run
        works. Nothing is inverted here.

        Anything already loaded is left alone: a run must not throw away work
        somebody was in the middle of.
        """
        if self._ert_data is not None or self._tl_files:
            return ""
        surveys = [str(p) for p in (inputs.get("time_lapse_files") or [])]
        single = inputs.get("data_file")
        electrodes = inputs.get("electrode_file")
        # The run's instrument, not this panel's. There is no format auto-detect
        # anywhere here - the device is chosen, not guessed - so leaving the
        # dropdown on its own default would read the run's files with the wrong
        # reader: an E4D .ohm parsed as a unified file has its leading index
        # column taken for electrode A, and every quadrupole then lands out of
        # bounds, so the panel would list the files and draw nothing.
        instrument = str(inputs.get("instrument") or "").strip()
        if not instrument and (surveys or single):
            # Nobody chose one, so the header decides - as it does in the run.
            instrument = self._instrument_from_header((surveys or [str(single)])[0])
        if instrument:
            self._agent_set_instrument(instrument)
        # Electrodes first: a survey file carrying no geometry of its own picks
        # them up as it loads, and loading them afterwards would not be applied.
        if electrodes:
            self._agent_load_electrodes(str(electrodes))
        if surveys:
            if self._agent_add_timelapse_files(surveys).get("status") != "ok":
                return ""
            self._agent_preview_timelapse(0)
            return (f"{len(surveys)} surveys, showing "
                    f"{Path(surveys[0]).name}")
        if single:
            if self._agent_load(str(single), None).get("status") == "failed":
                return ""
            return Path(str(single)).name
        return ""

    def show_run_stage(self, tool: str) -> str:
        """Follow the run through this page's own tabs.

        Loading belongs on the Data tab, a finished inversion on the model,
        and the quality check on the quality view. Without this the page would
        stay on whichever tab it opened with while the run moves on underneath it.
        """
        views = {
            "load_ert_surveys": (self._pseudo_widget, "Data"),
            "invert_ert": (self._model_tab, "Resistivity model"),
            "invert_time_lapse": (self._model_tab, "Resistivity model"),
            "evaluate_inversion": (self._quality_view, "Inversion quality"),
        }
        widget, name = views.get(str(tool), (None, ""))
        if widget is None:
            return ""
        self._tabs.setCurrentWidget(widget)
        return name

    @staticmethod
    def _instrument_from_header(path: str) -> str:
        """The instrument a file's header names, as the run reads it; "" if none."""
        try:
            from PyHydroGeophysX.agents.ert_loader_agent import ERTLoaderAgent

            return str(ERTLoaderAgent(api_key="")._detect_instrument_from_header(str(path)) or "")
        except Exception:  # noqa: BLE001 - nothing detected is no choice made
            _logger.debug("ERTProcessingModule._instrument_from_header: nothing detected is no choice made", exc_info=True)
            return ""

    def _agent_set_instrument(self, instrument: str) -> bool:
        """Point the format dropdown at ``instrument``. True when it matched."""
        key = str(instrument).strip().lower()
        for index, (label, value) in enumerate(_INSTRUMENTS):
            if value is not None and key in (value.lower(), label.lower()):
                self._instrument.setCurrentIndex(index)
                return True
        return False

    def agent_describe(self) -> Dict[str, Any]:
        return {
            "module": self.module_key,
            "title": self.module_title,
            "state": self._agent_status(),
            "actions": [
                {"name": "load_data", "args": {"path": "str", "instrument": "str (optional)"},
                 "desc": ("Load ERT data; pick the instrument/format that matches the file "
                          "(no auto-detect). One of: " +
                          ", ".join(v for _, v in _INSTRUMENTS if v) + ".")},
                {"name": "load_electrodes", "args": {"path": "str"},
                 "desc": ("Load an optional electrode geometry file (x, z table; x, y, z "
                          "for a 3-D survey's electrodes covering an area).")},
                {"name": "list_electrodes", "args": {},
                 "desc": ("List electrodes as index, label, x, z (and y in a 3-D survey), "
                          "and whether each came from the loaded file or was added "
                          "afterwards.")},
                {"name": "add_electrode", "args": {"x": "float", "z": "float",
                                                   "y": "float (optional, 3-D survey)",
                                                   "label": "str (optional)"},
                 "desc": "Append an electrode at (x, z). It carries no measurements."},
                {"name": "move_electrode", "args": {"index": "int", "x": "float (optional)",
                                                    "y": "float (optional, 3-D survey)",
                                                    "z": "float (optional)"},
                 "desc": ("Move electrode `index` (0-based). Give x, z, or both; the "
                          "omitted coordinate is left alone.")},
                {"name": "delete_electrode", "args": {"index": "int"},
                 "desc": ("Remove electrode `index` (0-based). Measurements that "
                          "reference it are dropped when the data are serialized.")},
                {"name": "set_electrode_label", "args": {"index": "int", "label": "str"},
                 "desc": "Rename electrode `index` (0-based)."},
                {"name": "clear_electrodes", "args": {},
                 "desc": "Remove every electrode. Load a geometry file to start over."},
                {"name": "apply_filter",
                 "args": {"min_rhoa": "float", "max_rhoa": "float", "max_error": "float (%)",
                          "drop_nonpositive_rhoa": "bool",
                          "min_voltage": "float (V)",
                          "min_current": "float (A)",
                          "max_geometric_factor": "float",
                          "max_contact_resistance": "float (ohm)",
                          "max_stacking_spread": "float (fraction)",
                          "max_reciprocal_error": "float (fraction)",
                          "average_reciprocal_pairs": "bool (optional)"},
                 "desc": ("Filter measurements by apparent resistivity range and max relative "
                          "error (20 % unless set; 0 is off). average_reciprocal_pairs=true "
                          "first averages each reading with its reciprocal into one reading "
                          "(mean resistance, the pair's difference as its error, never below "
                          "reciprocal_error_floor) - check 0, off by default, for data "
                          "measured both ways. The optional criteria turn on "
                          "'More checks'; each is skipped where the loaded file does not "
                          "carry the field it tests. With More checks on, a criterion the "
                          "call does not name keeps the panel's value, which starts at: "
                          "drop rhoa <= 0, |V| >= 1e-5 V, |I| >= 1e-4 A, |k| <= 20 x the "
                          "file's median, contact R <= 30000 ohm, stacking spread <= 0.5, "
                          "reciprocal error <= 0.05. Pass 0 (false for the rhoa check) to "
                          "switch one off.")},
                {"name": "set_params", "args": {"params": {"<key>": "value"}},
                 "desc": ("Set parameters. Shared by single + time-lapse inversion: lambda, "
                          "max_iterations, relative_error, time_lapse (bool). "
                          "Mesh (the Mesh tab; each maps to a PyGIMLi parameter-mesh "
                          "option): mesh_quality (smallest triangle angle, 20-34), "
                          "para_depth (m, 0 = auto), para_max_cell_size (m^2, 0 = no "
                          "limit), para_boundary (inverted region past the end "
                          "electrodes, in electrode spacings, 0.5-20, default 2), "
                          "surface_nodes (nodes between neighbouring electrodes, 1-8), "
                          "outer_width (outer region in electrode spreads, 0 = PyGIMLi's "
                          "4), outer_max_cell_size (m^2, 0 = no limit); a value out of "
                          "range is refused, not clipped. mesh_file (path to a "
                          ".bms/.msh/.vtk/.poly mesh, an E4D mesh's .1.node/.1.ele, or "
                          "an E4D mesh configuration .cfg, meshed on import, "
                          "to invert on instead of a generated one; the region to invert "
                          "needs marker 2 or above, and '' goes back to generating it). "
                          "A-priori zones: zones, a list of {name, polygon: [[x, z], ...] "
                          "in mesh coordinates (x along the line, z the elevation), "
                          "resistivity (ohm-m), fixed (bool)}; it replaces the zones on "
                          "the Mesh tab, and [] removes them. Every engine starts from "
                          "them; the in-house pyhydro engine also regularizes toward "
                          "them and does not invert a fixed zone, and the ADTLERT "
                          "time-lapse backend takes no zone values. conform_to_zones "
                          "(bool) rebuilds a generated mesh along the zone outlines, so "
                          "no cell straddles one; decouple_zones (bool) drops the "
                          "smoothness across the outlines so the model may jump there - "
                          "every engine honours it. "
                          "Error model: error_source (file/estimate/max, "
                          "or stack - each reading's stacking spread with the estimate in "
                          "quadrature, for data that record it - or reciprocal - each "
                          "reading's error from the power law dR = 10^b * R^m fitted to the "
                          "reciprocal pairs: the survey's own for a single inversion, one fit "
                          "over every survey for time-lapse; for data measured both ways), "
                          "reciprocal_error_floor (fraction, default 0.01: the smallest error "
                          "the model or an averaged pair gives), "
                          "error_model_fit ('all', the default: the model is fitted to every "
                          "reciprocal pair as read; 'kept': only to the pairs the applied QC "
                          "filter kept - its reciprocal-error limit removes outlier pairs; "
                          "the Reciprocal errors tab's Fit to, which every fit of the model "
                          "follows), "
                          "absolute_error (Ohm). pair_reciprocal_files (bool, default true): "
                          "a forward file and its reciprocal file in the list ('recip' in the "
                          "name, measured just after) are one survey; false makes every file "
                          "a survey of its own. Convergence: plateau_tolerance (fraction), "
                          "max_total_iterations, engine (pyhydro/pygimli/adtlert/e4d/r2/"
                          "r3t; e4d is PNNL's external 3D code, set up in the E4D rows the "
                          "page shows for it, and runs on Linux, or on Windows only "
                          "inside WSL 2 - elsewhere it writes the E4D run folder and "
                          "stops; r2 (2D profiles) and r3t (3D) are Binley's programs "
                          "that ResIPy runs, found in ResIPy, native on Windows and "
                          "through Wine elsewhere; they choose their own smoothing, so "
                          "lambda and auto_lambda do not apply to them). "
                          "Mode: inversion_mode ('quick', the default, skips the k check "
                          "and the lambda search; 'full' runs both). It is a preset, so "
                          "geometric_factor_policy or auto_lambda sent after it in the "
                          "same object override it. "
                          "Geometric factors: geometric_factor_policy "
                          "('fix' recomputes k numerically when a homogeneous forward run "
                          "does not return the model resistivity, 'check' only reports, "
                          "'off' skips), geometric_factor_tolerance. "
                          "Outlier rejection: reject_outliers (bool), outlier_threshold "
                          "(sigma), outlier_passes, min_data_fraction. "
                          "Auto-lambda: auto_lambda (bool), target_chi2, chi2_tolerance, "
                          "max_lambda_trials. "
                          "Time-lapse-only: tl_alpha, tl_norm (L2/L1/L1L2), tl_windowed, "
                          "tl_window_size, tl_low_memory. ADTLERT time-lapse currently "
                          "requires windowed mode and a common survey geometry.")},
                {"name": "preview_mesh", "args": {},
                 "desc": ("Show the Mesh tab: the mesh the next inversion will run on, "
                          "built from the loaded data (the first file in time-lapse "
                          "mode) and the mesh settings, with the zones on it. Reports "
                          "its cell counts, and how many cells each zone covers, once "
                          "it is built.")},
                {"name": "import_mesh", "args": {"path": "str"},
                 "desc": ("Invert on a mesh built elsewhere - .bms, .msh, .vtk, an E4D "
                          "mesh (.1.node / .1.ele) or configuration (.cfg), or one the 3D "
                          "Mesh Builder built. It is read and checked against the loaded "
                          "survey now, then shown on the Mesh tab, in 3D for a 3D mesh. "
                          "On a 3D mesh the in-house and PyGIMLi engines invert the "
                          "profile laid along x at y = 0 and show the section along it; "
                          "the whole model is saved as resistivity_3d.vtk. A time-lapse "
                          "series needs a 2D mesh. set_params mesh_file '' goes back to "
                          "a generated mesh.")},
                {"name": "run_inversion", "args": {},
                 "desc": ("Run a single-time ERT inversion. Stages run in the order that "
                          "lowers chi2: fix the error model, iterate at the set lambda "
                          "until the misfit flattens, optionally reject data the model "
                          "cannot explain, and only then search for a lambda whose chi2 "
                          "lands inside target_chi2 +/- chi2_tolerance. The run at the "
                          "settings you gave is always kept for comparison.")},
                {"name": "add_timelapse_files", "args": {"paths": ["str", "str"], "append": "bool (optional)"},
                 "desc": ("Add ERT files for time-lapse inversion (one file per time step, like seismic "
                          "shots). append=true adds to the current list; otherwise replaces it. Files load "
                          "with the selected instrument; times are parsed from filenames when dated. "
                          "A survey written as two files - a forward file and its reciprocal "
                          "('recip' in the name) - becomes one time step at the forward "
                          "file's time, both files merged, while pair_reciprocal_files is on; "
                          "a reciprocal file without a forward file is left out and named.")},
                {"name": "list_timelapse_files", "args": {},
                 "desc": ("List the ordered time-lapse surveys with their parsed time labels; a "
                          "paired survey names its reciprocal file.")},
                {"name": "remove_timelapse_files", "args": {"indices": ["int"]},
                 "desc": ("Remove time-lapse surveys by 0-based index (a paired survey's "
                          "reciprocal file goes with it), or omit to clear all.")},
                {"name": "preview_timelapse_file", "args": {"index": "int"},
                 "desc": "Load one time-lapse file (0-based index) into the electrode + pseudosection view."},
                {"name": "run_timelapse", "args": {},
                 "desc": "Run time-lapse ERT inversion (needs >=2 files)."},
                {"name": "export_timelapse", "args": {"folder": "str"},
                 "desc": ("Export the last time-lapse result to a folder: combined VTK, per-step VTKs, "
                          "final_models.npy, mesh (.bms), times CSV, and the figure.")},
                {"name": "get_status", "args": {},
                 "desc": ("Report inversion_status, inversion_running, has_model, and result_summary "
                          "(fit metrics, model range, source and output paths), plus data/settings. "
                          "Completed results are available before saving or adding them to Map.")},
            ],
        }

    def agent_apply(self, action: str, args: Dict[str, Any]) -> Dict[str, Any]:
        args = args or {}
        handlers = {
            "load_data": lambda: self._agent_load(args.get("path"), args.get("instrument")),
            "load_electrodes": lambda: self._agent_load_electrodes(args.get("path")),
            "list_electrodes": lambda: self._agent_list_electrodes(),
            "add_electrode": lambda: self._agent_add_electrode(
                args.get("x"), args.get("z"), args.get("label"), args.get("y")),
            "move_electrode": lambda: self._agent_move_electrode(
                args.get("index"), args.get("x"), args.get("z"), args.get("y")),
            "delete_electrode": lambda: self._agent_delete_electrode(args.get("index")),
            "set_electrode_label": lambda: self._agent_set_electrode_label(
                args.get("index"), args.get("label")),
            "clear_electrodes": lambda: self._agent_clear_electrodes(),
            "apply_filter": lambda: self._agent_apply_filter(args),
            "set_params": lambda: self._agent_set_params(args.get("params", args)),
            "preview_mesh": lambda: self._agent_preview_mesh(),
            "import_mesh": lambda: self._agent_import_mesh(args.get("path")),
            "run_inversion": lambda: self._agent_run_inversion(),
            "add_timelapse_files": lambda: self._agent_add_timelapse_files(
                args.get("paths"), args.get("append", False)),
            "list_timelapse_files": lambda: self._agent_list_timelapse(),
            "remove_timelapse_files": lambda: self._agent_remove_timelapse(args.get("indices")),
            "preview_timelapse_file": lambda: self._agent_preview_timelapse(args.get("index")),
            "run_timelapse": lambda: self._agent_run_timelapse(),
            "export_timelapse": lambda: self._agent_export_timelapse(args.get("folder")),
            "get_status": lambda: self._agent_status(),
        }
        handler = handlers.get(action)
        if handler is None:
            return {"status": "failed", "error": f"Unknown action '{action}'.",
                    "valid_actions": list(handlers.keys())}
        return handler()

    def _agent_status(self) -> Dict[str, Any]:
        last = self.state.module_results.get(self.module_key, {})
        result = self._agent_result_summary(last)
        return {
            "status": "ok",
            **result,
            "data_loaded": self._ert_data is not None,
            "electrodes": len(self._x),
            "measurements": self._n_meas,
            "instrument": self._instrument.currentText(),
            "data_file": str(self._data_path or ""),
            "reciprocal_file": str(self._data_partner or ""),
            "timelapse_files": len(self._tl_files),
            # Electrodes covering an area: drawn in plan, inverted in 3-D.
            "survey_3d": self._survey_3d,
            **self._agent_pairing(),
            "average_reciprocal_pairs": self._qc_average.isChecked(),
            "reciprocal_error_floor": self._reciprocal_floor(),
            "error_model_fit": self._error_fit_to(),
            "timelapse_labels": list(self._tl_labels),
            "timelapse_low_memory": self._tl_lowmem.isChecked(),
            "lambda": self._lam.value(),
            "lambda_bounds": list(_LAMBDA_BOUNDS),
            "mesh_file": str(self._mesh_path or ""),
            "mesh_settings": self._mesh_options(),
            "mesh_preview": self._mesh_summary(),
            "zones": self._mesh_tab.zone_report(),
            "conform_to_zones": self._mesh_tab.conform_to_zones(),
            "decouple_zones": self._mesh_tab.decouple_zones(),
            "engine": self._engine.currentData(),
            "inversion_mode": self._inv_mode.currentData(),
            "geometric_factor_policy": self._geom_policy,
            "error_source": self._err_source.currentData(),
            "relative_error": self._relerr.value(),
            "absolute_error": self._abserr.value(),
            "plateau_tolerance": self._plateau.value() / 100.0,
            "max_total_iterations": self._iter_ceiling.value(),
            "reject_outliers": self._reject.isChecked(),
            "outlier_threshold": self._reject_sigma.value(),
            "outlier_passes": self._reject_passes.value(),
            "min_data_fraction": self._min_keep.value() / 100.0,
            "auto_lambda": self._auto_lam.isChecked(),
            "target_chi2": self._target_chi2.value(),
            "chi2_tolerance": self._chi2_tol.value(),
            "max_lambda_trials": self._lam_trials.value(),
            "models_available": [c["label"] for c in self._inv_choices],
            "last_result_keys": sorted(last.keys()),
        }

    def agent_handover(self, folder: Path) -> Dict[str, Any]:
        """The model on display, written for an automatic run to carry on from.

        Called when a step-by-step task is handed to Auto to report. The model
        goes to ``folder`` as the inverted-model bundle the rest of the package
        reads (``mesh_res.bms``, ``resmodel.npy``, ``all_coverage.npy``), and
        ``handover.json`` beside it says what it is: the surveys it was made
        from, the fit and the settings. Returns that record with ``model_dir``,
        or {} when no model is on display or an inversion is still running.
        """
        status = self._agent_result_summary({})
        if status["inversion_running"] or not status["has_model"]:
            return {}
        summary = status["result_summary"]

        def plain(value):
            if isinstance(value, (np.floating, np.integer)):
                value = value.item()
            return None if isinstance(value, float) and not np.isfinite(value) else value

        info: Dict[str, Any] = {key: plain(summary.get(key)) for key in
                                ("kind", "chi2", "rrms", "iterations", "lambda", "engine")}
        if summary.get("kind") == "timelapse":
            record = dict(self._tl_result or {})
            mesh, coverage = self._tl_mesh, self._tl_coverage
            models = np.asarray(self._tl_models, dtype=float)
            sources = list(getattr(self, "_tl_run_sources", None) or self._tl_files)
            info.update(
                settings=dict(getattr(self, "_tl_run_params", None) or {}),
                chi2_history=[plain(c) for c in record.get("chi2_history") or []],
                time_labels=list(record.get("time_labels") or self._tl_step_titles or []),
                survey_timing=record.get("survey_timing"),
                # The sections on display, corrected when a correction is on.
                temperature_correction=(self._tl_correction or {}).get("note"))
            if info["lambda"] is None:
                info["lambda"] = plain(record.get("lambda_used"))
        else:
            mesh = self._inv_mgr.paraDomain
            models = np.asarray(self._inv_mgr.model, dtype=float).reshape(-1, 1)
            try:
                coverage = self._inv_mgr.coverage()
            except Exception:  # noqa: BLE001 - coverage is optional in the bundle
                _logger.debug("ERTProcessingModule.agent_handover: coverage is optional in the bundle", exc_info=True)
                coverage = None
            sources = [summary["data_file"]] if summary.get("data_file") else []
        info.update(source_files=[str(Path(p).resolve()) for p in sources],
                    instrument=self._instrument.currentData(),
                    electrode_file=str(getattr(self, "_electrode_path", None) or ""))
        folder = Path(folder)
        folder.mkdir(parents=True, exist_ok=True)
        np.save(folder / "resmodel.npy", models)
        if coverage is not None:
            np.save(folder / "all_coverage.npy", np.asarray(coverage, dtype=float))
        mesh.save(str(folder / "mesh_res.bms"))
        (folder / "handover.json").write_text(json.dumps(info, indent=2, default=str),
                                              encoding="utf-8")
        return {**info, "model_dir": str(folder)}

    def _agent_result_summary(self, last: Dict[str, Any]) -> Dict[str, Any]:
        """Expose the displayed model and its fit independently of Map exports."""
        running = False
        for worker in (self._inv_worker, self._tl_worker):
            try:
                running |= worker is not None and worker.isRunning()
            except RuntimeError:  # Qt may already have deleted the finished worker.
                pass
        single = self._inv_mgr is not None
        series = self._tl_models is not None and self._tl_mesh is not None
        kind = getattr(self, "_map_result_kind", "single")
        use_series = series and (kind == "timelapse" or not single)
        summary = {}
        if single or series:
            if use_series:
                record = dict(self._tl_result or {})
                values = np.asarray(self._tl_models, dtype=float)
                summary = {"kind": "timelapse", "time_steps": int(values.shape[1]),
                           "output_dir": str(self._tl_out or "")}
            else:
                index = self._lam_pick.currentIndex()
                choice = self._inv_choices[index] if 0 <= index < len(self._inv_choices) else {}
                record = dict(choice.get("metrics") or {}) if choice else dict(last)
                for key in ("chi2", "lambda", "vtk"):
                    if key in choice:
                        record[key] = choice[key]
                values = np.asarray(self._inv_mgr.model, dtype=float)
                summary = {"kind": "single", "label": choice.get("label", "Model"),
                           "data_file": str(getattr(self, "_inv_source", None) or "")}
            for key in ("chi2", "rrms", "iterations", "lambda", "engine", "convergence_stop"):
                value = record.get(key)
                # Non-finite fit statistics mean unavailable, not a successful fit.
                if isinstance(value, (float, np.floating)) and not np.isfinite(value):
                    value = None
                summary[key] = value
            summary["resistivity_vtk"] = str(record.get("vtk") or record.get("resistivity_vtk") or "")
            finite = values[np.isfinite(values)]
            summary["resistivity_range_ohm_m"] = ([float(finite.min()), float(finite.max())]
                                                  if finite.size else None)
            summary["model_cells"] = int(values.shape[0])
        state = self._agent_run_state
        if running:
            state = "running"
        elif state != "failed" and (single or series or last):
            state = "completed"
        return {"inversion_status": state, "inversion_running": bool(running),
                "has_model": bool(single or series), "result_summary": summary,
                "inversion_error": self._agent_run_error}

    def _agent_load(self, path: Any, instrument: Any) -> Dict[str, Any]:
        if not path:
            return {"status": "failed", "error": "Provide 'path' to an ERT data file."}
        p = Path(str(path))
        if not p.exists():
            return {"status": "failed", "error": f"File not found: {p}"}
        # An explicit instrument is matched; "auto"/"none" keeps the current
        # selection (there is no auto-detect format — the user picks the device).
        if instrument is not None and str(instrument).strip() \
                and str(instrument).strip().lower() not in ("auto", "none", "auto-detect"):
            inst_key = str(instrument).strip().lower()
            idx = None
            for i, (label, value) in enumerate(_INSTRUMENTS):
                if value is not None and (inst_key == value.lower() or inst_key == label.lower()):
                    idx = i
                    break
            if idx is None:
                return {"status": "failed", "error": f"Unknown instrument '{instrument}'.",
                        "valid": [v for _, v in _INSTRUMENTS if v]}
            self._instrument.setCurrentIndex(idx)
        # The parse runs on the page's load worker - the path a click in the
        # file list takes - and this waits for it with the window live, so the
        # studio does not freeze for the whole read. Starting it supersedes a
        # preview still in flight.
        outcome, value = self._load_and_wait(str(p))
        if outcome == "failed":
            return {"status": "failed", "error": f"Could not load: {value}"}
        if outcome != "loaded":
            return {"status": "failed",
                    "error": f"A newer load replaced {p.name} before it finished."}
        # Reflect the loaded file in the file list (it doubles as the loader).
        if str(p) not in self._tl_all:
            self._set_tl_files(self._tl_all + [str(p)])
        if str(p) in self._tl_files:
            self._tl_list.setCurrentRow(self._tl_files.index(str(p)))
        out = {"status": "ok", "electrodes": len(self._x), "measurements": self._n_meas,
               "instrument": self._instrument.currentText()}
        if self._pair_info:
            out["reciprocal_file"] = str(self._data_partner or "")
            out["pairing"] = {key: self._pair_info.get(key) for key in (
                "forward", "reciprocal", "total", "pairs", "unpaired")}
        return out

    def _agent_load_electrodes(self, path: Any) -> Dict[str, Any]:
        if not path:
            return {"status": "failed", "error": "Provide 'path' to an electrode file."}
        p = Path(str(path))
        if not p.exists():
            return {"status": "failed", "error": f"File not found: {p}"}
        return self._take_electrode_file(str(p), wait=True)

    # -- electrode editing (no UI panel; these are the whole surface) --------
    def _electrode_index(self, index: Any) -> int:
        """Validate a 0-based electrode index, raising with the allowed range."""
        try:
            idx = int(index)
        except (TypeError, ValueError):
            raise ValueError(f"'index' must be an integer, got {index!r}")
        if not self._x:
            raise ValueError("No electrodes are loaded.")
        if not -len(self._x) <= idx < len(self._x):
            raise ValueError(f"index {idx} out of range for {len(self._x)} electrodes")
        return idx % len(self._x)

    def _agent_list_electrodes(self) -> Dict[str, Any]:
        return {
            "status": "ok",
            "count": len(self._x),
            "electrodes": [
                {"index": i, "label": self._labels[i], "x": float(self._x[i]),
                 **({"y": float(self._y[i])} if self._survey_3d else {}),
                 "z": float(self._z[i]),
                 "from_file": self._electrode_origins[i] is not None}
                for i in range(len(self._x))
            ],
        }

    def _agent_add_electrode(self, x: Any, z: Any, label: Any = None,
                             y: Any = None) -> Dict[str, Any]:
        if x is None or z is None:
            return {"status": "failed", "error": "Provide both 'x' and 'z'."}
        try:
            xv, zv, yv = float(x), float(z), float(y or 0.0)
        except (TypeError, ValueError):
            return {"status": "failed", "error": "'x', 'y' and 'z' must be numbers."}
        self._x.append(xv)
        self._y.append(yv)
        self._z.append(zv)
        self._labels.append(str(label) if label else f"new-{len(self._x)}")
        self._electrode_origins.append(None)  # carries no measurements
        self._refresh()
        self.log(f"Added electrode {len(self._x) - 1} at x={xv:g}, z={zv:g}.", "info")
        return {"status": "ok", "index": len(self._x) - 1, "electrodes": len(self._x)}

    def _agent_move_electrode(self, index: Any, x: Any = None, z: Any = None,
                              y: Any = None) -> Dict[str, Any]:
        if x is None and z is None and y is None:
            return {"status": "failed", "error": "Provide 'x', 'y' or 'z'."}
        try:
            idx = self._electrode_index(index)
            if x is not None:
                self._x[idx] = float(x)
            if y is not None:
                self._y[idx] = float(y)
            if z is not None:
                self._z[idx] = float(z)
        except (ValueError, TypeError) as exc:
            return {"status": "failed", "error": str(exc)}
        self._refresh()
        self.log(f"Moved electrode {idx} to x={self._x[idx]:g}, z={self._z[idx]:g}.", "info")
        return {"status": "ok", "index": idx,
                "x": float(self._x[idx]), "z": float(self._z[idx])}

    def _agent_delete_electrode(self, index: Any) -> Dict[str, Any]:
        try:
            idx = self._electrode_index(index)
        except (ValueError, TypeError) as exc:
            return {"status": "failed", "error": str(exc)}
        label = self._labels[idx]
        self._delete(idx)
        self.log(f"Deleted electrode {idx} ({label}); {len(self._x)} remain. "
                 "Measurements referencing it are dropped at inversion time.", "warn")
        return {"status": "ok", "deleted": idx, "electrodes": len(self._x)}

    def _agent_set_electrode_label(self, index: Any, label: Any) -> Dict[str, Any]:
        if label is None or not str(label).strip():
            return {"status": "failed", "error": "Provide a non-empty 'label'."}
        try:
            idx = self._electrode_index(index)
        except (ValueError, TypeError) as exc:
            return {"status": "failed", "error": str(exc)}
        self._labels[idx] = str(label)
        self._refresh()
        return {"status": "ok", "index": idx, "label": self._labels[idx]}

    def _agent_clear_electrodes(self) -> Dict[str, Any]:
        removed = len(self._x)
        self._clear()
        self.log(f"Cleared {removed} electrode(s).", "warn")
        return {"status": "ok", "removed": removed}

    def _agent_apply_filter(self, args: Dict[str, Any]) -> Dict[str, Any]:
        if self._ert_data_full is None:
            return {"status": "failed", "error": "Load ERT data first."}
        try:
            if "min_rhoa" in args:
                self._rmin.setValue(float(args["min_rhoa"]))
            if "max_rhoa" in args:
                self._rmax.setValue(float(args["max_rhoa"]))
            if "max_error" in args:
                self._max_err.setValue(float(args["max_error"]))
            # The folded criteria are opt-in from the agent too: naming any one of
            # them unfolds the section, so the panel keeps matching what ran.
            if "average_reciprocal_pairs" in args:
                if args["average_reciprocal_pairs"] and not self._qc_average.isEnabled():
                    return {"status": "failed",
                            "error": "The loaded data have no reading measured both ways, "
                                     "so there are no reciprocal pairs to average."}
                self._qc_average.setChecked(bool(args["average_reciprocal_pairs"]))
            extra = {"drop_nonpositive_rhoa": lambda v: self._qc_drop_neg.setChecked(bool(v)),
                     "min_voltage": lambda v: self._qc_min_v.setValue(float(v)),
                     "min_current": lambda v: self._qc_min_i.setValue(float(v)),
                     "max_geometric_factor": lambda v: self._qc_max_k.setValue(float(v)),
                     "max_contact_resistance": lambda v: self._qc_max_rc.setValue(float(v)),
                     "max_stacking_spread": lambda v: self._qc_max_stack.setValue(float(v) * 100.0),
                     "max_reciprocal_error": lambda v: self._qc_max_recip.setValue(float(v) * 100.0)}
            used = [key for key in extra if key in args]
            for key in used:
                extra[key](args[key])
            if used:
                self._qc_more.setChecked(True)
        except Exception as exc:  # noqa: BLE001
            return {"status": "failed", "error": str(exc)}
        self._apply_filter()
        return {"status": "ok", "measurements": self._n_meas}

    def _agent_set_params(self, params: Any) -> Dict[str, Any]:
        if not isinstance(params, dict):
            return {"status": "failed", "error": "Provide 'params' as a JSON object."}

        def set_combo(combo, value):
            items = [combo.itemText(i) for i in range(combo.count())]
            if str(value) not in items:
                raise ValueError(f"must be one of {items}")
            combo.setCurrentText(str(value))

        def set_geom_policy(value):
            allowed = ("off", "check", "fix")
            key = str(value).strip().lower()
            if key not in allowed:
                raise ValueError(f"must be one of {list(allowed)}")
            self._geom_policy = key

        def set_inv_mode(value):
            """Select the Quick/Full preset.

            ``_agent_set_params`` walks the caller's object in its own order, so a
            ``geometric_factor_policy`` or ``auto_lambda`` listed after
            ``inversion_mode`` overrides what the preset just set, and one listed
            before it does not. Send the mode first and the exceptions after it.
            """
            allowed = ("quick", "full")
            key = str(value).strip().lower()
            if key not in allowed:
                raise ValueError(f"must be one of {list(allowed)}")
            self._inv_mode.setCurrentIndex(
                [self._inv_mode.itemData(i) for i in range(self._inv_mode.count())].index(key)
            )
            self._on_inv_mode_changed()

        def set_combo_data(combo, value):
            """Match on the stable itemData key, not on the display label."""
            keys = [combo.itemData(i) for i in range(combo.count())]
            key = str(value).strip().lower()
            for index, candidate in enumerate(keys):
                if str(candidate).lower() == key:
                    combo.setCurrentIndex(index)
                    return
            raise ValueError(f"must be one of {keys}")

        def set_error_source(value):
            """``stack`` needs data that record a spread, ``reciprocal`` data
            measured both ways; refused, not left greyed."""
            if str(value).strip().lower() == "stack" and not (
                    self._ert_data_full is not None and self._ert_data_full.haveData("stack")):
                raise ValueError("needs each reading's stacking spread, which the loaded "
                                 "data do not record (Subsurface Insights exports do)")
            if str(value).strip().lower() == "reciprocal" and not (
                    self._reciprocal_pair_count(self._ert_data_full) or self._tl_partner):
                raise ValueError("needs readings measured both ways; the loaded data and "
                                 "the file list have no reciprocal pairs")
            set_combo_data(self._err_source, value)

        def set_error_fit(value):
            """What the reciprocal error model is fitted to: 'all' or 'kept'."""
            key = str(value).strip().lower()
            if key not in ("all", "kept"):
                raise ValueError("must be one of ['all', 'kept']")
            self._recip_view.set_fit_to(key)

        def set_floor(value):
            """The "Minimum" error, given as a fraction."""
            set_in_range(self._recip_floor, float(value) * 100.0)

        def set_in_range(spin, value, cast=float):
            """A value the box would clip is refused, so the reply says so
            instead of reporting a setting that did not take."""
            number = cast(value)
            if not spin.minimum() <= number <= spin.maximum():
                raise ValueError(f"must be between {spin.minimum():g} and "
                                 f"{spin.maximum():g}")
            spin.setValue(number)

        handlers = {
            # shared by single + time-lapse inversion
            "lambda": lambda v: self._lam.setValue(float(v)),
            "max_iterations": lambda v: self._iter.setValue(int(v)),
            "relative_error": lambda v: self._relerr.setValue(float(v)),
            "mesh_quality": lambda v: set_in_range(self._quality, v),
            "para_depth": lambda v: set_in_range(self._para_depth, v),
            "para_max_cell_size": lambda v: set_in_range(self._para_max_cell, v),
            "para_boundary": lambda v: set_in_range(self._para_boundary, v),
            "surface_nodes": lambda v: set_in_range(self._surface_nodes, v, int),
            "outer_width": lambda v: set_in_range(self._outer_width, v),
            "outer_max_cell_size": lambda v: set_in_range(self._outer_max_cell, v),
            "mesh_file": lambda v: (self._apply_mesh_file(str(v)) if str(v)
                                    else self._clear_mesh()),
            # set_zones is silent, as a change from outside should be; the page
            # still has to follow it, and rebuild a mesh that follows the zones.
            "zones": lambda v: (self._mesh_tab.set_zones(v), self._mesh_inputs_changed()),
            "conform_to_zones": lambda v: self._mesh_tab.set_conform_to_zones(bool(v)),
            "decouple_zones": lambda v: self._mesh_tab.set_decouple_zones(bool(v)),
            "time_lapse": lambda v: self._set_timelapse(bool(v)),
            # single-inversion fit assistance
            "engine": lambda v: set_combo_data(self._engine, v),
            "inversion_mode": lambda v: set_inv_mode(v),
            "geometric_factor_policy": lambda v: set_geom_policy(v),
            "error_source": lambda v: set_error_source(v),
            "reciprocal_error_floor": lambda v: set_floor(v),
            "error_model_fit": lambda v: set_error_fit(v),
            # Ticked by default; the list regroups as it changes.
            "pair_reciprocal_files": lambda v: self._tl_pair_box.setChecked(bool(v)),
            "absolute_error": lambda v: self._abserr.setValue(float(v)),
            "plateau_tolerance": lambda v: self._plateau.setValue(float(v) * 100.0),
            "max_total_iterations": lambda v: self._iter_ceiling.setValue(int(v)),
            "reject_outliers": lambda v: self._reject.setChecked(bool(v)),
            "outlier_threshold": lambda v: self._reject_sigma.setValue(float(v)),
            "outlier_passes": lambda v: self._reject_passes.setValue(int(v)),
            "min_data_fraction": lambda v: self._min_keep.setValue(float(v) * 100.0),
            "auto_lambda": lambda v: self._auto_lam.setChecked(bool(v)),
            "target_chi2": lambda v: self._target_chi2.setValue(float(v)),
            "chi2_tolerance": lambda v: self._chi2_tol.setValue(float(v)),
            "max_lambda_trials": lambda v: self._lam_trials.setValue(int(v)),
            # time-lapse-only
            "tl_alpha": lambda v: self._tl_alpha.setValue(float(v)),
            "tl_norm": lambda v: set_combo(self._tl_type, v),
            "tl_windowed": lambda v: self._tl_windowed.setChecked(bool(v)),
            "tl_window_size": lambda v: self._tl_window.setValue(int(v)),
            "tl_low_memory": lambda v: self._tl_lowmem.setChecked(bool(v)),
            # aliases for the time-lapse names (these params are shared)
            "tl_lambda": lambda v: self._lam.setValue(float(v)),
            "tl_iterations": lambda v: self._iter.setValue(int(v)),
            "tl_relative_error": lambda v: self._relerr.setValue(float(v)),
            "tl_mesh_quality": lambda v: set_in_range(self._quality, v),
        }
        applied: Dict[str, Any] = {}
        ignored: Dict[str, str] = {}
        for key, value in params.items():
            handler = handlers.get(key)
            if handler is None:
                ignored[key] = "unknown parameter"
                continue
            try:
                handler(value)
                applied[key] = value
            except Exception as exc:  # noqa: BLE001
                ignored[key] = str(exc)
        return {"status": "ok" if applied else "failed", "applied": applied, "ignored": ignored}

    def _declined_since(self, last: Any) -> str:
        """Why the page did not start a run: the warnings it logged after ``last``."""
        lines = []
        for entry in reversed(self._turn_log):
            if entry is last:
                break
            if entry[1] in ("warn", "error"):
                lines.append(entry[2])
        return " ".join(reversed(lines)) or "The run did not start."

    def _agent_run_inversion(self) -> Dict[str, Any]:
        if self._ert_data is None:
            return {"status": "failed", "error": "Load ERT data with apparent resistivity first."}
        worker = getattr(self, "_inv_worker", None)
        last = self._turn_log[-1] if self._turn_log else None
        self._run_inversion()
        if getattr(self, "_inv_worker", None) is worker:    # the page declined it
            return {"status": "failed", "error": self._declined_since(last)}
        return {"status": "started", "message": "ERT inversion started. Ask for status shortly.",
                "lambda": self._lam.value(),
                "auto_lambda": self._auto_lam.isChecked(),
                "target_chi2": self._target_chi2.value(),
                "chi2_tolerance": self._chi2_tol.value(),
                "max_lambda_trials": self._lam_trials.value()}

    def _agent_import_mesh(self, path: Any) -> Dict[str, Any]:
        """Import a mesh as the inversion mesh and show it on the Mesh tab."""
        if not path:
            return {"status": "failed", "error": "Provide 'path' to a mesh file."}
        p = Path(str(path))
        if not p.exists():
            return {"status": "failed", "error": f"File not found: {p}"}
        try:
            summary = self._apply_mesh_file(str(p))
        except Exception as exc:  # noqa: BLE001 - said next to the button and returned
            self._mesh_note.setText(
                QCoreApplication.translate("PHGX", "<span style='color:{0}'>{1}: {2}</span>").format(theme.color('red'), p.name, exc))
            self.log(f"Could not import the mesh {p.name}: {exc}", "error")
            return {"status": "failed", "error": str(exc)}
        self._tabs.setCurrentWidget(self._mesh_tab)
        return {"status": "ok", "mesh": re.sub(r"<[^>]+>", "", summary)}

    def _agent_preview_mesh(self) -> Dict[str, Any]:
        request, message = self._mesh_preview_request()
        if request is None:
            return {"status": "failed", "error": message}
        # Opening the tab builds the mesh when it is not current.
        self._tabs.setCurrentWidget(self._mesh_tab)
        self._refresh_mesh_preview()
        summary = self._mesh_summary()
        if not summary.get("current"):
            return {"status": "started",
                    "message": "Building the inversion mesh on the Mesh tab; ask for "
                               "status shortly for its counts."}
        return {"status": "ok", "mesh": summary, "zones": self._mesh_tab.zone_report()}

    def _agent_add_timelapse_files(self, paths: Any, append: Any = False) -> Dict[str, Any]:
        if not isinstance(paths, list) or not paths:
            return {"status": "failed", "error": "Provide 'paths' as a non-empty list of files."}
        missing = [str(p) for p in paths if not Path(str(p)).exists()]
        if missing:
            return {"status": "failed", "error": f"Files not found: {missing}"}
        merged = list(self._tl_all) if append else []
        for p in paths:
            if str(p) not in merged:
                merged.append(str(p))
        self._set_tl_files(merged)
        self._tl_mode.setChecked(True)  # reveal the time-lapse options in the UI
        return {"status": "ok", "files": len(self._tl_files),
                "time_labels": list(self._tl_labels),
                "timing": self._tl_timing.summary() if self._tl_timing else "",
                **self._agent_pairing()}

    def _agent_pairing(self) -> Dict[str, Any]:
        """How the list paired forward and reciprocal files, for the agent."""
        found = getattr(self, "_tl_pairs_found", None) or {}
        if not (found.get("pairs") or found.get("orphans")):
            return {}
        return {"pair_reciprocal_files": self._tl_pair_box.isChecked(),
                "paired_surveys": len(self._tl_partner),
                "reciprocal_files_left_out": [Path(p).name for p in self._tl_left_out]}

    def _agent_list_timelapse(self) -> Dict[str, Any]:
        timing = self._tl_timing
        gaps = timing.intervals if timing is not None else []
        return {
            "status": "ok",
            "count": len(self._tl_files),
            # The interval between surveys, in words: the sequence reads the same
            # whether it is hourly or monthly until something says which.
            "timing": timing.summary() if timing is not None else "",
            "time_source": timing.source if timing is not None else "index",
            "intervals": [survey_timing.format_duration(g) for g in gaps],
            # One entry per survey; a paired survey names its reciprocal file.
            "files": [{"index": i, "label": self._tl_labels[i] if i < len(self._tl_labels) else str(i + 1),
                       "time": self._tl_times[i] if i < len(self._tl_times) else float(i + 1),
                       # Where this file's time came from, as its row's tooltip says.
                       "time_note": timing.describe(i) if timing is not None else "",
                       "name": Path(p).name, "path": p,
                       **({"reciprocal": Path(self._tl_partner[p]).name,
                           "reciprocal_path": self._tl_partner[p]}
                          if p in self._tl_partner else {})}
                      for i, p in enumerate(self._tl_files)],
            **self._agent_pairing(),
        }

    def _agent_remove_timelapse(self, indices: Any) -> Dict[str, Any]:
        if indices is None:
            self._set_tl_files([])
            return {"status": "ok", "files": 0, "message": "Cleared all time-lapse files."}
        try:
            drop = {int(i) for i in indices}
        except (TypeError, ValueError):
            return {"status": "failed", "error": "Provide 'indices' as a list of integers."}
        # An index is a survey: a paired survey's reciprocal file goes with it.
        self._set_tl_files(self._tl_flat(
            [p for i, p in enumerate(self._tl_files) if i not in drop]))
        return {"status": "ok", "files": len(self._tl_files)}

    def _agent_preview_timelapse(self, index: Any) -> Dict[str, Any]:
        try:
            i = int(index)
        except (TypeError, ValueError):
            return {"status": "failed", "error": "Provide 'index' as an integer (0-based)."}
        if not (0 <= i < len(self._tl_files)):
            return {"status": "failed", "error": f"index out of range (0..{len(self._tl_files) - 1})."}
        self._start_load(self._tl_files[i])
        partner = self._tl_partner.get(self._tl_files[i])
        return {"status": "started", "message": f"Loading time step {i} for preview.",
                "name": Path(self._tl_files[i]).name,
                **({"reciprocal": Path(partner).name} if partner else {})}

    def _agent_run_timelapse(self) -> Dict[str, Any]:
        if len(self._tl_files) < 2:
            return {"status": "failed", "error": "Add at least two ordered ERT files first.",
                    "files": len(self._tl_files)}
        worker = getattr(self, "_tl_worker", None)
        last = self._turn_log[-1] if self._turn_log else None
        self._run_timelapse()
        if getattr(self, "_tl_worker", None) is worker:     # the page declined it
            return {"status": "failed", "error": self._declined_since(last)}
        return {"status": "started", "message": "Time-lapse inversion started. Ask for status shortly.",
                "steps": len(self._tl_files)}

    def _agent_export_timelapse(self, folder: Any) -> Dict[str, Any]:
        if not self._tl_result:
            return {"status": "failed", "error": "Run the time-lapse inversion first."}
        if not folder:
            return {"status": "failed", "error": "Provide 'folder' to export the results into."}
        dest = self._export_tl_results(str(folder))
        if not dest:
            return {"status": "failed", "error": "Export failed (no result files found)."}
        return {"status": "ok", "folder": dest, "files": len(self._tl_result_files()),
                "vtk_combined": (self._tl_result or {}).get("vtk_combined", ""),
                "vtk_steps": len((self._tl_result or {}).get("vtk_step_paths") or [])}
