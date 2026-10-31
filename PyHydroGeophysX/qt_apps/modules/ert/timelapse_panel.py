"""The ERT page: time-lapse files, their QC, and time-lapse runs (plan M4.5).

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
    ProcessWorkflowWorker,
    QCoreApplication,
    QFileDialog,
    QListWidgetItem,
    Qt,
    TaskWorker,
    WorkflowRunResult,
    WorkflowSpec,
    _DATA_FILTER,
    _DATA_SUFFIXES,
    _TC_WAITING,
    ert_load,
    export_workflow_bundle,
    i18n,
    io_utils,
    np,
    re,
    run_inputs,
    shutil,
    survey_timing,
    theme,
)
from PyHydroGeophysX._internal.native_paths import pygimli_path


class _TimelapsePanel:

    # -- time-lapse inversion ------------------------------------------------
    def _set_tl_files(self, paths: List[str]) -> None:
        """Replace every file of the list, reciprocal files included, regroup
        them into surveys, and refresh the list and its times."""
        self._tl_all = [str(p) for p in paths]
        self._group_tl_surveys()
        self._read_tl_times()
        self._refresh_tl_list()
        self._sync_run_ready()

    def _group_tl_surveys(self) -> None:
        """Make each forward file and its reciprocal file one survey.

        ``survey_timing.reciprocal_pairs`` finds them by name and time; the
        pairs hold while "Pair reciprocal files" is ticked, and the box is shown
        only when the list holds a file named as a reciprocal. Unticked, or with
        none, every file is a survey of its own.
        """
        paths = list(self._tl_all)
        self._tl_partner, self._tl_left_out = {}, []
        found: Dict[str, Any] = {"pairs": [], "orphans": [], "gap_seconds": None}
        if paths:
            mtime_box = getattr(self, "_tl_use_mtime", None)
            timing = ert_load.survey_timing_for(
                paths, allow_mtime=bool(mtime_box is not None and mtime_box.isChecked()))
            found = survey_timing.reciprocal_pairs(paths, timing.found or None)
            # Each file's own time, the reciprocal files' included, for the rows.
            self._tl_stamp_of = dict(zip(paths, timing.found or []))
        self._tl_pairs_found = found
        detected = bool(found["pairs"] or found["orphans"])
        self._tl_pair_box.setVisible(detected)
        if detected and self._tl_pair_box.isChecked():
            self._tl_partner = {paths[f]: paths[r] for f, r in found["pairs"]}
            self._tl_left_out = [paths[r] for r in found["orphans"]]
            hidden = set(self._tl_partner.values()) | set(self._tl_left_out)
            self._tl_files = [p for p in paths if p not in hidden]
        else:
            self._tl_files = paths
        # The reciprocal error model is offered for a paired series.
        self._refresh_error_sources(self._ert_data_full)

    def _tl_flat(self, surveys: List[str]) -> List[str]:
        """Every file of ``surveys``, each forward file followed by its
        reciprocal file, and then the reciprocal files left out."""
        out: List[str] = []
        for path in surveys:
            out.append(path)
            if path in self._tl_partner:
                out.append(self._tl_partner[path])
        return out + [p for p in self._tl_left_out if p not in out]

    def _on_tl_pairing_changed(self, checked: bool) -> None:
        """Pair or unpair the list's reciprocal files, and reload the survey on
        screen when it was, or now is, one half of a pair."""
        before = dict(self._tl_partner)
        self._group_tl_surveys()
        self._read_tl_times()
        self._refresh_tl_list()
        if checked:
            self.log(f"Reciprocal files paired: {len(self._tl_partner)} survey(s) now "
                     "hold a forward and a reciprocal file each.", "info")
        else:
            self.log("Reciprocal files unpaired: every file is a time step of its own.",
                     "info")
        shown = str(self._data_path) if self._data_path is not None else ""
        if shown and (shown in before or shown in self._tl_partner) \
                and before.get(shown) != self._tl_partner.get(shown):
            self._start_load(shown)

    def _read_tl_times(self) -> None:
        """Read the acquisition time of every survey, from the names or the headers.

        Kept in one place because three operations reorder the sequence, and a set
        of times that no longer matches the list is worse than none: the inversion
        would pair each survey with someone else's date. A paired survey is timed
        by its forward file.
        """
        mtime_box = getattr(self, "_tl_use_mtime", None)   # absent until built
        self._tl_timing = ert_load.survey_timing_for(
            self._tl_files,
            allow_mtime=bool(mtime_box is not None and mtime_box.isChecked()))
        self._tl_times = list(self._tl_timing.times)
        self._tl_labels = list(self._tl_timing.labels)

    def _reciprocal_time(self, path: str) -> str:
        """When a reciprocal file was measured, as hh:mm, or "" when unknown."""
        stamp = getattr(self, "_tl_stamp_of", {}).get(path)
        return f"{stamp:%H:%M}" if stamp is not None else ""

    def _refresh_tl_list(self) -> None:
        self._tl_list.blockSignals(True)
        self._tl_list.clear()
        timing = getattr(self, "_tl_timing", None)
        gaps = timing.intervals if timing is not None else []
        # A forward file without its reciprocal is marked only in a list that
        # pairs some: in one without reciprocal files every file is unpaired.
        mark_unpaired = bool(self._tl_partner)
        for i, path in enumerate(self._tl_files):
            label = self._tl_labels[i] if i < len(self._tl_labels) else str(i + 1)
            # The gap to the previous survey, on the row it belongs to: an hourly
            # sequence and a monthly one look identical without it.
            gap = ""
            if i > 0 and i - 1 < len(gaps):
                step = gaps[i - 1]
                gap = (f"   (+{survey_timing.format_duration(step)})" if step >= 0
                       else f"   ({survey_timing.format_duration(step)}, out of order)")
            text = f"{i + 1}.  {label}    ·    {Path(path).name}{gap}"
            partner = self._tl_partner.get(path)
            # The reciprocal file on a line of its own under its forward file,
            # so a wrong pairing can be seen in the list itself.
            if partner:
                # Its time first: a long file name runs off the row's end.
                when = self._reciprocal_time(partner)
                text += (f"\n        + reciprocal{f' {when}' if when else ''}    ·    "
                         f"{Path(partner).name}")
            elif mark_unpaired:
                text += "   (unpaired: no reciprocal file)"
            item = QListWidgetItem(text)
            item.setData(Qt.UserRole, path)
            # Where this file's time came from: the one file whose time was not
            # read from its name, or was read two ways, is the one to look at.
            origin = timing.describe(i) if timing is not None else ""
            tip = f"{path}\n{origin}" if origin else path
            if partner:
                tip += (f"\n\nReciprocal file, merged with it into one survey:\n{partner}")
            item.setToolTip(i18n.tr(tip))
            self._tl_list.addItem(item)
        self._tl_list.blockSignals(False)
        n = len(self._tl_files)
        if n == 0:
            self._tl_info.setText(QCoreApplication.translate("PHGX", "No files added."))
        # The format is not repeated here: it is chosen two rows up, and a copy
        # of it would go stale as soon as the format is changed.
        elif n == 1:
            self._tl_info.setText("<b>1</b> survey; add more for a time-lapse series."
                                  + self._tl_pairs_text(timing))
        else:
            self._tl_info.setText(i18n.tr(self._tl_timing_text(timing)))
        # Offered while some files of a series carry no time - one survey needs
        # none - and kept on screen once ticked.
        undated = bool(timing is not None and n >= 2 and timing.undated_files())
        self._tl_use_mtime.setVisible(undated or self._tl_use_mtime.isChecked())
        # A time-lapse mesh is built from whichever survey is now first, and
        # the Reciprocal errors tab draws the series as the list now holds it.
        self._mesh_inputs_changed()
        self._recip_inputs_changed()

    def _tl_timing_text(self, timing: Optional[Any]) -> str:
        """The file list's summary line, and what to do when its times fall short.

        The accepted forms are on the line's tooltip; what is said here is only
        what this set of files needs: a time missing from some or all of them,
        files out of time order, or forward and reciprocal halves.
        """
        n = len(self._tl_files)
        if timing is None:
            return f"{n} files."
        how = ("  Put the time in each file name, year first (e.g. "
               "<code>site_2026-01-12_05-50-38.dat</code>), add a line "
               "<code># date: 2026-01-12 05:50:38</code> at the top of each file, "
               "or tick “Date undated files” below.")
        # The summary names the files that keep an undated list from being dated
        # (no time, or a time another file has too); hovering a row says why.
        text = timing.summary()
        if timing.dated and any(gap < 0 for gap in timing.intervals):
            text += " The files are not in time order: press Sort by time."
        elif not timing.dated and timing.undated_files():
            text += how
        return text + self._tl_pairs_text(timing)

    def _tl_pairs_text(self, timing: Any) -> str:
        """What the list made of forward and reciprocal files.

        Paired, each survey is one forward file with its reciprocal: said once,
        with the forward files that have none and - in amber - the reciprocal
        files left out for want of one. Unpaired while the names say there are
        pairs, each survey is inverted twice and its reciprocals are never
        compared, which is warned about.
        """
        found = getattr(self, "_tl_pairs_found", None) or {"pairs": [], "orphans": []}
        if not (found["pairs"] or found["orphans"]):
            self._tl_pairs_logged = None
            return ""
        gap = survey_timing.format_duration(found["gap_seconds"]) \
            if found.get("gap_seconds") is not None else ""
        if self._tl_pair_box.isChecked():
            paired = len(self._tl_partner)
            alone = len(self._tl_files) - paired
            text = (f" {paired} of {len(self._tl_files)} surveys are a forward file with its "
                    f"reciprocal file{f' (about {gap} later)' if gap else ''}, merged into "
                    "one time step so each reading is compared with its reciprocal.")
            if alone:
                text += f" {alone} forward file(s) have no reciprocal file and are inverted alone."
            warning = ""
            if self._tl_left_out:
                warning = (f"{len(self._tl_left_out)} reciprocal file(s) have no forward file "
                           "and are left out: "
                           + ", ".join(Path(p).name for p in self._tl_left_out) + ".")
            key = ("paired", paired, tuple(self._tl_left_out))
            message = (text.strip() + (" " + warning if warning else ""), "warn" if warning
                       else "info")
            shown = text + (f" <span style='color:{theme.color('amber')}'>{warning}</span>"
                            if warning else "")
        else:
            warning = (
                f"{len(found['pairs'])} file(s) look like the reciprocal half of a survey "
                f"(“recip” in the name){f', each about {gap} after its forward file' if gap else ''}. "
                f"With “Pair reciprocal files” unticked every file is a time step of its "
                f"own, so each survey appears twice and no reciprocal errors are formed "
                f"between the two files.")
            key = ("unpaired", tuple(sorted(found["reciprocal"])))
            message = (warning, "warn")
            shown = f" <span style='color:{theme.color('amber')}'>{warning}</span>"
        # Logged once per state, so reordering the list does not repeat it.
        if getattr(self, "_tl_pairs_logged", None) != key:
            self._tl_pairs_logged = key
            self.log(*message)
        return shown

    def _add_tl_files(self) -> None:
        from PyHydroGeophysX.qt_apps.widgets.project_dialogs import confirm_project_for_data
        if not confirm_project_for_data(self):   # name a Project before the first data
            return
        paths, _ = QFileDialog.getOpenFileNames(
            self, QCoreApplication.translate("PHGX", "Add ERT data file(s)"), "", _DATA_FILTER)
        if paths:
            self._add_files(paths)

    # -- files dropped on the page -------------------------------------------
    @staticmethod
    def _dropped_files(mime: Any) -> List[str]:
        """The data files of a drop: files as they are, a folder's data files by name."""
        if mime is None or not mime.hasUrls():
            return []
        found: List[str] = []
        for url in mime.urls():
            if not url.isLocalFile():
                continue
            path = Path(url.toLocalFile())
            if path.is_dir():
                found.extend(str(p) for p in sorted(path.iterdir())
                             if p.is_file() and p.suffix.lower() in _DATA_SUFFIXES)
            elif path.is_file():
                found.append(str(path))
        return found

    def dragEnterEvent(self, event) -> None:  # noqa: N802 - Qt override
        if event.mimeData() is not None and event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event) -> None:  # noqa: N802 - Qt override
        self.dragEnterEvent(event)

    def dropEvent(self, event) -> None:  # noqa: N802 - Qt override
        paths = self._dropped_files(event.mimeData())
        if not paths:
            self.log("Nothing in the drop is an ERT data file or a folder holding some.",
                     "warn")
            event.ignore()
            return
        event.acceptProposedAction()
        from PyHydroGeophysX.qt_apps.widgets.project_dialogs import confirm_project_for_data
        if confirm_project_for_data(self):
            self._add_files(paths)

    def _add_files(self, paths: List[str]) -> None:
        """Add data files to the list - chosen in the dialog or dropped on the page."""
        # Append new files, preserving order and dropping duplicates.
        old_n = len(self._tl_files)
        merged = list(self._tl_all)
        added = 0
        for p in paths:
            if p not in merged:
                merged.append(p); added += 1
        self._set_tl_files(merged)
        self.log(f"Added {added} ERT file(s); {len(self._tl_files)} survey(s) in the list.",
                 "info")
        # Auto-preview the first newly added survey so the user sees data immediately.
        if added and old_n < len(self._tl_files):
            self._tl_list.setCurrentRow(old_n)
            self._preview_tl_item(self._tl_list.item(old_n))

    def _selected_tl_rows(self) -> List[int]:
        return sorted(self._tl_list.row(it) for it in self._tl_list.selectedItems())

    def _remove_tl_files(self) -> None:
        rows = set(self._selected_tl_rows())
        if not rows:
            self.log("Select one or more files in the list to remove.", "warn")
            return
        # A row is a survey: its reciprocal file goes with it.
        self._set_tl_files(self._tl_flat(
            [p for i, p in enumerate(self._tl_files) if i not in rows]))
        self.log(f"Removed {len(rows)} survey(s); {len(self._tl_files)} remain.", "info")

    def _move_tl_files(self, delta: int) -> None:
        rows = self._selected_tl_rows()
        if not rows:
            return
        order = list(range(len(self._tl_files)))
        chosen = set(rows)
        # The selection moves as a block: a row steps past an unselected
        # neighbour, and one against the edge - or behind a selected row that
        # is - stays put. Swapped one at a time, a block already at the top would
        # be reversed, and the top row is the baseline every survey is compared to.
        steps = range(1, len(order)) if delta < 0 else range(len(order) - 2, -1, -1)
        for i in steps:
            j = i - 1 if delta < 0 else i + 1
            if order[i] in chosen and order[j] not in chosen:
                order[i], order[j] = order[j], order[i]
        if order == list(range(len(order))):
            return
        # A pair moves as one row; the full list follows the surveys' order.
        self._tl_files = [self._tl_files[i] for i in order]
        self._tl_all = self._tl_flat(self._tl_files)
        self._read_tl_times()
        moved = {order.index(i) for i in rows}
        self._refresh_tl_list()
        for r in moved:
            self._tl_list.item(r).setSelected(True)

    def _sort_tl_files_by_time(self) -> None:
        """Reorder the list into acquisition order.

        The sequence order is part of the result - each survey is compared with
        the one before it - and a file dialog returns names in whatever order the
        filesystem gives, which for ``survey_9`` and ``survey_10`` is not the
        order they were recorded in. A paired survey sorts by its forward file.
        """
        timing = getattr(self, "_tl_timing", None)
        if timing is None or not timing.dated:
            self.log("Cannot sort: the files carry no readable acquisition time. "
                     "Use ↑ ↓ to put them in order by hand.", "warn")
            return
        order = sorted(range(len(self._tl_files)), key=lambda i: timing.timestamps[i])
        if order == list(range(len(self._tl_files))):
            self.log("Files are already in acquisition order.", "info")
            return
        self._set_tl_files(self._tl_flat([self._tl_files[i] for i in order]))
        self.log(f"Sorted {len(self._tl_files)} surveys into acquisition order.", "success")

    def _clear_tl_files(self) -> None:
        self._set_tl_files([])
        self.log("Cleared time-lapse file list.", "info")

    def _on_tl_selection_changed(self) -> None:
        rows = self._selected_tl_rows()
        if len(rows) > 1:
            self._tl_info.setText(QCoreApplication.translate("PHGX", "{0} surveys selected — Remove / Move ↑ ↓, or click one to preview.").format(len(rows)))

    def _preview_tl_item(self, item: QListWidgetItem) -> None:
        path = item.data(Qt.UserRole)
        if path and Path(str(path)).exists():
            self.log(f"Preview: loading {Path(str(path)).name} …", "info")
            self._start_load(str(path))

    def _preview_selected_tl(self) -> None:
        items = self._tl_list.selectedItems()
        if items:
            self._preview_tl_item(items[0])

    def _run_timelapse(self) -> None:
        if len(self._tl_files) < 2:
            self.log("Add at least two ordered ERT data files (a time sequence).", "warn")
            return
        self._warn_external_not_running("time-lapse folder")
        if (
            self._engine.currentData() == "adtlert"
            and self._adtlert_timelapse_ready is not True
        ):
            self.log(
                "ADTLERT timelapse self-test has not passed. Wait for the check, "
                "or select In-house Gauss-Newton / PyHydro. "
                "To retry, switch engines and select ADTLERT again.",
                "warn",
            )
            return
        if (
            self._engine.currentData() == "adtlert"
            and not self._tl_windowed.isChecked()
        ):
            self.log(
                "ADTLERT time-lapse inversion requires Windowed (sliding window).",
                "warn",
            )
            return
        instrument = self._instrument.currentData()
        params = {
            "lambda_val": self._lam.value(), "alpha": self._tl_alpha.value(),
            "inversion_type": self._tl_type.currentText(), "max_iterations": self._iter.value(),
            "relativeError": self._relerr.value(),
            # The mesh settings are shared with the single inversion, the
            # imported mesh among them, which switches the others off; the
            # series is inverted on it.
            **self._mesh_options(),
            **self._zone_parameters(),
            "windowed": self._tl_windowed.isChecked(), "window_size": self._tl_window.value(),
            "engine": str(self._engine.currentData()),
            "instrument": instrument,
            # Same auto-λ switch as the single inversion; the trial budget is
            # smaller because each trial is a joint inversion over every step.
            "auto_lambda": bool(self._auto_lam.isChecked()),
            "target_chi2": float(self._target_chi2.value()),
            "chi2_tolerance": float(self._chi2_tol.value()),
            "max_lambda_trials": min(int(self._lam_trials.value()), 4),
            "temporal_weighting": (
                "interval" if self._tl_dt_weight.isChecked() else "uniform"),
        }
        if self._tl_lowmem.isChecked():
            params["save_memory"] = True
        # The same stopping rule as a single run: the in-house engine (full or
        # windowed) and E4D end once chi2 stops improving by this much.
        params["plateau_tolerance"] = float(self._plateau.value()) / 100.0
        if self._engine.currentData() == "e4d":
            params["e4d"] = self._e4d_settings()
        if self._r2_program_name() is not None:
            params["r2"] = self._r2_settings()
        # The exported panels are trimmed the way the Resistivity model view trims
        # the section ("Hide below" + "Clean cut"), the one place this is chosen.
        cut = self._model_view.clean_cut()
        if cut is not None:
            params["figure_clip"] = "envelope"
            params["figure_clip_threshold"] = cut
        times = self._tl_times if len(self._tl_times) == len(self._tl_files) else None
        timing = getattr(self, "_tl_timing", None)
        # The bundle below renames the files, so the acquisition times have to
        # travel with the run or the intervals cannot be reported from inside it.
        stamps = ([t.isoformat(sep=" ") for t in timing.timestamps]
                  if timing is not None and timing.dated else [])
        try:
            run = self.begin_persisted_run(
                "ert.timelapse_inversion", "ert.timelapse_inversion",
                label=self._run_label(self._tl_files, unit="surveys"),
            )
        except Exception as exc:  # noqa: BLE001
            self.log(f"Could not prepare Project run: {exc}", "error")
            return
        # Drop this module's references to the previous run's arrays before the
        # new one writes. They are ordinary in-memory arrays, but releasing
        # them keeps a stale model out of the viewer if the run fails.
        self._tl_models = None
        self._tl_models_raw = None
        self._tl_correction = None
        self._tl_coverage = None
        if getattr(self, "_map_result_kind", "") == "timelapse":
            # The series the panel was correcting is gone; a single inversion on
            # screen instead stays correctable while this one runs.
            self._tc_box.set_available(False, _TC_WAITING)
        # The list can be edited while the surveys are filtered below, so the run
        # keeps the sequence as it stood when Run was pressed.
        sources, labels = list(self._tl_files), list(self._tl_labels)
        # The electrode file places every survey's electrodes, as it placed the
        # survey on screen; otherwise the run would read each file's own header
        # while the preview showed the electrode file's positions.
        electrodes = self._electrode_file()
        if electrodes is not None:
            self.log("Time-lapse: every survey's electrodes are placed from "
                     f"{(self._electrode_path or Path(electrodes)).name}.", "info")
        self._tl_busy = BusyStateController([self._tl_btn])
        self._tl_busy.start()
        self._tl_btn.setText(QCoreApplication.translate("PHGX", "Inverting…"))
        self._tl_progress.setVisible(True); self._tl_progress.setRange(0, 0)
        qc = self._qc_applied
        # Each survey's reciprocal file, as the list paired them when Run was
        # pressed, and the reciprocal files it left out.
        partners = [self._tl_partner.get(path) for path in sources]
        left_out = list(self._tl_left_out)
        fit_model = self._err_source.currentData() == "reciprocal"
        # What the error model is fitted to, as the Reciprocal errors tab said
        # when Run was pressed; the surveys' cache keys, so the pairs the QC
        # reads are kept for the tab, and the ones the tab read can serve here.
        fit_to = self._error_fit_to()
        survey_keys = [self._recip_survey_key(path, partner)
                       for path, partner in zip(sources, partners)]
        qc_key = self._recip_qc_key(qc)
        reader = f"{instrument or 'auto-detected format'}" + (
            # The user's electrode file, not the readers' copy of it.
            f", electrodes from {(self._electrode_path or Path(electrodes)).name}"
            if electrodes is not None else "")
        if qc is None and not any(partners) and not fit_model:
            self.log("Time-lapse QC: no filter applied, so every survey is inverted as "
                     "loaded. The Data QC thresholds take effect with Apply filter, and "
                     "then filter every survey of the series.", "info")
            self._launch_timelapse(run, sources, sources, labels, params, times, stamps, None,
                                   electrodes, fit_to=fit_to)
            return
        if qc is None and not any(partners):
            # Read only to fit the model: when the Reciprocal errors tab has read
            # every survey already, its pairs are fitted and the surveys go to
            # the run as they are, as they do with no model.
            cached = [self._recip_cache.get(key, {}).get(qc_key) for key in survey_keys]
            if all(entry is not None and not entry.get("error") for entry in cached):
                self._fit_timelapse_from_cache(run, sources, labels, params, times, stamps,
                                               electrodes, [dict(e) for e in cached],
                                               reader, left_out, fit_to)
                return
        # The QC applied on this page holds for the whole series, as for the
        # survey on screen. Each survey is filtered on its own - the
        # pipeline accepts surveys with different measurement sets, and ADTLERT
        # aligns them - and handed over in PyGIMLi's own format, which it reads
        # back as written, as the single inversion's filtered data is. A survey
        # of two files is merged first, so its pairs are formed across them; and
        # the reciprocal error model is fitted over every survey's pairs.
        doing = [f"filtering as Apply filter did ({self._describe_qc(qc)})"
                 if qc is not None else "no QC filter applied"]
        if any(partners):
            doing.insert(0, f"merging {sum(1 for p in partners if p)} with their "
                            "reciprocal file")
        if fit_model:
            doing.append("fitting the reciprocal error model over the series, to "
                         + self._fit_to_text(fit_to, qc))
        self.log(f"Time-lapse QC: preparing each of the {len(sources)} surveys - "
                 + "; ".join(doing) + "…", "info")
        if left_out:
            self.log(f"Time-lapse: {len(left_out)} reciprocal file(s) have no forward file "
                     "and are left out of the run: "
                     + ", ".join(Path(p).name for p in left_out) + ".", "warn")
        # Its QC logs and report go in the run folder (qt_apps/ert_records.py).
        worker = TaskWorker(self._qc_series, sources, instrument, qc,
                            run.inputs_dir / "ert_timesteps_qc", with_log=True,
                            electrode_file=electrodes, report_dir=run.run_dir,
                            acquired=stamps, error_model=self._error_model_text(True),
                            reader=reader, partners=partners, left_out=left_out,
                            fit_model=fit_model, floor=self._reciprocal_floor(),
                            fit_to=fit_to)

        def prepared(out: Dict[str, Any]) -> None:
            # Every survey's pairs as the run read them, for the Reciprocal
            # errors tab, which then need not read the series again.
            for key, report in zip(survey_keys, out.get("reports") or []):
                self._cache_recip(self._recip_cache, key, qc_key, self._recip_entry(report))
            self._recip_inputs_changed()
            run_params = {**params, "instrument": None}
            model = out.get("model")
            if fit_model and model:
                run_params["error_model"] = model
            elif fit_model:
                self.log("Data errors: the series has too few reciprocal pairs to fit an "
                         "error model (at least 15 are needed), so each survey keeps its "
                         "own errors.", "warn")
            self._launch_timelapse(
                run, sources, out["files"], labels, run_params, times, stamps,
                {"thresholds": qc, "source_instrument": instrument, "steps": out["steps"],
                 "partners": partners, "left_out": left_out}, electrodes, fit_to=fit_to)

        worker.logged.connect(self._on_tl_qc_logged)
        worker.succeeded.connect(prepared)
        worker.failed.connect(self._on_tl_qc_failed)
        # Stopped, it ends at the next survey without a word; the button comes back.
        worker.finished.connect(
            lambda w=worker: self._reset_tl_button() if w.is_cancelled() else None)
        self._tl_qc_worker = self.register_worker(worker, activity="Checking data quality")
        self._tl_progress.setRange(0, len(sources))
        self._tl_progress.setValue(0)
        self._tl_progress.setFormat(f"Data QC 0/{len(sources)}")
        worker.start()
        # Reading every survey takes minutes for a long series, so the QC can
        # be stopped like the inversion that follows it.
        self._tl_stop.attach(worker, "ert.timelapse_inversion", "The time-lapse data QC")

    @staticmethod
    def _fit_to_text(fit_to: str, qc: Optional[Dict[str, Any]]) -> str:
        from PyHydroGeophysX.qt_apps.ert_records import fit_to_sentence

        return fit_to_sentence(fit_to, qc is not None)

    def _fit_timelapse_from_cache(self, run, sources: List[str], labels: List[str],
                                  params: Dict[str, Any], times, stamps: List[str],
                                  electrodes: Optional[str], reports: List[Dict[str, Any]],
                                  reader: str, left_out: List[str], fit_to: str) -> None:
        """Fit the series' error model to the pairs the Reciprocal errors tab
        read, write the QC records from them, and start the run on the surveys
        as they are - with no filter and no reciprocal files to merge, the
        surveys were read only for these pairs, and are not read twice."""
        self.log(f"Time-lapse: fitting the reciprocal error model to the pairs of the "
                 f"{len(sources)} surveys the Reciprocal errors tab has read, to "
                 f"{self._fit_to_text(fit_to, None)}; the surveys are not read again.",
                 "info")
        worker = TaskWorker(self._finish_series_qc, list(sources), reports, with_log=True,
                            report_dir=run.run_dir, stamps=list(stamps), reader=reader,
                            qc=None, error_model=self._error_model_text(True), fit_model=True,
                            floor=self._reciprocal_floor(), left_out=list(left_out),
                            fit_to=fit_to, logs_written=False)

        def fitted(model: Optional[Dict[str, Any]]) -> None:
            run_params = dict(params)
            if model:
                run_params["error_model"] = model
            else:
                self.log("Data errors: the series has too few reciprocal pairs to fit an "
                         "error model (at least 15 are needed), so each survey keeps its "
                         "own errors.", "warn")
            self._launch_timelapse(run, sources, sources, labels, run_params, times, stamps,
                                   None, electrodes, fit_to=fit_to)

        worker.logged.connect(lambda message: self.log(message, "info"))
        worker.succeeded.connect(fitted)
        worker.failed.connect(self._on_tl_qc_failed)
        worker.finished.connect(
            lambda w=worker: self._reset_tl_button() if w.is_cancelled() else None)
        self._tl_qc_worker = self.register_worker(worker, activity="Fitting the error model")
        worker.start()
        self._tl_stop.attach(worker, "ert.timelapse_inversion", "The time-lapse data QC")

    def _on_tl_qc_logged(self, message: str) -> None:
        """Log a line of the time-lapse QC, and move its progress bar per survey."""
        self.log(message, "info")
        match = re.match(r"^QC (\d+)/(\d+) ", str(message))
        if match is not None:
            done, total = int(match.group(1)), int(match.group(2))
            self._on_tl_progress(done, total, f"Data QC {done}/{total}")
            # The status bar too: reading a long series takes minutes, and a bare
            # "Checking data quality" for that long reads as a hang.
            worker = getattr(self, "_tl_qc_worker", None)
            if worker is not None:
                self._on_worker_progress(worker, done, total, "Checking data quality")

    @staticmethod
    def _describe_qc(qc: Dict[str, Any]) -> str:
        """The thresholds in ``qc`` that cut anything, in the panel's terms."""
        parts = [f"ρa {qc['min_rhoa']:g}–{qc['max_rhoa']:g} Ω·m"]
        if qc.get("average_reciprocals"):
            parts.insert(0, "each reading averaged with its reciprocal")
        if qc["max_error"] > 0:
            parts.append(f"error ≤ {qc['max_error']:g} %")
        if qc["more_checks"]:
            extra = [(qc["drop_nonpositive"], "ρa > 0"),
                     (qc["min_voltage"] > 0, f"|V| ≥ {qc['min_voltage']:g}"),
                     (qc["min_current"] > 0, f"|I| ≥ {qc['min_current']:g}"),
                     (qc["max_k"] > 0, f"|k| ≤ {qc['max_k']:g}"),
                     (qc["max_contact_r"] > 0, f"contact R ≤ {qc['max_contact_r']:g} Ω"),
                     (qc.get("max_stack", 0.0) > 0,
                      f"stacking spread ≤ {qc.get('max_stack', 0.0):g} %"),
                     (qc["max_reciprocal"] > 0, f"reciprocal error ≤ {qc['max_reciprocal']:g} %")]
            parts.extend(text for on, text in extra if on)
        return ", ".join(parts)

    @classmethod
    def _prepare_survey(cls, source: str, partner: Optional[str], instrument: Optional[str],
                        electrode_file: Optional[str], qc: Optional[Dict[str, Any]], *,
                        paired_series: bool = False, log=None):
        """``(data, report, reasons)``: one survey of a series, as the run prepares it.

        The file is read the way the time-lapse pipeline reads it, electrodes
        placed from ``electrode_file`` when there is one; with ``partner``,
        that reciprocal file is read too and merged with it
        (``ert_io.merge_reciprocal``), so its pairs are formed across the two.
        ``qc`` - None when no filter was applied - then filters it, check 0
        included (:meth:`_qc_survey`), marking which pairs it kept. ``report``
        is the survey's QC log as ``ert_records.survey_qc_log`` reads it. The
        run's QC (:meth:`_qc_series`) and the Reciprocal errors tab both read
        their surveys here, so the two hold the same pairs.
        """
        log = log or (lambda _message: None)
        data = ert_load.load_ert_container(source, instrument=instrument, log=log,
                                           electrode_file=electrode_file)
        report: Dict[str, Any] = {}
        if partner:
            other = ert_load.load_ert_container(partner, instrument=instrument, log=log,
                                                electrode_file=electrode_file)
            try:
                data, merged = ert_load.merge_reciprocal(data, other)
            except ValueError as exc:
                raise ValueError(
                    f"{Path(source).name} and its reciprocal file {Path(partner).name} "
                    f"could not be merged: {exc}") from exc
            report["files"] = {
                "forward": Path(source).name, "reciprocal": Path(partner).name,
                "forward_readings": merged["forward"],
                "reciprocal_readings": merged["reciprocal"],
                "dropped_fields": merged["dropped_fields"]}
        elif paired_series:
            report["files"] = {"forward": Path(source).name, "reciprocal": None,
                               "forward_readings": int(data.size())}
        if qc is not None:
            data, _keep, reasons = cls._qc_survey(data, qc, report)
        else:
            from PyHydroGeophysX.qt_apps.ert_records import reciprocal_pairing

            reasons = []
            report.update(readings=int(data.size()), kept=int(data.size()), checks=[],
                          pairing=reciprocal_pairing(cls._reciprocal_scores(data)))
        return data, report, reasons

    @classmethod
    def _qc_series(cls, files: List[str], instrument: Optional[str],
                   qc: Optional[Dict[str, Any]],
                   staging: Path, log=None,
                   electrode_file: Optional[str] = None,
                   report_dir: Optional[Path] = None,
                   acquired: Optional[List[str]] = None,
                   error_model: str = "", reader: str = "",
                   partners: Optional[List[Optional[str]]] = None,
                   left_out: Optional[List[str]] = None, fit_model: bool = False,
                   floor: float = 0.0, fit_to: str = "all") -> Dict[str, Any]:
        """Prepare every survey of a series for the run; runs off the UI thread.

        Each survey is read, merged with its reciprocal file in ``partners``
        and filtered by ``qc`` as :meth:`_prepare_survey` does it, and written
        back. Returns the prepared files, in order, per survey what was kept,
        ``reports`` (each survey's QC report, its pairing among it) and
        ``model``: with ``fit_model``, the reciprocal error model fitted over
        the pairs ``fit_to`` names - all of them as read, or those the filter
        kept - (``ert_records.fit_series_error_model``, the fit the QC report
        states), its errors never below ``floor``; None when there are too few
        pairs.

        With ``report_dir`` (the run folder) each survey's QC log goes in its
        ``qc/`` folder as it is prepared - a survey that stops the series
        included - and ``qc_report.txt`` sums them up at the end, naming the
        reciprocal files ``left_out`` for want of a forward file. Once the
        series' model is known each log is written again with it at the top
        (:meth:`_finish_series_qc`).
        """
        from PyHydroGeophysX.qt_apps import ert_records
        from PyHydroGeophysX.qt_apps.run_records import QC_FOLDER

        log = log or (lambda _message: None)
        staging = Path(staging)
        staging.mkdir(parents=True, exist_ok=True)
        out_files: List[str] = []
        steps: List[Dict[str, Any]] = []
        reports: List[Dict[str, Any]] = []
        stamps = list(acquired or [])
        partners = list(partners or [])
        paired_series = any(partners)
        reader = reader or f"{instrument or 'auto-detected format'}" + (
            f", electrodes from {Path(electrode_file).name}" if electrode_file else "")

        for index, source in enumerate(files):
            partner = partners[index] if index < len(partners) else None
            data, report, reasons = cls._prepare_survey(
                source, partner, instrument, electrode_file, qc,
                paired_series=paired_series, log=log)
            kept, total = int(report["kept"]), int(report["readings"])
            if report_dir is not None:
                ert_records.write_series_qc_logs(
                    Path(report_dir) / QC_FOLDER, index, len(files), source, report,
                    acquired=stamps[index] if index < len(stamps) else "", reader=reader,
                    fit_to=fit_to)
            reports.append(report)
            if kept < 4:
                raise ValueError(
                    f"the QC filter leaves {kept} of {total} measurements in "
                    f"{Path(source).name}, and a time-lapse step needs at least four. "
                    "Loosen the Data QC thresholds, or Reset them.")
            target = staging / f"step_{index:04d}.dat"
            data.save(pygimli_path(str(target), create=True))
            out_files.append(str(target))
            steps.append({"file": Path(source).name, "kept": kept, "total": total,
                          "cut": list(reasons), "qc": ert_records.step_summary(report)})
            pair_note = (f" + {Path(partner).name} (forward {report['files']['forward_readings']}"
                         f" | reciprocal {report['files']['reciprocal_readings']})"
                         if partner else "")
            log(f"QC {index + 1}/{len(files)} {Path(source).name}{pair_note}: kept {kept} "
                f"of {total}" + (f" ({'; '.join(reasons)})" if reasons else ""))
        model = cls._finish_series_qc(
            files, reports, report_dir=report_dir, stamps=stamps, reader=reader, qc=qc,
            error_model=error_model, fit_model=fit_model, floor=floor,
            left_out=left_out, fit_to=fit_to, log=log)
        return {"files": out_files, "steps": steps, "model": model, "reports": reports}

    @staticmethod
    def _fitted_over(fit: Dict[str, Any], series: bool) -> str:
        """The pairs a fitted model is over, for the settings file."""
        from PyHydroGeophysX.qt_apps.ert_records import FIT_KEPT

        where = f" of {fit['surveys']} surveys" if series else ""
        if fit.get("fit_to") == FIT_KEPT and fit.get("filtered"):
            return (f"the {fit['n']} reciprocal pairs{where} the filter kept; the "
                    f"{fit['left_out']} it removed are left out")
        if fit.get("fit_to") == FIT_KEPT:
            return f"{fit['n']} reciprocal pairs{where} (no filter applied, so every pair)"
        return f"{fit['n']} reciprocal pairs{where}, as read, before any filter"

    @classmethod
    def _finish_series_qc(cls, files: List[str], reports: List[Dict[str, Any]], *,
                          report_dir: Optional[Path], stamps: List[str], reader: str,
                          qc: Optional[Dict[str, Any]], error_model: str, fit_model: bool,
                          floor: float, left_out: Optional[List[str]], fit_to: str,
                          logs_written: bool = True, log=None) -> Optional[Dict[str, Any]]:
        """Fit the series' reciprocal error model and finish its QC records.

        ``reports`` are each survey's QC report (:meth:`_prepare_survey`). One
        model over the whole series, over the pairs ``fit_to`` names - the
        fit ``error_model_lines`` reports and the figure draws - so the
        records and the run agree; returned when ``fit_model``, else None.
        With ``report_dir`` each survey's QC log is written again with the
        model at its top (written for the first time, ``logs_written`` False,
        when the surveys were read for the Reciprocal errors tab instead), and
        ``qc_report.txt`` with the figure.
        """
        from PyHydroGeophysX.qt_apps import ert_records
        from PyHydroGeophysX.qt_apps.run_records import QC_FOLDER

        log = log or (lambda _message: None)
        fitted = ert_records.fit_series_error_model(
            [r.get("pairing") or {} for r in reports], fit_to)
        model = None
        if fit_model and fitted is not None:
            model = {"m": fitted["m"], "b": fitted["b"], "r2": fitted["r2"],
                     "r2_raw": fitted["r2_raw"], "pairs": fitted["n"],
                     "surveys": fitted["surveys"], "floor": float(floor),
                     "fitted_over": cls._fitted_over(fitted, series=True)}
            log(f"Reciprocal error model over the series, fitted to "
                f"{ert_records.fit_to_sentence(fit_to, fitted['filtered'])}: "
                f"{ert_records.power_law(model)} (binned R2 {fitted['r2']:.3f}, "
                f"{fitted['n']} pairs from {fitted['surveys']} surveys); every reading's "
                f"error is dR / |R|, at least {100.0 * float(floor):g} %.")
        if report_dir is not None:
            if fitted is not None or not logs_written:
                line = "" if fitted is None else (
                    f"{ert_records.power_law(fitted)} (global fit over the series, to "
                    f"{ert_records.FIT_TO_TEXT[fitted['fit_to']]}"
                    + ("; used as the data errors)" if model else
                       "; for reference, not used as the data errors)"))
                for index, (source, report) in enumerate(zip(files, reports)):
                    ert_records.write_series_qc_logs(
                        Path(report_dir) / QC_FOLDER, index, len(files), source, report,
                        acquired=stamps[index] if index < len(stamps) else "",
                        reader=reader, model=line, fit_to=fit_to)
            path = ert_records.write_series_qc_report(
                Path(report_dir), sources=files, acquired=stamps, reader=reader, qc=qc,
                reports=reports, error_model=error_model, applied_model=model,
                left_out=list(left_out or []), fit_to=fit_to)
            log(f"Data QC report written to {path}; each survey's QC log is in "
                f"{Path(report_dir) / QC_FOLDER}")
        return model

    def _on_tl_qc_failed(self, message: str) -> None:
        """A survey could not be read or filtered, so the inversion never started."""
        self._on_tl_failed(message, False)
        self._reset_tl_button()

    def _launch_timelapse(self, run, sources: List[str], files: List[str],
                          labels: List[str], params: Dict[str, Any], times, stamps,
                          qc: Optional[Dict[str, Any]],
                          electrodes: Optional[str] = None, *,
                          fit_to: str = "all") -> None:
        """Persist the series as it will be inverted, and start the workflow.

        ``sources`` are the files as the user listed them, ``files`` what is
        inverted: the same files, or their QC-filtered copies when ``qc`` says
        what filtered them. ``electrodes`` is the electrode table every survey
        is placed on; the run keeps its own copy, so it reruns as it ran.
        ``fit_to`` is what the reciprocal error model was fitted to, for the
        settings file.
        """
        electrodes_ref = None
        # One compressed bundle rather than a copy of every step. A time-lapse
        # run is as many raw files as it has time steps, and BERT data files are
        # ASCII, so loose copies would be the bulk of the run directory.
        try:
            stored = run_inputs.save_file_bundle(
                run.inputs_dir / "ert_timesteps",
                {
                    f"step_{index:04d}{Path(source).suffix}": Path(source)
                    for index, source in enumerate(files)
                },
                kind="ert_timelapse_observations",
                meta={
                    "measurement_times": [
                        float(times[index]) if times is not None else float(index)
                        for index in range(len(files))
                    ]
                },
            )
            if qc is not None:
                io_utils.write_json(run.inputs_dir / "ert_qc.json", {
                    **{key: value for key, value in qc.items()
                       if key not in ("partners", "left_out")},
                    "source_files": [Path(source).name for source in sources],
                    # Each survey's reciprocal file, merged into it, by name.
                    "reciprocal_files": [Path(p).name if p else None
                                         for p in (qc.get("partners") or [])],
                    "left_out": [Path(p).name for p in (qc.get("left_out") or [])]})
                # The bundle holds the filtered surveys; the loose copies go.
                shutil.rmtree(run.inputs_dir / "ert_timesteps_qc", ignore_errors=True)
            if electrodes is not None:
                table = run.inputs_dir / "electrodes_xyz.txt"
                shutil.copyfile(electrodes, table)
                electrodes_ref = ArtifactRef.from_path(
                    table,
                    artifact_id="ert-electrodes",
                    kind="electrode_geometry",
                    format="txt",
                    base_dir=run.run_dir,
                    metadata={"source_file": self._electrode_path.name
                              if self._electrode_path else ""},
                )
        except Exception as exc:  # noqa: BLE001
            self.fail_persisted_run(str(exc), "ert.timelapse_inversion")
            self.log(f"Could not persist time-lapse inputs: {exc}", "error")
            self._reset_tl_button()
            return
        metadata: Dict[str, Any] = {"source": "qt", "sequence_order_persisted": True}
        if qc is not None:
            metadata.update(qc_filtered=True, source_instrument=qc.get("source_instrument"))
        spec = WorkflowSpec(
            workflow_id="ert.timelapse_inversion",
            inputs={
                "data_bundle": ArtifactRef.from_path(
                    stored,
                    artifact_id="ert-timesteps",
                    kind="ert_timelapse_observations",
                    base_dir=run.run_dir,
                    metadata={"step_count": len(files)},
                ),
                "measurement_times": list(times or range(len(files))),
                # The bundle renames the files, so the acquisition dates parsed
                # from the originals have to travel with the times or the panels
                # end up headed by a bare elapsed-day number.
                "time_labels": list(labels),
                "timestamps": stamps,
                "time_unit": "d" if times is not None else "",
                **({"electrodes": electrodes_ref} if electrodes_ref is not None else {}),
            },
            parameters=params,
            metadata=metadata,
        )
        recipe_path, script_path = export_workflow_bundle(
            spec, run.run_dir, stem="ert_timelapse"
        )
        self._reproduce.set_bundle(recipe_path, script_path)
        self._tl_recipe_path = str(recipe_path)
        self._write_timelapse_settings(run, spec, sources, labels, stamps, times,
                                       electrodes, qc, fit_to)
        if not any(stamps):
            # A warning, so it is kept with the run: every interval reads as one
            # unit, which changes what the temporal smoothing does.
            self.log("Time-lapse: the surveys carry no acquisition times, so every "
                     "step is one unit apart.", "warn")
        self._tl_progress.setRange(0, 0)
        self.log(f"Starting {params['inversion_type']} time-lapse ERT inversion "
                 f"({len(files)} steps)…", "info")
        # Both supported time-lapse engines execute long native/GPU kernels.
        # Keep every time-lapse run outside Qt's interpreter so PyGIMLi cannot
        # retain the GIL and ADTLERT cannot monopolize the GUI CUDA context.
        # This also covers an unavailable ADTLERT request that falls back to
        # the PyHydro engine inside the workflow process.
        # What this run inverts, kept with it: the list on the page can change
        # while it runs, and a hand-over must name the surveys of the model.
        self._tl_run_sources = [str(source) for source in sources]
        self._tl_run_params = dict(params)
        self._agent_run_state = "running"
        self._agent_run_error = ""
        self._tl_worker = ProcessWorkflowWorker(
            recipe_path,
            run.run_dir,
            run.outputs_dir,
            run.result_path,
        )
        self._tl_worker.logged.connect(lambda m: self.log(m, "info"))
        self._tl_worker.progressed.connect(self._on_tl_progress)
        self._tl_worker.succeeded.connect(self._on_tl_workflow_ok)
        self._tl_worker.failed.connect(lambda message: self._on_tl_failed(message, False))
        self._tl_worker.finished.connect(self._reset_tl_button)
        self.register_worker(self._tl_worker, activity="Running the time-lapse inversion")
        self._tl_worker.start()
        self._tl_stop.attach(self._tl_worker, "ert.timelapse_inversion")

    def _write_timelapse_settings(self, run, spec: WorkflowSpec, sources: List[str],
                                  labels: List[str], stamps: List[str], times,
                                  electrodes: Optional[str],
                                  qc: Optional[Dict[str, Any]],
                                  fit_to: str = "all") -> None:
        """Write the run's ``inversion_settings.txt`` from the spec it is handed
        (``qt_apps/ert_records.py``); the QC report was written as the surveys
        were filtered. A file that cannot be written is said in the log only.
        ``fit_to`` - what the error model was fitted to - is stated wherever
        the run fitted one: its QC report has the model, or it used it."""
        from PyHydroGeophysX.qt_apps import ert_records
        from PyHydroGeophysX.qt_apps.run_records import QC_REPORT_NAME

        self._tl_settings = None
        try:
            instrument = str((qc or {}).get("source_instrument")
                             or spec.parameters.get("instrument") or "auto-detected")
            model = dict(spec.parameters.get("error_model") or {}) or None
            path = ert_records.write_settings(run.run_dir, ert_records.timelapse_settings_text(
                spec, run_id=run.run_id, sources=sources, labels=labels, stamps=stamps,
                times=times, instrument=instrument,
                electrode_file=str(self._electrode_path or electrodes or ""), qc=qc,
                partners=(qc or {}).get("partners"), left_out=(qc or {}).get("left_out") or (),
                data_errors=self._error_model_text(True, model)
                + ("; pairs averaged by the QC carry their own difference"
                   if ((qc or {}).get("thresholds") or {}).get("average_reciprocals")
                   and not model else ""),
                fit_to=fit_to if model or (Path(run.run_dir) / QC_REPORT_NAME).is_file()
                else None))
            # With what was asked, to say afterwards what the engine changed.
            self._tl_settings = (path, dict(spec.parameters))
            self.log(f"Inversion settings written to {path}", "info")
        except Exception as exc:  # noqa: BLE001 - a record must not stop the run
            self.log(f"Could not write the run's settings file: {exc}", "warn")

    def _on_tl_progress(self, current: int, total: int, label: str) -> None:
        """Show completed ADTLERT windows while retaining the text log."""
        if total <= 0:
            return
        self._tl_progress.setRange(0, total)
        self._tl_progress.setValue(max(0, min(current, total)))
        self._tl_progress.setFormat(label or f"Progress {current}/{total}")

    def _on_tl_workflow_ok(self, result: WorkflowRunResult) -> None:
        if hasattr(self.state, "update_workflow_result"):
            self.state.update_workflow_result(
                self.module_key,
                "ert.timelapse_inversion",
                result.to_dict(),
                recipe_path=self._tl_recipe_path,
            )
        payload = result.legacy_payload()
        settings = self._tl_settings
        if settings is not None:
            self._record_outcome(settings[0], "timelapse", payload, settings[1])
        if payload.get("mesh") is None and payload.get("model_bundle"):
            payload.update(self._load_timelapse_bundle(payload["model_bundle"]))
        self._on_tl_ok(payload)

    def _load_timelapse_bundle(self, bundle: Dict[str, Any]) -> Dict[str, Any]:
        """Load process-safe time-lapse arrays for the interactive Qt viewer."""
        try:
            from PyHydroGeophysX.core.mesh_serialization import read_bms

            base = (
                Path(self._tl_recipe_path).resolve().parent
                if self._tl_recipe_path else Path.cwd()
            )

            def resolve(value: Any) -> Path:
                path = Path(str(value))
                return path if path.is_absolute() else base / path

            paths = dict(bundle)
            mesh_path = resolve(paths.get("mesh", ""))
            models_path = resolve(paths.get("models", ""))
            if not mesh_path.is_file() or not models_path.is_file():
                raise FileNotFoundError(
                    f"missing mesh or model bundle ({mesh_path}, {models_path})"
                )
            coverage_path = resolve(paths.get("coverage", ""))
            # Read into memory rather than memory-mapping. A mapping stays open for
            # as long as the viewer holds the array, and Windows refuses to let the
            # next run overwrite a mapped file: np.save fails with
            # "OSError: [Errno 22] Invalid argument" after the inversion has already
            # finished, leaving the previous run's arrays on disk beside the new
            # run's figures. These are per-cell result arrays, small enough that
            # mapping buys nothing.
            return {
                # Without the cell-neighbour table, as in _load_model_bundle.
                "mesh": read_bms(mesh_path, neighbours=False),
                "final_models": np.load(models_path, allow_pickle=False),
                "coverage": (
                    np.load(coverage_path, allow_pickle=False)
                    if coverage_path.is_file() else None
                ),
            }
        except Exception as exc:  # noqa: BLE001 - retain scalar results on failure
            self.log(f"Could not load time-lapse model files: {exc}", "error")
            return {"mesh": None, "final_models": None, "coverage": None}
