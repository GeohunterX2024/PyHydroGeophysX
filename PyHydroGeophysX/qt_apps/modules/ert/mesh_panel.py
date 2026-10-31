"""The ERT page: mesh settings, imported meshes, the mesh preview and zones (plan M4.5).

Part of :class:`~.page.ERTProcessingModule`, split from the former
``ert_processing.py`` by area; the methods are unchanged.
"""

from __future__ import annotations

from .common import (
    Any,
    ArtifactRef,
    Dict,
    List,
    Path,
    PlainDoubleSpinBox,
    QAbstractSpinBox,
    QCoreApplication,
    QEventLoop,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QLabel,
    QPushButton,
    QSpinBox,
    TaskWorker,
    WorkflowSpec,
    _MAX_MESH_QUALITY,
    derive_preview,
    i18n,
    merged_row,
    mesh_build_spec,
    scratch_process_worker,
    table_io,
    theme,
)


class _MeshPanel:

    # -- mesh settings ----------------------------------------------------------
    def _build_mesh_settings(self) -> QGroupBox:
        """The mesh the inversion runs on, set up on the Mesh tab that draws it.

        Every setting is one of PyGIMLi's parameter-mesh options under a name
        that says what it does; each tooltip gives PyGIMLi's name and the E4D
        setting that plays the same part. The view rebuilds a moment after a
        change, so the effect of each is seen at once, and a setting left at
        its default builds the mesh PyGIMLi builds by itself.
        """
        box = QGroupBox(QCoreApplication.translate("PHGX", "Mesh"))
        form = QFormLayout(box)

        # An imported mesh. Building one from the electrode line is fine for a
        # 2D profile and hopeless for a 3D domain with topography, boreholes or
        # known structure, which is meshed externally (usually in Gmsh).
        self._mesh_path = ""
        self._mesh_btn = QPushButton(QCoreApplication.translate("PHGX", "Import mesh…"))
        self._mesh_btn.setIcon(theme.icon("fa5s.project-diagram"))
        self._mesh_btn.setToolTip(
            QCoreApplication.translate("PHGX", "Inverts on an externally built mesh instead of one generated from "
            "the electrode positions. PyGIMLi .bms, Gmsh .msh, VTK, .poly, or an "
            "E4D mesh (.1.node / .1.ele, with its .trn). An E4D mesh configuration "
            "(.cfg) is meshed once, on import. "
            "The region to invert must carry marker 2 or above; marker 0 and 1 "
            "are treated as background and stay fixed - for an E4D mesh, zone 1 "
            "is the background. The file is checked against the survey before the "
            "run starts."))
        self._mesh_btn.clicked.connect(self._import_mesh)
        self._mesh_clear = QPushButton("✕")
        self._mesh_clear.setMaximumWidth(32)
        self._mesh_clear.setToolTip(QCoreApplication.translate("PHGX", "Go back to a mesh generated from the data."))
        self._mesh_clear.setEnabled(False)
        self._mesh_clear.clicked.connect(self._clear_mesh)
        self._mesh_row = merged_row(self._mesh_btn, self._mesh_clear)
        form.addRow(QCoreApplication.translate("PHGX", "Source"), self._mesh_row)
        self._mesh_note = QLabel(QCoreApplication.translate("PHGX", "Built from the electrode positions."))
        self._mesh_note.setWordWrap(True)
        theme.set_tone(self._mesh_note, "hint")
        form.addRow("", self._mesh_note)
        # A 3D mesh is built in the 3D Mesh Builder around these electrodes and
        # comes back here as the imported mesh.
        self._mesh3d_btn = QPushButton(QCoreApplication.translate("PHGX", "Build a 3D mesh…"))
        self._mesh3d_btn.setIcon(theme.icon("fa5s.cubes"))
        self._mesh3d_btn.setToolTip(
            QCoreApplication.translate("PHGX", "Open the 3D Mesh Builder with these electrodes - a profile as a line at "
            "y = 0 - to build a 3D mesh around them with PyGIMLi, Gmsh or the E4D "
            "mesher. Its Use for ERT inversion button brings the mesh back here as "
            "the imported mesh, shown in 3D on this tab."))
        self._mesh3d_btn.clicked.connect(self._build_3d_mesh)
        form.addRow("", self._mesh3d_btn)

        def section(title: str, text: str) -> None:
            form.addRow(i18n.tr(QLabel(f"<b>{title}</b>")))
            hint = QLabel(i18n.tr(text))
            hint.setWordWrap(True)
            theme.set_tone(hint, "hint")
            form.addRow(i18n.tr(hint))

        section("Inverted region",
                "The cells the inversion solves for, under the electrodes "
                "(PyGIMLi's parameter domain, E4D's fine zone).")
        self._para_depth = PlainDoubleSpinBox()
        self._para_depth.setRange(0.0, 10000.0); self._para_depth.setDecimals(1)
        self._para_depth.setSingleStep(5.0); self._para_depth.setValue(0.0)
        self._para_depth.setSuffix(" m")
        self._para_depth.setSpecialValueText(QCoreApplication.translate("PHGX", "auto"))
        self._para_depth.setToolTip(
            QCoreApplication.translate("PHGX", "How deep to invert. PyGIMLi sizes the parameter domain from the array "
            "length, which for a long line reaches well below anything the data "
            "resolve; capping it removes unknowns the inversion cannot constrain and "
            "shortens every iteration. Leave at auto unless the sensitivity plot shows "
            "the bottom of the section is empty. Auto is 0.4 times the electrode "
            "spread (PyGIMLi's paraDepth)."))
        form.addRow(QCoreApplication.translate("PHGX", "Depth"), self._para_depth)
        self._para_boundary = PlainDoubleSpinBox()
        self._para_boundary.setRange(0.5, 20.0); self._para_boundary.setDecimals(1)
        self._para_boundary.setSingleStep(0.5); self._para_boundary.setValue(2.0)
        self._para_boundary.setSuffix(QCoreApplication.translate("PHGX", " spacings"))
        self._para_boundary.setToolTip(
            QCoreApplication.translate("PHGX", "How far the inverted region reaches past the first and the last "
            "electrode, in electrode spacings. A wider margin lets the inversion "
            "put structure beside the line rather than forcing it under the end "
            "electrodes, at the cost of cells the data barely see. PyGIMLi's "
            "paraBoundary, 2 by default; the padding of E4D's fine zone."))
        form.addRow(QCoreApplication.translate("PHGX", "Side margin"), self._para_boundary)
        self._surface_nodes = QSpinBox()
        self._surface_nodes.setRange(1, 8); self._surface_nodes.setValue(1)
        self._surface_nodes.setSuffix(QCoreApplication.translate("PHGX", " between electrodes"))
        self._surface_nodes.setToolTip(
            QCoreApplication.translate("PHGX", "Mesh nodes placed on the surface between two neighbouring electrodes. "
            "More give smaller cells near the surface, where the data resolve the "
            "most, and more unknowns. PyGIMLi's addNodes; 1, a node halfway "
            "between electrodes, by default."))
        form.addRow(QCoreApplication.translate("PHGX", "Surface nodes"), self._surface_nodes)
        self._para_max_cell = PlainDoubleSpinBox()
        self._para_max_cell.setRange(0.0, 1e6); self._para_max_cell.setDecimals(2)
        self._para_max_cell.setStepType(QAbstractSpinBox.StepType.AdaptiveDecimalStepType)
        self._para_max_cell.setSuffix(" m²")
        self._para_max_cell.setSpecialValueText(QCoreApplication.translate("PHGX", "no limit"))
        self._para_max_cell.setToolTip(
            QCoreApplication.translate("PHGX", "Upper limit on the area of an inverted cell. Without one the cells "
            "grow with depth; a limit keeps them small and even, with many more "
            "unknowns. The line under the plot gives the cell sizes of the mesh "
            "shown. PyGIMLi's paraMaxCellSize; the maximum volume of E4D's fine "
            "zone."))
        form.addRow(QCoreApplication.translate("PHGX", "Largest cell"), self._para_max_cell)
        self._quality = PlainDoubleSpinBox()
        self._quality.setRange(20.0, _MAX_MESH_QUALITY); self._quality.setDecimals(1)
        self._quality.setValue(34.0)
        self._quality.setSuffix("°")
        self._quality.setToolTip(
            QCoreApplication.translate("PHGX", "The smallest angle a triangle may have. Higher gives better-shaped "
            "triangles and more of them; Triangle cannot finish much above 34°, "
            "so that is the limit. PyGIMLi's quality; E4D sets the same for TetGen."))
        form.addRow(QCoreApplication.translate("PHGX", "Quality"), self._quality)

        section("Outer region",
                "Coarse cells that carry the boundary condition far from the "
                "electrodes; never inverted. Tick Outer region above the plot to "
                "see them.")
        self._outer_width = PlainDoubleSpinBox()
        self._outer_width.setRange(0.0, 50.0); self._outer_width.setDecimals(1)
        self._outer_width.setSingleStep(0.5); self._outer_width.setValue(0.0)
        self._outer_width.setSuffix(QCoreApplication.translate("PHGX", " × spread"))
        self._outer_width.setSpecialValueText(QCoreApplication.translate("PHGX", "auto (4 × spread)"))
        self._outer_width.setToolTip(
            QCoreApplication.translate("PHGX", "How far the outer region reaches beyond the inverted region, sideways "
            "and down, in lengths of the electrode spread. Too narrow and the "
            "boundary distorts the forward response; wider costs little, because "
            "its cells are large. PyGIMLi's boundary, 4 by default; E4D's outer "
            "boundary distance."))
        form.addRow(QCoreApplication.translate("PHGX", "Width"), self._outer_width)
        self._outer_max_cell = PlainDoubleSpinBox()
        self._outer_max_cell.setRange(0.0, 1e8); self._outer_max_cell.setDecimals(1)
        self._outer_max_cell.setStepType(QAbstractSpinBox.StepType.AdaptiveDecimalStepType)
        self._outer_max_cell.setSuffix(" m²")
        self._outer_max_cell.setSpecialValueText(QCoreApplication.translate("PHGX", "no limit"))
        self._outer_max_cell.setToolTip(
            QCoreApplication.translate("PHGX", "Upper limit on the cell area in the outer region. Leave it unlimited "
            "unless the forward solution needs a finer outer mesh: these cells are "
            "never inverted. PyGIMLi's boundaryMaxCellSize; the maximum volume of "
            "E4D's outer zone."))
        form.addRow(QCoreApplication.translate("PHGX", "Largest cell"), self._outer_max_cell)

        self._mesh_defaults = QPushButton(QCoreApplication.translate("PHGX", "Restore defaults"))
        self._mesh_defaults.setToolTip(
            QCoreApplication.translate("PHGX", "Put every setting above back to PyGIMLi's default mesh. The imported "
            "mesh and the zones are left alone."))
        self._mesh_defaults.clicked.connect(self._restore_mesh_defaults)
        form.addRow("", self._mesh_defaults)
        # The Mesh tab shows what these build, so it follows them.
        for spin in self._generated_mesh_widgets():
            spin.valueChanged.connect(self._mesh_inputs_changed)
        return box

    def _generated_mesh_widgets(self) -> tuple:
        """The settings of a mesh generated from the electrodes."""
        return (self._para_depth, self._para_boundary, self._surface_nodes,
                self._para_max_cell, self._quality, self._outer_width,
                self._outer_max_cell)

    def _restore_mesh_defaults(self) -> None:
        defaults = {self._para_depth: 0.0, self._para_boundary: 2.0,
                    self._surface_nodes: 1, self._para_max_cell: 0.0,
                    self._quality: 34.0, self._outer_width: 0.0,
                    self._outer_max_cell: 0.0}
        for widget, value in defaults.items():
            widget.setValue(value)

    def _mesh_options(self) -> Dict[str, Any]:
        """The mesh settings under the names ``build_inversion_mesh``, both
        workflows and the assistant use."""
        return {
            "mesh_quality": float(self._quality.value()),
            "para_depth": float(self._para_depth.value()),
            "para_max_cell_size": float(self._para_max_cell.value()),
            "para_boundary": float(self._para_boundary.value()),
            "surface_nodes": int(self._surface_nodes.value()),
            "outer_width": float(self._outer_width.value()),
            "outer_max_cell_size": float(self._outer_max_cell.value()),
            "mesh_file": str(self._mesh_path or ""),
            # Only when on, so a profile's recipe reads as it always has.
            **({"survey_3d": True} if self._survey_3d else {}),
        }

    def _update_mesh_link(self) -> None:
        """The Inversion panel's one line on the mesh, pointing to the Mesh tab."""
        link = getattr(self, "_mesh_link", None)
        if link is None:
            return  # still being built
        if self._mesh_path:
            parts = [f"imported <b>{Path(self._mesh_path).name}</b>"]
        else:
            depth = float(self._para_depth.value())
            parts = ["generated", "depth " + ("auto" if depth <= 0 else f"{depth:g} m"),
                     f"quality {float(self._quality.value()):g}°"]
            others = sum(1 for widget, default in (
                (self._para_boundary, 2.0), (self._surface_nodes, 1),
                (self._para_max_cell, 0.0), (self._outer_width, 0.0),
                (self._outer_max_cell, 0.0)) if widget.value() != default)
            if others:
                parts.append(f"{others} more changed")
        if self._mesh_tab.zones():
            if self._mesh_tab.conform_to_zones() and not self._mesh_path:
                parts.append("follows the zones")
            if self._mesh_tab.decouple_zones():
                parts.append("sharp zone edges")
        # The link first, so a narrow panel wraps the details, not the way there.
        link.setText("<a href='mesh'>Mesh tab</a>: " + " · ".join(parts))

    # -- imported mesh --------------------------------------------------------
    def _import_mesh(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, QCoreApplication.translate("PHGX", "Import inversion mesh"), "",
            "Meshes (*.bms *.msh *.vtk *.vtu *.poly *.node *.ele *.cfg);;"
            "E4D mesh (*.node *.ele);;E4D mesh configuration (*.cfg);;All files (*)")
        if not path:
            return
        try:
            self._apply_mesh_file(path)
        except Exception as exc:  # noqa: BLE001 - said next to the button, not in a traceback
            self._mesh_note.setText(QCoreApplication.translate("PHGX", "<span style='color:{0}'>{1}: {2}</span>").format(theme.color('red'), Path(path).name, exc))
            self.log(f"Could not import the mesh {Path(path).name}: {exc}", "error")

    def _mesh_from_e4d_config(self, path: str) -> str:
        """Build an E4D configuration's mesh once, and keep it as a .bms.

        The build runs in a process of its own (``ert.e4d_mesh``) - a borehole
        mesh takes seconds - while a local event loop keeps the window
        responsive until it is done. The run
        then inverts the saved mesh rather than rebuilding it every time.
        """
        stem = Path(path).stem
        spec = WorkflowSpec(
            workflow_id="ert.e4d_mesh",
            inputs={"config": ArtifactRef.from_path(Path(path), artifact_id="ert:e4d_config",
                                                    kind="e4d_mesh_configuration")},
            parameters={"name": stem}, metadata={"source": "qt"})
        settled: Dict[str, Any] = {}
        loop = QEventLoop()
        worker = scratch_process_worker(
            spec, self.state.ensure_results_store().scratch_dir(self.module_key) / "e4d" / stem)
        worker.succeeded.connect(lambda result: (settled.update(result=(
            result.summary["mesh_path"], result.summary["mesher"])), loop.quit()))
        worker.failed.connect(lambda message: (settled.update(error=message), loop.quit()))
        self.register_worker(worker, activity="Building the mesh")
        self._mesh_note.setText(QCoreApplication.translate("PHGX", "Building the mesh {0} describes, as E4D would…").format(Path(path).name))
        worker.start()
        if not settled:
            loop.exec()
        if "error" in settled:
            raise RuntimeError(settled["error"])
        target, mesher = settled["result"]
        self.log(f"Built the E4D mesh of {Path(path).name} with {mesher}; saved as "
                 f"{Path(target).name}.", "info")
        return target

    def _apply_mesh_file(self, path: str) -> str:
        """Load and check the mesh now, not when the inversion starts.

        A mesh whose origin or units are wrong fails deep in the forward solver,
        minutes into a run. Checking on import turns that into an immediate
        message next to the button that caused it. An E4D configuration is
        meshed here, once, and the run inverts on that mesh.
        """
        from PyHydroGeophysX.inversion.ert_mesh import load_inversion_mesh

        source = Path(path).name
        if Path(path).suffix.lower() == ".cfg":
            path = self._mesh_from_e4d_config(path)
        # Checked against the loaded survey when there is one; importing before
        # loading data is allowed, and the run re-checks it either way.
        mesh = load_inversion_mesh(path, data=self._ert_data, log=lambda m: None)
        invertible = sum(1 for cell in mesh.cells() if cell.marker() > 1)
        self._mesh_path = str(path)
        self._mesh_clear.setEnabled(True)
        built_from = f" (built from {source})" if source != Path(path).name else ""
        summary = (f"<b>{Path(path).name}</b>{built_from}: {mesh.cellCount()} cells "
                   f"({invertible} inverted), {mesh.dim()}D.")
        if mesh.dim() == 3 and self._ert_data is not None:
            summary += " The profile is inverted along x at y = 0, and its section shown."
        self._mesh_note.setText(i18n.tr(summary))
        self._sync_mesh_source()
        self.log(f"Imported inversion mesh {Path(path).name}: "
                 f"{mesh.cellCount()} cells, {invertible} inverted.", "success")
        if mesh.dim() == 3 and invertible > 20000:
            self.log(f"{invertible} inverted cells in 3D: PyGIMLi solves each forward run "
                     "on about eight times as many cells, and the in-house inversion holds "
                     "a Jacobian of every reading by every cell, so expect minutes per "
                     "iteration and several GB of memory. Larger cells away from the "
                     "electrodes cut both.", "warn")
        return summary

    def _build_3d_mesh(self) -> None:
        """Hand the electrodes to the 3D Mesh Builder; with none, just open it.

        A profile's electrodes go over as a line at y = 0, a 3-D survey's
        where they are.
        """
        if not self._x:
            self.navigateRequested.emit("mesh3d")
            return
        folder = self.state.ensure_results_store().scratch_dir(self.module_key)
        stem = self._data_path.stem if self._data_path else "survey"
        path = table_io.write_csv(
            Path(folder) / f"{stem}_electrodes.csv",
            [(float(x), float(y) if self._survey_3d else 0.0, float(z))
             for x, y, z in zip(self._x, self._y, self._z)],
            header=("x", "y", "z"))
        self.handoffRequested.emit("mesh3d", "load_sensor_file", {"path": str(path)})

    def _clear_mesh(self) -> None:
        self._mesh_path = ""
        self._mesh_clear.setEnabled(False)
        self._mesh_note.setText(QCoreApplication.translate("PHGX", "Built from the electrode positions."))
        self._sync_mesh_source()

    def _sync_mesh_source(self) -> None:
        """An imported mesh describes its own domain, so the sizing knobs are
        dead, and it cannot be rebuilt along the zone outlines either. A 3-D
        survey's generated mesh (``ert_mesh.survey_volume_mesh``) has no
        surface nodes, no outer cell size and no zone outlines."""
        generated = not self._mesh_path
        profile_only = (self._surface_nodes, self._outer_max_cell)
        for widget in self._generated_mesh_widgets():
            acts = generated and not (self._survey_3d and widget in profile_only)
            widget.setEnabled(acts)
            label = self.row_label(widget)
            if label is not None:
                label.setEnabled(acts)
        self._mesh_defaults.setEnabled(generated)
        self._mesh_tab.set_conform_available(
            generated and not self._survey_3d,
            "" if generated and not self._survey_3d else
            "Zones are drawn on 2-D sections; a 3-D survey's mesh is built without "
            "them." if generated else
            "An imported mesh is inverted as it is, so it cannot be rebuilt along "
            "the zone outlines. Go back to a generated mesh to use this.")
        self._mesh_inputs_changed()

    def _sync_survey_dimension(self) -> None:
        """Follow a change between a profile and a 3-D survey: the mesh settings
        that act, and the Data tab's view (a pseudosection or a plan)."""
        self._sync_mesh_source()

    # -- mesh preview and a-priori zones -------------------------------------
    def _electrode_rows(self) -> List[Dict[str, Any]]:
        """The electrodes as edited here, in the form the data are saved with."""
        rows = [
            {
                "order": index,
                "label": self._labels[index],
                "x": float(self._x[index]),
                "z": float(self._z[index]),
                "original_index": self._electrode_origins[index],
            }
            for index in range(len(self._x))
        ]
        if self._survey_3d:
            for row, y in zip(rows, self._y):
                row["y"] = float(y)
        return rows

    def _zone_parameters(self) -> Dict[str, Any]:
        """The a-priori zones for a recipe; nothing when there are none, so a run
        without zones records no zone entries. The two
        zone options are recorded only when on - and rebuilding along the
        outlines only for a generated mesh, the one it can rebuild."""
        zones = self._mesh_tab.zones()
        if not zones:
            return {}
        parameters: Dict[str, Any] = {"zones": zones}
        if self._mesh_tab.conform_to_zones() and not self._mesh_path:
            parameters["conform_to_zones"] = True
        if self._mesh_tab.decouple_zones():
            parameters["decouple_zones"] = True
        return parameters

    def _sync_mesh_engine(self, *_args: Any) -> None:
        """Tell the zone panel which engine, and which kind of run, will use it."""
        self._mesh_tab.set_engine(str(self._engine.currentData() or "pyhydro"),
                                  self._tl_mode.isChecked())

    def _on_tab_changed(self, index: int) -> None:
        self._sync_tab_controls()
        if self._tabs.widget(index) is self._mesh_tab:
            self._refresh_mesh_preview()
        elif self._tabs.widget(index) is self._recip_view:
            self._refresh_recip_view()

    def _sync_tab_controls(self) -> None:
        """Show only the controls belonging to the selected ERT stage."""
        if not hasattr(self, "_controls"):
            return
        current = self._tabs.currentWidget()
        data = current is self._pseudo_widget
        quality = current is self._quality_view
        timelapse = self._tl_mode.isChecked()
        # Mesh and model views already have their own tools beside the plot.
        # Hiding this whole column gives their plot and tools the full width.
        self._controls.setVisible(data or quality)
        for widget, visible in (
            (self._load_group, data),
            (self._info, data),
            (self._qc_group, data),
            (self._errors_group, data),
            (self._inversion_group, data or quality),
            (self._fit_group, data or quality),
            (self._tl_panel, (data or quality) and timelapse),
            (self._run_group, data or quality),
        ):
            widget.setVisible(visible)
        self._controls_scroll.fit_to_content()

    def _mesh_inputs_changed(self, *_args: Any) -> None:
        """Something the mesh depends on changed; rebuild it if it is on screen.

        After a short pause, so stepping a spin box builds one mesh, not one per
        step. Off screen nothing happens until the tab is opened again, when the
        inputs are compared with those of the mesh shown. Zone edits come here
        too; they change the mesh only while it follows the zone outlines, and
        the comparison of inputs sees to the rest.
        """
        self._update_mesh_link()
        if self._tabs.currentWidget() is self._mesh_tab:
            self._mesh_timer.start()

    def _mesh_preview_request(self):
        """What the next run would build its mesh from.

        Returns ``((key, task arguments, description), "")``, or ``(None,
        reason)`` when there is nothing to build from. The key holds every input
        of the mesh, so a mesh is rebuilt exactly when one of them changed: the
        settings, and the zone outlines while the mesh follows them - not the
        zones' values, which leave the mesh as it is.
        """
        options = self._mesh_options()
        mesh_file = options["mesh_file"]
        zones = self._mesh_tab.zones()
        outlines: tuple = ()
        if zones and self._mesh_tab.conform_to_zones() and not mesh_file:
            options["conform_zones"] = zones
            outlines = tuple(tuple(tuple(vertex) for vertex in zone["polygon"])
                             for zone in zones)
        settings = tuple(sorted((name, value) for name, value in options.items()
                                if name != "conform_zones")) + (outlines,)
        if self._tl_mode.isChecked() and self._tl_files:
            # The time-lapse pipeline meshes around its first survey, read with
            # the chosen instrument and placed from the electrode file, as the
            # run places it; this page's hand edits are not applied to a series.
            first, instrument = self._tl_files[0], self._instrument.currentData()
            electrodes = self._electrode_file()
            key = ("timelapse", first, instrument, electrodes, settings)
            args = ("timelapse", first, instrument, electrodes)
            where = f"first survey of the series, {Path(first).name}"
        elif self._ert_data is not None:
            rows = self._electrode_rows()
            key = ("single", id(self._ert_data),
                   tuple((r["x"], r.get("y"), r["z"], r["original_index"]) for r in rows),
                   settings)
            args = ("single", self._ert_data, None, rows)
            where = self._data_path.name if self._data_path else "the loaded survey"
        elif mesh_file:
            key = ("mesh", mesh_file)
            args = ("mesh", None, None, None)
            where = ""
        else:
            return None, "Load ERT data, or import a mesh, to see the inversion mesh."
        if mesh_file:
            where = f"imported {Path(mesh_file).name}" + (f", with {where}" if where else "")
        return (key, args + (options,), where), ""

    def _refresh_mesh_preview(self, force: bool = False) -> None:
        """Build the mesh preview if its inputs changed, or when ``force``d."""
        request, message = self._mesh_preview_request()
        if request is None:
            self._supersede_mesh_preview()
            self._mesh_preview_key = None
            self._mesh_tab.set_message(message)
            return
        key, args, where = request
        if not force and key in (self._mesh_preview_key, self._mesh_preview_pending):
            return
        scratch = self.state.ensure_results_store().scratch_dir(self.module_key)
        self._supersede_mesh_preview()
        self._mesh_preview_pending = key
        self._mesh_tab.set_status("Building the inversion mesh…")
        try:
            spec = mesh_build_spec(*args, scratch)
        except (ValueError, OSError, RuntimeError) as exc:  # said on the Mesh tab, as a failed build is
            self._on_mesh_preview_failed(None, key, str(exc))
            return
        # The generator in a process of its own (a native crash ends only that);
        # the preview is then derived from the mesh in a thread.
        worker = scratch_process_worker(spec, scratch / "mesh_preview", objects=("mesh", "data"))
        worker.succeeded.connect(lambda result, w=worker: self._derive_mesh_preview(w, key, where, result))
        worker.failed.connect(lambda error, w=worker: self._on_mesh_preview_failed(w, key, error))
        self._mesh_worker = self.register_worker(worker, activity="Previewing the mesh")
        worker.start()

    def _derive_mesh_preview(self, worker, key, where: str, result) -> None:
        if worker is not self._mesh_worker:
            return
        follow = TaskWorker(derive_preview, result)
        follow.succeeded.connect(lambda preview, w=follow: self._on_mesh_preview_ready(w, key, where, preview))
        follow.failed.connect(lambda error, w=follow: self._on_mesh_preview_failed(w, key, error))
        self._mesh_worker = self.register_worker(follow, activity="Previewing the mesh")
        follow.start()

    def _mesh_summary(self) -> Dict[str, Any]:
        """The counts of the mesh on the Mesh tab, and whether it is current."""
        preview = self._mesh_tab.preview()
        if not preview:
            return {"built": False}
        request, _ = self._mesh_preview_request()
        summary = {key: preview[key] for key in
                   ("dim", "cells", "para_cells", "outer_cells", "nodes")}
        summary.update(built=True, current=bool(request) and request[0] == self._mesh_preview_key,
                       electrodes=int(len(preview.get("sensors", ()))),
                       zone_outline_edges=int((preview.get("build") or {}).get(
                           "zone_outline_edges", 0)))
        if preview.get("para_extent") is not None:
            summary["para_extent"] = [round(float(v), 3) for v in preview["para_extent"]]
            summary["full_extent"] = [round(float(v), 3) for v in preview["full_extent"]]
        return summary

    def _supersede_mesh_preview(self) -> None:
        previous, self._mesh_worker = self._mesh_worker, None
        self._mesh_preview_pending = None
        if previous is not None and previous.isRunning():
            previous.cancel()

    def _on_mesh_preview_ready(self, worker, key, where: str, preview: Dict[str, Any]) -> None:
        if worker is not self._mesh_worker:
            return  # superseded by a newer build
        self._mesh_preview_pending = None
        self._mesh_preview_key = key
        # A zone drawn next starts at the survey's typical value, not at 100.
        if preview.get("median_rhoa"):
            self._mesh_tab.set_default_resistivity(float(preview["median_rhoa"]))
        self._mesh_tab.set_preview(preview, where)

    def _on_mesh_preview_failed(self, worker, key, message: str) -> None:
        if worker is not self._mesh_worker:
            return
        self._mesh_preview_pending = None
        # Kept, so the same inputs are not retried on every change of tab.
        self._mesh_preview_key = key
        self._mesh_tab.set_message(f"The inversion mesh could not be built: {message}")
        self.log(f"Mesh preview failed: {message}", "warn")

    def _on_inv_mode_changed(self, *_args: Any) -> None:
        """Apply the Quick/Full split to the stages each mode owns.

        Quick drops the two stages that cost the most and change no model on a
        clean dataset: the geometric-factor check and the auto-λ search. Full
        restores both.

        This is a preset, not a lock. The auto-λ checkbox stays enabled in both
        modes, so ticking it under Quick runs the search and the panel shows that
        it will. The k check has no such control by design, because a wrong k is
        the one problem the result cannot reveal.
        """
        quick = str(self._inv_mode.currentData() or "quick") == "quick"
        self._geom_policy = "off" if quick else "fix"
        self._auto_lam.setChecked(not quick)

    def _on_auto_lambda(self, on: bool) -> None:
        """Show the auto-λ target and trial budget only while auto-λ is on."""
        self._set_rows_visible((self._chi2_row, self._lam_trials), on)

    def _on_reject_outliers(self, on: bool) -> None:
        """Show the rejection cut and the data floor only while rejection is on."""
        self._set_rows_visible((self._reject_row, self._min_keep), on)

    def _on_inversion_failed(self, message: str) -> None:
        self._agent_run_state = "failed"
        self._agent_run_error = message
        self.fail_persisted_run(message, "ert.single_inversion")
        self.log(f"ERT inversion failed: {message}", "error")

    def _reset_invert_button(self) -> None:
        if self._inv_busy is not None:
            self._inv_busy.finish()
            self._inv_busy = None
        self._invert_btn.setText(QCoreApplication.translate("PHGX", "Run inversion"))
        self._inv_progress.setVisible(False)
        self._show_run_buttons(self._tl_mode.isChecked())
        self._sync_run_ready()
