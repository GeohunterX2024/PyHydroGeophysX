"""The ERT page: data errors, fit assistance, the Reciprocal errors tab and the pseudosection (plan M4.5).

Part of :class:`~.page.ERTProcessingModule`, split from the former
``ert_processing.py`` by area; the methods are unchanged.
"""

from __future__ import annotations

from .common import (
    Any,
    Dict,
    List,
    Optional,
    Path,
    QCoreApplication,
    QFileDialog,
    TaskWorker,
    Tuple,
    _ELECTRODE_MARK,
    _ELEC_FILTER,
    _EMPTY_DATA_MESSAGE,
    _RECIP_HOW,
    _RECIP_NO_DATA,
    cmaps,
    ert_load,
    i18n,
    json,
    length_factor,
    length_units,
    np,
    os,
    re,
    set_length_axis,
    uuid,
)


class _QCPanel:

    # -- the Reciprocal errors tab --------------------------------------------
    def _error_fit_to(self) -> str:
        """What the reciprocal error model is fitted to: the tab's "Fit to"."""
        return self._recip_view.fit_to()

    def _on_error_fit_changed(self, fit_to: str) -> None:
        from PyHydroGeophysX.qt_apps.ert_records import FIT_TO_TEXT

        self.log(f"Reciprocal error model: fitted to {FIT_TO_TEXT[fit_to]} - for data errors "
                 "taken from it, the QC report and the run's figure.", "info")

    def _recip_inputs_changed(self, *_args: Any) -> None:
        """Something the Reciprocal errors tab draws changed: the data, the file
        list or its pairing, the filter. Redrawn a moment later while the tab is
        on screen, so a burst of changes reads a series once; off screen when
        the tab is next opened."""
        timer = getattr(self, "_recip_timer", None)
        if timer is not None and self._tabs.currentWidget() is self._recip_view:
            timer.start()

    def _recip_series_mode(self) -> bool:
        """Whether the tab shows the time-lapse series rather than one survey."""
        box = getattr(self, "_tl_mode", None)
        return bool(box is not None and box.isChecked() and len(self._tl_files) >= 2)

    def _single_pairing(self) -> Optional[Dict[str, Any]]:
        """The loaded survey's reciprocal pairing: with each pair marked kept or
        not when Apply filter filtered these data, otherwise as read."""
        if self._qc_report is not None and self._qc_applied is not None:
            pairing = self._qc_report.get("pairing")
            if pairing:
                return pairing
        if self._loaded_pairing is None and self._ert_data_full is not None:
            from PyHydroGeophysX.qt_apps.ert_records import reciprocal_pairing

            self._loaded_pairing = reciprocal_pairing(
                self._reciprocal_scores(self._ert_data_full))
        return self._loaded_pairing

    def _sync_recip_use(self, *_args: Any) -> None:
        """Tell the Reciprocal errors tab whether the next run uses its model."""
        view = getattr(self, "_recip_view", None)
        if view is not None:
            view.set_use_state(self._err_source.currentData() == "reciprocal")

    def _use_reciprocal_errors(self) -> None:
        """The tab's "Use for the data errors": the source under Data errors."""
        index = self._err_source.findData("reciprocal")
        if index >= 0:
            self._err_source.setCurrentIndex(index)
            self.log("Data errors now come from the reciprocal error model.", "info")

    def _refresh_recip_view(self) -> None:
        """Draw the Reciprocal errors tab for the data on the page: the survey
        on screen, or, in time-lapse mode, every survey of the list."""
        if not hasattr(self, "_tl_mode"):
            return                                   # still being built
        self._recip_timer.stop()
        if self._recip_series_mode():
            self._show_series_pairs()
            return
        from PyHydroGeophysX.qt_apps.ert_records import error_model_pairs

        view = self._recip_view
        if self._ert_data_full is None:
            view.show_message(
                _RECIP_NO_DATA if self._data_path is None else
                f"{self._data_path.name} could not be converted for inversion, so its "
                "readings cannot be paired with their reciprocals.")
            return
        pairing = self._single_pairing() or {}
        pairs = error_model_pairs([pairing])
        if not pairs["R"].size:
            name = self._data_path.name if self._data_path is not None else "These data"
            view.show_message(
                f"Every reciprocal pair of {name} agrees exactly, so there is no error to "
                "plot." if pairing.get("scored_pairs") else
                f"{name} has no reciprocal pairs: no reading was measured a second time "
                "with its current and potential electrodes exchanged, so there is nothing "
                "to plot.\n\n" + _RECIP_HOW)
            return
        view.show_pairs(pairs, series=False)

    def _recip_survey_key(self, source: str, partner: Optional[str]) -> tuple:
        """What a survey's pairs depend on: its files as they are on disk, the
        reader and the electrode file."""
        def stamp(path: Optional[str]) -> Optional[tuple]:
            if not path:
                return None
            try:
                status = os.stat(path)
            except OSError:
                return (str(path), None, None)
            return (str(path), status.st_mtime_ns, status.st_size)

        return (stamp(source), stamp(partner), str(self._instrument.currentData()),
                stamp(self._electrode_file()))

    @staticmethod
    def _recip_qc_key(qc: Optional[Dict[str, Any]]) -> str:
        """The filter a survey was read through, as a cache key ("" for none)."""
        return json.dumps(qc, sort_keys=True, default=str) if qc else ""

    def _series_recip_jobs(self) -> Tuple[List[Tuple[str, Optional[str], tuple]],
                                          Optional[Dict[str, Any]], str]:
        """``(jobs, qc, qc_key)``: each survey of the list with its reciprocal
        file and cache key, and the filter a time-lapse run puts them through -
        Apply filter's, as the run applies it to every survey."""
        jobs = []
        for source in self._tl_files:
            partner = self._tl_partner.get(source)
            jobs.append((source, partner, self._recip_survey_key(source, partner)))
        qc = dict(self._qc_applied) if self._qc_applied is not None else None
        return jobs, qc, self._recip_qc_key(qc)

    def _show_series_pairs(self) -> None:
        """Draw every survey's pairs, reading the surveys not read yet first."""
        from PyHydroGeophysX.qt_apps.ert_records import error_model_pairs

        jobs, qc, qc_key = self._series_recip_jobs()
        reports = [self._recip_cache.get(key, {}).get(qc_key) for _s, _p, key in jobs]
        missing = [job for job, report in zip(jobs, reports) if report is None]
        if missing:
            self._start_recip_read(missing, qc, qc_key, len(jobs))
            return
        failed = [Path(source).name for (source, _p, _k), report in zip(jobs, reports)
                  if report.get("error")]
        unread = ""
        if failed:
            unread = (f"{len(failed)} survey(s) could not be read and are not drawn: "
                      + ", ".join(failed[:3]) + (", …" if len(failed) > 3 else "") + ".")
        pairs = error_model_pairs([report.get("pairing") or {} for report in reports])
        if not pairs["R"].size:
            self._recip_view.show_message(
                f"None of the {len(jobs)} surveys has reciprocal pairs: no reading was "
                "measured a second time with its current and potential electrodes "
                "exchanged, so there is nothing to plot.\n\n" + _RECIP_HOW
                + (f"\n\n{unread}" if unread else ""))
            return
        self._recip_view.show_pairs(pairs, series=True,
                                    note=unread)

    def _start_recip_read(self, missing: List[Tuple[str, Optional[str], tuple]],
                          qc: Optional[Dict[str, Any]], qc_key: str, total: int) -> None:
        """Read the surveys of ``missing`` off the UI thread, with progress."""
        reading = (tuple(key for _s, _p, key in missing), qc_key)
        worker = self._recip_worker
        if worker is not None and worker.isRunning():
            if self._recip_reading == reading:
                return                                # already reading these
            worker.cancel()                           # what it read is kept
        self._recip_view.show_message(self._recip_reading_text(0, len(missing), total))
        worker = TaskWorker(self._read_recip_surveys, list(missing),
                            self._instrument.currentData(), self._electrode_file(), qc,
                            qc_key, self._recip_cache, with_log=True)
        worker.logged.connect(
            lambda message, w=worker, n=total: self._on_recip_read_logged(w, message, n))
        worker.failed.connect(lambda message: self.log(
            f"Reading the surveys' reciprocal pairs stopped: {message}", "warn"))
        worker.finished.connect(lambda w=worker: self._on_recip_read_done(w))
        self._recip_worker = self.register_worker(
            worker, activity="Reading the surveys' reciprocal pairs")
        self._recip_reading = reading
        worker.start()

    @staticmethod
    def _recip_reading_text(done: int, count: int, total: int) -> str:
        before = f" ({total - count} read before)" if count < total else ""
        return (f"Reading the reciprocal pairs of {count} surveys{before}: {done} of {count} "
                "done.\n\nA long series takes a few minutes; the page can be used "
                "meanwhile.")

    def _on_recip_read_logged(self, worker: Any, message: str, total: int) -> None:
        match = re.match(r"^(\d+)/(\d+) ", str(message))
        if match is None:
            return
        done, count = int(match.group(1)), int(match.group(2))
        self._on_worker_progress(worker, done, count, "Reading the surveys' reciprocal pairs")
        if worker is self._recip_worker and not self._recip_view.has_plot():
            self._recip_view.show_message(self._recip_reading_text(done, count, total))

    def _on_recip_read_done(self, worker: Any) -> None:
        if worker is not self._recip_worker:
            return                                    # replaced by a newer read
        self._recip_worker = None
        self._recip_reading = None
        if not worker.is_cancelled() and self._tabs.currentWidget() is self._recip_view:
            self._refresh_recip_view()

    @classmethod
    def _read_recip_surveys(cls, jobs: List[Tuple[str, Optional[str], tuple]],
                            instrument: Optional[str], electrode_file: Optional[str],
                            qc: Optional[Dict[str, Any]], qc_key: str,
                            cache: Dict[tuple, Dict[str, Dict[str, Any]]], log=None) -> int:
        """Read each survey of ``jobs`` as the time-lapse run prepares it
        (:meth:`_prepare_survey`) and keep its QC report in ``cache``; runs off
        the UI thread. Each survey is kept as soon as it is read, so a read
        stopped half way keeps that half; one that cannot be read is kept as
        its error, so it is named rather than read again and again."""
        log = log or (lambda _message: None)
        for done, (source, partner, key) in enumerate(jobs, start=1):
            try:
                _data, report, _reasons = cls._prepare_survey(
                    source, partner, instrument, electrode_file, qc)
                entry = cls._recip_entry(report)
            except Exception as exc:  # noqa: BLE001 - one unreadable survey is named
                entry = {"error": str(exc), "readings": 0, "kept": 0, "pairing": {}}
            cls._cache_recip(cache, key, qc_key, entry)
            log(f"{done}/{len(jobs)} {Path(source).name}")
        return len(jobs)

    @staticmethod
    def _recip_entry(report: Dict[str, Any]) -> Dict[str, Any]:
        """The part of a survey's QC report the tab and the run's records use."""
        return {key: report[key] for key in ("readings", "kept", "checks", "pairing",
                                             "files", "averaged") if key in report}

    @staticmethod
    def _cache_recip(cache: Dict[tuple, Dict[str, Dict[str, Any]]], key: tuple,
                     qc_key: str, entry: Dict[str, Any]) -> None:
        """Keep a survey's report under its filter; two filters per survey at most."""
        slot = cache.setdefault(key, {})
        slot.pop(qc_key, None)
        slot[qc_key] = entry
        while len(slot) > 2:
            slot.pop(next(iter(slot)))

    @staticmethod
    def _read_electrodes(path: str) -> Tuple[List[float], List[float], List[float], str, bool]:
        """``(x, y, z, how, three_d)`` from an electrode file, its columns chosen by meaning.

        ``table_io.read_electrode_table`` decides, the reader the data loaders
        use as well, and z is each electrode's elevation. Taking the first
        column as x and the last as z read an ID column as the elevation, the
        electrode number as the position, or - for a table written the PyGIMLi
        way, x, elevation, 0 - a flat line at zero. Electrodes that cover an
        area are a 3-D survey's (``ert_io.read_electrode_layout``) and keep
        their y; a profile's y is 0.
        """
        positions, three_d, how = ert_load.read_electrode_layout(path)
        z = positions[:, 2] if three_d else positions[:, 1]
        y = positions[:, 1] if three_d else np.zeros(len(positions))
        return positions[:, 0].tolist(), y.tolist(), z.tolist(), how, three_d

    def _electrode_table_for(self, path: str, x: List[float], z: List[float],
                             y: Optional[List[float]] = None) -> Optional[Path]:
        """A plain x y z copy of ``path`` for the readers, or None if none can be written.

        The instrument readers take the electrode file as positional x y z
        columns, so the vendor table itself would be misread there the way it
        was here. They get the columns as chosen above instead. Each file gets a
        copy of its own, so the one in use survives a file that is refused.
        A 3-D survey's copy (``y`` given) names its columns, which is what
        keeps a flat grid's y a coordinate rather than an elevation.
        """
        try:
            table = (self.state.ensure_results_store().scratch_dir(self.module_key)
                     / f"electrodes_xyz_{uuid.uuid4().hex[:8]}.txt")
            if y is not None:
                np.savetxt(table, np.column_stack([x, y, z]), header="x y z", comments="")
            else:
                np.savetxt(table, np.column_stack([x, np.zeros(len(x)), z]))
            return table
        except Exception as exc:  # noqa: BLE001
            self.log(f"Later loads cannot use {Path(path).name}: {exc}", "warn")
            return None

    def _take_electrode_file(self, path: str, *, wait: bool = False) -> Dict[str, Any]:
        """Make ``path`` the electrode positions, through the reader the data use.

        Before any data is loaded, the positions are shown and every later load
        reads with them. With data on screen, the data are read again with the
        file, so both orders end in one result: the reader matches rows to the
        data's electrodes in order, refuses a file listing a different number of
        them, and carries apparent resistivities formed on the header's positions
        over to the file's. Laid over loaded data instead, a file one row short
        dropped that electrode and every reading on it, and the apparent
        resistivities stayed those of the old positions.

        ``wait`` holds the call until the data have been read again (the
        assistant needs the outcome to answer); otherwise that happens in the
        background and is reported in the log.
        """
        name = Path(path).name
        try:
            x, y, z, how, three_d = self._read_electrodes(path)
        except Exception as exc:  # noqa: BLE001
            return {"status": "failed", "error": f"Could not load electrodes: {exc}"}
        table = self._electrode_table_for(path, x, z, y if three_d else None)
        if three_d:
            how += "; they cover an area, a 3-D survey"
        if self._ert_data is None or self._data_path is None:
            self._x = [float(v) for v in x]
            self._y = [float(v) for v in y]
            self._z = [float(v) for v in z]
            self._survey_3d = bool(three_d)
            self._sync_survey_dimension()
            self._labels = [str(i + 1) for i in range(len(self._x))]
            self._electrode_origins = [None] * len(self._x)
            self._electrode_table = table
            self._electrode_path = Path(path)
            self._refresh()
            self.log(f"Loaded {len(self._x)} electrodes from {name} ({how}); data "
                     "loaded from now on are placed on them.", "success")
            return {"status": "ok", "electrodes": len(self._x), "columns": how}
        if table is None:
            return {"status": "failed",
                    "error": f"{name} could not be staged for the reader."}
        data_name = self._data_path.name
        previous = (self._electrode_table, self._electrode_path)
        refilter = self._qc_applied is not None
        kept_before = self._n_meas
        self._electrode_table, self._electrode_path = table, Path(path)
        self.log(f"Reading {data_name} again with the electrode positions from "
                 f"{name} ({how})…", "info")

        def settle(outcome: str, value: Any) -> Dict[str, Any]:
            if outcome == "loaded":
                refiltered = ""
                if refilter:
                    # The thresholds already applied. Apparent resistivity moves
                    # with the electrodes, so the same ρa limits can keep a
                    # different share of the readings; both counts are given.
                    self._apply_filter()
                    total = int(self._ert_data_full.size()) if self._ert_data_full is not None else 0
                    refiltered = (f"; the QC filter applied again keeps {self._n_meas} of "
                                  f"{total} readings ({kept_before} on the previous positions)")
                self.log(f"{data_name}: electrodes placed from {name}{refiltered}.",
                         "success")
                return {"status": "ok", "electrodes": len(self._x), "columns": how,
                        "measurements": self._n_meas}
            if outcome == "superseded":
                # A newer load took over, and it read with this file.
                return {"status": "failed", "error": "superseded by another load"}
            error = self._name_electrode_file(str(value))
            self._electrode_table, self._electrode_path = previous
            self._refresh()                    # the data on screen are the earlier read
            self.log(f"{name} was not applied; {data_name} stays as it was read "
                     "before.", "warn")
            return {"status": "failed", "error": error}

        if wait:
            return settle(*self._load_and_wait(str(self._data_path)))
        self._start_load(str(self._data_path), settle)
        return {"status": "pending"}

    def _load_electrodes(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, QCoreApplication.translate("PHGX", "Load electrode file"), "", _ELEC_FILTER)
        if not path:
            return
        outcome = self._take_electrode_file(path)
        if outcome["status"] == "failed":
            self.log(outcome["error"], "error")

    # -- pseudosection -------------------------------------------------------
    def _paint_pseudo_scale(self) -> None:
        """Draw the legend's colour bar in the pseudosection's colour map."""
        stops = []
        fractions = np.linspace(0.0, 1.0, 9)
        colours = self._cmap.map(fractions, mode="byte")
        for fraction, colour in zip(fractions, colours):
            stops.append(
                f"stop:{fraction:.3f} rgb({int(colour[0])},"
                f"{int(colour[1])},{int(colour[2])})"
            )
        self._pseudo_scale_bar.setStyleSheet(
            "QFrame { border: 1px solid #8b949e; border-radius: 2px; "
            "background: qlineargradient(x1:0, y1:0, x2:1, y2:0, "
            + ", ".join(stops)
            + "); }"
        )

    def _on_pseudo_colormap_changed(self, name: str) -> None:
        """Recolour the pseudosection from the measurements already loaded."""
        self._cmap = cmaps.to_pyqtgraph(name)
        self._paint_pseudo_scale()
        if self._pseudo:
            self._draw_pseudosection()

    def _electrode_summary(self) -> str:
        """The electrode line in words: how many, how far apart, how long, how high.

        In the studio's length unit. A line read without elevations puts every
        electrode at z = 0, and an elevation range then would present a made-up
        datum as a measured one, so it is said only for elevations read.
        """
        count = len(self._x)
        if not count:
            return "No electrodes"
        unit = length_units.current()
        factor = length_factor(unit)
        x = np.asarray(self._x, dtype=float)
        z = np.asarray(self._z, dtype=float)
        parts = [f"{count} electrode{'s' if count != 1 else ''}"]
        if self._survey_3d:
            from scipy.spatial import cKDTree

            plan = np.column_stack([x, np.asarray(self._y, dtype=float)])
            plan = np.unique(plan[np.isfinite(plan).all(axis=1)], axis=0)
            if len(plan) > 1:
                near = cKDTree(plan).query(plan, k=2)[0][:, 1]
                width, length = np.ptp(plan, axis=0) * factor
                parts.append(f"over {width:.4g} × {length:.4g} {unit}")
                parts.append(f"{np.median(near) * factor:.3g} {unit} apart")
            if np.any(np.abs(z[np.isfinite(z)]) > 1.0e-6):
                parts.append(f"elevation {np.nanmin(z) * factor:.4g} to "
                             f"{np.nanmax(z) * factor:.4g} {unit}")
            return ", ".join(parts)
        gaps = np.diff(np.unique(x[np.isfinite(x)]))
        gaps = gaps[gaps > 1.0e-9]
        if gaps.size:
            parts.append(f"{np.median(gaps) * factor:.3g} {unit} apart")
            parts.append(f"along {(gaps.sum()) * factor:.4g} {unit}")
        if np.any(np.abs(z[np.isfinite(z)]) > 1.0e-6):
            parts.append(f"elevation {np.nanmin(z) * factor:.4g} to "
                         f"{np.nanmax(z) * factor:.4g} {unit}")
        return ", ".join(parts)

    def _on_length_unit_changed(self, _unit: str) -> None:
        """Say the electrode line and redraw the pseudosection in the new unit."""
        self._update_info()
        self._draw_pseudosection()

    def _show_pseudosection_message(self, message: str) -> None:
        """Show a stable empty-state message on the static section canvas."""
        self._pseudo_ax.clear()
        self._pseudo_ax.set_axis_off()
        if message:
            self._pseudo_ax.text(
                0.5, 0.5, message, wrap=True,
                ha="center", va="center", transform=self._pseudo_ax.transAxes,
            )
        self._pseudo_legend.setVisible(False)
        self._pseudo_canvas.draw_idle()
        self._pseudo_toolbar.update()   # Home and Back belong to the new plot

    def _pseudosection_problem(self) -> str:
        """What the Data tab says when the file loaded gives no section to draw.

        In words a user can act on, rather than a list of numeric conditions.
        """
        name = self._data_path.name if self._data_path is not None else ""
        if name and self._data_note:
            return (f"{name} could not be read as {self._instrument.currentText()}.\n"
                    f"{self._data_note}\n"
                    "Choose the instrument / format the file was written by, on the right.")
        if name:
            return (f"No usable apparent resistivity was read from {name}.\n"
                    "Check the instrument / format setting on the right.")
        return _EMPTY_DATA_MESSAGE

    def _draw_electrode_marks(self, x: np.ndarray) -> None:
        """The electrodes as small triangles along the top of the section."""
        x = x[np.isfinite(x)]
        if x.size:
            self._pseudo_ax.scatter(
                x, np.zeros_like(x), marker="v", s=24, color=_ELECTRODE_MARK,
                linewidths=0, clip_on=False, zorder=5)

    def _draw_plan_view(self) -> None:
        """A 3-D survey in plan, as the pseudosection draws a profile.

        Each reading sits at the middle of its electrodes, coloured by its
        apparent resistivity; readings that share a middle are one dot, their
        median. The electrodes are drawn over them.
        """
        ax = self._pseudo_ax
        ax.clear()
        ax.set_axis_on()
        ex, ey = np.asarray(self._x, dtype=float), np.asarray(self._y, dtype=float)
        data = self._ert_data
        title = f"{self._electrode_summary()}. Add data files to see the readings."
        self._pseudo_legend.setVisible(False)
        if data is not None and int(data.size()) and data.haveData("rhoa"):
            index = np.column_stack([np.asarray(data[t], dtype=int) for t in "abmn"])
            sensors = np.asarray(data.sensorPositions(), dtype=float)[:, :2]
            used = index >= 0
            spots = np.where(used[..., None], sensors[np.maximum(index, 0)], 0.0)
            middle = spots.sum(axis=1) / np.maximum(used.sum(axis=1), 1)[:, None]
            rhoa = np.asarray(data["rhoa"], dtype=float)
            valid = np.isfinite(rhoa) & (rhoa > 0) & np.isfinite(middle).all(axis=1)
            if valid.any():
                keys, inverse = np.unique(np.round(middle[valid], 3), axis=0,
                                          return_inverse=True)
                inverse = np.asarray(inverse).reshape(-1)
                logs = np.log10(rhoa[valid])
                median = np.array([np.median(logs[inverse == k]) for k in range(len(keys))])
                lo, hi = np.percentile(logs, [3, 97])
                if hi <= lo:
                    lo, hi = float(lo) - 0.5, float(hi) + 0.5
                low, high = self._pseudo_range.limits(10.0 ** float(lo), 10.0 ** float(hi))
                lo, hi = np.log10(low), np.log10(high)
                lut = self._cmap.map(np.clip((median - lo) / (hi - lo), 0.0, 1.0), mode="byte")
                rgba = np.ones((len(lut), 4), dtype=float)
                rgba[:, :3] = np.asarray(lut[:, :3], dtype=float) / 255.0
                ax.scatter(keys[:, 0], keys[:, 1], s=34, c=rgba, marker="o",
                           edgecolors="#394b59", linewidths=0.35)
                for label, value in zip(self._pseudo_scale_labels,
                                        np.power(10.0, np.linspace(lo, hi, 5))):
                    label.setText(f"{float(value):.4g}")
                self._pseudo_legend.setVisible(True)
                kept = rhoa[valid]
                title = (f"{kept.size:,} readings at {len(keys):,} midpoints (plan), "
                         f"{kept.min():.3g}–{kept.max():.3g} Ω·m   ▲ electrodes")
        finite = np.isfinite(ex) & np.isfinite(ey)
        ax.scatter(ex[finite], ey[finite], marker="^", s=26, color=_ELECTRODE_MARK,
                   linewidths=0, zorder=5)
        ax.set_aspect("equal", adjustable="datalim")
        set_length_axis(ax, "x", "x")
        set_length_axis(ax, "y", "y")
        ax.grid(True, which="major", alpha=0.28)
        ax.set_title(i18n.tr(title))
        self._pseudo_canvas.draw_idle()
        self._pseudo_toolbar.update()

    def _draw_electrodes_only(self) -> None:
        """Electrodes and no data yet - an electrode file read before the data."""
        if self._survey_3d:
            self._draw_plan_view()
            return
        x = np.asarray(self._x, dtype=float)
        x = x[np.isfinite(x)]
        ax = self._pseudo_ax
        ax.clear()
        ax.set_axis_on()
        self._draw_electrode_marks(x)
        pad = 0.03 * max(float(np.ptp(x)) if x.size else 0.0, 1.0)
        ax.set_xlim(float(x.min()) - pad, float(x.max()) + pad)
        ax.set_ylim(1.0, 0.0)
        ax.set_yticks([])
        set_length_axis(ax, "x", "x")
        ax.set_title(QCoreApplication.translate("PHGX", "{0}. Add data files to see the pseudosection.").format(self._electrode_summary()))
        self._pseudo_legend.setVisible(False)
        self._pseudo_canvas.draw_idle()
        self._pseudo_toolbar.update()

    def _draw_pseudosection(self) -> None:
        if self._survey_3d and self._x and not self._data_note:
            self._draw_plan_view()
            return
        if not self._pseudo:
            if self._x and not self._data_note:
                self._draw_electrodes_only()
            else:
                self._show_pseudosection_message(self._pseudosection_problem())
            return
        arr = np.asarray(self._pseudo, dtype=float)
        if arr.ndim != 2 or arr.shape[1] < 3:
            self._show_pseudosection_message(self._pseudosection_problem())
            return
        mid, depth, rhoa = arr[:, 0], arr[:, 1], arr[:, 2]
        valid = (
            np.isfinite(mid)
            & np.isfinite(depth)
            & (depth >= 0.0)
            & np.isfinite(rhoa)
            & (rhoa > 0.0)
        )
        mid, depth, rhoa = mid[valid], depth[valid], rhoa[valid]
        if rhoa.size == 0:
            self._show_pseudosection_message(self._pseudosection_problem())
            return
        log_rhoa = np.log10(rhoa)
        lo, hi = np.percentile(log_rhoa, [3, 97])
        if hi <= lo:
            lo, hi = float(lo) - 0.5, float(hi) + 0.5
        # The limits typed in while "Lock range" is ticked, or these, which
        # the boxes then show; in Ω·m, the scale itself is logarithmic.
        low, high = self._pseudo_range.limits(10.0 ** float(lo), 10.0 ** float(hi))
        lo, hi = np.log10(low), np.log10(high)
        rng = hi - lo
        norm = np.clip((log_rhoa - lo) / rng, 0.0, 1.0)
        lut = self._cmap.map(norm, mode="byte")
        # The section spans the electrodes, which reach past the outermost
        # measurement midpoints.
        electrodes = np.asarray(self._x, dtype=float)
        electrodes = electrodes[np.isfinite(electrodes)]
        x_all = np.concatenate([mid, electrodes])
        x_min, x_max = float(np.min(x_all)), float(np.max(x_all))
        x_span = x_max - x_min
        if x_span <= 1e-9:
            x_center = 0.5 * (x_min + x_max)
            x_min, x_max = x_center - 0.5, x_center + 0.5
        else:
            x_pad = 0.03 * x_span
            x_min, x_max = x_min - x_pad, x_max + x_pad
        depth_max = max(float(np.max(depth)) * 1.08, 0.02)

        self._pseudo_ax.clear()
        self._pseudo_ax.set_axis_on()
        rgba = np.ones((len(lut), 4), dtype=float)
        rgba[:, :3] = np.asarray(lut[:, :3], dtype=float) / 255.0
        self._pseudo_ax.scatter(
            mid,
            depth,
            s=34,
            c=rgba,
            marker="o",
            edgecolors="#394b59",
            linewidths=0.35,
        )
        self._draw_electrode_marks(electrodes)
        self._pseudo_ax.set_xlim(x_min, x_max)
        self._pseudo_ax.set_ylim(depth_max, 0.0)
        # The y values are already depths below the surface, so only the unit
        # changes; the inverted axis keeps them positive down.
        set_length_axis(self._pseudo_ax, "x", "x")
        set_length_axis(self._pseudo_ax, "y", "Pseudo-depth")
        self._pseudo_ax.grid(True, which="major", alpha=0.28)
        self._pseudo_ax.minorticks_on()
        self._pseudo_ax.grid(True, which="minor", alpha=0.10)
        self._pseudo_ax.set_title(
            # Short enough for a narrow plot; the scale below names the quantity.
            QCoreApplication.translate("PHGX", "{0:,} readings, {1:.3g}–{2:.3g} Ω·m   ▼ electrodes").format(rhoa.size, rhoa.min(), rhoa.max())
        )
        self._pseudo_canvas.draw_idle()
        self._pseudo_toolbar.update()
        legend_values = np.power(10.0, np.linspace(float(lo), float(hi), 5))
        for label, value in zip(self._pseudo_scale_labels, legend_values):
            label.setText(f"{float(value):.4g}")
        self._pseudo_legend.setVisible(True)
