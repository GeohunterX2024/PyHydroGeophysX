"""The ERT page: loading data and electrodes (plan M4.5).

Part of :class:`~.page.ERTProcessingModule`, split from the former
``ert_processing.py`` by area; the methods are unchanged.
"""

from __future__ import annotations

from .common import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Path,
    QCoreApplication,
    QEventLoop,
    TaskWorker,
    Tuple,
    _QC_DEFAULTS,
    _logger,
    contextlib,
    ert_load,
    i18n,
    np,
    theme,
)


class _ImportPanel:

    # -- loading -------------------------------------------------------------
    def _start_load(self, path: str,
                    done: Optional[Callable[[str, Any], None]] = None) -> None:
        """Load one ERT file (off the UI thread) into the electrode + pseudosection
        view and make it the current single-inversion dataset. Used when a file is
        added and when a row in the file list is clicked to preview it.

        ``done(outcome, value)`` is told how this load ended, once the page has
        been updated: ``("loaded", result)``, ``("failed", message)``, or
        ``("superseded", None)`` when a newer load replaced it first. It is
        connected before the worker starts, so a fast parse cannot be missed.

        A forward file paired with its reciprocal file in the list is loaded
        with it, the two merged into one survey."""
        instrument = self._instrument.currentData()
        # Capture widget/state values on the UI thread; the parse runs off-thread.
        out_dir = self.state.ensure_results_store().scratch_dir(self.module_key)
        elec_file = self._electrode_file()
        spacing = None  # geometry comes from the file; instrument loaders handle layout
        reciprocal = self._tl_partner.get(str(path))
        self._info.setText(f"Loading {Path(path).name}"
                           + (" with its reciprocal file" if reciprocal else "") + "…")
        worker = TaskWorker(self._parse_ert, path, instrument, out_dir, elec_file, spacing,
                            reciprocal)
        # Only the latest request may land. Each click starts a load without
        # waiting for the one before, and a slow earlier file finishing last
        # would replace the data under a list highlighting the newer one - so
        # the next inversion would run on a survey nobody selected.
        def landed(res, w=worker):
            if w is not self._load_worker:
                if done is not None:
                    done("superseded", None)
                return
            res.setdefault("instrument", instrument)   # the format it was read as
            if done is None:
                self._on_ert_loaded(path, res)
                return
            try:
                self._on_ert_loaded(path, res)
            except Exception as exc:  # noqa: BLE001 - the caller reports it
                done("failed", str(exc))
            else:
                done("loaded", res)

        def refused(message, w=worker):
            if w is self._load_worker:
                self._on_ert_load_failed(message, path)
                if done is not None:
                    done("failed", message)
            elif done is not None:
                done("superseded", None)

        worker.succeeded.connect(landed)
        worker.failed.connect(refused)
        if done is not None:
            # A cancelled load emits no result at all, only ``finished``.
            worker.finished.connect(lambda: done("superseded", None))
        self._supersede_load()
        self._load_worker = self.register_worker(worker, activity="Reading the data file")
        worker.start()

    def _load_and_wait(self, path: str) -> Tuple[str, Any]:
        """Load ``path`` through :meth:`_start_load` and wait for it to land.

        For callers that need the outcome before they can answer - the
        assistant's ``load_data``, which reports the loaded counts. They run on
        the UI thread, and parsing there would freeze the studio for the length
        of the read; the parse runs on the worker while a local event loop keeps
        the window painting and responding until this load has settled.

        Returns
        -------
        tuple
            ``(outcome, value)`` as :meth:`_start_load` reports them.
        """
        settled: Dict[str, Any] = {}
        loop = QEventLoop()

        def done(outcome: str, value: Any) -> None:
            if not settled:        # the first report wins; ``finished`` follows it
                settled.update(outcome=outcome, value=value)
                loop.quit()

        self._start_load(path, done)
        if not settled:
            loop.exec()
        return settled["outcome"], settled["value"]

    def _supersede_load(self) -> None:
        """Drop a load still in flight: a newer request replaces it."""
        previous, self._load_worker = self._load_worker, None
        if previous is not None and previous.isRunning():
            previous.cancel()

    def _electrode_file(self) -> Optional[str]:
        """The electrode table the instrument readers are handed, if any."""
        table = self._electrode_table
        return str(table) if table is not None and table.exists() else None

    def _run_label(self, files, unit: str = "files") -> str:
        """The name a new run is listed under in Saved Results.

        Drawn from its data - the file, or the name a sequence shares and how
        many surveys - with the engine added when it is not the in-house one,
        so runs of different surveys are told apart in the list.
        """
        from PyHydroGeophysX.qt_apps.results_store import run_label_from_files

        label = run_label_from_files(files, unit=unit)
        if label and str(self._engine.currentData() or "pyhydro") != "pyhydro":
            label += " · " + self._engine.currentText().split(" ")[0]
        return label

    @staticmethod
    def _resipy_version() -> str:
        """Whether ResIPy is available, and its version where it reports one.

        Returns ``""`` when it is not installed. The installed distribution's
        metadata comes first: importing ResIPy checks the SHA1 of each of its
        executables, which holds up the UI thread as this page opens, and the
        loader imports it anyway, on its worker thread,
        when it reads a file. Without metadata the module is imported and asked:
        it carries its version as ``ResIPy_version`` rather than the usual
        ``__version__``, older builds carry neither, and a bare "yes" is the
        last resort.
        """
        import importlib.util
        import sys
        from importlib.metadata import version

        resipy = sys.modules.get("resipy")
        if resipy is None:
            try:
                if importlib.util.find_spec("resipy") is None:
                    return ""
                return str(version("resipy"))
            except Exception:  # noqa: BLE001 - no metadata; ask the module
                _logger.debug("ERTProcessingModule._resipy_version: no metadata; ask the module", exc_info=True)
            try:
                import resipy
            except Exception:  # noqa: BLE001 - an optional reader
                _logger.debug("ERTProcessingModule._resipy_version: an optional reader", exc_info=True)
                return ""
        for attribute in ("ResIPy_version", "__version__"):
            found = getattr(resipy, attribute, None)
            if found:
                return str(found)
        try:
            return str(version("resipy"))
        except Exception:  # noqa: BLE001
            _logger.debug("ERTProcessingModule._resipy_version: ignored error", exc_info=True)
            return "yes"

    def _show_reader_status(self, reader: str = "", detail: str = "") -> None:
        """One line naming the reader available, or the one that read the file.

        ``reader`` is empty before a file is loaded, when the line reports only
        what is installed.
        """
        version = self._resipy_version()
        named = "ResIPy" if version == "yes" else f"ResIPy {version}"
        self._resipy_ready.setText(QCoreApplication.translate("PHGX", "ResIPy ready") if version else QCoreApplication.translate("PHGX", "ResIPy unavailable"))
        theme.set_tone(self._resipy_ready, "ok" if version else "warn")
        self._resipy_ready.setToolTip(
            QCoreApplication.translate("PHGX", "{0} available for loading data.").format(named) if version else
            QCoreApplication.translate("PHGX", "ResIPy is not installed; some formats require it. See Data format."))
        if not reader:
            if version:
                self._reader_status.setText(QCoreApplication.translate("PHGX", "{0} available for loading data.").format(named))
                self._instrument.setToolTip(self._reader_status.text())
                self._reader_status.hide()
                return
            from PyHydroGeophysX.data_processing.ert_data_agent import (
                _EMBEDDED_PARSER_MAP, resipy_install_hint,
            )
            self._reader_status.setText(QCoreApplication.translate("PHGX", "ResIPy unavailable; some formats need it."))
            details = ("Available readers: " + ", ".join(sorted(_EMBEDDED_PARSER_MAP))
                       + ".\n\n" + resipy_install_hint())
            self._reader_status.setToolTip(i18n.tr(details))
            self._instrument.setToolTip(i18n.tr(details))
            self._reader_status.show()
            return
        note = f", {detail}" if detail else ""
        self._reader_status.setText(QCoreApplication.translate("PHGX", "Data loaded by {0}{1}.").format(reader, note))
        self._reader_status.setToolTip("")
        self._reader_status.show()

    def _parse_ert(self, path, instrument, out_dir, elec_file, spacing, reciprocal=None):
        """Parse ERT data off the UI thread. Returns a plain dict for the slot.

        With ``reciprocal``, that file is read the same way and its readings
        appended to ``path``'s (``ert_io.merge_reciprocal``): one survey, on
        the forward file's electrodes, whose readings pair across the two files.
        ``res["pair"]`` then holds the counts of each and of the pairs, and
        ``res["pairing"]`` is the survey's reciprocal pairing either way, for
        the Reciprocal errors tab and the error model.
        """
        from PyHydroGeophysX.qt_apps.ert_records import reciprocal_pairing

        res = self._parse_one(path, instrument, out_dir, elec_file, spacing)
        if not reciprocal:
            res["pairing"] = (reciprocal_pairing(self._reciprocal_scores(res["data"]))
                              if res["data"] is not None else None)
            return res
        if res["data"] is None:
            res["warning"] = "; ".join(filter(None, [res["warning"], (
                f"{Path(path).name} could not be converted for inversion, so its "
                f"reciprocal file {Path(reciprocal).name} was not merged with it.")]))
            return res
        other = self._parse_one(reciprocal, instrument, out_dir, elec_file, spacing)
        if other["data"] is None:
            raise ValueError(
                f"the reciprocal file {Path(reciprocal).name} could not be converted for "
                f"inversion ({other['data_note'] or 'no usable readings'}), so it cannot be "
                f"merged with {Path(path).name}. Untick “Pair reciprocal files” to load "
                "each file on its own.")
        try:
            merged, info = ert_load.merge_reciprocal(res["data"], other["data"])
        except ValueError as exc:
            raise ValueError(
                f"{Path(path).name} and its reciprocal file {Path(reciprocal).name} could "
                f"not be merged: {exc} Untick “Pair reciprocal files” to load each file on "
                "its own.") from exc
        pairing = reciprocal_pairing(self._reciprocal_scores(merged))
        info.update(file=str(reciprocal), pairs=int(pairing.get("pairs", 0) or 0),
                    unpaired=int(pairing.get("unpaired_readings", 0) or 0))
        res.update(data=merged, nmeas=int(merged.size()), pair=info, pairing=pairing,
                   pseudo=self._pseudo_from_data(merged),
                   warning="; ".join(filter(None, [res["warning"], other["warning"]])))
        return res

    def _parse_one(self, path, instrument, out_dir, elec_file, spacing):
        """Parse one ERT file; see :meth:`_parse_ert`."""
        warning = ""
        reader, reason = "ResIPy", ""
        read_as = instrument
        # An electrode file covering an area makes a 3-D survey whatever the
        # data file's own header says; without one the electrodes decide.
        file_3d = None
        if elec_file:
            with contextlib.suppress(Exception):  # the reader reports a bad file
                file_3d = ert_load.read_electrode_layout(elec_file)[1]
        if instrument is None:  # defensive: the dropdown has no auto/None option
            elec, pseudo, nmeas, data, note, three_d = self._load_pygimli(
                path, elec_file, file_3d)
            reader = "PyGIMLi"
        else:
            try:
                (elec, pseudo, nmeas, data, note, (reader, reason), read_as,
                 three_d) = self._load_resipy(path, instrument, out_dir, elec_file, spacing,
                                              file_3d)
            except NotImplementedError:
                # No reader for this format. PyGIMLi's reader would accept the
                # file and return a quadrupole table built from the wrong
                # columns, so this has to stop here and say what is missing
                # rather than hand back a section nobody can trust.
                raise
            except Exception as exc:  # noqa: BLE001
                # PyGIMLi's reader answers for the unified family only; outside
                # it the chosen reader's refusal is the answer. Retried natively,
                # a DAS-1 file missing its data section would load as one reading
                # and the reader's own explanation would be lost. Same rule, and message,
                # as ert_io.load_ert_container, so a file fails the same way
                # here as in a time-lapse run.
                if ert_load._canonical_instrument(str(instrument)) not in ert_load._NATIVE_RETRY:
                    raise ValueError(
                        f"'{Path(path).name}' could not be read as {instrument}: {exc}"
                    ) from exc
                warning = f"{instrument} loader failed ({exc}); fell back to pygimli's native reader."
                elec, pseudo, nmeas, data, note, three_d = self._load_pygimli(
                    path, elec_file, file_3d)
                reader, reason = "PyGIMLi", "ResIPy could not parse this file"
        return {"elec": elec, "pseudo": pseudo, "nmeas": nmeas, "data": data,
                "warning": warning, "reader": reader, "reader_reason": reason,
                "data_note": note, "instrument": read_as or instrument,
                "survey_3d": bool(three_d)}

    def _on_ert_loaded(self, path: str, res: dict) -> None:
        if res.get("warning"):
            self.log(res["warning"], "warn")
        self._show_reader_status(str(res.get("reader", "")),
                                 str(res.get("reader_reason", "")))
        elec, pseudo, nmeas, data = res["elec"], res["pseudo"], res["nmeas"], res["data"]
        self._loaded_format = res.get("instrument")
        # The loader reads a file whose header names its format as that format
        # (a PRIME .tab picked as BERT), so the chooser moves to it rather than
        # naming a reader that never saw the file. Set in code, so the reload
        # on a hand-picked format does not run.
        read_as = self._instrument.findData(self._loaded_format) if self._loaded_format else -1
        if read_as >= 0 and read_as != self._instrument.currentIndex():
            self.log(f"{Path(path).name} names its own format, so it was read as "
                     f"{self._instrument.itemText(read_as)}.", "info")
            self._instrument.setCurrentIndex(read_as)
        # A file read under the wrong format can come back "loaded": a DAS-1
        # file read as BERT gives one electrode and one reading, and the
        # inversion would fail on it a minute later. A survey no instrument
        # could have measured is refused here instead.
        from PyHydroGeophysX.data_processing.ert_formats import implausible_survey
        implausible = implausible_survey(len(elec), int(nmeas or 0))
        if implausible:
            data, pseudo = None, []
        self._x = [float(e[0]) for e in elec]
        self._z = [float(e[1]) for e in elec]
        self._y = [float(e[2]) if len(e) > 2 else 0.0 for e in elec]
        was_3d, self._survey_3d = self._survey_3d, bool(res.get("survey_3d"))
        self._labels = [str(i + 1) for i in range(len(self._x))]
        self._electrode_origins = list(range(len(self._x)))
        self._data_path = Path(path)
        pair = res.get("pair")
        self._pair_info = dict(pair) if pair else None
        self._data_partner = Path(pair["file"]) if pair else None
        self._pseudo = pseudo
        self._n_meas = nmeas
        self._ert_data = data
        self._ert_data_full = data
        # A file can parse into electrodes and readings and still not convert
        # into a pygimli container — no pygimli, or quadrupoles that cite
        # electrodes the file never defines. The pseudosection is still drawn
        # from the raw values, so say here what has been lost rather than
        # leaving the module looking loaded until an inversion asks for it.
        self._qc_mask = [True] * int(data.size()) if data is not None else []
        self._reset_manual_qc()
        self._qc_report = None       # these data are unfiltered until Apply filter
        self._loaded_pairing = res.get("pairing")
        self._data_note = ""
        # Whether the file's first lines name another format; offered beside
        # the format chooser either way, loaded or not.
        self._show_format_hint(path)
        if implausible:
            self._data_note = implausible
            suggestion = (f" It looks like a {self._format_guess[2]} file: press “Read as "
                          f"{self._format_guess[2]}” under the format."
                          if self._format_guess else
                          " Choose the instrument / format the file was written by.")
            self.log(f"Could not read {Path(path).name} as "
                     f"{self._instrument.currentText()}: {implausible}{suggestion}", "error")
        elif data is None:
            cause = str(res.get("data_note") or
                        "this file could not be converted for inversion.")
            self._data_note = cause  # _refresh puts it on the panel as well
            self.log(
                f"{Path(path).name}: {cause} The pseudosection below is drawn "
                "from the raw values, but QC filtering and inversion are "
                "unavailable for it.", "warn")
        # Which extra criteria this file can support is a property of the file,
        # so it is settled here rather than being rechecked on every Apply.
        self._refresh_qc_availability()
        if data is not None and hasattr(self.state, "register_geophysical_resource"):
            self.state.register_geophysical_resource(
                "ERT", "observed_data", data,
                label=f"ERT observations · {Path(path).name}", path=str(path),
                metadata={"measurements": int(nmeas), "electrodes": len(self._x),
                          **({"reciprocal_file": self._data_partner.name}
                             if self._data_partner else {})},
                resource_id="ert:observed_data:active",
            )
        self._refresh()
        self._recip_inputs_changed()
        # The Reciprocal errors tab stays up when it is the one being looked at:
        # clicking through the list compares the surveys' pairs there.
        if pseudo and self._tabs.currentWidget() is not self._recip_view:
            self._tabs.setCurrentWidget(self._pseudo_widget)
        if data is None:
            pass  # already reported above, naming the specific cause
        elif nmeas == 0:
            self.log(f"{Path(path).name}: parsed {len(self._x)} electrodes but 0 measurements — "
                     f"the Instrument / format is probably wrong for this file.", "warn")
        elif pair:
            # The pairing summary: both files, the readings of each, and how
            # many quadrupoles were measured both ways.
            self.log(f"Loaded {len(self._x)} electrodes, {nmeas} measurements from "
                     f"{Path(path).name} with its reciprocal file {Path(pair['file']).name}: "
                     f"forward {pair['forward']} | reciprocal {pair['reciprocal']} | total "
                     f"{pair['total']}; {pair['pairs']} quadrupoles measured both ways, "
                     f"{pair['unpaired']} readings without a reciprocal.", "success")
            if pair.get("dropped_fields"):
                self.log("Only one of the two files carries "
                         + ", ".join(pair["dropped_fields"])
                         + ", so the merged survey leaves it out.", "warn")
        else:
            self.log(f"Loaded {len(self._x)} electrodes, {nmeas} measurements from {Path(path).name}", "success")
        if self._survey_3d and not was_3d:
            self.log("The electrodes cover an area, so this is a 3-D survey: the Data "
                     "tab shows it in plan, and it is inverted on a 3-D mesh.", "info")
        self._sync_survey_dimension()

    def _name_electrode_file(self, message: str) -> str:
        """``message`` with the readers' copy of the electrode file named as the user's.

        The readers are handed a plain copy (:meth:`_electrode_table_for`), so
        their refusal would name a scratch file the user has never seen.
        """
        table, source = self._electrode_table, self._electrode_path
        if table is not None and source is not None:
            return str(message).replace(Path(table).name, source.name)
        return str(message)

    def _on_ert_load_failed(self, message: str, path: Optional[str] = None) -> None:
        message = self._name_electrode_file(message)
        self.log(f"Could not load ERT data: {message}", "error")
        self._info.setText(QCoreApplication.translate("PHGX", "Load failed: {0}").format(message))
        # Neither reader got there, so the line goes back to what is installed
        # rather than keeping the last file's answer.
        self._show_reader_status()
        # A refusal is most often the wrong format; offer the one the file names.
        self._show_format_hint(path)

    def _show_format_hint(self, path: Optional[Any]) -> None:
        """Offer the format ``path``'s first lines name, when it is not the one chosen."""
        from PyHydroGeophysX.data_processing.ert_formats import guess_ert_format

        guess = guess_ert_format(path) if path else None
        index = self._instrument.findData(guess) if guess else -1
        if index < 0 or index == self._instrument.currentIndex():
            self._format_guess = None
            self._format_hint.setVisible(False)
            return
        name = self._instrument.itemText(index)
        self._format_guess = (str(guess), str(path), name)
        self._format_hint_text.setText(
            QCoreApplication.translate("PHGX", "{0} looks like a {1} file, but is read as {2}.").format(Path(str(path)).name, name, self._instrument.currentText()))
        self._format_hint_btn.setText(QCoreApplication.translate("PHGX", "Read as {0}").format(name))
        self._format_hint.setVisible(True)

    def _take_format_hint(self) -> None:
        """Switch to the format the file looks like, and read it again with it."""
        if self._format_guess is None:
            return
        guess, path, _name = self._format_guess
        index = self._instrument.findData(guess)
        if index < 0:
            return
        self._instrument.setCurrentIndex(index)
        self._format_guess = None
        self._format_hint.setVisible(False)
        self.log(f"Reading {Path(path).name} again as {self._instrument.currentText()}.",
                 "info")
        self._start_load(path)

    def _reload_with_format(self, _index: int = -1) -> None:
        """Read the survey on screen again in the format just chosen by hand."""
        path = self._data_path
        if (path is None or not Path(path).exists()
                or self._instrument.currentData() == getattr(self, "_loaded_format", None)):
            return
        self._format_guess = None
        self._format_hint.setVisible(False)
        self.log(f"Reading {Path(path).name} again as {self._instrument.currentText()}.",
                 "info")
        self._start_load(str(path))

    def _load_pygimli(self, path: str, electrode_file: Optional[str] = None,
                      three_d: Optional[bool] = None):
        import pygimli.physics.ert as ert

        with ert_load.no_invalid_data_file():
            data = ert.load(path, verbose=False)
        if not data.haveData("rhoa"):
            try:
                data["k"] = ert.createGeometricFactors(data, numerical=False)
                if data.haveData("r"):
                    data["rhoa"] = data["r"] * data["k"]
                elif data.haveData("u") and data.haveData("i"):
                    data["rhoa"] = data["u"] / data["i"] * data["k"]
            except Exception:  # noqa: BLE001
                _logger.debug("ERTProcessingModule._load_pygimli: ignored error", exc_info=True)
        # PyGIMLi's reader takes no electrode file, so it is applied here - or
        # refused, as the instrument readers refuse one that does not fit.
        if electrode_file:
            ert_load.place_electrodes(data, electrode_file)
        pos = np.asarray(data.sensors(), dtype=float)
        x = pos[:, 0]
        if three_d is None:
            three_d = ert_load.survey_is_3d(pos)
        y = pos[:, 1] if three_d else np.zeros_like(x)
        if three_d or (pos.shape[1] >= 3 and np.std(pos[:, 2]) > 1e-9):
            z = pos[:, 2]
        elif pos.shape[1] >= 2:
            z = pos[:, 1]
        else:
            z = np.zeros_like(x)
        a = np.asarray(data["a"], dtype=int)
        b = np.asarray(data["b"], dtype=int)
        m = np.asarray(data["m"], dtype=int)
        nn = np.asarray(data["n"], dtype=int)
        rhoa = np.asarray(data["rhoa"], dtype=float) if data.haveData("rhoa") else np.full(data.size(), np.nan)
        elec = [(float(x[i]), float(z[i]), float(y[i])) for i in range(len(x))]
        pseudo = self._build_pseudo_from_indices(x, a, b, m, nn, rhoa)
        return elec, pseudo, int(data.size()), data, "", bool(three_d)

    def _load_resipy(self, path: str, instrument: str, out_dir, electrode_file, spacing,
                     three_d: Optional[bool] = None):
        from PyHydroGeophysX.data_processing.ert_data_agent import load_ert_resipy

        project_dir = str(Path(out_dir) / "resipy_project")
        std = load_ert_resipy(
            project_dir=project_dir, data_file=path, instrument=instrument,
            spacing=spacing, electrode_file=electrode_file,
        )
        electrodes = std.electrodes or []
        positions, three_d = ert_load.electrode_positions(electrodes, three_d)
        # (x, elevation, y): a profile's elevation is its container's y.
        elec = [(float(row[0]), float(row[2] if three_d else row[1]),
                 float(row[1] if three_d else 0.0)) for row in positions]
        data = self._standard_to_pg(std, three_d)
        note = ""
        if data is not None:
            # Use the corrected apparent resistivity (rhoa = R * k) for QC display.
            pseudo = self._pseudo_from_data(data)
        else:
            note = self._container_failure_reason(std)
            # Fallback when pygimli is unavailable: plot raw observation values.
            x_by_id = {int(e.id): float(e.x) for e in electrodes}
            pseudo = []
            for obs in (std.observations or []):
                if obs.app_res is None:
                    continue
                ids = [obs.quad.A, obs.quad.B, obs.quad.M, obs.quad.N]
                xs = [x_by_id.get(int(i), np.nan) for i in ids]
                if np.isfinite(xs).all():
                    span = float(np.max(xs) - np.min(xs))
                    pseudo.append((float(np.mean(xs)),
                                   max(span * ert_load.PSEUDO_DEPTH_FACTOR, 0.01),
                                   float(obs.app_res)))
        # The format the loader read it as: a file whose own header names its
        # format (PRIME, Subsurface Insights) is read as that whatever was chosen.
        read_as = str(getattr(std, "instrument", "") or instrument)
        return (elec, pseudo, len(std.observations or []), data, note,
                self._reader_of(std), read_as, three_d)

    @staticmethod
    def _reader_of(std) -> Tuple[str, str]:
        """``(reader, detail)`` naming what actually read the file.

        The instrument loader falls back to this package's own readers when
        ResIPy is absent or has no reader for the format, so "ResIPy" is not a
        safe assumption. The detail carries what the reader worked out beyond the
        table - above all where the electrode positions came from, since a
        format with no coordinates has to get them from somewhere.
        """
        meta = dict(getattr(std, "metadata", None) or {})
        if meta.get("loader") != "local_parsers_resipy_fallback":
            return "ResIPy", ""
        reader = f"PyHydroGeophysX's {meta.get('parser_used') or meta.get('instrument')} reader"
        notes = dict(meta.get("reader_notes") or {})
        parts = []
        if notes.get("sequence_file"):
            parts.append(f"sequence {notes['sequence_file']}")
        cables = notes.get("cables") or {}
        if cables:
            count = sum(int(size) for size in cables.values())
            parts.append(f"{count} electrodes on {len(cables)} "
                         f"cable{'s' if len(cables) != 1 else ''}")
        if notes.get("geometry_note"):
            parts.append(str(notes["geometry_note"]))
        return reader, "; ".join(parts)

    @staticmethod
    def _container_failure_reason(std) -> str:
        """Why a parsed file did not become a pygimli container.

        Worth distinguishing: a missing pygimli is fixed by an install, whereas
        quadrupoles that cite electrodes the file never defines almost always
        mean the Instrument setting does not match the file — and the reader is
        happy to parse the wrong columns without complaint.
        """
        try:
            import pygimli  # noqa: F401
        except Exception:  # noqa: BLE001
            _logger.debug("ERTProcessingModule._container_failure_reason: ignored error", exc_info=True)
            return ("pygimli is not installed, so the file can be plotted but "
                    "not inverted.")
        observations = list(std.observations or [])
        if not observations:
            return "no measurements were parsed from it."
        with_res = [obs for obs in observations if obs.app_res is not None]
        if not with_res:
            return ("no measurement carries an apparent resistivity, and none "
                    "could be rebuilt from the columns that were read.")
        known = {int(e.id) for e in (std.electrodes or [])}
        keys = ("A", "B", "M", "N")
        matched = [
            obs for obs in with_res
            if all(int(getattr(obs.quad, key)) in known for key in keys)
        ]
        if matched:
            return "the measurements could not be matched to the electrode table."
        if not known:
            return ("it defines no electrodes, so its quadrupoles cannot be "
                    "placed. The Instrument setting is probably wrong for this "
                    "file.")
        cited = sorted({int(getattr(obs.quad, key)) for obs in with_res for key in keys})
        return (f"its measurements cite electrodes {cited[0]}–{cited[-1]}, which "
                f"the electrode table ({min(known)}–{max(known)}) does not "
                "define, so no quadrupole can be placed. The Instrument setting "
                "is probably wrong for this file.")

    # Geometry/topography + StandardERT->pygimli conversion live in the shared
    # ``ert_load`` module so the single-inversion loader and the time-lapse
    # pipeline behave identically. Kept as thin static wrappers for callers here.
    _electrode_elevation = staticmethod(ert_load.electrode_elevation)
    _standard_to_pg = staticmethod(ert_load.standard_to_pg)

    @staticmethod
    def _build_pseudo_from_indices(x, a, b, m, n, rhoa) -> List[Tuple[float, float, float]]:
        # Placed as the workflow's raw-data figure places them (ert_io).
        return [tuple(row) for row in ert_load.pseudosection_points(x, a, b, m, n, rhoa).tolist()]

    def _pseudo_from_data(self, data) -> List[Tuple[float, float, float]]:
        return [tuple(row) for row in ert_load.container_pseudosection(data).tolist()]

    @classmethod
    def _reciprocal_error(cls, data) -> Optional[np.ndarray]:
        """Relative reciprocal error per measurement, NaN where there is no partner.

        See :meth:`_reciprocal_scores`, whose ``reciprocalErrRel`` this is.
        """
        scored = cls._reciprocal_scores(data)
        return None if scored is None else scored["reciprocalErrRel"].to_numpy(dtype=float)

    @staticmethod
    def _reciprocal_scores(data):
        """The survey paired with its reciprocals: a frame of a, b, m, n, resist
        with each reading's ``reciprocalErrRel`` and ``reciprocalMean``.

        A reciprocal swaps the current and potential pairs, (A,B,M,N) -> (M,N,A,B),
        and reciprocity requires the same transfer resistance from both. How far
        apart they land is the only error estimate that comes from the data rather
        than from an assumed percentage, which is why it is worth computing even
        though most files do not carry it as a column.

        The pairing and the score are the library's own
        (``ert_formats.reciprocal_errors``), so this page and a file's reciprocal
        analysis agree: a pair written in reverse order has its resistance
        negated before comparison - without that, (A,B,M,N) and (M,N,B,A) read
        as R against -R, a 200 % disagreement for a perfect pair - and repeats in
        one direction are stacked, not scored as reciprocals of each other.

        Returns None when the file has neither a resistance nor the rhoa and k
        needed to rebuild one. The pairing itself is ``ert_io.reciprocal_scores``,
        which also averages pairs and merges a survey's two files.
        """
        return ert_load.reciprocal_scores(data)

    def _refresh_qc_availability(self) -> None:
        """Enable each folded QC row only where the loaded file can support it.

        Voltage and current arrive with some instrument formats and not others,
        and a reciprocal error needs the survey to actually contain reciprocals.
        A row that cannot work is disabled with the reason in its tooltip, which
        is more useful than a control that silently filters on nothing.
        """
        def gate(widget, ok: bool, message: str) -> None:
            widget.setEnabled(bool(ok))
            label = self.row_label(widget)
            if label is not None:
                label.setEnabled(bool(ok))
            widget.setToolTip(i18n.tr(message))

        data = self._ert_data_full
        self._refresh_error_sources(data)
        if data is None:
            for w in (self._qc_min_v, self._qc_min_i, self._qc_max_k, self._qc_max_rc,
                      self._qc_max_stack, self._qc_max_recip, self._qc_average):
                gate(w, False, "Load ERT data first.")
            self._qc_support_note.setText(
                QCoreApplication.translate("PHGX", "Load data to see which checks are available.")
            )
            return

        # Volts and amperes: ert_io.standard_to_pg keeps these tokens only from a
        # reader that says it gives them in those units, and PyGIMLi's own reader
        # uses them. The defaults assume them; the observed range is quoted too.
        unavailable: List[str] = []
        for widget, token, name, unit, floor in (
                (self._qc_min_v, "u", "voltage", "V", "10 µV, a common noise floor"),
                (self._qc_min_i, "i", "current", "A", "0.1 mA, below which the "
                                                      "injection failed")):
            if data.haveData(token):
                v = np.abs(np.asarray(data[token], dtype=float))
                v = v[np.isfinite(v)]
                span = f"{v.min():.4g} to {v.max():.4g} {unit}" if v.size else "empty"
                gate(widget, True,
                     f"Drop readings whose |{token}| falls below this, in {unit} (0 = off; "
                     f"the default is {floor}). This file's {name} spans {span}.")
            else:
                gate(widget, False,
                     f"This file carries no {name} column, so there is nothing to test.")
                unavailable.append(f"Min |{token.upper()}| (no {name} column)")

        if data.haveData("k"):
            k = np.abs(np.asarray(data["k"], dtype=float))
            k = k[np.isfinite(k)]
            span = f"{k.min():.4g} to {k.max():.4g}" if k.size else "empty"
            multiple = _QC_DEFAULTS["k_over_median"]
            if self._qc_max_k_follows_file and k.size:
                cap = float(f"{multiple * float(np.median(k)):.2g}")
                self._qc_max_k.blockSignals(True)
                self._qc_max_k.setValue(cap)
                self._qc_max_k.blockSignals(False)
            gate(self._qc_max_k, True,
                 "Drop configurations whose geometric factor exceeds this (0 = off). A large "
                 "|k| multiplies the measured resistance and its noise with it, which is how "
                 f"geometry alone produces a rhoa outlier. This file spans {span}; until "
                 f"you set it, the cap is {multiple:g} × its median |k| "
                 f"({float(np.median(k)) if k.size else 0.0:.3g} m), since |k| grows with "
                 "the electrode spacing and no one value suits every survey.")
        else:
            gate(self._qc_max_k, False, "This file carries no geometric factors.")
            unavailable.append("Max |k| (no geometric factors)")

        if data.haveData("rc"):
            rc = np.asarray(data["rc"], dtype=float)
            rc = rc[np.isfinite(rc)]
            span = (f"{rc.min():.3g} to {rc.max():.3g} Ω, median {float(np.median(rc)):.3g} Ω"
                    if rc.size else "empty")
            gate(self._qc_max_rc, True,
                 "Drop readings whose transmitter contact resistance exceeds this (0 = off; "
                 "the default is 30 kΩ). A failed or dried-out electrode shows up here "
                 f"before it shows up in the section. This file's contacts run {span}.")
        else:
            gate(self._qc_max_rc, False,
                 "This file carries no contact resistance, so there is nothing to test.")
            unavailable.append("Max contact R (no contact resistance)")

        if data.haveData("stack"):
            spread = 100.0 * np.asarray(data["stack"], dtype=float)
            spread = spread[np.isfinite(spread)]
            span = (f"median {float(np.median(spread)):.3g}%, 90% of readings under "
                    f"{float(np.percentile(spread, 90)):.3g}%, largest {spread.max():.3g}%"
                    if spread.size else "empty")
            gate(self._qc_max_stack, True,
                 "Drop readings whose potential scattered by more than this across its own "
                 "samples, as a percentage of the potential (0 = off; the default, 50 %, is "
                 "a scatter of half the signal). A few percent is normal; hundreds of "
                 "percent is an electrode or a contact failing. This file's spread: "
                 f"{span}.")
        else:
            gate(self._qc_max_stack, False,
                 "This file records no spread of the potential's samples (Subsurface "
                 "Insights exports do), so there is nothing to test.")
            unavailable.append("Max stacking spread (no sample spread)")

        rec = self._reciprocal_error(data)
        paired = 0 if rec is None else int(np.isfinite(rec).sum())
        if paired:
            finite = rec[np.isfinite(rec)]
            gate(self._qc_max_recip, True,
                 f"Drop measurements whose normal and reciprocal disagree by more than this "
                 f"(0 = off; the default is 5 %). {paired} of {data.size()} measurements "
                 f"have a reciprocal here; "
                 f"their disagreement runs to {100.0 * finite.max():.1f}%, median "
                 f"{100.0 * float(np.median(finite)):.1f}%. Unpaired measurements are kept.")
            gate(self._qc_average, True,
                 "Check 0, before every other check: each reading and its reciprocal "
                 "become one reading, with the mean of their two resistances and their "
                 "difference as its error (never below the Minimum under Data "
                 f"errors). {paired} of {data.size()} readings here have a reciprocal. "
                 "Readings without one are kept as they are. The reciprocal-error check "
                 "still judges each averaged pair by its difference.\n\n"
                 "Off by default: kept apart, both readings go to the inversion and the "
                 "fit sees how far they disagree. Applied with Apply filter, like the "
                 "checks below, and to every survey of a time-lapse run.")
        else:
            gate(self._qc_max_recip, False,
                  "This survey contains no reciprocal pairs, so there is nothing to compare. "
                  "Reciprocals have to be measured in the field; they cannot be recovered here.")
            gate(self._qc_average, False,
                 "This survey contains no reading measured both ways, so there is nothing "
                 "to average. For a survey written as two files, add both and keep “Pair "
                 "reciprocal files” ticked.")
            unavailable.append("Max reciprocal error (no reciprocal pairs)")

        if unavailable:
            self._qc_support_note.setText(
                "Unavailable for this file: " + "; ".join(unavailable) + ". "
                "These controls are disabled because the required measurements "
                "were not recorded, not because the input box is broken."
            )
        else:
            self._qc_support_note.setText(
                QCoreApplication.translate("PHGX", "All extra checks are supported by this file. A value of 0 turns "
                "each numerical check off.")
            )

    def _max_k_set_by_hand(self, _value: float) -> None:
        """Keep a |k| cap somebody typed: files loaded afterwards do not overwrite it."""
        self._qc_max_k_follows_file = False

    def _refresh_error_sources(self, data) -> None:
        """Offer the stacking-spread error model only for data that record a
        spread, and the reciprocal error model only for data measured both ways."""
        model = self._err_source.model()
        index = self._err_source.findData("reciprocal")
        item = model.item(index) if index >= 0 and hasattr(model, "item") else None
        if item is not None:
            # A series counts too: a time-lapse run fits the model over all of
            # its surveys, whichever one is on screen.
            paired = self._reciprocal_pair_count(data)
            available = bool(paired or self._tl_partner)
            item.setEnabled(available)
            item.setToolTip(
                QCoreApplication.translate("PHGX", "Each reading's error from a line fitted to the reciprocal pairs: "
                "log10(dR) = m·log10(R) + b, where R is a pair's mean resistance and dR "
                "the difference between its two directions, so dR = 10^b·R^m and the "
                "relative error is dR / R, never below the Minimum set below. A "
                "single inversion fits it to the survey's own pairs; a time-lapse "
                "inversion fits one line to the pairs of every survey and gives it to "
                "all of them. The Reciprocal errors tab draws the pairs and the line, "
                "and its “Fit to” chooser sets whether the line is fitted to all pairs "
                "or only to those the filter kept. The Data QC report and the settings "
                "file state the fit.")
                if available else
                QCoreApplication.translate("PHGX", "Needs readings measured both ways (each reading and its reciprocal). "
                "The loaded data have none; for a survey written as two files, add both "
                "and keep “Pair reciprocal files” ticked."))
            if not available and self._err_source.currentData() == "reciprocal":
                self._err_source.setCurrentIndex(self._err_source.findData("file"))
                if data is not None:
                    self.log("These data have no reciprocal pairs, so the data errors are "
                             "taken from the file's err column instead.", "warn")
        index = self._err_source.findData("stack")
        item = model.item(index) if index >= 0 and hasattr(model, "item") else None
        if item is None:
            return
        available = data is not None and data.haveData("stack")
        item.setEnabled(available)
        item.setToolTip(
            QCoreApplication.translate("PHGX", "√(spread² + estimate²) for each reading: the scatter of its potential's "
            "samples, as a fraction of the potential, added in quadrature to the estimate "
            "below. The scatter within one reading is not its uncertainty and usually "
            "overstates it, so χ² tends to come out low; it is never the default.")
            if available else
            QCoreApplication.translate("PHGX", "Needs the spread of each reading's potential samples, which the loaded data "
            "do not record (Subsurface Insights exports do)."))
        if not available and self._err_source.currentData() == "stack":
            self._err_source.setCurrentIndex(self._err_source.findData("file"))
            if data is not None:
                self.log("These data record no stacking spread, so the data errors are "
                         "taken from the file's err column instead.", "warn")
        self._sync_error_rows()

    def _reciprocal_pair_count(self, data) -> int:
        """How many readings of ``data`` have a reciprocal (0 for no data)."""
        if data is None:
            return 0
        rec = self._reciprocal_error(data)
        return 0 if rec is None else int(np.isfinite(rec).sum())

    def _sync_error_rows(self, *_args: Any) -> None:
        """Show "Minimum" only while an error comes from reciprocals."""
        floor = getattr(self, "_recip_floor", None)
        if floor is None:                       # still being built
            return
        used = (self._err_source.currentData() == "reciprocal"
                or self._qc_average.isChecked())
        self._set_rows_visible([floor], used)

    def _reciprocal_floor(self) -> float:
        """The "Minimum" error as a fraction."""
        return float(self._recip_floor.value()) / 100.0

    def _qc_settings(self) -> Dict[str, Any]:
        """The QC thresholds as set in the panel, as plain values.

        Plain values so the same filter can run off the UI thread, over every
        survey of a time-lapse series, exactly as Apply filter ran it here.
        """
        return {
            "min_rhoa": float(self._rmin.value()), "max_rhoa": float(self._rmax.value()),
            "max_error": float(self._max_err.value()),
            # Folding the section away also switches its criteria off.
            "more_checks": bool(self._qc_more.isChecked()),
            "drop_nonpositive": bool(self._qc_drop_neg.isChecked()),
            "min_voltage": float(self._qc_min_v.value()),
            "min_current": float(self._qc_min_i.value()),
            "max_k": float(self._qc_max_k.value()),
            "max_contact_r": float(self._qc_max_rc.value()),
            "max_stack": float(self._qc_max_stack.value()),
            "max_reciprocal": float(self._qc_max_recip.value()),
            # Check 0 and the error each averaged pair takes, as a fraction.
            "average_reciprocals": bool(self._qc_average.isChecked()
                                        and self._qc_average.isEnabled()),
            "reciprocal_floor": self._reciprocal_floor(),
        }

    @classmethod
    def _qc_survey(cls, data, qc: Dict[str, Any],
                   report: Optional[Dict[str, Any]] = None):
        """``(survey, keep, reasons)``: ``data`` through check 0 and the checks.

        Check 0, when ``qc`` asks for it, averages each reading with its
        reciprocal (``ert_io.average_reciprocal_pairs``); the checks then run on
        what is left, the reciprocal-error check judging each averaged pair by
        its own difference. ``survey`` is the copy to invert, and ``keep`` says
        which rows of ``data`` it holds - an averaged pair as its first reading.
        The pairing in ``report`` is the survey's as read, and its ``readings``
        the count before check 0, so the logs total what the files held.
        """
        import pygimli as pg

        scores = cls._reciprocal_scores(data)
        work, reciprocal, averaged = data, None, None
        rows = np.arange(int(data.size()))
        if qc.get("average_reciprocals"):
            work, reciprocal, averaged = ert_load.average_reciprocal_pairs(
                data, scores, floor=float(qc.get("reciprocal_floor") or 0.0))
            rows = np.asarray(averaged.pop("kept_rows"), dtype=int)
            if report is not None:
                report["averaged"] = averaged
        passed, reasons = cls._qc_keep(work, qc, report, scores=scores,
                                       reciprocal=reciprocal)
        if averaged and averaged["removed"]:
            reasons.insert(0, f"averaging {averaged['pairs']} reciprocal pairs removed "
                              f"{averaged['removed']}")
        if report is not None:
            report["readings"] = int(data.size())
        survey = pg.DataContainerERT(work)
        survey.set("valid", pg.Vector(passed.astype(float)))
        survey.removeInvalid()
        keep = np.zeros(int(data.size()), dtype=bool)
        keep[rows[passed.astype(bool)]] = True
        pairing = (report or {}).get("pairing")
        if pairing and pairing.get("available"):
            # Which pairs the filter kept, for the error model fitted to them
            # and the Reciprocal errors tab that draws the rest in grey.
            from PyHydroGeophysX.qt_apps.ert_records import reciprocal_pair_kept

            kept = reciprocal_pair_kept(scores, keep, averaged=averaged is not None)
            if kept is not None:
                pairing["kept"] = kept
        return survey, keep, reasons

    @classmethod
    def _qc_keep(cls, data, qc: Dict[str, Any],
                 report: Optional[Dict[str, Any]] = None, *, scores=None,
                 reciprocal: Optional[np.ndarray] = None) -> Tuple[np.ndarray, List[str]]:
        """``(keep, reasons)``: which measurements pass ``qc``, and what cut the rest.

        Every criterion that drops anything says how many, the error limit too:
        it starts at 20 %, and a filter that quietly took readings for it would
        read as the ρa range having done so.

        ``report``, when given, is filled in as the filter runs - the readings,
        how they pair with their reciprocals, and each check with its threshold
        and the count before and after it - for the run's QC logs
        (``qt_apps/ert_records.py``). Recorded here rather than worked out again
        afterwards, so the logs say what this filter did.

        ``scores`` is the survey's reciprocal pairing when already made - of the
        survey as read, when ``data`` is its averaged copy - and ``reciprocal``
        the reciprocal error of each row of ``data``, which an averaged copy
        cannot be paired to find.
        """
        rhoa = np.asarray(data["rhoa"], dtype=float)
        total = int(rhoa.size)
        checks: Optional[List[Dict[str, Any]]] = None
        if scores is None and (report is not None or (
                reciprocal is None and qc["more_checks"] and qc["max_reciprocal"] > 0)):
            scores = cls._reciprocal_scores(data)
        if reciprocal is None and scores is not None and len(scores) == total:
            reciprocal = scores["reciprocalErrRel"].to_numpy(dtype=float)
        if report is not None:
            from PyHydroGeophysX.qt_apps.ert_records import reciprocal_pairing

            checks = []
            report.update(readings=total, pairing=reciprocal_pairing(scores), checks=checks)
        keep = np.isfinite(rhoa) & (rhoa >= qc["min_rhoa"]) & (rhoa <= qc["max_rhoa"])
        reasons: List[str] = []
        if int((~keep).sum()):
            reasons.append(f"ρa outside {qc['min_rhoa']:g}–{qc['max_rhoa']:g} Ω·m dropped "
                           f"{int((~keep).sum())}")
        if checks is not None:
            checks.append({"name": "Apparent resistivity range",
                           "threshold": f"{qc['min_rhoa']:g} to {qc['max_rhoa']:g} ohm-m",
                           "before": total, "after": int(keep.sum())})
        if qc["max_error"] > 0 and data.haveData("err"):
            before = int(keep.sum())
            keep &= np.asarray(data["err"], dtype=float) <= (qc["max_error"] / 100.0)
            if before - int(keep.sum()):
                reasons.append(f"error above {qc['max_error']:g} % dropped "
                               f"{before - int(keep.sum())}")
            if checks is not None:
                checks.append({"name": "Relative error (err column)",
                               "threshold": f"<= {qc['max_error']:g} %",
                               "before": before, "after": int(keep.sum())})
        elif checks is not None:
            checks.append({"name": "Relative error (err column)", "before": None,
                           "threshold": "off" if qc["max_error"] <= 0 else
                           f"<= {qc['max_error']:g} %",
                           "note": "" if qc["max_error"] <= 0 else
                           "not applied: the file has no error column"})
        if qc["more_checks"]:
            reasons += cls._apply_extra_filters(data, keep, qc, checks=checks,
                                                reciprocal=reciprocal)
        elif checks is not None:
            checks.append({"name": "More checks", "threshold": "off", "before": None,
                           "note": "not applied"})
        if report is not None:
            report["kept"] = int(keep.sum())
        return keep, reasons

    @classmethod
    def _apply_extra_filters(cls, data, keep: np.ndarray, qc: Dict[str, Any], *,
                             checks: Optional[List[Dict[str, Any]]] = None,
                             reciprocal: Optional[np.ndarray] = None) -> List[str]:
        """Apply the folded QC criteria to ``keep`` in place; report what each cost.

        A criterion whose field is missing is skipped rather than failing the
        whole filter, matching the row being disabled in the panel. ``checks``
        collects each criterion as :meth:`_qc_keep` describes; ``reciprocal``
        is each row's reciprocal error already worked out for it, used rather
        than made again.
        """
        reasons: List[str] = []

        def cut(mask: np.ndarray, label: str, name: str = "", threshold: str = "") -> None:
            before = int(keep.sum())
            # In place on purpose: `keep &= mask` here would rebind the enclosing
            # name and raise UnboundLocalError instead of narrowing the caller's array.
            np.logical_and(keep, mask, out=keep)
            lost = before - int(keep.sum())
            if lost:
                reasons.append(f"{label} dropped {lost}")
            if checks is not None:
                checks.append({"name": name or label, "threshold": threshold,
                               "before": before, "after": int(keep.sum())})

        def skipped(name: str, threshold: str, note: str) -> None:
            if checks is not None:
                checks.append({"name": name, "threshold": threshold, "before": None,
                               "note": note})

        if qc["drop_nonpositive"]:
            cut(np.asarray(data["rhoa"], dtype=float) > 0.0, "ρa ≤ 0",
                "Apparent resistivity above 0", "> 0")
        else:
            skipped("Apparent resistivity above 0", "off", "")
        for key, token, label, name, unit, column in (
                ("min_voltage", "u", "|V| floor", "Potential |V|", "V", "voltage"),
                ("min_current", "i", "|I| floor", "Current |I|", "A", "current")):
            if qc[key] > 0 and data.haveData(token):
                cut(np.abs(np.asarray(data[token], dtype=float)) >= qc[key], label,
                    name, f">= {qc[key]:g} {unit}")
            else:
                skipped(name, "off" if qc[key] <= 0 else f">= {qc[key]:g} {unit}",
                        "" if qc[key] <= 0 else f"not applied: no {column} column")
        if qc["max_k"] > 0 and data.haveData("k"):
            cut(np.abs(np.asarray(data["k"], dtype=float)) <= qc["max_k"], "|k| ceiling",
                "Geometric factor |k|", f"<= {qc['max_k']:g} m")
        else:
            skipped("Geometric factor |k|", "off" if qc["max_k"] <= 0 else
                    f"<= {qc['max_k']:g} m",
                    "" if qc["max_k"] <= 0 else "not applied: no geometric factors")
        if qc["max_contact_r"] > 0 and data.haveData("rc"):
            cut(np.asarray(data["rc"], dtype=float) <= qc["max_contact_r"],
                "contact R ceiling", "Contact resistance", f"<= {qc['max_contact_r']:g} ohm")
        else:
            skipped("Contact resistance", "off" if qc["max_contact_r"] <= 0 else
                    f"<= {qc['max_contact_r']:g} ohm",
                    "" if qc["max_contact_r"] <= 0 else
                    "not applied: no contact resistance column")
        # .get: QC settings saved without this check do not name it.
        stack = qc.get("max_stack", 0.0)
        if stack > 0 and data.haveData("stack"):
            cut(np.asarray(data["stack"], dtype=float) <= qc["max_stack"] / 100.0,
                "stacking spread ceiling", "Stacking spread", f"<= {stack:g} %")
        else:
            skipped("Stacking spread", "off" if stack <= 0 else f"<= {stack:g} %",
                    "" if stack <= 0 else "not applied: no stacking spread column")
        if qc["max_reciprocal"] > 0:
            rec = cls._reciprocal_error(data) if reciprocal is None else reciprocal
            threshold = f"<= {qc['max_reciprocal']:g} %"
            if rec is not None:
                limit = qc["max_reciprocal"] / 100.0
                # An unpaired measurement has no reciprocal to disagree with, so it
                # is kept rather than judged against a test it cannot take.
                cut(~(np.isfinite(rec) & (rec > limit)), "reciprocal error",
                    "Reciprocal error", threshold + " (unpaired kept)")
            else:
                skipped("Reciprocal error", threshold,
                        "not applied: no resistances to pair")
        else:
            skipped("Reciprocal error", "off", "")
        return reasons

    def _apply_filter(self) -> None:
        if self._ert_data_full is None:
            self.log("Load ERT data first.", "warn")
            return
        try:
            import pygimli as pg
            # Folding "More checks" away also switches its criteria off, so what
            # the panel shows is what the filter did.
            qc = self._qc_settings()
            report: Dict[str, Any] = {}
            data, keep, reasons = self._qc_survey_with_manual(qc, report)
            if self._pair_info is not None:
                report["files"] = self._pair_record()
            if reasons:
                self.log("QC: " + "; ".join(reasons), "info")
            removed = int((~keep).sum())
            self._qc_mask = keep.astype(bool).tolist()
        except Exception as exc:  # noqa: BLE001
            self.log(f"Filter failed: {exc}", "error")
            return
        self._ert_data = data
        self._qc_applied = qc
        # What this filter did to the data now loaded, for the next run's QC
        # report; a new load or Reset leaves the data unfiltered and drops it.
        self._qc_report = report
        self._pseudo = self._pseudo_from_data(data)
        self._n_meas = int(data.size())
        self._refresh()
        self._recip_inputs_changed()
        # On the Reciprocal errors tab the filter's effect on the pairs is what
        # is being looked at; elsewhere the section shows what it left.
        if self._tabs.currentWidget() is not self._recip_view:
            self._tabs.setCurrentWidget(self._pseudo_widget)
        self.log(f"Filter applied: kept {data.size()}, removed {removed}.", "success")

    def _pair_record(self) -> Dict[str, Any]:
        """The loaded survey's two files and their readings, for its QC log."""
        info = dict(self._pair_info or {})
        return {"forward": self._data_path.name if self._data_path else "",
                "reciprocal": self._data_partner.name if self._data_partner else None,
                "forward_readings": int(info.get("forward", self._n_meas) or 0),
                "reciprocal_readings": int(info.get("reciprocal", 0) or 0),
                "dropped_fields": list(info.get("dropped_fields") or [])}

    def _reset_filter(self) -> None:
        self._qc_applied = None
        self._qc_report = None
        self._recip_inputs_changed()
        if self._ert_data_full is None:
            return
        # Readings rejected by hand stay out; Restore on the pseudosection brings them back.
        self._apply_manual_only()
        self.log("Filter reset.", "info")

    # -- electrodes ----------------------------------------------------------
    def _delete(self, idx: int) -> None:
        for seq in (self._x, self._z, self._y, self._labels, self._electrode_origins):
            del seq[idx]
        self._refresh()

    def _clear(self) -> None:
        self._x, self._z, self._y, self._labels, self._electrode_origins = [], [], [], [], []
        self._survey_3d = False
        self._sync_survey_dimension()
        self._refresh()
